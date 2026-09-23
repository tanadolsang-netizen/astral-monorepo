from typing import Literal, Optional

from pydantic import BaseModel

MemoryTarget = Literal["memory", "user"]


class MemoryEntry(BaseModel):
    index: int
    content: str


class MemorySummary(BaseModel):
    memory_bytes: int
    memory_entries: int
    user_bytes: int
    user_entries: int


class MemoryAppendRequest(BaseModel):
    target: MemoryTarget
    content: str


class SessionMessage(BaseModel):
    id: int
    session_id: str
    role: str
    content: Optional[str] = None
    timestamp: Optional[float] = None
