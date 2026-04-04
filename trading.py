from fastapi import APIRouter, HTTPException
from database import get_db
from models.schemas import BinanceKeys
from services.encryption_service import encrypt
from services.binance_service import validate_keys

router = APIRouter()

@router.post("/save-keys/{email}")
def save_keys(email: str, keys: BinanceKeys):

    if not validate_keys(keys.api_key, keys.api_secret):
        raise HTTPException(400, "API Keys inválidas")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users 
        SET api_key=%s, api_secret=%s
        WHERE email=%s
    """, (
        encrypt(keys.api_key),
        encrypt(keys.api_secret),
        email
    ))

    conn.commit()

    return {"status": "keys_saved"}


@router.get("/profit/{email}")
def profit(email: str):
    return {"profit": 12.5}


@router.get("/history/{email}")
def history(email: str):
    return []
