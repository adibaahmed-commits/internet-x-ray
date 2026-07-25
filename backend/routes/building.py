# routes/building.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db, Building
from services.gemini_service import analyze_building_image, BuildingAnalysisError
from services.storage_service import UPLOAD_DIR

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/ping")
def ping():
    return {"message": "building routes alive"}


@router.post("/{building_id}/analyze")
def analyze_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    if not building.image_path:
        raise HTTPException(status_code=400, detail="Building has no uploaded image")

    building.status = "analyzing"
    db.commit()

    try:
        analysis = analyze_building_image(building.image_path)
    except BuildingAnalysisError as e:
        building.status = "failed"
        db.commit()
        raise HTTPException(status_code=502, detail=f"Analysis failed: {str(e)}")

    building.analysis_json = json.dumps(analysis)
    building.status = "complete"
    db.commit()
    db.refresh(building)

    return {
        "id": building.id,
        "status": building.status,
        "analysis": analysis,
    }