"""Build ONE authoritative star catalogue for the whole app.

There are two rival star tables today:
  * src/services/parans_service.py -- 24 stars, I/311/hip2 full precision,
    with proper motion.  Used for parans.
  * src/services/sky_view.py      -- ~92 stars, Yale BSC rounded to 3
    decimals, no proper motion.  Used for the planetarium canvas.

They overlap by roughly 20 stars, and they DISAGREE: sky_view's Aldebaran is
4.359h/-16.51... no, 4.359h/+16.51, parans' is full precision.  Rendering the
sky from a table that disagrees with the table the chart was computed from is
exactly the kind of drift an app must not have.

So: resolve the union of both lists against Hipparcos, emit a single module
src/services/star_catalogue.py, and let both consumers import it.

  I/311/hip2  = Hipparcos New Reduction (van Leeuwen 2007), ICRS, Ep=1991.25
  propagated to J2000 with the star's own proper motion.
  I/239/hip_main is pulled as an independent cross-check on that propagation.

A star that SIMBAD cannot resolve (Yale-only designations like "Scorpius G")
keeps its Yale position and is tagged precision="yale_rounded" with no PM --
never silently given a fabricated PM.
"""
from __future__ import annotations

import json
import math
import re
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
BACKEND = HERE.parent
sys.path.insert(0, str(BACKEND))

J2000_JD = 2451545.0
HIP2_EPOCH_JD = 2448349.0625  # 1991.25 (NOT 2458349 -- that is 2091)

GREEK = {
    "α": "Alfa", "β": "Beta", "γ": "Gamma", "δ": "Delta", "ε": "Epsilon",
    "ζ": "Zeta", "η": "Eta", "θ": "Theta", "ι": "Iota", "κ": "Kappa",
    "λ": "Lambda", "μ": "Mu", "ν": "Nu", "ξ": "Xi", "ο": "Omicron",
    "π": "Pi", "ρ": "Rho", "σ": "Sigma", "τ": "Tau", "υ": "Upsilon",
    "φ": "Phi", "χ": "Chi", "ψ": "Psi", "ω": "Omega",
}
# Bayer constellation abbreviation -> SIMBAD/VizieR "Genitive" form.
CONSTEL = {
    "Ursa Major": "UMa", "Ursa Minor": "UMi", "Centaurus": "Cen",
    "Cassiopeia": "Cas", "Carina": "Car", "Bootes": "Boo", "Bootes": "Boo",
    "Hydra": "Hya", "Leo": "Leo", "Pegasus": "Peg", "Perseus": "Per",
    "Orion": "Ori", "Sagittarius": "Sgr", "Scorpius": "Sco", "Draco": "Dra",
    "Triangulum Australe": "TrA", "Pictor": "Pic", "Eridanus": "Eri",
    "Fornax": "For", "Caelum": "Cae", "Lepus": "Lep", "Monoceros": "Mon",
    "Aries": "Ari", "Auriga": "Aur", "Gemini": "Gem", "Cancer": "Cnc",
    "Virgo": "Vir", "Libra": "Lib", "Scutum": "Sct", "Serpens": "Ser",
    "Capricornus": "Cap", "Aquarius": "Aqr", "Pisces": "Psc", "Aries": "Ari",
    "Cetus": "Cet", "Grus": "Gru", "Phoenix": "Phe", "Tucana": "Tuc",
    "Northern Crown": "CrB",
    "Lupus": "Lup", "Circinus": "Cir", "Norma": "Nor", "Ara": "Ara",
    "Pavo": "Pav", "Indus": "Ind", "Octantis": "Oct", "Volans": "Vol",
    "Dorado": "Dor", "Reticulum": "Ret", "Horologium": "Hor",
    "Antlia": "Ant", "Pyxis": "Pyx", "Vela": "Vel", "Columba": "Col",
    "Canis Major": "CMa", "Canis Minor": "CMi", "Monoceros": "Mon",
    "Triangulum": "Tri", "Ophiuchus": "Oph", "Corona Borealis": "CrB",
    "Boötes": "Boo", "Bootes": "Boo", "Cor Caroli": "CVn",
    "Canes Venatici": "CVn", "Musca": "Mus", "Camelopardalis": "Cam",
    "Cassiopeia": "Cas", "Andromeda": "And", "Pegasus": "Peg",
}


