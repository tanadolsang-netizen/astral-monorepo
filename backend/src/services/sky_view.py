"""Sky view — bright star catalog + live planet positions for planetarium.

Returns alt/az for a given time+location so the frontend canvas can render
a real sky (Stellarium/SkySafari style). Stars: I/311/hip2 astrometry
(86 bright stars, RA/Dec/mag with proper motion) bundled offline via
`services/star_catalogue.py`. Planets via existing ephemeris.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

from src.services.chart_service import compute_chart
from src.services.ephemeris import ts, earth, eph
from src.services.star_catalogue import BRIGHT_STARS

# ── Bright star catalog (RA hours, Dec deg, magnitude, name th/en) ──
# Built from src/services/star_catalogue.py, which holds I/311/hip2 astrometry
# (van Leeuwen 2007) with full-precision proper motion.  This table used to be a
# hand-entered copy of the Yale Bright Star Catalogue; 71 of its 82
# Hipparcos-checkable rows pointed at the wrong star, because the names and the
# coordinates had fallen out of alignment.  Measured by
# scripts/report_star_table_divergence.py.  Never hand-edit star positions here:
# regenerate the catalogue with scripts/fetch_bright_star_catalogue.py.
STARS: list[tuple[float, float, float, str, str]] = [
    (row["ra_h"], row["dec_deg"], row["mag"], name, row["th"])
    for name, row in sorted(
        # Only Hipparcos-verified rows are drawable.  A handful of companion
        # stars and one nebula have no single SIMBAD object, so their
        # coordinates and magnitudes are inherited from the app's old hand-
        # entered table and are demonstrably wrong (Aldebaran B is 1.66 mag in
        # that table; the real B component is ~13).  Drawing a wrong bright
        # dot is worse than drawing nothing, so they are held back.
        ((n, r) for n, r in BRIGHT_STARS.items() if r.get("precision") == "hip2_full"),
        key=lambda kv: kv[1]["ra_h"],
    )
]


def _alt_az(ra_deg: float, dec_deg: float, lat: float,
            lon_deg: float, utc_dt: datetime) -> tuple[float, float]:
    """Approximate alt/az from LST. Good to ~0.3° — plenty for canvas sky."""
    j2000 = datetime(2000, 1, 1, 12)
    d = (utc_dt.replace(tzinfo=None) - j2000).total_seconds() / 86400
    gmst = (280.46061837 + 360.98564736629 * d) % 360
    lst = (gmst + lon_deg) % 360

    ha = math.radians((lst - ra_deg + 360) % 360)
    dec = math.radians(dec_deg)
    phi = math.radians(lat)

    sin_alt = math.sin(dec) * math.sin(phi) + \
        math.cos(dec) * math.cos(phi) * math.cos(ha)
    alt = math.degrees(math.asin(max(-1, min(1, sin_alt))))

    y = -math.sin(ha) * math.cos(dec)
    x = math.sin(dec) * math.cos(phi) - math.cos(dec) * math.sin(phi) * math.cos(ha)
    az = math.degrees(math.atan2(y, x)) % 360
    return round(alt, 2), round(az, 2)


def _ra_dec_from_ecliptic(lon_ecl: float, lat_ecl: float = 0.0) -> tuple[float, float]:
    lam = math.radians(lon_ecl)
    beta = math.radians(lat_ecl)
    eps = math.radians(23.4367)
    ra = math.atan2(
        math.sin(lam) * math.cos(eps) - math.tan(beta) * math.sin(eps),
        math.cos(lam))
    dec = math.asin(math.sin(beta) * math.cos(eps) +
                    math.cos(beta) * math.sin(eps) * math.sin(lam))
    return math.degrees(ra) % 360, math.degrees(dec)


_PLANET_TH = {"Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
              "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสฯ",
              "Saturn": "ดาวเสาร์"}


def sky_view(date_iso: str, time_hhmm: str, tz_offset_hours: float,
             lat: float, lon_deg: float,
             include_stars: bool = True,
             mag_limit: float = 2.5) -> dict:
    naive = datetime.fromisoformat(f"{date_iso}T{time_hhmm}:00")
    utc = naive - timedelta(hours=tz_offset_hours)

    planets_out = []
    chart = compute_chart("sky", utc.date(), utc.time(), tz_offset_hours=0,
                          lat=lat, lon=lon_deg)
    for b in chart["bodies"]:
        ecl_lon = float(b["absolute_deg"])
        ra, dec = _ra_dec_from_ecliptic(ecl_lon)
        alt, az = _alt_az(ra, dec, lat, lon_deg, utc)
        if alt > -5:
            planets_out.append({
                "type": "planet", "name": b["body"],
                "name_th": _PLANET_TH.get(b["body"], b["body"]),
                "alt": alt, "az": az,
                "ecl_lon": round(ecl_lon, 3),
                "sign": b.get("sign", ""),
            })

    stars_out = []
    if include_stars:
        for ra_h, dec, mag, en, th in STARS:
            if mag > mag_limit:
                continue
            ra_deg = ra_h * 15
            alt, az = _alt_az(ra_deg, dec, lat, lon_deg, utc)
            if alt > 0:
                stars_out.append({
                    "type": "star", "name": en, "name_th": th,
                    "mag": mag, "alt": alt, "az": az,
                    "size_px": round(max(1.5, 7 - mag), 1),
                })
        stars_out.sort(key=lambda s: s["mag"])

    sun_above = any(p["name"] == "Sun" and p["alt"] > -0.5
                    for p in planets_out)

    return {
        "system": "sky-view",
        "time_utc": utc.isoformat(),
        "local_time": naive.isoformat(),
        "location": {"lat": lat, "lon": lon_deg},
        "daylight": sun_above,
        "planets": planets_out,
        "stars": stars_out,
        "star_count": len(stars_out),
        "interpretation": {
            "th": f"ท้องฟ้า {naive.strftime('%d/%m/%Y %H:%M')} — "
                  f"ดาวเคราะห์ {len(planets_out)} ดวง ดาวฤกษ์ "
                  f"{len(stars_out)} ดวงเหนือขอบฟ้า"
                  + (" (กลางวัน)" if sun_above else " (กลางคืน)"),
            "en": (f"Sky at {naive.strftime('%Y-%m-%d %H:%M')}: "
                   f"{len(planets_out)} planets, {len(stars_out)} stars above "
                   f"horizon."),
        },
    }
