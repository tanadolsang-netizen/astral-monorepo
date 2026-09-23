from fastapi import APIRouter

router = APIRouter()


@router.get("/ready")
async def ready():
    return {"status": "ok", "version": "3.0.0"}
