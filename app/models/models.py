from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ---------- TÀI KHOẢN ----------
class LoginRequest(BaseModel):
    taikhoan: str
    matkhau: str

class LoginResponse(BaseModel):
    maNDT: str
    ten: str
    email: str


# ---------- CỔ PHIẾU ----------
class co_phieu(BaseModel):
    maCP: str
    tenCongTy: str
    giaThamChieu: Optional[float] = 0
    giaTran: Optional[float] = 0
    giaSan: Optional[float] = 0
    giaDongCua: Optional[float] = 0


# ---------- LỊCH SỬ GIÁ ----------
class lich_su_gia(BaseModel):
    maCP: str
    ngay: datetime
    giaMoCua: float
    giaDongCua: float
    giaCaoNhat: float
    giaThapNhat: float
    khoiLuong: int



# ---------- SỞ HỮU ----------
class so_huu(BaseModel):
    maCP: str
    soLuong: int
    coPhieu: Optional[co_phieu] = None


# ---------- WATCHLIST (DANH MỤC QUAN TÂM) ----------
class WatchlistItem(BaseModel):
    soHuu: so_huu
    lichSuGia: Optional[lich_su_gia] = None


# ---------- TỔNG QUAN DANH MỤC ----------
class PortfolioSummary(BaseModel):
    nav: int
    pnlToday: int
    pnlPct: float
    cash: int


# ---------- LỆNH GIAO DỊCH ----------
class OrderModel(BaseModel):
    maNDT: str = Field(..., description="Mã nhà đầu tư")
    maCP: str = Field(..., description="Mã cổ phiếu")
    loaiGD: str = Field(..., description="M = Mua, B = Bán")
    loaiLenh: str = Field(..., description="LO / ATO / ATC")
    gia: float = Field(..., description="Giá đặt")
    soLuong: int = Field(..., description="Số lượng cổ phiếu")
    trangThai: Optional[str] = Field(default="Chờ khớp")
    ngayGD: Optional[datetime] = Field(default_factory=datetime.now)


# ---------- TRẢ VỀ LỆNH ----------
class OrderResponse(BaseModel):
    _id: Optional[str]
    maNDT: str
    maCP: str
    loaiGD: str
    loaiLenh: str
    gia: float
    soLuong: int
    trangThai: str
    ngayGD: datetime
