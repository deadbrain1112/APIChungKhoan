from fastapi import FastAPI
from app.routes import auth, portfolio, watchlist, top_movers, order, stocks, balance_route, transactions, napvarut,faceID

app = FastAPI(title="ChungKhoan API")

# Include routers
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(top_movers.router)
app.include_router(order.router)
app.include_router(stocks.router)
app.include_router(balance_route.router)
app.include_router(transactions.router)
app.include_router(napvarut.router)
app.include_router(faceID.router)