from fastapi import APIRouter, Depends, Header, HTTPException, Query

from src.integrations.supabase_client import User, get_current_user
from src.models.memory import (
    MemoryAppendRequest,
    MemoryEntry,
    MemorySummary,
    MemoryTarget,
)
from src.services import hermes_memory_service as memory_service

router = APIRouter()


async def _require_user(authorization: str = Header(default="")) -> User:
    try:
        return await get_current_user(authorization)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=401, detail="Unauthorized") from exc


@router.get("/summary", response_model=MemorySummary)
async def get_summary(_: User = Depends(_require_user)):
    return memory_service.read_summary()


@router.get("/entries", response_model=list[MemoryEntry])
async def list_entries(
    target: MemoryTarget = Query(...),
    _: User = Depends(_require_user),
):
    return memory_service.read_entries(target)


@router.post("/entries", response_model=MemoryEntry)
async def add_entry(body: MemoryAppendRequest, _: User = Depends(_require_user)):
    try:
        return memory_service.append_entry(body.target, body.content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/sessions")
async def search_sessions(
    query: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
    _: User = Depends(_require_user),
):
    return {"results": memory_service.search_sessions(query, limit)}
