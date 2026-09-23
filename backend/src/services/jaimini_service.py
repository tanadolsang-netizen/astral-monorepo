"""Jaimini astrology — Chara Karakas, Arudha Padas, Karakamsa, Chara Dasha."""

from __future__ import annotations

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
            "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]

KARAKA_ORDER_7 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]
KARAKA_TH = {"AK": "อาตมาการะ (ดวงวิญญาณ)", "AmK": "อัมมาตรการะ (อาชีพ)",
             "BK": "ภาตรุการะ (พี่น้อง)", "MK": "มาตรุการะ (มารดา)",
             "PK": "ปุตรการะ (บุตร)", "GK": "ชญาติการะ (ญาติ/ศัตรู)",
             "DK": "ทาราการะ (คู่สมรส)"}


def chara_karakas(planet_lons: dict[str, float],
                  scheme: int = 8) -> list[dict]:
    """Rank planets by degree-within-sign DESC. Rahu uses 30−degree."""
    entries = []
    for name, lon in planet_lons.items():
        lon = float(lon)
        deg_in_sign = lon % 30
        if name == "Rahu":
            deg_in_sign = 30 - deg_in_sign
        entries.append({"planet": name, "deg_in_sign": round(deg_in_sign, 3),
                        "sort_key": deg_in_sign})
    entries.sort(key=lambda e: e["deg_in_sign"], reverse=True)

    use = KARAKA_ORDER_7 if scheme == 7 else (
        ["AK", "AmK", "BK", "MK", "PK", "GK", "DK", "—"][:max(7, scheme)])
    for i, e in enumerate(entries):
        e["karaka"] = use[i] if i < len(use) else "—"
        e["karaka_th"] = KARAKA_TH.get(e["karaka"], "")
    return entries


def atmakaraka(planet_lons: dict[str, float]) -> dict:
    ks = chara_karakas(planet_lons)
    return ks[0]


def arudha_padas(planet_lons: dict[str, float], house_signs: dict[str, int]) -> dict:
    """Arudha of house X: count from sign to its lord's sign, reflect same.
    house_signs: {"1": lord_sign_idx, ...} provided by caller (sign lords).
    Exception rules: if arudha falls in same sign → 10th from it;
    if 7th → 4th from it (classical Jaimini exceptions).
    """
    out = {}
    for hkey, lord_sign in house_signs.items():
        try:
            h = int(hkey) - 1
        except ValueError:
            continue
        dist = (lord_sign - h) % 12
        arudha = (h + dist * 2) % 12
        if arudha == h:               # same sign exception
            arudha = (h + 9) % 12     # 10th from it
        elif arudha == (h + 6) % 12:  # 7th sign exception
            arudha = (h + 3) % 12     # 4th from it
        out[f"A{h+1}"] = {"sign_en": SIGNS[arudha], "sign_th": SIGNS_TH[arudha]}
    return out


def karakamsa(planet_lons: dict[str, float]) -> dict:
    """Navamsa sign of Atmakaraka."""
    ak = atmakaraka(planet_lons)
    lon = planet_lons[ak["planet"]]
    navamsa_index = int((lon * 9) // 30) % 12
    return {"karaka": ak["karaka"], "planet": ak["planet"],
            "navamsa_sign_en": SIGNS[navamsa_index],
            "navamsa_sign_th": SIGNS_TH[navamsa_index]}


def chara_dasha(lagna_sign_idx: int, years_per_sign: int = 6,
                max_periods: int = 12) -> list[dict]:
    """KN-Rao-simplified Chara dasha: direct for odd-footed signs,
    reverse for even-footed. Odd-footed: Ar, Ge, Le, Li, Sg, Aq (idx 0,2,4,...)."""
    odd_footed = lagna_sign_idx % 2 == 0
    periods = []
    idx = lagna_sign_idx
    age = 0
    for _ in range(max_periods):
        periods.append({"sign_en": SIGNS[idx], "sign_th": SIGNS_TH[idx],
                        "age_from": age, "age_to": age + years_per_sign})
        age += years_per_sign
        idx = (idx + (1 if odd_footed else -1)) % 12
    return periods


def compute_jaimini(natal_bodies_sidereal: dict[str, float],
                    asc_lon_sidereal: float,
                    person_name: str = "") -> dict:
    karakas = chara_karakas(natal_bodies_sidereal)
    ak = karakas[0]
    dk = next((k for k in karakas if k["karaka"] == "DK"), None)
    kamsa = karakamsa(natal_bodies_sidereal)
    asc_idx = int(asc_lon_sidereal // 30) % 12

    # sign lords for arudhas (classical rulers)
    LORD_OF = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
               5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
               9: "Saturn", 10: "Saturn", 11: "Jupiter"}
    house_signs = {}
    for h in range(12):
        sign_idx = (asc_idx + h) % 12
        lord_lon = natal_bodies_sidereal.get(LORD_OF[sign_idx])
        if lord_lon is not None:
            house_signs[str(h + 1)] = int(lord_lon // 30) % 12
    arudhas = arudha_padas(natal_bodies_sidereal, house_signs)
    dasha = chara_dasha(asc_idx)

    result = {
        "system": "jaimini",
        "karakas": [{"planet": k["planet"], "karaka": k["karaka"],
                     "karaka_th": k["karaka_th"],
                     "deg_in_sign": k["deg_in_sign"]} for k in karakas],
        "atmakaraka": {"planet": ak["planet"], "sign_th": SIGNS_TH[int(
            natal_bodies_sidereal[ak["planet"]] // 30) % 12]},
        "darakaraka": dk["planet"] if dk else None,
        "karakamsa": kamsa,
        "chara_dasha_first4": dasha[:4],
        "interpretation": {
            "th": (
                f"ดวงวิญญาณของคุณคือ <b>{ak['planet']}</b> "
                f"(อาตมาการะ) — ภาระของชีวิตนี้คือการพัฒนาคุณค่าของดาวดวงนี้ให้เต็มที่ "
                f"คู่สมรสและความสัมพันธ์สะท้อนผ่าน <b>{dk['planet'] if dk else '-'}</b> "
                f"(ทาราการะ) Karakamsa อยู่ราศี{kamsa['navamsa_sign_th']} — "
                f"ชี้ไปที่หน้าที่แห่งจิตวิญญาณในสาย{('ธรรมะและการสอน' if kamsa['navamsa_sign_th'] in ['พฤหัส', 'กันย์', 'มีน'] else 'การค้าและการสื่อสาร' if kamsa['navamsa_sign_th'] in ['เมถุน', 'พิจิก'] else 'ศิลป์และความงาม' if kamsa['navamsa_sign_th'] in ['ตุลย์', 'พฤษภ'] else 'การนำและความกล้า')}"
            ),
            "en": (
                f"Soul-planet (Atmakaraka): {ak['planet']}. "
                f"Spouse-indicator (Darakaraka): {dk['planet'] if dk else 'n/a'}. "
                f"Karakamsa in {kamsa['navamsa_sign_en']} — the soul's vocation axis."
            ),
        },
    }
    if person_name:
        result["person_name"] = person_name
    return result
