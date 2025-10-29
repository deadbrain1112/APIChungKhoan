from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import nhadautu_route, cophieu_route, lenh_route, auth_route

app = FastAPI(title="API Giao Dịch Cổ Phiếu (MongoDB + FastAPI)")

# Cho phép CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn các router
app.include_router(auth_route.router)
app.include_router(nhadautu_route.router)
app.include_router(cophieu_route.router)
app.include_router(lenh_route.router)

@app.get("/")
def root():
    return {"message": "Chào mừng đến API Giao Dịch Cổ Phiếu!"}
