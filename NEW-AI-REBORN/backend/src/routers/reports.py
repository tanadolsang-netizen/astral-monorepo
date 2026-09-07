"""Report endpoints — รวมผลดวงเป็น PDF (ไทย/อังกฤษ)."""



import os
import tempfile
from datetime import date, time

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.services.pdf_agent_th import (
    build_synastry_sections as build_synastry_sections_th,
    build_natal_sections as build_natal_sections_th,
    build_composite_sections as build_composite_sections_th,
    build_transit_sections as build_transit_sections_th,
    build_muhurta_sections as build_muhurta_sections_th,
)
from src.services.pdf_agent_en import (
    build_synastry_sections as build_synastry_sections_en,
    build_natal_sections as build_natal_sections_en,
    build_composite_sections as build_composite_sections_en,
    build_transit_sections as build_transit_sections_en,
    build_muhurta_sections as build_muhurta_sections_en,
)
from src.services.chart_service import compute_chart, compute_dual_chart
from src.services.premium_pdf_service import biwheel_svg
from src.services.pdf_renderer import render_brochure_v2


# Simple in-memory chart cache for a single request lifecycle.
# Key: (name, date, time, tz, lat, lon, system)
_CHART_CACHE: dict[tuple, dict] = {}


def _cached_compute_chart(**kwargs) -> dict:
    key = (
        kwargs.get("name", ""),
        str(kwargs.get("date", "")),
        str(kwargs.get("time", "")),
        float(kwargs.get("tz_offset_hours", 7)),
        float(kwargs.get("lat", 0)),
        float(kwargs.get("lon", 0)),
        kwargs.get("system", "tropical"),
    )
    if key not in _CHART_CACHE:
        _CHART_CACHE[key] = compute_chart(**kwargs)
    return _CHART_CACHE[key]


def _syn_builders(lang: str = "th"):
    return build_synastry_sections_th if _lang(lang) == "th" else build_synastry_sections_en


def _natal_builders(lang: str = "th"):
    return build_natal_sections_th if _lang(lang) == "th" else build_natal_sections_en


def _comp_builders(lang: str = "th"):
    return build_composite_sections_th if _lang(lang) == "th" else build_composite_sections_en


def _transit_builders(lang: str = "th"):
    return build_transit_sections_th if _lang(lang) == "th" else build_transit_sections_en


def _muhurta_builders(lang: str = "th"):
    return build_muhurta_sections_th if _lang(lang) == "th" else build_muhurta_sections_en


router = APIRouter(tags=["reports"])


class NatalPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    system: str = Field(default="tropical", pattern="^(tropical|sidereal)$")
    lang: str = Field(default="th", max_length=10)


class SynastryPayload(BaseModel):
    a: NatalPayload
    b: NatalPayload
    spread: str = Field(default="three_card", max_length=40)
    lang: str = Field(default="th", max_length=10)


class ReportPdfResponse(BaseModel):
    ok: bool
    file: str
    sections: int


class LegacyPdfRequest(BaseModel):
    person_name: str = Field(..., max_length=120)
    lang: str = Field(default="th", max_length=10)
    sections: list[dict]
    theme_hint: str = Field(default="", max_length=120)


class VedicReportPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    ayanamsa: str = Field(default="lahiri", max_length=40)


class BaZiReportPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)


class HumanDesignReportPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)


class ZiWeiReportPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    gender: str = Field(default="female", max_length=20)


class GrandSummaryPayload(BaseModel):
    name: str = Field(..., max_length=120)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    lat: float = Field(default=13.8591, ge=-90, le=90)
    lon: float = Field(default=100.5217, ge=-180, le=180)
    lang: str = Field(default="th", max_length=10)
    partner_name: str = Field(default="", max_length=120)
    partner_date: date | None = None
    partner_time: time | None = None
    partner_tz_offset_hours: float = Field(default=7.0, ge=-12, le=14)
    partner_lat: float | None = None
    partner_lon: float | None = None
    muhurta_action: str = Field(default="", max_length=50)
    muhurta_start: str = Field(default="", max_length=20)
    muhurta_days: int = Field(default=30, ge=1, le=365)
    muhurta_top_n: int = Field(default=3, ge=1, le=10)


