import math
import os
from pathlib import Path

from skyfield.api import load

# Anchor ephemeris file to repo root (C:/AI), regardless of cwd.
# backend/src/services/ephemeris.py → parents[3] = repo root.
_BSP_PATH = Path(__file__).resolve().parents[3] / "de421.bsp"

# Try multiple mirrors because NASA endpoints rotate/404 unexpectedly.
_BSP_URLS = [
    "https://ssd.jpl.nasa.gov/ftp/eph/planets/bsp/de421.bsp",
    "https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/de421.bsp",
]


def _ensure_bsp() -> Path:
    """Return path to de421.bsp, downloading it once if missing."""
    if _BSP_PATH.exists():
        return _BSP_PATH
    last_err = None
    for url in _BSP_URLS:
        try:
            print(f"[ephemeris] trying {url}")
            load(str(_BSP_PATH), url)
            if _BSP_PATH.exists():
                return _BSP_PATH
        except Exception as exc:
            last_err = exc
            print(f"[ephemeris] download failed from {url}: {exc}")
            try:
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                with urllib.request.urlopen(url, context=ctx, timeout=30) as src, open(_BSP_PATH, "wb") as dst:
                    dst.write(src.read())
                if _BSP_PATH.exists():
                    return _BSP_PATH
            except Exception as exc2:
                last_err = exc2
                print(f"[ephemeris] fallback download failed from {url}: {exc2}")
    raise FileNotFoundError(
        f"Ephemeris file not found and could not be downloaded from any mirror. "
        f"Last error: {last_err}"
    )


# Load via POSIX-style path so skyfield never treats a Windows absolute path
# like ``D:\AI\NEW-AI-REBORN\de421.bsp`` as a URL fragment.
_BSP_PATH_STR = _ensure_bsp().as_posix()

ts = load.timescale()
eph = load(_BSP_PATH_STR)
earth = eph["earth"]
OBLIQUITY = math.radians(23.4392911)
