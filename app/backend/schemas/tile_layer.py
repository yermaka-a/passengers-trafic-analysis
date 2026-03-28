from pydantic import BaseModel


class TileLayerSettingCreate(BaseModel):
    key: str
    value: str


class TileLayerSettingResponse(BaseModel):
    key: str
    value: str
