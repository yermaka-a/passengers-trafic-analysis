"""
CRUD операции для маршрутов

RoutesController:
- create_route(name, description, stops_list)
- get_route(route_id)
- update_route(route_id, stops_list)
- delete_route(route_id)
- get_all_routes()
- reorder_stops(route_id, stop_id, new_order)
"""
from typing import List, Optional, Dict
from sqlalchemy import select, func
from datetime import datetime
import uuid

from ..models import Route, RouteStop, MapObject
from ..logger import log


class RoutesController:
    def __init__(self, storage):
        self.storage = storage

    def _get_session(self):
        return self.storage.localSession()

    def create_route(self, name: str, description: str = None, 
                     stops_list: List[Dict] = None) -> Optional[str]:
        """
        Создать маршрут
        
        Args:
            name: Название маршрута
            description: Описание
            stops_list: Список остановок [{"stop_id": "...", "order": 1}, ...]
            
        Returns:
            UUID маршрута или None
        """
        try:
            with self._get_session() as session:
                # Создаём маршрут
                route_id = uuid.uuid4()
                route = Route(
                    id=route_id.bytes,
                    name=name,
                    description=description or "",
                    direction="forward"
                )
                session.add(route)
                session.flush()
                
                # Добавляем остановки
                if stops_list:
                    for stop_data in stops_list:
                        stop = session.get(MapObject, uuid.UUID(stop_data["stop_id"]).bytes)
                        if stop:
                            route_stop = RouteStop(
                                route_id=route.id,
                                stop_id=stop.id,
                                stop_order=stop_data.get("order", 0)
                            )
                            session.add(route_stop)
                
                session.commit()
                
                log.info("create_route: маршрут создан", extra={
                    "route_id": str(route_id),
                    "name": name,
                    "stops_count": len(stops_list) if stops_list else 0
                })
                return str(route_id)
                
        except Exception as e:
            log.error("create_route: ошибка", extra={"error": str(e)})
            return None

    def get_route(self, route_id: str) -> Optional[Dict]:
        """
        Получить маршрут с остановками
        
        Args:
            route_id: UUID маршрута
            
        Returns:
            Dict с данными маршрута
        """
        try:
            with self._get_session() as session:
                route = session.get(Route, uuid.UUID(route_id).bytes)
                if not route:
                    log.warning("get_route: маршрут не найден", extra={
                        "route_id": route_id
                    })
                    return None
                
                # Получаем остановки
                route_stops = session.execute(
                    select(RouteStop).where(
                        RouteStop.route_id == route.id
                    ).order_by(RouteStop.stop_order)
                ).scalars().all()
                
                stops = []
                for rs in route_stops:
                    stop_obj = session.get(MapObject, rs.stop_id)
                    if stop_obj:
                        stops.append({
                            "stop_id": rs.stop_uuid,
                            "stop_order": rs.stop_order,
                            "name": stop_obj.name,
                            "latitude": stop_obj.latitude,
                            "longitude": stop_obj.longitude
                        })
                
                result = {
                    "route_id": route.uuid,
                    "name": route.name,
                    "description": route.description,
                    "direction": route.direction,
                    "stops": stops,
                    "created_at": route.created_at.isoformat() if route.created_at else None,
                    "updated_at": route.updated_at.isoformat() if route.updated_at else None
                }
                
                log.info("get_route: маршрут найден", extra={
                    "route_id": route_id,
                    "stops_count": len(stops)
                })
                return result
                
        except Exception as e:
            log.error("get_route: ошибка", extra={"error": str(e)})
            return None

    def update_route(self, route_id: str, name: str = None, description: str = None,
                     stops_list: List[Dict] = None, direction: str = None) -> bool:
        """
        Обновить маршрут
        
        Args:
            route_id: UUID маршрута
            name: Новое название
            description: Новое описание
            stops_list: Новый список остановок
            direction: Направление ('forward' | 'backward')
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                route = session.get(Route, uuid.UUID(route_id).bytes)
                if not route:
                    log.warning("update_route: маршрут не найден", extra={
                        "route_id": route_id
                    })
                    return False
                
                # Обновляем поля
                if name:
                    route.name = name
                if description is not None:
                    route.description = description
                if direction:
                    route.direction = direction
                
                route.updated_at = datetime.utcnow()
                
                # Обновляем остановки
                if stops_list is not None:
                    # Удаляем старые
                    old_stops = session.execute(
                        select(RouteStop).where(RouteStop.route_id == route.id)
                    ).scalars().all()
                    
                    for old_stop in old_stops:
                        session.delete(old_stop)
                    
                    session.flush()
                    
                    # Добавляем новые
                    for stop_data in stops_list:
                        stop = session.get(MapObject, uuid.UUID(stop_data["stop_id"]).bytes)
                        if stop:
                            route_stop = RouteStop(
                                route_id=route.id,
                                stop_id=stop.id,
                                stop_order=stop_data.get("order", 0)
                            )
                            session.add(route_stop)
                
                session.commit()
                
                log.info("update_route: маршрут обновлён", extra={
                    "route_id": route_id
                })
                return True
                
        except Exception as e:
            log.error("update_route: ошибка", extra={"error": str(e)})
            return False

    def delete_route(self, route_id: str) -> bool:
        """
        Удалить маршрут
        
        Args:
            route_id: UUID маршрута
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                route = session.get(Route, uuid.UUID(route_id).bytes)
                if not route:
                    log.warning("delete_route: маршрут не найден", extra={
                        "route_id": route_id
                    })
                    return False
                
                session.delete(route)
                session.commit()
                
                log.info("delete_route: маршрут удалён", extra={
                    "route_id": route_id
                })
                return True
                
        except Exception as e:
            log.error("delete_route: ошибка", extra={"error": str(e)})
            return False

    def get_all_routes(self) -> List[Dict]:
        """
        Получить все маршруты
        
        Returns:
            Список маршрутов
        """
        try:
            with self._get_session() as session:
                routes = session.execute(
                    select(Route).order_by(Route.name)
                ).scalars().all()
                
                result = []
                for route in routes:
                    # Считаем количество остановок
                    stops_count = session.execute(
                        select(func.count()).select_from(RouteStop).where(
                            RouteStop.route_id == route.id
                        )
                    ).scalar()
                    
                    result.append({
                        "route_id": route.uuid,
                        "name": route.name,
                        "description": route.description,
                        "direction": route.direction,
                        "stops_count": stops_count,
                        "created_at": route.created_at.isoformat() if route.created_at else None
                    })
                
                log.info("get_all_routes: найдено маршрутов", extra={
                    "count": len(result)
                })
                return result
                
        except Exception as e:
            log.error("get_all_routes: ошибка", extra={"error": str(e)})
            return []

    def reorder_stops(self, route_id: str, stop_id: str, new_order: int) -> bool:
        """
        Изменить порядок остановки в маршруте
        
        Args:
            route_id: UUID маршрута
            stop_id: UUID остановки
            new_order: Новый порядковый номер
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                route_stop = session.execute(
                    select(RouteStop).where(
                        RouteStop.route_id == uuid.UUID(route_id).bytes,
                        RouteStop.stop_id == uuid.UUID(stop_id).bytes
                    )
                ).scalar_one_or_none()
                
                if not route_stop:
                    log.warning("reorder_stops: остановка не найдена", extra={
                        "route_id": route_id,
                        "stop_id": stop_id
                    })
                    return False
                
                # Проверяем что новый порядок уникален
                existing = session.execute(
                    select(RouteStop).where(
                        RouteStop.route_id == route_stop.route_id,
                        RouteStop.stop_order == new_order,
                        RouteStop.stop_id != route_stop.stop_id
                    )
                ).scalar_one_or_none()
                
                if existing:
                    # Сдвигаем существующую
                    existing.stop_order = route_stop.stop_order
                
                route_stop.stop_order = new_order
                session.commit()
                
                log.info("reorder_stops: порядок изменён", extra={
                    "route_id": route_id,
                    "stop_id": stop_id,
                    "new_order": new_order
                })
                return True
                
        except Exception as e:
            log.error("reorder_stops: ошибка", extra={"error": str(e)})
            return False

    def toggle_direction(self, route_id: str) -> bool:
        """
        Переключить направление маршрута
        
        Args:
            route_id: UUID маршрута
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                route = session.get(Route, uuid.UUID(route_id).bytes)
                if not route:
                    return False
                
                route.direction = "backward" if route.direction == "forward" else "forward"
                route.updated_at = datetime.utcnow()
                session.commit()
                
                log.info("toggle_direction: направление изменено", extra={
                    "route_id": route_id,
                    "new_direction": route.direction
                })
                return True
                
        except Exception as e:
            log.error("toggle_direction: ошибка", extra={"error": str(e)})
            return False
