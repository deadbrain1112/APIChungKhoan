from fastapi import APIRouter
from app.services import lenh_service

router = APIRouter(prefix="/lenh", tags=["Lệnh giao dịch"])

@router.get("/dat")
def get_all_lenhdat():
    return lenh_service.get_all_lenhdat()

@router.post("/dat")
def create_lenhdat(item: dict):
    return lenh_service.create_lenhdat(item)

@router.get("/khop")
def get_all_lenhkhop():
    return lenh_service.get_all_lenhkhop()

@router.post("/khop")
def create_lenhkhop(item: dict):
    return lenh_service.create_lenhkhop(item)
