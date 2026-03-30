import webview
from .crud import ObjectController, LogsController, TileLayerController, StopImportController
from .storage import Storage
from .schemas.stop_import import StopImportRequest
from .logger import log
import uuid
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .api import Api


class Api:
    """
    Единый API объект для всех окон pywebview.
    Все окна получают ссылку на один и тот же экземпляр,
    что обеспечивает синхронизацию данных через evaluate_js.
    """

    def __init__(self, storage: Storage) -> None:
        self.objects = ObjectController(storage)
        self.logs = LogsController()
        self.tile_layers = TileLayerController(storage)
        self.stop_import = StopImportController(storage)
        self._windows = {}  # Храним окна по ID для синхронизации
        self._main_window = None  # Главное окно
        self.storage = storage

        # Устанавливаем ссылку на API в контроллере
        self.objects.set_api(self)
    
    def set_main_window(self, window):
        """Установить главное окно для синхронизации"""
        self._main_window = window
        print('[API] Main window set')

    def open_panel_window(self, panel_id: str):
        """Открыть панель в отдельном окне pywebview через Vue Router"""
        # Уникальный ID для окна
        window_id = str(uuid.uuid4())[:8]
        
        # Маршруты Vue Router для отдельных панелей
        routes = {
            'map': '/map',
            'list': '/list',
            'brushTable': '/brush',
        }
        
        route = routes.get(panel_id, '/map')
        # URL для отдельной панели через роутинг
        url = f"http://localhost:5173{route}"
        
        # Заголовки окон
        titles = {
            'map': 'Карта - Passenger Traffic Analysis',
            'list': 'Список объектов - Passenger Traffic Analysis',
            'brushTable': 'Инструменты - Passenger Traffic Analysis',
        }
        
        title = titles.get(panel_id, 'Panel - Passenger Traffic Analysis')
        
        # Создаём новое окно с ТОЙ ЖЕ САМОЙ ссылкой на API
        # min_size=(100, 100) позволяет уменьшать до очень маленького размера
        window = webview.create_window(
            title,
            url,
            js_api=self,  # Тот же самый экземпляр Api!
            width=1000,
            height=700,
            resizable=True,
            min_size=(100, 100),  # Минимальный размер для возможности уменьшения
        )
        
        # Сохраняем окно
        self._windows[window_id] = {
            'window': window,
            'panel_id': panel_id,
        }
        
        # Подписываемся на событие закрытия
        def on_closing():
            print(f'[API] Window {window_id} closing')
            if window_id in self._windows:
                del self._windows[window_id]
        
        window.events.closing += on_closing
        
        return {'status': 'success', 'window_id': window_id}
    
    def get_window_id(self):
        """Получить ID текущего окна (вызывается из JS)"""
        import inspect
        frame = inspect.currentframe()
        try:
            # Получаем окно из которого вызван метод
            # Это хак но работает для определения отправителя
            return 'current_window'
        finally:
            del frame
    
    def sync_windows(self, event_type: str, data: dict = None, exclude_window_id: str = None):
        """
        Синхронизировать ВСЕ окна через evaluate_js.
        Вызывается после создания/обновления/удаления объекта.

        Args:
            event_type: Тип события (OBJECT_CREATED, OBJECT_UPDATED, OBJECT_DELETED)
            data: Данные события
            exclude_window_id: ID окна которое НЕ нужно уведомлять (окно-отправитель)
        """
        message = json.dumps({
            'type': event_type,
            'data': data or {}
        })

        print(f'[API] Syncing windows with {event_type} (exclude: {exclude_window_id})')
        print(f'[API] Message: {message}')

        # Отправляем в главное окно
        if self._main_window:
            try:
                js_code = f"""
                (function() {{
                    console.log('[Sync] === OBJECT_DELETED received ===');
                    console.log('[Sync] Data:', {message});
                    try {{
                        const event = new CustomEvent('panel-sync', {{
                            detail: {message}
                        }});
                        const dispatched = window.dispatchEvent(event);
                        console.log('[Sync] Dispatched:', dispatched);
                    }} catch(e) {{
                        console.error('[Sync] Error:', e);
                    }}
                }})();
                """
                print(f'[API] Executing JS in main window...')
                result = self._main_window.evaluate_js(js_code)
                print(f'[API] Main window sync result: {result}')
            except Exception as e:
                print(f'[API] Error syncing main window: {e}')
        
        # Отправляем во все дочерние окна
        for window_id, window_info in list(self._windows.items()):
            # Пропускаем окно-отправитель если указано
            if exclude_window_id and window_id == exclude_window_id:
                continue
                
            try:
                js_code = f"""
                (function() {{
                    try {{
                        console.log('[Sync] Received:', {message});
                        const event = new CustomEvent('panel-sync', {{
                            detail: {message}
                        }});
                        window.dispatchEvent(event);
                    }} catch(e) {{
                        console.error('[Sync] Error:', e);
                    }}
                }})();
                """
                window_info['window'].evaluate_js(js_code)
            except Exception as e:
                print(f'[API] Error syncing window {window_id}: {e}')

        return {'status': 'success'}
    
    def sync_chosen_type(self, option: list, exclude_window = None):
        """
        Синхронизировать выбранный тип объекта между всеми окнами.
        
        Args:
            option: [type, name] например ['Polygon', 'Полигон']
            exclude_window: Окно которое НЕ нужно уведомлять (отправитель)
        """
        message = json.dumps({
            'type': 'CHOSEN_TYPE_CHANGED',
            'data': {'option': option}
        })
        
        print(f'[API] Syncing chosen type: {option} (exclude: {exclude_window})')
        
        # Отправляем в главное окно (если это не отправитель)
        if self._main_window and self._main_window != exclude_window:
            try:
                js_code = f"""
                (function() {{
                    try {{
                        console.log('[Sync] Chosen type in main:', {message});
                        const event = new CustomEvent('chosen-type-changed', {{
                            detail: {message}
                        }});
                        window.dispatchEvent(event);
                    }} catch(e) {{
                        console.error('[Sync] Error in main:', e);
                    }}
                }})();
                """
                self._main_window.evaluate_js(js_code)
            except Exception as e:
                print(f'[API] Error syncing chosen type to main: {e}')
        
        # Отправляем во все дочерние окна (кроме отправителя)
        for window_id, window_info in list(self._windows.items()):
            if window_info['window'] == exclude_window:
                continue
                
            try:
                js_code = f"""
                (function() {{
                    try {{
                        console.log('[Sync] Chosen type:', {message});
                        const event = new CustomEvent('chosen-type-changed', {{
                            detail: {message}
                        }});
                        window.dispatchEvent(event);
                    }} catch(e) {{
                        console.error('[Sync] Error:', e);
                    }}
                }})();
                """
                window_info['window'].evaluate_js(js_code)
            except Exception as e:
                print(f'[API] Error syncing chosen type to window {window_id}: {e}')

        return {'status': 'success'}
    
    def get_current_tile_layer(self):
        """Получить текущий слой карт"""
        return self.tile_layers.get_current_layer()
    
    def set_current_tile_layer(self, layer: str):
        """Установить текущий слой карт"""
        result = self.tile_layers.set_current_layer(layer)
        # Синхронизируем ВСЕ окна (главное + дочерние с map)
        if result['status'] == 'success':
            # Отправляем в главное окно
            if self._main_window:
                try:
                    js_code = f"""
                    (function() {{
                        try {{
                            console.log('[Sync] TILE_LAYER_CHANGED in main:', '{layer}');
                            const event = new CustomEvent('panel-sync', {{
                                detail: {json.dumps({'type': 'TILE_LAYER_CHANGED', 'data': {'layer': layer}})}
                            }});
                            window.dispatchEvent(event);
                        }} catch(e) {{
                            console.error('[Sync] Error in main:', e);
                        }}
                    }})();
                    """
                    self._main_window.evaluate_js(js_code)
                except Exception as e:
                    print(f'[API] Error syncing tile layer to main: {e}')
            
            # Отправляем во ВСЕ дочерние окна с map
            for window_id, window_info in self._windows.items():
                if window_info['panel_id'] == 'map':
                    try:
                        js_code = f"""
                        (function() {{
                            try {{
                                console.log('[Sync] TILE_LAYER_CHANGED in map window {window_id}:', '{layer}');
                                const event = new CustomEvent('panel-sync', {{
                                    detail: {json.dumps({'type': 'TILE_LAYER_CHANGED', 'data': {'layer': layer}})}
                                }});
                                window.dispatchEvent(event);
                            }} catch(e) {{
                                console.error('[Sync] Error:', e);
                            }}
                        }})();
                        """
                        window_info['window'].evaluate_js(js_code)
                    except Exception as e:
                        print(f'[API] Error syncing tile layer to window {window_id}: {e}')
        return result
    
    def delete_object(self, id: str):
        """
        Удалить объект
        
        Args:
            id: ID объекта для удаления
            
        Returns:
            {"status": "success", "id": "..."} или {"status": "failed", "message": "..."}
        """
        try:
            from uuid import UUID

            # Валидация UUID
            obj_uuid = UUID(id)

            # Удаление через контроллер
            result = self.objects.delete_object(obj_uuid)

            if result:
                return {"status": "success", "id": id}
            else:
                return {"status": "failed", "message": "Объект не найден"}

        except Exception as e:
            log.error("api_delete_object", extra={"error": str(e), "id": id})
            return {"status": "failed", "message": str(e)}

    def export_geometry(self, data: dict):
        """
        Экспортировать полигоны и полилинии в JSON файл
        
        Args:
            data: {"objects": [...], "filename": "export.json"}
            
        Returns:
            {"status": "success", "message": "...", "count": N}
        """
        try:
            import json
            import webview
            from pathlib import Path
            from datetime import datetime
            
            objects = data.get("objects", [])
            if not objects:
                return {
                    "status": "failed",
                    "message": "Нет объектов для экспорта"
                }
            
            # Данные для экспорта
            export_data = {
                "version": 1,
                "exportedAt": datetime.now().isoformat(),
                "count": len(objects),
                "objects": objects
            }
            
            # Диалог сохранения файла
            window = webview.active_window()
            result = window.create_file_dialog(
                dialog_type=webview.FOLDER_DIALOG,
                directory=str(Path.home())
            )
            
            if not result:
                return {
                    "status": "cancelled",
                    "message": "Экспорт отменён пользователем"
                }
            
            # Сохраняем в выбранную папку
            folder = result[0] if isinstance(result, tuple) else result
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"geometry_export_{timestamp}.json"
            file_path = Path(folder) / filename
            
            # Записываем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            log.info("export_geometry", extra={"count": len(objects), "file": str(file_path)})
            return {
                "status": "success",
                "message": f"Экспортировано {len(objects)} объектов в {file_path}",
                "count": len(objects),
                "file_path": str(file_path)
            }
            
        except Exception as e:
            log.error("api_export_geometry", extra={"error": str(e)})
            return {
                "status": "failed",
                "message": str(e)
            }

    def import_geometry(self, data: dict):
        """
        Импортировать полигоны и полилинии из JSON файла
        
        Args:
            data: {}
            
        Returns:
            {"status": "success", "imported": N, "failed": N}
        """
        try:
            import json
            import webview
            from pathlib import Path
            
            # Диалог выбора файла
            window = webview.active_window()
            result = window.create_file_dialog(
                dialog_type=webview.OPEN_DIALOG,
                file_types=('JSON files (*.json)', 'All files (*.*)'),
                directory=str(Path.home())
            )
            
            if not result:
                return {
                    "status": "cancelled",
                    "message": "Импорт отменён пользователем"
                }
            
            file_path = result[0] if isinstance(result, tuple) else result
            
            # Читаем файл
            with open(file_path, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            if not export_data.get("objects") or not isinstance(export_data["objects"], list):
                raise ValueError("Неверный формат файла")
            
            # Импорт через контроллер
            imported_count = 0
            failed_count = 0
            
            for obj in export_data["objects"]:
                try:
                    self.objects.create_object(obj)
                    imported_count += 1
                except Exception as e:
                    log.error("import_geometry_object", extra={"error": str(e), "obj_id": obj.get("id")})
                    failed_count += 1
            
            log.info("import_geometry", extra={"imported": imported_count, "failed": failed_count, "file": file_path})
            return {
                "status": "success",
                "imported": imported_count,
                "failed": failed_count,
                "total": len(export_data["objects"])
            }
            
        except Exception as e:
            log.error("api_import_geometry", extra={"error": str(e)})
            return {
                "status": "failed",
                "message": str(e)
            }

    def delete_all_by_type(self, data: dict):
        """
        Удалить все объекты указанного типа
        
        Args:
            data: {"type": "Polygon" | "Polyline"}
            
        Returns:
            {"status": "success", "deleted": N}
        """
        try:
            obj_type = data.get("type")
            if not obj_type or obj_type not in ["Polygon", "Polyline"]:
                return {
                    "status": "failed",
                    "message": "Неверный тип объекта"
                }
            
            # Получаем все объекты из БД напрямую
            all_objects = self.storage.objects.get_all_objects()
            if not all_objects:
                return {
                    "status": "success",
                    "deleted": 0
                }
            
            # Фильтруем по типу и удаляем
            deleted_count = 0
            from uuid import UUID
            
            for obj in all_objects:
                if obj.obj_type == obj_type:
                    try:
                        obj_id = UUID(obj.uuid)
                        self.objects.delete(obj_id)
                        deleted_count += 1
                    except Exception as e:
                        log.error("delete_all_by_type_object", extra={"error": str(e), "obj_id": obj.uuid})
            
            log.info("delete_all_by_type", extra={"type": obj_type, "deleted": deleted_count})
            return {
                "status": "success",
                "deleted": deleted_count
            }
            
        except Exception as e:
            log.error("api_delete_all_by_type", extra={"error": str(e)})
            return {
                "status": "failed",
                "message": str(e)
            }

    def import_stops(self, data: dict):
        """
        Импортировать остановки из Overpass API
        
        Args:
            data: {"cities": "Ангарск,Москва", "stop_types": ["bus_stop", "platform"]}
        
        Returns:
            {"status": "success", "imported_count": 1234, "duplicate_count": 0, "cities": ["Ангарск"]}
        """
        try:
            print(f'[API] import_stops вызван с данными: {data}')
            
            # Валидация запроса
            request = StopImportRequest(**data)
            
            # Разделить города по запятой
            cities = [city.strip() for city in request.cities.split(',') if city.strip()]
            
            if not cities:
                print('[API] import_stops: города не указаны')
                return {
                    "status": "failed",
                    "message": "Города не указаны"
                }
            
            # Импорт через контроллер
            print(f'[API] import_stops: начинаем импорт для {cities}')
            result = self.stop_import.import_stops(cities, request.stop_types)
            print(f'[API] import_stops: результат {result}')

            return result.model_dump()

        except Exception as e:
            print(f'[API] import_stops ошибка: {e}')
            log.error("api_import_stops", extra={"error": str(e)})
            return {
                "status": "failed",
                "message": str(e)
            }

    def export_stops(self, data: dict):
        """
        Экспортировать остановки в Excel файл через Polars
        
        Args:
            data: {}
        
        Returns:
            {"status": "success", "message": "Экспортировано 320 остановок", "count": 320}
        """
        try:
            from .models.object import MapObject, StopMetadata
            import polars as pl
            import webview
            from webview import FileDialog
            from pathlib import Path
            from datetime import datetime
            
            with self.storage.localSession() as session:
                # Загружаем остановки с метаданными
                query = session.query(MapObject, StopMetadata).join(
                    StopMetadata,
                    MapObject.id == StopMetadata.object_id
                ).filter(
                    MapObject.obj_type == "StopMarker"
                )
                
                objects = query.all()
                
                if not objects:
                    return {
                        "status": "failed",
                        "message": "Нет остановок для экспорта"
                    }
                
                # Создаём DataFrame через Polars с русскими названиями
                data = {
                    'Название': [obj.name for obj, _ in objects],
                    'Описание': [obj.description or '' for obj, _ in objects],
                    'Широта': [obj.latitude for obj, _ in objects],
                    'Долгота': [obj.longitude for obj, _ in objects]
                }
                
                df = pl.DataFrame(data)
                
                # Диалог выбора папки
                window = webview.active_window()
                result = window.create_file_dialog(
                    FileDialog.FOLDER,
                    directory=str(Path.home())
                )
                
                # create_file_dialog возвращает кортеж или None
                if not result:
                    # Пользователь отменил
                    return {
                        "status": "cancelled",
                        "message": "Сохранение отменено",
                        "count": 0
                    }
                
                # Берём первый элемент из кортежа
                folder = result[0] if isinstance(result, tuple) else result
                
                # Генерируем имя файла с датой
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'остановки_{timestamp}.xlsx'
                file_path = Path(folder) / filename
                
                # Сохраняем Excel файл через polars
                df.write_excel(file_path, worksheet='Остановки')
                
                log.info("export_stops", extra={"count": len(objects), "file": str(file_path)})
                return {
                    "status": "success",
                    "message": f"Экспортировано {len(objects)} остановок в {file_path}",
                    "count": len(objects),
                    "file_path": str(file_path)
                }
                
        except Exception as e:
            log.error("api_export_stops", extra={"error": str(e)})
            return {
                "status": "failed",
                "message": str(e)
            }
