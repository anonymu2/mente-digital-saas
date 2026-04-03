from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_all_metadata, create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib
import time

# --- CONFIGURACIÓN DE BASE DE DATOS ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de Tabla para la Base de Datos
class TransactionDB(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    amount = Column(Float)
    txid = Column(String, unique=True)
    status = Column(String, default="completed")

# Crear las tablas automáticamente
Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- MODELOS PARA LA API ---
class TransactionCreate(BaseModel):
    user_id: str
    amount: float

# --- RUTAS ---
@app.post("/create-transaction")
def create_transaction(tx: TransactionCreate):
    db = SessionLocal()
    # Generar el TXID real
    new_txid = hashlib.sha256(f"{tx.user_id}{time.time()}".encode()).hexdigest()
    
    # Guardar en la base de datos
    db_tx = TransactionDB(user_id=tx.user_id, amount=tx.amount, txid=new_txid)
    db.add(db_tx)
    db.commit()
    db.refresh(db_tx)
    db.close()
    
    return {"message": "Guardado exitoso", "txid": new_txid}

@app.get("/history/{user_id}")
def get_history(user_id: str):
    db = SessionLocal()
    history = db.query(TransactionDB).filter(TransactionDB.user_id == user_id).all()
    db.close()
    return history

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
