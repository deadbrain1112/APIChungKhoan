from pydantic import BaseModel
from datetime import datetime

class LenhKhopSchema(BaseModel):
    magd: str
    malh: str
    ngaygio_khop: datetime
    soluongkhop: int
    giakhop: float
    kieukhop: str

class LenhKhopResponse(LenhKhopSchema):
    id: str