def simbad_name(en: str) -> list[str]:
    """Candidate SIMBAD identifiers for one catalogue entry, best first."""
    base = en.strip()
    cands = [base]

    # "Corona Borealis α" / "Bootes γ" -> "CrB alpha" (Yale carries no diaeresis)
    # The catalogue stores GREEK letters, so match on the GREEK key and emit
    # the Latin value.  Matching on GREEK.values() here never fires, because
    # "Ursa Major ε".endswith("Epsilon") is False.
    for greek, greek_latin in GREEK.items():
        if base.endswith(greek):
            genitive = base[: -len(greek)].strip()
            for full, abbr in CONSTEL.items():
                if genitive.replace("ö", "o") == full.replace("ö", "o"):
                    # SIMBAD puts the Greek letter FIRST: "Epsilon UMa".
                    # "UMa Epsilon" is a different (absent) object and the
                    # lookup silently returns nothing.
                    cands.append(f"{greek_latin} {abbr}")
                    break
            # SIMBAD also accepts the spelled-out constellation name.
            cands.append(f"{greek_latin} {genitive}")
            break

    # nebulae the Yale list carries under a Bayer slot
    for neb, ident in (("Sagittarius N", "M 8"), ("Sagittarius S", "M 20"),
                       ("Cassiopeia A", "NGC 663")):
        if base == neb:
            cands.append(ident)

    # "<constellation> <greek> B"  (Yale companion markers)
    m = re.match(r"(.+?)\s+([A-Za-z]+)\s+B$", base)
    if m:
        cands.append(f"{m.group(1)} {m.group(2)} B")

    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _build_bright_index(max_mag: float = 7.5) -> list[tuple[float, float, int, float]]:
    """Every hip2 entry brighter than max_mag, as (ra_deg, dec_deg, hip, vmag).

    VizieR's asu-tsv silently drops -c.eq/-c.r, so a server-side cone search
    returns the first N rows of the table instead. Download the bright slice
    once (paged by HIP number to stay under the 5000-row cap) and do the
    cone search locally.
    """
    from fetch_star_catalogue import _rows, _tsv, VIZIER

    idx: list[tuple[float, float, int, float]] = []
    for lo in range(1, 120001, 20000):
        q = urllib.parse.urlencode({
            "-source": "I/311/hip2",
            "-out": "HIP,RArad,DErad,Hpmag",
            "-out.max": "5000",
            "HIP": f"{lo}..{lo + 19999}",
            "Hpmag": f"<{max_mag}",
        })
        try:
            rows = _rows(_tsv(f"{VIZIER}?{q}"))
        except Exception as exc:            # noqa: BLE001 - VizieR 500s are routine
            print(f"  bright index {lo} failed: {exc}", flush=True)
            continue
        for r in rows:
            try:
                # RArad is in RADIANS, not hours -- the emitter propagates it
                # as radians for the same reason.
                idx.append((math.degrees(float(r["RArad"])), float(r["DErad"]),
                            int(r["HIP"]), float(r["Hpmag"])))
            except (KeyError, TypeError, ValueError):
                continue
    return idx


def _sep_deg(ra1: float, dec1: float, ra2: float, dec2: float) -> float:
    """Great-circle separation in degrees."""
    a1, d1, a2, d2 = map(math.radians, (ra1, dec1, ra2, dec2))
    c = math.sin(d1) * math.sin(d2) + math.cos(d1) * math.cos(d2) * math.cos(a1 - a2)
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def _nearest(idx, ra_h: float, dec_deg: float, max_sep_arcmin: float = 30.0):
    """Brightest star within max_sep_arcmin of the given position, or None.

    Yale BSC positions are rounded to ~100", so a 30' ceiling is generous
    while still far too tight to accept a wrong constellation.
    """
    ra_deg = ra_h * 15.0
    best = None
    for s_ra, s_dec, hip, vmag in idx:
        if _sep_deg(ra_deg, dec_deg, s_ra, s_dec) * 60.0 > max_sep_arcmin:
            continue
        if best is None or vmag < best[0]:
            best = (vmag, hip, _sep_deg(ra_deg, dec_deg, s_ra, s_dec))
    return best


def propagate(ra_deg, dec_deg, pmra_mas, pmde_mas, years):
    """Hipparcos Ep=1991.25 -> J2000 by tangential space motion.

    pmra_mas is mu_alpha*cos(dec) in mas/yr, so the RA increment in seconds
    of time is pmra/1000/cos(dec)/15 per year.
    """
    d_arcsec = pmde_mas / 1000.0 * years
    d_ra_sec_time = (pmra_mas / 1000.0) / math.cos(math.radians(dec_deg)) / 15.0 * years
    return (ra_deg + d_ra_sec_time * 15.0 / 3600.0) % 360.0, dec_deg + d_arcsec / 3600.0


