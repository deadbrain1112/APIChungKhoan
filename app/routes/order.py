from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.configs.database import db
from app.models.models import OrderModel, OrderResponse, co_phieu

router = APIRouter(prefix="/api/orders", tags=["Orders"])


# ==========  Đặt lệnh MUA ==========
@router.post("/buy", response_model=OrderResponse)
async def place_buy_order(order: OrderModel):
    order.loaiGD = "M"  # Mua
    order.trangThai = "Chờ khớp"
    order.ngayGD = datetime.now()

    result = await db.lenh_dat.insert_one(order.dict())
    saved_order = await db.LenhDat.find_one({"_id": result.inserted_id})
    saved_order["_id"] = str(saved_order["_id"])
    return saved_order


# ========== 2Đặt lệnh BÁN ==========
@router.post("/sell", response_model=OrderResponse)
async def place_sell_order(order: OrderModel):
    order.loaiGD = "B"  # Bán
    order.trangThai = "Chờ khớp"
    order.ngayGD = datetime.now()

    # Kiểm tra sở hữu cổ phiếu đủ không
    so_huu = await db.so_huu.find_one({"maNDT": order.maNDT, "maCP": order.maCP})
    if not so_huu or so_huu["soLuong"] < order.soLuong:
        raise HTTPException(status_code=400, detail="Không đủ cổ phiếu để bán")

    result = await db.LenhDat.insert_one(order.dict())
    saved_order = await db.LenhDat.find_one({"_id": result.inserted_id})
    saved_order["_id"] = str(saved_order["_id"])
    return saved_order


# ==========  Lấy danh sách lệnh của 1 nhà đầu tư ==========
@router.get("/all/{maNDT}", response_model=list[OrderResponse])
async def get_all_orders(maNDT: str):
    cursor = db.lenh_dat.find({"maNDT": maNDT})
    orders = []
    async for o in cursor:
        o["_id"] = str(o["_id"])
        orders.append(o)
    return orders


# ========== 4️⃣ Hủy lệnh ==========
@router.delete("/{order_id}")
async def cancel_order(order_id: str):
    result = await db.LenhDat.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Không tìm thấy lệnh để hủy")
    return {"message": "Đã hủy lệnh thành công"}


# ========== 5️⃣ Lấy thông tin cổ phiếu theo mã ==========
@router.get("/stock/{maCP}", response_model=co_phieu)
async def get_stock_info(maCP: str):
    cp = await db.co_phieu.find_one({"maCP": maCP.upper()})
    if not cp:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã cổ phiếu")
    cp["_id"] = str(cp["_id"])
    return cp


# ========== 6️⃣ Danh sách cổ phiếu sở hữu ==========
@router.get("/owned/{maNDT}")
async def get_owned_stocks(maNDT: str):
    cursor = db.so_huu.find({"maNDT": maNDT})
    result = []
    async for item in cursor:
        item["_id"] = str(item["_id"])
        result.append(item)
    return result
