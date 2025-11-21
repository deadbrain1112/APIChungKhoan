from fastapi import APIRouter
from typing import Dict
from app.crud.biendong import compute_balance

router = APIRouter(prefix="/balance", tags=["Balance"])

@router.get("/{maNDT}", response_model=Dict)
async def api_get_balance(maNDT: str):
    return await compute_balance(maNDT)
