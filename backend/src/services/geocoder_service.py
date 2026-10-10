"""
Geocoder service — เปลี่ยน "อำเภอ + จังหวัด" เป็น lat/lon + tz.

Uses OpenStreetMap Nominatim via geopy. Thai-language queries sometimes
return nothing (reduced forms in Thai are sparse in OSM), so the service
falls back through progressively simpler queries:

  Phase 1: 'อำเภอ X จังหวัด Y'       (full explicit form)
  Phase 2: 'X Y'                      (reduced Thai form)
  Phase 3: 'X, Y, Thailand'           (reduced + country)
  Phase 4: 'X Y Thailand' (English)   (English fallback — Thailand
                                       cities almost always match in EN)

The first phase that returns a hit within Thailand bounds wins. The
returned lat/lon is the administrative centroid — good enough for
house cusp calculation (a few km of error shifts Ascendant by < 0.1°
at the equator, and birth-time imprecision swamps this anyway).

Timezone: Thailand uses UTC+7 uniformly with no DST. For other
countries in a future expansion, use the `timezonefinder` package.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from functools import lru_cache

from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim

logger = logging.getLogger("astral.geocoder")

# Thailand bounding box (approx). Anything outside this is discarded so a
# foreign country's hit can't be returned as a Thai birthplace.
_THAI_BOUNDS = {"lat": (5.5, 20.5), "lon": (97.3, 105.7)}

# Cache results in-process for 1 day — geocoding is pure (given a query,
# the answer never changes) and the OSM free API rate-limits at 1 req/s.
_CACHE_TTL_SECONDS = 86_400
_cache: dict[str, tuple[float, "GeoResult | None"]] = {}


@dataclass
class GeoResult:
    """A geocoding hit."""
    lat: float
    lon: float
    display_name: str
    tz_offset_hours: float = 7.0  # Thailand default; expand later
    provider: str = "nominatim"


def _in_thailand(lat: float, lon: float) -> bool:
    return (
        _THAI_BOUNDS["lat"][0] <= lat <= _THAI_BOUNDS["lat"][1]
        and _THAI_BOUNDS["lon"][0] <= lon <= _THAI_BOUNDS["lon"][1]
    )


def _normalize_query(district: str, province: str) -> str:
    district = district.strip().replace("อำเภอ", "").replace("อ.", "").strip()
    province = province.strip().replace("จังหวัด", "").replace("จ.", "").strip()
    return f"{district} {province}"


def _fallback_queries(district: str, province: str) -> list[str]:
    """Progressive fallback queries (most explicit first)."""
    d = district.strip().replace("อำเภอ", "").replace("อ.", "").strip()
    p = province.strip().replace("จังหวัด", "").replace("จ.", "").strip()
    return [
        f"อำเภอ{d} จังหวัด{p}",
        f"{d} {p}",
        f"{d}, {p}, Thailand",
        f"{d} {p} Thailand",
    ]


def geocode(district: str, province: str, country: str = "Thailand") -> GeoResult | None:
    """Geocode 'อำเภอบ้านฉาง ชลบุรี' style queries.

    Returns GeoResult on hit, None if all fallbacks miss.
    """
    normalized = _normalize_query(district, province)

    # Cache check
    cached = _cache.get(normalized)
    if cached and (time.time() - cached[0]) < _CACHE_TTL_SECONDS:
        return cached[1]

    result = _geocode_fallback(district, province, country)
    _cache[normalized] = (time.time(), result)
    return result


def _geocode_fallback(district: str, province: str, country: str) -> GeoResult | None:
    geocoder = Nominatim(
        user_agent="astral-astrology/1.0 (contact: astral-app)",
        timeout=10,
    )
    for query in _fallback_queries(district, province):
        try:
            location = geocoder.geocode(query, language="th", addressdetails=True)
        except (GeocoderTimedOut, GeocoderUnavailable) as exc:
            logger.warning("geocode timeout for %r: %s", query, exc)
            continue
        except Exception as exc:  # noqa: BLE001
            logger.warning("geocode error for %r: %s", query, exc)
            continue

        if not location:
            continue

        lat, lon = location.latitude, location.longitude
        if not _in_thailand(lat, lon):
            logger.debug("geocode hit for %r outside Thailand: %s,%s", query, lat, lon)
            continue

        return GeoResult(
            lat=round(lat, 4),
            lon=round(lon, 4),
            display_name=location.address or query,
            tz_offset_hours=7.0,
        )

    logger.info("geocode miss after all fallbacks for district=%r province=%r", district, province)
    return None


def geocode_latlon(lat: float, lon: float) -> str | None:
    """Reverse geocode — for showing 'อำเภอบ้านฉาง, ชลบุรี' from coords."""
    geocoder = Nominatim(
        user_agent="astral-astrology/1.0 (contact: astral-app)",
        timeout=10,
    )
    try:
        location = geocoder.reverse((lat, lon), language="th", addressdetails=True)
        if location:
            addr = location.raw.get("address", {})
            parts = [
                addr.get("district") or addr.get("county") or "",
                addr.get("province") or addr.get("state") or "",
            ]
            return ", ".join(p for p in parts if p) or location.address
    except Exception as exc:  # noqa: BLE001
        logger.warning("reverse geocode failed: %s", exc)
    return None


def cache_stats() -> dict[str, int]:
    """Ops endpoint helper."""
    now = time.time()
    alive = sum(1 for ts, _ in _cache.values() if now - ts < _CACHE_TTL_SECONDS)
    return {"cached_queries": alive, "total_seen": len(_cache)}
