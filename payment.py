from fastapi import APIRouter
from database import get_db
from models.schemas import Payment

router = APIRouter()

@router.post("/verify-payment/{email}")
def verify_payment(email: str, data: Payment):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users 
        SET is_vip=TRUE, payment_txid=%s
        WHERE email=%s
    """, (data.txid, email))

    conn.commit()

    return {"status": "activated"}
