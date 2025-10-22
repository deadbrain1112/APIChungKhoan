from datetime import datetime
from bson import ObjectId
from app.configs.database import nhadautu_collection
from app.models.ndt_model import ndt_helper

async def get_all_ndt():
    ndts = []
    async for ndt in nhadautu_collection.find():
        ndts.append(ndt_helper(ndt))
    return ndts

async def get_ndt_by_username(username: str):
    ndt = await nhadautu_collection.find_one({"taikhoan": username})
    return ndt_helper(ndt) if ndt else None

async def create_ndt(data: dict):
    data["ngay_tao"] = datetime.utcnow()
    result = await nhadautu_collection.insert_one(data)
    return await nhadautu_collection.find_one({"_id": result.inserted_id})

async def check_login(username: str, password: str):
    ndt = await nhadautu_collection.find_one({"taikhoan": username, "matkhau": password})
    return ndt_helper(ndt) if ndt else None
