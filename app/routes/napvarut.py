from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from app.configs.database import db
from app.models.models import NapTienRequest, RutTienRequest

router = APIRouter()
@router.post("/nap-tien")
async def nap_tien(req: NapTienRequest):
    if req.soTien <= 0:
        raise HTTPException(400, "Số tiền không hợp lệ")

    ndt = await db.nha_dau_tu.find_one({"taikhoan": req.taikhoan})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy tài khoản")

    so_du_truoc = ndt.get("cash", 0)
    so_du_sau = so_du_truoc + req.soTien

    await db.nha_dau_tu.update_one(
        {"taikhoan": req.taikhoan},
        {"$set": {"cash": so_du_sau}}
    )

    await db.giao_dich.insert_one({
        "maNDT": req.taikhoan,
        "kieu": "NAP",
        "soTien": req.soTien,
        "soTienTruoc": so_du_truoc,
        "soTienSau": so_du_sau,
        "trangThai": "THANH_CONG",
        "ngayGD": datetime.now(),
        "moTa": "Nạp tiền vào tài khoản"
    })

    return {
        "message": "Nạp tiền thành công",
        "cash": so_du_sau
    }

@router.post("/rut-tien")
async def rut_tien(req: RutTienRequest):
    if req.soTien <= 0:
        raise HTTPException(400, "Số tiền không hợp lệ")

    ndt = await db.nha_dau_tu.find_one({"taikhoan": req.taikhoan})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy tài khoản")

    so_du_truoc = ndt.get("cash", 0)
    if so_du_truoc < req.soTien:
        raise HTTPException(400, "Số dư không đủ")

    so_du_sau = so_du_truoc - req.soTien

    await db.nha_dau_tu.update_one(
        {"taikhoan": req.taikhoan},
        {"$set": {"cash": so_du_sau}}
    )

    await db.giao_dich.insert_one({
        "maNDT": req.taikhoan,
        "kieu": "RUT",
        "soTien": req.soTien,
        "soTienTruoc": so_du_truoc,
        "soTienSau": so_du_sau,
        "trangThai": "THANH_CONG",
        "ngayGD": datetime.now(),
        "moTa": f"Rút tiền về {req.nganHang} - {req.stk}"
    })

    return {
        "message": "Rút tiền thành công",
        "cash": so_du_sau
    }


@router.get("/cash/{taikhoan}")
async def get_cash(taikhoan: str):
    ndt = await db.nha_dau_tu.find_one({"taikhoan": taikhoan})
    if not ndt:
        raise HTTPException(404, "Không tìm thấy tài khoản")

    return {
        "cash": ndt.get("cash", 0)
    }


@router.get("/lich-su/{taikhoan}")
async def lich_su_nap_rut(taikhoan: str):
    cursor = db.giao_dich.find(
        {"maNDT": taikhoan, "kieu": {"$in": ["NAP", "RUT"]}}
    ).sort("ngayGD", -1)

    return await cursor.to_list(100)


