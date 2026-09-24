"""Fusion engine tests — verified against the vault natal chart
(19 May 1997, 05:45 ICT, Chonburi 13.36N 100.98E).

Known ground truth (from the vault + research session):
- sidereal Moon Virgo 23.69° → nakshatra Chitra pada 1, dasha lord Mars
- Vimshottari: Jupiter MD active since 2022, Saturn MD starts 2038
- birth year pillar: Fire Ox (Ding Chou), clash partner Goat
- ตรียัมปาไถ for 19-05-1997: day 1+9=10→1, month 5, year 1+9+9+7=26→8, total 1+5+8=14→5
"""

from datetime import date, time

from src.services.fusion_engine import (
    bazi_year_pillars, fuse_daily, moon_nakshatra, triyampath_digits,
    vimshottari_now,
)

NATAL = {"name": "M", "date": date(1997, 5, 19), "time": time(5, 45)}
BIRTH_ARGS = dict(lat=13.36, lon=100.98, tz_offset_hours=7.0)


def test_bazi_fire_ox_with_goat_clash():
    b = bazi_year_pillars(date(1997, 5, 19))
    assert b["stem"] == "Ding"
    assert b["branch"] == "Ox"
    assert b["element_stem"] == "Fire"
    assert b["clash_with"] == "Goat"


def test_triyampath_known_values():
    t = triyampath_digits(date(1997, 5, 19))
    assert (t["day"], t["month"], t["year"], t["total"]) == (1, 5, 8, 5)


def test_moon_nakshatra_chitra_pada1():
    # Moon sidereal lon = 5*30 + 23.69 = 173.69
    n = moon_nakshatra(173.69)
    assert n["nakshatra"] == "Chitra"
    assert n["pada"] == 1
    assert n["lord"] == "Mars"


def test_vimshottari_jupiter_md_now_saturn_2038():
    # birth year fraction for 1997-05-19 ≈ 1997.38
    v = vimshottari_now(173.69, 1997.38, 2026.64)  # Aug 2026
    assert v["mahadasha"]["lord"] == "Jupiter"
    assert v["mahadasha"]["start"].startswith("2022")
    assert v["antardasha"] is not None
    # sanity: Saturn MD must not be active in 2026
    assert v["mahadasha"]["end"].startswith("2038")


def test_fuse_daily_full_structure():
    out = fuse_daily(NATAL, now_utc=None, **BIRTH_ARGS)
    # all three layers present
    assert out["layers"]["western_transits"]["count"] >= 0
    vedic = out["layers"]["vedic"]
    assert vedic["birth_moon_nakshatra"]["nakshatra"] == "Chitra"
    assert vedic["vimshottari"]["mahadasha"]["lord"] == "Jupiter"
    thai = out["layers"]["thai_bazi"]
    assert thai["year"].endswith("Ox (Fire)")
    # verdicts cover every life domain, each with score + evidence
    assert set(out["verdicts"].keys()) == {"career", "love", "money", "health", "growth"}
    for v in out["verdicts"].values():
        assert 5 <= v["score"] <= 95
        assert "dasha_backdrop" in v


def test_fuse_daily_deterministic():
    a = fuse_daily(NATAL, **BIRTH_ARGS)
    b = fuse_daily(NATAL, **BIRTH_ARGS)
    assert a["verdicts"] == b["verdicts"]
