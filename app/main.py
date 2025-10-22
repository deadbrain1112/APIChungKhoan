from fastapi import FastAPI
from app.routes import auth_router

app = FastAPI(title="Chứng khoán API")

app.include_router(auth_router.router)
