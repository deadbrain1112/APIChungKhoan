from fastapi import APIRouter
from typing import List, Dict
from app.models.models import  BienDongTaiKhoan
from app.crud.biendong import (
    get_transactions_by_type,
    compute_balance
)


router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/{maNDT}/{type}", response_model=List[BienDongTaiKhoan])
async def api_get_transactions(maNDT: str, type: str):
    return await get_transactions_by_type(maNDT, type)
