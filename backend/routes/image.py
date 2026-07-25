from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from db.database import get_db, Building
from services.storage_service import save_upload_file
from utils.validators import validate_image_file
from models.schemas import UploadResponse

router = APIRouter()


@router.post("/buildings/upload", response_model=UploadResponse)
async def upload_building_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    validate_image_file(file)
    filename = save_upload_file(file)

    building = Building(image_path=filename, status="pending")
    db.add(building)
    db.commit()
    db.refresh(building)

    return UploadResponse(
        building_id=building.id,
        status=building.status,
        image_url=f"/uploads/{filename}",
    )