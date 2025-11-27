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
    changePct: float | None = None


# ---------- SỞ HỮU ----------
class so_huu(BaseModel):
    maCP: str
    soLuong: int
    coPhieu: Optional[co_phieu] = None


# ---------- WATCHLIST ----------
class WatchlistItem(BaseModel):
    soHuu: so_huu
    lichSuGia: Optional[lich_su_gia] = None


# ---------- TỔNG QUAN DANH MỤC ----------
class PortfolioSummary(BaseModel):
    nav: int
    pnlToday: int
    pnlPct: float
    cash: int


# ============================================================
#                 📌 BỔ SUNG CHO ORDER BUY / SELL
# ============================================================

# ---------- LỆNH GIAO DỊCH ----------
class OrderModel(BaseModel):
    maNDT: str = Field(..., description="Mã nhà đầu tư")
    maCP: str = Field(..., description="Mã cổ phiếu")
    loaiGD: str = Field(..., description="M = Mua, B = Bán")
    loaiLenh: str = Field(..., description="LO / ATO / ATC")
    gia: float = Field(..., description="Giá đặt")
    soLuong: int = Field(..., description="Số lượng cổ phiếu")
    trangThai: Optional[str] = "Chờ khớp"
    ngayGD: Optional[datetime] = Field(default_factory=datetime.now)


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


# ============================================================
#             📌 MODEL BỔ SUNG CHO BUY / SELL
# ============================================================

# ------- CO PHIEU DUNG CHO MarketDiscovery, Buy, Sell --------
class Stock(BaseModel):
    maCP: str
    tenCP: str
    giaDongCua: float
    giaThamChieu: float
    phanTramThayDoi: float
    chenhlech: Optional[float] = 0


# ---------- DANH SÁCH LỊCH SỬ GIÁ DẠNG NẾN ----------
class CandleEntry(BaseModel):
    open: float
    high: float
    low: float
    close: float
    ngay: datetime


class CandlestickData(BaseModel):
    maCP: str
    candles: List[CandleEntry]


# ---------- LỆNH CHỜ (PENDING ORDER) ----------
class PendingOrder(BaseModel):
    _id: Optional[str]
    maCP: str
    soLuong: int
    loaiLenh: str
    gia: float
    trangThai: str
    thoiGian: datetime


# ---------- STOCK OWNED (DÙNG CHO SELL FRAGMENT) ----------
class StockOwned(BaseModel):
    maCP: str
    soLuong: int
    giaVon: Optional[float] = 0      # giá vốn (nếu có)
    giaHienTai: Optional[float] = 0  # từ bảng giá
    giaTri: Optional[float] = 0      # soLuong * giaHienTai

# ---------- SAOKE(THONGKEGIAODICH) ----------
class GiaoDich(BaseModel):
    _id: Optional[str]
    maNDT: str
    kieu: str               # cp, nap, rut
    maCP: Optional[str] = None
    loaiGD: Optional[str] = None
    loaiLenh: Optional[str] = None
    gia: Optional[float] = None
    soLuong: Optional[int] = None
    soTien: Optional[float] = None
    trangThai: str
    ngayGD: datetime

class LenhDat(BaseModel):
    _id: Optional[str]
    maNDT: str
    maCP: str
    loaiGD: str
    loaiLenh: str
    gia: float
    soLuong: int
    trangThai: str
    ngayGD: datetime
