from fastapi import APIRouter
from app.crud.home import get_watchlist
from app.models.models import WatchlistItem
from typing import List

router = APIRouter()

@router.get("/watchlist/{taikhoan}", response_model=List[WatchlistItem])
async def watchlist(maNDT: str):
    return await get_watchlist(maNDT)
