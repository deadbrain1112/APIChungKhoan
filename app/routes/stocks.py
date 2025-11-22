from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import co_phieu, lich_su_gia
from fastapi import Query

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])

# ==========================
# 1. Lấy danh sách cổ phiếu
# ==========================
@router.get("/", response_model=list[co_phieu])
async def get_stock_list(page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    skip = (page - 1) * size
    cursor = db["co_phieu"].find().skip(skip).limit(size)
    result = []
    async for doc in cursor:
        result.append(co_phieu(**doc))
    return result

# ============================================
# 2. Lịch sử giá dạng candlestick cho 1 mã CP
# ============================================
@router.get("/{maCP}/candlestick", response_model=list[lich_su_gia])
async def get_candle_data(maCP: str, limit: int = 50):

    cursor = (
        db["lich_su_gia"]
        .find({"maCP": maCP})
        .sort("ngay", -1)
        .limit(limit)
    )

    result = []
    async for doc in cursor:
        doc.pop("_id", None)
        result.append(lich_su_gia(**doc))

    if not result:
        raise HTTPException(status_code=404, detail="Không có lịch sử giá")

    return result[::-1]   # đảo lại để chart đúng thứ tự thời gian


# ================================
# 3. Tìm kiếm cổ phiếu theo từ khóa
# ================================
@router.get("/search/{keyword}", response_model=list[co_phieu])
async def search_stock(keyword: str):
    cursor = db["co_phieu"].find({"maCP": {"$regex": keyword, "$options": "i"}})
    result = []
    async for doc in cursor:
        result.append(co_phieu(**doc))
    return result
