from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.models import LoginRequest, LoginResponse, nha_dau_tu

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
from fastapi import APIRouter, HTTPException
from app.configs.database import db
from app.models.nhadau_tu import NhaDauTu
from bson import ObjectId

router = APIRouter()

@router.post("/register")
async def register_account(ndt: NhaDauTu, password: str):
    # Kiểm tra email trùng
    existed = await db.nha_dau_tu.find_one({"email": ndt.email})
    if existed:
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    # Kiểm tra tài khoản trùng
    existed = await db.nha_dau_tu.find_one({"taikhoan": ndt.taikhoan})
    if existed:
        raise HTTPException(status_code=400, detail="Tài khoản đã tồn tại")

    # Tạo document
    data = ndt.dict()
    data["password"] = password            # không mã hóa
    data["faceEmbeddings"] = ndt.faceEmbeddings or ""  # mặc định chuỗi rỗng

    # Lưu vào DB (Mongo tự tạo _id)
    result = await db.nha_dau_tu.insert_one(data)

    return {
        "message": "Đăng ký thành công",
        "id": str(result.inserted_id)
    }
