from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session
from typing import Optional
import io
from PIL import Image
from PIL.ExifTags import TAGS

from db.database import get_db, Building
from services.storage_service import save_upload_file
from utils.validators import validate_image_file
from models.schemas import UploadResponse

router = APIRouter()


def _extract_gps_from_bytes(image_bytes: bytes):
    """Extracts (latitude, longitude) from image EXIF data. Returns (None, None) if unavailable."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()
        if not exif_data:
            return None, None

        gps_info = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                gps_info = value
                break

        if not gps_info:
            return None, None

        def convert_to_degrees(value):
            d, m, s = value
            return d + (m / 60.0) + (s / 3600.0)

        lat = lon = None
        if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
            lat = convert_to_degrees(gps_info['GPSLatitude'])
            if gps_info['GPSLatitudeRef'] != 'N':
                lat = -lat
        if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
            lon = convert_to_degrees(gps_info['GPSLongitude'])
            if gps_info['GPSLongitudeRef'] != 'E':
                lon = -lon

        return lat, lon
    except Exception:
        return None, None


@router.post("/buildings/upload", response_model=UploadResponse)
async def upload_building_image(
    file: UploadFile = File(...),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    db: Session = Depends(get_db),
):
    validate_image_file(file)

    # If the caller didn't explicitly send GPS coordinates, try to pull them
    # from the image's own EXIF data before falling back to None.
    if latitude is None or longitude is None:
        contents = await file.read()
        exif_lat, exif_lon = _extract_gps_from_bytes(contents)
        if latitude is None:
            latitude = exif_lat
        if longitude is None:
            longitude = exif_lon
        # Reset the stream so save_upload_file can read it again from the start.
        await file.seek(0)

    filename = save_upload_file(file)

    building = Building(
        image_path=filename,
        latitude=latitude,
        longitude=longitude,
        status="pending",
    )
    db.add(building)
    db.commit()
    db.refresh(building)

    return UploadResponse(
        building_id=building.id,
        status=building.status,
        image_url=f"/uploads/{filename}",
    )