"""Research corpus endpoints: serve ingested JSON test vectors / reference data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.integrations.local_db import _connect

router = APIRouter(tags=["research"])


class CorpusItem(BaseModel):
    id: str
    category: str
    name: str


class CorpusDetail(CorpusItem):
    data: Any


@router.get("/corpus", response_model=list[CorpusItem])
def list_corpus() -> list[dict[str, str]]:
    con = _connect()
    rows = con.execute("SELECT id, category, name FROM research_corpus ORDER BY category, name").fetchall()
    con.close()
    return [dict(r) for r in rows]


@router.get("/corpus/{item_id}", response_model=CorpusDetail)
def get_corpus(item_id: str) -> dict[str, Any]:
    con = _connect()
    row = con.execute("SELECT id, category, name, data FROM research_corpus WHERE id = ?", (item_id,)).fetchone()
    con.close()
    if not row:
        raise HTTPException(status_code=404, detail="corpus item not found")
    return {"id": row["id"], "category": row["category"], "name": row["name"], "data": json.loads(row["data"])}


@router.get("/categories")
def list_categories() -> dict[str, int]:
    con = _connect()
    rows = con.execute("SELECT category, count(*) as n FROM research_corpus GROUP BY category ORDER BY category").fetchall()
    con.close()
    return {r["category"]: r["n"] for r in rows}
