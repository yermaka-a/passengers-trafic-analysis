import webview
from .crud import (
    ObjectController,
    LogsController,
    TileLayerController,
    StopImportController,
    ObjectRelationsController,
    PassengerFlowController,
    RoutesController,
)
from .storage import Storage
from .schemas.stop_import import StopImportRequest
from .logger import log
from .services import SpatialService
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
        self.relations = ObjectRelationsController(storage)
        self.passenger_flow = PassengerFlowController(storage)
        self.routes = RoutesController(storage)
        self.spatial = SpatialService()
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

        # Маршруты Vue Router для отдельных панелей (hash router)
        routes = {
            'map': '/#/map',
            'list': '/#/list',
            'brushTable': '/#/brush',
        }

        route = routes.get(panel_id, '/#/map')
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
            from webview import FileDialog
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
                dialog_type=FileDialog.SAVE,
                directory=str(Path.home()),
                save_filename=f"geometry_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not result:
                return {
                    "status": "cancelled",
                    "message": "Экспорт отменён пользователем"
                }
            
            file_path = result[0] if isinstance(result, tuple) else result
            
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
            from webview import FileDialog
            from pathlib import Path
            
            # Диалог выбора файла
            window = webview.active_window()
            result = window.create_file_dialog(
                dialog_type=FileDialog.OPEN,
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
            
            # Helper для конвертации RGBA в hex
            def rgba_to_hex(rgba):
                if isinstance(rgba, str):
                    return rgba
                if isinstance(rgba, list) and len(rgba) >= 3:
                    return f"#{int(rgba[0]):02x}{int(rgba[1]):02x}{int(rgba[2]):02x}"
                return "#000000"
            
            for idx, obj in enumerate(export_data["objects"]):
                try:
                    # Генерируем новый UUID для объекта
                    from uuid import uuid4
                    new_id = str(uuid4())
                    
                    # Конвертируем формат экспорта в формат ObjectCreate
                    obj_type = obj.get("type")
                    style = obj.get("style", {})
                    import_obj = {
                        "latlng": [{"lat": c[1], "lng": c[0]} for c in obj.get("coordinates", [])],
                        "options": {
                            "Id": new_id,
                            "objType": obj_type,
                            "name": obj.get("name", ""),
                            "description": obj.get("description", ""),
                            "color": rgba_to_hex(style.get("color")),
                            "stroke": style.get("strokeWidth", 0) > 0,
                            "weight": style.get("strokeWidth", 2),
                            "fill": style.get("filled", False),
                            "fillOpacity": style.get("fillOpacity", 0.5),
                            "dashArray": style.get("strokeDasharray"),
                            # Для StopMarker/CircleMarker
                            "markerType": obj.get("markerType"),
                            "radius": style.get("radius"),
                        }
                    }
                    
                    log.info("import_geometry_creating", extra={"idx": idx, "old_id": obj.get("id"), "new_id": new_id, "type": obj_type})
                    result = self.objects.create_object(import_obj)
                    # create_object возвращает {"status": "success", ...} или {"status": "failed", ...}
                    if result and result.get("status") == "success":
                        imported_count += 1
                        log.info("import_geometry_created", extra={"idx": idx, "new_id": new_id})
                        # Синхронизируем окна
                        if self.objects.api:
                            self.objects.api.sync_windows('OBJECT_CREATED', {'id': new_id})
                    else:
                        failed_count += 1
                        log.error("import_geometry_create_failed", extra={"old_id": obj.get("id"), "new_id": new_id, "result": result})
                except Exception as e:
                    log.error("import_geometry_object", extra={"error": str(e), "old_id": obj.get("id"), "traceback": __import__('traceback').format_exc()})
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
                if hasattr(obj, 'obj_type') and obj.obj_type == obj_type:
                    try:
                        obj_id = UUID(obj.uuid)
                        self.storage.objects.delete(obj_id)
                        deleted_count += 1
                        # Синхронизируем окна
                        if self.objects.api:
                            self.objects.api.sync_windows('OBJECT_DELETED', {'id': str(obj_id)})
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

    # ========================================================================
    # Связи между объектами (Object Relations)
    # ========================================================================

    def add_object_relation(self, data: dict):
        """
        Добавить связь между объектами
        
        Args:
            data: {"parent_id": "...", "child_id": "...", "relation_type": "CONTAINS"}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.relations.add_relation(
                data.get("parent_id"),
                data.get("child_id"),
                data.get("relation_type", "CONTAINS")
            )
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_add_object_relation", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def remove_object_relation(self, data: dict):
        """
        Удалить связь между объектами
        
        Args:
            data: {"parent_id": "...", "child_id": "..."}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.relations.remove_relation(
                data.get("parent_id"),
                data.get("child_id")
            )
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_remove_object_relation", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_polygon_stops(self, data: dict):
        """
        Получить все остановки в полигоне/полилинии
        
        Args:
            data: {"polygon_id": "..."}
            
        Returns:
            {"status": "success", "stops": [...]}
        """
        try:
            children = self.relations.get_children(data.get("polygon_id"))
            
            stops = []
            for child in children:
                if child.obj_type == 'StopMarker':
                    stops.append({
                        "id": child.uuid,
                        "name": child.name,
                        "lat": child.latitude,
                        "lng": child.longitude,
                        "obj_type": child.obj_type
                    })
            
            return {"status": "success", "stops": stops}
        except Exception as e:
            log.error("api_get_polygon_stops", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def auto_assign_stops(self, data: dict):
        """
        Автоматически назначить остановки полигонам/полилиниям

        Args:
            data: {"tolerance_meters": 50} (для полилиний)

        Returns:
            {"status": "success", "assigned": N}
        """
        try:
            tolerance = data.get("tolerance_meters", 50)

            # Получаем все объекты
            all_objects = self.storage.objects.get_all_objects()

            polygons = [o for o in all_objects if o.obj_type == 'Polygon']
            polylines = [o for o in all_objects if o.obj_type == 'Polyline']
            stops = [o for o in all_objects if o.obj_type == 'StopMarker']

            log.info("auto_assign_stops: объекты", extra={
                "polygons": len(polygons),
                "polylines": len(polylines),
                "stops": len(stops)
            })

            assigned_count = 0

            # Для каждого полигона находим остановки внутри
            for polygon in polygons:
                coords = polygon.latlng
                stops_in_polygon = self.spatial.find_stops_in_polygon(
                    [{"id": s.uuid, "lat": s.latitude, "lng": s.longitude} for s in stops if s.latitude and s.longitude],
                    coords
                )

                log.info("auto_assign_stops: полигон", extra={
                    "polygon_id": polygon.uuid,
                    "polygon_name": polygon.name,
                    "stops_found": len(stops_in_polygon)
                })

                for stop_data in stops_in_polygon:
                    # Используем UUID строки - add_relation сам сконвертирует
                    if self.relations.add_relation(polygon.uuid, stop_data["id"], "CONTAINS"):
                        assigned_count += 1

            # Для каждой полилинии находим остановки рядом
            for polyline in polylines:
                coords = polyline.latlng
                stops_near_line = self.spatial.find_stops_near_polyline(
                    [{"id": s.uuid, "lat": s.latitude, "lng": s.longitude} for s in stops if s.latitude and s.longitude],
                    coords,
                    tolerance
                )

                log.info("auto_assign_stops: полилиния", extra={
                    "polyline_id": polyline.uuid,
                    "polyline_name": polyline.name,
                    "stops_found": len(stops_near_line)
                })

                for stop_data in stops_near_line:
                    if self.relations.add_relation(polyline.uuid, stop_data["id"], "NEAR"):
                        assigned_count += 1

            log.info("auto_assign_stops", extra={"assigned": assigned_count})
            return {"status": "success", "assigned": assigned_count}

        except Exception as e:
            log.error("api_auto_assign_stops", extra={"error": str(e), "traceback": __import__('traceback').format_exc()})
            return {"status": "failed", "message": str(e)}

    # ========================================================================
    # Пассажиропоток (Passenger Flow)
    # ========================================================================

    def create_passenger_flow(self, data: dict):
        """
        Создать пассажиропоток
        
        Args:
            data: {
                "name": "...",
                "date": "YYYY-MM-DD",
                "time_period": "morning_peak",
                "direction": "forward",
                "description": "...",
                "route_id": "...",
                "stops": [{"stop_id": "...", "order": 1, "passengers_on_board": 10, "passengers_off_board": 5}, ...]
            }
            
        Returns:
            {"status": "success", "flow_id": "..."}
        """
        try:
            flow_id = self.passenger_flow.create_flow(
                name=data.get("name"),
                date=data.get("date"),
                time_period=data.get("time_period", "off_peak"),
                direction=data.get("direction", "forward"),
                description=data.get("description"),
                route_id=data.get("route_id"),
                stops_list=data.get("stops")
            )
            if flow_id:
                return {"status": "success", "flow_id": flow_id}
            else:
                return {"status": "failed", "message": "Не удалось создать поток"}
        except Exception as e:
            log.error("api_create_passenger_flow", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_passenger_flow(self, data: dict):
        """
        Получить пассажиропоток
        
        Args:
            data: {"flow_id": "..."}
            
        Returns:
            {"status": "success", "flow": {...}}
        """
        try:
            flow = self.passenger_flow.get_flow(data.get("flow_id"))
            if flow:
                return {"status": "success", "flow": flow}
            else:
                return {"status": "failed", "message": "Поток не найден"}
        except Exception as e:
            log.error("api_get_passenger_flow", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def update_passenger_flow(self, data: dict):
        """
        Обновить пассажиропоток
        
        Args:
            data: {
                "flow_id": "...",
                "name": "...",
                "date": "...",
                "time_period": "...",
                "direction": "...",
                "description": "...",
                "stops": [...]
            }
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.passenger_flow.update_flow(
                flow_id=data.get("flow_id"),
                name=data.get("name"),
                date=data.get("date"),
                time_period=data.get("time_period"),
                direction=data.get("direction"),
                description=data.get("description"),
                stops_list=data.get("stops")
            )
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_update_passenger_flow", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def delete_passenger_flow(self, data: dict):
        """
        Удалить пассажиропоток
        
        Args:
            data: {"flow_id": "..."}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.passenger_flow.delete_flow(data.get("flow_id"))
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_delete_passenger_flow", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_all_passenger_flows(self, data: dict):
        """
        Получить все пассажиропотоки

        Args:
            data: {"date_from": "YYYY-MM-DD", "date_to": "YYYY-MM-DD"}

        Returns:
            {"status": "success", "flows": [...]}
        """
        try:
            flows = self.passenger_flow.get_all_flows(
                date_from=data.get("date_from"),
                date_to=data.get("date_to")
            )
            return {"status": "success", "flows": flows}
        except Exception as e:
            log.error("api_get_all_passenger_flows", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_passenger_flows_with_coordinates(self, data: dict = None):
        """
        Получить все пассажиропотоки с координатами для визуализации

        Returns:
            {"status": "success", "flows": [...]}
        """
        try:
            flows = self.passenger_flow.get_flows_with_coordinates()
            return {"status": "success", "flows": flows}
        except Exception as e:
            log.error("api_get_passenger_flows_with_coordinates", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_flows_by_route(self, data: dict):
        """
        Получить все потоки для маршрута
        
        Args:
            data: {"route_id": "...", "date": "YYYY-MM-DD"}
            
        Returns:
            {"status": "success", "flows": [...]}
        """
        try:
            flows = self.passenger_flow.get_flows_by_route(
                route_id=data.get("route_id"),
                date=data.get("date")
            )
            return {"status": "success", "flows": flows}
        except Exception as e:
            log.error("api_get_flows_by_route", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    # ========================================================================
    # Маршруты (Routes)
    # ========================================================================

    def create_route(self, data: dict):
        """
        Создать маршрут
        
        Args:
            data: {"name": "...", "description": "...", "stops": [{"stop_id": "...", "order": 1}, ...]}
            
        Returns:
            {"status": "success", "route_id": "..."}
        """
        try:
            route_id = self.routes.create_route(
                data.get("name"),
                data.get("description"),
                data.get("stops")
            )
            if route_id:
                return {"status": "success", "route_id": route_id}
            else:
                return {"status": "failed", "message": "Не удалось создать маршрут"}
        except Exception as e:
            log.error("api_create_route", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_route(self, data: dict):
        """
        Получить маршрут
        
        Args:
            data: {"route_id": "..."}
            
        Returns:
            {"status": "success", "route": {...}}
        """
        try:
            route = self.routes.get_route(data.get("route_id"))
            if route:
                return {"status": "success", "route": route}
            else:
                return {"status": "failed", "message": "Маршрут не найден"}
        except Exception as e:
            log.error("api_get_route", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def update_route(self, data: dict):
        """
        Обновить маршрут
        
        Args:
            data: {"route_id": "...", "name": "...", "description": "...", "stops": [...]}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.routes.update_route(
                data.get("route_id"),
                data.get("name"),
                data.get("description"),
                data.get("stops")
            )
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_update_route", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def delete_route(self, data: dict):
        """
        Удалить маршрут
        
        Args:
            data: {"route_id": "..."}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.routes.delete_route(data.get("route_id"))
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_delete_route", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def get_all_routes(self, data: dict):
        """
        Получить все маршруты
        
        Returns:
            {"status": "success", "routes": [...]}
        """
        try:
            routes = self.routes.get_all_routes()
            return {"status": "success", "routes": routes}
        except Exception as e:
            log.error("api_get_all_routes", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def reorder_route_stops(self, data: dict):
        """
        Изменить порядок остановок в маршруте
        
        Args:
            data: {"route_id": "...", "stop_id": "...", "new_order": N}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.routes.reorder_stops(
                data.get("route_id"),
                data.get("stop_id"),
                data.get("new_order")
            )
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_reorder_route_stops", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

    def toggle_route_direction(self, data: dict):
        """
        Переключить направление маршрута
        
        Args:
            data: {"route_id": "..."}
            
        Returns:
            {"status": "success" | "failed"}
        """
        try:
            result = self.routes.toggle_direction(data.get("route_id"))
            return {"status": "success" if result else "failed"}
        except Exception as e:
            log.error("api_toggle_route_direction", extra={"error": str(e)})
            return {"status": "failed", "message": str(e)}

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