def _chart_from_payload(p: dict | NatalPayload):
    if isinstance(p, dict):
        p = NatalPayload(**p)
    return _cached_compute_chart(
        name=p.name,
        date=p.date,
        time=p.time,
        tz_offset_hours=p.tz_offset_hours,
        lat=p.lat,
        lon=p.lon,
        system=p.system,
    )


def _lang(lang: str = "th") -> str:
    return "en" if str(lang).lower().startswith("en") else "th"


def _pick_greek_art(sections: list[dict]) -> dict[int, str]:
    """Return section_art mapping based on section content/theme."""
    art_dir = os.path.join(r"D:\AI\NEW-AI-REBORN\assets\art")
    art = {
        "venus_mars": os.path.join(art_dir, "venus_mars.jpg"),
        "diana": os.path.join(art_dir, "diana.jpg"),
        "cupid_psyche": os.path.join(art_dir, "cupid_psyche.jpg"),
    }

    def _theme(text: str) -> str:
        t = text.lower()
        if any(k in t for k in ["💌 คำแนะนำ", "oracle", "advice", "ward", "passion", "heat", " sexually", " desire"]):
            return "venus_mars"
        if any(k in t for k in ["ภาพรวม", "overview", "sun", "moon", "ambition", "quiet confidence", "destiny", " language", " meeting"]):
            return "cupid_psyche"
        if any(k in t for k in ["✨ พันธะ", "bonds", "hold", "communication", "mercury", "emotional", " loyalty", " trust"]):
            return "diana"
        if any(k in t for k in ["⚡ จุด", "edges", "grow", "friction", "mars", " tension", " fight", " anger"]):
            return "venus_mars"
        if any(k in t for k in ["🔮 คะแนน", "score", "compatibility", "numbers", " worth", " failure"]):
            return "cupid_psyche"
        return ""

    result = {}
    for idx, sec in enumerate(sections, start=1):
        title = sec.get("title") or ""
        lines = " ".join(sec.get("lines", []))
        theme = _theme(title + " " + lines)
        if theme:
            result[idx] = art[theme]
        else:
            fallback = [art["cupid_psyche"], art["diana"], art["venus_mars"], art["cupid_psyche"], art["diana"]]
            result[idx] = fallback[(idx - 1) % len(fallback)]

    return result


