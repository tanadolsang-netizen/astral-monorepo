"""Grand Fusion — Universe Phase 2/4 extended sections.

``compute_grand_fusion`` composes the grand modules over a stored
profile's birth data and returns one payload:

{
  "person":   {name, birth data},
  "extended": {
      "fixed_stars":  {...royal-star contacts + Sabian symbols...},
      "asteroids":    {...Chiron/Ceres/Pallas/Juno/Vesta or graceful unavailable...},
      "varshaphal":   {"years": {YYYY: {return instant, lagna, muntha, year lord, sahams}}},
      "ziwei":        {...lunar month/day, Life/Body Palace, Sui Po per year...},
      # Phase 4 sciences:
      "numerology":   {...Life Path / Birth Day / Personal Years (+ name numbers if given)...},
      "iching":       {...seeded deterministic hexagram cast + date-fallback cross-check...},
      "ninestar_ki":  {...year star real; month/day stars constant_unpinned [VERIFY]...},
      "mayan_tzolkin":{...Dreamspell Kin/seal/tone + daily Kin...},
      "cosmobiology": {...Ebertin midpoint tree C(n,2), pictures ≤2°, confirmed ≤1°...},
      "human_design": {...Type/Authority/Definition + profile gate.lines, status ok...}
      "kalachakra":   {...Rabjung year element/animal/gender + parkha day number...}
  },
  "reading":  {"th": ..., "en": ...}   # one-line summaries per section
}

Precedence note (fusion rules §4): these are backdrop layers — dated transit
windows from the daily fusion engine remain the clock; nothing here may
contradict them, only color them.
"""

from __future__ import annotations

from datetime import date as date_type, datetime, time as time_type, timezone

from src.services.chart_service import compute_chart
from src.services.grand.asteroids import compute_asteroids
from src.services.grand.cosmobiology import compute_cosmobiology
from src.services.grand.fixed_stars import compute_fixed_stars
from src.services.grand.human_design import compute_human_design
from src.services.grand.iching import compute_iching
from src.services.grand.kalachakra import compute_kalachakra
from src.services.grand.mayan_tzolkin import compute_mayan_tzolkin
from src.services.grand.ninestar_ki import compute_ninestar_ki
from src.services.grand.numerology import compute_numerology
from src.services.grand.varshaphal import compute_varshaphal
from src.services.grand.ziwei import compute_ziwei, ziwei_summary


def _default_years() -> list[int]:
    now = datetime.now(timezone.utc)
    return [now.year, now.year + 1]


def _varsha_brief(v: dict, max_aspects: int = 6) -> dict:
    return {
        "return_datetime_utc": v["return_datetime_utc"],
        "system": v["system"],
        "varsha_lagna": v["varsha_lagna"],
        "muntha": v["muntha"],
        "year_lord": v["year_lord"],
        "sahams": v["sahams"],
        "tajika_aspects": v["tajika_aspects"][:max_aspects],
        "tajika_aspect_count": len(v["tajika_aspects"]),
    }


