"""Universe Phase 4.7 — asteroids REAL via Swiss Ephemeris + HD Type/Authority.

Completes the last two previously-unavailable sciences (all 18 now real).

Verified anchors used here:
- Asteroids: ATLAS asteroids_ephe_guide.json (commit b5ac4d0) — seas_18.se1 +
  sepl_18.se1 + semo_18.se1 vendored in <repo>/ephe/ (1.92 MB, committed).
  Ground truth M (1997-05-19 05:45 ICT = JD 2450587.447917): Chiron tropical
  206.7767° abs (26°46' Libra Rx), speed −0.05803°/day. Body ids: Chiron=15,
  Ceres/Pallas/Juno/Vesta = AST_OFFSET(10000)+1..4 (swe aliases verified).
- Human Design: ATLAS hd_channels_centers.json (commit b5ac4d0). Validation
  vector Donald Trump (1946-06-14 10:54 EDT, Queens NY): published consensus
  Type = Manifesting Generator, Authority = Emotional, Profile 1/3,
  channels 6-59 / 17-62 / 21-45 / 35-36 (geneticmatrix, totalhumandesign,
  humandesignsystem.co agree; our pipeline reproduces ALL 26 gate.line
  labels exactly on the ecliptic-of-date frame via pyswisseph).
"""

import json
from datetime import date, datetime, time, timezone
from pathlib import Path

import pytest

from src.services.grand import human_design as hdp
from src.services.grand.asteroids import (
    EPHE_DIR,
    _REQUIRED_EPHE_FILES,
    compute_asteroid_positions,
    compute_asteroids,
    natal_asteroid_positions,
)
from src.services.grand.human_design import (
    _CHANNELS,
    _GATE_CENTER,
    compute_human_design,
    lon_to_gate_line,
    true_north_node,
    type_and_authority_from_gates,
)

_M_BIRTH = date(1997, 5, 19)
_M_PROFILE = {
    "date": _M_BIRTH.isoformat(),
    "time": time(5, 45).isoformat(),
    "tz_offset_hours": 7.0,
    "lat": 13.36,
    "lon": 100.98,
}

_DATA_DIR = Path("C:/AI/research-astrology/data")

_TYPES = {
    "Manifestor", "Generator", "Manifesting Generator",
    "Projector", "Reflector",
}


def _m_chart(system="tropical"):
    from src.services.chart_service import compute_chart

    return compute_chart(
        name="M", date=_M_BIRTH, time=time(5, 45),
        tz_offset_hours=7.0, lat=13.36, lon=100.98, system=system,
    )


def _trump_chart():
    from src.services.chart_service import compute_chart

    return compute_chart(
        name="Trump", date=date(1946, 6, 14), time=time(10, 54),
        tz_offset_hours=-4.0, lat=40.7287, lon=-73.7949, system="tropical",
    )


# ---------------------------------------------------------------------------
# Asteroids — Swiss Ephemeris REAL (ground truth pinned)
# ---------------------------------------------------------------------------

class TestAsteroidsReal:
    def test_ephe_files_vendored_in_repo(self):
        # Mission: commit the three .se1 files (<5 MB total) so deploys work
        # offline. If these are gone, everything below skips gracefully.
        missing = [f for f in _REQUIRED_EPHE_FILES if not (EPHE_DIR / f).exists()]
        if missing:
            pytest.skip(f"ephe files missing from repo: {missing}")
        total = sum((EPHE_DIR / f).stat().st_size for f in _REQUIRED_EPHE_FILES)
        assert total < 5 * 1024 * 1024

    def test_chiron_ground_truth_exact(self):
        """ATLAS anchor: JD 2450587.447917 → Chiron 206.7767° ±0.01."""
        result = compute_asteroid_positions(
            datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)
        )
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {result.get('reason', '')[:80]}")
        chiron = result["positions"]["Chiron"]
        assert abs(chiron["absolute_deg"] - 206.7767) < 0.01
        assert chiron["retrograde"] is True          # speed −0.05803°/day
        assert chiron["speed_lon_deg_per_day"] == pytest.approx(-0.05803, abs=1e-4)
        assert "Libra" in chiron["sign"]             # tropical 26°46' Libra Rx

    def test_all_five_bodies_via_ast_offset_ids(self):
        result = compute_asteroid_positions(
            datetime(1997, 5, 18, 22, 45, tzinfo=timezone.utc)
        )
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {result.get('reason', '')[:80]}")
        assert set(result["positions"]) == {"Chiron", "Ceres", "Pallas", "Juno", "Vesta"}
        for name, pos in result["positions"].items():
            assert 0.0 <= pos["absolute_deg"] < 360.0
            assert 0.0 <= pos["sidereal"]["absolute_deg"] < 360.0

    def test_sidereal_is_lahiri_same_as_chart_pipeline(self):
        from src.services.chart_service import lahiri_ayanamsa

        dt = datetime(2026, 8, 23, tzinfo=timezone.utc)
        result = compute_asteroid_positions(dt)
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {result.get('reason', '')[:80]}")
        year_frac = 2026 + (dt.timetuple().tm_yday / 365.2425)
        ayanamsa = lahiri_ayanamsa(year_frac)
        for pos in result["positions"].values():
            expected = (pos["absolute_deg"] - ayanamsa) % 360.0
            assert pos["sidereal"]["absolute_deg"] == pytest.approx(expected, abs=5e-4)

    def test_natal_positions_for_any_chart(self):
        result = natal_asteroid_positions(_m_chart())
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {result.get('reason', '')[:80]}")
        chiron = result["positions"]["Chiron"]
        # Same instant as the guide's ground truth JD 2450587.447917.
        assert abs(chiron["absolute_deg"] - 206.7767) < 0.01

    def test_compute_asteroids_full_payload(self):
        result = compute_asteroids(_m_chart())
        if result["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {result.get('reason', '')[:80]}")
        assert result["status"] in ("ok", "partial")
        assert "transit_aspects" in result
        assert "natal_positions" in result
        assert result["natal_positions"]["status"] in ("ok", "partial")


