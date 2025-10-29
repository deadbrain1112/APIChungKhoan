from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import date, datetime

class SoHuu(BaseModel):
    macp: str
    so_luong: int

class TaiKhoanGiaoDich(BaseModel):
    matk: str
    taikhoan: str
    matkhau: str
    sotien: float
    ngay_tao: date

class NhaDauTuSchema(BaseModel):
    mandt: str
    hoten: str
    ngaysinh: date
    cmnd: str
    diachi: str
    email: EmailStr
    gioitinh: str
    phone: str
    mkdg: str
    taikhoan_giaodich: TaiKhoanGiaoDich
    sohuu: List[SoHuu] = []

class NhaDauTuResponse(NhaDauTuSchema):
    id: str
