from fastapi import FastAPI
from routes import auth, dashboard, payment, trading, user

app = FastAPI(title="Mente Digital API PRO")

app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(payment.router, prefix="/api")
app.include_router(trading.router, prefix="/api")
app.include_router(user.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "API Mente Digital VIP Online"}
