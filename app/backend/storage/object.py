from ..schemas import ObjectCreate
from sqlalchemy.orm import sessionmaker, Session
from ..logger import logger
from ..models import MapObject

OP_CLASS_MSG = f"{__name__} class Objects "


class Objects:

    def __init__(self, localSession: sessionmaker[Session]):
        self.localSession = localSession

    def get_all_objects(self):
        try:
            with self.localSession() as ls:
                objects = ls.query(MapObject).all()
                print(objects)
                return objects
        except Exception as e:
            op_method = "get_all_objects"
            logger.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return None

    def get(self, Id: str):
        try:
            with self.localSession() as ls:
                obj = ls.get(MapObject, Id)
                return obj
        except Exception as e:
            op_method = "get"
            logger.error(OP_CLASS_MSG + op_method, extra={"error": e})
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
            logger.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False
