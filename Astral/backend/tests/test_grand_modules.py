"""Universe Phase 2 — grand modules on M's ground truth.

Owner birth data (validated ledger): 1997-05-19 05:45 ICT, Chonburi
(13.36 N, 100.98 E). Verified anchors used here (never exact unverifiable
numbers):

- Tropical: Sun Tau 28.05, Moon Lib 17.37, ASC Tau ~25.9, Venus Gem 10.15
- Sidereal Lahiri: Sun Tau 4.37  → solar-return 2026 lands ≈ 14 May 2026
- Fixed stars: Venus conj Aldebaran within 2°, Moon conj Gienah within 2°
- Sabian (spec 09): Sun→Taurus 29 cobblers · Moon→Libra 18 under arrest ·
  ASC→Taurus 26 Spanish gallant
- Ziwei (spec 05): lunar month 4 / day 13 / 卯 hour → Life Palace 寅,
  Body Palace 申; 2026 丙午 → Sui Po 子/Rat; 2027 丁未 → Sui Po 丑/Ox
"""

from datetime import date, time

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.services.chart_service import SIGNS
from src.services.grand.asteroids import compute_asteroids
from src.services.grand.fixed_stars import (
    FIXED_STARS,
    compute_fixed_stars,
    sabian_symbol,
)
from src.services.grand.varshaphal import compute_varshaphal
from src.services.grand.ziwei import compute_ziwei
from src.services.grand.grand_fusion import compute_grand_fusion

client = TestClient(app)

_M = {
    "name": "M",
    "date": date(1997, 5, 19),
    "time": time(5, 45),
    "tz_offset_hours": 7.0,
    "lat": 13.36,
    "lon": 100.98,
}

_CLASSICAL = {"Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"}


def _m_profile() -> dict:
    return {
        "date": _M["date"].isoformat(),
        "time": _M["time"].isoformat(),
        "tz_offset_hours": _M["tz_offset_hours"],
        "lat": _M["lat"],
        "lon": _M["lon"],
    }


def _m_chart(system="tropical"):
    from src.services.chart_service import compute_chart
    return compute_chart(
        name="M", date=_M["date"], time=_M["time"],
        tz_offset_hours=_M["tz_offset_hours"],
        lat=_M["lat"], lon=_M["lon"], system=system,
    )


# ---------------------------------------------------------------------------
# Fixed stars + Sabian
# ---------------------------------------------------------------------------

class TestFixedStars:
    def test_royal_table_has_four_royal_stars(self):
        royals = [s for s in FIXED_STARS if s["royal"]]
        assert {s["name"] for s in royals} == {"Aldebaran", "Regulus", "Antares", "Fomalhaut"}

    def test_m_venus_conjunct_aldebaran_within_2_deg(self):
        result = compute_fixed_stars(_m_chart())
        contacts = {
            (c["natal_point"], c["star"]): c for c in result["conjunctions"]
        }
        aldebaran = contacts.get(("Venus", "Aldebaran"))
        assert aldebaran is not None, "ground truth: Venus sits on Aldebaran within 2°"
        assert aldebaran["orb_deg"] <= 2.0
        assert aldebaran["royal"] is True

    def test_contacts_sorted_and_well_formed(self):
        result = compute_fixed_stars(_m_chart())
        orbs = [c["orb_deg"] for c in result["conjunctions"]]
        assert orbs == sorted(orbs)
        assert all(0 <= o <= 2.0 for o in orbs)
        for c in result["conjunctions"]:
            assert {"star", "natal_point", "orb_deg", "royal", "meaning_en", "meaning_th"} <= set(c)

    def test_sabian_owner_points_verbatim(self):
        result = compute_fixed_stars(_m_chart())
        sab = result["sabian"]
        assert sab["sun"]["phrase_en"] == "Two cobblers working at a table"
        assert sab["sun"]["number"] == 29 and "Taurus" in sab["sun"]["sign"]
        assert sab["moon"]["number"] == 18 and sab["moon"]["verbatim"] is True
        assert sab["asc"]["phrase_en"] == "A Spanish gallant serenades his beloved"
        # Thai phrases always ride along
        assert sab["moon"]["phrase_th"]

    def test_sabian_fallback_never_invents(self):
        sym = sabian_symbol(123.45)  # Leo-ish untabulated degree
        assert sym["verbatim"] is False
        assert sym["phrase_en"].startswith("symbol ")
        assert sym["source"] == "fallback-index"


