import os
import sys
import ccxt
import database 
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Forzar a Python a buscar 'database.py' en la misma carpeta del backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Mente Digital VIP API")

# Configuración de CORS para que tu App de Flutter pueda conectarse
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de datos para recibir llaves de Binance
class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

@app.get("/")
async def root():
    return {
        "status": "Mente Digital API Online",
        "message": "Servidor listo para trading"
    }

@app.get("/status")
async def get_status():
    # Aquí puedes luego conectar la lógica real de tu worker.py
    return {
        "status": "Bot Operando en Binance 🚀",
        "active": True
    }

@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    """
    Valida las llaves con Binance y las guarda en la base de datos de Render.
    """
    try:
        # Intenta conectar a Binance para ver si las llaves son reales
        exchange = ccxt.binance({
            'apiKey': keys.api_key,
            'secret': keys.api_secret,
            'enableRateLimit': True,
        })
        exchange.fetch_balance() # Si esto falla, las llaves son malas
    except Exception:
        raise HTTPException(status_code=401, detail="Las llaves de Binance son incorrectas o no tienen permisos.")

    conn = database.get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión con la base de datos.")

    try:
        cur = conn.cursor()
        # Actualizamos las llaves del usuario según su email
        cur.execute("""
            UPDATE users 
            SET api_key = %s, api_secret = %s 
            WHERE email = %s
        """, (keys.api_key, keys.api_secret, keys.email))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "API Keys vinculadas correctamente"}
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=f"Error al guardar: {str(e)}")

@app.get("/history/{email}")
async def get_history(email: str):
    """
    Obtiene los últimos 20 trades del usuario para mostrar en la App.
    """
    conn = database.get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT symbol, side, CAST(amount_usdt AS FLOAT), 
                   CAST(price_entry AS FLOAT), created_at 
            FROM trade_history 
            WHERE user_email = %s 
            ORDER BY created_at DESC LIMIT 20
        """, (email,))
        trades = cur.fetchall()
        cur.close()
        conn.close()
        
        return [
            {
                "symbol": t[0],
                "side": t[1],
                "amount": t[2],
                "price": t[3],
                "date": t[4].strftime("%Y-%m-%d %H:%M:%S")
            } for t in trades
        ]
    except Exception as e:
        if conn: conn.close()
        return []

if __name__ == "__main__":
    import uvicorn
    # En local corre en el puerto 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
