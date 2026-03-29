from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..models.object import MapObject


class RootObjBaseModel(BaseModel):
    pass


class LatLng(RootObjBaseModel):
    lat: float
    lng: float


class Options(RootObjBaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
    Id: str = Field(max_length=36, min_length=36)
    name: str = Field(max_length=255)
    description: Optional[str] | None = Field(
        None,
        max_length=40000,
    )
    custom_name: Optional[str] = Field(
        None,
        alias="customName",
        serialization_alias="customName",
        max_length=255,
    )
    color: Optional[str] | None = Field(None, max_length=10)
    stroke: Optional[bool] | None = None
    dash_array: Optional[List[float]] | None = Field(
        None,
        alias="dashArray",
        serialization_alias="dashArray",
    )
    fill_opacity: Optional[float] = Field(
        None,
        alias="fillOpacity",
        serialization_alias="fillOpacity",
    )
    weight: Optional[int] | None = None
    fill: Optional[bool] | None = None
    obj_type: str = Field(
        max_length=30,
        alias="objType",
        serialization_alias="objType",
    )
    marker_type: Optional[str] | None = Field(
        None,
        alias="markerType",
        serialization_alias="markerType",
        max_length=50,
    )

    @field_validator("dash_array", mode="before")
    @classmethod
    def validate_dash_array(cls, value):
        """Валидация dash_array: принимаем None, пустой список, или [num, num]"""
        if value is None or value == []:
            return None
        if isinstance(value, list) and len(value) == 2:
            return [float(v) for v in value]
        return value


class ObjectCreate(RootObjBaseModel):
    latlng: List[LatLng]
    options: Options

    @classmethod
    def from_db(cls, obj: MapObject) -> "ObjectCreate":
        """Валидация и трансформация одного объекта из БД"""
        return cls(
            latlng=[LatLng(**p) for p in obj.latlng],
            options=Options.model_validate(obj),
        )


class Response(RootObjBaseModel):
    status: Literal["success", "failed"]


class ObjectResponse(Response):
    obj: ObjectCreate | None


class AllObjectsResponse(Response):
    objects: List[ObjectCreate]
