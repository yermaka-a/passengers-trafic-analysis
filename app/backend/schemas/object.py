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
    radius: Optional[int] | None = Field(
        None,
        alias="radius",
        serialization_alias="radius",
    )
    osm_id: Optional[str] | None = Field(
        None,
        alias="osmId",
        serialization_alias="osmId",
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
        # Получаем связанные данные
        options_data = {
            "Id": obj.uuid,
            "name": obj.name,
            "objType": obj.obj_type,
        }
        
        # Добавляем данные из stop_metadata если есть
        if obj.stop_metadata:
            options_data.update({
                "markerType": obj.stop_metadata.marker_type,
                "radius": obj.stop_metadata.radius,
                "color": obj.stop_metadata.color,
                "osmId": obj.stop_metadata.osm_id,
            })
        
        # Добавляем данные из object_styles если есть
        if obj.object_styles:
            options_data.update({
                "color": obj.object_styles.color,
                "stroke": obj.object_styles.stroke,
                "weight": obj.object_styles.weight,
                "fill": obj.object_styles.fill,
                "fillOpacity": obj.object_styles.fill_opacity,
                "dashArray": obj.object_styles.dash_array,
            })
        
        return cls(
            latlng=[LatLng(**p) for p in obj.latlng],
            options=Options.model_validate(options_data),
        )


class Response(RootObjBaseModel):
    status: Literal["success", "failed"]


class ObjectResponse(Response):
    obj: ObjectCreate | None


class AllObjectsResponse(Response):
    objects: List[ObjectCreate]
