import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Render inyecta DATABASE_URL automáticamente si conectas el servicio de DB al Web Service
# Si no, usará la URL que pegaste como respaldo.
DB_URL = os.getenv("DATABASE_URL", "postgresql://mente_digital_db_user:pZxzCrtBwn5ec3XANj4bfwkJL9Rvy7NZ@dpg-d77qjb95pdvs73976ga0-a.oregon-postgres.render.com/mente_digital_db")

def get_db_connection():
    """Retorna una conexión lista para usar con formato de Diccionario"""
    try:
        # Forzamos sslmode=require porque Render (y la mayoría de nubes) lo exige
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor, sslmode='require')
        return conn
    except Exception as e:
        print(f"❌ Error conectando a Postgres: {e}")
        return None