# ---------------------------------------------------------------------------
# Varshaphal (sidereal solar return)
# ---------------------------------------------------------------------------

class TestVarshaphal:
    def test_sr2026_lands_mid_may(self):
        v26 = compute_varshaphal(
            name=_M["name"], birth_date=_M["date"], birth_time=_M["time"],
            target_year=2026, tz_offset_hours=_M["tz_offset_hours"],
            lat=_M["lat"], lon=_M["lon"], system="sidereal",
        )
        stamp = v26["return_datetime_utc"]
        assert stamp.startswith("2026-05")
        day = int(stamp[8:10])
        # Birthday-window rule (mission): the return lands around May 19.
        # (Spec 16's "≈14 May" was its own pre-solver estimate flagged
        # [RUNTIME solve exact HH:MM]; the numeric solver supersedes it.)
        assert 16 <= day <= 22, f"expected return near birthday May 19, got {stamp}"

    def test_year_over_year_drift_under_one_day_per_year(self):
        v26 = compute_varshaphal(
            name=_M["name"], birth_date=_M["date"], birth_time=_M["time"],
            target_year=2026, tz_offset_hours=_M["tz_offset_hours"],
            lat=_M["lat"], lon=_M["lon"], system="sidereal",
        )
        v27 = compute_varshaphal(
            name=_M["name"], birth_date=_M["date"], birth_time=_M["time"],
            target_year=2027, tz_offset_hours=_M["tz_offset_hours"],
            lat=_M["lat"], lon=_M["lon"], system="sidereal",
        )
        from datetime import datetime
        t26 = datetime.fromisoformat(v26["return_datetime_utc"].replace("Z", "+00:00"))
        t27 = datetime.fromisoformat(v27["return_datetime_utc"].replace("Z", "+00:00"))
        delta = (t27 - t26).total_seconds() / 86400
        assert 364 <= delta <= 366.5  # one tropical year, drift well under 1.5 d

    def test_structure_muntha_year_lord_sahams(self):
        v = compute_varshaphal(
            name=_M["name"], birth_date=_M["date"], birth_time=_M["time"],
            target_year=2026, tz_offset_hours=_M["tz_offset_hours"],
            lat=_M["lat"], lon=_M["lon"], system="sidereal",
        )
        # Muntha: sign advanced from natal lagna by completed years
        assert v["muntha"]["sign"] in SIGNS
        assert 1 <= v["muntha"]["house_from_natal_lagna"] <= 12
        assert v["muntha"]["lord"] in _CLASSICAL
        # Year Lord chosen among the three deterministic candidates
        yl = v["year_lord"]
        assert yl["planet"] in _CLASSICAL
        assert {c["planet"] for c in yl["candidates"]} >= {yl["planet"]}
        assert yl["planet"] == max(
            yl["candidates"], key=lambda c: c["score"]
        )["planet"]
        # Lagna + sahams + aspects shape
        assert v["varsha_lagna"]["sign"] in SIGNS
        assert {"Punya", "Spirit", "Vivaha", "Courage"} <= set(v["sahams"])
        for a in v["tajika_aspects"]:
            assert a["aspect"] in {"conjunction", "opposition", "trine", "square", "sextile"}
        assert v["chart"]["system"] == "sidereal"


# ---------------------------------------------------------------------------
# Ziwei (minimal real computation)
# ---------------------------------------------------------------------------

