import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- CONFIGURACIÓN DE BASE DE DATOS ---
# 1. Obtiene la URL de la variable de entorno que configuraste en Render
DATABASE_URL = os.environ.get("DATABASE_URL")

# 2. Si no hay variable (ej. en tu Kali local), usa SQLite para no romper el código
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test.db"
else:
    # IMPORTANTE: Render da 'postgres://', pero SQLAlchemy 2.0 requiere 'postgresql://'
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Crear el motor de la base de datos
# check_same_thread solo es necesario para SQLite
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELOS DE DATOS ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_vip = Column(Boolean, default=False)
    binance_api_key = Column(String, nullable=True)
    binance_api_secret = Column(String, nullable=True)

# Crear tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mente Digital SaaS - Pro Edition")

# --- ESQUEMAS ---
class UserEmail(BaseModel):
    email: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# --- ENDPOINTS ---
@app.get("/")
def home():
    return {
        "message": "Mente Digital SaaS is Live",
        "database": "PostgreSQL Connected" if "postgresql" in DATABASE_URL else "SQLite"
    }

@app.post("/confirm-payment")
async def confirm_payment(data: UserEmail):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            user = User(email=data.email, is_vip=True)
            db.add(user)
        else:
            user.is_vip = True
        db.commit()
        return {"status": "success", "message": "VIP activado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == keys.email).first()
        if not user or not user.is_vip:
            raise HTTPException(status_code=403, detail="No eres VIP")
        
        user.binance_api_key = keys.api_key
        user.binance_api_secret = keys.api_secret
        db.commit()
        return {"status": "success", "message": "API Keys guardadas"}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    # Render asigna el puerto automáticamente
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
