import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. CONFIGURACIÓN DINÁMICA DE BASE DE DATOS
# Intenta leer la variable de Render; si no existe (local), usa SQLite
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./database.db")

# Corrección de formato necesaria para SQLAlchemy 2.0+ y Render
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configuración del motor según el tipo de base de datos
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. MODELO DE BASE DE DATOS (Persistencia de Usuarios)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_vip = Column(Boolean, default=False)
    binance_api_key = Column(String, nullable=True)
    binance_api_secret = Column(String, nullable=True)

# Crear las tablas en la base de datos (Postgres o SQLite)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mente Digital SaaS - API")

# 3. ESQUEMAS DE VALIDACIÓN (Pydantic)
class UserEmail(BaseModel):
    email: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# 4. ENDPOINTS
@app.get("/")
def home():
    # Este mensaje te confirmará si detectó Postgres o sigue en SQLite
    db_type = "PostgreSQL" if "postgresql" in DATABASE_URL else "SQLite (Local)"
    return {
        "message": "Mente Digital SaaS is Live",
        "database_connected": db_type,
        "status": "Aeterna Bot Online"
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
        return {"status": "success", "message": "VIP activado correctamente"}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == keys.email).first()
        if not user or not user.is_vip:
            raise HTTPException(status_code=403, detail="Usuario no encontrado o no es VIP")
        
        user.binance_api_key = keys.api_key
        user.binance_api_secret = keys.api_secret
        db.commit()
        return {"status": "success", "message": "Llaves de Binance guardadas"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

# 5. ARRANQUE (Configuración para Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
