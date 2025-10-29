from pydantic import BaseModel
from typing import List
from datetime import date

class LichSuGia(BaseModel):
    ngay: date
    gia_san: float
    gia_tran: float
    gia_tc: float

class CoPhieuSchema(BaseModel):
    macp: str
    tencty: str
    diachi: str
    soluongph: int
    lichsu_gia: List[LichSuGia] = []

class CoPhieuResponse(CoPhieuSchema):
    id: str
