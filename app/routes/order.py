from fastapi import APIRouter, HTTPException
from bson import ObjectId
from datetime import datetime
from app.configs.database import db
from app.models.models import OrderModel, OrderResponse, co_phieu, LenhDat, so_huu

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
    await xu_ly_lenh_moi(saved_order)
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
    await xu_ly_lenh_moi(saved_order)
    return to_string_id(saved_order)

# ========== 3️⃣ Lấy danh sách lệnh của 1 nhà đầu tư ==========
@router.get("/all/{maNDT}", response_model=list[LenhDat])
async def get_all_orders(maNDT: str, loaiGD: str):
    cursor = db.lenh_dat.find(
        {
            "maNDT": maNDT,
            "loaiGD": loaiGD,
            "trangThai": {"$in": ["Chờ khớp", "Khớp một phần"]}
        }
    ).sort("ngayGD", -1)

    orders = []
    async for o in cursor:
        clean = {
            "_id": str(o["_id"]),
            "maNDT": o["maNDT"],
            "maCP": o["maCP"],
            "loaiGD": o["loaiGD"],
            "loaiLenh": o["loaiLenh"],
            "gia": o["gia"],
            "soLuong": o["soLuong"],
            "trangThai": o["trangThai"],
            "ngayGD": o["ngayGD"],
        }
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
    maCP = maCP.upper()

    # --- Lấy thông tin cổ phiếu ---
    cp = await db.co_phieu.find_one({"maCP": maCP})
    if not cp:
        raise HTTPException(status_code=404, detail="Không tìm thấy mã cổ phiếu")

    # --- Lấy lịch sử giá mới nhất ---
    latest = await db.lich_su_gia.find_one(
        {"maCP": maCP},
        sort=[("ngay", -1)]   # Sắp xếp giảm dần theo ngày
    )

    if not latest:
        raise HTTPException(status_code=404, detail="Không có lịch sử giá cho mã này")

    # --- Tính giá tham chiếu, trần, sàn ---
    gia_tham_chieu = float(latest.get("giaDongCua", 0))
    gia_tran = round(gia_tham_chieu * 1.1, 2)
    gia_san = round(gia_tham_chieu * 0.9, 2)

    # --- Thêm vào response ---
    cp["giaThamChieu"] = gia_tham_chieu
    cp["giaTran"] = gia_tran
    cp["giaSan"] = gia_san

    return to_string_id(cp)

# ========== 6️⃣ Danh sách cổ phiếu sở hữu ==========
@router.get("/owned/{maNDT}", response_model=list[dict])
async def get_owned_stocks(maNDT: str):
    cursor = db["so_huu"].find({"maNDT": maNDT})
    result = []

    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        result.append(doc)

    return result


async def khop_lenh(mua: dict, ban: dict):


    if mua["gia"] < ban["gia"]:
        return

    so_luong_khop = min(mua["soLuong"], ban["soLuong"])
    mua["soLuong"] -= so_luong_khop
    ban["soLuong"] -= so_luong_khop
    gia_khop = ban["gia"]  # hoặc giá của lệnh vào trước

    so_tien = so_luong_khop * gia_khop

    ndt_mua = await db.nha_dau_tu.find_one({"_id": ObjectId(mua["maNDT"])})
    ndt_ban = await db.nha_dau_tu.find_one({"_id": ObjectId(ban["maNDT"])})

    if ndt_mua["cash"] < so_tien:
        raise HTTPException(400, "NĐT mua không đủ tiền")

    await db.nha_dau_tu.update_one(
        {"_id": ndt_mua["_id"]},
        {"$inc": {"cash": -so_tien}}
    )

    await db.nha_dau_tu.update_one(
        {"_id": ndt_ban["_id"]},
        {"$inc": {"cash": so_tien}}
    )

    # ===== 3️⃣ TRỪ SỐ LƯỢNG + TRẠNG THÁI =====
    async def cap_nhat_lenh(lenh, so_khop):
        so_moi = lenh["soLuong"] - so_khop
        trang_thai = "Hoàn tất" if so_moi == 0 else "Khớp 1 phần"

        await db.lenh_dat.update_one(
            {"_id": lenh["_id"]},
            {
                "$inc": {"soLuong": -so_khop},
                "$set": {"trangThai": trang_thai}
            }
        )

    await cap_nhat_lenh(mua, so_luong_khop)
    await cap_nhat_lenh(ban, so_luong_khop)

    # ===== 4️⃣ CẬP NHẬT SỞ HỮU =====
    # người mua +
    await db.so_huu.update_one(
        {"maNDT": mua["maNDT"], "maCP": mua["maCP"]},
        {"$inc": {"soLuong": so_luong_khop}},
        upsert=True
    )

    await db.so_huu.update_one(
        {"maNDT": ban["maNDT"], "maCP": ban["maCP"]},
        {"$inc": {"soLuong": -so_luong_khop}}
    )

    async def ghi_giao_dich(lenh, loai):
        ndt = await db.nha_dau_tu.find_one({"_id": ObjectId(lenh["maNDT"])})
        so_tien_truoc = ndt["cash"] + (so_tien if loai == "M" else -so_tien)
        so_tien_sau = ndt["cash"]

        await db.giao_dich.insert_one({
            "maNDT": lenh["maNDT"],
            "kieu": "cp",
            "maCP": lenh["maCP"],
            "gia": gia_khop,
            "soLuong": so_luong_khop,
            "soTien": so_tien,
            "soTienTruoc": so_tien_truoc,
            "soTienSau": so_tien_sau,
            "trangThai": "Hoàn tất",
            "ngayGD": datetime.utcnow(),
            "moTa": f"Khớp {'mua' if loai=='M' else 'bán'} {lenh['maCP']} SL {so_luong_khop} @ {gia_khop}"
        })

    await ghi_giao_dich(mua, "M")
    await ghi_giao_dich(ban, "B")

async def xu_ly_lenh_moi(lenh_moi):
    if lenh_moi["loaiGD"] == "M":
        ds_ban = db.lenh_dat.find({
            "maCP": lenh_moi["maCP"],
            "loaiGD": "B",
            "trangThai": {"$in": ["Chờ khớp", "Khớp 1 phần"]},
            "gia": {"$lte": lenh_moi["gia"]}
        }).sort([("gia", 1), ("ngayGD", 1)])
    else:
        ds_ban = db.lenh_dat.find({
            "maCP": lenh_moi["maCP"],
            "loaiGD": "M",
            "trangThai": {"$in": ["Chờ khớp", "Khớp 1 phần"]},
            "gia": {"$gte": lenh_moi["gia"]}
        }).sort([("gia", -1), ("ngayGD", 1)])

    async for lenh_doi_ung in ds_ban:
        if lenh_doi_ung["trangThai"] == "Hoàn tất":
            continue
        await khop_lenh(
            lenh_moi if lenh_moi["loaiGD"] == "M" else lenh_doi_ung,
            lenh_doi_ung if lenh_moi["loaiGD"] == "M" else lenh_moi
        )
