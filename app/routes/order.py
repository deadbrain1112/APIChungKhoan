from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.configs.database import db
from app.models.models import OrderModel, OrderResponse, co_phieu, LenhDat

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# ---------- Utility chuyển ObjectId sang str ----------
def to_string_id(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# ========== 1️⃣ Đặt lệnh MUA ==========
@router.post("/buy", response_model=OrderResponse)
async def place_buy_order(order: OrderModel):
    order.loaiGD = "M"  # Mua
    order.trangThai = "Chờ khớp"
    order.ngayGD = datetime.now()

    result = await db.lenh_dat.insert_one(order.dict())
    saved_order = await db.lenh_dat.find_one({"_id": result.inserted_id})
    return to_string_id(saved_order)

# ========== 2️⃣ Đặt lệnh BÁN ==========
@router.post("/sell", response_model=OrderResponse)
async def place_sell_order(order: OrderModel):
    order.loaiGD = "B"
    order.trangThai = "Chờ khớp"
    order.ngayGD = datetime.now()

    # Kiểm tra sở hữu cổ phiếu
    so_huu = await db.so_huu.find_one({"maNDT": order.maNDT, "maCP": order.maCP})
    if not so_huu or so_huu["soLuong"] < order.soLuong:
        raise HTTPException(status_code=400, detail="Không đủ cổ phiếu để bán")

    result = await db.lenh_dat.insert_one(order.dict())
    saved_order = await db.lenh_dat.find_one({"_id": result.inserted_id})
    return to_string_id(saved_order)

# ========== 3️⃣ Lấy danh sách lệnh của 1 nhà đầu tư ==========
@router.get("/all/{maNDT}", response_model=list[LenhDat])
async def get_all_orders(maNDT: str):
    cursor = db.lenh_dat.find(
        {
            "maNDT": maNDT,
            "trangThai": {"$in": ["Chờ khớp", "Khớp một phần"]}
        }
    ).sort("ngayGD", -1)

    orders = []
    async for o in cursor:
        clean = to_string_id(o)
        orders.append(LenhDat(**clean))
    return orders

# ========== 4️⃣ Hủy lệnh ==========
@router.delete("/{order_id}")
async def cancel_order(order_id: str):
    result = await db.lenh_dat.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy lệnh để hủy")
    return {"message": "Đã hủy lệnh thành công"}

# ========== 5️⃣ Lấy thông tin cổ phiếu theo mã ==========
@router.get("/stock/{maCP}", response_model=co_phieu)
async def get_stock_info(maCP: str):
    cp = await db.co_phieu.find_one({"maCP": maCP.upper()})
    if not cp:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã cổ phiếu")
    return to_string_id(cp)

# ========== 6️⃣ Danh sách cổ phiếu sở hữu ==========
@router.get("/owned/{maNDT}")
async def get_owned_stocks(maNDT: str):
    cursor = db.so_huu.find({"maNDT": maNDT})
    result = []
    async for item in cursor:
        result.append(to_string_id(item))
    return result
