from datetime import datetime

from bson import ObjectId
from typing import List
from app.configs.database import db
from app.models.models import so_huu, co_phieu, WatchlistItem, lich_su_gia

async def get_so_huu(maNDT: str):
    cursor = db.so_huu.find({"maNDT": maNDT})
    return [so_huu(**doc) async for doc in cursor]
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
async def get_watchlist(maNDT: str):
    data = []
    so_huu_list = await get_so_huu(maNDT)

    for so_huu in so_huu_list:
        maCP = so_huu.maCP

        # --- Lấy lịch sử giá gần nhất ---
        lich_su = await db.lich_su_gia.find_one(
            {"maCP": maCP},
            sort=[("ngay", -1)]   # sắp xếp giảm dần -> lấy bản mới nhất
        )

        if lich_su:
            # ---- Có lịch sử giá: dùng giá đóng cửa gần nhất ----
            item = WatchlistItem(
                soHuu=so_huu,
                lichSuGia=lich_su_gia(**lich_su)
            )
        else:
            # ---- Không có lịch sử giá: fallback sang giá tham chiếu ----
            cp = await db.co_phieu.find_one({"maCP": maCP})
            if cp:
                fake_lich_su = lich_su_gia(
                    maCP=maCP,
                    ngay=datetime.now(),
                    giaMoCua=cp["giaThamChieu"],
                    giaDongCua=cp["giaThamChieu"],
                    giaCaoNhat=cp["giaThamChieu"],
                    giaThapNhat=cp["giaThamChieu"],
                    khoiLuong=0
                )
            else:
                fake_lich_su = None  # phòng trường hợp cổ phiếu cũng không có

            item = WatchlistItem(
                soHuu=so_huu,
                lichSuGia=fake_lich_su
            )

        data.append(item)

    return data



# Lấy top movers
async def get_top_movers(mode: str) -> List[lich_su_gia]:
    data = []

    if mode == "volume":
        # Thêm changePct vào luôn
        pipeline = [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "changePct": {
                        "$cond": [
                            {"$eq": ["$giaMoCua", 0]},
                            0,
                            {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            {"$subtract": ["$giaDongCua", "$giaMoCua"]},
                                            "$giaMoCua"
                                        ]
                                    },
                                    100
                                ]
                            }
                        ]
                    }
                }
            },
            {"$sort": {"khoiLuong": -1}},
            {"$limit": 5}
        ]
        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]

    elif mode == "value":
        # Thêm changePct + tránh chia 0
        pipeline = [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "value": {"$multiply": ["$giaDongCua", "$khoiLuong"]},
                    "changePct": {
                        "$cond": [
                            {"$eq": ["$giaMoCua", 0]},
                            0,
                            {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            {"$subtract": ["$giaDongCua", "$giaMoCua"]},
                                            "$giaMoCua"
                                        ]
                                    },
                                    100
                                ]
                            }
                        ]
                    }
                }
            },
            {"$sort": {"value": -1}},
            {"$limit": 5}
        ]
        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]

    elif mode in ["gainers", "losers"]:
        pipeline = [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "changePct": {
                        "$cond": [
                            {"$eq": ["$giaMoCua", 0]},
                            0,
                            {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            {"$subtract": ["$giaDongCua", "$giaMoCua"]},
                                            "$giaMoCua"
                                        ]
                                    },
                                    100
                                ]
                            }
                        ]
                    }
                }
            }
        ]

        if mode == "gainers":
            pipeline.append({"$sort": {"changePct": -1}})
        else:
            pipeline.append({"$sort": {"changePct": 1}})

        pipeline.append({"$limit": 5})
        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]

    return [lich_su_gia(**d) for d in data]

