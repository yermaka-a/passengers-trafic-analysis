"""
CRUD для пакетного импорта остановок из Overpass API

Использует SQLAlchemy bulk_insert_mappings для высокой производительности
"""
import asyncio
from typing import List, Tuple
from uuid import uuid4

from ..services.overpass_client import OverpassClient
from ..schemas.stop_import import OverpassStop, StopImportResponse
from ..models.object import MapObject
from ..storage import Storage
from ..logger import log


class StopImportController:
    """Контроллер для импорта остановок"""
    
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def import_stops(self, cities: List[str], stop_types: List[str]) -> StopImportResponse:
        """
        Импортировать остановки из Overpass API
        
        Args:
            cities: Список городов
            stop_types: Список типов остановок
        
        Returns:
            Результат импорта
        """
        try:
            log.info("stop_import_start", extra={"cities": cities, "stop_types": stop_types})
            
            # 1. Получить остановки из Overpass API
            overpass_stops = asyncio.run(self._fetch_overpass_stops(cities, stop_types))
            
            if not overpass_stops:
                return StopImportResponse(
                    status="failed",
                    imported_count=0,
                    duplicate_count=0,
                    cities=cities,
                    message="Остановки не найдены"
                )
            
            # 2. Дедупликация по osm_id
            unique_stops = self._deduplicate_stops(overpass_stops)
            log.info("stop_import_dedup", extra={
                "total": len(overpass_stops),
                "unique": len(unique_stops),
                "duplicates": len(overpass_stops) - len(unique_stops)
            })
            
            # 3. Конвертация в MapObject
            map_objects = self._convert_to_map_objects(unique_stops)
            
            # 4. Массовая вставка
            imported_count = self._bulk_insert(map_objects)
            
            log.info("stop_import_complete", extra={
                "imported": imported_count,
                "cities": cities
            })
            
            return StopImportResponse(
                status="success",
                imported_count=imported_count,
                duplicate_count=len(overpass_stops) - len(unique_stops),
                cities=cities
            )
            
        except Exception as e:
            log.error("stop_import_error", extra={"error": str(e)})
            return StopImportResponse(
                status="failed",
                imported_count=0,
                duplicate_count=0,
                cities=cities,
                message=str(e)
            )
    
    async def _fetch_overpass_stops(self, cities: List[str], stop_types: List[str]) -> List[OverpassStop]:
        """Получить остановки из Overpass API"""
        client = OverpassClient()
        return await client.fetch_stops(cities, stop_types)
    
    def _deduplicate_stops(self, stops: List[OverpassStop]) -> List[OverpassStop]:
        """
        Удалить дубликаты по osm_id
        
        Args:
            stops: Список остановок
        
        Returns:
            Список уникальных остановок
        """
        seen = {}
        for stop in stops:
            if stop.osm_id not in seen:
                seen[stop.osm_id] = stop
        return list(seen.values())
    
    def _convert_to_map_objects(self, stops: List[OverpassStop]) -> List[MapObject]:
        """
        Конвертировать OverpassStop в MapObject
        
        Args:
            stops: Список остановок
        
        Returns:
            Список MapObject для вставки
        """
        map_objects = []
        
        for stop in stops:
            map_obj = MapObject(
                Id=str(uuid4()),
                name=stop.name[:255] if stop.name else f"Остановка {stop.osm_id}",
                description=f"OSM {stop.osm_id}",
                custom_name=None,
                color="#FF0000",  # Красный цвет по умолчанию
                stroke=None,
                weight=None,
                fill=None,
                fill_opacity=None,
                latitude=stop.lat,
                longitude=stop.lon,
                latlng=[{"lat": stop.lat, "lng": stop.lon}],
                obj_type="StopMarker",
                dash_array=None,
                marker_type="pin",  # Маркер по умолчанию
                radius=30
            )
            map_objects.append(map_obj)
        
        log.info("stop_import_convert", extra={"count": len(map_objects)})
        return map_objects
    
    def _bulk_insert(self, objects: List[MapObject]) -> int:
        """
        Массовая вставка через bulk_insert_mappings
        
        Args:
            objects: Список MapObject для вставки
        
        Returns:
            Количество вставленных объектов
        """
        if not objects:
            return 0
        
        with self.storage.localSession() as session:
            # 1. Проверка на дубликаты в БД (по координатам)
            log.info("stop_import_check_duplicates", extra={"count": len(objects)})
            
            # Собрать координаты для проверки
            coords_set = {(obj.latitude, obj.longitude) for obj in objects if obj.latitude and obj.longitude}
            
            if coords_set:
                # Найти существующие объекты с такими координатами
                existing = session.query(MapObject.latitude, MapObject.longitude).filter(
                    MapObject.obj_type == "StopMarker",
                    MapObject.latitude.in_([lat for lat, lon in coords_set]),
                    MapObject.longitude.in_([lon for lat, lon in coords_set])
                ).all()
                
                existing_coords = {(row.latitude, row.longitude) for row in existing}
                log.info("stop_import_existing", extra={"count": len(existing_coords)})
                
                # Фильтровать новые объекты
                new_objects = [
                    obj for obj in objects
                    if (obj.latitude, obj.longitude) not in existing_coords
                ]
            else:
                new_objects = objects
            
            log.info("stop_import_new", extra={"count": len(new_objects)})
            
            if not new_objects:
                return 0
            
            # 2. Bulk insert
            mappings = [
                {
                    'Id': obj.Id,
                    'name': obj.name,
                    'description': obj.description,
                    'custom_name': obj.custom_name,
                    'color': obj.color,
                    'stroke': obj.stroke,
                    'weight': obj.weight,
                    'fill': obj.fill,
                    'fill_opacity': obj.fill_opacity,
                    'latitude': obj.latitude,
                    'longitude': obj.longitude,
                    'latlng': obj.latlng,
                    'obj_type': obj.obj_type,
                    'dash_array': obj.dash_array,
                    'marker_type': obj.marker_type,
                    'radius': obj.radius
                } for obj in new_objects
            ]
            
            session.bulk_insert_mappings(MapObject, mappings)
            session.commit()
            
            log.info("stop_import_inserted", extra={"count": len(new_objects)})
            return len(new_objects)
