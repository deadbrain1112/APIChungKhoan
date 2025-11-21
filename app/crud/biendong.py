from typing import List, Optional
from bson import ObjectId
from app.configs.database import db
from app.models.models import BienDongTaiKhoan
from datetime import datetime

# -------------------------------
# Lấy toàn bộ biến động tài khoản theo NDT
# -------------------------------
async def get_all_transactions(maNDT: str) -> List[BienDongTaiKhoan]:
    ndt_id = ObjectId(maNDT)
    cursor = db.bien_dong_tai_khoan.find({"maNDT": ndt_id}).sort("ngay", -1)
    data = [BienDongTaiKhoan(**t) async for t in cursor]
    return data


# -------------------------------
# Lọc theo loại giao dịch
# type = ALL, DEPOSIT, WITHDRAW, TRADE
# -------------------------------
async def get_transactions_by_type(maNDT: str, type: str) -> List[BienDongTaiKhoan]:
    data = await get_all_transactions(maNDT)

    if type == "ALL":
        return data

    filtered = []

    for t in data:
        loai = t.loaiGiaoDich

        if type == "DEPOSIT" and loai in ["NAP_TIEN", "CO_TUC", "LAI_SUAT"]:
            filtered.append(t)

        if type == "WITHDRAW" and loai in ["RUT_TIEN", "PHI_GIAO_DICH"]:
            filtered.append(t)

        if type == "TRADE" and loai in ["MUA_CP", "BAN_CP"]:
            filtered.append(t)

    return filtered


# -------------------------------
# Tính Balance + Thu/Chi tháng
# -------------------------------
async def compute_balance(maNDT: str):
    data = await get_all_transactions(maNDT)

    if not data:
        return {
            "balance": 0,
            "monthIncome": 0,
            "monthExpense": 0
        }

    balance = data[0].soTienSau

    now = datetime.now()
    month = now.month
    year = now.year

    income = 0
    expense = 0

    for t in data:
        if t.ngay.month == month and t.ngay.year == year:
            if t.soTienPhatSinh >= 0:
                income += t.soTienPhatSinh
            else:
                expense += t.soTienPhatSinh

    return {
        "balance": balance,
        "monthIncome": income,
        "monthExpense": expense
    }
