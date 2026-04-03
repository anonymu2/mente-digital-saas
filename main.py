import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import uvicorn

app = FastAPI(title="Mente Digital API VIP")

# --- EL PUENTE DE COMUNICACIÓN (CORS) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- CONEXIÓN SEGURA CON RENDER ---
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise Exception("Error: DATABASE_URL no configurada en Render")
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

# --- MODELOS DE DATOS ---
class User(BaseModel):
    email: str
    password: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# --- RUTAS ---

@app.get("/")
def health():
    return {"status": "Mente Digital Online", "server": "Render Cloud"}

# 1. REGISTRO
@app.post("/register")
async def register(user: User):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        hashed_pw = pwd_context.hash(user.password)
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING",
            (user.email, hashed_pw)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Usuario registrado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al registrar")

# 2. LOGIN (Faltaba en tu código)
@app.post("/login")
async def login(user: User):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE email = %s", (user.email,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result and pwd_context.verify(user.password, result[0]):
            return {"status": "success", "message": "Acceso concedido"}
        else:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error en el servidor")

# 3. GUARDAR API KEYS (Faltaba en tu código)
@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET api_key = %s, api_secret = %s WHERE email = %s",
            (keys.api_key, keys.api_secret, keys.email)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Llaves vinculadas"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al guardar llaves")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
