from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 1. CONFIGURACIÓN DE BASE DE DATOS
# Render usa un sistema de archivos efímero en el plan gratuito, 
# pero para empezar, database.db funcionará.
DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. MODELO DE USUARIO (Para tu SaaS de Trading)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    is_vip = Column(Boolean, default=False)
    binance_api_key = Column(String, nullable=True)
    binance_api_secret = Column(String, nullable=True)

# 3. CREAR TABLAS (Esto reemplaza el error de 'create_all_metadata')
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mente Digital SaaS API")

# 4. ESQUEMAS DE DATOS (Pydantic)
class PaymentRequest(BaseModel):
    email: str

class BinanceKeys(BaseModel):
    email: str
    api_key: str
    api_secret: str

# 5. ENDPOINTS PARA TU APP FLUTTER

@app.get("/")
def health_check():
    return {"status": "Aeterna Bot Online", "environment": "Production"}

@app.post("/confirm-payment")
async def confirm_payment(request: PaymentRequest):
    db = SessionLocal()
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Si el usuario no existe, lo creamos como VIP
        user = User(email=request.email, is_vip=True)
        db.add(user)
    else:
        user.is_vip = True
    
    db.commit()
    db.close()
    return {"status": "success", "message": "Pago verificado, cuenta VIP activa"}

@app.post("/save-keys")
async def save_keys(keys: BinanceKeys):
    db = SessionLocal()
    user = db.query(User).filter(User.email == keys.email).first()
    
    if not user or not user.is_vip:
        db.close()
        raise HTTPException(status_code=403, detail="Debes ser VIP para configurar el bot")
    
    user.binance_api_key = keys.api_key
    user.binance_api_secret = keys.api_secret
    
    db.commit()
    db.close()
    return {"status": "success", "message": "Llaves de Binance vinculadas correctamente"}

# 6. ARRANQUE (Importante para Render)
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
