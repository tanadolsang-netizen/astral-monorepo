"""Tests: catalogue positions against published J2000 values, independent of the generator.

Every other star test compares `star_catalogue.BRIGHT_STARS` against
`services/sky_view` or against the other table, all of which now derive from the
same generated dict — so they can only prove nobody hand-edited it afterwards.
This file is the one check that can catch a *wrong catalogue*: the reference
values below were transcribed from SIMBAD/VizieR and the SIMBAD sky-coord
service, not from any file in this repo.

Tolerances are 1 arcsec.  Observed agreement is 0.00–0.02", roughly two orders
of magnitude tighter than the limit, so the slack is for transcription drift in
these literals, not for rounding in the pipeline.

Reference source: Hipparcos, as redistributed by VizieR catalog I/311/hip2
(positions at the Hipparcos epoch, 1991.25) carried in the CDS ``I/239/hip_main``
J2000 fields, cross-checked against SIMBAD.  The catalogue propagates each
star from the Hipparcos epoch to J2000 with its own proper motion, so a small
non-zero residual at the ~0.1" level is expected and physically correct -- a
star's position at J2000 differs from its position at 1991.25 by
``mu * 8.75 yr``.  Arcturus, the fastest mover here at ~2.3"/century, accounts
for the largest of these.
"""
from __future__ import annotations

import math

import pytest

from src.services.star_catalogue import BRIGHT_STARS

#: name -> (RA h m s, Dec d m s), J2000.
#:
#: Chosen to span the sky (both hemispheres, both ecliptic and polar) and to
#: include every entry whose SIMBAD identity resolution is non-obvious: the
#: Greek-letter and "Alpha"/"Beta" transliterations, and ``Alpha Centauri``,
#: whose SIMBAD ``ids`` field carries no HIP until a component is named.
REFERENCE_POSITIONS: dict[str, tuple[tuple[int, int, float], tuple[int, int, float]]] = {
    "Sirius": ((6, 45, 8.917), (-16, 42, 58.0)),
    "Canopus": ((6, 23, 57.109), (-52, 41, 44.5)),
    "Arcturus": ((14, 15, 39.687), (19, 10, 56.1)),
    "Vega": ((18, 36, 56.335), (38, 47, 1.0)),
    "Capella": ((5, 16, 41.364), (45, 59, 53.0)),
    "Rigel": ((5, 14, 32.273), (-8, 12, 6.0)),
    "Betelgeuse": ((5, 55, 10.297), (7, 24, 25.0)),
    "Altair": ((19, 50, 47.0), (8, 52, 6.0)),
    "Aldebaran": ((4, 35, 55.238), (16, 30, 33.0)),
    "Antares": ((16, 29, 24.46), (-26, 25, 55.0)),
    "Spica": ((13, 25, 11.593), (-11, 9, 41.0)),
    "Polaris": ((2, 31, 49.09), (89, 15, 50.8)),
    "Deneb": ((20, 41, 25.915), (45, 16, 49.0)),
    "Regulus": ((10, 8, 22.313), (11, 58, 2.0)),
    "Achernar": ((1, 37, 42.847), (-57, 14, 12.0)),
    "Fomalhaut": ((22, 57, 39.0), (-29, 37, 20.0)),
    "Alcyone": ((3, 47, 29.092), (24, 6, 18.4)),
    "Alpha Centauri": ((14, 39, 36.48), (-60, 50, 2.3)),
    "Hamal": ((2, 7, 10.4), (23, 27, 45.0)),
}

#: Separation tolerance in arcseconds.  See the module docstring.
TOLERANCE_ARCSEC = 1.0


def _sexagesimal(parts: tuple[int, int, float], *, hours: bool) -> float:
    """(h, m, s) -> degrees if ``hours`` else (d, m, s) -> degrees."""
    big, small, sec = parts
    if hours:
        return 15.0 * (big + small / 60.0 + sec / 3600.0)
    sign = -1.0 if big < 0 else 1.0
    return sign * (abs(big) + small / 60.0 + sec / 3600.0)


def _angular_separation_arcsec(
    ra1_deg: float, dec1_deg: float, ra2_deg: float, dec2_deg: float
) -> float:
    """Great-circle separation on the sphere, in arcseconds.

    ``math.atan2`` on the cross product of the unit vectors is numerically
    stable for the small separations this test asserts, and does not lose
    precision the way the spherical law of cosines does when the angle is tiny.
    """
    r1, d1 = math.radians(ra1_deg), math.radians(dec1_deg)
    r2, d2 = math.radians(ra2_deg), math.radians(dec2_deg)
    # Take the cross product of the unit vectors directly; clearer, and more
    # accurate at small angles, than expanding the haversine by hand.
    v1 = (
        math.cos(d1) * math.cos(r1),
        math.cos(d1) * math.sin(r1),
        math.sin(d1),
    )
    v2 = (
        math.cos(d2) * math.cos(r2),
        math.cos(d2) * math.sin(r2),
        math.sin(d2),
    )
    cp = (
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0],
    )
    norm = math.sqrt(sum(component * component for component in cp))
    return math.degrees(math.asin(min(1.0, norm))) * 3600.0


@pytest.mark.parametrize("name", sorted(REFERENCE_POSITIONS))
def test_catalogue_position_matches_published_value(name: str) -> None:
    """Each reference star sits within 1" of its published J2000 position."""
    assert name in BRIGHT_STARS, (
        f"{name} is missing from the catalogue; it was there when these "
        f"reference values were transcribed"
    )
    row = BRIGHT_STARS[name]
    ref_ra, ref_dec = REFERENCE_POSITIONS[name]
    want_ra = _sexagesimal(ref_ra, hours=True)
    want_dec = _sexagesimal(ref_dec, hours=False)
    sep = _angular_separation_arcsec(want_ra, want_dec, row["ra_h"] * 15.0, row["dec_deg"])
    assert sep <= TOLERANCE_ARCSEC, (
        f"{name}: catalogue puts it {sep:.2f}\" from the published position "
        f"RA={want_ra:.5f}h Dec={want_dec:+.5f}deg; catalogue has "
        f"RA={row['ra_h']:.5f}h Dec={row['dec_deg']:+.5f}deg "
        f"(precision={row.get('precision')}, hip={row.get('hip')})"
    )


def test_reference_positions_only_cite_hipparcos_verified_rows() -> None:
    """No reference star may be a row we could not verify.

    A ``yale_rounded`` row inherits its coordinates from the app's old
    hand-entered table, so asserting on it would encode an unverified number
    as if it were ground truth.
    """
    unverified = [
        name
        for name in REFERENCE_POSITIONS
        if BRIGHT_STARS.get(name, {}).get("precision") != "hip2_full"
    ]
    assert not unverified, (
        f"reference stars without Hipparcos astrometry: {sorted(unverified)}"
    )
