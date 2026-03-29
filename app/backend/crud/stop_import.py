"""
CRUD для пакетного импорта остановок из Overpass API

Использует SQLAlchemy bulk_insert_mappings для высокой производительности
"""
import asyncio
from typing import List, Tuple
from uuid import uuid4

from ..services.overpass_client import OverpassClient
from ..schemas.stop_import import OverpassStop, StopImportResponse
from ..models.object import MapObject, StopMetadata
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
            
            # Считаем общее количество дубликатов (из дедупликации + из БД)
            duplicates_from_dedup = len(overpass_stops) - len(unique_stops)
            duplicates_from_db = len(unique_stops) - imported_count
            total_duplicates = duplicates_from_dedup + duplicates_from_db

            log.info("stop_import_complete", extra={
                "imported": imported_count,
                "cities": cities,
                "duplicates": total_duplicates
            })

            return StopImportResponse(
                status="success",
                imported_count=imported_count,
                duplicate_count=total_duplicates,
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
                id=str(uuid4()),
                name=stop.name[:255] if stop.name else f"Остановка {stop.osm_id}",
                obj_type="StopMarker",
                latitude=stop.lat,
                longitude=stop.lon,
                latlng=[{"lat": stop.lat, "lng": stop.lon}],
            )
            # Создаём связанные метаданные
            map_obj.stop_metadata = StopMetadata(
                object_id=map_obj.id,
                osm_id=stop.osm_id,
                marker_type="pin",
                radius=30,
                color="#FF0000",
            )
            map_objects.append(map_obj)
        
        log.info("stop_import_convert", extra={"count": len(map_objects)})
        return map_objects
    
    def _bulk_insert(self, objects: List[MapObject]) -> int:
        """
        Массовая вставка объектов

        Args:
            objects: Список MapObject для вставки

        Returns:
            Количество вставленных объектов
        """
        if not objects:
            return 0

        with self.storage.localSession() as session:
            # 1. Проверка на дубликаты по osm_id
            log.info("stop_import_check_duplicates", extra={"count": len(objects)})

            # Собрать osm_id для проверки
            osm_ids = [obj.stop_metadata.osm_id for obj in objects if obj.stop_metadata and obj.stop_metadata.osm_id]

            if osm_ids:
                # Найти существующие объекты с такими osm_id
                existing = session.query(StopMetadata.osm_id).filter(
                    StopMetadata.osm_id.in_(osm_ids)
                ).all()

                existing_osm_ids = {row.osm_id for row in existing}
                duplicate_count = len(objects) - len([
                    obj for obj in objects
                    if not (obj.stop_metadata and obj.stop_metadata.osm_id in existing_osm_ids)
                ])
                log.info("stop_import_existing", extra={"count": len(existing_osm_ids), "duplicates": duplicate_count})

                # Фильтровать новые объекты
                new_objects = [
                    obj for obj in objects
                    if not (obj.stop_metadata and obj.stop_metadata.osm_id in existing_osm_ids)
                ]
            else:
                new_objects = objects
                duplicate_count = 0

            log.info("stop_import_new", extra={"count": len(new_objects)})

            if not new_objects:
                return 0

            # 2. Вставка объектов
            for obj in new_objects:
                session.add(obj)

            session.commit()

            log.info("stop_import_inserted", extra={"count": len(new_objects), "duplicates": duplicate_count})
            return len(new_objects)
