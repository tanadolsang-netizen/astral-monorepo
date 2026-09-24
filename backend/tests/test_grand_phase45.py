"""Universe Phase 4.5 — human_design + kalachakra unlocked on verified data.

QA ground truth (2026-08-23):
- HD wheel: C:/AI/research-astrology/data/hd_gate_wheel.json (64-gate Rave
  Mandala, anchor 302° ecliptic = Gate 41, Gate 33 slice = 127.625–133.25°).
  M natal tropical Sun ≈ 58.05° → Personality Sun **8.4** (verified worked
  example). Design moment ≈ 88° solar arc back ≈ Feb 18–19 1997 (±2 d).
- Kalachakra: data/kalachakra_anchor.json — epoch 1027 = Fire-female-Hare,
  i = (Y−4) mod 60; M (1997-05-19, after Losar 1997-02-08) → Fire-Ox-Female
  (Rabjung cycle 17 year 11). Parkha day number = JDN mod 8 (number only).
"""

import json
import re
from datetime import date, time
from pathlib import Path

import pytest

from src.services.grand.human_design import (
    _WHEEL_ORDER_FALLBACK,
    compute_human_design,
    lon_to_gate_line,
)
from src.services.grand.kalachakra import compute_kalachakra, rabjung_label

_M_BIRTH = date(1997, 5, 19)
_M_PROFILE = {
    "date": _M_BIRTH.isoformat(),
    "time": time(5, 45).isoformat(),
    "tz_offset_hours": 7.0,
    "lat": 13.36,
    "lon": 100.98,
}

_WHEEL_FILE = Path("C:/AI/research-astrology/data/hd_gate_wheel.json")


def _m_chart(system="tropical"):
    from src.services.chart_service import compute_chart

    return compute_chart(
        name="M", date=_M_BIRTH, time=time(5, 45),
        tz_offset_hours=7.0, lat=13.36, lon=100.98, system=system,
    )


def _hd():
    return compute_human_design(natal_chart=_m_chart())


# ---------------------------------------------------------------------------
# Human Design — wheel math (spec 06 QA ground truth)
# ---------------------------------------------------------------------------

class TestWheelMath:
    def test_anchor_gate41_line1_at_302(self):
        assert lon_to_gate_line(302.0) == (41, 1)

    def test_wrap_below_anchor_lands_last_slot(self):
        assert lon_to_gate_line(301.99) == (60, 6)

    def test_gate33_slice_pinned_boundaries(self):
        # thehumandesign.com: Gate 33 starts 7°37′30″ Leo (=127.625°)
        assert lon_to_gate_line(127.625) == (33, 1)
        assert lon_to_gate_line(133.2499) == (33, 6)
        assert lon_to_gate_line(133.26)[0] != 33  # past the end

    def test_all_64x6_slots_tile_without_gaps(self):
        order = _WHEEL_ORDER_FALLBACK
        assert sorted(order) == list(range(1, 65))
        seen = set()
        for slot in range(64):
            for line in range(6):
                mid = 302.0 + (slot + (line + 0.5) / 6) * (360 / 64)
                g, l = lon_to_gate_line(mid)
                assert (g, l) == (order[slot], line + 1)
                seen.add((g, l))
        assert len(seen) == 384

    def test_embedded_fallback_matches_verified_file(self):
        if not _WHEEL_FILE.exists():
            pytest.skip("research data dir not present on this machine")
        order = json.loads(_WHEEL_FILE.read_text(encoding="utf-8"))["order"]
        assert _WHEEL_ORDER_FALLBACK == [int(g) for g in order]

    def test_worked_example_sun_ground_truth(self):
        # hd_gate_wheel.json rerun row: Sun lon 58.05 → 8.4 (M's natal Sun)
        assert lon_to_gate_line(58.05) == (8, 4)


# ---------------------------------------------------------------------------
# Human Design — Profile via design-moment iteration (M ground truth)
# ---------------------------------------------------------------------------

class TestHumanDesignProfile:
    def test_m_profile_partial_structure(self):
        hd = _hd()
        # Phase 4.7: full unlock — status ok with real Type/Authority.
        assert hd["status"] == "ok"
        prof = hd["profile"]
        for key in ("p_sun", "d_sun"):
            assert re.fullmatch(r"\d{1,2}\.\d", str(prof[key]))
        assert re.fullmatch(r"\d{1,2}/\d{1,2}", str(prof["profile_name"]))
        assert prof["profile_name"] == (
            f"{prof['p_sun'].split('.')[1]}/{prof['d_sun'].split('.')[1]}"
        )
        # Type/Authority are now REAL (36-channel table), never absent guesses.
        assert hd["type"] in {
            "Manifestor", "Generator", "Manifesting Generator",
            "Projector", "Reflector",
        }
        assert hd["authority"]
        assert hd["defined_channels"] and hd["defined_centers"]
        assert hd["channels_source"]

    def test_m_personality_sun_is_8_4(self):
        hd = _hd()
        assert hd["personality"]["gate"] == 8
        assert hd["personality"]["line"] == 4
        assert hd["profile"]["p_sun"] == "8.4"

    def test_m_design_moment_within_window(self):
        # Ground truth: ~1997-02-18/19 from birth; mission window ±2 days.
        hd = _hd()
        d = hd["design"]
        moment = d["moment_utc"]
        assert "1997-02-16" <= moment[:10] <= "1997-02-21"
        assert 87.0 <= d["arc_days_before_birth"] <= 92.0
        # Design Sun sits −88° solar arc from the Personality Sun (frame-agnostic:
        # Phase 4.7 switched activations to ecliptic-of-date via pyswisseph).
        assert abs(d["sun_longitude_tropical"] - (
            (hd["personality"]["sun_longitude_tropical"] - 88.0) % 360
        )) < 0.01
        assert hd["profile"]["d_sun"] == f"{d['gate']}.{d['line']}"

    def test_degraded_paths_stay_unavailable(self):
        assert compute_human_design()["reason"] == "missing_natal_chart"
        no_sun = {"bodies": [{"body": "Moon", "absolute_deg": 10.0}]}
        assert compute_human_design(natal_chart=no_sun)["reason"] == \
            "missing_natal_sun_longitude"
        bad_dt = {
            "bodies": [{"body": "Sun", "absolute_deg": 58.05}],
            "datetime_utc": "not-a-date",
        }
        assert compute_human_design(natal_chart=bad_dt)["reason"] == \
            "invalid_natal_datetime_utc"


