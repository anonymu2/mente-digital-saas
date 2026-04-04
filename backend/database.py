import psycopg2
from psycopg2.extras import RealDictCursor
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
