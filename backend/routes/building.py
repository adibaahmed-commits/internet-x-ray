# routes/building.py
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc

from db.database import get_db, Building
from services.gemini_service import analyze_building_image, BuildingAnalysisError
from services.storage_service import UPLOAD_DIR
from schemas.building import BuildingListItem, BuildingDetail   # <-- new import

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


# ---- new endpoints below ----

@router.get("", response_model=list[BuildingListItem])
def list_buildings(db: Session = Depends(get_db)):
    buildings = db.query(Building).order_by(desc(Building.id)).all()
    return [
        {
            "id": b.id,
            "name": b.name,
            "image_url": f"/uploads/{b.image_path}",
            "status": b.status,
        }
        for b in buildings
    ]


@router.get("/{building_id}", response_model=BuildingDetail)
def get_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    parsed_analysis = json.loads(building.analysis_json) if building.analysis_json else None

    return {
        "id": building.id,
        "name": building.name,
        "image_url": f"/uploads/{building.image_path}",
        "status": building.status,
        "analysis_json": parsed_analysis,
        "created_at": building.created_at,
    }