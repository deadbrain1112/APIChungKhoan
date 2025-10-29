from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class NhaDauTuCreate(BaseModel):
    maNDT: str
    hoTen: str
    ngaySinh: Optional[date]
    diaChi: str
    phone: str
    cmnd: str
    gioiTinh: str
    email: Optional[EmailStr]
    taiKhoan: str
    matKhau: str
    soDu: float = 0.0
    trangThai: str = "Hoạt động"
    ngayTao: datetime = datetime.now()
