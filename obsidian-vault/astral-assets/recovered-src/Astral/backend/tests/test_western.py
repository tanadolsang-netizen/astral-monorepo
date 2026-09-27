"""Comprehensive tests for the Western astrology system.

Covers:
- Placidus / Koch house cusps and house_system selector
- Essential dignities (domicile, exaltation, detriment, fall)
- Essential dignity scores
- Progressed chart endpoint
- Solar return endpoint
- Lunar return endpoint
"""

from datetime import date, time

from fastapi.testclient import TestClient

from src.main import app
from src.services.chart_service import (
    BODIES,
    DOMICILE,
    DETRIMENT,
    EXALTATION,
    FALL,
    HOUSE_SYSTEMS,
    SIGNS,
    compute_chart,
    compute_dignity,
    compute_houses,
)
from src.services.progressions_service import compute_progressions, progressed_date
from src.services.returns_service import compute_lunar_return, compute_solar_return

client = TestClient(app)

_BIRTH_DATE = date(1990, 5, 15)
_BIRTH_TIME = time(14, 30)
_LAT = 13.7563
_LON = 100.5018


# ---------------------------------------------------------------------------
# 1. House system: Placidus / Koch / selector
# ---------------------------------------------------------------------------

class TestPlacidusKochHouses:
    def _chart(self, house_system: str):
        return compute_chart(
            name="Houses",
            date=_BIRTH_DATE,
            time=_BIRTH_TIME,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
            system="tropical",
            house_system=house_system,
        )

    def test_placidus_returns_12_cusps(self):
        chart = self._chart("placidus")
        assert len(chart["houses"]["cusps"]) == 12
        assert chart["houses"]["house_system"] == "placidus"

    def test_koch_returns_12_cusps(self):
        chart = self._chart("koch")
        assert len(chart["houses"]["cusps"]) == 12
        assert chart["houses"]["house_system"] == "koch"

    def test_placidus_and_koch_differ(self):
        placidus = self._chart("placidus")
        koch = self._chart("koch")
        p_degs = [c["absolute_deg"] for c in placidus["houses"]["cusps"]]
        k_degs = [c["absolute_deg"] for c in koch["houses"]["cusps"]]
        assert p_degs != k_degs

    def test_house_cusps_in_range(self):
        for hs in HOUSE_SYSTEMS:
            chart = self._chart(hs)
            for cusp in chart["houses"]["cusps"]:
                assert 0 <= cusp["degree"] < 30, f"house {cusp['house']} out of range"
                assert 0 <= cusp["absolute_deg"] < 360

    def test_house_1_is_ascendant(self):
        for hs in HOUSE_SYSTEMS:
            chart = self._chart(hs)
            h1 = chart["houses"]["cusps"][0]
            assert h1["house"] == 1
            asc = chart["ascendant"]
            assert h1["absolute_deg"] == asc["absolute_deg"]

    def test_house_10_is_midheaven(self):
        for hs in HOUSE_SYSTEMS:
            chart = self._chart(hs)
            h10 = next(c for c in chart["houses"]["cusps"] if c["house"] == 10)
            mc = chart["midheaven"]
            assert h10["absolute_deg"] == mc["absolute_deg"]

    def test_default_house_system_is_placidus(self):
        chart = compute_chart(
            name="Default",
            date=_BIRTH_DATE,
            time=_BIRTH_TIME,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert chart["houses"]["house_system"] == "placidus"

    def test_invalid_house_system_raises(self):
        try:
            compute_houses(
                dt_utc=date(1990, 5, 15),
                lat=_LAT,
                lon=_LON,
                system="tropical",
                house_system="invalid",
            )
            assert False, "Expected ValueError"
        except ValueError:
            pass

    def test_compute_chart_with_house_system_param(self):
        for hs in HOUSE_SYSTEMS:
            chart = compute_chart(
                name="Test",
                date=_BIRTH_DATE,
                time=_BIRTH_TIME,
                tz_offset_hours=7.0,
                lat=_LAT,
                lon=_LON,
                house_system=hs,
            )
            assert chart["houses"]["house_system"] == hs


# ---------------------------------------------------------------------------
# 2. Essential dignities
# ---------------------------------------------------------------------------

class TestEssentialDignities:
    def test_domicile_table_covers_all_bodies(self):
        for body in BODIES:
            assert body in DOMICILE, f"{body} missing from DOMICILE"

    def test_exaltation_table_covers_classical_planets(self):
        classical = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for body in classical:
            assert body in EXALTATION, f"{body} missing from EXALTATION"

    def test_detriment_opposite_domicile(self):
        for body, domiciles in DOMICILE.items():
            for dom in domiciles:
                dom_idx = SIGNS.index(dom)
                det_idx = (dom_idx + 6) % 12
                assert SIGNS[det_idx] in DETRIMENT[body]

    def test_fall_opposite_exaltation(self):
        for body, exalt in EXALTATION.items():
            exalt_idx = SIGNS.index(exalt)
            fall_idx = (exalt_idx + 6) % 12
            assert SIGNS[fall_idx] == FALL[body]

    def test_domicile_signs_are_valid(self):
        for body, signs in DOMICILE.items():
            for s in signs:
                assert s in SIGNS

    def test_sun_in_aries_is_exalted(self):
        result = compute_dignity("Sun", "เมษ(Aries)")
        assert result["exaltation"] is True
        assert result["score"] == 4

    def test_sun_in_leo_is_domicile(self):
        result = compute_dignity("Sun", "สิงห์(Leo)")
        assert result["domicile"] is True
        assert result["score"] == 5

    def test_sun_in_aquarius_is_detriment(self):
        result = compute_dignity("Sun", "กุมภ์(Aquarius)")
        assert result["detriment"] is True
        assert result["score"] == -5

    def test_sun_in_libra_is_fall(self):
        result = compute_dignity("Sun", "ตุลย์(Libra)")
        assert result["fall"] is True
        assert result["score"] == -4

    def test_peregrine_when_no_dignity(self):
        result = compute_dignity("Sun", "พฤษภ(Taurus)")
        assert result["domicile"] is False
        assert result["exaltation"] is False
        assert result["detriment"] is False
        assert result["fall"] is False
        assert result["score"] == 0
        assert result["label"] == "peregrine"


# ---------------------------------------------------------------------------
# 3. Dignity scores in chart computation
# ---------------------------------------------------------------------------

class TestDignityScoresInChart:
    def _chart(self):
        return compute_chart(
            name="Dignities",
            date=_BIRTH_DATE,
            time=_BIRTH_TIME,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )

    def test_all_bodies_have_dignity(self):
        chart = self._chart()
        for body in chart["bodies"]:
            assert "dignity" in body, f"{body['body']} missing dignity"
            assert "score" in body["dignity"]
            assert "label" in body["dignity"]

    def test_dignity_score_range(self):
        chart = self._chart()
        for body in chart["bodies"]:
            s = body["dignity"]["score"]
            assert -9 <= s <= 9, f"{body['body']} score {s} out of range"

    def test_dignity_label_valid(self):
        valid = {"domicile", "exaltation", "detriment", "fall", "peregrine"}
        chart = self._chart()
        for body in chart["bodies"]:
            assert body["dignity"]["label"] in valid

    def test_each_body_matches_compute_dignity(self):
        chart = self._chart()
        for body in chart["bodies"]:
            expected = compute_dignity(body["body"], body["sign"])
            assert body["dignity"] == expected

    def test_chart_has_cumulative_dignity_score(self):
        chart = self._chart()
        total = sum(b["dignity"]["score"] for b in chart["bodies"])
        assert isinstance(total, int)

    def test_domicile_flag_matches_label(self):
        chart = self._chart()
        for body in chart["bodies"]:
            if body["dignity"]["label"] == "domicile":
                assert body["dignity"]["domicile"] is True
            if body["dignity"]["label"] == "exaltation":
                assert body["dignity"]["exaltation"] is True
            if body["dignity"]["label"] == "detriment":
                assert body["dignity"]["detriment"] is True
            if body["dignity"]["label"] == "fall":
                assert body["dignity"]["fall"] is True


# ---------------------------------------------------------------------------
# 4. Progressed chart endpoint
# ---------------------------------------------------------------------------

class TestProgressedChart:
    def test_progressions_service_basic(self):
        result = compute_progressions(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2020, 5, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert "natal" in result
        assert "progressed" in result
        assert "aspects_to_natal" in result
        assert result["age_years"] > 0

    def test_progressed_date_rule(self):
        bd = date(2000, 1, 1)
        td = date(2020, 1, 1)
        pd = progressed_date(bd, td)
        age = round((td - bd).days / 365.25)
        expected = bd + __import__("datetime").timedelta(days=age)
        assert pd == expected

    def test_progressed_chart_endpoint(self):
        res = client.post(
            "/v1/western/progressions",
            json={
                "name": "Prog",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2020-05-15",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
                "system": "tropical",
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert "natal" in body
        assert "progressed" in body
        assert "aspects_to_natal" in body
        assert "caveat" in body
        assert len(body["progressed"]["bodies"]) == 10

    def test_progressed_bodies_have_dignities(self):
        res = client.post(
            "/v1/western/progressions",
            json={
                "name": "Prog",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2020-05-15",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        for body in res.json()["progressed"]["bodies"]:
            assert "dignity" in body

    def test_progressed_different_from_natal(self):
        res = client.post(
            "/v1/western/progressions",
            json={
                "name": "Prog",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2024-01-01",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        natal_bodies = {b["body"]: b["absolute_deg"] for b in res.json()["natal"]["bodies"]}
        prog_bodies = {b["body"]: b["absolute_deg"] for b in res.json()["progressed"]["bodies"]}
        diffs = [abs(natal_bodies[b] - prog_bodies[b]) for b in natal_bodies]
        assert any(d > 0.01 for d in diffs), "Progressed chart should differ from natal"

    def test_sidereal_progressions(self):
        res = client.post(
            "/v1/western/progressions",
            json={
                "name": "Prog",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2020-05-15",
                "system": "sidereal",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        assert res.json()["progressed"]["system"] == "sidereal"


# ---------------------------------------------------------------------------
# 5. Solar return endpoint
# ---------------------------------------------------------------------------

class TestSolarReturn:
    def test_solar_return_service(self):
        result = compute_solar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_year=2024,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert "chart" in result
        assert result["body"] == "Sun"
        assert "target_year" in result
        assert result["target_year"] == 2024
        assert "natal" in result

    def test_solar_return_endpoint(self):
        res = client.post(
            "/v1/western/solar-return",
            json={
                "name": "Solar",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_year": 2024,
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["body"] == "Sun"
        assert "chart" in body
        assert "caveat" in body
        assert len(body["chart"]["bodies"]) == 10

    def test_solar_return_sun_near_natal_longitude(self):
        result = compute_solar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_year=2024,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        natal_sun_lon = result["natal_longitude"]
        solar_sun = next(
            b for b in result["chart"]["bodies"] if b["body"] == "Sun"
        )
        diff = abs(solar_sun["absolute_deg"] - natal_sun_lon)
        assert diff < 1.0, f"Solar return Sun {diff:.2f}deg from natal"

    def test_solar_return_relocation(self):
        result = compute_solar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_year=2024,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
            return_lat=40.7128,
            return_lon=-74.0060,
        )
        assert result["chart"]["bodies"]
        relocated_asc = result["chart"]["ascendant"]
        natal_chart = compute_chart(
            name="Test",
            date=_BIRTH_DATE,
            time=_BIRTH_TIME,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert relocated_asc["absolute_deg"] != natal_chart["ascendant"]["absolute_deg"]

    def test_solar_return_sidereal(self):
        res = client.post(
            "/v1/western/solar-return",
            json={
                "name": "Solar",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_year": 2024,
                "system": "sidereal",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        assert res.json()["chart"]["system"] == "sidereal"


# ---------------------------------------------------------------------------
# 6. Lunar return endpoint
# ---------------------------------------------------------------------------

class TestLunarReturn:
    def test_lunar_return_service(self):
        result = compute_lunar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2024, 6, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert "chart" in result
        assert result["body"] == "Moon"
        assert "target_date" in result
        assert "natal" in result

    def test_lunar_return_endpoint(self):
        res = client.post(
            "/v1/western/lunar-return",
            json={
                "name": "Lunar",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2024-06-15",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        body = res.json()
        assert body["body"] == "Moon"
        assert "chart" in body
        assert "caveat" in body
        assert len(body["chart"]["bodies"]) == 10

    def test_lunar_return_moon_near_natal_longitude(self):
        result = compute_lunar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2024, 6, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        natal_moon_lon = result["natal_longitude"]
        lunar_moon = next(
            b for b in result["chart"]["bodies"] if b["body"] == "Moon"
        )
        diff = abs(lunar_moon["absolute_deg"] - natal_moon_lon)
        assert diff < 1.0, f"Lunar return Moon {diff:.2f}deg from natal"

    def test_lunar_return_relocation(self):
        result = compute_lunar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2024, 6, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
            return_lat=40.7128,
            return_lon=-74.0060,
        )
        relocated_asc = result["chart"]["ascendant"]
        natal_chart = compute_chart(
            name="Test",
            date=_BIRTH_DATE,
            time=_BIRTH_TIME,
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        assert relocated_asc["absolute_deg"] != natal_chart["ascendant"]["absolute_deg"]

    def test_lunar_return_sidereal(self):
        res = client.post(
            "/v1/western/lunar-return",
            json={
                "name": "Lunar",
                "date": "1990-05-15",
                "time": "14:30:00",
                "target_date": "2024-06-15",
                "system": "sidereal",
                "tz_offset_hours": 7,
                "lat": _LAT,
                "lon": _LON,
            },
        )
        assert res.status_code == 200
        assert res.json()["chart"]["system"] == "sidereal"

    def test_lunar_returns_recurrence(self):
        r1 = compute_lunar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2024, 3, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        r2 = compute_lunar_return(
            name="Test",
            birth_date=_BIRTH_DATE,
            birth_time=_BIRTH_TIME,
            target_date=date(2024, 4, 15),
            tz_offset_hours=7.0,
            lat=_LAT,
            lon=_LON,
        )
        diff_days = abs(
            (r1["return_datetime_utc"][:10] != r2["return_datetime_utc"][:10])
        )
        assert r1["return_datetime_utc"] != r2["return_datetime_utc"]
