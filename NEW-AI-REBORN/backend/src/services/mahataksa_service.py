"""มหาทักษา (Maha Taksa) — Thai destiny-cycle engine + เลขเจ้าสังวาลย์.

Classical Thai astrology: 108-year planetary cycle. Start lord = birth
weekday's lord; sequence follows the classical taksa rotation; sub-lords
(อธิโบดิ) proportional to fixed planet strengths.
Deterministic, offline, documented in-code.
"""
from __future__ import annotations

from datetime import date

# Fixed planet strengths (ตัวเลขมาตรฐานวิชามหาทักษา)
STRENGTHS = {
    "Sun": 6, "Moon": 15, "Mars": 8, "Mercury": 17,
    "Saturn": 10, "Jupiter": 19, "Rahu": 12, "Venus": 21,
}
STRENGTH_TH = {"Sun": "อาทิตย์", "Moon": "จันทร์", "Mars": "อังคาร",
               "Mercury": "พุธ", "Saturn": "เสาร์", "Jupiter": "พฤหัสฯ",
               "Rahu": "ราหู", "Venus": "ศุกร์"}

# Classical rotation order of the eight lords
ROTATION = ["Sun", "Moon", "Mars", "Rahu", "Venus",
            "Mercury", "Jupiter", "Saturn"]

WEEKDAY_START_LORD = {
    # birth weekday → first maha-taksa lord (classical mapping)
    0: "Sun",     # Sunday → อาทิตย์
    1: "Moon",    # Monday → จันทร์
    2: "Mars",    # Tuesday → อังคาร
    3: "Mercury", # Wednesday → พุธ
    4: "Jupiter", # Thursday → พฤหัสฯ
    5: "Venus",   # Friday → ศุกร์
    6: "Saturn",  # Saturday → เสาร์
}

WEEKDAY_TH = ["อาทิตย์", "จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์"]

CYCLE = sum(STRENGTHS.values())  # 108


def _rotation_index(lord: str) -> int:
    return ROTATION.index(lord)


def _taksa_sequence(start_lord: str) -> list[str]:
    """Full 8-lord rotation starting from start_lord (classical cycle)."""
    i = _rotation_index(start_lord)
    return [ROTATION[(i + k) % 8] for k in range(8)]


def compute_mahataksa(birth_date_iso: str, query_date_iso: str | None = None) -> dict:
    b = date.fromisoformat(birth_date_iso)
    q = date.fromisoformat(query_date_iso) if query_date_iso else date.today()

    weekday = b.weekday()  # Mon=0..Sun=6 in Python! adjust to Sun=0 table
    # Python: Monday=0 ... Sunday=6 → convert to Sunday=0 convention
    sunday0 = (weekday + 1) % 7
    start_lord = WEEKDAY_START_LORD[sunday0]

    seq = _taksa_sequence(start_lord)

    # Build full life timeline: each maha-taksa lord spans its strength years,
    # cycling until CYCLE (108) years covered.
    timeline = []  # (lord, age_from, age_to)
    age = 0.0
    lord_i = 0
    while age < CYCLE:
        lord = seq[lord_i % len(seq)]
        span = float(STRENGTHS[lord])
        timeline.append((lord, round(age, 2), round(min(age + span, CYCLE), 2)))
        age += span
        lord_i += 1

    age_now = (q - b).days / 365.2425

    current = next((t for t in timeline if t[1] <= age_now < t[2]), timeline[-1])
    cur_lord = current[0]

    # athibodi sub-lords inside current period, proportional to strengths
    remaining = STRENGTHS[cur_lord]
    subs = []
    sub_age = current[1]
    j = _rotation_index(cur_lord)
    sub_seq = [ROTATION[(j + k) % 8] for k in range(8)]
    for sub_lord in sub_seq:
        span = remaining * STRENGTHS[sub_lord] / CYCLE
        end = min(sub_age + span, current[2])
        subs.append({"lord": sub_lord, "th": STRENGTH_TH[sub_lord],
                     "from": round(sub_age, 3), "to": round(end, 3)})
        sub_age = end
        if sub_age >= current[2]:
            break
    cur_sub = next((s for s in subs if s["from"] <= age_now < s["to"]), subs[-1])

    favorable = [l for l in ("Jupiter", "Venus", "Mercury", "Moon") ]
    unfavorable = ["Rahu", "Saturn"]

    result = {
        "system": "maha-taksa",
        "birth_weekday_th": WEEKDAY_TH[sunday0],
        "start_lord": start_lord,
        "start_lord_th": STRENGTH_TH[start_lord],
        "cycle_years": CYCLE,
        "current": {
            "age": round(age_now, 2),
            "maha_lord": cur_lord, "maha_lord_th": STRENGTH_TH[cur_lord],
            "athibodi_lord": cur_sub["lord"],
            "athibodi_th": cur_sub["th"],
        },
        "timeline": [{"lord": t[0], "th": STRENGTH_TH[t[0]],
                      "from": t[1], "to": t[2]} for t in timeline],
        "interpretation": {"th": "", "en": ""},
    }

    tone = "ดี" if cur_lord in favorable else ("ปานกลาง" if cur_lord == "Sun" else "ต้องระวัง")
    result["interpretation"]["th"] = (
        f"คุณเกิดวัน{WEEKDAY_TH[sunday0]} มหาทักษาเริ่มที่{STRENGTH_TH[start_lord]} "
        f"ตอนนี้อายุ {result['current']['age']:.1f} ปี อยู่ในกาล{STRENGTH_TH[cur_lord]} "
        f"(อธิโบดิ: {cur_sub['th']}) — ช่วงนี้โดยรวม{tone} "
        + ("โชคและโอกาสเข้ามาไม่ขาดมือ" if cur_lord == "Jupiter"
           else "เรื่องความรักและศิลปะราบรื่น" if cur_lord == "Venus"
           else "ความคิดและการค้าคล่องตัว" if cur_lord == "Mercury"
           else "ใจสงบ ครอบครัวอุ่น" if cur_lord == "Moon"
           else "ใช้เหตุผล ระวังสุขภาพ" if cur_lord == "Saturn"
           else "พลังเต็มเปี่ยม แต่ใจร้อน" if cur_lord == "Mars"
           else "ระวังการหลอกลวงและความคิดสับสน" if cur_lord == "Rahu"
           else "ภาวะผู้นำเด่นชัด")
    )
    result["interpretation"]["en"] = (
        f"Born on {WEEKDAY_TH[sunday0]} — Maha Taksa starts with {start_lord}. "
        f"At age {result['current']['age']:.1f} you run the {cur_lord} period "
        f"(sub-lord: {cur_sub['lord']}). Overall tone: {tone}."
    )
    return result


