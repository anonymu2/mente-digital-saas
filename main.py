import ccxt
import database  # Importación directa para Render
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Mente Digital VIP API")

# --- CONFIGURACIÓN DE SEGURIDAD (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de datos para las peticiones
class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

@app.get("/")
async def root():
    return {"status": "Mente Digital API Online", "version": "1.2.0"}

# 1. OBTENER HISTORIAL DE TRADES (PostgreSQL)
@app.get("/history/{email}")
async def get_history(email: str):
    conn = database.get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a la DB")
    
    try:
        cur = conn.cursor()
        query = """
            SELECT symbol, side, 
                   CAST(amount_usdt AS FLOAT) as amount, 
                   CAST(price_entry AS FLOAT) as price, 
                   status,
                   created_at 
            FROM trade_history 
            WHERE user_email = %s 
            ORDER BY created_at DESC LIMIT 20
        """
        cur.execute(query, (email,))
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail=str(e))

# 2. VALIDAR Y GUARDAR LLAVES DE BINANCE
@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    # --- PASO A: VALIDACIÓN REAL CON CCXT ---
    try:
        exchange = ccxt.binance({
            'apiKey': keys.api_key,
            'secret': keys.api_secret,
            'enableRateLimit': True,
        })
        # Intentamos leer el balance para confirmar que las llaves funcionan
        exchange.fetch_balance()
    except Exception:
        # Si falla el fetch_balance, las llaves no sirven
        raise HTTPException(
            status_code=401, 
            detail="Binance rechazó las llaves. Verifica que tengan permisos de lectura."
        )

    # --- PASO B: GUARDAR EN POSTGRESQL SI SON VÁLIDAS ---
    conn = database.get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE users 
            SET api_key = %s, api_secret = %s 
            WHERE email = %s
        """, (keys.api_key, keys.api_secret, keys.email))
        
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Llaves vinculadas correctamente"}
    except Exception as e:
        if conn: conn.close()
        raise HTTPException(status_code=500, detail="Error interno al guardar llaves")

# 3. ESTATUS DEL USUARIO (VIP/ACTIVO)
@app.get("/user-status/{email}")
async def get_status(email: str):
    conn = database.get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT subscription_status FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return {"status": user['subscription_status']}
        return {"status": "inactive"}
    except Exception:
        if conn: conn.close()
        return {"status": "error"}
