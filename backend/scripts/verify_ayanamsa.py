"""Verify ayanamsa module against Swiss Ephemeris across modes and epochs."""
import swisseph as swe

from src.services.ayanamsa import SUPPORTED, ayanamsa_for, source, _polynomial, _jd_from_datetime
from datetime import datetime, timezone

SWISS_MODE = {
    "lahiri": "SIDM_LAHIRI",
    "raman": "SIDM_RAMAN",
    "fagan_bradley": "SIDM_FAGAN_BRADLEY",
    "krishnamurti": "SIDM_KRISHNAMURTI",
    "deluce": "SIDM_DELUCE",
}

print("source =", source(), "| modes =", SUPPORTED)
print()

EPOCHS = (1900, 1950, 2000, 2026, 2050, 2200)

print(f"{'mode':14s} {'live max|err|':>14s} {'fallback max|err|':>18s}   (arcsec vs Swiss)")
for nm in SUPPORTED:
    swe.set_sid_mode(getattr(swe, SWISS_MODE[nm]), 0.0, 0.0)
    live = []
    fb = []
    for y in EPOCHS:
        dt = datetime(y, 1, 1, tzinfo=timezone.utc)
        jd = swe.julday(y, 1, 1, 0.0, swe.GREG_CAL)
        ref = swe.get_ayanamsa_ut(jd)
        live.append((ayanamsa_for(nm, dt) - ref) * 3600.0)
        fb.append((_polynomial(nm, _jd_from_datetime(dt)) - ref) * 3600.0)
    ml = max(abs(e) for e in live)
    mf = max(abs(e) for e in fb)
    print(
        f"{nm:14s} {ml:14.6f} {mf:18.6f}   "
        + " ".join(f"{y}:{e:+.3f}" for y, e in zip(EPOCHS, fb))
    )

print()
print("--- published anchor check: Lahiri @ J2000 should be 23°51'25\" = 23.857094° ---")
v = ayanamsa_for("lahiri", datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
d = v * 60
print(f"  live   = {v:.6f}° = {int(d)}° {int((d%1)*60)}' {(((d%1)*60)%1)*3600:.1f}\"")
p = _polynomial("lahiri", _jd_from_datetime(datetime(2000, 1, 1, 12, tzinfo=timezone.utc)))
d2 = p * 60
print(f"  poly   = {p:.6f}° = {int(d2)}° {int((d2%1)*60)}' {(((d2%1)*60)%1)*3600:.1f}\"")

print()
print("--- KP = Lahiri - 5'49\" (KP literature) ---")
k = ayanamsa_for("krishnamurti", datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc))
print(f"  Lahiri - KP = {(23.857092347830 - k) * 3600 / 60:.3f} arcmin  (expect ~5.8)")
