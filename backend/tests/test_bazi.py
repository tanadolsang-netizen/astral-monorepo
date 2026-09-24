"""Spec 04 BaZi engine — verified ground truths + endpoint contract."""

from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.bazi_service import (
    four_pillars,
    jdn,
    yearly_relations,
)

client = TestClient(app)


# ── JDN arithmetic ────────────────────────────────────────────────────

def test_jdn_matches_spec():
    assert jdn(1997, 5, 19) == 2450588
    assert jdn(2001, 8, 18) == 2452140


# ── Four pillars (spec 04 §1 ground truth) ────────────────────────────

def test_owner_four_pillars():
    r = four_pillars(date(1997, 5, 19), time(5, 45))
    p = r["pillars"]
    assert p["year"]["pillar"] == "丁丑"
    assert p["month"]["pillar"] == "乙巳"
    assert p["day"]["pillar"] == "辛酉"
    assert p["hour"]["pillar"] == "辛卯"
    assert r["jdn"] == 2450588
    assert r["day_master"]["stem"] == "辛"
    assert r["day_master"]["label_th"] == "โลหะหยิน"


def test_mai_four_pillars():
    r = four_pillars(date(2001, 8, 18), time(22, 32))
    p = r["pillars"]
    assert p["year"]["pillar"] == "辛巳"
    assert p["month"]["pillar"] == "丙申"
    assert p["day"]["pillar"] == "癸丑"
    assert p["hour"]["pillar"] == "癸亥"
    assert r["day_master"]["stem"] == "癸"


def test_year_lichun_cutoff():
    # Before Feb 4 -> previous BaZi year: 1997-02-01 belongs to 丙子.
    r = four_pillars(date(1997, 2, 1), time(12, 0))
    assert r["pillars"]["year"]["pillar"] == "丙子"
    # Near-cutoff dates carry MEDIUM confidence (fixed-date Lichun approx).
    assert r["pillars"]["year"]["confidence"] == "MEDIUM"
    assert four_pillars(date(1997, 5, 19), time(5, 45))["pillars"]["year"]["confidence"] == "HIGH"


def test_month_confidence_medium():
    r = four_pillars(date(1997, 5, 19), time(5, 45))
    assert r["confidence"]["month"] == "MEDIUM"


def test_late_zi_hour_uses_next_day_stem():
    # 23:10 on a 辛 day -> late 子 hour, stem from the NEXT (壬) day stem:
    # 壬 day -> 子-hour stem 庚 -> pillar 庚子.
    r = four_pillars(date(1997, 5, 19), time(23, 10))
    hour = r["pillars"]["hour"]
    assert hour["branch"] == "子"
    assert hour["late_zi"] is True
    assert hour["stem"] == "庚"


def test_hour_branch_boundaries():
    assert four_pillars(date(2001, 8, 18), time(22, 32))["pillars"]["hour"]["branch"] == "亥"
    assert four_pillars(date(2001, 8, 18), time(0, 30))["pillars"]["hour"]["branch"] == "子"


# ── Yearly clash/harm generator (spec 04 §3) ──────────────────────────

def test_ox_person_yearly_clash_harm():
    r = yearly_relations(date(1997, 5, 19), [2026, 2027])
    by_year = {y["year"]: y for y in r["years"]}
    # 2026 丙午 fire horse: Ox -> HARM 丑午
    assert by_year[2026]["pillar"] == "丙午"
    assert by_year[2026]["relation"] == "harm"
    assert by_year[2026]["pair"] == "丑午"
    assert by_year[2026]["en"] == "Ox-harm-Horse"
    # 2027 丁未 fire goat: Ox -> CLASH 丑未
    assert by_year[2027]["pillar"] == "丁未"
    assert by_year[2027]["relation"] == "clash"
    assert by_year[2027]["pair"] == "丑未"
    assert by_year[2027]["en"] == "Ox-clash-Goat"


def test_snake_person_2026_neutral():
    # Mai = 巳 year: spec table says 午↔巳 neutral ("กลาง ๆ").
    r = yearly_relations(date(2001, 8, 18), [2026])
    assert r["years"][0]["relation"] is None


# ── Endpoints ─────────────────────────────────────────────────────────

def test_pillars_get_endpoint():
    res = client.get(
        "/v1/bazi/pillars",
        params={"date": "1997-05-19", "time": "05:45", "tz_offset_hours": 7},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["pillars"]["day"]["pillar"] == "辛酉"
    assert body["day_master"]["stem"] == "辛"
    assert set(body["confidence"].values()) >= {"HIGH", "MEDIUM"}
    assert "caveat" in body


def test_pillars_post_endpoint():
    res = client.post(
        "/v1/bazi/pillars",
        json={"name": "ไหม", "date": "2001-08-18", "time": "22:32", "tz_offset_hours": 7},
    )
    assert res.status_code == 200
    body = res.json()
    assert [body["pillars"][k]["pillar"] for k in ("year", "month", "day", "hour")] == [
        "辛巳", "丙申", "癸丑", "癸亥",
    ]
    assert body["zodiac_en"] == "Snake"


def test_yearly_get_endpoint():
    res = client.get(
        "/v1/bazi/yearly",
        params={"birth_date": "1997-05-19", "years": "2026,2027"},
    )
    assert res.status_code == 200
    years = {y["year"]: y for y in res.json()["years"]}
    assert years[2026]["relation"] == "harm"
    assert years[2027]["relation"] == "clash"


def test_yearly_post_endpoint():
    res = client.post(
        "/v1/bazi/yearly",
        json={"birth": {"date": "1997-05-19"}, "years": [2027]},
    )
    assert res.status_code == 200
    assert res.json()["years"][0]["relation"] == "clash"
