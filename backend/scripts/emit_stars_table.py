"""Emit the new STARS table literal from star_catalogue.json.

Prints a Python dict literal with full-precision ICRS J2000 positions and
Hipparcos proper motion, ready to paste into parans_service.py.

Run:  ./.venv/Scripts/python.exe scripts/emit_stars_table.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

HERE = Path(__file__).parent
CATALOGUE = HERE / "star_catalogue.json"

# Visual magnitudes are carried over unchanged from the shipped table; they are
# display/selection data, not astrometry, so the catalogue's Hp does not apply.
MAG = {
    "Aldebaran": 0.87, "Rigel": 0.13, "Betelgeuse": 0.50, "Sirius": -1.46,
    "Castor": 1.58, "Pollux": 1.14, "Procyon": 0.34, "Regulus": 1.35,
    "Alphard": 1.98, "Spica": 0.97, "Arcturus": -0.05, "Antares": 1.06,
    "Vega": 0.03, "Altair": 0.76, "Fomalhaut": 1.16, "Deneb": 1.25,
    "Achernar": 0.46, "Alcyone (Pleiades)": 2.87, "Bellatrix": 1.64,
    "Capella": 0.08, "Aldebaran_N": 0.85, "Canopus": -0.74, "Hamal": 2.00,
    "Polaris": 1.98,
}

# Aldebaran_N is a synthetic traditional point ("Aldebaran's north node
# companion", Lilly/Billy), not a star.  It has no catalogue counterpart, so
# it keeps its legacy position and gets no invented proper motion.
SYNTHETIC = {
    "Aldebaran_N": {"ra": 4.598, "dec": 16.51},
}


def main() -> None:
    doc = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    stars = doc["stars"]

    print("STARS: dict[str, dict] = {")
    for name in MAG:
        if name in SYNTHETIC:
            s = SYNTHETIC[name]
            print(
                f'    "{name}": {{"ra": {s["ra"]}, "dec": {s["dec"]}, '
                f'"mag": {MAG[name]}}},'
            )
            continue
        c = stars[name]
        print(
            f'    "{name}": {{"ra": {c["ra_h"]:.8f}, "dec": {c["dec_deg"]:.8f}, '
            f'"pm_ra": {c["pm_ra_masyr"]:.3f}, "pm_dec": {c["pm_dec_masyr"]:.3f}, '
            f'"mag": {MAG[name]}}},'
        )
    print("}")

    # Sanity: the synthetic point must still sit within rounding of Aldebaran.
    a = stars["Aldebaran"]
    s = SYNTHETIC["Aldebaran_N"]
    d = math.hypot(
        (s["ra"] * 15 - a["ra_h"] * 15) * math.cos(math.radians(a["dec_deg"])),
        s["dec"] - a["dec_deg"],
    ) * 3600
    print(f"\n# Aldebaran_N sits {d:.1f}\" from Aldebaran (legacy point retained)")


if __name__ == "__main__":
    main()
