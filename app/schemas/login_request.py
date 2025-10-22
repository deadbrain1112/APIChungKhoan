from pydantic import BaseModel

class LoginRequest(BaseModel):
    taikhoan: str
    matkhau: str
