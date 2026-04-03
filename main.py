from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

app = FastAPI(title="Mente Digital SaaS API")

# --- CONFIGURACIÓN DE CORS ---
# Esto es VITAL para que tu App de Flutter en Android/iOS pueda hablar con Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ruta de la base de datos (Estructura de carpetas en tu Kali)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.db")

# --- MODELOS DE DATOS (Pydantic) ---
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
    conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
    return conn

# --- RUTAS / ENDPOINTS ---

@app.get("/")
def health_check():
    return {
        "status": "online", 
        "brand": "Mente Digital Pro",
        "system": "Sistema Aeterna Trading"
    }

# 1. LOGIN: Devuelve el estatus VIP para que la App decida qué pantalla mostrar
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

# 2. REGISTRO: Crea usuarios nuevos con estatus 'inactive' por defecto
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
        raise HTTPException(status_code=400, detail="El correo ya existe en el sistema")
    finally:
        db.close()

# 3. VERIFICAR STATUS: Consulta rápida para refrescar la App
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

# 4. GUARDAR LLAVES BINANCE: Para el funcionamiento del bot
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
        return {"message": "Configuración de API Binance guardada exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
