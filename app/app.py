import webview


class App:
    @classmethod
    def run(cls) -> None:
        print("Running App...")
        window = webview.create_window(
            "Passenger Traffic Analysis",
            "./app/front/dist/index.html",
        )
        if isinstance(window, webview.Window):
            webview.start(http_server=True)
