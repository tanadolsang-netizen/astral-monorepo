"""Tests for Chinese BaZi Four Pillars, zodiac animal, and Wu Xing."""

from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.chinese_service import (
    HEAVENLY_STEMS,
    EARTHLY_BRANCHES,
    WU_XING,
    ELEMENT_NAMES,
    compute_bazi,
    get_zodiac,
    compute_element_analysis,
    _jdn,
    _pillar_label,
)

client = TestClient(app)

# ── Heavenly Stems ────────────────────────────────────────────────

class TestHeavenlyStems:
    def test_count(self):
        assert len(HEAVENLY_STEMS) == 10

    def test_all_have_required_keys(self):
        for stem in HEAVENLY_STEMS:
            assert "thai" in stem and "name" in stem
            assert "element" in stem and "polarity" in stem

    def test_elements_are_wu_xing(self):
        stem_elements = {s["element"] for s in HEAVENLY_STEMS}
        assert stem_elements == {"wood", "fire", "earth", "metal", "water"}

    def test_polarity_alternates(self):
        pols = [s["polarity"] for s in HEAVENLY_STEMS]
        assert pols == ["yang", "yin"] * 5

    def test_no_chinese_chars(self):
        for stem in HEAVENLY_STEMS:
            assert "chinese" not in stem


# ── Earthly Branches ─────────────────────────────────────────────

class TestEarthlyBranches:
    def test_count(self):
        assert len(EARTHLY_BRANCHES) == 12

    def test_all_have_animal(self):
        for b in EARTHLY_BRANCHES:
            assert "animal" in b and "animal_en" in b
            assert len(b["animal"].strip()) > 0

    def test_animals_are_distinct(self):
        animals = [b["animal_en"] for b in EARTHLY_BRANCHES]
        assert len(set(animals)) == 12

    def test_first_branch_is_rat(self):
        assert EARTHLY_BRANCHES[0]["animal_en"] == "Rat"
        assert EARTHLY_BRANCHES[0]["thai"] == "ชวด"

    def test_no_chinese_chars(self):
        for b in EARTHLY_BRANCHES:
            assert "chinese" not in b


# ── Year Pillar ─────────────────────────────────────────────────

class TestYearPillar:
    def test_1984_is_gia_chut(self):
        """1984 = กั่วชวด, pillar index 0"""
        p = compute_bazi(date(1984, 3, 1), time(12, 0))
        y = p["pillars"]["year"]
        assert y["stem"]["thai"] == "กั่ว"
        assert y["branch"]["thai"] == "ชวด"
        assert y["stem"]["name"] == "Gia"
        assert y["branch"]["animal_en"] == "Rat"

    def test_2024_is_gia_mam_rong(self):
        """2024 = กั่วมะโรง, pillar index 40"""
        p = compute_bazi(date(2024, 3, 1), time(12, 0))
        y = p["pillars"]["year"]
        assert y["stem"]["thai"] == "กั่ว"
        assert y["branch"]["thai"] == "มะโรง"
        assert y["branch"]["animal_en"] == "Dragon"

    def test_early_feb_uses_previous_year(self):
        """3 ก.พ. 2024 → ยังเป็นเสาปี 2023 (ก่อนวันตรุษ)"""
        p = compute_bazi(date(2024, 2, 3), time(12, 0))
        y23 = compute_bazi(date(2023, 3, 1), time(12, 0))
        assert p["pillars"]["year"]["sexagenary_index"] == y23["pillars"]["year"]["sexagenary_index"]


# ── Month Pillar ────────────────────────────────────────────────

class TestMonthPillar:
    def test_august_2024_pillar(self):
        p = compute_bazi(date(2024, 8, 15), time(12, 0))
        m = p["pillars"]["month"]
        # เดือน 7 ของปีกั่วมะโรง → เดงวอก
        assert m["stem"]["thai"] == "เดง"
        assert m["branch"]["thai"] == "วอก"
        assert m["branch"]["animal_en"] == "Monkey"


# ── Day Pillar ──────────────────────────────────────────────────

class TestDayPillar:
    def test_known_date(self):
        """ตรวจสอบจากวันหกสิบปีที่รู้จัก สำหรับ 1990-08-10"""
        p = compute_bazi(date(1990, 8, 10), time(14, 30))
        d = p["pillars"]["day"]
        assert d["stem"]["thai"] == "บุ๋ง"
        assert d["branch"]["thai"] == "วอก"

    def test_jdn_consistency(self):
        jdn = _jdn(date(2000, 1, 1))
        # วันจูเลียน 2000-01-01 คือ 2451545
        assert jdn == 2451545

    def test_pillar_label_format(self):
        label = _pillar_label(0)
        assert label["label_th"] == "กั่วชวด"
        assert label["label_en"] == "Gia-Rat"
        assert label["stem"]["index"] == 0
        assert label["branch"]["index"] == 0

    def test_no_chinese_in_pillar(self):
        label = _pillar_label(44)
        assert "chinese" not in label


