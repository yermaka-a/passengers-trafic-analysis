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
                log.info("get_all_objects", extra={"count": len(objects)})
                return objects
        except Exception as e:
            op_method = "get_all_objects"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return None

    def get(self, Id: UUID6):
        try:
            with self.localSession() as ls:
                log.info("get_object", extra={"Id": str(Id)})
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
                log.info(
                    "create_object",
                    extra={
                        "Id": options.Id,
                        "name": options.name,
                        "obj_type": options.obj_type,
                        "dash_array": options.dash_array,
                    },
                )
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
                    dash_array=options.dash_array,
                    marker_type=options.marker_type,  # ← Добавлено!
                )

                ls.add(new_obj)
                ls.commit()
                log.info("create_object_success", extra={"Id": options.Id})
            return True
        except Exception as e:
            op_method = "create"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False

    def delete(self, Id: UUID6):
        try:
            with self.localSession() as ls:
                log.info("delete_object", extra={"Id": str(Id)})
                ls.execute(delete(MapObject).where(MapObject.Id == str(Id)))
                ls.commit()
                log.info("delete_object_success", extra={"Id": str(Id)})
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
                log.info(
                    "update_object",
                    extra={
                        "Id": options.Id,
                        "name": options.name,
                        "color": options.color,
                        "weight": options.weight,
                        "fill": options.fill,
                        "fill_opacity": options.fill_opacity,
                        "dash_array": options.dash_array,
                    },
                )
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
                    marker_type=options.marker_type,  # ← Добавлено!
                )

                ls.merge(updated_obj)
                ls.commit()
                log.info("update_object_success", extra={"Id": options.Id})
            return True
        except Exception as e:
            op_method = "update"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False
