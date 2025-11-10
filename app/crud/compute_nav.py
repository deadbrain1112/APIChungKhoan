from bson import ObjectId
from app.configs.database import db

async def compute_nav(maNDT: str) -> int:
    ndt_id = ObjectId(maNDT)
    ndt = await db.NhaDauTu.find_one({"_id": ndt_id})
    if not ndt:
        return 0

    total_value = 0
    async for s in db.SoHuu.find({"maNDT": ndt_id}):
        maCP = s["maCP"]
        lich_su = await db.LichSuGia.find_one({"maCP": maCP}, sort=[("ngay", -1)])
        giaDongCua = lich_su["giaDongCua"] if lich_su else 0
        total_value += giaDongCua * s["soLuong"]

    nav = total_value + ndt.get("tien_kha_dung", 0) - ndt.get("tong_no", 0)
    return nav
