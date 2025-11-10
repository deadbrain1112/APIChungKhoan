from fastapi import FastAPI
from routes import auth, portfolio, watchlist, top_movers

app = FastAPI(title="ChungKhoan API")

# Include routers
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(top_movers.router)
