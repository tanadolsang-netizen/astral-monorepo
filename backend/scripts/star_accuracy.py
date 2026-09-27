"""Star ecliptic-longitude accuracy: project vs Skyfield IAU 2006 precession.

Skyfield's `build_ecliptic_matrix` is the reference. Before the fix the project
used a constant obliquity plus a linear 50.29"/yr shift, which drifted up to
2.8 deg for birth epochs ~100 yr from J2000.
"""
import math
from datetime import datetime, timezone

from skyfield.api import load
from skyfield.framelib import build_ecliptic_matrix

from src.services.parans_service import STARS, _jd_ut, star_positions

ts = load.timescale()

EPOCHS = [(1900, 1, 1, 0), (1950, 6, 15, 12), (1997, 5, 18, 22),
          (2016, 1, 1, 0), (2100, 1, 1, 0)]
SHOW = (1900, 1997, 2100)
SHOW_STARS = ("Sirius", "Vega", "Arcturus", "Antares")

# The pre-fix constant, reproduced exactly so the old number is not folklore.
OLD_OBLIQUITY = math.radians(23.4367)


def reference(ra_h, dec_d, y, mo, d, h):
    m = build_ecliptic_matrix(ts.utc(y, mo, d, h))
    ra = math.radians(ra_h * 15.0)
    dec = math.radians(dec_d)
    v = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
    o = [sum(m[i][j] * v[j] for j in range(3)) for i in range(3)]
    return math.degrees(math.atan2(o[1], o[0])) % 360


def old_formula(ra_h, dec_d, y):
    """Constant obliquity + linear precession SUBTRACTED: the original bug."""
    ra = math.radians(ra_h * 15.0)
    dec = math.radians(dec_d)
    x = math.cos(dec) * math.cos(ra)
    y_ = math.cos(dec) * math.sin(ra)
    z = math.sin(dec)
    ye = y_ * math.cos(OLD_OBLIQUITY) + z * math.sin(OLD_OBLIQUITY)
    lon = math.degrees(math.atan2(ye, x)) % 360.0
    return (lon - (y - 2000) * 50.29 / 3600.0) % 360.0


def main():
    print("star       epoch              project  skyfield    diff\"    old diff\"")
    worst_new = worst_old = 0.0
    at_new = at_old = ("-", 0)
    for y, mo, d, h in EPOCHS:
        jd = _jd_ut(datetime(y, mo, d, h, tzinfo=timezone.utc))
        sp = star_positions(jd)
        for nm, s in STARS.items():
            r = reference(s["ra"], s["dec"], y, mo, d, h)
            diff = (sp[nm] - r) * 3600.0
            old = (old_formula(s["ra"], s["dec"], y) - r) * 3600.0
            if abs(diff) > worst_new:
                worst_new, at_new = abs(diff), (nm, y)
            if abs(old) > worst_old:
                worst_old, at_old = abs(old), (nm, y)
            if y in SHOW and nm in SHOW_STARS:
                print("%-10s %-16s %9.4f %9.4f %8.3f %11.1f"
                      % (nm, "%d-%02d-%02dT%02d" % (y, mo, d, h),
                         sp[nm], r, diff, old))
    print()
    print("stars checked   : %d x %d epochs = %d"
          % (len(STARS), len(EPOCHS), len(STARS) * len(EPOCHS)))
    print("worst now       : %.6f arcsec  (%s %d)"
          % (worst_new, at_new[0], at_new[1]))
    print("worst before fix: %.1f arcsec  (%s %d)  = %.4f deg"
          % (worst_old, at_old[0], at_old[1], worst_old / 3600.0))
    if worst_new > 0:
        print("improvement     : %.0fx" % (worst_old / worst_new))
    else:
        print("improvement     : exact at double precision")


if __name__ == "__main__":
    main()
