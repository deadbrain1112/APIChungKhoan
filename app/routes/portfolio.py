from fastapi import APIRouter, HTTPException
from app.models.models import PortfolioSummary
from app.configs.database import db
from app.crud.home import compute_nav
from bson import ObjectId

router = APIRouter()

@router.get("/portfolio/{maNDT}", response_model=PortfolioSummary)
async def get_portfolio(maNDT: str):
    ndt_id = ObjectId(maNDT)
    ndt = await db.NhaDauTu.find_one({"_id": ndt_id})
    if not ndt:
        raise HTTPException(status_code=404, detail="Nha dau tu khong ton tai")

    nav = await compute_nav(maNDT)
    pnlToday = int(nav * 0.01)
    pnlPct = pnlToday / nav * 100 if nav else 0
    return PortfolioSummary(
        nav=nav,
        pnlToday=pnlToday,
        pnlPct=pnlPct,
        cash=ndt.get("tien_kha_dung", 0)
    )
