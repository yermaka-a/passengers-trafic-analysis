"""
Схемы для импорта остановок из Overpass API
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class OverpassStop(BaseModel):
    """Остановка из Overpass API"""
    
    osm_id: str = Field(..., description="Уникальный ID остановки (node_123 или way_123)")
    name: str = Field(..., description="Название остановки")
    lat: float = Field(..., description="Широта")
    lon: float = Field(..., description="Долгота")
    type: str = Field(..., description="Тип остановки (bus_stop, platform, etc.)")
    tags: Dict[str, str] = Field(default_factory=dict, description="Дополнительные теги OSM")
    
    class Config:
        from_attributes = True


class StopImportRequest(BaseModel):
    """Запрос на импорт остановок"""
    
    cities: str = Field(..., description="Список городов через запятую (например: 'Ангарск,Москва')")
    stop_types: List[str] = Field(
        default=["bus_stop", "platform"],
        description="Типы остановок для импорта"
    )
    
    class Config:
        from_attributes = True


class StopImportResponse(BaseModel):
    """Ответ на импорт остановок"""
    
    status: Literal["success", "failed"] = Field(..., description="Статус операции")
    imported_count: int = Field(..., description="Количество импортированных остановок")
    duplicate_count: int = Field(default=0, description="Количество дубликатов (не импортировано)")
    cities: List[str] = Field(..., description="Список городов")
    message: Optional[str] = Field(None, description="Сообщение об ошибке (если failed)")
    
    class Config:
        from_attributes = True
