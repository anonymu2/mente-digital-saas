# utils/security.py
from fastapi import Request, HTTPException
from database import users

def get_user_by_token(token: str):
    return next((u for u in users if u["token"] == token), None)

def auth_middleware(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="No token")
    token = auth_header.split(" ")[1]
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Token inválido")
    return user
