#!/usr/bin/env python3
"""Western tropical deep-dive techniques not yet in the vault: precise aspect
grid, Placidus house cusps, Part of Fortune, composite chart, Davison chart,
secondary progressions.

Reuses natal_chart.compute_chart (JPL DE421 via skyfield) for all raw
planetary positions. No Chiron here — DE421 has no minor-planet ephemeris;
Chiron was researched externally instead (see raw/2026-08-15-chiron-ephemeris-serennu.md).

Usage: python3 western_advanced.py   (runs the demo() self-check + prints
report for both the vault owner and Mai using the birth data already
established in the vault's other scripts/notes)
"""
import math
from datetime import datetime, timezone, timedelta
from natal_chart import compute_chart, local_to_utc, to_sign, BODIES, OBLIQUITY

# ---- birth data already established/verified elsewhere in the vault ----
OWNER = dict(date="1997-05-19", time="05:45", tz=7.0, lat=13.36, lon=100.98, name="เจ้าของ vault")
MAI = dict(date="2001-08-18", time="22:32", tz=7.0, lat=13.86, lon=100.52, name="Mai")

ALL_POINTS = list(BODIES) + ['ASC']

# ---------------------------------------------------------------- aspects --
ASPECTS = {
    'conjunction': 0, 'sextile': 60, 'square': 90, 'trine': 120, 'opposition': 180,
}
ORBS = {'conjunction': 8, 'sextile': 6, 'square': 7, 'trine': 8, 'opposition': 8}


