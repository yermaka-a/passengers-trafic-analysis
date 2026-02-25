from pydantic import UUID6
from sqlalchemy import delete

from ..schemas import ObjectCreate
from sqlalchemy.orm import sessionmaker, Session
from ..logger import log
from ..models import MapObject

OP_CLASS_MSG = f"{__name__} class Objects "


class Objects:

    def __init__(self, localSession: sessionmaker[Session]):
        self.localSession = localSession

    def get_all_objects(self):
        try:
            with self.localSession() as ls:
                objects = ls.query(MapObject).all()
                return objects
        except Exception as e:
            op_method = "get_all_objects"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return None

    def get(self, Id: UUID6):
        try:
            with self.localSession() as ls:
                obj = ls.get(MapObject, str(Id))
                return obj
        except Exception as e:
            op_method = "get"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return None

    def create(self, obj: ObjectCreate):
        try:
            with self.localSession() as ls:

                options = obj.options
                latlng = [p.model_dump() for p in obj.latlng]
                new_obj = MapObject(
                    Id=options.Id,
                    color=options.color,
                    custom_name=options.custom_name,
                    description=options.description,
                    fill=options.fill,
                    fill_opacity=options.fill_opacity,
                    name=options.name,
                    stroke=options.stroke,
                    weight=options.weight,
                    latlng=latlng,
                    obj_type=options.obj_type,
                )

                ls.add(new_obj)
                ls.commit()
            return True
        except Exception as e:
            op_method = "create"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False

    def delete(self, Id: UUID6):
        try:
            with self.localSession() as ls:
                ls.execute(delete(MapObject).where(MapObject.Id == str(Id)))
                ls.commit()
            return True
        except Exception as e:
            op_method = "delete"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False

    def update(self, obj: ObjectCreate):
        try:
            with self.localSession() as ls:

                options = obj.options
                latlng = [p.model_dump() for p in obj.latlng]
                updated_obj = MapObject(
                    Id=options.Id,
                    color=options.color,
                    custom_name=options.custom_name,
                    description=options.description,
                    fill=options.fill,
                    fill_opacity=options.fill_opacity,
                    name=options.name,
                    stroke=options.stroke,
                    weight=options.weight,
                    latlng=latlng,
                    obj_type=options.obj_type,
                    dash_array=options.dash_array,
                )

                ls.merge(updated_obj)
                ls.commit()
            return True
        except Exception as e:
            op_method = "update"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False
