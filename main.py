from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import uvicorn

app = FastAPI(title="Mente Digital Pro API")

# --- CONFIGURACIÓN DE CORS ---
# Vital para que el APK de Flutter no sea bloqueado
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de base de datos
# Usamos una ruta absoluta basada en la ubicación de este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "database.db")

# --- MODELOS ---
class UserAuth(BaseModel):
    email: str
    password: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# --- UTILIDADES ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- RUTAS ---

@app.get("/")
def home():
    return {"status": "Mente Digital Server Online", "version": "1.0.0"}

@app.post("/login")
async def login(user: UserAuth):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT email, subscription_status FROM users WHERE email = ? AND password = ?",
            (user.email, user.password)
        )
        row = cursor.fetchone()
        if row:
            return {
                "email": row["email"],
                "subscription_status": row["subscription_status"],
                "message": "Login exitoso"
            }
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    finally:
        db.close()

@app.post("/register")
async def register(user: UserAuth):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password, subscription_status) VALUES (?, ?, ?)",
            (user.email, user.password, "inactive")
        )
        db.commit()
        return {"message": "Usuario registrado"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    finally:
        db.close()

@app.get("/user-status/{email}")
async def get_status(email: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT subscription_status FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    db.close()
    if row:
        return {"status": row["subscription_status"]}
    return {"status": "inactive"}

# --- INICIO DEL SERVIDOR (CRÍTICO PARA RENDER) ---
if __name__ == "__main__":
    # Render asigna el puerto mediante la variable de entorno PORT
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
