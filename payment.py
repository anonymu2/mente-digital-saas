from fastapi import APIRouter

router = APIRouter()

@router.post("/verify-payment/{email}")
def verify(email: str):
    return {"status": "activated"}
