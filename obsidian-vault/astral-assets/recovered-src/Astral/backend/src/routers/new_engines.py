"""Routers for the 12 new engines — thin wrappers over services."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.hellenistic_timelords_service import compute_timelords
from src.services.ashtakavarga_service import ashtakavarga_report
from src.services.arabic_lots_service import compute_lots
from src.services.draconic_harmonic_service import (
    draconic_report, harmonics_report,
)
from src.services.astrocartography_service import (
    score_relocation, compare_cities,
)
from src.services.mahataksa_service import compute_mahataksa, lucky_numbers
from src.services.jaimini_service import compute_jaimini
from src.services.prashna_service import compute_prashna
from src.services.qmdj_service import compute_qmdj
from src.services.daliuren_service import compute_daliuren
from src.services.flying_stars_service import compute_flying_stars
from src.services.solar_arc_service import solar_arc_progressions
from src.services.fusion_transparency import compute_fusion_evidence
from src.services.rectification_tournament import rectification_tournament
from src.services.uranian_service import (
    tnp_longitudes, uranian_report,
)
from src.services.triple_activation import triple_activation_windows
from src.services.kp_service import kp_event_filter
from src.services.sa_rectifier import rectify_sa_convergence
from src.services.kakshya_service import transit_micro_windows
from src.services.parans_service import brady_parans
from src.services.genekeys_service import gene_keys_profile, gene_key_for


class BirthIn(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 7.0


def _chart_bodies(b: BirthIn) -> tuple[dict, dict]:
    d = datetime.fromisoformat(f"{b.date}T{b.time}:00")
    utc = datetime.utcfromtimestamp(d.replace(
        tzinfo=None).timestamp() - b.tz * 3600)
    c = compute_chart("x", utc.date(), utc.time(), tz_offset_hours=0,
                      lat=b.lat, lon=b.lon)
    bodies = {x["body"]: float(x["absolute_deg"]) for x in c["bodies"]}
    asc = float(c["ascendant"]["absolute_deg"])
    return bodies, {"asc": asc}


# ── Hellenistic ──────────────────────────────────────────────────────
tr = APIRouter()


@tr.post("/zr")
def zr(b: BirthIn, lot_spirit_lon: float, query_age: int | None = None):
    bodies, ang = _chart_bodies(b)
    return compute_timelords(ang["asc"], lot_spirit_lon,
                             (lot_spirit_lon + 180) % 360,
                             f"{b.date}T{b.time}", b.tz, query_age)


# ── Ashtakavarga ─────────────────────────────────────────────────────
av = APIRouter()


@av.post("/report")
def av_report(b: BirthIn):
    bodies, _ = _chart_bodies(b)
    return ashtakavarga_report(bodies)


# ── Arabic Lots ──────────────────────────────────────────────────────
al = APIRouter()


@al.post("/all")
def lots_all(b: BirthIn, is_day_chart: bool = True):
    bodies, ang = _chart_bodies(b)
    return compute_lots(bodies, ang["asc"], is_day_chart)


# ── Draconic / Harmonics ────────────────────────────────────────────
dh = APIRouter()


@dh.post("/draconic")
def draconic(b: BirthIn):
    bodies, _ = _chart_bodies(b)
    from datetime import datetime as dt
    birth_dt = dt.fromisoformat(f"{b.date}T{b.time}:00") - \
        timedelta(hours=b.tz)
    jd = birth_dt.toordinal() + 1721424.5
    return draconic_report(bodies, jd)


@dh.post("/harmonics")
def harmonics(b: BirthIn):
    bodies, _ = _chart_bodies(b)
    return harmonics_report(bodies)


# ── Astro-Cartography ───────────────────────────────────────────────
acg = APIRouter()


class RelocIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    natal_lat: float = 13.7563
    natal_lon: float = 100.5018
    tz: float = 7.0
    city: str | None = None
    custom_lat: float | None = None
    custom_lon: float | None = None


@acg.post("/score")
def reloc_score(r: RelocIn) -> dict:
    try:
        return score_relocation(
            f"{r.birth_date}T{r.birth_time}", r.natal_lat, r.natal_lon,
            r.tz, city_key=r.city, custom_lat=r.custom_lat,
            custom_lon=r.custom_lon)
    except ValueError as e:
        raise HTTPException(400, str(e))


@acg.get("/cities")
def list_cities() -> dict:
    from src.services.astrocartography_service import CITIES
    return {k: {kk: v[kk] for kk in ("th", "en", "lat", "lon")}
            for k, v in CITIES.items()}


@acg.post("/rank")
def rank_cities(b: BirthIn, cities: list[str] | None = None) -> list[dict]:
    return compare_cities(f"{b.date}T{b.time}", b.lat, b.lon, b.tz, cities)


# ── Maha Taksa + Thai numerology ────────────────────────────────────
mt = APIRouter()


@mt.get("/period")
def mahataksa_period(birth_date: str, query_date: str | None = None) -> dict:
    return compute_mahataksa(birth_date, query_date)


@mt.get("/lucky-numbers")
def lucky(name: str, birthday_ddmm: str) -> dict:
    return lucky_numbers(name, birthday_ddmm)


# ── Jaimini (needs sidereal bodies — reuse vedic conversion) ────────
jm = APIRouter()


@jm.post("/report")
def jaimini_report(b: BirthIn) -> dict:
    from src.services.vedic_service import _sidereal
    from datetime import datetime as dt, timedelta
    naive = dt.fromisoformat(f"{b.date}T{b.time}:00")
    utc = naive - timedelta(hours=b.tz)
    c = compute_chart("jaimini", utc.date(), utc.time(), tz_offset_hours=0,
                      lat=b.lat, lon=b.lon)
    sid = {x["body"]: _sidereal(float(x["absolute_deg"]), utc)
           for x in c["bodies"]}
    asc_sid = _sidereal(float(c["ascendant"]["absolute_deg"]), utc)
    return compute_jaimini(sid, asc_sid)


# ── Prashna ─────────────────────────────────────────────────────────
pr = APIRouter()


class PrashnaIn(BaseModel):
    question_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    question_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 7.0
    category: str
    question_text: str = ""


@pr.post("/ask")
def prashna_ask(r: PrashnaIn) -> dict:
    try:
        return compute_prashna(r.question_date, r.question_time, r.lat,
                               r.lon, r.tz, r.category, r.question_text)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── QMDJ ────────────────────────────────────────────────────────────
qm = APIRouter()


class QmdjIn(BaseModel):
    year: int; month: int; day: int; hour: int; minute: int = 0
    tz: float = 7.0; intent: str = "career"


@qm.post("/chart")
def qmdj_chart(r: QmdjIn) -> dict:
    local = datetime(r.year, r.month, r.day, r.hour, r.minute)
    return compute_qmdj(local, r.tz, r.intent)


# ── Da Liu Ren ──────────────────────────────────────────────────────
dlr = APIRouter()


class DlrIn(BaseModel):
    year: int; month: int; day: int; hour: int; minute: int = 0
    intent: str = "decision"


@dlr.post("/reading")
def dlr_reading(r: DlrIn) -> dict:
    return compute_daliuren(datetime(r.year, r.month, r.day, r.hour, r.minute),
                            r.intent)


# ── Flying Stars ────────────────────────────────────────────────────
fs = APIRouter()


class FsIn(BaseModel):
    build_year: int = Field(ge=1864, le=2100)
    facing_degrees: float = Field(ge=0, lt=360)


@fs.post("/chart")
def fs_chart(r: FsIn) -> dict:
    try:
        return compute_flying_stars(r.build_year, r.facing_degrees)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── Solar Arc ───────────────────────────────────────────────────────
sa = APIRouter()


class SolarArcIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 7.0
    target_age_years: float | None = Field(default=None, ge=0, le=120)
    target_date_iso: str | None = None


@sa.post("/progressions")
def solar_arc(r: SolarArcIn) -> dict:
    return solar_arc_progressions(
        f"{r.birth_date}T{r.birth_time}", r.lat, r.lon, r.tz,
        target_age_years=r.target_age_years,
        target_date_iso=r.target_date_iso)


# ── Fusion transparency ─────────────────────────────────────────────
ft = APIRouter()


class FuseIn(BaseModel):
    name: str = "user"
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 7.0


@ft.post("/evidence")
def fusion_evidence(r: FuseIn) -> dict:
    return compute_fusion_evidence(
        {"name": r.name, "date": __import__("datetime").date.fromisoformat(r.date),
         "time": __import__("datetime").datetime.strptime(r.time, "%H:%M").time()},
        lat=r.lat, lon=r.lon, tz_offset_hours=r.tz)


# ── Rectification tournament ────────────────────────────────────────
rt = APIRouter()


class RectIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    stated_time_local: str = Field(pattern=r"^\d{2}:\d{2}$")
    natal_lat: float = 13.7563
    natal_lon: float = 100.5018
    tz: float = 7.0
    events: list[dict] = Field(min_length=1, max_length=20)
    window_hours: int = Field(default=6, ge=1, le=12)
    step_minutes: int = Field(default=10, ge=5, le=60)


@rt.post("/run")
def rect_run(r: RectIn) -> dict:
    try:
        return rectification_tournament(
            r.birth_date, r.stated_time_local, r.tz, r.natal_lat,
            r.natal_lon, r.events, r.window_hours, r.step_minutes)
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── Uranian TNP ─────────────────────────────────────────────────────
ur = APIRouter()


@ur.get("/tnp")
def tnp_now(date_iso: str = None) -> dict:
    from datetime import datetime as _dt
    d = _dt.fromisoformat(date_iso) if date_iso else _dt.now(timezone.utc)
    return {"system": "uranian-tnp", "positions": tnp_longitudes(d)}


class UranianIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    tz: float = 7.0
    query_date_iso: str | None = None


@ur.post("/report")
def uranian_report_ep(r: UranianIn) -> dict:
    from src.services.chart_service import compute_chart as _cc
    from datetime import datetime as _dt, timedelta as _td
    naive = _dt.fromisoformat(f"{r.birth_date}T{r.birth_time}:00")
    utc = naive - _td(hours=r.tz)
    c = _cc("ur", utc.date(), utc.time(), tz_offset_hours=0,
            lat=13.7563, lon=100.5018)
    bodies = {x["body"]: float(x["absolute_deg"]) for x in c["bodies"]}
    return uranian_report(bodies, f"{r.birth_date}T{r.birth_time}", r.tz,
                          r.query_date_iso)


# ── Triple activation + KP (precision stack) ─────────────────────────
ta = APIRouter()


class TripleIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 7.0
    category: str
    scan_days: int = Field(default=365, ge=30, le=730)


@ta.post("/windows")
def triple_windows(r: TripleIn) -> dict:
    from datetime import datetime as _dt, timezone as _tz
    try:
        return triple_activation_windows(
            "user", r.birth_date, r.birth_time, r.tz, r.lat, r.lon,
            category=r.category, now_utc=_dt.now(_tz.utc),
            scan_days=r.scan_days)
    except ValueError as e:
        raise HTTPException(400, str(e))


kp = APIRouter()


class KpIn(BaseModel):
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 0.0  # treat input as UTC for chart computation parity
    category: str


@kp.post("/event-filter")
def kp_filter(r: KpIn) -> dict:
    from datetime import datetime as _dt, timedelta as _td
    from src.services.chart_service import compute_chart as _cc
    naive = _dt.fromisoformat(f"{r.date}T{r.time}:00")
    c = _cc("kpf", naive.date(), naive.time(), tz_offset_hours=0,
            lat=r.lat, lon=r.lon)
    return kp_event_filter(c, naive.replace(tzinfo=None), r.category)


cm = APIRouter()


@cm.get("/numerology")
def chomangkala_v2(first_name: str, last_name: str = "",
                   birth_day: int | None = None) -> dict:
    from src.services.chomangkala_v2 import chomangkala_full
    return chomangkala_full(first_name, last_name, birth_day)


bn = APIRouter()


@bn.get("/run")
def bench_run() -> dict:
    from src.services.astral_bench import BenchCase, run_bench
    cases = [BenchCase("c1", "1990-05-19", "05:45", 13.75, 100.52),
             BenchCase("c2", "1997-08-18", "22:32", 13.86, 100.52),
             BenchCase("c3", "2000-01-01", "12:00", 13.75, 100.52)]
    return run_bench(cases)


# ── Precision batch 2 ────────────────────────────────────────────────
sar = APIRouter()


class SarIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    stated_time_local: str = Field(pattern=r"^\d{2}:\d{2}$")
    tz: float = 7.0
    natal_lat: float = 13.7563
    natal_lon: float = 100.5018
    events: list[dict] = Field(min_length=1, max_length=20)
    window_hours: int = Field(default=4, ge=1, le=12)
    step_minutes: int = Field(default=5, ge=5, le=60)


@sar.post("/rectify")
def sa_rectify(r: SarIn) -> dict:
    try:
        return rectify_sa_convergence(
            r.birth_date, r.stated_time_local, r.tz,
            r.natal_lat, r.natal_lon, r.events,
            r.window_hours, r.step_minutes)
    except ValueError as e:
        raise HTTPException(400, str(e))


kk = APIRouter()


class KakIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    lat: float = 13.7563
    lon: float = 100.5018
    tz: float = 0.0
    planet: str = "Jupiter"
    scan_start: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    scan_days: int = Field(default=365, ge=30, le=730)


@kk.post("/windows")
def kak_windows(r: KakIn) -> dict:
    from datetime import datetime as _dt, timedelta as _td
    from src.services.chart_service import compute_chart as _cc
    naive = _dt.fromisoformat(f"{r.birth_date}T{r.birth_time}:00")
    c = _cc("kak", naive.date(), naive.time(), tz_offset_hours=0,
            lat=r.lat, lon=r.lon)
    bodies = {b["body"]: float(b["absolute_deg"]) for b in c["bodies"]}
    asc = float(c["ascendant"]["absolute_deg"])
    return transit_micro_windows(bodies, asc, r.planet,
                                 r.scan_start, r.scan_days)


br = APIRouter()


class ParanIn(BaseModel):
    birth_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    birth_time: str = Field(pattern=r"^\d{2}:\d{2}$")
    tz: float = 7.0
    lat: float = 13.7563
    lon: float = 100.5018
    orb_minutes: int = Field(default=2, ge=1, le=10)


@br.post("/parans")
def brady_parans_ep(r: ParanIn) -> dict:
    return brady_parans(r.birth_date, r.birth_time, r.tz,
                        r.lat, r.lon, r.orb_minutes)


rv = APIRouter()


class ReelIn(BaseModel):
    name: str = ""
    spread: str = "single"
    lang: str = "th"
    out_dir: str | None = None


@rv.post("/script")
def reel_script(r: ReelIn) -> dict:
    from src.services.reel_video import build_reel_script
    return build_reel_script(r.name or "draw", r.spread, None, r.lang)


@rv.post("/render")
def reel_render(r: ReelIn) -> dict:
    from src.services.reel_video import generate_reel
    out = r.out_dir or os.path.join(os.path.expanduser("~"),
                                    "astral-reels", (r.name or "draw"))
    os.makedirs(out, exist_ok=True)
    return generate_reel(r.name, out, r.spread, None, r.lang)


# ── Gene Keys ────────────────────────────────────────────────────────
gk = APIRouter()


class GKIn(BaseModel):
    sun_lon: float = Field(ge=0, lt=360)
    earth_lon: float | None = Field(default=None, ge=0, lt=360)
    moon_lon: float | None = Field(default=None, ge=0, lt=360)
    asc_lon: float | None = Field(default=None, ge=0, lt=360)


@gk.post("/profile")
def genekeys_profile_ep(r: GKIn) -> dict:
    from src.services.genekeys_service import gene_keys_profile
    return gene_keys_profile(r.sun_lon, r.earth_lon,
                             r.moon_lon, r.asc_lon)


@gk.get("/gate")
def gate_for(lon: float) -> dict:
    from src.services.genekeys_service import gene_key_for
    return gene_key_for(lon % 360)


