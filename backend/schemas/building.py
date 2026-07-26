from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class BuildingListItem(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: str
    status: str


class BuildingDetail(BaseModel):
    id: int
    name: Optional[str] = None
    image_url: str
    status: str
    analysis_json: Optional[Any] = None
    created_at: Optional[datetime] = None