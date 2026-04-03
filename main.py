import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Configuración de la Base de Datos (SQLite para el plan Free de Render)
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Modelo de Base de Datos
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_vip = Column(Boolean, default=False)
    binance_api_key = Column(String, nullable=True)
    binance_api_secret = Column(String, nullable=True)

# 3. Creación de tablas (ESTA ES LA LÍNEA QUE REEMPLAZA EL ERROR ANTERIOR)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mente Digital SaaS API")

# 4. Esquemas de Pydantic para validación de datos
class UserEmail(BaseModel):
    email: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# 5. Endpoints
@app.get("/")
def home():
    return {"message": "Mente Digital SaaS is Live", "status": "Aeterna Bot Online"}

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
    finally:
        db.close()

# 6. Ejecución (Adaptado para el puerto dinámico de Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
