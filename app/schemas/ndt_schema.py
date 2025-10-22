from pydantic import BaseModel
from typing import Optional

class NhaDauTuSchema(BaseModel):
    maNDT: str
    hoTen: str
    cmnd: str
    sdt: str
    email: str
    diaChi: str
    taikhoan: str
    matkhau: str
