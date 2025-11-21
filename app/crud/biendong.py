from datetime import datetime
from typing import List
from bson import ObjectId
from app.configs.database import db
from app.models.models import GiaoDich

async def get_transactions(maNDT: str, kieu: str) -> List[GiaoDich]:
    query = {"maNDT": maNDT}

    if kieu != "all":
        query["kieu"] = kieu  # cp | nap | rut

    cursor = db.giao_dich.find(query).sort("ngayGD", -1)
    return [GiaoDich(**t) async for t in cursor]


async def create_transaction(data: GiaoDich):
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
        # --- Tính balance chung ---
        if t.kieu == "nap":
            balance += t.soTien or 0
        elif t.kieu == "rut":
            balance -= t.soTien or 0

        # --- Tính theo tháng ---
        if t.ngayGD.month == now.month and t.ngayGD.year == now.year:
            if t.kieu == "nap":
                month_income += t.soTien or 0
            elif t.kieu == "rut":
                month_expense += t.soTien or 0

    return {
        "balance": balance,
        "monthIncome": month_income,
        "monthExpense": month_expense
    }
