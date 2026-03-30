"""
CRUD операции для пассажиропотока

PassengerFlowController:
- create_or_update(stop_id, date, hour, incoming, outgoing)
- get_by_stop(stop_id, date_from, date_to)
- get_by_route(route_id, date)
- aggregate_by_polygon(polygon_id, date)
"""
from typing import List, Optional, Dict
from sqlalchemy import select, func
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, date
import uuid

from ..models import PassengerFlow, MapObject, ObjectRelation
from ..logger import log


class PassengerFlowController:
    def __init__(self, sessionmaker: sessionmaker):
        self.sessionmaker = sessionmaker

    def _get_session(self) -> Session:
        return self.sessionmaker()

    def create_or_update(self, stop_id: str, date_str: str, hour: int, 
                         incoming: int = 0, outgoing: int = 0) -> bool:
        """
        Создать или обновить запись о пассажиропотоке
        
        Args:
            stop_id: UUID остановки
            date_str: дата в формате YYYY-MM-DD
            hour: час (0-23)
            incoming: входящие пассажиры
            outgoing: исходящие пассажиры
            
        Returns:
            True если успешно
        """
        try:
            with self._get_session() as session:
                # Проверяем существование остановки
                stop = session.get(MapObject, uuid.UUID(stop_id).bytes)
                if not stop:
                    log.warning("create_or_update: остановка не найдена", extra={
                        "stop_id": stop_id
                    })
                    return False
                
                # Ищем существующую запись
                flow = session.execute(
                    select(PassengerFlow).where(
                        PassengerFlow.stop_id == stop.id,
                        PassengerFlow.date == date_str,
                        PassengerFlow.hour == hour
                    )
                ).scalar_one_or_none()
                
                if flow:
                    # Обновляем
                    flow.incoming = incoming
                    flow.outgoing = outgoing
                    flow.updated_at = datetime.utcnow()
                    log.info("create_or_update: обновлено", extra={
                        "stop_id": stop_id,
                        "date": date_str,
                        "hour": hour
                    })
                else:
                    # Создаём
                    flow = PassengerFlow(
                        stop_id=stop.id,
                        date=date_str,
                        hour=hour,
                        incoming=incoming,
                        outgoing=outgoing
                    )
                    session.add(flow)
                    log.info("create_or_update: создано", extra={
                        "stop_id": stop_id,
                        "date": date_str,
                        "hour": hour
                    })
                
                session.commit()
                return True
                
        except Exception as e:
            log.error("create_or_update: ошибка", extra={"error": str(e)})
            return False

    def get_by_stop(self, stop_id: str, date_from: str, date_to: str) -> List[PassengerFlow]:
        """
        Получить пассажиропоток остановки за период
        
        Args:
            stop_id: UUID остановки
            date_from: дата от (YYYY-MM-DD)
            date_to: дата до (YYYY-MM-DD)
            
        Returns:
            Список записей PassengerFlow
        """
        try:
            with self._get_session() as session:
                flows = session.execute(
                    select(PassengerFlow).where(
                        PassengerFlow.stop_id == uuid.UUID(stop_id).bytes,
                        PassengerFlow.date >= date_from,
                        PassengerFlow.date <= date_to
                    ).order_by(PassengerFlow.date, PassengerFlow.hour)
                ).scalars().all()
                
                log.info("get_by_stop: найдено записей", extra={
                    "stop_id": stop_id,
                    "count": len(flows)
                })
                return list(flows)
                
        except Exception as e:
            log.error("get_by_stop: ошибка", extra={"error": str(e)})
            return []

    def get_by_route(self, route_id: str, date_str: str) -> Dict:
        """
        Получить пассажиропоток маршрута за дату
        
        Args:
            route_id: UUID маршрута
            date_str: дата (YYYY-MM-DD)
            
        Returns:
            Dict с данными по остановкам
        """
        try:
            with self._get_session() as session:
                # Получаем все остановки маршрута
                from ..models import RouteStop
                route_stops = session.execute(
                    select(RouteStop).where(
                        RouteStop.route_id == uuid.UUID(route_id).bytes
                    ).order_by(RouteStop.stop_order)
                ).scalars().all()
                
                result = {
                    "route_id": route_id,
                    "date": date_str,
                    "stops": []
                }
                
                for rs in route_stops:
                    flows = session.execute(
                        select(PassengerFlow).where(
                            PassengerFlow.stop_id == rs.stop_id,
                            PassengerFlow.date == date_str
                        )
                    ).scalars().all()
                    
                    # Агрегируем по часам
                    hourly_data = {}
                    for flow in flows:
                        hourly_data[flow.hour] = {
                            "incoming": flow.incoming,
                            "outgoing": flow.outgoing
                        }
                    
                    result["stops"].append({
                        "stop_id": rs.stop_uuid,
                        "stop_order": rs.stop_order,
                        "hourly_data": hourly_data
                    })
                
                log.info("get_by_route: найдено остановок", extra={
                    "route_id": route_id,
                    "count": len(result["stops"])
                })
                return result
                
        except Exception as e:
            log.error("get_by_route: ошибка", extra={"error": str(e)})
            return {}

    def aggregate_by_polygon(self, polygon_id: str, date_str: str) -> Dict:
        """
        Агрегировать пассажиропоток всех маркеров в полигоне
        
        Args:
            polygon_id: UUID полигона
            date_str: дата (YYYY-MM-DD)
            
        Returns:
            Dict с агрегированными данными
        """
        try:
            with self._get_session() as session:
                # Получаем все остановки в полигоне
                relations = session.execute(
                    select(ObjectRelation).where(
                        ObjectRelation.parent_id == uuid.UUID(polygon_id).bytes,
                        ObjectRelation.relation_type == 'CONTAINS'
                    )
                ).scalars().all()
                
                total_incoming = 0
                total_outgoing = 0
                hourly_totals = {}
                stops_count = 0
                
                for relation in relations:
                    flows = session.execute(
                        select(PassengerFlow).where(
                            PassengerFlow.stop_id == relation.child_id,
                            PassengerFlow.date == date_str
                        )
                    ).scalars().all()
                    
                    if flows:
                        stops_count += 1
                        for flow in flows:
                            total_incoming += flow.incoming
                            total_outgoing += flow.outgoing
                            
                            if flow.hour not in hourly_totals:
                                hourly_totals[flow.hour] = {"incoming": 0, "outgoing": 0}
                            hourly_totals[flow.hour]["incoming"] += flow.incoming
                            hourly_totals[flow.hour]["outgoing"] += flow.outgoing
                
                result = {
                    "polygon_id": polygon_id,
                    "date": date_str,
                    "total_incoming": total_incoming,
                    "total_outgoing": total_outgoing,
                    "hourly_totals": hourly_totals,
                    "stops_count": stops_count
                }
                
                log.info("aggregate_by_polygon: агрегировано", extra={
                    "polygon_id": polygon_id,
                    "total_incoming": total_incoming,
                    "total_outgoing": total_outgoing
                })
                return result
                
        except Exception as e:
            log.error("aggregate_by_polygon: ошибка", extra={"error": str(e)})
            return {
                "polygon_id": polygon_id,
                "date": date_str,
                "total_incoming": 0,
                "total_outgoing": 0,
                "hourly_totals": {},
                "stops_count": 0
            }

    def get_daily_summary(self, stop_id: str, date_str: str) -> Dict:
        """
        Получить сводку за день
        
        Args:
            stop_id: UUID остановки
            date_str: дата (YYYY-MM-DD)
            
        Returns:
            Dict с суммарными данными
        """
        try:
            with self._get_session() as session:
                flows = session.execute(
                    select(PassengerFlow).where(
                        PassengerFlow.stop_id == uuid.UUID(stop_id).bytes,
                        PassengerFlow.date == date_str
                    )
                ).scalars().all()
                
                total_incoming = sum(f.incoming for f in flows)
                total_outgoing = sum(f.outgoing for f in flows)
                
                # Пиковый час
                peak_hour = None
                peak_total = 0
                for flow in flows:
                    total = flow.incoming + flow.outgoing
                    if total > peak_total:
                        peak_total = total
                        peak_hour = flow.hour
                
                result = {
                    "stop_id": stop_id,
                    "date": date_str,
                    "total_incoming": total_incoming,
                    "total_outgoing": total_outgoing,
                    "peak_hour": peak_hour,
                    "peak_total": peak_total
                }
                
                log.info("get_daily_summary", extra={
                    "stop_id": stop_id,
                    "total_incoming": total_incoming,
                    "total_outgoing": total_outgoing
                })
                return result
                
        except Exception as e:
            log.error("get_daily_summary: ошибка", extra={"error": str(e)})
            return {}
