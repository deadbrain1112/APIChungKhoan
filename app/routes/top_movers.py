from fastapi import APIRouter, Query
from app.crud.home import get_top_movers
from app.models.models import lich_su_gia
from typing import List

router = APIRouter()

@router.get("/top-movers", response_model=List[lich_su_gia])
async def top_movers(mode: str = Query(..., enum=["volume", "value", "gainers", "losers"])):
    return await get_top_movers(mode)
