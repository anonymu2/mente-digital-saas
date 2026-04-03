import os
import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import uvicorn

app = FastAPI(title="Mente Digital SaaS - Secure API")

# CONFIGURACIÓN DE RED (CORS)
# Permite que tu APK conecte desde cualquier lugar (Datos móviles o WiFi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# CONEXIÓN A BASE DE DATOS
# En el panel de Render, añade la variable: DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        raise Exception("Error: DATABASE_URL no configurada en Render")
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(url)

# MODELOS DE DATOS
class User(BaseModel):
    email: str
    password: str

# RUTAS PRINCIPALES
@app.get("/")
def home():
    return {"status": "Mente Digital Gateway Live", "secure": True}

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
        return {"status": "success", "message": "Registro completado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error en el servidor seguro")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
