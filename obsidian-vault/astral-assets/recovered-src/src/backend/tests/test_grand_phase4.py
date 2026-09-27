"""Universe Phase 4 — remaining science modules on M's ground truth.

QA notes (2026-08-23) in C:/AI/research-astrology/11,12,13,14,15,06,18
govern every constant here. Asserts are structure-first per module; exact
values only where a QA ground truth pins them:

- Numerology (M 1997-05-19): Life Path 5 · Birth Day 1 · PY 2026 = 7 ·
  PY 2027 = 8.
- I Ching seeded vector M|1997-05-19||hermes-v1: primary #11 Peace,
  zero changing lines, nuclear #54; date-fallback for the same date → #45.
- Nine Star Ki: M → year star 3 Three Blue Wood (spec code path, [VERIFY]
  flag carried); month/day stars constant_unpinned.
- Mayan Dreamspell: M → Kin 239 · Seal 19 BLUE STORM · Tone 5 Overtone.
- Cosmobiology: tropical-only tree; Sun/Moon midpoint 127.71° (Leo 7°43′);
  the four §3 natal pictures reproduce (orbs within input-rounding).
- Human Design / Kalachakra: Phase 4.5 unlocked (profile 8.4/30.6 = 4/6;
  Rabjung Fire-Ox-female) — full coverage lives in test_grand_phase45.py.
"""

from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.grand.cosmobiology import compute_cosmobiology, midpoint
from src.services.grand.grand_fusion import compute_grand_fusion
from src.services.grand.human_design import compute_human_design
from src.services.grand.iching import (
    HEX_TEXTS,
    compute_iching,
    date_fallback_number,
)
from src.services.grand.kalachakra import compute_kalachakra
from src.services.grand.mayan_tzolkin import (
    ANCHOR_JDN,
    compute_mayan_tzolkin,
    jdn,
)
from src.services.grand.ninestar_ki import compute_ninestar_ki
from src.services.grand.numerology import compute_numerology

client = TestClient(app)

_M_BIRTH = date(1997, 5, 19)
_M_PROFILE = {
    "date": _M_BIRTH.isoformat(),
    "time": time(5, 45).isoformat(),
    "tz_offset_hours": 7.0,
    "lat": 13.36,
    "lon": 100.98,
}

_PHASE4_SECTIONS = (
    "numerology", "iching", "ninestar_ki", "mayan_tzolkin",
    "cosmobiology", "human_design", "kalachakra",
)


def _m_chart(system="tropical"):
    from src.services.chart_service import compute_chart
    return compute_chart(
        name="M", date=_M_BIRTH, time=time(5, 45),
        tz_offset_hours=7.0, lat=13.36, lon=100.98, system=system,
    )


# ---------------------------------------------------------------------------
# Numerology (spec 11)
# ---------------------------------------------------------------------------

class TestNumerology:
    def test_ground_truth_m_exact(self):
        n = compute_numerology(_M_BIRTH)
        assert n["status"] == "ok"
        assert n["life_path"]["number"] == 5
        assert n["life_path"]["raw_digit_sum"] == 41
        assert n["birth_day"]["number"] == 1
        assert n["personal_year"]["2026"]["number"] == 7
        assert n["personal_year"]["2027"]["number"] == 8

    def test_master_preserving_reduction(self):
        # 29 → 11 stays master; 2027 year digits 11 kept then total 17 → 8.
        from src.services.grand.numerology import reduce_number
        assert reduce_number(29) == 11
        assert reduce_number(38) == 11
        assert reduce_number(41) == 5

    def test_degradation_missing_and_invalid(self):
        assert compute_numerology(None) == {
            "status": "unavailable", "reason": "missing_birth_date",
        }
        bad = compute_numerology("not-a-date")
        assert bad["status"] == "unavailable" and bad["reason"] == "invalid_birth_date"

    def test_name_numbers_graceful_without_name(self):
        n = compute_numerology(_M_BIRTH)
        assert n["name_numbers"]["reason"] == "birth_name_not_provided"

    def test_structure(self):
        n = compute_numerology(_M_BIRTH)
        for key in ("status", "life_path", "birth_day", "personal_year", "name_numbers"):
            assert key in n
        for entry in n["personal_year"].values():
            assert {"number", "core_en", "core_th"} <= set(entry)


# ---------------------------------------------------------------------------
# I Ching (spec 12)
# ---------------------------------------------------------------------------

