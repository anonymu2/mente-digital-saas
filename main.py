from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import auth
import user
import trading
import payment

app = FastAPI(title="Mente Digital API PRO")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(trading.router)
app.include_router(payment.router)

@app.get("/")
def root():
    return {"status": "Mente Digital API Online 🚀"}
