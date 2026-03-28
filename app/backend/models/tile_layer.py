from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TileLayerSetting(Base):
    __tablename__ = "tile_layer_settings"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    value: Mapped[str] = mapped_column(String(50), nullable=False)
