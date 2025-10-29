from pydantic import BaseModel
from datetime import datetime

class LichSuBienDongSchema(BaseModel):
    mandt: str
    matk: str
    thoigian: datetime
    loaigd: str
    sotien_biendong: float
    sodu_truoc: float
    sodu_sau: float
    lydo: str

class LichSuBienDongResponse(LichSuBienDongSchema):
    id: str
