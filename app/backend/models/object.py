from typing import List
from sqlalchemy import Integer, String, Text, Boolean, Float, JSON, Index
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
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
    __tablename__ = "map_objects"
    
    # Индексы для оптимизации производительности
    __table_args__ = (
        # Индексы для фильтрации
        Index('ix_obj_type', 'obj_type'),
        Index('ix_marker_type', 'marker_type'),
        Index('ix_obj_type_marker', 'obj_type', 'marker_type'),
        
        # Индексы для поиска
        Index('ix_custom_name', 'custom_name'),
        Index('ix_name', 'name'),
        
        # Индексы для координат
        Index('ix_latitude', 'latitude'),
        Index('ix_longitude', 'longitude'),
    )

    Id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default=None, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    custom_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None, index=True
    )
    color: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)
    stroke: Mapped[bool | None] = mapped_column(Boolean, default=True)
    weight: Mapped[int | None] = mapped_column(Integer, default=3)
    fill: Mapped[bool | None] = mapped_column(Boolean, default=None)
    fill_opacity: Mapped[float | None] = mapped_column(Float, default=None)
    
    # Координаты (извлечённые из JSON для производительности)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    
    latlng: Mapped[List[dict[str, float]]] = mapped_column(
        MutableList.as_mutable(JSON), nullable=False, default=list
    )
    obj_type: Mapped[str] = mapped_column(String(30), nullable=False, default=None, index=True)
    dash_array: Mapped[List[float] | None] = mapped_column(
        MutableList.as_mutable(JSON), nullable=False, default=None
    )
    marker_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, default=None, index=True
    )
    radius: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=30
    )
    
    # Методы для конвертации UUID
    @property
    def uuid(self) -> str:
        """Получить UUID как строку"""
        return binary_to_uuid(self.Id)
    
    @uuid.setter
    def uuid(self, value: str):
        """Установить UUID из строки"""
        self.Id = uuid_to_binary(value)
