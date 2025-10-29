from fastapi import APIRouter
from app.services import cophieu_service

router = APIRouter(prefix="/cophieu", tags=["Cổ phiếu"])

@router.get("/")
def get_all():
    return cophieu_service.get_all()

@router.post("/")
def create(item: dict):
    return cophieu_service.create(item)