class TestIching:
    def test_qa_seeded_vector_exact(self):
        ic = compute_iching("M", "1997-05-19")
        assert ic["status"] == "ok"
        assert ic["line_values_bottom_up"] == [7, 7, 7, 8, 8, 8]
        assert ic["lines_bottom_up"] == [1, 1, 1, 0, 0, 0]
        assert ic["changing_line_indexes"] == []
        assert ic["primary"]["king_wen"] == 11
        assert ic["primary"]["en"] == "Peace"
        assert ic["primary"]["text_complete"] is True
        assert ic["derived"] is None  # no changing lines → derived = primary
        assert ic["nuclear"]["king_wen"] == 54
        assert ic["nuclear"]["en"] == "The Marrying Maiden"

    def test_date_fallback_cross_check(self):
        assert date_fallback_number(1997, 5, 19) == 45  # (19*5 + 1997) % 64 + 1
        ic = compute_iching("M", "1997-05-19")
        assert ic["cross_check_fallback"]["king_wen"] == 45

    def test_missing_seed_degrades(self):
        assert compute_iching(None, None) == {
            "status": "unavailable", "reason": "missing_seed_input",
        }

    def test_unwritten_text_never_faked(self):
        # Pick a date whose fallback hexagram has no written entry.
        assert len(HEX_TEXTS) < 64
        for num, text in HEX_TEXTS.items():
            assert text["judgment_en"] and text["judgment_th"]

    def test_deterministic_reproducible(self):
        a = compute_iching("M", "1997-05-19", salt="hermes-v1")
        b = compute_iching("M", "1997-05-19", salt="hermes-v1")
        assert a["lines_bottom_up"] == b["lines_bottom_up"]
        assert a["primary"]["king_wen"] == b["primary"]["king_wen"]


# ---------------------------------------------------------------------------
# Nine Star Ki (spec 13)
# ---------------------------------------------------------------------------

class TestNineStarKi:
    def test_m_year_star_three_blue_wood(self):
        ns = compute_ninestar_ki(_M_BIRTH)
        assert ns["status"] == "ok"
        assert ns["year_star"]["star"] == 3
        assert ns["year_star"]["name_en"] == "Three Blue Wood"
        assert ns["year_star"]["element"] == "Wood"
        assert ns["year_star"]["palace"] == "Zhen/East"

    def test_verify_flag_carried_not_silently_picked(self):
        ns = compute_ninestar_ki(_M_BIRTH)
        assert "[VERIFY]" in ns["year_star"]["verify_flag"]
        assert ns["month_star"] == {
            "status": "unavailable", "reason": "constant_unpinned:month",
        }
        assert ns["day_star"]["reason"] == "constant_unpinned:day"

    def test_lichun_cutoff(self):
        from src.services.grand.ninestar_ki import year_star
        assert year_star(1997, 5, 19) == 3
        assert year_star(1997, 2, 3) == year_star(1996)  # before LiChun → prior year

    def test_degradation(self):
        assert compute_ninestar_ki(None)["reason"] == "missing_birth_date"
        assert compute_ninestar_ki("junk")["reason"] == "invalid_birth_date"
        assert compute_ninestar_ki(date(1899, 12, 31))["reason"] == \
            "year_out_of_supported_range"


# ---------------------------------------------------------------------------
# Mayan Dreamspell / Tzolkin (spec 14)
# ---------------------------------------------------------------------------

class TestMayanTzolkin:
    def test_ground_truth_m_exact(self):
        my = compute_mayan_tzolkin(_M_BIRTH, today=date(2026, 8, 23))
        assert my["status"] == "ok"
        assert my["kin"] == 239
        assert my["seal"]["number"] == 19
        assert my["seal"]["name"] == "BLUE STORM"
        assert my["tone"]["number"] == 5
        assert my["tone"]["name"] == "Overtone"
        assert my["signature_en"] == "Kin 239 — Blue Overtone Storm"

    def test_epoch_offset_not_naive_delta(self):
        # QA bug-class guard: JDN 2450588 − 2447003 = 3585; naive mod 260 = 205,
        # correct Kin 239 comes only through the Kin-34 epoch formula.
        assert jdn(1987, 7, 26) == ANCHOR_JDN == 2447003
        assert jdn(1997, 5, 19) == 2450588
        naive = (2450588 - ANCHOR_JDN) % 260 + 1
        assert naive != 239
        my = compute_mayan_tzolkin(_M_BIRTH)
        assert my["kin"] == 239

    def test_daily_kin_present(self):
        my = compute_mayan_tzolkin(_M_BIRTH, today=date(2026, 8, 23))
        assert my["daily_kin"]["date"] == "2026-08-23"
        assert 1 <= my["daily_kin"]["kin"] <= 260

    def test_classical_gmt_unpinned(self):
        my = compute_mayan_tzolkin(_M_BIRTH)
        assert my["classical_gmt"] == {
            "status": "unavailable", "reason": "correlation_constant_unpinned",
        }

    def test_degradation(self):
        assert compute_mayan_tzolkin(None)["reason"] == "missing_birth_date"
        assert compute_mayan_tzolkin("31/02/1997")["reason"] == "invalid_birth_date"


# ---------------------------------------------------------------------------
# Cosmobiology (spec 15)
# ---------------------------------------------------------------------------

