from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uvicorn

app = FastAPI(title="Mente Digital Pro API - PostgreSQL")

# --- CONFIGURACIÓN DE CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONEXIÓN A POSTGRESQL ---
# Render proporciona la URL en la variable de entorno DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    try:
        # Esto conecta directamente usando la URL de Render
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None

# --- MODELOS ---
class UserAuth(BaseModel):
    email: str
    password: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# --- RUTAS ---

@app.get("/")
def home():
    return {"status": "Mente Digital Server Online", "database": "PostgreSQL Active"}

@app.post("/login")
async def login(user: UserAuth):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT email, subscription_status FROM users WHERE email = %s AND password = %s",
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
        cursor.close()
        conn.close()

@app.post("/register")
async def register(user: UserAuth):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Error de base de datos")
    
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password, subscription_status) VALUES (%s, %s, %s)",
            (user.email, user.password, "inactive")
        )
        conn.commit()
        return {"message": "Usuario registrado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="El usuario ya existe o error en datos")
    finally:
        cursor.close()
        conn.close()

@app.get("/user-status/{email}")
async def get_status(email: str):
    conn = get_db_connection()
    if not conn:
        return {"status": "inactive"}
    
    cursor = conn.cursor()
    cursor.execute("SELECT subscription_status FROM users WHERE email = %s", (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if row:
        return {"status": row["subscription_status"]}
    return {"status": "inactive"}

# --- INICIO DEL SERVIDOR ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
