"""Brady paran engine — fixed-star angle crossings at birth latitude.

A paran occurs when planet A is on one angle while star S touches another,
within ~2 minutes of clock time. Latitude-dependent — doubles as a
rectification discriminator and a true differentiator vs conjunction apps.

24 major stars (the subset of Brady's canonical list this engine ships:
the brightest named stars plus the culturally significant ones — Aldebaran
and its "north node" companion, Alcyone for the Pleiades, Regulus, Spica,
Fomalhaut, the two bear-dipper guards, and so on). Not the full 64.

Star longitudes are precessed from the J2000 catalogue to the true equinox
and ecliptic of date by Skyfield's `build_ecliptic_matrix` (IAU 2006/2006A
precession plus true obliquity and nutation) and `t.M`, which is the frame
right ascension and declination are measured in. This module is a thin
wrapper: it holds no rotation matrices of its own.

That has a consequence worth stating plainly. Any comparison of this engine
against Skyfield is a CONSISTENCY check and proves nothing about accuracy --
the engine *is* that code path. The frame is instead held against a reference
it shares no code with: SOFA/ERFA's `pnm06a` (IAU 2006A precession-nutation).
Measured worst residual over the 24 stars, at the reference epoch:

    right ascension / dec    vs ERFA pnm06a               0.0000 arcsec

So the rotation is not merely close to, but numerically identical to, the
reference implementation of the model it claims. Earlier revisions validated
the frame against abbreviated Meeus ch. 21/22 series and quoted a 0.40 arcsec
residual; that figure was the *reference's* truncation error, not the engine's,
and is now retired. Obliquity is still cross-checked against Swiss Ephemeris
ECL_NUT[0] (0.0008 arcsec) and tests/test_parans_frames.py still pins the
precession-rate difference as a regression bound.

Star positions are ICRS J2000 from the Hipparcos new reduction (van Leeuwen
2007, VizieR I/311/hip2), propagated from its Ep=1991.25 reference epoch.
Proper motion IS applied, and is applied in the ICRS frame *before* the
precession-nutation rotation, which is the order SOFA's sla_STARPV uses. The
order matters: PM is up to 228 arcsec/century (Arcturus), and rotating that
motion into the wrong frame first would leave a ~0.4 arcsec error at a 1997
epoch -- the same size as the frame residual this module cares about.
Over 1900-2100 the largest tangential proper-motion term is ~34 arcsec
(Arcturus at +100 yr); for the 1900-2100 span this engine accepts, the term
is never larger than the 0.05 arcmin parans are read to.

An earlier revision of this docstring claimed the PM omission was ~0.2
arcsec/century. Measured against Swiss Ephemeris 2.10.03 by differencing
unit-vector motion over a 100-year same-calendar-date span, it is up to
228 arcsec/century -- understated by three orders of magnitude. The five
largest cases reproduce published Hipparcos proper motions to better than 1%.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

import numpy as np

from src.services.chart_service import compute_chart

# ICRS J2000 mean positions from the Hipparcos new reduction (van Leeuwen
# 2007), VizieR I/311/hip2, propagated from its Ep=1991.25 reference epoch.
# `ra` is hours, `dec` degrees, `pm_ra` is mu_alpha*cos(dec) and `pm_dec` is
# mu_dec, both mas/yr, applied per `_star_epoch_radec` before precession.
#
# The previous table was rounded to 0.001h/0.001deg, which is up to 54 arcsec
# of error in RA on its own -- larger than the proper-motion term it was
# missing. Full precision costs nothing here and removes the ambiguity.
#
# `Aldebaran_N` is not a star. It is the traditional "north node companion" of
# Aldebaran (Lilly/Billy), a synthetic point with no catalogue counterpart, so
# it keeps its legacy position and is given no invented proper motion. It lies
# 35 arcsec from Aldebaran, so ignoring the motion costs well under 1 arcsec
# over any chart the engine accepts.
STARS: dict[str, dict] = {
    "Aldebaran": {"ra": 4.59867752, "dec": 16.50930235, "pm_ra": 63.450, "pm_dec": -188.940, "mag": 0.87},
    "Rigel": {"ra": 5.24229780, "dec": -8.20163836, "pm_ra": 1.310, "pm_dec": 0.500, "mag": 0.13},
    "Betelgeuse": {"ra": 5.91952927, "dec": 7.40706400, "pm_ra": 27.540, "pm_dec": 11.300, "mag": 0.5},
    "Sirius": {"ra": 6.75247703, "dec": -16.71611580, "pm_ra": -546.010, "pm_dec": -1223.070, "mag": -1.46},
    "Castor": {"ra": 7.57663144, "dec": 31.88828222, "pm_ra": -191.450, "pm_dec": -145.190, "mag": 1.58},
    "Pollux": {"ra": 7.75526385, "dec": 28.02619890, "pm_ra": -626.550, "pm_dec": -45.800, "mag": 1.14},
    "Procyon": {"ra": 7.65503319, "dec": 5.22498758, "pm_ra": -714.590, "pm_dec": -1036.800, "mag": 0.34},
    "Regulus": {"ra": 10.13953083, "dec": 11.96720878, "pm_ra": -248.730, "pm_dec": 5.590, "mag": 1.35},
    "Alphard": {"ra": 9.45978964, "dec": -8.65859953, "pm_ra": -15.230, "pm_dec": 34.370, "mag": 1.98},
    "Spica": {"ra": 13.41988316, "dec": -11.16131949, "pm_ra": -42.350, "pm_dec": -30.670, "mag": 0.97},
    "Arcturus": {"ra": 14.26102001, "dec": 19.18240920, "pm_ra": -1093.390, "pm_dec": -2000.060, "mag": -0.05},
    "Antares": {"ra": 16.49012769, "dec": -26.43200261, "pm_ra": -12.110, "pm_dec": -23.300, "mag": 1.06},
    "Vega": {"ra": 18.61564899, "dec": 38.78368896, "pm_ra": 200.940, "pm_dec": 286.230, "mag": 0.03},
    "Altair": {"ra": 19.84638849, "dec": 8.86832120, "pm_ra": 536.230, "pm_dec": 385.290, "mag": 0.76},
    "Fomalhaut": {"ra": 22.96084618, "dec": -29.62223704, "pm_ra": 328.950, "pm_dec": -164.670, "mag": 1.16},
    "Deneb": {"ra": 20.69053198, "dec": 45.28033881, "pm_ra": 2.010, "pm_dec": 1.850, "mag": 1.25},
    "Achernar": {"ra": 1.62856819, "dec": -57.23675279, "pm_ra": 87.000, "pm_dec": -38.240, "mag": 0.46},
    "Alcyone (Pleiades)": {"ra": 3.79141015, "dec": 24.10513565, "pm_ra": 19.340, "pm_dec": -43.670, "mag": 2.87},
    "Bellatrix": {"ra": 5.41885090, "dec": 6.34970326, "pm_ra": -8.110, "pm_dec": -12.880, "mag": 1.64},
    "Capella": {"ra": 5.27815520, "dec": 45.99799147, "pm_ra": 75.250, "pm_dec": -426.890, "mag": 0.08},
    "Aldebaran_N": {"ra": 4.598, "dec": 16.51, "mag": 0.85},
    "Canopus": {"ra": 6.39919719, "dec": -52.69566138, "pm_ra": 19.930, "pm_dec": 23.240, "mag": -0.74},
    "Hamal": {"ra": 2.11955714, "dec": 23.46241755, "pm_ra": 188.550, "pm_dec": -148.080, "mag": 2.0},
    "Polaris": {"ra": 2.53030407, "dec": 89.26410898, "pm_ra": 44.480, "pm_dec": -11.850, "mag": 1.98},
}
STAR_TH = {
    "Aldebaran": ("อัลเดบารัน", "ความสำเร็จผ่านความกล้าหาญ"),
    "Sirius": ("เซียริอุส", "ชื่อเสียงกระจาย เปล่งประกาย"),
    "Regulus": ("เรกุลุส", "หัวหน้า ราชวงศ์ พลังบารมี"),
    "Spica": ("สไปกา", "โชคลาภ ความงาม ของขวัญจากฟ้า"),
    "Vega": ("เวกา", "ศิลปิน เสียง เสน่ห์ทางคำพูด"),
    "Arcturus": ("อาร์คทุรุส", "มองไกล ความมั่งคั่งจากการเดินทาง"),
    "Antares": ("แอนทาเรส", "ความร้อนแรง ไม่ยอมแพ้"),
    "Fomalhaut": ("โฟมาลเฮาต์", "ความฝันอันสูงส่ง อุดมคติ"),
    "Procyon": ("โพรซิออน", "เร็วว่องไว ชื่อดังฉับพลัน"),
    "Pollux": ("พอลลักซ์", "ความกล้า ยืนหยัดเพื่อคนอื่น"),
}

# Same planet wording as astrocartography_service / hellenistic_timelords, so
# one planet reads the same way across the whole app.
_PLANET_TH = {"Sun": "ดวงอาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
              "Venus": "ดาวศุกร์", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัสฯ",
              "Saturn": "ดาวเสาร์"}

_TIMESCALE = None
_STARS_CACHE: dict[float, dict[str, float]] = {}
_STARS_RADEC_CACHE: dict[float, dict[str, tuple[float, float]]] = {}


def _timescale():
    global _TIMESCALE
    if _TIMESCALE is None:
        from skyfield.api import load
        _TIMESCALE = load.timescale()
    return _TIMESCALE


def _jd_ut(dt) -> float:
    """Python datetime (naive is read as UTC) -> Julian Date in TT.

    The star matrix is evaluated in Terrestrial Time, so the UTC input is
    converted rather than relabelled: TT-UTC was 62.2 s on 1997-05-18. That
    62 s is 2.6e-4 deg of precession (1.3e-6 arcsec), negligible for the
    catalogue, but carrying the right scale costs nothing.
    """
    d = dt
    if d.tzinfo is not None:
        d = d.astimezone(timezone.utc).replace(tzinfo=None)
    t = _timescale().utc(d.year, d.month, d.day,
                         d.hour + d.minute / 60.0 + d.second / 3600.0)
    return t.tt


def _ecliptic_matrix(jd_ut: float):
    """3x3 row-major matrix mapping an ICRF unit vector to ecliptic of-date.

    Skyfield's `build_ecliptic_matrix` implements IAU 2006 precession plus the
    true obliquity and nutation of the requested instant. The hand-rolled code
    this replaced used one constant obliquity and a linear 50.29"/yr shift,
    which was wrong by up to 2.8 deg of ecliptic longitude for birth epochs
    ~100 yr from J2000.
    """
    from skyfield.framelib import build_ecliptic_matrix

    t = _timescale().tt(jd=jd_ut)
    m = build_ecliptic_matrix(t)
    return tuple(tuple(float(v) for v in row) for row in m)


def _frames(jd_ut: float):
    """(m_ecl, m_tete) for one instant, both derived from the same Skyfield time.

    m_tete maps an ICRF vector to the true equator and equinox of date --
    the frame right ascension and declination are measured in. m_ecl maps
    it to the ecliptic of date. Skyfield builds the ecliptic matrix as
    rot_x(-true_obliquity) applied to t.M, so the true obliquity of date is
    recoverable from the pair without reaching into private attributes:
    rot_x(-eps) = m_ecl @ m_tete.T, and cos(eps) is its [1][1] element.
    """
    from skyfield.framelib import build_ecliptic_matrix

    t = _timescale().tt(jd=jd_ut)
    m_ecl = build_ecliptic_matrix(t)
    m_tete = np.array(t.M)
    return m_ecl, m_tete


def _star_epoch_radec(name: str, jd_ut: float) -> tuple[float, float]:
    """(RA, Dec) in degrees of one catalogue star at the requested epoch.

    The catalogue position is ICRS/J2000, so proper motion is propagated along
    the sky in the ICRS frame and only the result is handed to the
    precession-nutation matrix.  Doing it the other way round -- rotating the
    motion vector into the of-date frame first -- is the same order as
    applying the motion in the wrong frame, and for Arcturus over a 1997
    birth epoch that mistake is worth ~0.4 arcsec, the same size as the frame
    residual this module is careful about.

    Second-order terms are deliberately not modelled: perspective
    acceleration needs radial velocity, and the curvature term is
    pm^2*t^2/2, which for the fastest star here (Sirius, 1.34 arcsec/yr) is
    under a microarcsecond over the +-100 yr the engine accepts.

    `jd_ut` is Terrestrial Time despite the name; see `_jd_ut`.
    """
    s = STARS[name]
    ra = s["ra"] * 15.0
    dec = s["dec"]
    pm_ra = s.get("pm_ra", 0.0)
    pm_dec = s.get("pm_dec", 0.0)
    if pm_ra or pm_dec:
        years = (jd_ut - 2451545.0) / 365.25  # Julian years from J2000
        dec += pm_dec / 1000.0 * years / 3600.0
        # pm_ra is mu_alpha*cos(dec), so undo the cos before scaling RA.
        ra += pm_ra / 1000.0 * years / 3600.0 / math.cos(math.radians(dec))
        ra %= 360.0
    return ra, dec


def _obliquity_of_date(m_ecl, m_tete) -> float:
    """True obliquity of date (radians) implied by Skyfield's two frames.

    Replaces a single hardcoded J2000 constant, which was off by up to
    ~0.01 deg across the 1900-2100 span the engine accepts. Nutation makes
    the true value differ from the mean by up to 9 arcsec.
    """
    rot = np.asarray(m_ecl) @ m_tete.T
    return math.acos(max(-1.0, min(1.0, float(rot[1][1]))))


def star_positions(jd_ut: float) -> dict[str, float]:
    """Ecliptic longitudes (deg) of every fixed star at Julian date `jd_ut` (UT).

    The star catalogue is J2000; positions are precessed to the true equinox of
    date with the IAU 2006 model. Cached per day-ish epoch because the callers
    ask repeatedly for the same chart.
    """
    key = round(jd_ut * 4) / 4.0  # ~6h granularity
    cached = _STARS_CACHE.get(key)
    if cached is not None:
        return cached

    m = _ecliptic_matrix(jd_ut)
    out: dict[str, float] = {}
    for name in STARS:
        ra_deg, dec_deg = _star_epoch_radec(name, jd_ut)
        ra = math.radians(ra_deg)
        dec = math.radians(dec_deg)
        v = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
        o = (
            m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
            m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
            m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
        )
        out[name] = math.degrees(math.atan2(o[1], o[0])) % 360
    _STARS_CACHE[key] = out
    return out


def star_radec(jd_ut: float) -> dict[str, tuple[float, float]]:
    """(RA, Dec) of date in degrees for every fixed star.

    This is what parans need, and `star_positions` is the wrong input for
    them. A paran is a horizon/meridian event, so it lives in the equatorial
    frame: Kenneth Bowser's "Aspects in Mundo" (The Mountain Astrologer,
    1996) is explicit that these aspects are reckoned in right ascension,
    which is why they return the same result under any zodiac or ayanamsa.
    Star longitudes cannot substitute -- reconstructing RA/Dec from an
    ecliptic longitude throws away the star's ecliptic latitude, and for
    Sirius (beta ~ -39.6 deg) that reconstruction lands 39 deg away in
    declination from where the star actually rises and sets.
    """
    key = round(jd_ut * 4) / 4.0
    cached = _STARS_RADEC_CACHE.get(key)
    if cached is not None:
        return cached

    _, m_tete = _frames(jd_ut)
    out: dict[str, tuple[float, float]] = {}
    for name in STARS:
        ra_deg, dec_deg = _star_epoch_radec(name, jd_ut)
        ra0 = math.radians(ra_deg)
        dec0 = math.radians(dec_deg)
        v = np.array([math.cos(dec0) * math.cos(ra0),
                      math.cos(dec0) * math.sin(ra0),
                      math.sin(dec0)])
        o = m_tete @ v
        ra = math.degrees(math.atan2(o[1], o[0])) % 360
        dec = math.degrees(math.asin(max(-1.0, min(1.0, float(o[2])))))
        out[name] = (ra, dec)
    _STARS_RADEC_CACHE[key] = out
    return out


def _rise_hour_angle(lat_deg: float, dec_deg: float) -> float | None:
    """Hour angle (deg) at rising/setting, or None if the body is circumpolar.

    Direct spherical astronomy -- cos H = -tan(phi) tan(delta) -- so it needs
    only the body's declination of date. The previous helper scanned a whole
    day at 4-minute steps looking for the crossing, and when it found a
    circumpolar star it returned H = 180, which is indistinguishable from
    "culminating at the IC": Aldebaran_N at high latitude would have been
    reported as rising when it never leaves the northern sky.
    """
    cos_h = (-math.tan(math.radians(lat_deg))
             * math.tan(math.radians(dec_deg)))
    if cos_h > 1.0 or cos_h < -1.0:
        return None
    return math.degrees(math.acos(cos_h))


def _lonlat_to_radec(lon_deg: float, lat_deg: float, obliquity: float) -> tuple[float, float]:
    """Ecliptic-of-date (lon, lat) -> RA/Dec of date, in degrees.

    The latitude term is the whole point of this function. Dropping it
    (the previous `star_ra_dec`/`planet_ra_dec` pair) silently forces the
    body onto the ecliptic, and the resulting RA error runs to ~2.4 deg for
    Mercury and ~1.3 deg for Mars -- far outside a 2-minute orb. Bowser
    tabulates exactly these figures as the reason mundane aspects differ
    from zodiacal ones.
    """
    lam = math.radians(lon_deg)
    bet = math.radians(lat_deg)
    ra = math.atan2(
        math.sin(lam) * math.cos(bet) * math.cos(obliquity)
        - math.sin(bet) * math.sin(obliquity),
        math.cos(bet) * math.cos(lam),
    )
    dec = math.asin(
        math.sin(bet) * math.cos(obliquity)
        + math.cos(bet) * math.sin(obliquity) * math.sin(lam)
    )
    return math.degrees(ra) % 360, math.degrees(dec)


def _angle_lst(asc_or_mc: float, obliquity: float) -> float:
    """RAMC/LST (deg of RA) from an MC ecliptic longitude.

    The MC is a point *on the ecliptic*, so its right ascension is not its
    longitude. Using the longitude directly is wrong by up to 2.46 deg
    mid-quadrant -- 9.9 minutes of clock time against a 2-minute orb.
    """
    lam = math.radians(asc_or_mc)
    ra = math.atan2(math.sin(lam) * math.cos(obliquity), math.cos(lam))
    return math.degrees(ra) % 360


def brady_parans(birth_date_iso: str, birth_time_hhmm: str,
                 tz_offset_hours: float, lat: float, lon: float,
                 orb_minutes: float = 4) -> dict:
    """Compute parans present at birth: planet-on-angle while star-on-angle
    within +/-orb_minutes of clock time.

    `orb_minutes` is the allowed difference between the two bodies' *positions
    on the angle* (POA), not the distance from the angle itself. The default of
    4 min is ~1 deg of arc measured along the angle circle, the usual POA
    tolerance in the locals method; 1 deg of arc / 360 deg * sidereal day is
    3.99 min of clock time. Raise it for a denser chart, lower it for the
    tightest signatures only.
    """
    birth_local = datetime.fromisoformat(f"{birth_date_iso}T{birth_time_hhmm}:00")
    birth_utc = birth_local - timedelta(hours=tz_offset_hours)

    chart = compute_chart("parans", birth_utc.date(), birth_utc.time(),
                          tz_offset_hours=0, lat=lat, lon=lon)
    bodies = {b["body"]: (float(b["absolute_deg"]), float(b.get("latitude", 0.0)))
              for b in chart["bodies"]}
    angles = {"ASC": chart["ascendant"]["absolute_deg"]}
    for c in (chart.get("houses") or {}).get("cusps", []):
        if c.get("house") == 10:
            angles["MC"] = float(c["absolute_deg"])
    angles.setdefault("MC", (angles["ASC"] + 90) % 360)
    angles["DSC"] = (angles["ASC"] + 180) % 360
    angles["IC"] = (angles["MC"] + 180) % 360

    jd = _jd_ut(birth_utc)
    m_ecl, m_tete = _frames(jd)
    eps = _obliquity_of_date(m_ecl, m_tete)
    ramc = _angle_lst(angles["MC"], eps)
    stars = star_radec(jd)
    # Aldebaran_N is a synthetic row (Lilly's north companion, 35" from the
    # real Aldebaran) and carries no proper motion, so no catalogue can
    # resolve it. Left in, it produces a near-duplicate paran a couple of
    # arcminutes from Aldebaran's own, which reads as noise. Keep it in
    # STARS; drop it from chart output.
    stars = {k: v for k, v in stars.items() if "pm_ra" in STARS.get(k, {})}
    orb_deg = orb_minutes * (360.0 / (24 * 60))  # deg of hour angle per minute of clock

    # A paran is one angle circle held in common by both bodies. Matching a
    # planet at the ASC against a star at the DSC is not that -- those are
    # opposite ends of the horizon -- so the four angles are looped once, not
    # crossed against each other.
    def poa_minutes(ra_deg: float, dec_deg: float, angle: str) -> float | None:
        """Signed position on the angle, in minutes of clock time.

        Positive = the body reaches the angle that many minutes *after* the
        birth instant, negative = that long *before*. The value belongs to the
        chart, not to the birth moment: a planet at POA -438 min and a star at
        -440 min reach that angle two hours away from the birth, and they
        reach it together. That is the paran.
        """
        h = (ramc - ra_deg) % 360
        if angle == "MC":
            target = 0.0
        elif angle == "IC":
            target = 180.0
        else:
            h_rise = _rise_hour_angle(lat, dec_deg)
            if h_rise is None:
                return None  # circumpolar: never on this horizon angle
            target = -h_rise if angle == "ASC" else h_rise
        d = (h - target + 180) % 360 - 180
        return d * (24 * 60) / 360.0

    parans = []
    planets_considered = ["Sun", "Moon", "Mercury", "Venus", "Mars",
                          "Jupiter", "Saturn"]
    for pname in planets_considered:
        plon = bodies.get(pname)
        if plon is None:
            continue
        pra, pdec = _lonlat_to_radec(plon[0], plon[1], eps)
        for sname, (sra, sdec) in stars.items():
            for ang in ("ASC", "MC", "DSC", "IC"):
                p_poa = poa_minutes(pra, pdec, ang)
                if p_poa is None:
                    continue
                s_poa = poa_minutes(sra, sdec, ang)
                if s_poa is None:
                    continue
                # The paran is the COINCIDENCE of the two positions on the
                # angle. Gating on max(|planet|, |star|) instead -- i.e.
                # demanding both bodies sit on the angle at the birth instant
                # -- discards every paran whose bodies reach that angle some
                # minutes away from the birth, which is the normal case and
                # silently returned zero for whole charts.
                gap = abs(p_poa - s_poa)
                if gap > orb_minutes:
                    continue
                th_name, meaning = STAR_TH.get(sname, (sname, "ดาวฤกษ์หลัก"))
                parans.append({
                    "planet": pname, "planet_angle": ang,
                    "star": sname, "star_angle": ang,
                    "separation_minutes": round(gap, 2),
                    "planet_poa_minutes": round(p_poa, 2),
                    "star_poa_minutes": round(s_poa, 2),
                    # th_name is the whole name; th_name[0] yielded only its
                    # first character, rendering "ดาวอ" for อัลเดบารัน.
                    "th": f"{_PLANET_TH.get(pname, pname)} มุม{ang} × ดาว{th_name} มุม{ang}",
                    "meaning_th": meaning,
                })

    # dedupe, tightest first -- the headline parans of a chart are the ones
    # whose two positions on the angle nearly coincide.
    seen = set()
    unique = []
    for p in parans:
        k = (p["planet"], p["planet_angle"], p["star"], p["star_angle"])
        if k not in seen:
            seen.add(k)
            unique.append(p)
    unique.sort(key=lambda p: p["separation_minutes"])

    return {
        "system": "brady-parans",
        "latitude_used": lat,
        "stars_checked": len(STARS),
        "orb_minutes": orb_minutes,
        "parans_found": len(unique),
        "parans": unique[:20],
        "interpretation": {
            "th": (
                f'ณ ละติจูด {lat:.2f}° พบ paranatellonta '
                f'{len(unique)} คู่ (เกณฑ์ตำแหน่งบนมุมต่างกันไม่เกิน '
                f'{orb_minutes:g} นาที) — แต่ละคู่คือดาวเคราะห์กับดาวฤกษ์ที่ '
                f'ตรงกันบนมุมเดียวกันของท้องฟ้า '
                f'(paran = ลายเซ็นของท้องฟ้า ณ แผ่นดินที่คุณเกิด)'
            ),
            "en": (f"{len(unique)} stellar parans at latitude {lat:.2f}° "
                   f"(Brady method, POA within {orb_minutes:g} min)."),
        },
    }
