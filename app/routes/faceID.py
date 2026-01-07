from fastapi import APIRouter, HTTPException
from bson import ObjectId
from app.configs.database import db

router = APIRouter(prefix="/api/face", tags=["Face"])

@router.get("/{maNDT}")
async def get_face_embedding(maNDT: str):
    if not ObjectId.is_valid(maNDT):
        raise HTTPException(status_code=400, detail="ID không hợp lệ")

    ndt = await db.nha_dau_tu.find_one(
        {"_id": ObjectId(maNDT)},
        {"faceEmbeddings": 1}   # chỉ lấy field này
    )

    if not ndt or "faceEmbeddings" not in ndt:
        raise HTTPException(status_code=404, detail="Không có dữ liệu face")

    return {
        "maNDT": maNDT,
        "faceEmbeddings": ndt["faceEmbeddings"]
    }
