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
async def get_top_movers(mode: str) -> List[lich_su_gia]:

    if mode in ["gainers", "losers"]:
        pipeline = [
            # 1. Lấy phiên mới nhất theo từng mã
            {"$sort": {"maCP": 1, "ngay": -1}},
            {"$group": {
                "_id": "$maCP",
                "maCP": {"$first": "$maCP"},
                "ngay": {"$first": "$ngay"},
                "giaMoCua": {"$first": "$giaMoCua"},
                "giaDongCua": {"$first": "$giaDongCua"},
                "giaCaoNhat": {"$first": "$giaCaoNhat"},
                "giaThapNhat": {"$first": "$giaThapNhat"},
                "khoiLuong": {"$first": "$khoiLuong"},
            }},
            # 2. Tính tỷ lệ phần trăm thay đổi
            {"$project": {
                "maCP": 1,
                "ngay": 1,
                "giaMoCua": 1,
                "giaDongCua": 1,
                "giaCaoNhat": 1,
                "giaThapNhat": 1,
                "khoiLuong": 1,
                "changePct": {
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
            }}
        ]

        # 3. Sort theo tăng hoặc giảm
        if mode == "gainers":
            pipeline.append({"$sort": {"changePct": -1}})
        else:
            pipeline.append({"$sort": {"changePct": 1}})

        # 4. Lấy top 5
        pipeline.append({"$limit": 5})

        cursor = db.lich_su_gia.aggregate(pipeline)
        data = [d async for d in cursor]
        return [lich_su_gia(**d) for d in data]

