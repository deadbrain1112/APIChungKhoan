from app.configs.database import nhadautu_col
from app.models.collections import to_dict

def get_all():
    data = list(nhadautu_col.find())
    return [to_dict(d) for d in data]

def get_by_id(maNDT: str):
    doc = nhadautu_col.find_one({"maNDT": maNDT})
    return to_dict(doc) if doc else None

def create(item: dict):
    nhadautu_col.insert_one(item)
    return {"message": "Đã thêm nhà đầu tư!"}

def update(maNDT: str, update: dict):
    result = nhadautu_col.update_one({"maNDT": maNDT}, {"$set": update})
    return result.modified_count > 0

def delete(maNDT: str):
    result = nhadautu_col.delete_one({"maNDT": maNDT})
    return result.deleted_count > 0
