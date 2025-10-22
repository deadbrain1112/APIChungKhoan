import os
from dotenv import load_dotenv

# ==========================================================
# 📦 Tải các biến môi trường từ file .env
# ==========================================================
load_dotenv()

# ==========================================================
# 🗄️ Cấu hình MongoDB
# ==========================================================
MONGO_URI = os.getenv("MONGODB_URI", "mongodb+srv://congtiengod_db_user:ahihi1234@chungkhoan.hk5fj6c.mongodb.net/?retryWrites=true&w=majority&appName=Chungkhoan")
DATABASE_NAME = os.getenv("MONGODB_DB", "chungkhoan_pro")

# ==========================================================
# 🔐 Cấu hình JWT (Token đăng nhập)
# ==========================================================
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ==========================================================
# 💳 Cấu hình PayOS (Thanh toán)
# ==========================================================
PAYOS_CLIENT_ID = os.getenv("PAYOS_CLIENT_ID", "")
PAYOS_API_KEY = os.getenv("PAYOS_API_KEY", "")
PAYOS_CHECKSUM_KEY = os.getenv("PAYOS_CHECKSUM_KEY", "")
PAYOS_RETURN_URL = os.getenv("PAYOS_RETURN_URL", "http://localhost:3000/payment/success")
PAYOS_CANCEL_URL = os.getenv("PAYOS_CANCEL_URL", "http://localhost:3000/payment/cancel")


