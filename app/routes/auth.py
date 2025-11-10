from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import LoginRequest, LoginResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest):
    ndt = await db.nha_dau_tu.find_one({
        "taikhoan": data.taikhoan.strip(),
        "matkhau": data.matkhau.strip()
    })

    if not ndt:
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu")
    return LoginResponse(
        maNDT=str(ndt["_id"]),
        ten=ndt.get("ten", ""),
        email=ndt.get("email", "")
    )
