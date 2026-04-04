from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.post("/verify-payment/{email}")
def verify(email: str):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET is_vip=TRUE WHERE email=%s", (email,))
    conn.commit()

    return {"status": "VIP ACTIVADO"}
