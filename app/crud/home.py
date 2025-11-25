from bson import ObjectId
from typing import List
from app.configs.database import db
from app.models.models import so_huu, co_phieu, WatchlistItem, lich_su_gia

# Tính NAV
async def compute_nav(maNDT: str) -> float:
    ndt_id = ObjectId(maNDT)
    # Lấy tất cả cổ phiếu sở hữu
    holdings = db.so_huu.find({"maNDT": ndt_id})
    total_value = 0
    async for h in holdings:
        maCP = h["maCP"]
        qty = h["soLuong"]
        lich_su = await db.lich_su_gia.find_one({"maCP": maCP}, sort=[("ngay", -1)])
        gia_dong_cua = lich_su["giaDongCua"] if lich_su else 0
        total_value += qty * gia_dong_cua

    ndt = await db.nha_dau_tu.find_one({"_id": ndt_id})
    cash = ndt.get("cash", 0)
    debt = ndt.get("debt", 0)

    nav = total_value + cash - debt
    return nav


# Lấy watchlist
async def get_watchlist(maNDT: str) -> List[WatchlistItem]:
    result = []

    # Lưu ý: so_huu.maNDT là string trong DB, không convert sang ObjectId
    async for s in db.so_huu.find({"maNDT": maNDT}):
        maCP = s["maCP"]

        # Lấy thông tin cổ phiếu
        cp = await db.co_phieu.find_one({"maCP": maCP})
        if not cp:
            continue  # Bỏ qua nếu cổ phiếu không tồn tại

        # Lấy nến mới nhất
        lich_su = await db.lich_su_gia.find_one({"maCP": maCP}, sort=[("ngay", -1)])

        item = WatchlistItem(
            soHuu=so_huu(
                maCP=maCP,
                soLuong=s.get("soLuong", 0),
                coPhieu=co_phieu(
                    maCP=cp["maCP"],
                    tenCongTy=cp.get("tenCongTy", "N/A"),
                    giaDongCua=lich_su["giaDongCua"] if lich_su else cp.get("giaDongCua", 0)
                )
            ),
            lichSuGia=lich_su_gia(**lich_su) if lich_su else None
        )
        result.append(item)

    return result

# Lấy top movers
from datetime import datetime
from app.configs.database import db
from app.models.models import lich_su_gia
from typing import List


async def get_top_movers(mode: str) -> List[lich_su_gia]:
    # --- 1. Lấy ngày mới nhất ---
    newest_doc = await db.lich_su_gia.find_one(sort=[("ngay", -1)])
    if not newest_doc:
        return []

    newest_date = newest_doc["ngay"]

    # --- 2. Lấy ngày liền trước ---
    prev_doc = await db.lich_su_gia.find_one(
        {"ngay": {"$lt": newest_date}},
        sort=[("ngay", -1)]
    )
    if not prev_doc:
        return []

    previous_date = prev_doc["ngay"]

    # --- 3. Join today's & yesterday's ---
    pipeline = [
        {"$match": {"ngay": {"$in": [newest_date, previous_date]}}},
        {"$sort": {"maCP": 1, "ngay": 1}},

        {"$group": {
            "_id": "$maCP",
            "records": {"$push": {
                "ngay": "$ngay",
                "giaDongCua": "$giaDongCua",
                "giaMoCua": "$giaMoCua",
                "giaCaoNhat": "$giaCaoNhat",
                "giaThapNhat": "$giaThapNhat",
                "khoiLuong": "$khoiLuong"
            }}
        }},

        # Lọc những mã có đúng 2 phiên
        {"$match": {"records.1": {"$exists": True}}},

        # Tính % thay đổi
        {"$project": {
            "maCP": "$_id",
            "today": {"$arrayElemAt": ["$records", 1]},
            "yesterday": {"$arrayElemAt": ["$records", 0]},
            "changePct": {
                "$multiply": [
                    {"$divide": [
                        {"$subtract": [
                            {"$arrayElemAt": ["$records.giaDongCua", 1]},
                            {"$arrayElemAt": ["$records.giaDongCua", 0]}
                        ]},
                        {"$arrayElemAt": ["$records.giaDongCua", 0]}
                    ]},
                    100
                ]
            }
        }}
    ]

    # --- Sort theo mode ---
    if mode == "gainers":
        pipeline.append({"$sort": {"changePct": -1}})
    elif mode == "losers":
        pipeline.append({"$sort": {"changePct": 1}})
    elif mode == "volume":
        pipeline.append({"$sort": {"today.khoiLuong": -1}})
    elif mode == "value":
        pipeline.append({"$sort": {
            "value": -1
        }})
        pipeline.insert(-1, {
            "$addFields": {
                "value": {"$multiply": ["$today.giaDongCua", "$today.khoiLuong"]}
            }
        })

    pipeline.append({"$limit": 5})

    cursor = db.lich_su_gia.aggregate(pipeline)
    data = [d async for d in cursor]

    # Convert output về mô hình lich_su_gia (trả về today)
    result = []
    for d in data:
        today = d["today"]
        today["maCP"] = d["maCP"]
        today["changePct"] = d["changePct"]
        result.append(lich_su_gia(**today))

    return result


