from fastapi import APIRouter

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("/ping")
def ping():
    return {"message": "building routes alive"}