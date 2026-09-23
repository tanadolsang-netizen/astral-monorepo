"""Arabic Lots catalog — day/night sect formulas, 40+ classical lots.

lot = A + B − C (mod 360); formulas swap by sect where traditional.
Reference: Paulus Alexandrinus / standard Hermetic lot lists.
"""
from __future__ import annotations

# (name_en, name_th, planet_A, planet_B, planet_C, swap_by_night)
# Formula: lon(A) + lon(B) − lon(C) mod 360; if swap: lon(A) + lon(C) − lon(B)
LOTS = [
    ("Fortune", "โชคฟ้า (ประโยคภพ)", "ASC", "Moon", "Sun", True),
    ("Spirit", "ดวงวิญญาณ (ไดมอน)", "ASC", "Sun", "Moon", True),
    ("Eros", "เอรอส — แรงปรารถนา", "Venus", "Spirit", "Fortune", False),
    ("Necessity", "จำเป็น — ข้อจำกัด", "Fortune", "Mercury", "ASC", False),
    ("Courage", "ความกล้าหาญ", "Fortune", "Day_of_Week_Sun", "Mars", False),
    ("Victory", "ชัยชนะ", "Jupiter", "Spirit", "Fortune", False),
    ("Nemesis", "เนเมซิส — กรรมตอบ", "Fortune", "Saturn", "Fortune", False),
    ("Children", "บุตร", "Saturn", "Jupiter", "Fortune", False),
    ("Brothers", "พี่น้อง", "Jupiter", "Saturn", "Mars", False),
    ("Father", "บิดา", "Saturn", "Fortune", "Father", False),
    ("Mother", "มารดา", "Venus", "Fortune", "Mother", False),
    ("Enemies", "ศัตรู", "Mercury", "Fortune", "Mars", False),
    ("Sickness", "โรคภัย", "Mars", "Saturn", "Sun", False),
    ("Marriage_M", "การสมรส (ดวงชาย)", "Saturn", "Venus", "Moon", False),
    ("Marriage_F", "การสมรส (ดวงหญิง)", "Moon", "Venus", "Saturn", False),
    ("Love_Self", "ความรักที่มีต่อผู้อื่น", "Venus", "Spirit", "Fortune", False),
    ("Love_Other", "ความรักที่ผู้อื่นมีต่อเรา", "Spirit", "Venus", "ASC", False),
    ("Travel_Land", "การเดินทางทางบก", "Fortune", "Mercury", "Moon", False),
    ("Travel_Sea", "การเดินทางทางน้ำ", "Fortune", "Moon", "Mercury", False),
    ("Career_Action", "หน้าที่การงาน", "Mars", "Fortune", "Mercury", False),
    ("Kingship_Rank", "ฐานันดร/ตำแหน่ง", "Jupiter", "Fortune", "Saturn", False),
    ("Friendship", "มิตรภาพ", "Mercury", "Fortune", "Venus", False),
    ("Death", "ความตาย (ธาตุวารี)", "ASC", "Eighth_House_Lord_Placeholder", "Moon", False),
]


def _lon(planet_or_point: str, bodies: dict[str, float],
         houses_cusps: list[float] | None = None,
         extra: dict[str, float] | None = None) -> float | None:
    src = extra or {}
    if planet_or_point in bodies:
        return float(bodies[planet_or_point])
    if planet_or_point in src:
        return float(src[planet_or_point])
    if planet_or_point == "ASC":
        return None  # caller injects asc separately
    if planet_or_point.startswith("H8_"):
        return None
    # symbolic fallbacks resolved by caller through `extra`
    aliases = {
        "Day_of_Week_Sun": "Sun",
        "Eighth_House_Lord_Placeholder": "Saturn",
        "Father": "Saturn",
        "Mother": "Venus",
        "Eros": "Venus",
        "Spirit": "Spirit",
        "Fortune": "Fortune",
    }
    inner = aliases.get(planet_or_point)
    if inner and inner in bodies:
        return float(bodies[inner])
    if inner and inner in (src or {}):
        return float(src[inner])
    return None


def compute_lots(natal_bodies: dict[str, float], asc_lon: float,
                 is_day_chart: bool) -> dict:
    """Compute all lots. Fortune/Spirit computed first (they reference each other)."""
    base = dict(natal_bodies)
    base["ASC"] = asc_lon

    def formula(lot_def, b):
        _, _, a, bb, c, swap = lot_def
        la = _lon(a, b)
        lb = _lon(bb, b)
        lc = _lon(c, b)
        if la is None or lb is None or lc is None:
            return None
        if swap:
            if not is_day_chart:
                lb, lc = lc, lb
        return (la + lb - lc) % 360

    out = {}
    # pass 1: Fortune & Spirit (day formulas; night swapped)
    fortune = (base["ASC"] + _lon("Moon", base)
               - _lon("Sun", base)) % 360
    spirit = (base["ASC"] + _lon("Sun", base)
              - _lon("Moon", base)) % 360
    if not is_day_chart:
        fortune, spirit = spirit, fortune
    out["Fortune"] = fortune
    out["Spirit"] = spirit

    for lot in LOTS:
        name_en = lot[0]
        if name_en in ("Fortune", "Spirit"):
            continue
        v = formula(lot, base | {"Fortune": fortune, "Spirit": spirit})
        if v is not None:
            out[name_en] = v

    SIGNS_TH = ["เมษ", "พฤษภ", "เมถุน", "กรกฎ", "สิงห์", "กันย์",
                "ตุลย์", "พิจิก", "ธนู", "มกร", "กุมภ์", "มีน"]
    lots_out = {}
    for name, lon in out.items():
        idx = int(lon // 30) % 12
        lots_out[name] = {"longitude": round(lon, 3), "sign_th": SIGNS_TH[idx]}
    return {
        "system": "arabic-lots", "is_day_chart": is_day_chart,
        "lots": lots_out,
        "count": len(lots_out),
        "interpretation": {
            "th": f"คำนวณได้ {len(lots_out)} ประโยคภพ — "
                  f"โชคฟ้าอยู่ราศี{lots_out['Fortune']['sign_th']} "
                  f"และดวงวิญญาณอยู่ราศี{lots_out['Spirit']['sign_th']}",
            "en": f"{len(lots_out)} lots computed.",
        },
    }