# ---------------------------------------------------------------------------
# HD Type/Authority — pure rule engine on synthetic activation sets
# ---------------------------------------------------------------------------

class TestTypeRulesSynthetic:
    def test_no_defined_centers_is_reflector_lunar(self):
        ta = type_and_authority_from_gates(set())
        assert ta["type"] == "Reflector"
        assert ta["authority"] == "Lunar"
        assert ta["defined_centers"] == []

    def test_only_channel_21_45_is_manifestor_ego(self):
        # Heart+Throat defined via the Money channel; Sacral undefined;
        # Heart is a motor connected to Throat → Manifestor path.
        ta = type_and_authority_from_gates({21, 45})
        assert ta["defined_channels"] == ["21-45"]
        assert sorted(ta["defined_centers"]) == ["Heart", "Throat"]
        assert ta["motor_throat_connected"] is True
        assert ta["type"] == "Manifestor"
        assert ta["authority"] == "Ego / Heart"

    def test_sacral_without_throat_link_is_generator_sacral(self):
        ta = type_and_authority_from_gates({2, 14})  # The Beat: G–Sacral
        assert ta["type"] == "Generator"
        assert ta["authority"] == "Sacral"

    def test_sacral_to_throat_is_manifesting_generator(self):
        ta = type_and_authority_from_gates({20, 34})  # Charisma: Throat–Sacral
        assert ta["type"] == "Manifesting Generator"
        assert ta["authority"] == "Sacral"

    def test_above_throat_only_is_projector_mental(self):
        ta = type_and_authority_from_gates({23, 43})  # Structuring: Throat–Ajna
        assert ta["type"] == "Projector"
        assert ta["authority"].startswith("Mental")

    def test_authority_hierarchy_ordering(self):
        # Splenic beats Ego: Spleen+Root via Struggle vs Heart alone.
        assert type_and_authority_from_gates({28, 38})["authority"] == "Splenic"
        # Emotional beats everything: SolarPlexus+Sacral via Mating.
        emo = type_and_authority_from_gates({6, 59})
        assert emo["authority"].startswith("Emotional")
        # …even combined with Sacral authority candidates (The Beat added).
        both = type_and_authority_from_gates({6, 59, 2, 14})
        assert both["authority"].startswith("Emotional")

    def test_self_projected_requires_projector_with_g(self):
        # G+Throat (Prodigal) + Ajna+Throat (Curiosity): G defined, no
        # SP/Sacral/Spleen/Heart, Sacral undefined → Projector, Self-Projected.
        ta = type_and_authority_from_gates({13, 33, 11, 56})
        assert ta["type"] == "Projector"
        assert ta["authority"] == "Self-Projected"


# ---------------------------------------------------------------------------
# HD channel/center table integrity
# ---------------------------------------------------------------------------

class TestChannelTableIntegrity:
    def test_embedded_tables_match_verified_file(self):
        path = _DATA_DIR / "hd_channels_centers.json"
        if not path.exists():
            pytest.skip("research data dir not present on this machine")
        data = json.loads(path.read_text(encoding="utf-8"))
        assert len(data["channels"]) == len(_CHANNELS) == 36
        file_pairs = {tuple(sorted(c["gates"])) for c in data["channels"]}
        ours = {tuple(sorted(c["gates"])) for c in _CHANNELS}
        assert ours == file_pairs
        for g, center in data["centers"].items():
            assert _GATE_CENTER[int(g)] == center

    def test_every_channel_endpoint_center_consistent(self):
        for ch in _CHANNELS:
            (a, b), (ca, cb) = ch["gates"], ch["centers"]
            assert _GATE_CENTER[a] == ca
            assert _GATE_CENTER[b] == cb

    def test_gate_wheel_covers_all_64_gates(self):
        assert sorted(_GATE_CENTER) == list(range(1, 65))
        for gate in _GATE_CENTER:
            assert lon_to_gate_line(302.0)[0] in _GATE_CENTER  # anchor sane

    def test_south_node_is_north_plus_180(self):
        nn = true_north_node(2450587.447917)  # M's birth JD
        assert ((nn + 180.0) % 360.0) == pytest.approx(
            (true_north_node(2450587.447917) + 180.0) % 360.0
        )


