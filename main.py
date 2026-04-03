import os
import sys
import ccxt
import database 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Aseguramos que la raíz esté en el PATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Mente Digital VIP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

@app.get("/")
async def root():
    return {"status": "Mente Digital API Online", "database": "Conectado"}

@app.get("/history/{email}")
async def get_history(email: str):
    conn = database.get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de DB")
    try:
        cur = conn.cursor()
        # CAST a FLOAT para que Flutter no llore con los tipos de datos
        cur.execute("""
            SELECT symbol, side, CAST(amount_usdt AS FLOAT) as amount, 
                   CAST(price_entry AS FLOAT) as price, created_at 
            FROM trade_history WHERE user_email = %s 
            ORDER BY created_at DESC LIMIT 20
        """, (email,))
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    try:
        exchange = ccxt.binance({'apiKey': keys.api_key, 'secret': keys.api_secret})
        exchange.fetch_balance()
    except Exception:
        raise HTTPException(status_code=401, detail="Llaves inválidas")

    conn = database.get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET api_key = %s, api_secret = %s WHERE email = %s", 
                    (keys.api_key, keys.api_secret, keys.email))
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail="Error al guardar")
