"""Fetch ICRS star positions + proper motion for the 24 parans stars.

Source: I/311/hip2  (Hipparcos, New Reduction -- van Leeuwen 2007).
Independent of Swiss Ephemeris' sefstars.txt, so the frame test in
tests/test_parans_frames.py stays a genuine cross-implementation check
rather than comparing the engine against its own input.

hip2 positions are ICRS at Ep=1991.25, so they are propagated to J2000 with
their own proper motion.  The Hipparcos original (I/239/hip_main) also
publishes J2000 positions, which gives a free check on that propagation:
agreeing to a few mas means the PM sign, the cos(dec) factor and the
Julian-year convention are all right.

Writes scripts/star_catalogue.json.
"""
from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from pathlib import Path

VIZIER = "https://vizier.cds.unistra.fr/viz-bin/asu-tsv"
HERE = Path(__file__).resolve().parent

# engine key -> SIMBAD-resolvable preferred name
TARGETS = {
    "Aldebaran": "Aldebaran",
    "Rigel": "Rigel",
    "Betelgeuse": "Betelgeuse",
    "Sirius": "Sirius",
    "Castor": "Castor",
    "Pollux": "Pollux",
    "Procyon": "Procyon",
    "Regulus": "Regulus",
    "Alphard": "Alphard",
    "Spica": "Spica",
    "Arcturus": "Arcturus",
    "Antares": "Antares",
    "Vega": "Vega",
    "Altair": "Altair",
    "Fomalhaut": "Fomalhaut",
    "Deneb": "Deneb",
    "Achernar": "Achernar",
    "Alcyone (Pleiades)": "Alcyone",
    "Bellatrix": "Bellatrix",
    "Capella": "Capella",
    "Aldebaran_N": "Aldebaran",   # same sky point, see note in _ALDEB_N_NOTE
    "Canopus": "Canopus",
    "Hamal": "Hamal",
    "Polaris": "Polaris",
}

# Aldebaran_N is not a separate star.  In Brady's scheme it is a point offset
# from Aldebaran; the shipped table already put it at the same RA/Dec to
# within the 0.001h/0.001deg rounding, i.e. the same direction on the sky.
# It therefore inherits Aldebaran's motion, and that is recorded explicitly
# rather than left to look like an independent measurement.
_ALDEB_N_NOTE = (
    "Not an independent star: same sky direction as Aldebaran within the "
    "old table's rounding, so it inherits Aldebaran's proper motion."
)

J2000_JD = 2451545.0
HIP2_EPOCH_JD = 2448349.0625  # 1991.25 (NOT 2458349 -- that would be 2091)


def _tsv(url: str) -> str:
    with urllib.request.urlopen(url, timeout=90) as fh:
        return fh.read().decode("utf-8", "replace")


def _rows(text: str) -> list[dict[str, str]]:
    """Parse a VizieR TSV body into dicts, skipping the '#' comment block.

    A column-units row and a dashed separator row sit between the header and
    the data; both are discarded by _by_hip's integer check, so they are kept
    here and filtered downstream.
    """
    header: list[str] | None = None
    out = []
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        if not line.strip():
            continue
        if header is None:
            header = line.split("\t")
            continue
        cells = line.split("\t")
        cells += [""] * (len(header) - len(cells))
        out.append(dict(zip(header, cells)))
    return out


def _query(source: str, out: str, extra: str = "") -> list[dict[str, str]]:
    """Run one VizieR TSV query.

    VizieR refuses to stream more than a few thousand rows per request, so
    callers must restrict the query (by HIP list) rather than pulling a whole
    catalogue. Overflow and separator rows come back as dashes, so only rows
    whose key column parses as an integer are kept.
    """
    q = urllib.parse.urlencode(
        {"-source": source, "-out": out, "-out.max": "5000", "-sort": "HIP"}
    ) + extra
    return _rows(_tsv(f"{VIZIER}?{q}"))


def _by_hip(rows: list[dict[str, str]]) -> dict[int, dict[str, str]]:
    out: dict[int, dict[str, str]] = {}
    for r in rows:
        try:
            out[int(r["HIP"])] = r
        except (KeyError, TypeError, ValueError):
            continue  # header/separator/overflow row
    return out


def propagate(ra_deg, dec_deg, pmra_mas, pmde_mas, years: float) -> tuple[float, float]:
    """J2000 position -> position `years` later by tangential space motion.

    pmra_mas is mu_alpha*cos(dec) in mas/yr, so the RA increment in seconds
    of time is pmra/1000/cos(dec)/15 per year.  Second-order terms (great-
    circle curvature, radial-velocity perspective acceleration) are below a
    mas over the 8.75 yr this is used for.
    """
    d_arcsec = pmde_mas / 1000.0 * years
    d_ra_sec_time = (pmra_mas / 1000.0) / math.cos(math.radians(dec_deg)) / 15.0 * years
    d_ra_deg = d_ra_sec_time * 15.0 / 3600.0
    dec2 = dec_deg + d_arcsec / 3600.0
    ra2 = ra_deg + d_ra_deg
    return ra2 % 360.0, dec2


