from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from src.integrations.supabase_client import User, get_current_user
from src.services import chart_store
from src.services.caveat import CAVEAT

router = APIRouter()


async def _require_user(authorization: str = Header(default="")) -> User:
    try:
        return await get_current_user(authorization)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=401, detail="Unauthorized") from exc


class RecentIn(BaseModel):
    limit: int = Field(default=5, ge=0, le=50)


class RecentItem(BaseModel):
    id: str | None = None
    name: str
    date: str | None = None
    time: str | None = None
    system: str
    created_at: str | None = None


class RecentOut(BaseModel):
    recent: list[RecentItem]
    caveat: str


@router.post("/recent", response_model=RecentOut)
async def recent(payload: RecentIn, user: User = Depends(_require_user)) -> RecentOut:
    try:
        rows = chart_store.list_recent(user.id, payload.limit)
    except RuntimeError as exc:
        # Supabase unconfigured (local dev): surface it rather than serving
        # fabricated rows that look like real history.
        raise HTTPException(status_code=503, detail="Chart storage unavailable") from exc
    return RecentOut(recent=[RecentItem(**row) for row in rows], caveat=CAVEAT)
