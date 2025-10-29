from app.configs.database import cophieu_col
from app.models.collections import to_dict

def get_all():
    data = list(cophieu_col.find())
    return [to_dict(d) for d in data]

def create(item: dict):
    cophieu_col.insert_one(item)
    return {"message": "Đã thêm cổ phiếu!"}
