from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.configs.database import nhadautu_col  # motor async collection

router = APIRouter(prefix="/auth", tags=["Đăng nhập"])

class LoginRequest(BaseModel):
    taiKhoan: str
    matKhau: str

@router.post("/login")
async def login(req: LoginRequest):
    try:
        user = await nhadautu_col.find_one({
            "taiKhoan": req.taiKhoan,
            "matKhau": req.matKhau
        })

        if not user:
            raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu!")

        return {
            "message": "Đăng nhập thành công!",
            "maNDT": user.get("maNDT"),
            "hoTen": user.get("hoTen"),
            "email": user.get("email"),
            "soDu": user.get("soDu", 0)
        }

    except Exception as e:
        print("❌ Lỗi khi đăng nhập:", e)
        raise HTTPException(status_code=500, detail="Lỗi server nội bộ")
