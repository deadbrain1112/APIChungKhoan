from fastapi import APIRouter, Form, HTTPException
from app.configs.database import nhadautu_col

router = APIRouter(prefix="/auth", tags=["Đăng nhập"])

@router.post("/login")
def login(
    taiKhoan: str = Form(...),
    matKhau: str = Form(...)
):

    print(f"Nhận login: taiKhoan={taiKhoan}, matKhau={matKhau}")

    user = nhadautu_col.find_one({
        "taiKhoan": taiKhoan,
        "matKhau": matKhau
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
