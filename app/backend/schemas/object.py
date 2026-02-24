from typing import List, Optional
from pydantic import BaseModel, Field


class LatLng(BaseModel):
    lat: float
    lng: float


class Options(BaseModel):
    Id: str = Field(max_length=36, min_length=36)
    order: int
    name: str = Field(max_length=255)
    description: Optional[str] | None = Field(
        None,
        max_length=40000,
    )
    customName: Optional[str] | None = Field(None, max_length=255)
    color: Optional[str] | None = Field(None, max_length=10)
    stroke: Optional[bool] | None = None
    dashArray: Optional[str] | None = Field(None, max_length=255)
    fillOpacity: Optional[float] | None = None
    weight: Optional[int] | None = None
    fill: Optional[bool] | None = None


class ObjectCreate(BaseModel):
    latlng: List[LatLng]
    options: Options
