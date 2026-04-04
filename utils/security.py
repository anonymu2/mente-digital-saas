from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "MENTE_DIGITAL_SECRET"
ALGORITHM = "HS256"

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def create_token(data: dict):
    data_copy = data.copy()
    data_copy["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(data_copy, SECRET_KEY, algorithm=ALGORITHM)