@router.post("/report/synastry-dual")
def synastry_report_dual(req: SynastryPayload):
    try:
        a_dual = compute_dual_chart(
            name=req.a.name,
            date=req.a.date,
            time=req.a.time,
            tz_offset_hours=req.a.tz_offset_hours,
            lat=req.a.lat,
            lon=req.a.lon,
        )
        b_dual = compute_dual_chart(
            name=req.b.name,
            date=req.b.date,
            time=req.b.time,
            tz_offset_hours=req.b.tz_offset_hours,
            lat=req.b.lat,
            lon=req.b.lon,
        )

        sections, tarot_html, tarot_title = _syn_builders(req.lang)(
            name_a=req.a.name,
            name_b=req.b.name,
            chart_a=_cached_compute_chart(name=req.a.name, date=req.a.date, time=req.a.time, tz_offset_hours=req.a.tz_offset_hours, lat=req.a.lat, lon=req.a.lon, system=req.a.system),
            chart_b=_cached_compute_chart(name=req.b.name, date=req.b.date, time=req.b.time, tz_offset_hours=req.b.tz_offset_hours, lat=req.b.lat, lon=req.b.lon, system=req.b.system),
            spread=req.spread,
        )

        # build biwheel using tropical half of the dual charts
        a_deg = {b["body"]: float(b["absolute_deg"]) for b in a_dual["tropical"]["bodies"]}
        b_deg = {b["body"]: float(b["absolute_deg"]) for b in b_dual["tropical"]["bodies"]}
        a_deg["ASC"] = float(a_dual["tropical"]["ascendant"]["absolute_deg"])
        b_deg["ASC"] = float(b_dual["tropical"]["ascendant"]["absolute_deg"])
        wheel = biwheel_svg({k: v for k, v in a_deg.items() if k != "ASC"}, {k: v for k, v in b_deg.items() if k != "ASC"}, name_a=req.a.name, name_b=req.b.name)

        # dynamic Greek mythology artwork based on section content
        art = _pick_greek_art(sections)

        out_dir = tempfile.mkdtemp(prefix="astral_synastry_")
        out_path = os.path.join(out_dir, f"astral-synastry-dual-{os.getpid()}.pdf")
        render_brochure_v2(
            sections,
            out_path,
            person_name=f"{req.a.name} ♥ {req.b.name}",
            lang=req.lang,
            theme_hint="venus taurus libra",
            biwheel=wheel,
            section_art=art,
            raw_section=tarot_html,
            raw_title=tarot_title,
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/synastry")
def synastry_report(req: SynastryPayload):
    try:
        sections, tarot_html, tarot_title = _syn_builders(req.lang)(
            name_a=req.a.name,
            name_b=req.b.name,
            chart_a=_cached_compute_chart(name=req.a.name, date=req.a.date, time=req.a.time, tz_offset_hours=req.a.tz_offset_hours, lat=req.a.lat, lon=req.a.lon, system=req.a.system),
            chart_b=_cached_compute_chart(name=req.b.name, date=req.b.date, time=req.b.time, tz_offset_hours=req.b.tz_offset_hours, lat=req.b.lat, lon=req.b.lon, system=req.b.system),
            spread=req.spread,
        )

        a_chart = _chart_from_payload(req.a)
        b_chart = _chart_from_payload(req.b)

        # build biwheel
        a_deg = {b["body"]: float(b["absolute_deg"]) for b in a_chart["bodies"]}
        b_deg = {b["body"]: float(b["absolute_deg"]) for b in b_chart["bodies"]}
        a_deg["ASC"] = float(a_chart["ascendant"]["absolute_deg"])
        b_deg["ASC"] = float(b_chart["ascendant"]["absolute_deg"])
        wheel = biwheel_svg({k: v for k, v in a_deg.items() if k != "ASC"}, {k: v for k, v in b_deg.items() if k != "ASC"}, name_a=req.a.name, name_b=req.b.name)

        # dynamic Greek mythology artwork based on section content
        art = _pick_greek_art(sections)

        out_dir = tempfile.mkdtemp(prefix="astral_synastry_")
        out_path = os.path.join(out_dir, f"astral-synastry-{os.getpid()}.pdf")
        render_brochure_v2(
            sections,
            out_path,
            person_name=f"{req.a.name} ♥ {req.b.name}",
            lang=req.lang,
            theme_hint="venus taurus libra",
            biwheel=wheel,
            section_art=art,
            raw_section=tarot_html,
            raw_title=tarot_title,
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/natal")
def natal_report(req: NatalPayload):
    try:
        chart = _chart_from_payload(req)
        sections = _natal_builders(req.lang)(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_natal_")
        out_path = os.path.join(out_dir, f"astral-natal-{os.getpid()}.pdf")

        render_brochure_v2(
            sections,
            out_path,
            person_name=req.name,
            lang=req.lang,
            theme_hint="sun leo moon libra asc taurus",
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/composite")
def composite_report(req: SynastryPayload):
    try:
        a_chart = _chart_from_payload(req.a)
        b_chart = _chart_from_payload(req.b)
        sections = _comp_builders(req.lang)(req.a.name, req.b.name, a_chart, b_chart)

        out_dir = tempfile.mkdtemp(prefix="astral_composite_")
        out_path = os.path.join(out_dir, f"astral-composite-{os.getpid()}.pdf")

        render_brochure_v2(
            sections,
            out_path,
            person_name=f"{req.a.name} + {req.b.name}",
            lang=req.lang,
            theme_hint="composite midpoint",
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/transit")
def transit_report(req: NatalPayload):
    try:
        chart = _chart_from_payload(req)
        from src.services.fusion_engine import compute_transit_hits
        transits = compute_transit_hits(chart)
        sections = _transit_builders(req.lang)(req.name, chart, transits)

        out_dir = tempfile.mkdtemp(prefix="astral_transit_")
        out_path = os.path.join(out_dir, f"astral-transit-{os.getpid()}.pdf")

        render_brochure_v2(
            sections,
            out_path,
            person_name=req.name,
            lang=req.lang,
            theme_hint="transit now",
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/muhurta")
def muhurta_report(req: dict):
    from src.services.muhurta_service import find_windows
    try:
        action = req.get("action", "marriage")
        start_date = req.get("start_date", "")
        days = int(req.get("days", 60))
        top_n = int(req.get("top_n", 3))
        lat = float(req.get("lat", 13.7565))
        lon = float(req.get("lon", 100.5018))
        tz_offset_hours = float(req.get("tz_offset_hours", 7.0))

        windows = find_windows(
            action=action,
            start_date=start_date,
            days=days,
            lat=lat,
            lon=lon,
            tz_offset_hours=tz_offset_hours,
            top_n=top_n,
        )
        sections = _muhurta_builders(req.lang)(action, windows.get("windows", []))

        out_dir = tempfile.mkdtemp(prefix="astral_muhurta_")
        out_path = os.path.join(out_dir, f"astral-muhurta-{os.getpid()}.pdf")

        render_brochure_v2(
            sections,
            out_path,
            person_name=f"muhurta {action}",
            lang=req.lang,
            theme_hint="electional",
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/health")
def reports_health():
    return {
        "ok": True,
        "reports": [
            "natal", "synastry", "synastry-dual", "composite", "transit", "muhurta",
            "vedic", "bazi", "human-design", "ziwei", "grand-summary",
            "brochure/natal", "brochure/composite", "brochure/transit",
            "brochure/muhurta", "brochure/synastry", "brochure/synastry-dual",
            "brochure/vedic", "brochure/bazi", "brochure/human-design", "brochure/ziwei"
        ],
    }


@router.post("/report/vedic")
def vedic_report(req: VedicReportPayload):
    try:
        from src.services.vedic_service import compute_vedic
        birth_dt = f"{req.date.isoformat()}T{req.time.isoformat()}"
        chart = compute_vedic(
            birth_datetime_local=birth_dt,
            lat=req.lat,
            lon=req.lon,
            tz_offset_hours=req.tz_offset_hours,
            person_name=req.name,
        )
        sections = _vedic_sections(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_vedic_")
        out_path = os.path.join(out_dir, f"astral-vedic-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang=req.lang, theme_hint="vedic")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/bazi")
def bazi_report(req: BaZiReportPayload):
    try:
        from src.services.bazi_service import four_pillars
        chart = four_pillars(req.date, req.time)
        sections = _bazi_sections(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_bazi_")
        out_path = os.path.join(out_dir, f"astral-bazi-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang=req.lang, theme_hint="bazi")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/human-design")
def human_design_report(req: HumanDesignReportPayload):
    try:
        from src.services.chart_service import compute_chart
        from src.services.grand.human_design import compute_human_design
        natal = _cached_compute_chart(
            name=req.name,
            date=req.date,
            time=req.time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            system="tropical",
        )
        chart = compute_human_design(natal_chart=natal)
        sections = _human_design_sections(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_hd_")
        out_path = os.path.join(out_dir, f"astral-hd-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang=req.lang, theme_hint="human design")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/ziwei")
def ziwei_report(req: ZiWeiReportPayload):
    try:
        from src.services.grand.ziwei import compute_ziwei
        chart = compute_ziwei(req.date, req.time)
        sections = _ziwei_sections(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_ziwei_")
        out_path = os.path.join(out_dir, f"astral-ziwei-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang=req.lang, theme_hint="ziwei")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/report/grand-summary")
def grand_summary_report(req: GrandSummaryPayload):
    try:
        from src.services.tarot_downloader import ensure_deck_ready
        ensure_deck_ready(background=True)
        from src.services.grand.grand_fusion import compute_grand_fusion
        payload = compute_grand_fusion(req.name, lang=req.lang)
        sections = _grand_sections(payload)

        # optional synastry with partner
        try:
            from datetime import date, time
            from src.services.chart_service import compute_chart
            d = date.fromisoformat(payload.get("person", {}).get("birth", {}).get("date", "1997-05-19"))
            t = time.fromisoformat(payload.get("person", {}).get("birth", {}).get("time", "05:45:00"))
            tz = float(payload.get("person", {}).get("birth", {}).get("tz_offset_hours", 7))
            lat = float(payload.get("person", {}).get("birth", {}).get("lat", 13.36))
            lon = float(payload.get("person", {}).get("birth", {}).get("lon", 100.98))
            a_chart = _cached_compute_chart(name=req.name, date=d, time=t, tz_offset_hours=tz, lat=lat, lon=lon)
            if req.partner_name and req.partner_date and req.partner_time and req.partner_lat is not None and req.partner_lon is not None:
                b_chart = _cached_compute_chart(name=req.partner_name, date=req.partner_date, time=req.partner_time, tz_offset_hours=req.partner_tz_offset_hours, lat=req.partner_lat, lon=req.partner_lon)
            else:
                b_chart = a_chart
            syn_sections, tarot_html, tarot_title = _syn_builders(req.lang)(req.name, req.partner_name or req.name, a_chart, b_chart, "three_card")
            sections.extend(syn_sections)
            if tarot_html:
                sections.append({"title": tarot_title, "lines": [tarot_html], "html": True})
        except Exception:
            pass

        if req.muhurta_action:
            try:
                from src.services.muhurta_service import find_windows
                m = find_windows(
                    action=req.muhurta_action,
                    start_date=req.muhurta_start or payload.get("person", {}).get("birth", {}).get("date", "1997-05-19"),
                    days=req.muhurta_days,
                    lat=req.lat,
                    lon=req.lon,
                    tz_offset_hours=req.tz_offset_hours,
                    top_n=req.muhurta_top_n,
                )
                windows = m.get("windows", [])[: req.muhurta_top_n]
                if windows:
                    muh_lines = [f"ช่วงมงคลสำหรับ {req.muhurta_action} ในบริเวณ birthplace"]
                    for i, w in enumerate(windows, 1):
                        muh_lines.append(f"อันดับ {i}: {w.get('when_local','-')} — score {w.get('score','-')}")
                        if w.get("reasons_th"):
                            muh_lines.append(f"   เหตุผล: {'; '.join(w['reasons_th'][:2])}")
                    sections.append({"title": f"muhurta — {req.muhurta_action} / เลือกวันมงคล", "lines": muh_lines})
                else:
                    sections.append({"title": f"muhurta — {req.muhurta_action} / เลือกวันมงคล", "lines": ["ไม่พบช่วงมงคลในช่วงนี้", ""]})
            except Exception:
                pass

        out_dir = tempfile.mkdtemp(prefix="astral_grand_")
        out_path = os.path.join(out_dir, f"astral-grand-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang=req.lang, theme_hint="grand summary")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/natal")
def brochure_natal(req: NatalPayload):
    try:
        chart = _chart_from_payload(req)
        sections = _natal_builders(req.lang)(req.name, chart)

        out_dir = tempfile.mkdtemp(prefix="astral_natal_brochure_")
        out_path = os.path.join(out_dir, f"astral-natal-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="natal")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/composite")
def brochure_composite(req: SynastryPayload):
    try:
        a_chart = _chart_from_payload(req.a)
        b_chart = _chart_from_payload(req.b)
        sections = _comp_builders(req.lang)(req.a.name, req.b.name, a_chart, b_chart)

        out_dir = tempfile.mkdtemp(prefix="astral_composite_brochure_")
        out_path = os.path.join(out_dir, f"astral-composite-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=f"{req.a.name} + {req.b.name}", lang="th", theme_hint="composite")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/transit")
def brochure_transit(req: NatalPayload):
    try:
        chart = _chart_from_payload(req)
        from src.services.fusion_engine import compute_transit_hits
        transits = compute_transit_hits(chart)
        sections = _transit_builders(req.lang)(req.name, chart, transits)

        out_dir = tempfile.mkdtemp(prefix="astral_transit_brochure_")
        out_path = os.path.join(out_dir, f"astral-transit-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="transit")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/muhurta")
def brochure_muhurta(req: dict):
    from src.services.muhurta_service import find_windows
    try:
        action = req.get("action", "marriage")
        start_date = req.get("start_date", "")
        days = int(req.get("days", 60))
        top_n = int(req.get("top_n", 3))
        lat = float(req.get("lat", 13.7565))
        lon = float(req.get("lon", 100.5018))
        tz_offset_hours = float(req.get("tz_offset_hours", 7.0))

        windows = find_windows(
            action=action,
            start_date=start_date,
            days=days,
            lat=lat,
            lon=lon,
            tz_offset_hours=tz_offset_hours,
            top_n=top_n,
        )
        sections = _muhurta_builders(req.lang)(action, windows.get("windows", []))

        out_dir = tempfile.mkdtemp(prefix="astral_muhurta_brochure_")
        out_path = os.path.join(out_dir, f"astral-muhurta-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=f"muhurta {action}", lang="th", theme_hint="muhurta")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/synastry")
def brochure_synastry(req: SynastryPayload):
    try:
        a_chart = _chart_from_payload(req.a)
        b_chart = _chart_from_payload(req.b)
        sections, tarot_html, tarot_title = _syn_builders(req.lang)(req.a.name, req.b.name, a_chart, b_chart, req.spread)
        if tarot_html:
            sections.append({"title": tarot_title, "lines": [tarot_html], "html": True})

        out_dir = tempfile.mkdtemp(prefix="astral_synastry_brochure_")
        out_path = os.path.join(out_dir, f"astral-synastry-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=f"{req.a.name} + {req.b.name}", lang="th", theme_hint="synastry")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/synastry-dual")
def brochure_synastry_dual(req: SynastryPayload):
    try:
        a_chart = _chart_from_payload(req.a)
        b_chart = _chart_from_payload(req.b)
        sections, tarot_html, tarot_title = _syn_builders(req.lang)(req.a.name, req.b.name, a_chart, b_chart, req.spread)
        if tarot_html:
            sections.append({"title": tarot_title, "lines": [tarot_html], "html": True})

        out_dir = tempfile.mkdtemp(prefix="astral_synastry_dual_brochure_")
        out_path = os.path.join(out_dir, f"astral-synastry-dual-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=f"{req.a.name} + {req.b.name}", lang="th", theme_hint="synastry dual")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


def _brochure_report(route: str, payload_builder, theme_hint: str):
    req = payload_builder()
    sections = req["sections"]
    out_dir = tempfile.mkdtemp(prefix=f"astral_{route.split('/')[-1]}_")
    out_path = os.path.join(out_dir, f"astral-{route.split('/')[-1]}-{os.getpid()}.pdf")
    render_brochure_v2(sections, out_path, person_name=req.get("person_name",""), lang="th", theme_hint=theme_hint)
    return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))


@router.post("/brochure/vedic")
def brochure_vedic(req: VedicReportPayload):
    try:
        from src.services.vedic_service import compute_vedic
        chart = compute_vedic(birth_datetime_local=f"{req.date.isoformat()}T{req.time.isoformat()}", lat=req.lat, lon=req.lon, tz_offset_hours=req.tz_offset_hours, person_name=req.name)
        sections = _vedic_sections(req.name, chart)
        out_dir = tempfile.mkdtemp(prefix="astral_vedic_brochure_")
        out_path = os.path.join(out_dir, f"astral-vedic-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="vedic")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/bazi")
def brochure_bazi(req: BaZiReportPayload):
    try:
        from src.services.bazi_service import four_pillars
        chart = four_pillars(req.date, req.time)
        sections = _bazi_sections(req.name, chart)
        out_dir = tempfile.mkdtemp(prefix="astral_bazi_brochure_")
        out_path = os.path.join(out_dir, f"astral-bazi-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="bazi")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/human-design")
def brochure_human_design(req: HumanDesignReportPayload):
    try:
        from src.services.chart_service import compute_chart
        from src.services.grand.human_design import compute_human_design
        natal = _cached_compute_chart(name=req.name, date=req.date, time=req.time, tz_offset_hours=req.tz_offset_hours, lat=req.lat, lon=req.lon, system="tropical")
        chart = compute_human_design(natal_chart=natal)
        sections = _human_design_sections(req.name, chart)
        out_dir = tempfile.mkdtemp(prefix="astral_hd_brochure_")
        out_path = os.path.join(out_dir, f"astral-hd-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="human design")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/brochure/ziwei")
def brochure_ziwei(req: ZiWeiReportPayload):
    try:
        from src.services.grand.ziwei import compute_ziwei
        chart = compute_ziwei(req.date, req.time)
        sections = _ziwei_sections(req.name, chart)
        out_dir = tempfile.mkdtemp(prefix="astral_ziwei_brochure_")
        out_path = os.path.join(out_dir, f"astral-ziwei-{os.getpid()}.pdf")
        render_brochure_v2(sections, out_path, person_name=req.name, lang="th", theme_hint="ziwei")
        return ReportPdfResponse(ok=True, file=out_path, sections=len(sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/pdf")
def legacy_pdf(req: LegacyPdfRequest):
    try:
        out_dir = tempfile.mkdtemp(prefix="astral_legacy_")
        out_path = os.path.join(out_dir, f"astral-legacy-{os.getpid()}.pdf")
        render_brochure_v2(
            req.sections,
            out_path,
            person_name=req.person_name,
            lang=req.lang,
            theme_hint=req.theme_hint or "natal",
        )
        return ReportPdfResponse(ok=True, file=out_path, sections=len(req.sections))
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/pdf/download")
def legacy_download(req: LegacyPdfRequest):
    res = legacy_pdf(req)
    return FileResponse(res.file, filename=os.path.basename(res.file))


@router.post("/premium")
def legacy_premium(req: LegacyPdfRequest):
    return legacy_pdf(req)


@router.post("/premium/download")
def legacy_premium_download(req: LegacyPdfRequest):
    res = legacy_pdf(req)
    return FileResponse(res.file, filename=os.path.basename(res.file))


def _vedic_sections(name: str, chart: dict) -> list[dict]:
    interp = chart.get("interpretation") or {}
    th = (interp.get("th") or "").strip()
    zodiac = (chart.get("zodiac_th") or "").strip()

    lines = []
    if zodiac:
        lines.append(zodiac)
    if th:
        lines.append(th)

    if not lines:
        lines = [
            f"ดวงเวทิกาของ {name} เป็นเครื่องมือช่วยเข้าใจสมบัติ spirituality และ vibe พื้นฐานของคุณ",
            f"ข้อมูลดวงจะช่วยระบุจุดแข็ง、จุดอ่อน、และช่วงเวลาที่ดีที่สุดในการทำ things สำคัญ",
        ]

    return [{"title": f"ดวงเวทิก — {name}", "lines": lines}]


def _bazi_sections(name: str, chart: dict) -> list[dict]:
    pillars = chart.get("pillars") or {}
    dm = chart.get("day_master") or {}
    zodiac = (chart.get("zodiac_th") or "").strip()

    year = pillars.get("year") or {}
    month = pillars.get("month") or {}
    day = pillars.get("day") or {}
    hour = pillars.get("hour") or {}

    lines = [
        f"ดูตำแหน่ง four pillars ของ {name} เดือนนี้หมุนไปอย่างกลมกลืน: ปี{_s(year.get('pillar',''))} เป็นรากที่ให้กำเนิดคุณ, เดือน{_s(month.get('pillar',''))} คือช่วงที่โลกเริ่มเห็นความพยายามของคุณ, วันที่{_s(day.get('pillar',''))} คือตัวที่แท้จริงที่painstakingly หล่อหลอม, ชั่วโมง{_s(hour.get('pillar',''))} คือบทสรุปที่ลงท้ายลงในความจริง",
        f"วันนี้เป็น{_s(day.get('animal_th',''))} กับธาตุ{_s(day.get('stem_element_th',''))} — นี่คือetalon ของตัวคุณ คือสิ่งที่rutin ทำให้คนรู้สึกถึง presence โดยไม่ต้องพูด",
        f" estat分析ไม่ใช่บทวิจารณ์ แต่เป็นสะพาน cross-reference ว่าวันใดควรใช้ไฟ ควรใช้ไม้ ควรใช้โลหะ — เมื่ออ่านก็รู้สึกไม่ใช่ future ที่ถูกเขียน แต่คือ track ที่คุณเลือกเดิน",
    ]
    if zodiac:
        lines.append(zodiac)
    return [{"title": f"BaZi — {name}", "lines": lines}]


def _human_design_sections(name: str, chart: dict) -> list[dict]:
    profile = chart.get("profile") or {}
    lines = [
        f"Type: {chart.get('type', '')}",
        f"Authority: {chart.get('authority', '')}",
        f"Profile: {profile.get('profile_name', '')}",
    ]
    centers = chart.get("defined_centers") or []
    if centers:
        lines.append("Centers: " + ", ".join(centers))
    channels = chart.get("defined_channels") or []
    if channels:
        lines.append("Channels: " + ", ".join(channels[:6]))
    gates = chart.get("activated_gates") or []
    if gates:
        lines.append("Gates: " + ", ".join(str(g) for g in gates[:10]))
    return [{"title": f"Human Design — {name}", "lines": lines}]


def _ziwei_sections(name: str, chart: dict) -> list[dict]:
    life = chart.get("life_palace") or {}
    body = chart.get("body_palace") or {}
    lunar = chart.get("lunar") or {}
    lines = [
        f"Life: {life.get('pillar', '')} ({life.get('animal', '')})",
        f"Body: {body.get('pillar', '')} ({body.get('animal', '')})",
        f"Lunar: {lunar.get('year_ganzhi', '')} / {lunar.get('month', '')}-{lunar.get('day', '')}",
    ]
    return [{"title": f"Zi Wei Dou Shu — {name}", "lines": lines}]


def _grand_sections(payload: dict) -> list[dict]:
    from datetime import date, time
    from src.services.chart_service import compute_chart
    from src.services.vedic_service import compute_vedic
    from src.services.bazi_service import four_pillars
    from src.services.grand.human_design import compute_human_design
    from src.services.grand.ziwei import compute_ziwei

    person = payload.get("person", {})
    birth = person.get("birth", {})
    name = person.get("name", "")
    sections = []

    try:
        d = date.fromisoformat(birth.get("date", "1997-05-19"))
        t = time.fromisoformat(birth.get("time", "05:45:00"))
        tz = float(birth.get("tz_offset_hours", 7))
        lat = float(birth.get("lat", 13.36))
        lon = float(birth.get("lon", 100.98))

        chart = _cached_compute_chart(name=name, date=d, time=t, tz_offset_hours=tz, lat=lat, lon=lon)
        vedic = compute_vedic(birth_datetime_local=f"{d.isoformat()}T{t.isoformat()}", lat=lat, lon=lon, tz_offset_hours=tz, person_name=name)
        bazi = four_pillars(d, t)
        hd = compute_human_design(natal_chart=chart)
        zw = compute_ziwei(d, t)

        sections.extend(_vedic_sections(name, vedic))
        sections.extend(_bazi_sections(name, bazi))
        sections.extend(_human_design_sections(name, hd))
        sections.extend(_ziwei_sections(name, zw))
        sections.extend(build_natal_sections_th(name, chart))

        try:
            a_chart = _chart_from_payload({"name": name, "date": d.isoformat(), "time": t.isoformat(), "tz_offset_hours": tz, "lat": lat, "lon": lon})
            if req.partner_name and req.partner_date and req.partner_time and req.partner_lat is not None and req.partner_lon is not None:
                b_chart = _chart_from_payload({"name": req.partner_name, "date": req.partner_date.isoformat(), "time": req.partner_time.isoformat(), "tz_offset_hours": req.partner_tz_offset_hours, "lat": req.partner_lat, "lon": req.partner_lon})
            else:
                b_chart = a_chart
            syn_sections, tarot_html, tarot_title = _syn_builders(req.lang)(name, req.partner_name or name, a_chart, b_chart, "three_card")
            sections.extend(syn_sections)
            if tarot_html:
                sections.append({"title": tarot_title, "lines": [tarot_html], "html": True})
        except Exception:
            pass
    except Exception:
        pass

    r = payload.get("reading", {})
    for key, val in r.items():
        if isinstance(val, dict):
            sub = [f"{k}: {v}" for k, v in val.items() if v]
            if sub:
                sections.append({"title": key, "lines": sub})
    return sections