def main() -> None:
    stars: dict[str, dict] = {}
    problems: list[str] = []

    # --- 3. Resolve each engine key to a HIP number via SIMBAD ------------
    import astroquery.simbad as simbad_mod

    simbad = simbad_mod.Simbad()
    simbad.add_votable_fields("ids")

    key_to_hip: dict[str, int] = {}
    for key, name in TARGETS.items():
        res = simbad.query_object(name)
        if len(res) == 0:
            problems.append(f"{key}: SIMBAD found nothing for {name!r}")
            continue
        hip = None
        # `ids` comes back as one pipe-joined string, e.g. "...|HIP 69673|HD ...|"
        for ident in str(res[0]["ids"]).split("|"):
            if ident.strip().upper().startswith("HIP "):
                hip = int(ident.split()[1])
                break
        if hip is None:
            problems.append(f"{key}: SIMBAD gave no HIP id for {name!r}")
            continue
        key_to_hip[key] = hip

    # --- 4. Pull catalogue rows for exactly those HIPs --------------------
    by2: dict[int, dict[str, str]] = {}
    by1: dict[int, dict[str, str]] = {}
    hips = sorted(set(key_to_hip.values()))
    for chunk in (hips[i : i + 60] for i in range(0, len(hips), 60)):
        hip_list = ",".join(str(h) for h in chunk)
        by2.update(
            _by_hip(_query("I/311/hip2", "HIP,RArad,DErad,Plx,pmRA,pmDE,Hpmag",
                           f"&HIP={hip_list}"))
        )
        by1.update(
            # I/239/hip_main exposes RAICRS/DEICRS (ICRS degrees). There is no
            # RAJ2000/DEJ2000 column and VizieR drops unknown names silently.
            _by_hip(_query("I/239/hip_main", "HIP,RAICRS,DEICRS,pmRA,pmDE",
                           f"&HIP={hip_list}"))
        )

    for key, name in TARGETS.items():
        hip = key_to_hip.get(key)
        if hip is None or hip not in by2:
            problems.append(f"{key}: no catalogue row in hip2 ({name!r})")
            continue

        r2, r1 = by2[hip], by1.get(hip)
        ra91 = float(r2["RArad"])
        dec91 = float(r2["DErad"])
        pmra = float(r2["pmRA"]) if r2["pmRA"].strip() else 0.0
        pmde = float(r2["pmDE"]) if r2["pmDE"].strip() else 0.0
        plx = float(r2["Plx"]) if r2["Plx"].strip() else None
        vmag = float(r2["Hpmag"]) if r2["Hpmag"].strip() else None

        # I/311/hip2 is referenced to Ep=1991.25; propagate forward to J2000.
        # (J2000 - 1991.25) in Julian years, positive.
        years_to_j2000 = (J2000_JD - HIP2_EPOCH_JD) / 365.25
        ra00, dec00 = propagate(ra91, dec91, pmra, pmde, years_to_j2000)

        entry = {
            "hip": hip,
            "source": "I/311/hip2 (van Leeuwen 2007, ICRS Ep=1991.25) propagated to J2000",
            "ra_h": ra00 / 15.0,
            "dec_deg": dec00,
            # mas/yr; pm_ra is mu_alpha*cos(dec)
            "pm_ra_masyr": pmra,
            "pm_dec_masyr": pmde,
            "pm_ra_arcsec_cy": pmra / 1000.0 * 100.0,
            "pm_dec_arcsec_cy": pmde / 1000.0 * 100.0,
            "parallax_mas": plx,
            "vmag": vmag,
        }
        if r1 is not None and r1.get("RAICRS", "").strip():
            d_ra = ((ra00 - float(r1["RAICRS"]) + 540) % 360 - 180) * 3600.0
            d_ra *= math.cos(math.radians(dec00))
            d_dec = (dec00 - float(r1["DEICRS"])) * 3600.0
            entry["hip1_minus_vue2_arcsec"] = round(math.hypot(d_ra, d_dec), 3)
        if key == "Aldebaran_N":
            entry["note"] = _ALDEB_N_NOTE

        stars[key] = entry

    payload = {
        "generated_by": "scripts/fetch_star_catalogue.py",
        "epoch": "J2000.0 ICRS",
        "pm_units": "mas/yr; pm_ra is mu_alpha*cos(dec)",
        "frame_note": (
            "hip2 is ICRS. The original hip_main J2000 columns are FK5 and are "
            "used only as an independent check on the 1991.25->2000 propagation."
        ),
        "stars": stars,
        "problems": problems,
    }
    out_path = HERE / "star_catalogue.json"
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"resolved {len(stars)}/{len(TARGETS)} stars -> {out_path.name}")
    for p in problems:
        print("  PROBLEM:", p)
    print(f"\n{'star':<20} {'HIP':>7} {'RA(h)':>11} {'Dec(deg)':>10} "
          f"{'pmRA/cy':>9} {'pmDE/cy':>9} {'|pm|':>7} {'vs hip1':>8}")
    for k, v in stars.items():
        pm = math.hypot(v["pm_ra_arcsec_cy"], v["pm_dec_arcsec_cy"])
        print(f"{k:<20} {v['hip']:>7} {v['ra_h']:>11.7f} "
              f"{v['dec_deg']:>10.6f} {v['pm_ra_arcsec_cy']:>9.2f} "
              f"{v['pm_dec_arcsec_cy']:>9.2f} {pm:>7.2f} "
              f"{v.get('hip1_minus_vue2_arcsec', float('nan')):>8.3f}")


if __name__ == "__main__":
    main()
