# schemas/building.py
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class BuildingListItem(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: str = Field(validation_alias="image_path")
    status: str

    class Config:
        from_attributes = True
        populate_by_name = True


class BuildingDetail(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: str
    status: str
    analysis_json: Optional[Any] = None
    created_at: Optional[datetime] = None
    hospitals: Optional[Any] = None
    schools: Optional[Any] = None
    shopping_centers: Optional[Any] = None

    class Config:
        from_attributes = True