def compute_grand_fusion(
    name: str,
    lang: str = "th",
    years: list[int] | None = None,
    profile: dict | None = None,
) -> dict:
    """All four grand modules over a stored profile. `profile` may be injected
    directly (tests); otherwise it is loaded from the fusion profile store."""
    if profile is None:
        from src.routers.fusion_profile import _load_profile
        profile = _load_profile(name)

    birth_date = date_type.fromisoformat(profile["date"])
    birth_time = time_type.fromisoformat(profile["time"])
    tz = float(profile.get("tz_offset_hours", 7.0))
    lat = float(profile.get("lat", 13.8591))
    lon = float(profile.get("lon", 100.5217))
    years = years or _default_years()

    natal_tropical = compute_chart(
        name=name, date=birth_date, time=birth_time,
        tz_offset_hours=tz, lat=lat, lon=lon, system="tropical",
    )

    fixed_stars = compute_fixed_stars(natal_tropical)
    asteroids = compute_asteroids(natal_tropical)

    varshaphal_years: dict[str, dict] = {}
    for y in sorted(set(years)):
        varshaphal_years[str(y)] = _varsha_brief(
            compute_varshaphal(
                name=name, birth_date=birth_date, birth_time=birth_time,
                target_year=y, tz_offset_hours=tz, lat=lat, lon=lon,
                system="sidereal",
            )
        )

    zw = compute_ziwei(birth_date, birth_time, annual_years=years)

    # Phase 4 sciences (QA notes 2026-08-23 govern each module).
    numerology = compute_numerology(birth_date)
    iching = compute_iching(user_id=name, iso_date=profile["date"])
    ninestar = compute_ninestar_ki(birth_date)
    mayan = compute_mayan_tzolkin(birth_date)
    cosmobiology = compute_cosmobiology(natal_tropical)
    # Phase 4.5 unlock: real HD Profile (gate/line wheel + design-moment
    # ephemeris) and Rabjung year layer (verified anchor data).
    human_design = compute_human_design(natal_chart=natal_tropical)
    kalachakra = compute_kalachakra(birth_date)

    reading = _reading(
        name, lang, fixed_stars, varshaphal_years, zw, asteroids,
        numerology=numerology, iching=iching, ninestar=ninestar,
        mayan=mayan, cosmobiology=cosmobiology,
        human_design=human_design, kalachakra=kalachakra,
    )

    return {
        "person": {
            "name": name,
            "birth": {
                "date": profile["date"],
                "time": profile["time"],
                "tz_offset_hours": tz,
                "lat": lat,
                "lon": lon,
            },
        },
        "extended": {
            "fixed_stars": fixed_stars,
            "asteroids": asteroids,
            "varshaphal": {"years": varshaphal_years},
            "ziwei": zw,
            "numerology": numerology,
            "iching": iching,
            "ninestar_ki": ninestar,
            "mayan_tzolkin": mayan,
            "cosmobiology": cosmobiology,
            "human_design": human_design,
            "kalachakra": kalachakra,
        },
        "reading": reading,
        "precedence_note": "backdrop layers only — transit windows remain the clock (fusion rules §4)",
    }


