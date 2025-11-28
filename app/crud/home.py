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

    nav = total_value + cash
    return nav


# Lấy watchlist
async def get_watchlist(maNDT: str) -> List[WatchlistItem]:
    result = []

    async for s in db.so_huu.find({"maNDT": maNDT}):
        maCP = s["maCP"]

        cp = await db.co_phieu.find_one({"maCP": maCP})
        if not cp:
            continue

        lich_su = await db.lich_su_gia.find_one(
            {"maCP": maCP},
            sort=[("ngay", -1)]
        )

        # ========================
        # TẠO MODEL LỊCH SỬ GIÁ
        # ========================
        if lich_su:
            # Có lịch sử
            giaMo = lich_su.get("giaMoCua", 0)
            giaDong = lich_su.get("giaDongCua", 0)
            giaTC = cp.get("giaThamChieu", 0)

            # Nếu giaDongCua = 0 → dùng giá tham chiếu
            if giaDong == 0:
                giaDong = giaTC
                lich_su["giaDongCua"] = giaDong

            # Tính % thay đổi
            changePct = (
                ((giaDong - giaMo) / giaMo) * 100
                if giaMo != 0 else 0
            )

            lich_su["changePct"] = changePct

            lich_su_model = lich_su_gia(**lich_su)

        else:
            # KHÔNG có lịch sử → dùng giá tham chiếu
            giaTC = cp.get("giaThamChieu", 0)

            lich_su_model = lich_su_gia(
                maCP=maCP,
                ngay=datetime.now(),
                giaMoCua=giaTC,
                giaDongCua=giaTC,
                giaCaoNhat=giaTC,
                giaThapNhat=giaTC,
                khoiLuong=0,
                changePct=0
            )

        # ========================
        # TẠO MODEL so_huu
        # ========================
        so_huu_model = so_huu(
            maCP=maCP,
            soLuong=s.get("soLuong", 0),
            coPhieu=co_phieu(
                maCP=cp["maCP"],
                tenCongTy=cp.get("tenCongTy", "N/A"),
                giaThamChieu=cp.get("giaThamChieu", 0),
                giaTran=cp.get("giaTran", 0),
                giaSan=cp.get("giaSan", 0),
                giaDongCua=lich_su_model.giaDongCua
            )
        )

        result.append(
            WatchlistItem(
                soHuu=so_huu_model,
                lichSuGia=lich_su_model
            )
        )

    return result

# Lấy top movers
async def get_top_movers(mode: str) -> List[lich_su_gia]:
    data = []

    # ==========================================
    # STEP 1: Lấy lịch sử giá gần nhất của mỗi cổ phiếu
    # ==========================================
    latest_price_stage = [
        {"$sort": {"maCP": 1, "ngay": -1}},
        {
            "$group": {
                "_id": "$maCP",
                "latest": {"$first": "$$ROOT"}  # lấy bản ghi mới nhất
            }
        },
        {"$replaceWith": "$latest"}
    ]

    # ==========================================
    # STEP 2: Join co_phieu để lấy giá tham chiếu
    # ==========================================
    base_lookup = [
        {
            "$lookup": {
                "from": "co_phieu",
                "localField": "maCP",
                "foreignField": "maCP",
                "as": "cp"
            }
        },
        {"$unwind": "$cp"},
        {
            "$addFields": {
                "giaDongHoacThamChieu": {
                    "$cond": [
                        {"$gt": ["$giaDongCua", 0]},
                        "$giaDongCua",
                        "$cp.giaThamChieu"
                    ]
                }
            }
        }
    ]

    # ==========================================
    # STEP 3: COMMON changePct
    # ==========================================
    changePct_field = {
        "$cond": [
            {"$eq": ["$giaMoCua", 0]},
            0,
            {
                "$multiply": [
                    {
                        "$divide": [
                            {"$subtract": ["$giaDongHoacThamChieu", "$giaMoCua"]},
                            "$giaMoCua"
                        ]
                    },
                    100
                ]
            }
        ]
    }

    # ==========================================
    # CHỌN MODE
    # ==========================================

    # ---------- MODE = VOLUME ----------
    if mode == "volume":
        pipeline = latest_price_stage + base_lookup + [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "changePct": changePct_field
                }
            },
            {"$sort": {"khoiLuong": -1}},
            {"$limit": 5}
        ]

    # ---------- MODE = VALUE ----------
    elif mode == "value":
        pipeline = latest_price_stage + base_lookup + [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "value": {"$multiply": ["$giaDongHoacThamChieu", "$khoiLuong"]},
                    "changePct": changePct_field
                }
            },
            {"$sort": {"value": -1}},
            {"$limit": 5}
        ]

    # ---------- MODE = GAINERS / LOSERS ----------
    elif mode in ["gainers", "losers"]:
        pipeline = latest_price_stage + base_lookup + [
            {
                "$project": {
                    "maCP": 1, "ngay": 1, "giaDongCua": 1, "giaMoCua": 1,
                    "giaCaoNhat": 1, "giaThapNhat": 1, "khoiLuong": 1,
                    "changePct": changePct_field
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

