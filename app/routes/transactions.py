from fastapi import APIRouter
from typing import List
from app.models.models import GiaoDich
from app.crud.biendong import  get_transactions, create_transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/{maNDT}/{kieu}", response_model=List[GiaoDich])
async def api_get_transactions(maNDT: str, kieu: str):
    return await get_transactions(maNDT, kieu)

@router.post("", response_model=GiaoDich)
async def api_create_transaction(data: GiaoDich):
    return await create_transaction(data)
