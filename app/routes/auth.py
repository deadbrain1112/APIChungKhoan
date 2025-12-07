import random
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.configs.email import send_email
from app.models.models import LoginRequest, LoginResponse, nha_dau_tu, RegisterRequest, ResetPasswordRequest, \
    VerifyOtpRequest, ForgotPasswordRequest, PasswordResetRecord

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

@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    email = data.email

    ndt = await db.nha_dau_tu.find_one({"email": email})
    if not ndt:
        raise HTTPException(status_code=404, detail="Email không tồn tại")

    # tạo mã OTP
    otp = str(random.randint(100000, 999999))

    record = PasswordResetRecord(
        email=email,
        otp=otp,
        expiresAt=datetime.utcnow() + timedelta(minutes=5)
    )

    # xoá old otp
    await db.password_reset.delete_many({"email": email})

    # lưu new otp
    await db.password_reset.insert_one(record.dict())

    subject = "Mã xác nhận đặt lại mật khẩu"
    content = f"""
        <h3>Mã OTP của bạn:</h3>
        <h2>{otp}</h2>
        <p>Mã OTP có hiệu lực trong 5 phút.</p>
    """

    success = await send_email(email, subject, content)

    if not success:
        raise HTTPException(status_code=500, detail="Không gửi được email OTP")

    return {"message": "OTP đã gửi qua email thành công"}


# ---------- 2. Xác minh OTP ----------
@router.post("/verify-otp")
async def verify_otp(data: VerifyOtpRequest):
    record = await db.password_reset.find_one({
        "email": data.email,
        "otp": data.otp
    })

    if not record:
        raise HTTPException(status_code=400, detail="OTP không chính xác")

    if datetime.utcnow() > record["expiresAt"]:
        raise HTTPException(status_code=400, detail="OTP đã hết hạn")

    # tạo token reset password
    token = str(random.randint(100000000, 999999999))

    # cập nhật token vào record
    await db.password_reset.update_one(
        {"email": data.email},
        {"$set": {"token": token}}
    )

    return {"message": "Xác thực thành công", "token": token}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest):
    record = await db.password_reset.find_one({"token": data.token})

    if not record:
        raise HTTPException(status_code=400, detail="Token không hợp lệ")

    email = record["email"]

    # update mật khẩu
    result = await db.nha_dau_tu.update_one(
        {"email": email},
        {"$set": {"matkhau": data.newPassword}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Không thể đặt mật khẩu mới")

    await db.password_reset.delete_many({"email": email})

    return {"message": "Đặt mật khẩu mới thành công"}
