from bson import ObjectId
from typing import List
from app.configs.database import db
from app.models.models import so_huu, CoPhieu, WatchlistItem, lich_su_gia

# Tính NAV
async def compute_nav(maNDT: str) -> int:
    ndt_id = ObjectId(maNDT)
    ndt = await db.nha_dau_tu.find_one({"_id": ndt_id})
    if not ndt:
        return 0

    total_value = 0
    async for s in db.so_huu.find({"maNDT": ndt_id}):
        maCP = s["maCP"]
        lich_su = await db.lich_su_gia.find_one({"maCP": maCP}, sort=[("ngay", -1)])
        giaDongCua = lich_su["giaDongCua"] if lich_su else 0
        total_value += giaDongCua * s["soLuong"]

    nav = total_value + ndt.get("tien_kha_dung", 0) - ndt.get("tong_no", 0)
    return nav

# Lấy watchlist
async def get_watchlist(maNDT: str) -> List[WatchlistItem]:
    ndt_id = ObjectId(maNDT)
    result = []
    async for s in db.so_huu.find({"maNDT": ndt_id}):
        maCP = s["maCP"]
        cp = await db.co_phieu.find_one({"maCP": maCP})
        lich_su = await db.lich_su_gia.find_one({"maCP": maCP}, sort=[("ngay", -1)])
        item = WatchlistItem(
            soHuu=so_huu(
                maCP=maCP,
                soLuong=s["soLuong"],
                coPhieu=CoPhieu(
                    maCP=cp["maCP"],
                    tenCongTy=cp["tenCongTy"],
                    giaDongCua=lich_su["giaDongCua"] if lich_su else 0
                )
            ),
            lichSuGia=lich_su_gia(**lich_su) if lich_su else None
        )
        result.append(item)
    return result

# Lấy top movers
async def get_top_movers(mode: str) -> List[lich_su_gia]:
    data = []
    if mode == "volume":
        cursor = db.lich_su_gia.find().sort("khoiLuong", -1).limit(5)
        data = [d async for d in cursor]
    elif mode == "value":
        pipeline = [
            {"$project": {"maCP":1, "ngay":1, "giaDongCua":1, "giaMoCua":1,
                          "giaCaoNhat":1, "giaThapNhat":1, "khoiLuong":1,
                          "value": {"$multiply":["$giaDongCua","$khoiLuong"]}} },
            {"$sort": {"value": -1}},
            {"$limit": 5}
        ]
        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]
    elif mode in ["gainers", "losers"]:
        pipeline = [
            {"$project": {"maCP":1, "ngay":1, "giaDongCua":1, "giaMoCua":1,
                          "giaCaoNhat":1, "giaThapNhat":1, "khoiLuong":1,
                          "changePct": {"$multiply":[{"$divide":[{"$subtract":["$giaDongCua","$giaMoCua"]},"$giaMoCua"]},100]}} }
        ]
        if mode == "gainers":
            pipeline.append({"$sort": {"changePct": -1}})
        else:
            pipeline.append({"$sort": {"changePct": 1}})
        pipeline.append({"$limit": 5})
        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]

    return [lich_su_gia(**d) for d in data]
