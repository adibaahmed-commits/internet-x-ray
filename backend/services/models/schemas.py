from pydantic import BaseModel

class UploadResponse(BaseModel):
    building_id: int
    status: str
    image_url: str