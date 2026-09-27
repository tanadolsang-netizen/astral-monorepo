import re
from pathlib import Path
from fastapi import APIRouter, HTTPException
import os

router = APIRouter()

_DEFAULT_BASE = Path(__file__).resolve().parents[2] / 'raw' / 'astrology'
BASE = Path(os.getenv('ASTRO_RAW_DIR') or _DEFAULT_BASE).resolve()

# Slugs come from filenames we generated ourselves (see list_branches), so a
# strict allowlist is both correct and closes off path traversal (e.g.
# "../../etc/passwd") through the {slug} path param below.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


@router.get("/list")
async def list_branches():
    branches = []
    for p in sorted(BASE.glob("*.md")):
        branches.append({"slug": p.stem, "path": p.relative_to(BASE.parent.parent).as_posix()})
    return {"branches": branches}


@router.get("/{slug}")
async def get_branch(slug: str):
    if not _SLUG_RE.match(slug):
        raise HTTPException(status_code=404, detail="not found")
    path = BASE / f"{slug}.md"
    if not path.exists():
        raise HTTPException(status_code=404, detail="not found")
    return {"slug": slug, "content": path.read_text(encoding="utf-8")}