# Stars the app listed under their English name. The Thai is the form Thai
# astrology actually uses, not a bare transliteration.
THAI_OVERRIDES = {
    "Capella": "ดาวแคปเลลลา",
    "Alphard": "ดาวตาคู่",
}


def _hip_from_simbad(simbad, cand: str) -> int | None:
    """Resolve one candidate name to a HIP number via SIMBAD, or None.

    Retries on rate limits, since a transient failure and a genuine
    non-resolution look identical otherwise -- and the old code answered the
    latter with a fabricated HIP.

    Close multiples have no HIP on the system's own row, so when the ids
    carry none, retry the primary component: SIMBAD answers 'Alpha Centauri'
    as the unresolved system '* alf Cen', but 'alf Cen A' with HIP 71683.
    Without this the brightest southern star silently kept a bad fallback
    position instead.
    """
    attempts = (cand, f"{cand} A") if " " in cand else (cand,)
    for attempt_name in attempts:
        res = None
        for attempt in range(3):
            try:
                res = simbad.query_object(attempt_name)
                break
            except Exception as exc:  # rate limit / transient network
                print(f"  ! {attempt_name} try {attempt + 1}: "
                      f"{type(exc).__name__}: {exc}", flush=True)
                time.sleep(2.0 * (attempt + 1))
        if res is None or len(res) == 0:
            continue
        ids = str(res[0]["ids"]).replace("\n", "|").split("|")
        for ident in ids:
            if ident.strip().upper().startswith("HIP "):
                return int(ident.split()[1])
        time.sleep(0.3)
    return None


def collect_base_rows() -> list[tuple[str, str, float, float, float]]:
    """(en, th, ra_h, dec_deg, mag) for every star currently in the app."""
    from src.services.sky_view import STARS as SKY_STARS
    from src.services.parans_service import STARS as PARANS_STARS, STAR_TH

    rows: dict[str, tuple[str, str, float, float, float]] = {}
    for ra_h, dec, mag, en, th in SKY_STARS:
        th = THAI_OVERRIDES.get(en, th)
        if th == en:                      # sky_view carried no Thai for a few
            th = STAR_TH.get(en, (en, None))[0]
        rows[en] = (en, th, float(ra_h), float(dec), float(mag))

    for name, rec in PARANS_STARS.items():
        en = name.split("_")[0] if "_" in name else name
        en = en.replace("(Pleiades)", "").strip()
        if en in rows:
            continue
        th = THAI_OVERRIDES.get(en) or STAR_TH.get(name, en)
        if isinstance(th, tuple):   # a few entries carry (th, alias)
            th = th[0]
        # parans STARS stores RA in HOURS, under 'ra'
        rows[en] = (en, th, float(rec["ra"]), float(rec["dec"]),
                    float(rec.get("mag", 2.5)))

    return list(rows.values())


