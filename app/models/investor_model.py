from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class Investor(BaseModel):
    maNDT: str
    hoTen: str
    ngaySinh: Optional[datetime] = None
    diaChi: Optional[str] = None
    phone: Optional[str] = None
    cmnd: Optional[str] = None
    gioiTinh: Optional[str] = None
    email: Optional[EmailStr] = None
    taiKhoan: str
    matKhau: str
    soDu: float = 0.0
    trangThai: str = "Hoạt động"
    ngayTao: datetime = datetime.now()