def _reading(
    name, lang, fixed_stars, varshaphal_years, zw, asteroids,
    numerology=None, iching=None, ninestar=None, mayan=None,
    cosmobiology=None, human_design=None, kalachakra=None,
) -> dict:
    """One-line summaries per section (th + en always present)."""
    royal = fixed_stars.get("royal_star_contacts", [])
    sab_sun = fixed_stars.get("sabian", {}).get("sun", {})

    star_th = "ดาวฤกษ์หลวงไม่มีดาวเคราะห์ใดเข้าเกณฑ์ 2° ในดวงเกิด" if not royal else (
        "ดาวฤกษ์หลวง: " + " · ".join(
            f"{c['natal_point']}–{c['star']} (orb {c['orb_deg']}°)" for c in royal[:3]
        )
    )
    star_en = "No royal-star contact within 2° in the natal chart." if not royal else (
        "Royal stars: " + " · ".join(
            f"{c['natal_point']}–{c['star']} (orb {c['orb_deg']}°)" for c in royal[:3]
        )
    )

    varsha_th = " · ".join(
        f"ปี {y}: มุณฐะราศี{v['muntha']['sign']} เจ้าปี {v['year_lord']['planet']}"
        for y, v in sorted(varshaphal_years.items())
    )
    varsha_en = " · ".join(
        f"{y}: Muntha {v['muntha']['sign']}, Year Lord {v['year_lord']['planet']}"
        for y, v in sorted(varshaphal_years.items())
    )

    lp = zw.get("life_palace", {})
    annual = zw.get("annual", {})
    zw_th = (
        f"ตถุดาว: เดือนจันทรคติ {zw['lunar']['month']} วัน {zw['lunar']['day']} "
        f"เข้าชั่วโมง{zw['lunar']['hour_zhi']} — 命宮ที่ {lp.get('branch')} "
        + (" · ".join(f"ปี {y} 歲破ที่ {v['sui_po_branch']}" for y, v in sorted(annual.items())) if annual else "")
    ).strip(" —")
    zw_en = (
        f"Lunar month {zw['lunar']['month']}, day {zw['lunar']['day']}, hour {zw['lunar']['hour_zhi']}"
        f" — Life Palace at {lp.get('branch')}"
        + (" · ".join(f"{y} Sui Po at {v['sui_po_branch']}" for y, v in sorted(annual.items())) if annual else "")
    ).rstrip(" —")

    if asteroids.get("status") == "ok":
        ast_th = "ดาวเคราะห์น้อย (Chiron/Ceres/Pallas/Juno/Vesta) คำนวณจาก Swiss Ephemeris สำเร็จ"
        ast_en = "Asteroids computed from Swiss Ephemeris."
    else:
        ast_th = "ดาวเคราะห์น้อยยังไม่พร้อม (ไม่มีไฟล์ Swiss Ephemeris) — ข้ามอย่างสง่างาม"
        ast_en = "Asteroids unavailable (no Swiss Ephemeris files) — degraded gracefully."

    # ---- Phase 4 sciences ----
    numerology = numerology or {}
    if numerology.get("status") == "ok":
        lp = numerology["life_path"]["number"]
        pys = numerology.get("personal_year", {})
        py_txt = "/".join(str(v["number"]) for _, v in sorted(pys.items()))
        num_th = (
            f"ตัวเลขศาสตร์: Life Path {lp} ({numerology['life_path']['core_th']}) · "
            f"ปีส่วนบุคคล {py_txt}"
        )
        num_en = (
            f"Numerology: Life Path {lp} ({numerology['life_path']['core_en']}) · "
            f"Personal Year {py_txt}"
        )
    else:
        reason = numerology.get("reason", "unavailable")
        num_th = f"ตัวเลขศาสตร์ยังไม่พร้อม — {reason}"
        num_en = f"Numerology unavailable — {reason}"

    iching = iching or {}
    if iching.get("status") == "ok" and iching.get("primary"):
        prim = iching["primary"]
        n_changing = len(iching.get("changing_line_indexes", []))
        ich_th = (
            f"หยี่จิ๋ง: #{prim['king_wen']} {prim['cn']} {prim['th']} — "
            f"เส้นเปลี่ยน {n_changing} เส้น · nuclear #{iching['nuclear']['king_wen']}"
        )
        ich_en = (
            f"I Ching: #{prim['king_wen']} {prim['cn']} {prim['en']} — "
            f"{n_changing} changing line(s) · nuclear #{iching['nuclear']['king_wen']}"
        )
    else:
        reason = iching.get("reason", "unavailable")
        ich_th = f"หยี่จิ๋งยังไม่พร้อม — {reason}"
        ich_en = f"I Ching unavailable — {reason}"

    ninestar = ninestar or {}
    ys = ninestar.get("year_star", {}) if ninestar.get("status") == "ok" else None
    if ys:
        nsk_th = f"ดาวประจำปีเกิด (Nine Star Ki): {ys['name_th']} — {ys['core_th']} (ค่าคงที่เดือน/วัน ยังไม่ pin [VERIFY])"
        nsk_en = (
            f"Nine Star Ki year star: {ys['name_en']} — {ys['core_en']} "
            "(month/day constants unpinned [VERIFY])"
        )
    else:
        reason = ninestar.get("reason", "unavailable")
        nsk_th = f"Nine Star Ki ยังไม่พร้อม — {reason}"
        nsk_en = f"Nine Star Ki unavailable — {reason}"

    mayan = mayan or {}
    if mayan.get("status") == "ok":
        may_th = f"ทซอลกิน (Dreamspell): {mayan['signature_th']} — {mayan['seal'].get('keyword_th') or mayan['seal']['keyword_en']}"
        may_en = f"Mayan Dreamspell: {mayan['signature_en']} — {mayan['seal']['keyword_en']}"
    else:
        reason = mayan.get("reason", "unavailable")
        may_th = f"ทซอลกินยังไม่พร้อม — {reason}"
        may_en = f"Mayan Tzolkin unavailable — {reason}"

    cosmobiology = cosmobiology or {}
    if cosmobiology.get("status") == "ok":
        cb_th = (
            f"จุดกึ่งกลาง (Ebertin): {cosmobiology['pair_count']} คู่ · "
            f"ภาพ ≤2° {cosmobiology['picture_count']} ภาพ "
            f"(ยืนยัน ≤1° {len(cosmobiology['confirmed_pictures'])} ภาพ)"
        )
        cb_en = (
            f"Midpoint tree (Ebertin): {cosmobiology['pair_count']} pairs · "
            f"{cosmobiology['picture_count']} pictures within 2° "
            f"({len(cosmobiology['confirmed_pictures'])} confirmed ≤1°)"
        )
    else:
        reason = cosmobiology.get("reason", "unavailable")
        cb_th = f"จุดกึ่งกลางยังไม่พร้อม — {reason}"
        cb_en = f"Cosmobiology unavailable — {reason}"

    def _unavail(section, data):
        data = data or {}
        reason = data.get("reason", "unavailable")
        return {
            "th": f"{section}ยังไม่พร้อม — {reason}",
            "en": f"{section} unavailable — {reason}",
        }

    hd = human_design or {}
    if hd.get("status") in ("ok", "partial"):
        prof = hd.get("profile", {})
        hd_th = (
            f"ฮิวแมนดีไซน์: {hd.get('type', '?')} · อำนาจตัดสินใจ {hd.get('authority', '?')} · "
            f"โปรไฟล์ {prof.get('profile_name')} "
            f"(ดวงอาทิตย์เกิด {prof.get('p_sun')} · ดวงอาทิตย์ดีไซน์ {prof.get('d_sun')})"
        )
        hd_en = (
            f"Human Design: {hd.get('type', '?')} · Authority {hd.get('authority', '?')} · "
            f"profile {prof.get('profile_name')} "
            f"(Personality Sun {prof.get('p_sun')} · Design Sun {prof.get('d_sun')})"
        )
        hd_lines = {"th": hd_th, "en": hd_en}
    else:
        hd_lines = _unavail("Human Design", hd)

    kal = kalachakra or {}
    if kal.get("status") == "ok":
        y = kal.get("year", {})
        approx = " (approx.)" if kal.get("losar_rule", {}).get("approximate") else ""
        kal_th = (
            f"ปีทิเบต (Rabjung): {y.get('element')} {y.get('animal')} ({y.get('gender')})"
            f"{approx} · พาร์คาวันที่ {kal.get('parkha_day_number')}"
        )
        kal_en = (
            f"Tibetan year (Rabjung): {y.get('element')} {y.get('animal')} ({y.get('gender')})"
            f"{approx} · Parkha day number {kal.get('parkha_day_number')}"
        )
        kal_lines = {"th": kal_th, "en": kal_en}
    else:
        kal_lines = _unavail("Kalachakra", kal)

    return {
        "th": {
            "fixed_stars": star_th,
            "sabian_sun": f"ซาเบียนดวงอาทิตย์: {sab_sun.get('phrase_th', '')}" if sab_sun else "",
            "varshaphal": f"วรรษผล {name}: {varsha_th}",
            "ziwei": zw_th,
            "asteroids": ast_th,
            "numerology": num_th,
            "iching": ich_th,
            "ninestar_ki": nsk_th,
            "mayan_tzolkin": may_th,
            "cosmobiology": cb_th,
            "human_design": hd_lines["th"],
            "kalachakra": kal_lines["th"],
        },
        "en": {
            "fixed_stars": star_en,
            "sabian_sun": f"Sabian Sun: {sab_sun.get('phrase_en', '')}" if sab_sun else "",
            "varshaphal": f"Varshaphal {name}: {varsha_en}",
            "ziwei": zw_en,
            "asteroids": ast_en,
            "numerology": num_en,
            "iching": ich_en,
            "ninestar_ki": nsk_en,
            "mayan_tzolkin": may_en,
            "cosmobiology": cb_en,
            "human_design": hd_lines["en"],
            "kalachakra": kal_lines["en"],
        },
    }
