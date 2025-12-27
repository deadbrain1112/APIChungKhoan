from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from app.configs.database import db
from app.models.models import NapTienRequest, RutTienRequest

router = APIRouter()
def oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except:
        raise HTTPException(400, "maNDT không hợp lệ")


@router.post("/nap-tien")
async def nap_tien(req: NapTienRequest):
    if req.soTien <= 0:
        raise HTTPException(400, "Số tiền không hợp lệ")

    ndt = await db.nha_dau_tu.find_one({"_id": oid(req.maNDT)})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy NĐT")

    so_du_truoc = ndt.get("cash", 0)
    so_du_sau = so_du_truoc + req.soTien

    await db.nha_dau_tu.update_one(
        {"_id": oid(req.maNDT)},
        {"$set": {"cash": so_du_sau}}
    )

    await db.giao_dich.insert_one({
        "maNDT": req.maNDT,          # lưu ObjectId dạng string
        "kieu": "nap",
        "soTien": req.soTien,
        "soTienTruoc": so_du_truoc,
        "soTienSau": so_du_sau,
        "trangThai": "Hoàn tất",
        "ngayGD": datetime.utcnow(),
        "moTa": f"Nạp {req.soTien}"
    })

    return {
        "message": "Nạp tiền thành công",
        "cash": so_du_sau
    }


@router.post("/rut-tien")
async def rut_tien(req: RutTienRequest):
    if req.soTien <= 0:
        raise HTTPException(400, "Số tiền không hợp lệ")

    ndt = await db.nha_dau_tu.find_one({"_id": oid(req.maNDT)})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy NĐT")

    so_du_truoc = ndt.get("cash", 0)
    if so_du_truoc < req.soTien:
        raise HTTPException(400, "Số dư không đủ")

    so_du_sau = so_du_truoc - req.soTien

    await db.nha_dau_tu.update_one(
        {"_id": oid(req.maNDT)},
        {"$set": {"cash": so_du_sau}}
    )

    await db.giao_dich.insert_one({
        "maNDT": req.maNDT,
        "kieu": "rut",
        "soTien": -req.soTien,
        "soTienTruoc": so_du_truoc,
        "soTienSau": so_du_sau,
        "trangThai": "Hoàn tất",
        "ngayGD": datetime.utcnow(),
        "moTa": f"Rút {req.soTien} về {req.nganHang} - {req.stk}"
    })

    return {
        "message": "Rút tiền thành công",
        "cash": so_du_sau
    }


@router.get("/cash/{maNDT}")
async def get_cash(maNDT: str):
    ndt = await db.nha_dau_tu.find_one({"_id": oid(maNDT)})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy NĐT")

    return {
        "cash": ndt.get("cash", 0)
    }


@router.get("/lich-su/{maNDT}")
async def lich_su(maNDT: str):
    cursor = db.giao_dich.find(
        {"maNDT": maNDT, "kieu": {"$in": ["nap", "rut"]}}
    ).sort("ngayGD", -1)

    return await cursor.to_list(100)


