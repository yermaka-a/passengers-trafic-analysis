from .crud import ObjectController, LogsController
from .storage import Storage


class Api:
    def __init__(self, storage: Storage) -> None:
        self.objects = ObjectController(storage)
        self.logs = LogsController()
