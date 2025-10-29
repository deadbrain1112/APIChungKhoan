from datetime import datetime
from app.configs.database import lenhdat_col, lenhkhop_col
from app.models.collections import to_dict

def get_all_lenhdat():
    data = list(lenhdat_col.find())
    return [to_dict(d) for d in data]

def create_lenhdat(item: dict):
    item["ngayGD"] = datetime.now()
    lenhdat_col.insert_one(item)
    return {"message": "Đã thêm lệnh đặt!"}

def get_all_lenhkhop():
    data = list(lenhkhop_col.find())
    return [to_dict(d) for d in data]

def create_lenhkhop(item: dict):
    item["ngayGioKhop"] = datetime.now()
    lenhkhop_col.insert_one(item)
    return {"message": "Đã thêm lệnh khớp!"}
