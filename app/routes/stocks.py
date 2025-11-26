from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import co_phieu, lich_su_gia
from fastapi import Query

router = APIRouter(prefix="/api/stocks", tags=["Stocks"])

# ==========================
# 1. Lấy danh sách cổ phiếu
# ==========================
from bson import ObjectId

def to_string_id(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


@router.get("/", response_model=list[dict])
async def get_stock_list(page: int = Query(1, ge=1), size: int = Query(10, ge=1)):
    skip = (page - 1) * size

    cursor = db["co_phieu"].find().skip(skip).limit(size)
    result = []

    async for cp in cursor:
        cp = to_string_id(cp)   # convert ObjectId của cp

        # Lấy lịch sử giá gần nhất
        latest_price = await db["lich_su_gia"].find_one(
            {"maCP": cp["maCP"]},
            sort=[("ngay", -1)]
        )

        if latest_price:
            latest_price = to_string_id(latest_price)

            gia_dong_cua_hom_truoc = latest_price.get("giaDongCua", 0)
            gia_mo_cua = latest_price.get("giaMoCua", 0)

            change = gia_dong_cua_hom_truoc - gia_mo_cua

            changePct = 0
            if gia_mo_cua != 0:
                changePct = (change / gia_mo_cua) * 100
        else:
            gia_dong_cua_hom_truoc = None
            change = None
            changePct = None

        result.append({
            **cp,
            "giaDongCuaHomTruoc": gia_dong_cua_hom_truoc,
            "chenhLechGia": change,
            "changePct": changePct
        })

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

    return result[::-1]


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
