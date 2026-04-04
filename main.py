# main.py
from fastapi import FastAPI
from routes import dashboard  # Importamos nuestro dashboard

app = FastAPI(title="Mente Digital API PRO")

app.include_router(dashboard.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "API Mente Digital VIP Online"}
