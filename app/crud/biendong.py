from datetime import datetime
from typing import List
from bson import ObjectId
from app.configs.database import db
from app.models.models import GiaoDich

async def get_transactions(maNDT: str, kieu: str) -> List[GiaoDich]:
    query = {"maNDT": maNDT}

    if kieu != "all":
        query["kieu"] = kieu

    cursor = db.giao_dich.find(query).sort("ngayGD", -1)
    return [GiaoDich(**t) async for t in cursor]


async def create_transaction(data: GiaoDich):

    # 1. Lấy số dư hiện tại
    last_tx = await db.giao_dich.find_one(
        {"maNDT": data.maNDT},
        sort=[("ngayGD", -1)]
    )

    so_du_truoc = last_tx["soTienSau"] if last_tx else 0
    so_du_sau = so_du_truoc + data.soTien

    # 2. Cập nhật vào object
    data.soTienTruoc = so_du_truoc
    data.soTienSau = so_du_sau

    # 3. Insert Mongo
    doc = data.dict(by_alias=True)

    result = await db.giao_dich.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    return doc


async def compute_balance(maNDT: str):
    cursor = db.giao_dich.find({"maNDT": maNDT})
    data = [GiaoDich(**t) async for t in cursor]

    balance = 0
    month_income = 0
    month_expense = 0

    now = datetime.now()

    for t in data:
        balance = t.soTienSau

        # Tính trong tháng
        if t.ngayGD.month == now.month and t.ngayGD.year == now.year:
            if t.soTien > 0:
                month_income += t.soTien
            else:
                month_expense += abs(t.soTien)

    return {
        "balance": balance,
        "monthIncome": month_income,
        "monthExpense": month_expense
    }
