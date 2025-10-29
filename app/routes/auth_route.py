from fastapi import APIRouter
from app.configs.database import nhadautu_col  # giả sử đây là Motor collection

router = APIRouter()

@router.post("/login")
async def login(taiKhoan: str, matKhau: str):
    user = await nhadautu_col.find_one({
        "taiKhoan": taiKhoan,
        "matKhau": matKhau
    })
    if not user:
        return {"message": "Sai tài khoản hoặc mật khẩu"}
    return {"message": "Đăng nhập thành công", "user": str(user["_id"])}
