from fastapi import APIRouter, HTTPException
from app.models.models import PortfolioSummary
from app.configs.database import db
from app.crud.home import compute_nav
from bson import ObjectId

router = APIRouter()

@router.get("/portfolio/{taikhoan}", response_model=PortfolioSummary)
async def get_portfolio(taikhoan: str):
    ndt = await db.NhaDauTu.find_one({"taikhoan": taikhoan})
    if not ndt:
        raise HTTPException(status_code=404, detail="Nha dau tu khong ton tai")

    nav = await compute_nav(ndt["taikhoan"])  # hoặc dùng ndt["_id"] nếu muốn
    pnlToday = int(nav * 0.01)
    pnlPct = pnlToday / nav * 100 if nav else 0
    return PortfolioSummary(
        nav=nav,
        pnlToday=pnlToday,
        pnlPct=pnlPct,
        cash=ndt.get("tien_kha_dung", 0)
    )

