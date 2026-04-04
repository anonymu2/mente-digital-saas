from fastapi import APIRouter

router = APIRouter()

@router.get("/user-status/{email}")
def status(email: str):
    return {"status": "inactive"}
