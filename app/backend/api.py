from .crud import ObjectController
from .storage import Storage


class Api:
    def __init__(self, storage: Storage) -> None:
        self.objects = ObjectController(storage)
