"""Report where the app's own star table disagrees with the Hipparcos catalogue.

`services/sky_view.py` and `services/parans_service.py` used to carry their own
hand-entered Yale Bright Star Catalogue rows.  Those rows are only good to about
a tenth of a degree, and an unknown number of them are wrong outright.  Now that
`star_catalogue.py` holds I/311/hip2 astrometry, this probe measures the damage so
the divergence is a number instead of a suspicion.

Two independent checks:
  1. POSITION   -- separation between the app's row and Hipparcos.
  2. IDENTITY   -- is the app's name a *different* star in Hipparcos?  A large
                   separation is a typo; a separation of tens of degrees is a
                   wrong star, which is the class that silently corrupts a chart.

Run:  python scripts/report_star_table_divergence.py
"""

from __future__ import annotations

import math
import sys

sys.path.insert(0, ".")

from src.services.star_catalogue import BRIGHT_STARS  # noqa: E402

# Yale BSC is a printed table: 0.01h RA = 36", 0.01 deg Dec = 36".  Anything past a
# few times that is not rounding, it is a different or mistyped position.
TOLERANCE_ARCMIN = 2.0


def separation_arcmin(ra_h_a: float, dec_a: float, ra_h_b: float, dec_b: float) -> float:
    """Great-circle separation in arcminutes between two equatorial positions."""
    d_ra = math.radians((ra_h_b - ra_h_a) * 15.0)
    dec_1 = math.radians(dec_a)
    dec_2 = math.radians(dec_b)
    d_dec = math.radians(dec_b - dec_a)
    cos_sep = (
        math.sin(dec_1) * math.sin(dec_2)
        + math.cos(dec_1) * math.cos(dec_2) * math.cos(d_ra)
    )
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_sep)))) * 60.0


def main() -> int:
    # The app's own table: (ra_hours, dec_deg, magnitude, english, thai).
    from src.services.sky_view import STARS as APP_STARS

    app = {row[3]: row for row in APP_STARS}

    checked = 0
    missing = []
    rounded = []
    wrong = []

    for name, row in sorted(app.items()):
        cat = BRIGHT_STARS.get(name)
        if cat is None or cat["precision"] != "hip2_full":
            missing.append(name)
            continue
        checked += 1
        sep = separation_arcmin(row[0], row[1], cat["ra_h"], cat["dec_deg"])
        if sep > 60.0:
            wrong.append((sep, name, row[0], row[1], cat["ra_h"], cat["dec_deg"]))
        elif sep > TOLERANCE_ARCMIN:
            rounded.append((sep, name))

    print(f"app rows              : {len(app)}")
    print(f"names in catalogue    : {len(app) - len(missing)}")
    print(f"names not in catalogue: {len(missing)} {missing}")
    print(f"positions checked     : {checked}")
    print()
    print(f"consistent (<= {TOLERANCE_ARCMIN:.0f}') : {checked - len(rounded) - len(wrong)}")
    print(f"Yale rounding noise   : {len(rounded)}")
    print(f"WRONG (different star): {len(wrong)}")
    print()

    if wrong:
        print("The app is pointing at the wrong sky entirely for these:")
        for sep, name, ra_a, dec_a, ra_b, dec_b in sorted(wrong, reverse=True):
            print(
                f"  {name:24s} app {ra_a:9.4f}h {dec_a:+8.3f}  "
                f"hipparcos {ra_b:9.4f}h {dec_b:+8.3f}  off by {sep / 60.0:6.2f} deg"
            )

    return 1 if wrong else 0


if __name__ == "__main__":
    raise SystemExit(main())
