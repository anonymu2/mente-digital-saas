import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import uvicorn

# Inicializamos FastAPI
app = FastAPI(title="Mente Digital SaaS API")

# --- CONFIGURACIÓN DE SEGURIDAD (CORS) ---
# Esto permite que tu APK de Flutter se conecte desde cualquier parte del mundo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración para encriptar contraseñas de usuarios
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- CONEXIÓN A BASE DE DATOS (SEGURIDAD MÁXIMA) ---
# No ponemos la URL aquí. La leerá de Render automáticamente.
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise Exception("ERROR: La variable DATABASE_URL no está configurada en Render.")
    
    # Render usa 'postgres://', pero SQLAlchemy/Psycopg2 necesitan 'postgresql://'
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

# --- RUTAS / ENDPOINTS ---

@app.get("/")
def home():
    return {
        "status": "Mente Digital Gateway Online",
        "database": "Connected",
        "security": "Environment Variables Active"
    }

@app.post("/register")
async def register(user: User):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Encriptamos la contraseña antes de guardarla
        hashed_pw = pwd_context.hash(user.password)
        
        # Insertar o ignorar si ya existe
        cur.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s) ON CONFLICT (email) DO NOTHING",
            (user.email, hashed_pw)
        )
        
        conn.commit()
        cur.close()
        conn.close()
        return {"status": "success", "message": "Usuario gestionado correctamente"}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

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
        return {"status": "success", "message": "API Keys vinculadas correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error al vincular llaves")

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    # Render asigna el puerto automáticamente
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