def main() -> None:
    from astroquery.simbad import Simbad

    # Reuse the proven raw-VizieR helpers rather than astroquery's Vizier
    # class: the catalogue is fetched by explicit HIP list, and VizieR
    # silently drops column names it does not know.
    from fetch_star_catalogue import _by_hip, _query

    base = collect_base_rows()
    print(f"union of both tables: {len(base)} stars", flush=True)

    simbad = Simbad()
    simbad.add_votable_fields("ids")

    hip_by_star: dict[str, int] = {}
    unresolved: list[str] = []
    # VizieR rate-limits, and a rebuild only changes the Thai labels, not the
    # astrometry. Cache the network lookups so regeneration is offline.
    cache_p = HERE / "bright_star_cache.json"
    cache = json.loads(cache_p.read_text(encoding="utf-8")) if cache_p.exists() else {}
    if cache.get("schema") != 3:
        # Schema 1 was written by a cone fallback that VizieR silently ignored,
        # stamping one arbitrary HIP onto every unresolved star.  Schema 2 was
        # meant to cover that, but the bump was applied by hand while `names`
        # still held schema 1's fabricated mappings, so the guard never fired
        # again and Altair/Capella/Alcyone/alpha Cen kept wrong HIPs (83675 /
        # 116228 / 88528 / 48310). Bump to 3 to force one clean rebuild under
        # the current SIMBAD-only resolver, which returns the correct numbers.
        cache.pop("names", None)
    cache["schema"] = 3
    names = cache.setdefault("names", {})
    rows_cache = cache.setdefault("rows", {})
    dirty = False
    for i, (en, th, ra_h, dec, mag) in enumerate(base, 1):
        if en in names:
            if names[en]:
                hip_by_star[en] = names[en]
            else:
                unresolved.append(en)
            continue
        hip = None
        for cand in simbad_name(en):
            hip = _hip_from_simbad(simbad, cand)
            if hip is not None:
                break
        names[en] = hip
        dirty = True
        if hip is None:
            unresolved.append(en)
        else:
            hip_by_star[en] = hip
        if i % 15 == 0:
            print(f"  SIMBAD {i}/{len(base)}", flush=True)

    rows2: dict[int, dict] = {}
    rows1: dict[int, dict] = {}
    def fetch_rows(hips: list[int]) -> None:
        """Fill rows2/rows1 from cache or VizieR, in 60-HIP chunks."""
        for chunk in (hips[i:i + 60] for i in range(0, len(hips), 60)):
            if not chunk:
                continue
            miss = [h for h in chunk if str(h) not in rows_cache]
            if not miss:
                rows2.update({h: rows_cache[str(h)] for h in chunk if "RArad" in rows_cache[str(h)]})
                rows1.update({h: rows_cache[str(h)] for h in chunk if "RAICRS" in rows_cache[str(h)]})
                continue
            hip_list = ",".join(str(h) for h in miss)
            got2 = _by_hip(_query(
                "I/311/hip2", "HIP,RArad,DErad,Plx,pmRA,pmDE,Hpmag",
                f"&HIP={hip_list}"))
            # I/239/hip_main exposes RAICRS/DEICRS; there is no RAJ2000/DEJ2000.
            got1 = _by_hip(_query(
                "I/239/hip_main", "HIP,RAICRS,DEICRS,pmRA,pmDE",
                f"&HIP={hip_list}"))
            rows2.update(got2)
            rows1.update(got1)
            for h in miss:
                rows_cache.setdefault(str(h), {}).update(got2.get(h) or got1.get(h) or {})
            dirty = True
            print(f"  VizieR chunk: hip2 {len(got2)} / hip_main {len(got1)}", flush=True)

    fetch_rows(sorted(set(hip_by_star.values())))

    # SIMBAD resolves Bayer names by identifier, independent of coordinates.
    # A SIMBAD name hit is position-independent and therefore authoritative:
    # never throw it away.  The Yale position is cross-checked, NOT trusted --
    # sky_view's hand-entered table is wrong for ~1 row in 5 (Sirius RA is
    # 18 min out), so a large disagreement is a bug in sky_view, not here.
    #
    # There is deliberately NO position-based fallback.  A match would be made
    # against a table that is wrong one row in five, and a silent mis-assignment
    # would write one star's proper motion under another star's name.  A star
    # that SIMBAD cannot name stays out of the catalogue and gets reported.
    base_by_en = {en: (th, ra_h, dec, mag) for en, th, ra_h, dec, mag in base}
    yale_wrong: list[str] = []
    for en, (th, ra_h, dec, mag) in base_by_en.items():
        hip = hip_by_star.get(en)
        if hip is not None and hip in rows2:
            got = _sep_deg(ra_h * 15.0, dec,
                           math.degrees(float(rows2[hip]["RArad"])),
                           float(rows2[hip]["DErad"])) * 3600.0
            if got > 30.0 * 60.0:
                yale_wrong.append(f"    {en}: Yale is {got / 60.0:.1f}' from Hipparcos "
                                  f"HIP {hip}")
            continue
        print(
            f"  ! {en}: SIMBAD has no single object for this name -- kept as"
            " yale_rounded (position inherited from the app's own table, so it"
            " is NOT Hipparcos-verified)",
            flush=True,
        )
    if yale_wrong:
        print(f"\n  !! {len(yale_wrong)} rows where the app's own star table"
              " disagrees with Hipparcos by >30' -- the app table is stale:",
              flush=True)
        for line in yale_wrong:
            print(line, flush=True)

    unresolved = [en for en, _, _, _, _ in base if en not in hip_by_star or hip_by_star[en] not in rows2]
    if unresolved:
        print(f"  UNRESOLVED: {unresolved}", flush=True)
    if dirty:
        cache_p.write_text(json.dumps(cache, indent=1), encoding="utf-8")

    years = (J2000_JD - HIP2_EPOCH_JD) / 365.25
    catalogue: dict[str, dict] = {}
    provenance: dict[str, dict] = {}
    for en, th, ra_h, dec, mag in base:
        hip = hip_by_star.get(en)
        rec: dict = {"en": en, "th": th, "mag": mag}
        if hip is not None and hip in rows2:
            r2 = rows2[hip]
            pmra = float(r2["pmRA"]) if str(r2["pmRA"]).strip() else 0.0
            pmde = float(r2["pmDE"]) if str(r2["pmDE"]).strip() else 0.0
            ra00, dec00 = propagate(float(r2["RArad"]), float(r2["DErad"]),
                                     pmra, pmde, years)
            rec.update(ra_h=ra00 / 15.0, dec_deg=dec00,
                       pm_ra_masyr=pmra, pm_dec_masyr=pmde, hip=hip,
                       precision="hip2_full")
            if str(r2["Hpmag"]).strip():
                rec["vmag"] = float(r2["Hpmag"])
            if hip in rows1 and str(rows1[hip]["RAICRS"]).strip():
                d_ra = ((ra00 - float(rows1[hip]["RAICRS"]) + 540) % 360 - 180) * 3600.0
                d_ra *= math.cos(math.radians(dec00))
                d_dec = (dec00 - float(rows1[hip]["DEICRS"])) * 3600.0
                rec["check_hip1_arcsec"] = round(math.hypot(d_ra, d_dec), 3)
        else:
            rec.update(ra_h=ra_h, dec_deg=dec, pm_ra_masyr=None,
                       pm_dec_masyr=None, hip=hip, precision="yale_rounded")
            unresolved.append(en) if en not in unresolved else None
        catalogue[en] = rec
        provenance[en] = rec.get("precision", "?")

    out_mod = BACKEND / "src" / "services" / "star_catalogue.py"
    lines = [
        '"""GENERATED by scripts/fetch_bright_star_catalogue.py -- do not hand-edit.',
        "",
        "One star catalogue for the whole app.  Astrometry is I/311/hip2",
        "(Hipparcos New Reduction, van Leeuwen 2007, ICRS Ep=1991.25) propagated",
        "to J2000 with each star's own proper motion.  Stars SIMBAD could not",
        "resolve keep their Yale BSC position, tagged precision='yale_rounded',",
        "and carry no proper motion -- they are never given a fabricated one.",
        "",
        "pm_ra_masyr is mu_alpha*cos(dec);  pm_dec_masyr is mu_delta.",
        '"""',
        "from __future__ import annotations",
        "",
        "# en -> {'th', 'mag', 'ra_h', 'dec_deg', 'pm_ra_masyr', 'pm_dec_masyr',",
        "#        'hip', 'precision'}",
        "BRIGHT_STARS: dict[str, dict] = {",
    ]
    for en in sorted(catalogue, key=lambda k: catalogue[k]["ra_h"]):
        r = catalogue[en]
        pmr = "None" if r["pm_ra_masyr"] is None else f"{r['pm_ra_masyr']!r}"
        pmd = "None" if r["pm_dec_masyr"] is None else f"{r['pm_dec_masyr']!r}"
        hip = "None" if r["hip"] is None else str(r["hip"])
        lines.append(
            f'    "{en}": {{"th": "{r["th"]}", "mag": {r["mag"]!r}, '
            f'"ra_h": {r["ra_h"]!r}, "dec_deg": {r["dec_deg"]!r}, '
            f'"pm_ra_masyr": {pmr}, "pm_dec_masyr": {pmd}, '
            f'"hip": {hip}, "precision": "{r["precision"]}"}},'
        )
    lines += ["}", "",
              "STAR_NAMES = tuple(sorted(BRIGHT_STARS))", ""]
    out_mod.write_text("\n".join(lines), encoding="utf-8")

    (HERE / "bright_star_catalogue.json").write_text(
        json.dumps({"generated_by": "scripts/fetch_bright_star_catalogue.py",
                    "epoch": "J2000.0 ICRS",
                    "counts": {
                        "total": len(catalogue),
                        "hip2_full": sum(1 for v in catalogue.values()
                                         if v["precision"] == "hip2_full"),
                        "yale_rounded": sum(1 for v in catalogue.values()
                                            if v["precision"] == "yale_rounded"),
                    },
                    "stars": catalogue}, indent=2, ensure_ascii=False),
        encoding="utf-8")

    print(f"\nwrote {out_mod}")
    print(f"  hip2_full     : {sum(1 for v in catalogue.values() if v['precision'] == 'hip2_full')}")
    print(f"  yale_rounded  : {sum(1 for v in catalogue.values() if v['precision'] == 'yale_rounded')}")
    if unresolved:
        print("  unresolved    :", ", ".join(sorted(set(unresolved))))


if __name__ == "__main__":
    main()
