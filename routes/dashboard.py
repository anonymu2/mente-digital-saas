from fastapi import APIRouter, HTTPException
from utils.security import decode_token
from database import get_db

router = APIRouter()

@router.get("/dashboard")
def dashboard(token: str):
    conn = get_db()
    cur = conn.cursor()
    try:
        user_data = decode_token(token)
        cur.execute("SELECT email, is_vip, profit FROM users WHERE email=%s", (user_data["email"],))
        db_user = cur.fetchone()
        if not db_user:
            raise HTTPException(404, "Usuario no encontrado")
        return {
            "email": db_user["email"],
            "profit": db_user.get("profit", 0.0),
            "vipStatus": "active" if db_user["is_vip"] else "inactive"
        }
    finally:
        cur.close()
