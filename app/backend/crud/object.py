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
        self.api = None  # Будет установлен из app.py

    def set_api(self, api):
        """Установить ссылку на API для broadcast"""
        self.api = api

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
                # Синхронизируем ВСЕ окна (включая отправителя)
                if self.api:
                    self.api.sync_windows('OBJECT_CREATED', {'id': str(obj_data.options.Id)})
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
            result = self.objects.delete(Id)
            # Синхронизируем ВСЕ окна (включая отправителя)
            if self.api:
                self.api.sync_windows('OBJECT_DELETED', {'id': str(Id)})
            return result
        except Exception as e:
            op = "delete_object"
            log.error(op, {"err": e})

    def update_object(self, data):
        try:
            obj_data = ObjectCreate(**data)
            res = self.objects.update(obj_data)
            if res:
                # Синхронизируем ВСЕ окна (включая отправителя)
                if self.api:
                    self.api.sync_windows('OBJECT_UPDATED', {'id': str(obj_data.options.Id)})
                return {"status": "success", "message": obj_data.options.Id}
            return {"satus": "failed", "message": "data is not written"}
        except ValidationError as e:
            op = "update_object"
            log.error(op, {"err": e})
            return {"status": "failed", "message": e.errors()}

    def set_object_type(self, option: list):
        """Установить тип объекта и синхронизировать"""
        try:
            # Синхронизируем все окна
            if self.api:
                self.api.sync_chosen_type(option)
            return {"status": "success", "option": option}
        except Exception as e:
            op = "set_object_type"
            log.error(op, {"err": e})
            return {"status": "failed", "message": str(e)}

    def delete_all_objects(self):
        pass
