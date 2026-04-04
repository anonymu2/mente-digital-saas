# routes/dashboard.py
from fastapi import APIRouter, Request
from utils.security import auth_middleware
from utils.binance_bot import get_profit

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request):
    user = auth_middleware(request)
    profit = get_profit(user)
    return {
        "name": user["name"],
        "email": user["email"],
        "profit": profit,
        "vipStatus": user["vipStatus"]
    }

@router.post("/verify-payment/{email}")
def verify_payment(email: str):
    from database import users
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        return {"error": "Usuario no encontrado"}
    user["vipStatus"] = "active"
    return {"vipStatus": "active", "message": "Pago confirmado ✅"}
