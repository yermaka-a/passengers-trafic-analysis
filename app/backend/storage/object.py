from ..schemas import ObjectCreate
from sqlalchemy.orm import sessionmaker, Session

from ..models import MapObject


class Objects:
    def __init__(self, localSession: sessionmaker[Session]):
        self.localSession = localSession

    def create(self, obj: ObjectCreate):
        try:
            with self.localSession() as ls:

                options = obj.options
                latlng = [p.model_dump() for p in obj.latlng]
                new_obj = MapObject(
                    Id=options.Id,
                    color=options.color,
                    custom_name=options.customName,
                    description=options.description,
                    fill=options.fill,
                    fill_opacity=options.fillOpacity,
                    name=options.name,
                    order=options.order,
                    stroke=options.stroke,
                    weight=options.weight,
                    latlng=latlng,
                )

                ls.add(new_obj)
                ls.commit()
            return True
        except Exception as e:
            print("exception:", e)
            return False
