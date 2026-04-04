from fastapi import APIRouter
from database import get_db

router = APIRouter()

@router.get("/user-status/{email}")
def status(email: str):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT is_vip FROM users WHERE email=%s", (email,))
    user = cur.fetchone()

    return {"status": "active" if user and user["is_vip"] else "inactive"}
