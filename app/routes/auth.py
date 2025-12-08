import random
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import LoginRequest, LoginResponse, RegisterRequest, ResetPasswordOTP

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

@router.post("/register")
async def register_account(data: RegisterRequest):
    ndt = data.ndt
    matkhau = data.matkhau

    # Kiểm tra email
    existed_email = await db.nha_dau_tu.find_one({"email": ndt.email})
    if existed_email:
        raise HTTPException(status_code=400, detail="Email đã tồn tại")

    # Kiểm tra tài khoản
    existed_tk = await db.nha_dau_tu.find_one({"taikhoan": ndt.taikhoan})
    if existed_tk:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")

    # Chuẩn bị dữ liệu để lưu
    ndt_dict = ndt.dict(exclude_none=True)
    ndt_dict["matkhau"] = matkhau

    # Lưu vào MongoDB
    result = await db.nha_dau_tu.insert_one(ndt_dict)

    return {"message": "Đăng ký thành công", "id": str(result.inserted_id)}

@router.post("/save-otp")
async def save_otp(data: dict):
    email = data["email"]
    otp = data["otp"]
    expire = datetime.utcnow() + timedelta(minutes=5)

    await db.otp_codes.update_one(
        {"email": email},
        {"$set": {"otp": otp, "expired_at": expire}},
        upsert=True
    )

    return {"message": "OTP saved"}
@router.post("/reset-password")
async def reset_password_otp(data: ResetPasswordOTP):
    email = data.email.strip()
    otp = data.otp.strip()
    new_password = data.newPassword.strip()

    # 1. Lấy OTP theo email
    otp_doc = await db.password_reset.find_one({"email": email})

    if otp_doc is None:
        raise HTTPException(status_code=400, detail="Không tìm thấy yêu cầu đặt lại mật khẩu")

    # 2. Kiểm tra OTP
    if otp != otp_doc["otp"]:
        raise HTTPException(status_code=400, detail="OTP không chính xác")

    # 3. Kiểm tra hết hạn
    expired_at = otp_doc["expired_at"]
    if datetime.now(timezone.utc) > expired_at:
        raise HTTPException(status_code=400, detail="OTP đã hết hạn")

    # 4. Cập nhật mật khẩu KHÔNG hash
    update_result = await db.nha_dau_tu.update_one(
        {"email": email},
        {"$set": {"password": new_password}}
    )

    if update_result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Không thể cập nhật mật khẩu")

    # 5. Xóa OTP sau khi sử dụng
    await db.password_reset.delete_one({"email": email})

    return {"message": "Đổi mật khẩu thành công"}