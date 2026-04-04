from fastapi import APIRouter, HTTPException
from models.schemas import UserRegister, UserLogin
from database import get_db
from utils.security import hash_password, verify_password, create_token

router = APIRouter()

@router.post("/register")
def register(user: UserRegister):
    conn = get_db()
    cur = conn.cursor()

    hashed = hash_password(user.password)

    try:
        cur.execute(
            "INSERT INTO users (email, password, is_vip) VALUES (%s, %s, FALSE)",
            (user.email, hashed)
        )
        conn.commit()
        return {"status": "ok"}
    except:
        raise HTTPException(400, "Usuario ya existe")

@router.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT password, is_vip FROM users WHERE email=%s", (user.email,))
    db_user = cur.fetchone()

    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(401, "Credenciales incorrectas")

    token = create_token({"email": user.email})

    return {
        "access_token": token,
        "email": user.email,
        "subscription_status": "active" if db_user["is_vip"] else "inactive"
    }