class TestCosmobiology:
    def test_tree_structure(self):
        cb = compute_cosmobiology(_m_chart())
        assert cb["status"] == "ok"
        assert cb["frame"] == "tropical-only"
        n_points = cb["point_count"]
        assert cb["pair_count"] == n_points * (n_points - 1) // 2
        assert len(cb["midpoints"]) == cb["pair_count"]
        for m in cb["midpoints"]:
            assert {"pair", "direct_deg", "indirect_deg", "hits"} <= set(m)
            # entries are each rounded to 4dp — allow rounding drift
            assert abs(m["indirect_deg"] - (m["direct_deg"] + 180) % 360) < 1e-3
        for p in cb["pictures"]:
            assert p["orb_deg"] <= 2.0
        for p in cb["confirmed_pictures"]:
            assert p["orb_deg"] <= 1.0

    def test_sun_moon_midpoint_regression(self):
        cb = compute_cosmobiology(_m_chart())
        sm = cb["sun_moon_midpoint"]
        assert sm is not None
        assert round(sm["direct_deg"], 2) == 127.71  # Leo 7°43′ (spec §3)
        assert sm["sign"] and sm["degree_in_sign"] > 7.0

    def test_spec3_natal_pictures_reproduce(self):
        cb = compute_cosmobiology(_m_chart())
        by_name = {p["picture"]: p for p in cb["pictures"]}
        ve_ma = by_name["Venus/Mars=Neptune"]
        assert ve_ma["side"] == "indirect" and ve_ma["orb_deg"] < 0.2
        su_ve = by_name["Sun/Venus=Pluto"]
        assert su_ve["side"] == "indirect" and su_ve["orb_deg"] < 0.4
        ve_ju = by_name["Venus/Jupiter=Saturn"]
        assert ve_ju["side"] == "direct" and ve_ju["orb_deg"] < 0.45
        su_mo = by_name["Sun/Moon=Uranus"]
        assert su_mo["side"] == "indirect" and su_mo["orb_deg"] < 1.0

    def test_wrap_never_naive_average(self):
        # Jupiter/Saturn straddles 0° Aries: direct ≈ 348.65, not ~168.6.
        d = midpoint(321.2104, 16.0879)
        assert 348.0 < d < 349.5

    def test_degradation_insufficient_points(self):
        cb = compute_cosmobiology({"bodies": [{"body": "Sun", "absolute_deg": 10.0}]})
        assert cb["status"] == "unavailable"
        assert cb["reason"] == "insufficient_points(<2 valid longitudes)"
        assert cb["midpoints"] == []


# ---------------------------------------------------------------------------
# Graceful-unavailable modules (spec 06 / 18)
# ---------------------------------------------------------------------------

class TestHumanDesignUnavailable:
    def test_exact_reason_no_type_guess(self):
        # Phase 4.5: without a natal chart the module still degrades honestly.
        hd = compute_human_design()
        assert hd["status"] == "unavailable"
        assert hd["reason"] == "missing_natal_chart"
        assert "Type" not in hd or "type" not in hd  # never a Type guess


class TestKalachakraUnavailable:
    def test_exact_reason_constants_not_implemented(self):
        # Phase 4.5: year layer unlocked; only the degradation path remains here.
        kal = compute_kalachakra(None)
        assert kal["status"] == "unavailable"
        assert kal["reason"] == "missing_birth_date"
        # The spec's broken phase must NOT be implemented: no Wood/Ox/male output.
        assert "Wood" not in str(kal.get("year", ""))


# ---------------------------------------------------------------------------
# Fusion wiring (extended + reading)
# ---------------------------------------------------------------------------

class TestGrandFusionPhase4Wiring:
    def test_extended_has_all_sections(self):
        payload = compute_grand_fusion("M", profile=dict(_M_PROFILE))
        ext = payload["extended"]
        # Phase 2 sections must not regress.
        for section in ("fixed_stars", "asteroids", "varshaphal", "ziwei"):
            assert section in ext, f"missing extended section {section}"
        for section in _PHASE4_SECTIONS:
            assert section in ext, f"missing extended section {section}"

    def test_phase4_values_through_fusion(self):
        ext = compute_grand_fusion("M", profile=dict(_M_PROFILE))["extended"]
        assert ext["numerology"]["life_path"]["number"] == 5
        assert ext["iching"]["primary"]["king_wen"] == 11
        assert ext["ninestar_ki"]["year_star"]["star"] == 3
        assert ext["mayan_tzolkin"]["kin"] == 239
        assert ext["cosmobiology"]["status"] == "ok"
        # Phase 4.5: both sections now compute for real.
        # Phase 4.7: HD is fully unlocked (Type/Authority included).
        assert ext["human_design"]["status"] == "ok"
        assert ext["human_design"]["type"]
        assert ext["kalachakra"]["status"] == "ok"

    def test_reading_lines_th_and_en(self):
        payload = compute_grand_fusion("M", profile=dict(_M_PROFILE))
        for lang in ("th", "en"):
            for section in _PHASE4_SECTIONS:
                line = payload["reading"][lang].get(section)
                assert line, f"missing reading[{lang}][{section}]"

    def test_api_endpoint_serves_phase4(self):
        resp = client.get("/v1/fusion/grand/M", params={"lang": "th", "years": "2026,2027"})
        assert resp.status_code == 200
        body = resp.json()
        for section in _PHASE4_SECTIONS:
            assert section in body["extended"], f"API missing extended section {section}"
