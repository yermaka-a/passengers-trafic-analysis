"""
CRUD операции для пассажиропотоков

PassengerFlowController:
- create_flow(name, date, time_period, direction, stops_list)
- get_flow(flow_id)
- update_flow(flow_id, stops_list)
- delete_flow(flow_id)
- get_all_flows(date_from, date_to)
- get_flows_by_route(route_id, date)
"""
from typing import List, Optional, Dict
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime
import uuid

from ..models import PassengerFlow, PassengerFlowStop, MapObject
from ..logger import log


class PassengerFlowController:
    def __init__(self, sessionmaker: sessionmaker):
        self.sessionmaker = sessionmaker

    def _get_session(self) -> Session:
        return self.sessionmaker()

    def create_flow(self, name: str, date: str, time_period: str = 'off_peak',
                    direction: str = 'forward', description: str = None,
                    route_id: str = None, stops_list: List[Dict] = None) -> Optional[str]:
        """
        Создать пассажиропоток
        
        Args:
            name: Название потока
            date: Дата (YYYY-MM-DD)
            time_period: Период (morning_peak, evening_peak, off_peak, night)
            direction: Направление
            description: Описание
            route_id: UUID связанного маршрута (опционально)
            stops_list: Список остановок [
                {"stop_id": "...", "order": 1, "passengers_on_board": 10, "passengers_off_board": 5},
                ...
            ]
            
        Returns:
            UUID потока или None
        """
        try:
            with self._get_session() as session:
                flow_id = uuid.uuid4()
                
                # Создаём поток
                flow = PassengerFlow(
                    id=flow_id.bytes,
                    name=name,
                    date=date,
                    time_period=time_period,
                    direction=direction,
                    description=description or "",
                    route_id=uuid.UUID(route_id).bytes if route_id else None
                )
                session.add(flow)
                session.flush()
                
                # Добавляем остановки
                if stops_list:
                    passengers_remaining = 0
                    
                    for stop_data in stops_list:
                        stop = session.get(MapObject, uuid.UUID(stop_data["stop_id"]).bytes)
                        if stop:
                            # Считаем остаток пассажиров
                            on_board = stop_data.get("passengers_on_board", 0)
                            off_board = stop_data.get("passengers_off_board", 0)
                            passengers_remaining = passengers_remaining + on_board - off_board
                            
                            flow_stop = PassengerFlowStop(
                                flow_id=flow.id,
                                stop_id=stop.id,
                                stop_order=stop_data.get("order", 0),
                                passengers_on_board=on_board,
                                passengers_off_board=off_board,
                                passengers_remaining=max(0, passengers_remaining)
                            )
                            session.add(flow_stop)
                
                session.commit()
                
                log.info("create_flow: поток создан", extra={
                    "flow_id": str(flow_id),
                    "name": name,
                    "stops_count": len(stops_list) if stops_list else 0
                })
                return str(flow_id)
                
        except Exception as e:
            log.error("create_flow: ошибка", extra={"error": str(e)})
            return None

    def get_flow(self, flow_id: str) -> Optional[Dict]:
        """
        Получить пассажиропоток с остановками
        
        Args:
            flow_id: UUID потока
            
        Returns:
            Dict с данными потока
        """
        try:
            with self._get_session() as session:
                flow = session.get(PassengerFlow, uuid.UUID(flow_id).bytes)
                if not flow:
                    log.warning("get_flow: поток не найден", extra={"flow_id": flow_id})
                    return None
                
                # Получаем остановки
                flow_stops = session.execute(
                    select(PassengerFlowStop).where(
                        PassengerFlowStop.flow_id == flow.id
                    ).order_by(PassengerFlowStop.stop_order)
                ).scalars().all()
                
                stops = []
                for fs in flow_stops:
                    stop_obj = session.get(MapObject, fs.stop_id)
                    stops.append({
                        "stop_id": fs.stop_uuid,
                        "stop_order": fs.stop_order,
                        "stop_name": stop_obj.name if stop_obj else "Unknown",
                        "passengers_on_board": fs.passengers_on_board,
                        "passengers_off_board": fs.passengers_off_board,
                        "passengers_remaining": fs.passengers_remaining
                    })
                
                result = {
                    "flow_id": flow.uuid,
                    "name": flow.name,
                    "date": flow.date,
                    "time_period": flow.time_period,
                    "direction": flow.direction,
                    "description": flow.description,
                    "route_id": binary_to_uuid(flow.route_id) if flow.route_id else None,
                    "stops": stops,
                    "created_at": flow.created_at.isoformat() if flow.created_at else None,
                    "updated_at": flow.updated_at.isoformat() if flow.updated_at else None
                }
                
                log.info("get_flow: поток найден", extra={
                    "flow_id": flow_id,
                    "stops_count": len(stops)
                })
                return result
                
        except Exception as e:
            log.error("get_flow: ошибка", extra={"error": str(e)})
            return None

    def update_flow(self, flow_id: str, name: str = None, date: str = None,
                    time_period: str = None, direction: str = None,
                    description: str = None, stops_list: List[Dict] = None) -> bool:
        """
        Обновить пассажиропоток
        
        Args:
            flow_id: UUID потока
            name: Новое название
            date: Новая дата
            time_period: Новый период
            direction: Новое направление
            description: Новое описание
            stops_list: Новый список остановок
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                flow = session.get(PassengerFlow, uuid.UUID(flow_id).bytes)
                if not flow:
                    log.warning("update_flow: поток не найден", extra={"flow_id": flow_id})
                    return False
                
                # Обновляем поля
                if name:
                    flow.name = name
                if date:
                    flow.date = date
                if time_period:
                    flow.time_period = time_period
                if direction:
                    flow.direction = direction
                if description is not None:
                    flow.description = description
                
                flow.updated_at = datetime.utcnow()
                
                # Обновляем остановки
                if stops_list is not None:
                    # Удаляем старые
                    old_stops = session.execute(
                        select(PassengerFlowStop).where(
                            PassengerFlowStop.flow_id == flow.id
                        )
                    ).scalars().all()
                    
                    for old_stop in old_stops:
                        session.delete(old_stop)
                    
                    session.flush()
                    
                    # Добавляем новые
                    passengers_remaining = 0
                    for stop_data in stops_list:
                        stop = session.get(MapObject, uuid.UUID(stop_data["stop_id"]).bytes)
                        if stop:
                            on_board = stop_data.get("passengers_on_board", 0)
                            off_board = stop_data.get("passengers_off_board", 0)
                            passengers_remaining = passengers_remaining + on_board - off_board
                            
                            flow_stop = PassengerFlowStop(
                                flow_id=flow.id,
                                stop_id=stop.id,
                                stop_order=stop_data.get("order", 0),
                                passengers_on_board=on_board,
                                passengers_off_board=off_board,
                                passengers_remaining=max(0, passengers_remaining)
                            )
                            session.add(flow_stop)
                
                session.commit()
                
                log.info("update_flow: поток обновлён", extra={"flow_id": flow_id})
                return True
                
        except Exception as e:
            log.error("update_flow: ошибка", extra={"error": str(e)})
            return False

    def delete_flow(self, flow_id: str) -> bool:
        """
        Удалить пассажиропоток
        
        Args:
            flow_id: UUID потока
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                flow = session.get(PassengerFlow, uuid.UUID(flow_id).bytes)
                if not flow:
                    log.warning("delete_flow: поток не найден", extra={"flow_id": flow_id})
                    return False
                
                session.delete(flow)
                session.commit()
                
                log.info("delete_flow: поток удалён", extra={"flow_id": flow_id})
                return True
                
        except Exception as e:
            log.error("delete_flow: ошибка", extra={"error": str(e)})
            return False

    def get_all_flows(self, date_from: str = None, date_to: str = None) -> List[Dict]:
        """
        Получить все пассажиропотоки
        
        Args:
            date_from: Дата от (YYYY-MM-DD)
            date_to: Дата до (YYYY-MM-DD)
            
        Returns:
            Список потоков
        """
        try:
            with self._get_session() as session:
                query = select(PassengerFlow)
                
                if date_from:
                    query = query.where(PassengerFlow.date >= date_from)
                if date_to:
                    query = query.where(PassengerFlow.date <= date_to)
                
                query = query.order_by(PassengerFlow.date, PassengerFlow.name)
                flows = session.execute(query).scalars().all()
                
                result = []
                for flow in flows:
                    # Считаем количество остановок
                    stops_count = session.execute(
                        select(func.count()).select_from(PassengerFlowStop).where(
                            PassengerFlowStop.flow_id == flow.id
                        )
                    ).scalar()
                    
                    result.append({
                        "flow_id": flow.uuid,
                        "name": flow.name,
                        "date": flow.date,
                        "time_period": flow.time_period,
                        "direction": flow.direction,
                        "stops_count": stops_count,
                        "route_id": binary_to_uuid(flow.route_id) if flow.route_id else None
                    })
                
                log.info("get_all_flows: найдено потоков", extra={"count": len(result)})
                return result
                
        except Exception as e:
            log.error("get_all_flows: ошибка", extra={"error": str(e)})
            return []

    def get_flows_by_route(self, route_id: str, date: str = None) -> List[Dict]:
        """
        Получить все потоки для маршрута
        
        Args:
            route_id: UUID маршрута
            date: Дата (опционально)
            
        Returns:
            Список потоков
        """
        try:
            with self._get_session() as session:
                query = select(PassengerFlow).where(
                    PassengerFlow.route_id == uuid.UUID(route_id).bytes
                )
                
                if date:
                    query = query.where(PassengerFlow.date == date)
                
                flows = session.execute(query).scalars().all()
                
                result = []
                for flow in flows:
                    result.append({
                        "flow_id": flow.uuid,
                        "name": flow.name,
                        "date": flow.date,
                        "time_period": flow.time_period,
                        "direction": flow.direction
                    })
                
                log.info("get_flows_by_route: найдено потоков", extra={
                    "route_id": route_id,
                    "count": len(result)
                })
                return result
                
        except Exception as e:
            log.error("get_flows_by_route: ошибка", extra={"error": str(e)})
            return []


# Helper для конвертации
def binary_to_uuid(binary: bytes) -> str:
    """Конвертировать бинарный UUID в строку"""
    if isinstance(binary, str):
        return binary
    import uuid
    return str(uuid.UUID(bytes=binary))
