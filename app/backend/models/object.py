from typing import List
from sqlalchemy import Integer, String, Text, Boolean, Float, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MapObject(Base):
    __tablename__ = "map_objects"

    Id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, default=None)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    custom_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    color: Mapped[str | None] = mapped_column(String(10), nullable=True, default=None)
    stroke: Mapped[bool | None] = mapped_column(Boolean, default=True)
    weight: Mapped[int | None] = mapped_column(Integer, default=3)
    fill: Mapped[bool | None] = mapped_column(Boolean, default=None)
    fill_opacity: Mapped[float | None] = mapped_column(Float, default=None)
    latlng: Mapped[List[dict[str, float]]] = mapped_column(
        MutableList.as_mutable(JSON), nullable=False, default=list
    )
    obj_type: Mapped[str] = mapped_column(String(30), nullable=False, default=None)
    dash_array: Mapped[List[float] | None] = mapped_column(
        MutableList.as_mutable(JSON), nullable=False, default=None
    )
