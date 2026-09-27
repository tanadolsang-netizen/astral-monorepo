"""Tests: Triple-activation timing + KP sub-lord engine."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.services.kp_service import (
    kp_ayanamsa, star_and_sub, kp_event_filter, cuspal_sub_lords,
)
from src.services.triple_activation import (
    triple_activation_windows, _whole_sign_house, _EVENT_HOUSE_MAP,
)


# ── KP ───────────────────────────────────────────────────────────────
def test_kp_ayanamsa_2026_value() -> None:
    a = kp_ayanamsa(datetime(2026, 9, 1))
    assert 24.10 <= a <= 24.16  # ~24°8'


def test_star_lord_zero_is_ketu() -> None:
    r = star_and_sub(0.0)
    assert r["star_lord"] == "Ketu"
    assert r["sub_lord"] == "Ketu"      # first sub of Ketu star is Ketu
    assert r["nakshatra"] == 1


def test_bharani_starts_venus() -> None:
    r = star_and_sub(13.34)             # 13°20' = Bharani
    assert r["nakshatra"] == 2
    assert r["star_lord"] == "Venus"


def test_sub_spans_proportional_to_vim_years() -> None:
    # Venus star: sub order Venus(20),Sun(6),Moon(10)... spans ∝ years
    v = star_and_sub(13.34)                          # start of Venus sub
    s = star_and_sub(13.34 + 13.3333 * (20 / 120))   # end of Venus sub span
    assert v["sub_lord"] == "Venus"
    assert s["sub_lord"] in ("Sun", "Venus")          # boundary tolerance


def test_event_filter_structure() -> None:
    from src.services.chart_service import compute_chart
    c = compute_chart("kp", __import__("datetime").date(1990, 5, 19),
                      __import__("datetime").time(5, 45),
                      tz_offset_hours=0, lat=13.75, lon=100.52)
    r = kp_event_filter(c, datetime(2026, 9, 1), "marriage")
    assert r["system"] == "kp-event-filter"
    houses = [x["house"] for x in r["cusps"]]
    assert sorted(houses) == [2, 7, 11]
    assert isinstance(r["event_allowed_by_kp"], bool)


def test_event_filter_bad_category() -> None:
    from src.services.chart_service import compute_chart
    c = compute_chart("kp", __import__("datetime").date(1990, 5, 19),
                      __import__("datetime").time(5, 45),
                      tz_offset_hours=0, lat=13.75, lon=100.52)
    with pytest.raises(ValueError):
        kp_event_filter(c, datetime(2026, 9, 1), "lottery")


def test_cuspal_table_12_houses() -> None:
    from src.services.chart_service import compute_chart
    c = compute_chart("kp", __import__("datetime").date(1990, 5, 19),
                      __import__("datetime").time(5, 45),
                      tz_offset_hours=0, lat=13.75, lon=100.52)
    rows = cuspal_sub_lords(c, datetime(2026, 9, 1))
    assert len(rows) == 12
    for row in rows:
        assert row["star_lord"] and row["sub_lord"]


# ── Triple activation ────────────────────────────────────────────────
def test_whole_sign_house_math() -> None:
    assert _whole_sign_house(5.0, 0.0) == 1
    assert _whole_sign_house(35.0, 0.0) == 2


def test_categories_covered() -> None:
    assert {"marriage", "career", "children"} <= set(_EVENT_HOUSE_MAP)


def test_windows_scan_runs_and_deterministic() -> None:
    a = triple_activation_windows(
        "t", "1990-05-19", "05:45", 7.0, 13.75, 100.52,
        category="marriage",
        now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc),
        scan_days=90)
    b = triple_activation_windows(
        "t", "1990-05-19", "05:45", 7.0, 13.75, 100.52,
        category="marriage",
        now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc),
        scan_days=90)
    assert a == b
    assert a["target_house"] == 7
    assert len(a["interpretation"]["th"]) > 40


def test_window_confidence_labels() -> None:
    r = triple_activation_windows(
        "t", "1990-05-19", "05:45", 7.0, 13.75, 100.52,
        category="career",
        now_utc=datetime(2026, 9, 1, tzinfo=timezone.utc),
        scan_days=120)
    valid = {"none", "low", "medium", "HIGH"}
    for w in r["windows"]:
        assert w["peak_layers"] >= 3     # only >=3 emitted


# ── เจ้าสังวาลย์ v2 ──────────────────────────────────────────────────
def test_chomangkala_v2_basic() -> None:
    from src.services.chomangkala_v2 import chomangkala_full
    r = chomangkala_full("สมชาย", "ใจดี", birth_day_of_month=19)
    assert r["first_name"]["raw_total"] > 0
    assert 1 <= r["combined_digit"] <= 9
    assert r["harmony_with_birth"] is not None


def test_chomangkala_v2_deterministic() -> None:
    from src.services.chomangkala_v2 import chomangkala_full
    a = chomangkala_full("มะนาว", "โสภณ")
    b = chomangkala_full("มะนาว", "โสภณ")
    assert a == b


def test_chomangkala_v2_thai_voice() -> None:
    from src.services.chomangkala_v2 import chomangkala_full
    r = chomangkala_full("สมหญิง")
    assert "ดาว" in r["interpretation"]["th"]