# ── Hour Pillar ─────────────────────────────────────────────────

class TestHourPillar:
    def test_noon_hour(self):
        """ยาม 12-13 → ดินเสมอที่ 6 (มะเมีย)"""
        p = compute_bazi(date(2024, 8, 15), time(12, 0))
        h = p["pillars"]["hour"]
        assert h["branch"]["animal_en"] == "Horse"

    def test_midnight_hour(self):
        """ยาม 0-1 → ดินเสมอที่ 0 (ชวด)"""
        p = compute_bazi(date(2024, 8, 15), time(0, 0))
        h = p["pillars"]["hour"]
        assert h["branch"]["animal_en"] == "Rat"

    def test_late_night_hour(self):
        """ยาม 23-00 → ดินเสมอที่ 0 (ชวด)"""
        p = compute_bazi(date(2024, 8, 15), time(23, 30))
        h = p["pillars"]["hour"]
        assert h["branch"]["animal_en"] == "Rat"


# ── Zodiac Animal ───────────────────────────────────────────────

class TestZodiacAnimal:
    def test_2024_dragon(self):
        z = get_zodiac(2024)
        assert z["animal_en"] == "Dragon"
        assert z["element"] == "earth"
        assert "มะโรง" in z["note"]

    def test_2023_rabbit(self):
        z = get_zodiac(2023)
        assert z["animal_en"] == "Rabbit"

    def test_2020_rat(self):
        z = get_zodiac(2020)
        assert z["animal_en"] == "Rat"

    def test_all_12_covered(self):
        animals = [get_zodiac(2024 - i)["animal_en"] for i in range(12)]
        assert set(animals) == {
            "Dragon", "Rabbit", "Tiger", "Ox", "Rat", "Pig",
            "Dog", "Rooster", "Monkey", "Goat", "Horse", "Snake",
        }

    def test_buddhist_year(self):
        z = get_zodiac(2025)
        assert z["buddhist_year"] == 2568


# ── Element Balance ─────────────────────────────────────────────

class TestElementBalance:
    def test_all_five_elements(self):
        p = compute_bazi(date(1990, 5, 15), time(14, 30))
        counts = p["element_balance"]["counts"]
        assert set(counts.keys()) == set(ELEMENT_NAMES)

    def test_counts_sum_to_8(self):
        """4 ฟ้าismeปี + 4 ดินเสมอ = 8 การจัดสรรธาตุ"""
        p = compute_bazi(date(1990, 5, 15), time(14, 30))
        assert sum(p["element_balance"]["counts"].values()) == 8

    def test_yin_yang_sum_to_8(self):
        p = compute_bazi(date(1990, 5, 15), time(14, 30))
        y = p["yin_yang_balance"]
        assert y["yang"] + y["yin"] == 8

    def test_dominant_and_lacking(self):
        p = compute_bazi(date(1990, 5, 15), time(14, 30))
        eb = p["element_balance"]
        assert eb["dominant"] in ELEMENT_NAMES
        assert eb["lacking"] in ELEMENT_NAMES

    def test_element_analysis_breakdown(self):
        a = compute_element_analysis(date(1990, 5, 15), time(14, 30))
        assert set(a["breakdown"].keys()) == set(ELEMENT_NAMES)
        for el_info in a["breakdown"].values():
            assert "thai" in el_info
            assert "count" in el_info
            assert "percent" in el_info


# ── API Integration ─────────────────────────────────────────────

def test_bazi_endpoint():
    res = client.post("/v1/chinese/bazi", json={"date": "1990-05-15", "time": "14:30:00"})
    assert res.status_code == 200
    body = res.json()
    assert "pillars" in body
    assert all(k in body["pillars"] for k in ("year", "month", "day", "hour"))
    assert "caveat" in body
    assert body["element_balance"]["counts"]["fire"] >= 0


def test_zodiac_endpoint():
    res = client.post("/v1/chinese/zodiac", json={"year": 2024})
    assert res.status_code == 200
    body = res.json()
    assert body["animal_en"] == "Dragon"
    assert body["year"] == 2024
    assert "caveat" in body


def test_element_endpoint():
    res = client.post("/v1/chinese/element", json={"date": "2000-01-01", "time": "00:00:00"})
    assert res.status_code == 200
    body = res.json()
    assert "breakdown" in body
    assert "dominant" in body
    assert "caveat" in body


def test_bazi_endpoint_invalid_date():
    res = client.post("/v1/chinese/bazi", json={"date": "not-a-date", "time": "12:00:00"})
    # Pydantic validation rejects malformed dates with 422 before the handler runs.
    assert res.status_code == 422
