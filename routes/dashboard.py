from fastapi import APIRouter, HTTPException, Depends
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
        if not user_data:
            raise HTTPException(401, "Token inválido")
        cur.execute("SELECT email, is_vip FROM users WHERE email=%s", (user_data["email"],))
        db_user = cur.fetchone()
        if not db_user:
            raise HTTPException(404, "Usuario no encontrado")
        return {
            "email": db_user["email"],
            "profit": get_profit(db_user["email"]),
            "vipStatus": "active" if db_user["is_vip"] else "inactive"
        }
    finally:
        cur.close()
