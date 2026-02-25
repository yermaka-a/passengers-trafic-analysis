from ..schemas import (
    ObjectCreate,
    AllObjectsResponse,
    ObjectResponse,
)
from pydantic import TypeAdapter, ValidationError, UUID6
from ..storage import Storage
from ..logger import log


class ObjectController:

    def __init__(self, storage: Storage) -> None:
        if storage.objects is None:
            raise Exception("storage.objects not created")
        self.objects = storage.objects

    def get_object(self, data):
        try:
            id_validator = TypeAdapter(UUID6)
            Id = id_validator.validate_python(data.Id)
            obj = self.objects.get(Id)
            if obj is not None:
                validated_obj = ObjectCreate.from_db(obj)
                return ObjectResponse(status="success", obj=validated_obj)
            return ObjectResponse(status="failed", obj=None)
        except Exception as e:
            op = "get_object"
            log.error(op, {"err": e})

    def create_object(self, data):
        try:
            obj_data = ObjectCreate(**data)
            res = self.objects.create(obj_data)
            if res:
                return {"status": "success", "message": obj_data.options.Id}
            return {"satus": "failed", "message": "data is not written"}
        except ValidationError as e:
            return {"status": "failed", "message": e.json()}

    def get_all_objects(self):
        try:
            objects = self.objects.get_all_objects()
            if objects is not None:
                validated_objects = [ObjectCreate.from_db(obj) for obj in objects]

                return AllObjectsResponse(
                    status="success", objects=validated_objects
                ).model_dump(by_alias=True)
        except Exception as e:
            op = "get_all_objects"
            log.error(op, {"err": e})

    def delete_object(self, Id: UUID6):
        try:
            id_validator = TypeAdapter(UUID6)
            Id = id_validator.validate_python(Id)
            return self.objects.delete(Id)
        except Exception as e:
            op = "delete_object"
            log.error(op, {"err": e})

    def update_object(self, data):
        try:
            obj_data = ObjectCreate(**data)
            res = self.objects.update(obj_data)
            if res:
                return {"status": "success", "message": obj_data.options.Id}
            return {"satus": "failed", "message": "data is not written"}
        except ValidationError as e:
            op = "update_object"
            log.error(op, {"err": e})
            return {"status": "failed", "message": e.errors()}

    def delete_all_objects(self):
        pass
