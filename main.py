from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from datetime import datetime

app = FastAPI(title="Mente Digital API")

# --- CONFIGURACIÓN ---
# Usamos tu URL de Render (Lo ideal es usar variables de entorno)
DB_URL = "postgresql://mente_digital_db_user:pZxzCrtBwn5ec3XANj4bfwkJL9Rvy7NZ@dpg-d77qjb95pdvs73976ga0-a.oregon-postgres.render.com/mente_digital_db"

# Habilitar CORS para que tu App de Flutter pueda consultar la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Función auxiliar para serializar fechas (Postgres -> JSON)
def date_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)

@app.get("/")
def read_root():
    return {"status": "Mente Digital API Online"}

@app.get("/history/{email}")
def get_history(email: str):
    """Obtiene los últimos 20 trades de un usuario desde PostgreSQL"""
    conn = None
    try:
        # Conexión a la base de datos
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query optimizada
        query = """
            SELECT 
                symbol, 
                side, 
                CAST(amount_usdt AS FLOAT) as amount_usdt, 
                CAST(price_entry AS FLOAT) as price_entry, 
                status,
                created_at 
            FROM trade_history 
            WHERE user_email = %s 
            ORDER BY created_at DESC 
            LIMIT 20
        """
        
        cur.execute(query, (email,))
        data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        # Retornamos los datos (FastAPI se encarga de convertirlos a JSON)
        return data

    except Exception as e:
        if conn:
            conn.close()
        print(f"❌ Error en /history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Para correr localmente en Kali: python3 main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
