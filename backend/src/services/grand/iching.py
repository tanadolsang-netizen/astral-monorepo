"""I Ching daily oracle — engine spec C:/AI/research-astrology/12.

Primary casting = spec §2 sha256-seeded coin method:
``seed = sha256(f"{user_id}|{iso_date}|{question}|{salt}")`` with salt
"hermes-v1"; per-line weights old-yin 1 / young-yang 5 / young-yin 7 /
old-yang 3 of 16 — exactly the classic three-coin probabilities
P(6)=1/16 P(7)=5/16 P(8)=7/16 P(9)=3/16.

Secondary/cross-check when no seed exists: ``((day*month + year) mod 64)+1``
(King Wen number). Lookup = spec §1 Wilhelm KW[lower][upper].

Unit vector (QA note b): user_id="M", iso_date="1997-05-19", question="",
salt="hermes-v1" → vals [7,7,7,8,8,8], lines bottom-up [1,1,1,0,0,0],
primary #11 泰 Tài "Peace", zero changing lines (derived = primary),
nuclear #54 歸妹 Guī Mèi "The Marrying Maiden". Fallback for that date →
2092 mod 64 = 44 → #45 萃 Cuì "Gathering Together".

Text policy (QA note c): only fully-written hexagram entries carry
judgment/image text; anything else is flagged ``text_complete: false`` and
the module reports ``hexagram_text_missing:<n>`` — an unwritten entry is
never emitted as if complete.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

SALT_DEFAULT = "hermes-v1"

# Trigram images by bottom-up bit value (spec §1).
TRIGRAMS: dict[int, dict[str, str]] = {
    7: {"name": "Qian", "cn": "☰", "image_en": "Heaven", "element": "Metal"},
    3: {"name": "Dui", "cn": "☱", "image_en": "Lake", "element": "Metal"},
    5: {"name": "Li", "cn": "☲", "image_en": "Fire", "element": "Fire"},
    1: {"name": "Zhen", "cn": "☳", "image_en": "Thunder", "element": "Wood"},
    6: {"name": "Xun", "cn": "☴", "image_en": "Wind", "element": "Wood"},
    2: {"name": "Kan", "cn": "☵", "image_en": "Water", "element": "Water"},
    4: {"name": "Gen", "cn": "☶", "image_en": "Mountain", "element": "Earth"},
    0: {"name": "Kun", "cn": "☷", "image_en": "Earth", "element": "Earth"},
}

# King Wen table KW[(lower_bits, upper_bits)] — spec §1 Wilhelm layout,
# QA cross-checked (#11 Qian/Kun, #54 Dui/Zhen, #45 Kun/Dui all reproduce).
KW: dict[tuple[int, int], int] = {
    (7, 7): 1, (7, 3): 43, (7, 5): 14, (7, 1): 34, (7, 6): 9, (7, 2): 5, (7, 4): 26, (7, 0): 11,
    (3, 7): 10, (3, 3): 58, (3, 5): 38, (3, 1): 54, (3, 6): 61, (3, 2): 60, (3, 4): 41, (3, 0): 19,
    (5, 7): 13, (5, 3): 49, (5, 5): 30, (5, 1): 55, (5, 6): 37, (5, 2): 63, (5, 4): 22, (5, 0): 36,
    (1, 7): 25, (1, 3): 17, (1, 5): 21, (1, 1): 51, (1, 6): 42, (1, 2): 3, (1, 4): 27, (1, 0): 24,
    (6, 7): 44, (6, 3): 28, (6, 5): 50, (6, 1): 32, (6, 6): 57, (6, 2): 48, (6, 4): 18, (6, 0): 46,
    (2, 7): 6, (2, 3): 47, (2, 5): 64, (2, 1): 40, (2, 6): 59, (2, 2): 29, (2, 4): 4, (2, 0): 7,
    (4, 7): 33, (4, 3): 31, (4, 5): 56, (4, 1): 62, (4, 6): 53, (4, 2): 39, (4, 4): 52, (4, 0): 15,
    (0, 7): 12, (0, 3): 45, (0, 5): 35, (0, 1): 16, (0, 6): 20, (0, 2): 8, (0, 4): 23, (0, 0): 2,
}

# King Wen index facts (number → cn / pinyin / EN title / TH short title).
HEX_NAMES: dict[int, dict[str, str]] = {
    1: {"cn": "乾", "pinyin": "Qián", "en": "The Creative", "th": "ผู้สร้างสรรค์"},
    2: {"cn": "坤", "pinyin": "Kūn", "en": "The Receptive", "th": "ผู้รับ"},
    3: {"cn": "屯", "pinyin": "Zhūn", "en": "Difficulty at the Beginning", "th": "เริ่มต้นยากลำบาก"},
    4: {"cn": "蒙", "pinyin": "Méng", "en": "Youthful Folly", "th": "เยาว์วัยเรียนรู้"},
    5: {"cn": "需", "pinyin": "Xū", "en": "Waiting", "th": "การรอคอย"},
    6: {"cn": "訟", "pinyin": "Sòng", "en": "Conflict", "th": "ความขัดแย้ง"},
    7: {"cn": "師", "pinyin": "Shī", "en": "The Army", "th": "กองทัพ"},
    8: {"cn": "比", "pinyin": "Bǐ", "en": "Holding Together", "th": "การผูกพัน"},
    9: {"cn": "小畜", "pinyin": "Xiǎo Chù", "en": "The Taming Power of the Small", "th": "พลังประคับประคองเล็ก"},
    10: {"cn": "履", "pinyin": "Lǚ", "en": "Treading", "th": "การก้าวเดินอย่างระมัดระวัง"},
    11: {"cn": "泰", "pinyin": "Tài", "en": "Peace", "th": "ความสงบร่มเย็น"},
    12: {"cn": "否", "pinyin": "Pǐ", "en": "Standstill", "th": "ความหยุดชะงัก"},
    13: {"cn": "同人", "pinyin": "Tóng Rén", "en": "Fellowship with Men", "th": "ความสามัคคี"},
    14: {"cn": "大有", "pinyin": "Dà Yǒu", "en": "Great Possession", "th": "ทรัพย์ใหญ่"},
    15: {"cn": "謙", "pinyin": "Qiān", "en": "Modesty", "th": "ความถ่อมตน"},
    16: {"cn": "豫", "pinyin": "Yù", "en": "Enthusiasm", "th": "ความกระตือรือร้น"},
    17: {"cn": "隨", "pinyin": "Suí", "en": "Following", "th": "การตาม"},
    18: {"cn": "蠱", "pinyin": "Gǔ", "en": "Work on the Decayed", "th": "แก้ไขสิ่งที่เน่าเสีย"},
    19: {"cn": "臨", "pinyin": "Lín", "en": "Approach", "th": "การเข้าใกล้"},
    20: {"cn": "觀", "pinyin": "Guān", "en": "Contemplation", "th": "การพิจารณา"},
    21: {"cn": "噬嗑", "pinyin": "Shì Kè", "en": "Biting Through", "th": "การตัดสินขาด"},
    22: {"cn": "賁", "pinyin": "Bì", "en": "Grace", "th": "ความงดงาม"},
    23: {"cn": "剝", "pinyin": "Bō", "en": "Splitting Apart", "th": "การแตกร้าว"},
    24: {"cn": "復", "pinyin": "Fù", "en": "Return", "th": "การหวนคืน"},
    25: {"cn": "無妄", "pinyin": "Wú Wàng", "en": "Innocence", "th": "ความบริสุทธิ์"},
    26: {"cn": "大畜", "pinyin": "Dà Chù", "en": "The Taming Power of the Great", "th": "พลังควบคุมใหญ่"},
    27: {"cn": "頤", "pinyin": "Yí", "en": "Nourishment", "th": "การหล่อเลี้ยง"},
    28: {"cn": "大過", "pinyin": "Dà Guò", "en": "Preponderance of the Great", "th": "ภาระเกินกำลังใหญ่"},
    29: {"cn": "坎", "pinyin": "Kǎn", "en": "The Abysmal (Water)", "th": "เหวลึก (น้ำ)"},
    30: {"cn": "離", "pinyin": "Lí", "en": "The Clinging (Fire)", "th": "เปลวไฟ"},
    31: {"cn": "咸", "pinyin": "Xián", "en": "Influence", "th": "แรงดึงดูด"},
    32: {"cn": "恆", "pinyin": "Héng", "en": "Duration", "th": "ความยั่งยืน"},
    33: {"cn": "遯", "pinyin": "Dùn", "en": "Retreat", "th": "การถอย"},
    34: {"cn": "大壯", "pinyin": "Dà Zhuàng", "en": "Great Power", "th": "พลังใหญ่"},
    35: {"cn": "晉", "pinyin": "Jìn", "en": "Progress", "th": "ความก้าวหน้า"},
    36: {"cn": "明夷", "pinyin": "Míng Yí", "en": "Darkening of the Light", "th": "แสงสว่างมืดมน"},
    37: {"cn": "家人", "pinyin": "Jiā Rén", "en": "The Family", "th": "ครอบครัว"},
    38: {"cn": "睽", "pinyin": "Kuí", "en": "Opposition", "th": "ความขัดแย้งแยกทาง"},
    39: {"cn": "蹇", "pinyin": "Jiǎn", "en": "Obstruction", "th": "อุปสรรค"},
    40: {"cn": "解", "pinyin": "Xiè", "en": "Deliverance", "th": "การหลุดพ้น"},
    41: {"cn": "損", "pinyin": "Sǔn", "en": "Decrease", "th": "การลดลง"},
    42: {"cn": "益", "pinyin": "Yì", "en": "Increase", "th": "การเพิ่มพูน"},
    43: {"cn": "夬", "pinyin": "Guài", "en": "Breakthrough", "th": "การฝ่าฝัน"},
    44: {"cn": "姤", "pinyin": "Gòu", "en": "Coming to Meet", "th": "การประจันหน้า"},
    45: {"cn": "萃", "pinyin": "Cuì", "en": "Gathering Together", "th": "การรวมกัน"},
    46: {"cn": "升", "pinyin": "Shēng", "en": "Pushing Upward", "th": "การไต่ขึ้น"},
    47: {"cn": "困", "pinyin": "Kùn", "en": "Oppression", "th": "ความอัดอั้น"},
    48: {"cn": "井", "pinyin": "Jǐng", "en": "The Well", "th": "บ่อน้ำ"},
    49: {"cn": "革", "pinyin": "Gé", "en": "Revolution", "th": "การปฏิวัติ"},
    50: {"cn": "鼎", "pinyin": "Dǐng", "en": "The Cauldron", "th": "หม้อปรุงใหญ่"},
    51: {"cn": "震", "pinyin": "Zhèn", "en": "The Arousing (Thunder)", "th": "ฝนฟ้าคะนอง"},
    52: {"cn": "艮", "pinyin": "Gèn", "en": "Keeping Still (Mountain)", "th": "ภูเขานิ่ง"},
    53: {"cn": "漸", "pinyin": "Jiàn", "en": "Development", "th": "ความก้าวหน้าทีละขั้น"},
    54: {"cn": "歸妹", "pinyin": "Guī Mèi", "en": "The Marrying Maiden", "th": "หญิงสาวที่สมรส"},
    55: {"cn": "豐", "pinyin": "Fēng", "en": "Abundance", "th": "ความมั่งคั่ง"},
    56: {"cn": "旅", "pinyin": "Lǚ", "en": "The Wanderer", "th": "นักเดินทาง"},
    57: {"cn": "巽", "pinyin": "Xùn", "en": "The Gentle (Wind)", "th": "ลมอ่อนโยน"},
    58: {"cn": "兌", "pinyin": "Duì", "en": "The Joyous (Lake)", "th": "ทะเลสาบแห่งความรื่นเริง"},
    59: {"cn": "渙", "pinyin": "Huàn", "en": "Dispersion", "th": "การกระจาย"},
    60: {"cn": "節", "pinyin": "Jié", "en": "Limitation", "th": "การคุมจำกัด"},
    61: {"cn": "中孚", "pinyin": "Zhōng Fú", "en": "Inner Truth", "th": "ความจริงภายใน"},
    62: {"cn": "小過", "pinyin": "Xiǎo Guò", "en": "Preponderance of the Small", "th": "เกินกำลังเล็ก"},
    63: {"cn": "既濟", "pinyin": "Jì Jì", "en": "After Completion", "th": "หลังสำเร็จ"},
    64: {"cn": "未濟", "pinyin": "Wèi Jì", "en": "Before Completion", "th": "ก่อนสำเร็จ"},
}

# Fully-written entries (spec §3 anchors + QA ground-truth hexagrams).
# Anything absent is reported text-incomplete — never filled in from thin air.
HEX_TEXTS: dict[int, dict[str, str]] = {
    1: {
        "judgment_en": "The Creative works sublime success, furthering through perseverance.",
        "judgment_th": "ผู้สร้างสรรค์: สำเร็จสูงส่ง ยั่งยืนด้วยความเพียร",
        "image_en": "Heaven's movement: the superior person strengthens himself unceasingly.",
        "image_th": "ฟ้าหมุนเวียนไม่หยุด — ผู้ใหญ่ฝึกตนให้เข้มแข็งไม่ว่างเว้น",
        "source": "Wilhelm/Baynes (public domain), spec §3 anchor",
    },
    11: {
        "judgment_en": "Peace. The small departs, the great approaches. Good fortune, success.",
        "judgment_th": "สงบร่มเย็น: เล็กจากไป ใหญ่เข้ามา — เฮง สำเร็จ",
        "image_en": "Heaven and earth unite: the flow of abundance governs the people.",
        "image_th": "ฟ้ากับแผ่นดินสมานกัน — ความอุดมสมบูรณ์ไหลถึงผู้คน",
        "source": "Wilhelm/Baynes (public domain)",
    },
    24: {
        "judgment_en": "Return. Success. Going out and coming in without error. Friends come without blame.",
        "judgment_th": "การหวนคืน: สำเร็จ ออกและเข้าไม่ผิดพลาด มิตรกลับมาโดยไม่ต้องโทษ",
        "image_en": "Thunder in the earth: the light returns on winter-solstice rhythm.",
        "image_th": "สายฟ้าใต้พื้นดิน — แสงสว่างหวนคืนตามจังหวะครีษมายัน",
        "source": "Wilhelm/Baynes (public domain), spec §3 anchor",
    },
    31: {
        "judgment_en": "Influence. Success. Perseverance furthers. To take a maiden as a wife brings good fortune.",
        "judgment_th": "แรงดึงดูด: สำเร็จ · ความมั่นคงช่วยให้รุดหน้า · รับเธอมาเป็นคู่จึงเป็นมงคล",
        "image_en": "A lake on the mountain: the superior person encourages people to approach him by his readiness to receive them.",
        "image_th": "ทะเลสาบอยู่บนภูเขา — ผู้ใหญ่เปิดรับคนเข้าหาด้วยความพร้อมรับฟัง",
        "source": "spec §3 verbatim",
    },
    45: {
        "judgment_en": "Gathering Together. Success. Perseverance furthers. Bring great offerings — confidence serves.",
        "judgment_th": "การรวมกัน: สำเร็จ · มั่นคงช่วยให้รุดหน้า · จัดเครื่องสักการะใหญ่ ความเชื่อมั่นเป็นศรี",
        "image_en": "The lake over the earth: the superior person renews his weapons to meet the unforeseen.",
        "image_th": "ทะเลสาบเหนือแผ่นดิน — ผู้ใหญ่เตรียมพร้อมรับสิ่งคาดไม่ถึง",
        "source": "Wilhelm/Baynes (public domain), QA ground-truth entry",
    },
    50: {
        "judgment_en": "The Cauldron. Supreme good fortune. Success. Nourishment and refinement of the talented.",
        "judgment_th": "หม้อปรุงใหญ่: มงคลสูงสุด สำเร็จ — หล่อเลี้ยงและหล่อหลอมคนเก่ง",
        "image_en": "Fire over wood: the superior person positions his calling true.",
        "image_th": "ไฟบนไม้ — ผู้ใหญ่วางภารกิจของตนให้ถูกทิศ",
        "source": "Wilhelm/Baynes (public domain), spec §3 anchor",
    },
    54: {
        "judgment_en": "The Marrying Maiden. Undertakings bring misfortune. Nothing that would further.",
        "judgment_th": "หญิงสาวที่สมรส: กิจการใหญ่พาเสียหาย ไม่มีอะไรที่รุดหน้า — ตำแหน่งไม่ชอบธรรม",
        "image_en": "Thunder over the lake: the inferior endures, the superior must know the position is not equal.",
        "image_th": "สายฟ้าเหนือทะเลสาบ — รู้ตำแหน่งของตน อย่าฝืนยืมเกินฐานะ",
        "source": "Wilhelm/Baynes (public domain), QA nuclear-of-test-vector entry",
    },
}


def _bits(trigram_lines: list[int]) -> int:
    """Bottom-up lines → trigram bit value (bottom line = LSB)."""
    return sum(bit << i for i, bit in enumerate(trigram_lines))


def _cast(user_id: str, iso_date: str, question: str, salt: str) -> tuple[list[int], list[int], list[int]]:
    """Spec §2 seeded coin cast. Returns (line_values, lines, changing)."""
    digest = hashlib.sha256(f"{user_id}|{iso_date}|{question}|{salt}".encode()).digest()
    vals: list[int] = []
    for i in range(6):
        r = digest[i] / 255 * 16
        vals.append(6 if r < 1 else 7 if r < 6 else 8 if r < 13 else 9)
    lines = [1 if v in (7, 9) else 0 for v in vals]
    changing = [i for i, v in enumerate(vals) if v in (6, 9)]
    return vals, lines, changing


def hexagram_from_lines(lines: list[int]) -> int:
    lower, upper = _bits(lines[0:3]), _bits(lines[3:6])
    return KW[(lower, upper)]


def nuclear_hexagram_from_lines(lines: list[int]) -> int:
    """Nuclear hexagram (spec §2): new_lower = lines[1:4], new_upper = lines[2:5]."""
    return hexagram_from_lines(lines[1:4] + lines[2:5])


def date_fallback_number(year: int, month: int, day: int) -> int:
    """Secondary formula (QA note a): ((day*month + year) mod 64) + 1."""
    return ((day * month + year) % 64) + 1


def _hex_entry(number: int, role: str) -> dict:
    names = HEX_NAMES.get(number, {})
    text = HEX_TEXTS.get(number)
    entry: dict = {
        "role": role,
        "king_wen": number,
        "cn": names.get("cn"),
        "pinyin": names.get("pinyin"),
        "en": names.get("en"),
        "th": names.get("th"),
        "text_complete": text is not None,
    }
    if text:
        entry.update({
            "judgment_en": text["judgment_en"],
            "judgment_th": text["judgment_th"],
            "image_en": text["image_en"],
            "image_th": text["image_th"],
            "text_source": text["source"],
        })
    return entry


def compute_iching(
    user_id: str | None = None,
    iso_date: str | None = None,
    question: str = "",
    salt: str = SALT_DEFAULT,
) -> dict:
    """Seeded deterministic cast (primary) + date-fallback cross-check."""
    if not user_id or not iso_date:
        return {"status": "unavailable", "reason": "missing_seed_input"}

    vals, lines, changing = _cast(str(user_id), str(iso_date), str(question or ""), str(salt))
    primary_num = hexagram_from_lines(lines)

    derived_entry: dict | None = None
    if changing:
        derived_lines = [
            bit ^ 1 if idx in changing else bit for idx, bit in enumerate(lines)
        ]
        derived_entry = _hex_entry(hexagram_from_lines(derived_lines), "derived")

    nuclear_num = nuclear_hexagram_from_lines(lines)
    fb_y, fb_m, fb_d = str(iso_date)[:10].split("-")
    fb_num = date_fallback_number(int(fb_y), int(fb_m), int(fb_d))

    missing_texts = [
        f"hexagram_text_missing:{n}"
        for n in sorted({primary_num, fb_num, nuclear_num}
                        | ({derived_entry["king_wen"]} if derived_entry else set()))
        if n not in HEX_TEXTS
    ]
    primary = _hex_entry(primary_num, "primary")
    status = "ok" if primary["text_complete"] else "unavailable"

    payload: dict = {
        "status": status,
        "method": "seeded_cast_coin_distribution",
        "seed_input": f"{user_id}|{iso_date}|{question or ''}|{salt}",
        "line_values_bottom_up": vals,
        "lines_bottom_up": lines,
        "changing_line_indexes": changing,
        "lower_trigram": TRIGRAMS[_bits(lines[0:3])],
        "upper_trigram": TRIGRAMS[_bits(lines[3:6])],
        "primary": primary,
        "derived": derived_entry,
        "nuclear": _hex_entry(nuclear_num, "nuclear"),
        "cross_check_fallback": {
            "formula": "((day*month + year) mod 64) + 1",
            "king_wen": fb_num,
            **{k: v for k, v in _hex_entry(fb_num, "date_fallback").items() if k != "role"},
        },
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
    if missing_texts:
        payload["text_warnings"] = missing_texts
        if not primary["text_complete"]:
            payload["reason"] = f"hexagram_text_missing:{primary_num}"
    return payload