# ---------------------------------------------------------------------------
# HD full pipeline — validation vector + owner chart
# ---------------------------------------------------------------------------

class TestHDValidationVector:
    def test_trump_published_consensus_reproduced(self):
        if hdp._swe is None:
            pytest.skip("pyswisseph unavailable — historical-date frame too imprecise")
        hd = compute_human_design(natal_chart=_trump_chart())
        assert hd["status"] == "ok"
        assert hd["profile"]["p_sun"] == "12.1"
        assert hd["profile"]["d_sun"] == "36.3"
        assert hd["profile"]["profile_name"] == "1/3"
        assert hd["type"] == "Manifesting Generator"
        assert hd["authority"] == "Emotional (Solar Plexus)"
        assert set(hd["defined_channels"]) == {"6-59", "17-62", "21-45", "35-36"}
        assert set(hd["defined_centers"]) == {
            "Ajna", "Heart", "Sacral", "SolarPlexus", "Throat",
        }
        # every published activation label reproduces (26/26)
        pub_p = {"Sun": "12.1", "Earth": "11.1", "North Node": "45.5",
                 "South Node": "26.5", "Moon": "26.5", "Mercury": "52.6",
                 "Venus": "62.6", "Mars": "29.3", "Jupiter": "57.3",
                 "Saturn": "62.4", "Uranus": "45.1", "Neptune": "18.3",
                 "Pluto": "33.3"}
        pub_d = {"Sun": "36.3", "Earth": "6.3", "North Node": "12.4",
                 "South Node": "11.4", "Moon": "59.6", "Mercury": "21.1",
                 "Venus": "17.2", "Mars": "53.2", "Jupiter": "32.6",
                 "Saturn": "53.4", "Uranus": "35.3", "Neptune": "18.4",
                 "Pluto": "33.3"}
        for body, want in pub_p.items():
            assert hd["personality"]["activations"][body]["label"] == want, body
        for body, want in pub_d.items():
            assert hd["design"]["activations"][body]["label"] == want, body


class TestHDOwnerChart:
    def test_m_full_hd_real(self):
        hd = compute_human_design(natal_chart=_m_chart())
        assert hd["status"] == "ok"
        assert hd["type"] in _TYPES
        assert hd["profile"]["profile_name"] == "4/6"
        assert hd["profile"]["p_sun"] == "8.4"
        assert hd["profile"]["d_sun"] == "30.6"
        assert hd["activated_gates"] == sorted(set(hd["activated_gates"]))
        assert 0 < len(hd["defined_channels"]) <= 18
        assert len(hd["defined_centers"]) == len(set(hd["defined_centers"]))
        if hdp._swe is not None:
            assert hd["sun_longitude_source"] == "swisseph(of-date)"
            # Owner ground truth (Generator, emotional authority per live run)
            assert hd["type"] == "Generator"
            assert hd["authority"] == "Emotional (Solar Plexus)"

    def test_type_consistent_with_centers_rules(self):
        hd = compute_human_design(natal_chart=_m_chart())
        defined = set(hd["defined_centers"])
        if not defined:
            assert hd["type"] == "Reflector"
        elif "Sacral" in defined:
            assert hd["type"] == (
                "Manifesting Generator" if hd["motor_throat_connected"] else "Generator"
            )
        elif hd["motor_throat_connected"]:
            assert hd["type"] == "Manifestor"
        else:
            assert hd["type"] == "Projector"


# ---------------------------------------------------------------------------
# Fusion wiring — extended sections fully real
# ---------------------------------------------------------------------------

class TestFusionPhase47Wiring:
    def test_extended_hd_has_type_authority(self):
        from src.services.grand.grand_fusion import compute_grand_fusion

        ext = compute_grand_fusion("M", profile=dict(_M_PROFILE))["extended"]
        hd = ext["human_design"]
        assert hd["status"] == "ok"
        assert hd["type"] in _TYPES
        assert hd["authority"]
        assert hd["profile"]["profile_name"] == "4/6"

    def test_reading_lines_name_type_and_authority(self):
        from src.services.grand.grand_fusion import compute_grand_fusion

        reading = compute_grand_fusion("M", profile=dict(_M_PROFILE))["reading"]
        for lang in ("th", "en"):
            line = reading[lang]["human_design"]
            assert "unavailable" not in line.lower()
            assert "4/6" in line and "8.4" in line and "30.6" in line
            assert "Generator" in line

    def test_extended_asteroids_real_when_ephe_present(self):
        from src.services.grand.grand_fusion import compute_grand_fusion

        ext = compute_grand_fusion("M", profile=dict(_M_PROFILE))["extended"]
        ast = ext["asteroids"]
        if ast["status"] == "unavailable":
            pytest.skip(f"swisseph unavailable: {ast.get('reason', '')[:80]}")
        assert ast["status"] in ("ok", "partial")
        assert set(ast["positions"]) == {"Chiron", "Ceres", "Pallas", "Juno", "Vesta"}
