"""เลขเจ้าสังวาลย์ v2 — full classical letter tables + first/last-name split.

Sources: mahamongkol.com, sinsae.com (ตารางค่าตัวอักษรไทยมาตรฐาน).
Method: ค่ากำลังดาวของชื่อตัว → นามสกุล → ผลรวมหาดาวประจำตัว.
"""
from __future__ import annotations

# ── ตารางค่าอักษรไทย (กำลังดาว) — classical grouping ─────────────────
# แต่ละกลุ่มอักษรมีเลขประจำ; สระ/วรรณยุกต์บางตัวมีค่า
LETTER_VALUES: dict[str, int] = {}
for _ch in "กข":
    LETTER_VALUES[_ch] = 1
for _ch in "ฆง":
    LETTER_VALUES[_ch] = 3
for _ch in "คซ":
    LETTER_VALUES[_ch] = 6
for _ch in "ฌญ":
    LETTER_VALUES[_ch] = 7
for _ch in "จฉช":
    LETTER_VALUES[_ch] = 8
for _ch in "ซ":
    LETTER_VALUES[_ch] = 2
for _ch in "ฎฏฐฑฒณดตถทธน":
    LETTER_VALUES[_ch] = 1
for _ch in "บปผฝพฟภ":
    LETTER_VALUES[_ch] = 4
for _ch in "ม":
    LETTER_VALUES[_ch] = 5
for _ch in "ยรลว":
    LETTER_VALUES[_ch] = 9
for _ch in "ศษสหฬอฮ":
    LETTER_VALUES[_ch] = 0
for _ch in "ะาิีึืุูเแโใไ":
    LETTER_VALUES[_ch] = 8
for _ch in "ำ":
    LETTER_VALUES[_ch] = 3
for _ch in "่้๊๋":      # mai ek, tho, tri, chattawa
    LETTER_VALUES[_ch] = 1
for _ch in "็์":        # maitaikhu, thanthakhat
    LETTER_VALUES[_ch] = 0

# ดาวประจำเลข 1-9
_NUMBER_STAR = {
    1: ("ดวงอาทิตย์", "Sun", "ผู้นำ เกียรติยศ มีคนเกรงใจ"),
    2: ("ดวงจันทร์", "Moon", "อ่อนโยน เป็นที่รัก มีเสน่ห์"),
    3: ("ดาวพฤหัสฯ", "Jupiter", "โชคดี มีผู้ใหญ่หนุนนำ"),
    4: ("ราหู", "Rahu", "คิดเร็ว กล้าเสี่ยง ชีวิตพลิกผัน"),
    5: ("ดาวพุธ", "Mercury", "ฉลาด ปากเก่ง ค้าขายรวย"),
    6: ("ดาวศุกร์", "Venus", "เสน่ห์แรง ศิลปะ รักมั่นคง"),
    7: ("ดาวเสาร์", "Saturn", "อดทน ได้ดีเนือกหลัง"),
    8: ("ดาวอังคาร", "Mars", "ใจสู้ กล้าหาญ แต่ใจร้อน"),
    9: ("ดาวพฤหัสฯสูงสุด", "Jupiter+", "เจ้าปัญญา มีลาภยศ"),
}


def _digit_reduce(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def name_star_value(name: str) -> dict:
    """ค่ากำลังดาวของชื่อ (หรือนามสกุล)."""
    total = sum(LETTER_VALUES.get(ch, 0) for ch in name if not ch.isspace())
    digit = _digit_reduce(total)
    star_th, star_en, meaning = _NUMBER_STAR[digit]
    return {"text": name, "raw_total": total,
            "digit": digit, "star_th": star_th,
            "star_en": star_en, "meaning": meaning}


def chomangkala_full(first_name: str, last_name: str = "",
                     birth_day_of_month: int | None = None) -> dict:
    """Full v2 reading: first-name star + surname star + birth-day harmony."""
    fn = name_star_value(first_name)
    ln = name_star_value(last_name) if last_name else None

    combined_total = fn["digit"] + (ln["digit"] if ln else 0)
    final_digit = _digit_reduce(combined_total)

    harmony = None
    if birth_day_of_month:
        day_digit = _digit_reduce(birth_day_of_month)
        gap = abs(day_digit - final_digit)
        harmony = {
            "birth_digit": day_digit,
            "name_digit": final_digit,
            "gap": gap,
            "verdict_th": ("ชื่อกับวันเกิดกันดีนักหนา" if gap <= 2 else
                           "ชื่อกับวันเกิดค่อนข้างกัน — พอใช้ได้" if gap <= 5
                           else "ชื่อฝืนวันเกิดอยู่บ้าง อาจต้องใช้ชื่อเล่นเสริม"),
        }

    th_lines = [f"ชื่อ '{first_name}' ได้ดาว{fn['star_th']} — {fn['meaning']}"]
    if ln:
        th_lines.append(f"นามสกุล '{last_name}' ได้ดาว{ln['star_th']}")
    th_lines.append(f"รวมกันเป็นเลข {final_digit} "
                    f"({_NUMBER_STAR[final_digit][0]}): "
                    f"{_NUMBER_STAR[final_digit][2]}")
    if harmony:
        th_lines.append(harmony["verdict_th"])

    return {
        "system": "chomangkala-v2",
        "first_name": fn,
        "last_name": ln,
        "combined_digit": final_digit,
        "harmony_with_birth": harmony,
        "interpretation": {
            "th": "\n".join(th_lines),
            "en": (f"'{first_name}' → {fn['star_en']} ({fn['digit']}); "
                   f"combined number {final_digit}."),
        },
    }
