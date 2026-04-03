from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="Mente Digital SaaS API")

# --- CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# Esto permite que tu App de Flutter se conecte sin bloqueos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de la base de datos (Ajustada para la estructura de carpetas de Kali)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.db")

# --- MODELOS DE DATOS ---
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
    conn.row_factory = sqlite3.Row  # Permite acceder a datos por nombre de columna
    return conn

# --- RUTAS / ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "online", "brand": "Mente Digital Pro"}

# 1. LOGIN (Retorna subscription_status para la App)
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
                "subscription_status": row["subscription_status"], # 'active' o 'inactive'
                "message": "Acceso concedido"
            }
        else:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    finally:
        db.close()

# 2. REGISTRO (Crea usuarios como 'inactive' por defecto)
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
        return {"message": "Usuario registrado correctamente"}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    finally:
        db.close()

# 3. VERIFICAR STATUS (Endpoint rápido para la App)
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

# 4. GUARDAR LLAVES DE BINANCE
@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(
            "UPDATE users SET api_key = ?, api_secret = ? WHERE email = ?",
            (keys.api_key, keys.api_secret, keys.email)
        )
        db.commit()
        return {"message": "Configuración de Binance guardada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

# --- INICIALIZACIÓN DE TABLA (Si no existe) ---
@app.on_event("startup")
def setup_database():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            subscription_status TEXT DEFAULT 'inactive',
            api_key TEXT,
            api_secret TEXT
        )
    """)
    db.commit()
    db.close()