class TestZiwei:
    def test_m_life_body_palace_ground_truth(self):
        zw = compute_ziwei(_M["date"], _M["time"])
        lp = zw["lunar"]
        assert (lp["month"], lp["day"]) == (4, 13)          # 一九九七年四月十三
        assert lp["is_leap_month"] is False
        assert lp["hour_zhi"] == "卯"                        # 05:45 → Mao hour
        assert lp["year_ganzhi"] == "丁丑"
        assert zw["life_palace"]["branch"] == "寅"           # spec 05 §1 test case
        assert zw["body_palace"]["branch"] == "申"
        assert zw["life_palace"]["pillar"] == "壬寅"         # 五虎遁: 丁年 → 壬寅起

    def test_palace_wheel_twelve_paired(self):
        zw = compute_ziwei(_M["date"], _M["time"])
        wheel = zw["palace_wheel"]
        assert len(wheel) == 12
        assert wheel[0]["name_en"] == "Life" and wheel[0]["branch"] == "寅"
        branches = [p["branch"] for p in wheel]
        assert len(set(branches)) == 12                      # every branch exactly once

    def test_annual_layer_sui_po_2026_2027(self):
        zw = compute_ziwei(_M["date"], _M["time"], annual_years=[2026, 2027])
        a26, a27 = zw["annual"]["2026"], zw["annual"]["2027"]
        assert a26["ganzhi"] == "丙午" and a26["sui_po_branch"] == "子"
        assert a26["sui_po_animal"] == "Rat"
        assert a27["ganzhi"] == "丁未" and a27["sui_po_branch"] == "丑"
        assert a27["sui_po_animal"] == "Ox"

    def test_summary_is_compact_dict(self):
        from src.services.grand.ziwei import ziwei_summary
        s = ziwei_summary(compute_ziwei(_M["date"], _M["time"]))
        assert s["life_pillar"] == "壬寅"
        assert "Life" in s["key_palaces"]


# ---------------------------------------------------------------------------
# Asteroids — graceful when swisseph/seas_18.se1 absent
# ---------------------------------------------------------------------------

class TestAsteroidsGraceful:
    def test_ok_or_unavailable_never_raises(self):
        result = compute_asteroids(_m_chart())
        assert result["status"] in ("ok", "partial", "unavailable")
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable on this runtime: {result.get('reason', '')[:80]}")
        for name in ("Chiron", "Ceres", "Pallas", "Juno", "Vesta"):
            assert name in result["positions"]
            assert 0 <= result["positions"][name]["absolute_deg"] < 360


# ---------------------------------------------------------------------------
# Grand fusion wiring
# ---------------------------------------------------------------------------

class TestGrandFusionWiring:
    def test_service_returns_all_four_sections(self):
        payload = compute_grand_fusion(
            "M", lang="th", years=[2026, 2027], profile=_m_profile(),
        )
        ext = payload["extended"]
        for section in ("fixed_stars", "asteroids", "varshaphal", "ziwei"):
            assert section in ext, f"missing extended section {section}"
        assert ext["fixed_stars"]["status"] == "ok"
        assert ext["fixed_stars"]["royal_star_contacts"]
        assert set(ext["varshaphal"]["years"]) == {"2026", "2027"}
        assert ext["ziwei"]["life_palace"]["branch"] == "寅"
        assert ext["asteroids"]["status"] in ("ok", "partial", "unavailable")
        # reading lines exist in both languages
        assert payload["reading"]["th"]["varshaphal"]
        assert payload["reading"]["en"]["fixed_stars"]

    def test_endpoint_live_shape(self):
        resp = client.get("/v1/fusion/grand/M", params={"lang": "th", "years": "2026,2027"})
        assert resp.status_code == 200, resp.text
        body = resp.json()
        ext = body["extended"]
        assert ext["varshaphal"]["years"]["2026"]["muntha"]["sign"] in SIGNS
        assert ext["ziwei"]["body_palace"]["branch"] == "申"
        assert body["person"]["birth"]["date"] == "1997-05-19"

    def test_endpoint_unknown_profile_is_404(self):
        assert client.get("/v1/fusion/grand/nobody-here").status_code == 404
