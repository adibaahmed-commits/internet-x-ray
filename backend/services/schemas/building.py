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