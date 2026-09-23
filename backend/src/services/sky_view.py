"""Sky view — bright star catalog + live planet positions for planetarium.

Returns alt/az for a given time+location so the frontend canvas can render
a real sky (Stellarium/SkySafari style). Stars: Yale BSC bright subset
(~120 stars, RA/Dec/mag) bundled offline. Planets via existing ephemeris.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta

from src.services.chart_service import compute_chart
from src.services.ephemeris import ts, earth, eph

# ── Bright star catalog (RA hours, Dec deg, magnitude, name th/en) ──
STARS = [
    # (ra_h, dec, mag, en, th)
    (0.086, 29.09, 2.06, "Alpheratz", "อัลเฟอรัตส์"),
    (0.675, -17.99, 2.42, "Caph", "คาฟ"),
    (1.257, 60.24, 2.37, "Cassiopeia α", "แคสซิโอเปีย α"),
    (1.435, -60.84, 0.76, "Achernar", "อาเชอนาร์"),
    (1.911, -57.10, 2.86, "Phoenix α", "ฟีนิกซ์ α"),
    (2.073, 23.46, 2.12, "Hamal", "ฮามาล"),
    (2.530, 89.26, 1.98, "Polaris", "ดาวเหนือ"),
    (2.968, 53.51, 2.27, "Mirfak", "มีร์ฟัก"),
    (3.136, -17.54, 2.83, "Menkar", "เมนคาร์"),
    (3.791, 24.11, 2.87, "Alcyone", "แอลไซโอนี"),
    (4.359, 16.51, 0.85, "Aldebaran", "อัลเดบารัน"),
    (4.598, 16.51, 1.66, "Aldebaran B", "อัลเดบารัน B"),
    (5.019, 8.29, 2.97, "Elnath", "เอลนาธ"),
    (5.267, -69.13, 2.79, "Doradus α", "โดราดุส α"),
    (5.363, -1.20, 1.74, "Rigel", "ไรเจล"),
    (5.552, 7.41, 1.64, "Bellatrix", "เบลลาทริกซ์"),
    (5.679, -62.49, 1.45, "Adhara", "อาดารา"),
    (5.919, 7.41, 0.42, "Betelgeuse", "เบเทลจุส"),
    (5.992, -61.34, 2.39, "Velorum γ", "เวโลรุม γ"),
    (6.377, 16.40, 2.59, "Meissa", "ไมซา"),
    (6.452, -16.72, -1.46, "Sirius", "ซิริอุส"),
    (6.580, -52.70, -0.74, "Canopus", "คาโนปัส"),
    (6.978, -28.98, 1.50, "Wezen", "วีเซน"),
    (7.084, -26.39, 1.83, "Adhara B", "อาดารา B"),
    (7.344, -43.00, 1.98, "Almuhlifain", "อัลมุห์ลิไฟน์"),
    (7.348, 31.89, 1.90, "Castor", "แคสตอร์"),
    (7.453, 28.03, 1.14, "Pollux", "พอลลักซ์"),
    (7.567, -23.28, 2.21, "Naos", "นาโอส"),
    (7.655, 5.22, 0.38, "Procyon", "โพรซิออน"),
    (8.375, -59.51, 2.25, "Carina ε", "คารินา ε"),
    (8.675, -63.02, 2.21, "Avior", "อาวีออร์"),
    (9.130, -69.72, 2.47, "Volans β", "โวลันส์ β"),
    (9.220, 41.50, 2.01, "Ursa Major ε", "หมีใหญ่ ε"),
    (9.613, 16.04, 2.94, "Hydra α", "ไฮดรา α"),
    (9.832, 44.30, 2.27, "Ursa Major α", "หมีใหญ่ α"),
    (10.139, 11.97, 1.36, "Regulus", "เรกุลุส"),
    (10.715, -64.39, 2.68, "Carina θ", "คารินา θ"),
    (10.796, 12.04, 2.14, "Leo γ", "สิงห์ γ"),
    (11.031, 61.75, 1.79, "Ursa Major β", "หมีใหญ่ β"),
    (11.062, 61.75, 2.37, "Ursa Major η", "หมีใหญ่ η"),
    (11.818, -53.47, 2.55, "Centaurus δ", "เซนทอรัส δ"),
    (11.946, -62.73, 2.20, "Hadar", "ฮาดาร์"),
    (12.263, -63.10, -0.27, "Alpha Centauri", "อัลฟา เซนทอรี"),
    (12.430, -48.96, 2.75, "Mimosa", "มิโมซา"),
    (12.905, 38.32, 2.44, "Cor Caroli", "คอร์ คาโรไล"),
    (12.934, -11.16, 1.04, "Vindemiatrix", "วินเดเมียทริกซ์"),
    (13.062, -60.38, 2.75, "Centaurus γ", "เซนทอรัส γ"),
    (13.420, -11.16, 0.98, "Spica", "สไปกา"),
    (13.711, 27.08, 2.83, "Bootes ε", "บู้ทส ε"),
    (13.795, 21.18, 2.65, "Bootes γ", "บู้ทส γ"),
    (14.158, 19.18, -0.05, "Arcturus", "อาร์คทุรุส"),
    (14.678, -60.83, 1.86, "Triangulum Australe α", "สามเหลี่ยมใต้ α"),
    (14.884, -63.02, 2.63, "Triangulum Australe β", "สามเหลี่ยมใต้ β"),
    (15.303, 26.43, 2.77, "Northern Crown α", "มงกุฎเหนือ α"),
    (15.583, -26.28, 2.62, "Lupus α", "หมาป่า α"),
    (15.787, 33.31, 2.75, "Serpens α", "เซอร์เพนส์ α"),
    (16.021, -61.37, 1.80, "Scorpius α", "พิจิก α"),
    (16.490, -26.43, 1.08, "Antares", "แอนทาเรส"),
    (16.836, -34.29, 2.29, "Scorpius ε", "พิจิก ε"),
    (17.337, -37.10, 2.32, "Scorpius λ", "พิจิก λ"),
    (17.420, -39.03, 2.89, "Scorpius υ", "พิจิก υ"),
    (17.538, -37.10, 3.00, "Scorpius G", "พิจิก G"),
    (17.622, -42.36, 2.82, "Scorpius κ", "พิจิก κ"),
    (17.976, -37.04, 1.86, "Shaula", "ชาอูลา"),
    (18.242, -34.38, 2.69, "Draco γ", "ดราโค γ"),
    (18.616, 38.78, 0.03, "Vega", "เวกา"),
    (18.763, -63.10, 2.79, "Ara β", "แท่นบูชา β"),
    (19.046, -40.62, 2.76, "Ara α", "แท่นบูชา α"),
    (19.525, 10.96, 2.72, "Ophiuchus η", "โอฟิวคัส η"),
    (19.626, -21.75, 2.56, "Sabik", "ซาบิก"),
    (19.846, 8.87, 0.77, "Altair", "อัลทาอิร์"),
    (20.212, -12.85, 2.77, "Sagittarius N", "ธนู N"),
    (20.427, -40.62, 2.02, "Peacock", "พีค็อก"),
    (20.690, 45.28, 1.26, "Deneb", "ดีเนบ"),
    (21.142, -11.35, 2.81, "Capricornus α", "แพะยัง α"),
    (21.256, -38.05, 2.85, "Grus α", "นกกระเรียน α"),
    (21.478, -46.88, 2.07, "Grus α B", "นกกระเรียน α B"),
    (21.736, 62.59, 2.27, "Cepheus α", "เซเฟอุส α"),
    (21.868, -77.08, 2.80, "Octantis ν", "อ็อกแทนติส ν"),
    (22.053, -46.96, 1.74, "Fomalhaut", "โฟมาลเฮาต์"),
    (22.828, -46.88, 2.39, "Tucana α", "นกทูแคน α"),
    (22.961, -29.62, 1.17, "Fomalhaut B", "โฟมาลเฮาต์ B"),
    (23.038, 15.21, 2.77, "Pegasus ε", "ม้าบิน ε"),
    (23.286, 15.21, 2.49, "Markab", "มาร์คับ"),
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
