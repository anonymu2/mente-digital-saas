from fastapi import APIRouter

router = APIRouter()

@router.post("/save-keys/{email}")
def save_keys(email: str):
    return {"status": "ok"}

@router.get("/profit/{email}")
def profit(email: str):
    return {"profit": 0}

@router.get("/history/{email}")
def history(email: str):
    return []
