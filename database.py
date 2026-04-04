# database.py
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db():
    conn = psycopg2.connect(
        host="localhost",
        database="mente_digital",
        user="tu_usuario",
        password="tu_password",
        cursor_factory=RealDictCursor
    )
    return conn
