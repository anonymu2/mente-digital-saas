# routes/dashboard.py
from fastapi import APIRouter, HTTPException
from utils.security import decode_token
from database import get_db
from utils.binance_bot import get_profit

router = APIRouter()

@router.get("/dashboard")
def dashboard(token: str):
    conn = get_db()
    cur = conn.cursor()
    try:
        user_data = decode_token(token)
        cur.execute("SELECT email, is_vip FROM users WHERE email=%s", (user_data["email"],))
        db_user = cur.fetchone()
        if not db_user:
            raise HTTPException(404, "Usuario no encontrado")
        profit = get_profit()
        return {
            "email": db_user["email"],
            "profit": profit,
            "vipStatus": "active" if db_user["is_vip"] else "inactive"
        }
    finally:
        cur.close()
        conn.close()

@router.post("/verify-payment/{email}")
def verify_payment(email: str):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE users SET is_vip=TRUE WHERE email=%s", (email,))
        conn.commit()
        return {"vipStatus": "active", "message": "Pago confirmado ✅"}
    finally:
        cur.close()
        conn.close()
