from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import LoginRequest, LoginResponse, nha_dau_tu, RegisterRequest

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
    matkhau = data.password

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
    ndt_dict["matkhau"] = matkhau # Nếu bạn lưu password vào DB

    # Lưu vào MongoDB
    result = await db.nha_dau_tu.insert_one(ndt_dict)

    return {"message": "Đăng ký thành công", "id": str(result.inserted_id)}


