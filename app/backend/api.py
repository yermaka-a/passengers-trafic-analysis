import webview
from .crud import ObjectController, LogsController
from .storage import Storage


class Api:
    def __init__(self, storage: Storage) -> None:
        self.objects = ObjectController(storage)
        self.logs = LogsController()
        self._windows = []  # Храним ссылки на окна

    def open_panel_window(self, panel_id: str):
        """Открыть панель в отдельном окне pywebview"""
        # URL для отдельной панели
        url = f"http://localhost:5173/?panel={panel_id}"
        
        # Заголовки окон
        titles = {
            'map': 'Карта - Passenger Traffic Analysis',
            'list': 'Список объектов - Passenger Traffic Analysis',
            'brushTable': 'Инструменты - Passenger Traffic Analysis',
        }
        
        title = titles.get(panel_id, 'Panel - Passenger Traffic Analysis')
        
        # Создаём новое окно
        window = webview.create_window(
            title,
            url,
            width=1000,
            height=700,
            resizable=True,
        )
        
        self._windows.append(window)
        return {'status': 'success', 'window': 'created'}