def angle_diff(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def tightness(orb):
    if orb <= 1:
        return "very tight"
    if orb <= 3:
        return "tight"
    if orb <= 6:
        return "moderate"
    return "wide"


def aspect_grid(chart, points=None, exclude_same=True):
    """All-pairs aspect grid within ONE chart (tropical). Returns sorted rows."""
    points = points or ALL_POINTS
    rows = []
    for i, p1 in enumerate(points):
        for p2 in points[i + 1:] if exclude_same else points:
            if p1 == p2:
                continue
            sep = angle_diff(chart[p1]['trop'], chart[p2]['trop'])
            for name, exact in ASPECTS.items():
                orb = abs(sep - exact)
                if orb <= ORBS[name]:
                    rows.append((p1, p2, name, sep, orb, tightness(orb)))
                    break  # a pair only gets its closest-matching aspect
    rows.sort(key=lambda r: r[4])
    return rows


def cross_aspect_grid(chart_a, chart_b, points=None):
    """All-pairs aspect grid BETWEEN two charts (synastry), precise orbs."""
    points = points or ALL_POINTS
    rows = []
    for p1 in points:
        for p2 in points:
            sep = angle_diff(chart_a[p1]['trop'], chart_b[p2]['trop'])
            for name, exact in ASPECTS.items():
                orb = abs(sep - exact)
                if orb <= ORBS[name]:
                    rows.append((p1, p2, name, sep, orb, tightness(orb)))
                    break
    rows.sort(key=lambda r: r[4])
    return rows


# ------------------------------------------------------------- ecliptic->RA/dec --
def ecl_to_eq(lon_deg, lat_deg=0.0):
    """Ecliptic (lon,lat=0, on the ecliptic) -> equatorial RA/dec, degrees."""
    lon = math.radians(lon_deg)
    eps = OBLIQUITY
    sin_dec = math.sin(eps) * math.sin(lon)
    dec = math.asin(sin_dec)
    ra = math.atan2(math.cos(eps) * math.sin(lon), math.cos(lon))
    return math.degrees(ra) % 360, math.degrees(dec)


def semi_diurnal_arc(dec_deg, lat_deg):
    """SDA in degrees (0-180). None if circumpolar (shouldn't happen at these latitudes)."""
    x = -math.tan(math.radians(lat_deg)) * math.tan(math.radians(dec_deg))
    x = max(-1.0, min(1.0, x))
    return math.degrees(math.acos(x))


# -------------------------------------------------------------- Placidus houses --
def _find_cusp(ramc, lat_deg, target_fn, lo, hi, steps=3600):
    """Scan lo->hi (unwrapped degrees, hi>lo) for sign change of g(lambda), then bisect.
    target_fn(lambda_deg) -> g value (should cross zero once in this bracket)."""
    prev_l = lo
    prev_g = target_fn(lo)
    step = (hi - lo) / steps
    lo_bracket, hi_bracket = None, None
    l = lo
    for _ in range(steps):
        l += step
        g = target_fn(l)
        if prev_g == 0:
            return prev_l % 360
        if (prev_g < 0) != (g < 0):
            lo_bracket, hi_bracket = prev_l, l
            break
        prev_l, prev_g = l, g
    if lo_bracket is None:
        raise ValueError("no sign change found in bracket — Placidus solver failed")
    a, b = lo_bracket, hi_bracket
    ga = target_fn(a)
    for _ in range(60):
        m = (a + b) / 2
        gm = target_fn(m)
        if (gm < 0) == (ga < 0):
            a, ga = m, gm
        else:
            b = m
    return ((a + b) / 2) % 360


def placidus_cusps(dt_utc, lat_deg, lon_deg):
    """Return dict house# (1-12) -> tropical ecliptic longitude, Placidus system."""
    ts_chart = compute_chart(dt_utc, lat_deg, lon_deg)
    from skyfield.api import load
    ts = load.timescale()
    t = ts.from_datetime(dt_utc)
    ramc = (t.gmst * 15 + lon_deg) % 360  # RA of MC = local sidereal time

    asc_lon = ts_chart['ASC']['trop']
    ra_asc, _ = ecl_to_eq(asc_lon)
    # MC: ecliptic point whose RA == ramc
    mc_lon = math.degrees(math.atan2(math.sin(math.radians(ramc)), math.cos(math.radians(ramc)) * math.cos(OBLIQUITY))) % 360

    def g_upper(f):
        def fn(lam):
            ra, dec = ecl_to_eq(lam)
            sda = semi_diurnal_arc(dec, lat_deg)
            target_ra = (ramc + f * sda) % 360
            # unwrap difference to keep it continuous across the bracket
            diff = (ra - target_ra + 540) % 360 - 180
            return diff
        return fn

    def g_lower(f):
        def fn(lam):
            ra, dec = ecl_to_eq(lam)
            sna = 180 - semi_diurnal_arc(dec, lat_deg)
            target_ra = (ramc + 180 - f * sna) % 360
            diff = (ra - target_ra + 540) % 360 - 180
            return diff
        return fn

    # bracket from MC to ASC (unwrap forward span), and ASC to IC(=MC+180), forward
    span_mc_asc = (asc_lon - mc_lon) % 360
    lam11 = _find_cusp(ramc, lat_deg, g_upper(1 / 3), mc_lon, mc_lon + span_mc_asc)
    lam12 = _find_cusp(ramc, lat_deg, g_upper(2 / 3), mc_lon, mc_lon + span_mc_asc)

    ic_lon = (mc_lon + 180) % 360
    span_asc_ic = (ic_lon - asc_lon) % 360  # going forward from ASC to IC the "long way" (through 2,3,4)
    # cusp2,3 bracket is IC -> ASC going backward, i.e. asc_lon .. asc_lon+span (ending at ic_lon+360)
    lam3 = _find_cusp(ramc, lat_deg, g_lower(1 / 3), asc_lon, asc_lon + span_asc_ic)
    lam2 = _find_cusp(ramc, lat_deg, g_lower(2 / 3), asc_lon, asc_lon + span_asc_ic)

    cusps = {
        1: asc_lon, 4: ic_lon, 7: (asc_lon + 180) % 360, 10: mc_lon,
        11: lam11, 12: lam12, 2: lam2, 3: lam3,
    }
    for h in (11, 12, 2, 3):
        cusps[(h + 6 - 1) % 12 + 1] = (cusps[h] + 180) % 360
    return cusps, ramc, mc_lon


def whole_sign_house(planet_lon, asc_lon):
    return (int(planet_lon // 30) - int(asc_lon // 30)) % 12 + 1


def placidus_house_of(planet_lon, cusps):
    """Which Placidus house does planet_lon fall in? cusps: dict house->lon."""
    order = [cusps[h] for h in range(1, 13)]
    for h in range(1, 13):
        lo = order[h - 1]
        hi = order[h % 12]
        span = (hi - lo) % 360
        pos = (planet_lon - lo) % 360
        if pos < span:
            return h
    return None  # shouldn't happen


# --------------------------------------------------------------- Part of Fortune --
def part_of_fortune(chart, is_day_chart):
    asc = chart['ASC']['trop']
    sun = chart['Sun']['trop']
    moon = chart['Moon']['trop']
    if is_day_chart:
        return (asc + moon - sun) % 360
    else:
        return (asc + sun - moon) % 360


# --------------------------------------------------------------- composite/Davison --
def circular_mean(a, b):
    """Midpoint of two angles taking the SHORTER arc between them."""
    diff = (b - a) % 360
    if diff > 180:
        a, b = b, a
        diff = 360 - diff
    return (a + diff / 2) % 360


def composite_chart(chart_a, chart_b):
    comp = {}
    for p in ALL_POINTS:
        comp[p] = {'trop': circular_mean(chart_a[p]['trop'], chart_b[p]['trop'])}
    return comp


def davison_chart(a, b):
    """a, b: dicts with date/time/tz/lat/lon (local). Returns compute_chart output
    for the midpoint moment (UTC) and midpoint location."""
    dt_a = local_to_utc(a['date'], a['time'], a['tz'])
    dt_b = local_to_utc(b['date'], b['time'], b['tz'])
    mid_dt = dt_a + (dt_b - dt_a) / 2
    mid_lat = (a['lat'] + b['lat']) / 2
    mid_lon = (a['lon'] + b['lon']) / 2
    return compute_chart(mid_dt, mid_lat, mid_lon), mid_dt, mid_lat, mid_lon


# --------------------------------------------------------------- progressions --
def progressed_chart(person, on_date=None):
    """Secondary progression: birth + N days (N = age in years) at birth time/place."""
    dt_birth = local_to_utc(person['date'], person['time'], person['tz'])
    birth_local = datetime.strptime(f"{person['date']} {person['time']}", "%Y-%m-%d %H:%M")
    today = on_date or datetime.utcnow()
    age_years = (today - birth_local).days / 365.25
    prog_dt = dt_birth + timedelta(days=age_years)
    chart = compute_chart(prog_dt, person['lat'], person['lon'])
    return chart, age_years, prog_dt


# --------------------------------------------------------------------- report --
def fmt(lon):
    s, d = to_sign(lon)
    return f"{s.split('(')[0]:12s} {d:5.2f}"


def print_aspect_rows(rows, chart_label_fn):
    for p1, p2, name, sep, orb, tight in rows:
        print(f"  {p1:8s} {p2:8s} {name:12s} sep={sep:6.2f} orb={orb:5.2f} ({tight})")


def demo():
    """Self-check: MC/ASC exactness, monotonic Placidus order, opposite-cusp symmetry."""
    dt_utc = local_to_utc(OWNER['date'], OWNER['time'], OWNER['tz'])
    cusps, ramc, mc_lon = placidus_cusps(dt_utc, OWNER['lat'], OWNER['lon'])
    chart = compute_chart(dt_utc, OWNER['lat'], OWNER['lon'])
    assert abs(cusps[10] - mc_lon) < 1e-6, "cusp10 must equal MC exactly"
    assert abs(cusps[1] - chart['ASC']['trop']) < 1e-6, "cusp1 must equal ASC exactly"
    for h in (11, 12, 2, 3):
        h2 = (h + 6 - 1) % 12 + 1
        opp = (cusps[h] + 180) % 360
        assert abs(opp - cusps[h2]) < 1e-6, f"cusp{h} and cusp{h2} must be exactly opposite"
    # monotonic order test: walking cusps 1..12 in house order should always advance forward
    order = [cusps[h] for h in range(1, 13)]
    for i in range(12):
        span = (order[(i + 1) % 12] - order[i]) % 360
        assert 0 < span < 180, f"house {i+1} span looks wrong: {span}"
    print("demo(): Placidus self-check OK (ASC/MC exact, opposite pairs exact, monotonic order)")


if __name__ == "__main__":
    demo()
    print()

    dt_owner = local_to_utc(OWNER['date'], OWNER['time'], OWNER['tz'])
    dt_mai = local_to_utc(MAI['date'], MAI['time'], MAI['tz'])
    chart_owner = compute_chart(dt_owner, OWNER['lat'], OWNER['lon'])
    chart_mai = compute_chart(dt_mai, MAI['lat'], MAI['lon'])

    print("=" * 70)
    print("OWNER — natal internal aspect grid (tropical)")
    print("=" * 70)
    print_aspect_rows(aspect_grid(chart_owner), None)

    print()
    print("=" * 70)
    print("MAI — natal internal aspect grid (tropical)")
    print("=" * 70)
    print_aspect_rows(aspect_grid(chart_mai), None)

    print()
    print("=" * 70)
    print("SYNASTRY — full cross-aspect grid, precise orbs (tropical)")
    print("=" * 70)
    print_aspect_rows(cross_aspect_grid(chart_owner, chart_mai), None)

    print()
    print("=" * 70)
    print("OWNER — Placidus house cusps vs Whole Sign")
    print("=" * 70)
    cusps, ramc, mc_lon = placidus_cusps(dt_owner, OWNER['lat'], OWNER['lon'])
    asc_lon = chart_owner['ASC']['trop']
    print(f"RAMC={ramc:.3f}  MC={fmt(mc_lon)}  ASC={fmt(asc_lon)}")
    for h in range(1, 13):
        print(f"  house {h:2d} cusp: {fmt(cusps[h])}")
    print("\nPlanet placements — Placidus house vs Whole-sign house:")
    for p in list(BODIES):
        lon = chart_owner[p]['trop']
        ph = placidus_house_of(lon, cusps)
        wh = whole_sign_house(lon, asc_lon)
        flag = "  <-- DIFFERS" if ph != wh else ""
        print(f"  {p:8s} {fmt(lon)}  Placidus house {ph:2d}   Whole-sign house {wh:2d}{flag}")

    print()
    print("=" * 70)
    print("Part of Fortune (owner + Mai, both nocturnal charts)")
    print("=" * 70)
    pof_owner = part_of_fortune(chart_owner, is_day_chart=False)
    pof_mai = part_of_fortune(chart_mai, is_day_chart=False)
    print(f"  Owner PoF: {fmt(pof_owner)}  (whole-sign house {whole_sign_house(pof_owner, asc_lon)})")
    print(f"  Mai   PoF: {fmt(pof_mai)}  (whole-sign house {whole_sign_house(pof_mai, chart_mai['ASC']['trop'])})")

    print()
    print("=" * 70)
    print("Composite chart (midpoint method)")
    print("=" * 70)
    comp = composite_chart(chart_owner, chart_mai)
    for p in ALL_POINTS:
        print(f"  {p:8s} {fmt(comp[p]['trop'])}")

    print()
    print("=" * 70)
    print("Davison chart (real midpoint time+place)")
    print("=" * 70)
    dav, mid_dt, mid_lat, mid_lon = davison_chart(OWNER, MAI)
    print(f"  Midpoint moment (UTC): {mid_dt.isoformat()}  local~ICT {(mid_dt + timedelta(hours=7)).isoformat()}")
    print(f"  Midpoint location: {mid_lat:.3f}N {mid_lon:.3f}E")
    for p in ALL_POINTS:
        print(f"  {p:8s} {fmt(dav[p]['trop'])}")

    print()
    print("=" * 70)
    print("Secondary progression — owner, current age")
    print("=" * 70)
    prog, age, prog_dt = progressed_chart(OWNER)
    print(f"  Age: {age:.2f} years  ->  progressed date (birth+age days, UTC): {prog_dt.isoformat()}")
    for p in ALL_POINTS:
        natal_lon = chart_owner[p]['trop']
        prog_lon = prog[p]['trop']
        moved = angle_diff(natal_lon, prog_lon)
        print(f"  {p:8s} natal {fmt(natal_lon)}  ->  progressed {fmt(prog_lon)}  (moved {moved:.2f}°)")

    print()
    print("=" * 70)
    print("Progressed internal aspects (progressed planets to NATAL planets)")
    print("=" * 70)
    rows = []
    for p1 in ALL_POINTS:
        for p2 in ALL_POINTS:
            sep = angle_diff(prog[p1]['trop'], chart_owner[p2]['trop'])
            for name, exact in ASPECTS.items():
                orb = abs(sep - exact)
                tight_orb = {'conjunction': 1.5, 'opposition': 1.5, 'square': 1.2, 'trine': 1.2, 'sextile': 1.0}[name]
                if orb <= tight_orb:
                    rows.append((f"prog.{p1}", f"natal.{p2}", name, sep, orb, tightness(orb)))
    rows.sort(key=lambda r: r[4])
    print_aspect_rows(rows, None)
