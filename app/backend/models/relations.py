"""
Модели SQLAlchemy для связей объектов, пассажиропотока и маршрутов

Таблицы:
1. object_relations - связи между объектами (полигоны ↔ маркеры)
2. passenger_flow - пассажиропоток остановок
3. routes - маршруты
4. route_stops - остановки в маршрутах
"""
from typing import List, Optional
from sqlalchemy import Integer, String, Text, Boolean, Float, JSON, ForeignKey, Index, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from datetime import datetime
import uuid


def uuid_to_binary(uuid_str: str) -> bytes:
    """Конвертировать UUID строку в бинарный формат (16 байт)"""
    if isinstance(uuid_str, bytes):
        return uuid_str
    return uuid.UUID(uuid_str).bytes


def binary_to_uuid(binary: bytes) -> str:
    """Конвертировать бинарный UUID в строку"""
    if isinstance(binary, str):
        return binary
    return str(uuid.UUID(bytes=binary))


class ObjectRelation(Base):
    """Связь между объектами (родитель → потомок)"""

    __tablename__ = "object_relations"

    __table_args__ = (
        Index('ix_relations_parent', 'parent_id'),
        Index('ix_relations_child', 'child_id'),
        Index('ix_relations_type', 'relation_type'),
        UniqueConstraint('parent_id', 'child_id', name='uq_parent_child'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[bytes] = mapped_column("parent_id", String(16).with_variant(String(16), 'sqlite'), nullable=False, index=True)
    child_id: Mapped[bytes] = mapped_column("child_id", String(16).with_variant(String(16), 'sqlite'), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True, default='CONTAINS')
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow)

    # Связи с объектами
    parent: Mapped[Optional["MapObject"]] = relationship(
        "MapObject", foreign_keys=[parent_id], back_populates="child_relations", init=False
    )
    child: Mapped[Optional["MapObject"]] = relationship(
        "MapObject", foreign_keys=[child_id], back_populates="parent_relations", init=False
    )

    @property
    def parent_uuid(self) -> str:
        """Получить UUID родителя"""
        return binary_to_uuid(self.parent_id)

    @property
    def child_uuid(self) -> str:
        """Получить UUID потомка"""
        return binary_to_uuid(self.child_id)


class PassengerFlow(Base):
    """Пассажиропоток остановки"""

    __tablename__ = "passenger_flow"

    __table_args__ = (
        Index('ix_flow_stop', 'stop_id'),
        Index('ix_flow_date', 'date'),
        Index('ix_flow_stop_date', 'stop_id', 'date'),
        UniqueConstraint('stop_id', 'date', 'hour', name='uq_stop_date_hour'),
        CheckConstraint('hour >= 0 AND hour <= 23', name='ck_hour_range'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stop_id: Mapped[bytes] = mapped_column("stop_id", String(16).with_variant(String(16), 'sqlite'), nullable=False, index=True)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD
    hour: Mapped[int] = mapped_column(Integer, nullable=False)  # 0-23
    incoming: Mapped[int] = mapped_column(Integer, default=0)
    outgoing: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь с остановкой
    stop: Mapped[Optional["MapObject"]] = relationship(
        "MapObject", back_populates="passenger_flows", init=False
    )

    @property
    def stop_uuid(self) -> str:
        """Получить UUID остановки"""
        return binary_to_uuid(self.stop_id)


class Route(Base):
    """Маршрут транспорта"""

    __tablename__ = "routes"

    __table_args__ = (
        Index('ix_routes_name', 'name'),
    )

    id: Mapped[bytes] = mapped_column("id", String(16).with_variant(String(16), 'sqlite'), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direction: Mapped[str] = mapped_column(String(20), default='forward')  # forward | backward
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow, onupdate=datetime.utcnow)

    # Остановки в маршруте
    route_stops: Mapped[List["RouteStop"]] = relationship(
        "RouteStop", back_populates="route", cascade="all, delete-orphan", init=False
    )

    @property
    def uuid(self) -> str:
        """Получить UUID маршружа"""
        return binary_to_uuid(self.id)

    @uuid.setter
    def uuid(self, value: str):
        """Установить UUID"""
        self.id = uuid_to_binary(value)


class RouteStop(Base):
    """Остановка в маршруте"""

    __tablename__ = "route_stops"

    __table_args__ = (
        Index('ix_route_stops_route', 'route_id'),
        Index('ix_route_stops_stop', 'stop_id'),
        UniqueConstraint('route_id', 'stop_id', name='uq_route_stop'),
    )

    route_id: Mapped[bytes] = mapped_column("route_id", String(16).with_variant(String(16), 'sqlite'), primary_key=True)
    stop_id: Mapped[bytes] = mapped_column("stop_id", String(16).with_variant(String(16), 'sqlite'), primary_key=True)
    stop_order: Mapped[int] = mapped_column(Integer, primary_key=True)  # Порядковый номер
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow)

    # Связи
    route: Mapped["Route"] = relationship("Route", back_populates="route_stops", init=False)
    stop: Mapped[Optional["MapObject"]] = relationship("MapObject", back_populates="route_stops", init=False)

    @property
    def route_uuid(self) -> str:
        """Получить UUID маршрута"""
        return binary_to_uuid(self.route_id)

    @property
    def stop_uuid(self) -> str:
        """Получить UUID остановки"""
        return binary_to_uuid(self.stop_id)
