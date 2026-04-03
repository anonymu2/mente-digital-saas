import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import uvicorn

app = FastAPI(title="Mente Digital SaaS - Payment System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

# --- MODELOS ---
class User(BaseModel):
    email: str
    password: str

class Payment(BaseModel):
    email: str
    txid: str

# --- RUTAS ---

@app.get("/")
def home():
    return {"status": "Aeterna Bot System Live"}

# 1. Registro (Crea el usuario como INACTIVO por defecto)
@app.post("/register")
async def register(user: User):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        hashed_pw = pwd_context.hash(user.password)
        # Seteamos 'active' como False al registrar
        cur.execute(
            "INSERT INTO users (email, password, active) VALUES (%s, %s, FALSE) ON CONFLICT (email) DO NOTHING",
            (user.email, hashed_pw)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error de registro")

# 2. Login (Devuelve si el usuario está activo o no)
@app.post("/login")
async def login(user: User):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password, active FROM users WHERE email = %s", (user.email,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and pwd_context.verify(user.password, result[0]):
            return {"status": "success", "active": result[1]}
        raise HTTPException(status_code=401, detail="Error de acceso")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error de servidor")

# 3. Verificar Pago (Recibe el TXID de los 50 USDT)
@app.post("/verify-payment")
async def verify_payment(pay: Payment):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Guardamos el TXID para que tú lo revises en tu Binance
        cur.execute(
            "UPDATE users SET txid = %s WHERE email = %s",
            (pay.txid, pay.email)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "TXID registrado para revision"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar TXID")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
