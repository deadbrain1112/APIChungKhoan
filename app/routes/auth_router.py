from fastapi import APIRouter, HTTPException
from app.schemas.login_request import LoginRequest
from app.schemas.login_response import LoginResponse
from app.services.ndt_service import check_login

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    ndt = await check_login(request.taikhoan, request.matkhau)
    if ndt:
        return LoginResponse(success=True, message="Đăng nhập thành công!", data=ndt)
    else:
        raise HTTPException(status_code=401, detail="Sai tài khoản hoặc mật khẩu!")
