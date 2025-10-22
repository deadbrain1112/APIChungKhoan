from bson import ObjectId
from datetime import datetime

def ndt_helper(ndt) -> dict:
    return {
        "id": str(ndt["_id"]),
        "maNDT": ndt["maNDT"],
        "hoTen": ndt["hoTen"],
        "cmnd": ndt["cmnd"],
        "sdt": ndt["sdt"],
        "email": ndt["email"],
        "diaChi": ndt["diaChi"],
        "taikhoan": ndt["taikhoan"],
        "ngay_tao": ndt.get("ngay_tao", datetime.utcnow()),
    }