# ── เลขเจ้าสังวาลย์ (Thai name numerology) ──────────────────────────
_LETTER_VALUES = {}
def _build_letter_values() -> None:
    """Classical เจ้าสังวาลย์ letter values (มูลนิธิตารางมาตรฐาน)."""
    groups = [
        (["ก", "ข", "ค", "ง"], 1),
        (["จ", "ฉ", "ช", "ญ"], 2), (["ฎ", "ฏ", "ฐ", "ฑ", "ฒ", "ณ"], 3),
        (["ด", "ต", "ถ", "ท", "ธ", "น"], 5),
        (["บ", "ป", "ผ", "ฝ", "พ", "ฟ", "ภ"], 8),
        (["ม", "ย", "ร", "ล", "ว"], 9),
        (["ศ", "ษ", "ส", "ห", "ฮ"], 6), (["อ", "ะ"], 8),
    ]
    for letters, v in groups:
        for ch in letters:
            _LETTER_VALUES[ch] = v


_build_letter_values()


def chomangkala_number(name: str) -> dict:
    total = sum(_LETTER_VALUES.get(ch, 0) for ch in name)
    return {"name": name, "total": total}


def lucky_numbers(name: str, birthday_ddmm: str) -> dict:
    cm = chomangkala_number(name)
    digits = "".join(ch for ch in birthday_ddmm if ch.isdigit())
    day_digit = sum(int(d) for d in digits)
    while day_digit > 9:
        day_digit = sum(int(d) for d in str(day_digit))
    luck = (cm["total"] + day_digit) % 9 or 9
    meanings = {
        1: "ผู้นำ — ควรใช้เลข 1, 9 เสริมดวง",
        2: "เมตตา — เลข 2, 7 นำพาสุข",
        3: "สร้างสรรค์ — เลข 3, 5 หนุน",
        5: "เป็นที่รัก — เลข 5, 6 ช่วยเสริม",
        6: "ร่ำรวย — เลข 6, 8 เสริมทรัพย์",
        8: "มั่นคง — เลข 8, 4 ยึดเหนี่ยว",
        9: "เจริญก้าวหน้า — เลข 9, 1 ผลักดัน",
        4: "มั่นคงปลอดภัย — เลข 4, 8 หนุน",
        7: "โชคเข้าตัว — เลข 7, 2 ดี",
    }
    return {
        "system": "chomangkala-numerology",
        "name_total": cm["total"],
        "day_digit": day_digit,
        "luck_number": luck,
        "meaning": meanings.get(luck, ""),
        "interpretation": {
            "th": f"ชื่อ '{name}' ได้เลขเจ้าสังวาลย์รวม {cm['total']} "
                  f"เมื่อผสานกับวันเกิดได้เลขนำโชค **{luck}** — {meanings.get(luck, '')}",
            "en": f"Name value {cm['total']} combined with birth digit gives "
                  f"lucky number {luck}.",
        },
    }
