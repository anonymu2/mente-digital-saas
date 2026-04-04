import psycopg2
from psycopg2.extras import RealDictCursor
import os

DB_URL = os.environ.get("DATABASE_URL")  # variable de entorno

def get_db():
    conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
    return conn