# ---------------------------------------------------------------------------
# Kalachakra — Rabjung year layer (spec 18 QA ground truth)
# ---------------------------------------------------------------------------

class TestKalachakraYear:
    def test_m_fire_ox_female_post_losar(self):
        kal = compute_kalachakra(_M_BIRTH)
        assert kal["status"] == "ok"
        assert kal["year"]["element"] == "Fire"
        assert kal["year"]["animal"] == "Ox"
        assert kal["year"]["gender"] == "female"
        assert kal["tibetan_year"] == 1997
        assert kal["rabjung"]["cycle"] == 17
        assert kal["rabjung"]["year_in_cycle"] == 11
        assert kal["losar_rule"]["assigned_prior_year"] is False

    @pytest.mark.parametrize("year,element,animal,gender", [
        (1027, "Fire", "Hare", "female"),   # Rabjung c1y1 epoch (Laufer/Janson)
        (1987, "Fire", "Hare", "female"),   # 17th cycle begins (Janson)
        (1991, "Iron", "Sheep", "female"),  # Janson Table 1
        (2008, "Earth", "Mouse", "male"),   # sa pho byi
        (2021, "Iron", "Ox", "female"),     # Tibetan Nuns Project Losar 2021
        (2026, "Fire", "Horse", "male"),    # TNP Losar 2026
    ])
    def test_published_anchor_vectors(self, year, element, animal, gender):
        lab = rabjung_label(year)
        assert (lab["element"], lab["animal"], lab["gender"]) == (element, animal, gender)

    def test_rejected_phase_never_resurfaces(self):
        # Spec pseudocode phase gave Wood-Ox-male for 1997 — must never appear.
        assert rabjung_label(1997)["label"] != "Wood-Ox (male)"

    def test_pre_losar_assigns_prior_year_flagged_approximate(self):
        early = compute_kalachakra(date(1997, 2, 5))
        assert early["tibetan_year"] == 1996
        assert early["losar_rule"]["assigned_prior_year"] is True
        assert early["losar_rule"]["approximate"] is True
        boundary = compute_kalachakra(date(1997, 2, 8))  # Losar day itself
        assert boundary["tibetan_year"] == 1997
        assert boundary["losar_rule"]["assigned_prior_year"] is False


class TestKalachakraParkhaDay:
    def test_m_parkha_day_number_range_and_value(self):
        kal = compute_kalachakra(_M_BIRTH)
        n = kal["parkha_day_number"]
        assert isinstance(n, int) and 0 <= n <= 7
        from src.services.grand.mayan_tzolkin import jdn
        assert n == jdn(1997, 5, 19) % 8  # 2450588 % 8

    def test_parkha_names_not_invented(self):
        kal = compute_kalachakra(_M_BIRTH)
        assert kal["parkha_names"]["status"] == "unavailable"


class TestKalachakraDegradation:
    def test_missing_and_invalid(self):
        assert compute_kalachakra(None)["reason"] == "missing_birth_date"
        assert compute_kalachakra("31/02/1997")["reason"] == "invalid_birth_date"


# ---------------------------------------------------------------------------
# Fusion wiring — extended sections live, reading lines updated
# ---------------------------------------------------------------------------

class TestFusionPhase45Wiring:
    def test_extended_sections_no_longer_unavailable(self):
        from src.services.grand.grand_fusion import compute_grand_fusion

        ext = compute_grand_fusion("M", profile=dict(_M_PROFILE))["extended"]
        hd, kal = ext["human_design"], ext["kalachakra"]
        # Phase 4.7: HD fully unlocked — ok + Type/Authority; profile preserved.
        assert hd["status"] == "ok" and hd["profile"]["p_sun"] == "8.4"
        assert hd["type"] in {
            "Manifestor", "Generator", "Manifesting Generator",
            "Projector", "Reflector",
        }
        assert kal["status"] == "ok"
        assert kal["year"] == {
            "element": "Fire", "animal": "Ox",
            "gender": "female", "label": "Fire-Ox (female)",
        }

    def test_reading_lines_reflect_unlock(self):
        from src.services.grand.grand_fusion import compute_grand_fusion

        reading = compute_grand_fusion("M", profile=dict(_M_PROFILE))["reading"]
        for lang in ("th", "en"):
            hd_line = reading[lang]["human_design"]
            kal_line = reading[lang]["kalachakra"]
            assert "unavailable" not in hd_line.lower()
            assert "unavailable" not in kal_line.lower()
            assert "4/6" in hd_line and "8.4" in hd_line and "30.6" in hd_line
            assert "Fire" in kal_line and "Ox" in kal_line
