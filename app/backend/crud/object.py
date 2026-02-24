from ..schemas import ObjectCreate
from pydantic import ValidationError
from ..storage import Storage


class ObjectController:

    def __init__(self, storage: Storage) -> None:
        if storage.objects is None:
            raise Exception("storage.objects not created")
        self.objects = storage.objects

    def create_object(self, data):

        try:
            obj_data = ObjectCreate(**data)
            print(obj_data.model_dump_json())
            res = self.objects.create(obj_data)
            if res:
                return {"status": "success", "message": obj_data.options.Id}
            return {"satus": "failed", "message": "data is not written"}
        except ValidationError as e:
            print(e)
            return {"status": "failed", "message": e.json()}

    def delete_object(self):
        pass

    def update_object(self):
        pass

    def delete_all_objects(self):
        pass
