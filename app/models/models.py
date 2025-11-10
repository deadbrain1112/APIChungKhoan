from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PortfolioSummary(BaseModel):
    nav: int
    pnlToday: int
    pnlPct: float
    cash: int

class CoPhieu(BaseModel):
    maCP: str
    tenCongTy: str
    giaDongCua: Optional[float] = 0

class LichSuGia(BaseModel):
    maCP: str
    ngay: datetime
    giaMoCua: float
    giaDongCua: float
    giaCaoNhat: float
    giaThapNhat: float
    khoiLuong: int
    changePct: Optional[float] = 0

class SoHuu(BaseModel):
    maCP: str
    soLuong: int
    coPhieu: CoPhieu

class WatchlistItem(BaseModel):
    soHuu: SoHuu
    lichSuGia: Optional[LichSuGia] = None

class LoginRequest(BaseModel):
    taikhoan: str
    matkhau: str

class LoginResponse(BaseModel):
    maNDT: str
    ten: str
    email: str
