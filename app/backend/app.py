import socket
import os
from sqlalchemy import create_engine
import webview
from .storage import Storage
from .api import Api


class App:
    # Настройки разработки

    def __init__(self) -> None:
        # Стандартный порт Vite
        self.VITE_DEV_URL = "http://localhost:5173"

    def __is_nuitka(self):
        """Проверяет, запущен ли код в скомпилированном виде (Nuitka)"""
        return "__compiled__" in globals()

    def __is_vite_running(self, url: str):
        """Проверяет, поднят ли сервер Vite на указанном порту"""
        host = url.split("//")[-1].split(":")[0]
        port = int(url.split(":")[-1])
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except:  # noqa: E722
            return False

    def __get_entrypoint(self):
        """Автоматически выбирает: сервер Vite или собранный index.html"""

        # 1. Если это скомпилированный бинарник — всегда берем локальный файл
        if self.__is_nuitka():
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
            return os.path.join(project_root, "app", "frontend", "dist", "index.html")

        # 2. Если мы в режиме разработки — проверяем, запущен ли Vite
        if self.__is_vite_running(self.VITE_DEV_URL):
            print(f"[*] Подключено к Vite Dev Server: {self.VITE_DEV_URL}")
            return self.VITE_DEV_URL

        # 3. Если Vite не запущен, пробуем найти последний билд
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_file_dir, "..", ".."))
        index_path = os.path.join(project_root, "app", "frontend", "dist", "index.html")

        if os.path.exists(index_path):
            print("[!] Vite не запущен. Загружаю из папки dist.")
            return index_path

        raise RuntimeError("Ни сервер Vite, ни папка dist/index.html не найдены!")

    def start(self):
        url = app.__get_entrypoint()
        DB_PATH = os.path.join(Storage.get_base_dir(), "passengers.db")
        DATABASE_URL = f"sqlite:///{DB_PATH}"

        engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        storage = Storage.create(engine)
        api = Api(storage)

        # Устанавливаем ссылку на api в контроллере
        api.objects.set_api(api)

        # Главное окно - регистрируем API и сохраняем ссылку
        window = webview.create_window(
            "passengers trafic analysis",
            url,
            js_api=api,  # Регистрируем API для главного окна
            width=1200,
            height=800,
        )
        
        # Сохраняем главное окно для синхронизации
        api.set_main_window(window)

        # Запускаем приложение
        # Все новые окна будут созданы через api.open_panel_window()
        debug_mode = not self.__is_nuitka()
        webview.start(debug=debug_mode)


app = App()
