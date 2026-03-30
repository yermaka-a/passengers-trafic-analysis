"""
Оптимизированные модели SQLAlchemy

Разделение на 3 таблицы:
1. map_objects - базовая информация для всех объектов
2. stop_metadata - специфичные данные для StopMarker
3. object_styles - стили для Polygon/Polyline/CircleMarker

Все ID в binary(16) для экономии места
"""
from typing import List, Optional
from sqlalchemy import Integer, String, Text, Boolean, Float, JSON, ForeignKey, Index, DateTime, ForeignKeyConstraint
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign
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


class MapObject(Base):
    """Базовая таблица для всех гео-объектов"""

    __tablename__ = "map_objects"

    # Индексы для оптимизации
    __table_args__ = (
        Index('ix_obj_type', 'obj_type'),
        Index('ix_latitude', 'latitude'),
        Index('ix_longitude', 'longitude'),
        Index('ix_name', 'name'),
    )

    # Поля БЕЗ default (обязательные) - должны идти первыми для dataclasses
    id: Mapped[bytes] = mapped_column("id", String(16).with_variant(String(16), 'sqlite'), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    obj_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    latlng: Mapped[List[dict]] = mapped_column(MutableList.as_mutable(JSON), nullable=False)

    # Поля С default (необязательные) - должны идти после
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default=None)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True, default=None)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True, index=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default_factory=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship должны идти последними с init=False (не участвуют в dataclass __init__)
    stop_metadata: Mapped[Optional["StopMetadata"]] = relationship(
        "StopMetadata", back_populates="object", uselist=False, cascade="all, delete-orphan", init=False
    )
    object_styles: Mapped[Optional["ObjectStyles"]] = relationship(
        "ObjectStyles", back_populates="object", uselist=False, cascade="all, delete-orphan", init=False
    )
    
    # Связи для object_relations (полигоны ↔ маркеры)
    child_relations: Mapped[List["ObjectRelation"]] = relationship(
        "ObjectRelation", 
        foreign_keys="ObjectRelation.parent_id", 
        back_populates="parent", 
        init=False,
        primaryjoin="foreign(ObjectRelation.parent_id) == MapObject.id"
    )
    parent_relations: Mapped[List["ObjectRelation"]] = relationship(
        "ObjectRelation", 
        foreign_keys="ObjectRelation.child_id", 
        back_populates="child", 
        init=False,
        primaryjoin="foreign(ObjectRelation.child_id) == MapObject.id"
    )
    
    # Связи для passenger_flow_stops
    passenger_flow_stops: Mapped[List["PassengerFlowStop"]] = relationship(
        "PassengerFlowStop", 
        back_populates="stop", 
        cascade="all, delete-orphan", 
        init=False,
        primaryjoin="foreign(PassengerFlowStop.stop_id) == MapObject.id"
    )
    
    # Связи для routes
    route_stops: Mapped[List["RouteStop"]] = relationship(
        "RouteStop", 
        back_populates="stop", 
        cascade="all, delete-orphan", 
        init=False,
        primaryjoin="foreign(RouteStop.stop_id) == MapObject.id"
    )

    # Методы для конвертации UUID
    @property
    def uuid(self) -> str:
        """Получить UUID как строку"""
        return binary_to_uuid(self.id)

    @uuid.setter
    def uuid(self, value: str):
        """Установить UUID из строки"""
        self.id = uuid_to_binary(value)


class StopMetadata(Base):
    """Метаданные для StopMarker (основанные на OSM)"""
    
    __tablename__ = "stop_metadata"
    
    __table_args__ = (
        Index('ix_stop_osm_id', 'osm_id'),
        Index('ix_stop_marker_type', 'marker_type'),
    )

    object_id: Mapped[bytes] = mapped_column(
        ForeignKey("map_objects.id", ondelete="CASCADE"),
        primary_key=True
    )
    osm_id: Mapped[Optional[str]] = mapped_column(String(50), unique=True, nullable=True, index=True)
    marker_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    radius: Mapped[Optional[int]] = mapped_column(Integer, default=30)
    color: Mapped[Optional[str]] = mapped_column(String(10), default='#FF0000')
    
    # Связь с родительским объектом (init=False чтобы не ломать dataclass порядок)
    object: Mapped[MapObject] = relationship("MapObject", back_populates="stop_metadata", init=False)


class ObjectStyles(Base):
    """Стили для Polygon/Polyline/CircleMarker"""

    __tablename__ = "object_styles"

    __table_args__ = (
        Index('ix_object_styles_object_id', 'object_id'),
    )

    # Поля БЕЗ default (обязательные)
    object_id: Mapped[bytes] = mapped_column(
        ForeignKey("map_objects.id", ondelete="CASCADE"),
        primary_key=True
    )

    # Поля С default (необязательные)
    stroke: Mapped[Optional[bool]] = mapped_column(Boolean, default=True)
    weight: Mapped[Optional[int]] = mapped_column(Integer, default=3)
    fill: Mapped[Optional[bool]] = mapped_column(Boolean, default=None)
    fill_opacity: Mapped[Optional[float]] = mapped_column(Float, default=None)
    dash_array: Mapped[Optional[List[float]]] = mapped_column(MutableList.as_mutable(JSON), nullable=True, default=None)
    color: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, default=None)

    # Связь с родительским объектом (init=False)
    object: Mapped[MapObject] = relationship("MapObject", back_populates="object_styles", init=False)
