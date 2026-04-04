# utils/security.py
import bcrypt, jwt
from fastapi import HTTPException

SECRET = "TU_SECRET_KEY"

# Hash de contraseña
def hash_password(password: str):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# JWT
def create_token(payload: dict):
    import datetime
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=7)
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except:
        raise HTTPException(401, "Token inválido")
