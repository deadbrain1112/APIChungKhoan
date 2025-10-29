from fastapi import APIRouter, HTTPException
from app.schemas.nhadautu_schema import NhaDauTuCreate
from app.services import nhadautu_service

router = APIRouter(prefix="/nhadautu", tags=["Nhà đầu tư"])

@router.get("/")
def get_all():
    return nhadautu_service.get_all()

@router.get("/{maNDT}")
def get_by_id(maNDT: str):
    ndt = nhadautu_service.get_by_id(maNDT)
    if not ndt:
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà đầu tư")
    return ndt

@router.post("/")
def create(item: NhaDauTuCreate):
    return nhadautu_service.create(item.dict())

@router.put("/{maNDT}")
def update(maNDT: str, update: dict):
    if not nhadautu_service.update(maNDT, update):
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà đầu tư")
    return {"message": "Cập nhật thành công"}

@router.delete("/{maNDT}")
def delete(maNDT: str):
    if not nhadautu_service.delete(maNDT):
        raise HTTPException(status_code=404, detail="Không tìm thấy nhà đầu tư")
    return {"message": "Đã xóa nhà đầu tư"}
