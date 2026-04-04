from fastapi import APIRouter
from utils.security import decode_token
from database import get_db

router = APIRouter()

TRON_WALLET = "20TRocsW1mR2JbHq1S7Nf4E9z8K6vP5L9XyQ"

@router.post("/activate-vip")
def activate_vip(token: str):
    """
    Marca al usuario como VIP después de recibir pago en TRC20 (Binance).
    Por ahora, la activación es manual: verificas el pago y luego llamas este endpoint.
    """
    conn = get_db()
    cur = conn.cursor()
    user_data = decode_token(token)
    if not user_data:
        return {"error": "Token inválido"}

    cur.execute("UPDATE users SET is_vip = TRUE WHERE email=%s", (user_data["email"],))
    conn.commit()
    cur.close()

    return {
        "message": f"Usuario activado como VIP. Asegúrate de recibir $50 en TRC20 en Binance: {TRON_WALLET}"
    }
