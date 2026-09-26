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

# J2000 mean obliquity — kept only for callers that need the fixed reference
# value. House cusps and the ascendant MUST use mean_obliquity(dt) instead.
OBLIQUITY = math.radians(23.4392911)


def mean_obliquity(dt_utc=None, jd_tt: float | None = None) -> float:
    """Mean obliquity of the ecliptic **of date**, in radians.

    The obliquity is not constant: it was 23.45098 deg in 1901 and is
    23.43582 deg in 2026. Using the J2000 constant for a 1901 chart is out by
    0.0117 deg, which is enough to move a cusp near a sign boundary.

    Laskar 1986, valid to well beyond the 1900-2100 range DE421 covers.
    """
    if jd_tt is None:
        jd_tt = ts.from_datetime(dt_utc).tt
    t = (jd_tt - 2451545.0) / 36525.0
    sec = 21.448 - t * (46.8150 + t * (0.00059 - t * 0.001813))
    return math.radians(23.0 + (26.0 + sec / 60.0) / 60.0)


def ecliptic_longitude(body, dt_utc) -> float:
    """Apparent geocentric ecliptic longitude **of date**, degrees 0-360.

    Skyfield's ``ecliptic_latlon()`` defaults to the J2000 equinox, which is
    wrong for astrology: the tropical zodiac is referred to the equinox of
    date. Getting this wrong displaces every body by the general precession
    (0.01397 deg/yr) — 0.04 deg for a 1997 birth, but 1.37 deg for 1901.
    """
    t = ts.from_datetime(dt_utc)
    lat, lon, _ = earth.at(t).observe(body).apparent().ecliptic_latlon(epoch=t)
    return lon.degrees % 360
