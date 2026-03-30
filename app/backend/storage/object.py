"""
Storage для оптимизированной схемы БД

Работа с разделёнными таблицами:
- map_objects (базовая информация)
- stop_metadata (данные для StopMarker)
- object_styles (стили для Polygon/Polyline/CircleMarker)
"""
from pydantic import UUID6
from sqlalchemy import delete
from sqlalchemy.orm import sessionmaker, Session, joinedload

from ..schemas import ObjectCreate
from ..logger import log
from ..models import MapObject, StopMetadata, ObjectStyles

OP_CLASS_MSG = f"{__name__} class Objects "


class Objects:

    def __init__(self, localSession: sessionmaker[Session]):
        self.localSession = localSession

    def get_all_objects(self):
        """Получить все объекты с связанными данными"""
        try:
            with self.localSession() as ls:
                # Загружаем связанные данные через joinedload
                objects = ls.query(MapObject)\
                    .options(
                        joinedload(MapObject.stop_metadata),
                        joinedload(MapObject.object_styles)
                    )\
                    .all()
                log.info("get_all_objects", extra={"count": len(objects)})
                return objects
        except Exception as e:
            op_method = "get_all_objects"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return []

    def get(self, Id: UUID6):
        """Получить объект по ID с связанными данными"""
        try:
            with self.localSession() as ls:
                log.info("get_object", extra={"Id": str(Id)})
                obj = ls.query(MapObject)\
                    .options(
                        joinedload(MapObject.stop_metadata),
                        joinedload(MapObject.object_styles)
                    )\
                    .get(str(Id))
                return obj
        except Exception as e:
            op_method = "get"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return None

    def create(self, obj: ObjectCreate):
        """Создать объект с связанными данными"""
        try:
            with self.localSession() as ls:
                options = obj.options
                latlng = [p.model_dump() for p in obj.latlng]

                # Извлечь первую координату для latitude/longitude
                latitude = latlng[0]['lat'] if latlng else None
                longitude = latlng[0]['lng'] if latlng else None

                is_stop_marker = options.obj_type == 'StopMarker'
                is_circle_marker = options.obj_type == 'CircleMarker'

                log.info(
                    "create_object",
                    extra={
                        "Id": options.Id,
                        "name": options.name,
                        "obj_type": options.obj_type,
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )

                # Создаём базовый объект
                log.info("create_object_before", extra={
                    "options_Id": options.Id,
                    "options_osm_id": getattr(options, 'osm_id', None),
                    "obj_type": options.obj_type
                })
                
                new_obj = MapObject(
                    id=str(options.Id),
                    name=options.name,
                    obj_type=options.obj_type,
                    latitude=latitude,
                    longitude=longitude,
                    latlng=latlng,
                )
                ls.add(new_obj)
                ls.flush()  # Получаем ID

                # Создаём связанные данные
                if is_stop_marker:
                    stop_meta = StopMetadata(
                        object_id=new_obj.id,
                        osm_id=getattr(options, 'osm_id', None),
                        marker_type=options.marker_type,
                        radius=options.radius,
                        color=options.color,
                    )
                    ls.add(stop_meta)
                elif is_circle_marker or options.obj_type in ('Polygon', 'Polyline'):
                    styles = ObjectStyles(
                        object_id=new_obj.id,
                        stroke=options.stroke,
                        weight=options.weight,
                        fill=options.fill,
                        fill_opacity=options.fill_opacity,
                        dash_array=options.dash_array,
                        color=options.color,
                    )
                    ls.add(styles)

                ls.commit()
                log.info("create_object_success", extra={"Id": options.Id})
            return True
        except Exception as e:
            op_method = "create"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False

    def delete(self, Id):
        """Удалить объект (CASCADE удалит связанные данные)"""
        try:
            from uuid import UUID
            # Конвертируем строку в UUID если нужно
            if isinstance(Id, str):
                Id = UUID(Id)
                
            with self.localSession() as ls:
                ls.execute(delete(MapObject).where(MapObject.id == str(Id)))
                ls.commit()
                log.info("delete_object_success", extra={"Id": str(Id)})
                return True
        except Exception as e:
            op_method = "delete"
            log.error(OP_CLASS_MSG + op_method, extra={"error": str(e)})
            return False

    def update(self, obj: ObjectCreate):
        """Обновить объект и связанные данные"""
        try:
            with self.localSession() as ls:
                options = obj.options
                latlng = [p.model_dump() for p in obj.latlng]

                # Извлечь первую координату
                latitude = latlng[0]['lat'] if latlng else None
                longitude = latlng[0]['lng'] if latlng else None

                is_stop_marker = options.obj_type == 'StopMarker'
                is_circle_marker = options.obj_type == 'CircleMarker'

                log.info(
                    "update_object",
                    extra={
                        "Id": options.Id,
                        "name": options.name,
                        "description": options.description,
                        "obj_type": options.obj_type,
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                )

                # Обновляем базовый объект
                updated_obj = MapObject(
                    id=str(options.Id),
                    name=options.name,
                    obj_type=options.obj_type,
                    description=options.description,
                    latitude=latitude,
                    longitude=longitude,
                    latlng=latlng,
                )
                ls.merge(updated_obj)

                # Удаляем старые связанные данные
                ls.execute(delete(StopMetadata).where(StopMetadata.object_id == str(options.Id)))
                ls.execute(delete(ObjectStyles).where(ObjectStyles.object_id == str(options.Id)))

                # Создаём новые связанные данные
                if is_stop_marker:
                    stop_meta = StopMetadata(
                        object_id=updated_obj.id,
                        osm_id=getattr(options, 'osm_id', None),
                        marker_type=options.marker_type,
                        radius=options.radius,
                        color=options.color,
                    )
                    ls.add(stop_meta)
                elif is_circle_marker or options.obj_type in ('Polygon', 'Polyline'):
                    styles = ObjectStyles(
                        object_id=updated_obj.id,
                        stroke=options.stroke,
                        weight=options.weight,
                        fill=options.fill,
                        fill_opacity=options.fill_opacity,
                        dash_array=options.dash_array,
                        color=options.color,
                    )
                    ls.add(styles)

                ls.commit()
                log.info("update_object_success", extra={"Id": options.Id})
            return True
        except Exception as e:
            op_method = "update"
            log.error(OP_CLASS_MSG + op_method, extra={"error": e})
            return False
