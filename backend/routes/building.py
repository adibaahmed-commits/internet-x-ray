from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
import os

from db.database import Building, get_db
from schemas.building import BuildingDetail
from services.places_service import get_nearby_places
from services.gemini_service import analyze_building_image, BuildingAnalysisError
from services.storage_service import UPLOAD_DIR
from schemas.building import BuildingChatRequest, BuildingChatResponse
from services.chat_service import answer_building_question

router = APIRouter()

@router.get("/buildings/{building_id}", response_model=BuildingDetail)
def get_building_details(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()

    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    analysis = json.loads(building.analysis_json) if building.analysis_json else None

    hospitals = schools = shopping_centers = None
    if building.latitude is not None and building.longitude is not None:
        nearby_data = get_nearby_places(lat=building.latitude, lon=building.longitude)
        hospitals = nearby_data["hospitals"]
        schools = nearby_data["schools"]
        shopping_centers = nearby_data["shopping_centers"]

    return BuildingDetail(
        id=building.id,
        name=building.name,
        image_url=building.image_path,
        status=building.status,
        analysis_json=analysis,
        created_at=building.created_at,
        hospitals=hospitals,
        schools=schools,
        shopping_centers=shopping_centers,
    )

@router.post("/buildings/{building_id}/analyze", response_model=BuildingDetail)
def analyze_building(building_id: int, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()

    if not building:
        raise HTTPException(status_code=404, detail="Building not found")

    full_image_path = os.path.join(UPLOAD_DIR, building.image_path)

    if not os.path.exists(full_image_path):
        raise HTTPException(
            status_code=410,
            detail="Original image is no longer available. Please re-upload."
        )

    try:
        analysis_result = analyze_building_image(full_image_path)
    except BuildingAnalysisError as e:
        raise HTTPException(status_code=503, detail=str(e))

    building.analysis_json = json.dumps(analysis_result)
    building.status = "complete"
    db.commit()
    db.refresh(building)

    hospitals = schools = shopping_centers = None
    if building.latitude is not None and building.longitude is not None:
        nearby_data = get_nearby_places(lat=building.latitude, lon=building.longitude)
        hospitals = nearby_data["hospitals"]
        schools = nearby_data["schools"]
        shopping_centers = nearby_data["shopping_centers"]

    return BuildingDetail(
        id=building.id,
        name=building.name,
        image_url=building.image_path,
        status=building.status,
        analysis_json=analysis_result,
        created_at=building.created_at,
        hospitals=hospitals,
        schools=schools,
        shopping_centers=shopping_centers,
    )

@router.post("/buildings/{building_id}/chat", response_model=BuildingChatResponse)
def chat_about_building(building_id: int, req: BuildingChatRequest, db: Session = Depends(get_db)):
    building = db.query(Building).filter(Building.id == building_id).first()

    if not building or not building.analysis_json:
        raise HTTPException(status_code=404, detail="No analysis available for this building")

    analysis = json.loads(building.analysis_json)
    answer = answer_building_question(analysis, req.question)
    return BuildingChatResponse(answer=answer)