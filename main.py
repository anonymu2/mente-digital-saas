from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import database  # <-- CAMBIO CLAVE: Importación directa sin el punto (.)

app = FastAPI(title="Mente Digital VIP API")

# Habilitar CORS para que el APK de Flutter conecte sin errores
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "Mente Digital API Online", "provider": "Render & Postgres"}

@app.get("/history/{email}")
async def get_history(email: str):
    """Consulta el historial de trades directamente desde PostgreSQL"""
    # Usamos el módulo database que importamos arriba
    conn = database.get_db_connection() 
    
    if not conn:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")
    
    try:
        cur = conn.cursor()
        # El CAST a FLOAT es vital para que Flutter reciba números y no Strings
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
        if conn:
            conn.close()
        raise HTTPException(status_code=500, detail=str(e))
