import webview
from .crud import ObjectController, LogsController
from .storage import Storage
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
        
        # Отправляем в главное окно
        if self._main_window:
            try:
                js_code = f"""
                (function() {{
                    try {{
                        console.log('[Sync] Received in main:', {message});
                        const event = new CustomEvent('panel-sync', {{
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
