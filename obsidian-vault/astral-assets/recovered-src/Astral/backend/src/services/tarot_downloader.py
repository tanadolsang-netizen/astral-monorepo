"""Optional tarot deck downloader.

Downloads Rider-Waite public-domain cards on demand if they are not
already present locally. Never blocks PDF generation: if the network
or the source is unavailable, callers get None and the renderer falls
back to the text placeholder automatically.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Optional

from src.services.tarot_images import DECK_DIR, CARD_INDEX

# Sources in preference order.
# Priority 1: direct image URLs with numbered filenames 00.jpg .. 77.jpg
_IMAGE_BASES = [
    # Archive.org 4K PNG set: cards-4K/{nn}.png
    {
        "base_url": "https://archive.org/download/rider-waite-tarot/4K/cards-4K",
        "ext": "png",
        "prefix": "",
        "width": None,
    },
    # Wikimedia thumbnails: /{width}px-Rider-Waite_XX_Name.jpg
    {
        "base_url": "https://upload.wikimedia.org/wikipedia/commons/thumb",
        "ext": "jpg",
        "prefix": "",
        "width": 600,
    },
]

_STATE_LOCK = threading.Lock()
_STATE = {"ready": False, "have": 0, "total": 78, "error": None}


def _count_local() -> int:
    if not DECK_DIR.exists():
        return 0
    return sum(1 for i in range(78) if (DECK_DIR / f"{i:02d}.jpg").exists())


def _download_image(url: str, dest: Path, timeout: int = 20) -> bool:
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=timeout).read()
        if len(data) > 5000:
            dest.write_bytes(data)
            return True
    except Exception:
        pass
    if dest.exists():
        dest.unlink(missing_ok=True)
    return False


def _try_archive_org() -> bool:
    """Try Archive.org direct PNG URLs: cards-4K/{nn}.png"""
    ok = 0
    for i in range(78):
        dest = DECK_DIR / f"{i:02d}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            ok += 1
            continue
        url = f"https://archive.org/download/rider-waite-tarot/4K/cards-4K/{i:02d}.png"
        if _download_image(url, dest):
            ok += 1
    return ok >= 10


def _try_wikimedia() -> bool:
    """Try Wikimedia Commons thumbnails for the 22 majors only."""
    # Only majors for now; minors can be added later.
    MAJORS = [
        "The_Fool", "The_Magician", "The_High_Priestess", "The_Empress",
        "The_Emperor", "The_Hierophant", "The_Lovers", "The_Chariot",
        "Strength", "The_Hermit", "Wheel_of_Fortune", "Justice",
        "The_Hanged_Man", "Death", "Temperance", "The_Devil",
        "The_Tower", "The_Star", "The_Moon", "The_Sun",
        "Judgement", "The_World",
    ]
    ok = 0
    for i, name in enumerate(MAJORS):
        dest = DECK_DIR / f"{i:02d}.jpg"
        if dest.exists() and dest.stat().st_size > 5000:
            ok += 1
            continue
        url = (
            f"https://upload.wikimedia.org/wikipedia/commons/thumb/"
            f"9/93/Rider-Waite_{name}.jpg/600px-Rider-Waite_{name}.jpg"
        )
        if _download_image(url, dest):
            ok += 1
    return ok >= 5


def _background_download() -> None:
    """Download in background; never raise."""
    try:
        DECK_DIR.mkdir(parents=True, exist_ok=True)
        if _try_archive_org():
            return
        if _try_wikimedia():
            return
    except Exception as exc:
        with _STATE_LOCK:
            _STATE["error"] = str(exc)


def ensure_deck_ready(background: bool = True) -> dict:
    """Make sure the deck is available locally.

    Returns a status dict: {ready, have, total, error}
    """
    with _STATE_LOCK:
        if _STATE["ready"]:
            return dict(_STATE)

        have = _count_local()
        _STATE["have"] = have
        _STATE["total"] = 78
        _STATE["ready"] = have >= 10

        if have < 10 and background:
            t = threading.Thread(target=_background_download, daemon=True)
            t.start()

        return dict(_STATE)


def get_card_path(card_name: str) -> Optional[Path]:
    """Return local image path for a card, or None if unavailable."""
    idx = CARD_INDEX.get(card_name)
    if idx is None:
        return None
    p = DECK_DIR / f"{idx:02d}.jpg"
    if p.exists() and p.stat().st_size > 5000:
        return p
    return None
