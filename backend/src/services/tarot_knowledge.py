"""Comprehensive Tarot Knowledge Base — narrative Thai only.

Covers ALL 78 cards plus:
  • Yes/No/Maybe classification (upright & reversed)
  • Timing system (suit = speed, number = quantity)
  • Spread definitions (single, 3-card, celtic-cross, 7-card agenda, etc.)
  • Court Cards ↔ Zodiac mapping
  • Element/dominant analysis rules
  • Combination reading principles
  • Reversed card meaning patterns

Pure Thai narrative. No EN/CJK fragments.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════
# 1. YES / NO / MAYBE — ระบบตอบคำถามทั้ง 78 ใบ
# ═══════════════════════════════════════════════════════════════════════════
#  ✅ = Yes  ❌ = No  ⚖️ = Maybe / ขึ้นอยู่กับบริบท
#  🔄 = กลับหัว (reversed) เปลี่ยนผลลัพธ์

YES_NO: dict[str, dict[str, str]] = {
    # ── Major Arcana ──
    "The Fool":             {"upright": "yes",   "reversed": "no",   "note": "ก้าวใหม่ได้ แต่ถ้าลังเลก็อย่า"},
    "The Magician":         {"upright": "yes",   "reversed": "no",   "note": "พร้อมแล้ว ยกเว้นจะหลอกลวง"},
    "The High Priestess":   {"upright": "no",    "reversed": "maybe", "note": "ยังไม่ถึงเวลา ต้องรอ"},
    "The Empress":          {"upright": "yes",   "reversed": "maybe", "note": "อุดมสมบูรณ์ ยกเว้นต้องดูแลตัวเอง"},
    "The Emperor":          {"upright": "yes",   "reversed": "no",   "note": "มั่นคง ยกเว้นเผด็จการ"},
    "The Hierophant":       {"upright": "yes",   "reversed": "maybe", "note": "ประเพณี ยกเว้นต้องทลายกรอบ"},
    "The Lovers":           {"upright": "yes",   "reversed": "no",   "note": "เลือกได้ ยกเว้นเลือกผิด"},
    "The Chariot":          {"upright": "yes",   "reversed": "no",   "note": "มุ่งหน้าได้ ยกเว้นควบคุมไม่ได้"},
    "Strength":             {"upright": "yes",   "reversed": "no",   "note": "อ่อนโยนคือพลัง ยกเว้นอ่อนแอ"},
    "The Hermit":           {"upright": "no",    "reversed": "maybe", "note": "ถอยกลับ ยกเว้นโดดเดี่ยว"},
    "Wheel of Fortune":     {"upright": "yes",   "reversed": "no",   "note": "โชคเข้าทาง ยกเว้นโชคร้าย"},
    "Justice":              {"upright": "yes",   "reversed": "no",   "note": "ยุติธรรม ยกเว้นอยุติธรรม"},
    "The Hanged Man":       {"upright": "maybe", "reversed": "no",   "note": "หยุดชะงัก ยกเว้นทิ้งเวลา"},
    "Death":                {"upright": "no",    "reversed": "no",   "note": "จบสิ้น — ไม่ใช่คำตอบที่ต้องการ"},
    "Temperance":           {"upright": "yes",   "reversed": "no",   "note": "ช้าแต่ชัด ยกเว้นไม่สมดุล"},
    "The Devil":            {"upright": "no",    "reversed": "yes",  "note": "ผูกมัด ยกเว้นหลุดพ้น"},
    "The Tower":            {"upright": "no",    "reversed": "maybe", "note": "พังทลาย ยกเว้นหนีเปลี่ยน"},
    "The Star":             {"upright": "yes",   "reversed": "maybe", "note": "ความหวัง ยกเว้นหมดหวัง"},
    "The Moon":             {"upright": "no",    "reversed": "yes",  "note": "ลวงหลอก ยกเว้นคลายตัว"},
    "The Sun":              {"upright": "yes",   "reversed": "maybe", "note": "รุ่งโรจน์ ยกเว้นมืดมัว"},
    "Judgement":            {"upright": "yes",   "reversed": "no",   "note": "ตื่นรู้ ยกเว้นหลับใหล"},
    "The World":            {"upright": "yes",   "reversed": "maybe", "note": "สมบูรณ์ ยกเว้นไม่เสร็จ"},

    # ── Wands (ไฟ) — ส่วนใหญ่ Yes ──
    "Ace of Wands":         {"upright": "yes",   "reversed": "no",   "note": "จุดเริ่มต้นใหม่"},
    "Two of Wands":         {"upright": "maybe", "reversed": "no",   "note": "วางแผนอยู่"},
    "Three of Wands":       {"upright": "yes",   "reversed": "maybe", "note": "ขยายออก"},
    "Four of Wands":        {"upright": "yes",   "reversed": "maybe", "note": "เฉลิมฉลอง"},
    "Five of Wands":        {"upright": "maybe", "reversed": "yes",  "note": "แข่งขัน"},
    "Six of Wands":         {"upright": "yes",   "reversed": "maybe", "note": "ชัยชนะ"},
    "Seven of Wands":       {"upright": "maybe", "reversed": "no",   "note": "ปกป้อง"},
    "Eight of Wands":       {"upright": "yes",   "reversed": "no",   "note": "เร็วว่องไว"},
    "Nine of Wands":        {"upright": "maybe", "reversed": "no",   "note": "เกือบจบ"},
    "Ten of Wands":         {"upright": "no",    "reversed": "yes",  "note": "หนักเกิน"},
    "Page of Wands":        {"upright": "yes",   "reversed": "no",   "note": "ข่าวดี"},
    "Knight of Wands":      {"upright": "yes",   "reversed": "no",   "note": "พุ่งไป"},
    "Queen of Wands":       {"upright": "yes",   "reversed": "no",   "note": "เสน่ห์"},
    "King of Wands":        {"upright": "yes",   "reversed": "no",   "note": "ผู้นำ"},

    # ── Cups (น้ำ) — ส่วนใหญ่ Yes ──
    "Ace of Cups":          {"upright": "yes",   "reversed": "no",   "note": "รักใหม่"},
    "Two of Cups":          {"upright": "yes",   "reversed": "no",   "note": "คู่ครอง"},
    "Three of Cups":        {"upright": "yes",   "reversed": "maybe", "note": "เฉลิมฉลอง"},
    "Four of Cups":         {"upright": "maybe", "reversed": "yes",  "note": "เบื่อหน่าย"},
    "Five of Cups":         {"upright": "no",    "reversed": "yes",  "note": "สูญเสีย"},
    "Six of Cups":          {"upright": "maybe", "reversed": "no",   "note": "อดีต"},
    "Seven of Cups":        {"upright": "no",    "reversed": "yes",  "note": "ภาพลวง"},
    "Eight of Cups":        {"upright": "maybe", "reversed": "no",   "note": "จากไป"},
    "Nine of Cups":         {"upright": "yes",   "reversed": "maybe", "note": "สุขใจ"},
    "Ten of Cups":          {"upright": "yes",   "reversed": "maybe", "note": "ครอบครัว"},
    "Page of Cups":         {"upright": "yes",   "reversed": "no",   "note": "ข่าวจากใจ"},
    "Knight of Cups":       {"upright": "yes",   "reversed": "no",   "note": "สารแห่งรัก"},
    "Queen of Cups":        {"upright": "yes",   "reversed": "no",   "note": "อ่อนโยน"},
    "King of Cups":         {"upright": "yes",   "reversed": "no",   "note": "ควบคุมอารมณ์"},

    # ── Swords (ลม) — ส่วนใหญ่ No ──
    "Ace of Swords":        {"upright": "yes",   "reversed": "no",   "note": "ความจริงชัด"},
    "Two of Swords":        {"upright": "maybe", "reversed": "yes",  "note": "ลำบากใจ"},
    "Three of Swords":      {"upright": "no",    "reversed": "yes",  "note": "เจ็บปวด"},
    "Four of Swords":       {"upright": "maybe", "reversed": "yes",  "note": "พักผ่อน"},
    "Five of Swords":       {"upright": "no",    "reversed": "yes",  "note": "ชนะแต่เสีย"},
    "Six of Swords":        {"upright": "yes",   "reversed": "no",   "note": "ผ่านพ้น"},
    "Seven of Swords":      {"upright": "no",    "reversed": "maybe", "note": "โกงหลอก"},
    "Eight of Swords":      {"upright": "no",    "reversed": "yes",  "note": "ผูกมัด"},
    "Nine of Swords":       {"upright": "no",    "reversed": "yes",  "note": "วิตกกังวล"},
    "Ten of Swords":        {"upright": "no",    "reversed": "maybe", "note": "จบเลวร้าย"},
    "Page of Swords":       {"upright": "maybe", "reversed": "no",   "note": "ข่าวเฉียบ"},
    "Knight of Swords":     {"upright": "yes",   "reversed": "no",   "note": "พุ่งเฉียบ"},
    "Queen of Swords":      {"upright": "yes",   "reversed": "no",   "note": "ชัดเจน"},
    "King of Swords":       {"upright": "yes",   "reversed": "no",   "note": "ยุติธรรม"},

    # ── Pentacles (ดิน) — ปานกลาง ──
    "Ace of Pentacles":     {"upright": "yes",   "reversed": "no",   "note": "โอกาสใหม่"},
    "Two of Pentacles":     {"upright": "maybe", "reversed": "no",   "note": "ปรับสมดุล"},
    "Three of Pentacles":   {"upright": "yes",   "reversed": "no",   "note": "ทำงานร่วม"},
    "Four of Pentacles":    {"upright": "maybe", "reversed": "yes",  "note": "กั๊กตัว"},
    "Five of Pentacles":    {"upright": "no",    "reversed": "yes",  "note": "ขาดแคลน"},
    "Six of Pentacles":     {"upright": "yes",   "reversed": "no",   "note": "ให้รับ"},
    "Seven of Pentacles":   {"upright": "maybe", "reversed": "no",   "note": "รอเก็บ"},
    "Eight of Pentacles":   {"upright": "yes",   "reversed": "no",   "note": "ฝึกฝน"},
    "Nine of Pentacles":    {"upright": "yes",   "reversed": "maybe", "note": "สำเร็จ"},
    "Ten of Pentacles":     {"upright": "yes",   "reversed": "maybe", "note": "มรดก"},
    "Page of Pentacles":    {"upright": "yes",   "reversed": "no",   "note": "เรียนรู้"},
    "Knight of Pentacles":  {"upright": "yes",   "reversed": "no",   "note": "ช้าแต่มั่น"},
    "Queen of Pentacles":   {"upright": "yes",   "reversed": "no",   "note": "ดูแล"},
    "King of Pentacles":    {"upright": "yes",   "reversed": "no",   "note": "มั่งคั่ง"},
}


def yes_no_answer(card_name: str, orientation: str = "upright") -> dict:
    """Return yes/no/maybe for a card with narrative explanation."""
    entry = YES_NO.get(card_name)
    if not entry:
        return {"answer": "maybe", "th": "ไม่มีข้อมูล — ให้ดูความหมายหลักประกอบ"}
    key = "reversed" if orientation == "reversed" else "upright"
    answer = entry.get(key, "maybe")
    th_answer = {"yes": "ใช่", "no": "ไม่ใช่", "maybe": "ยังไม่แน่ / ขึ้นอยู่กับบริบท"}.get(answer, "ยังไม่แน่")
    return {
        "answer": answer,
        "th": th_answer,
        "note": entry.get("note", ""),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. TIMING SYSTEM — ระบบทำนายเวลา (suit = ความเร็ว, number = ปริมาณ)
# ═══════════════════════════════════════════════════════════════════════════

SUIT_SPEED: dict[str, dict] = {
    "Wands": {
        "element": "ไฟ",
        "speed": "เร็ว",
        "unit": "สัปดาห์",
        "narrative": "ธาตูไฟคือเปลวเพลิงที่ลุกโชน เรื่องนี้จะเกิดขึ้นภายในไม่กี่สัปดาห์ เพราะพลังงานไฟคือการเคลื่อนที่ ความกระตือรือร้น และการขับเคลื่อนอย่างรวดเร็ว",
    },
    "Cups": {
        "element": "น้ำ",
        "speed": "ปานกลาง",
        "unit": "เดือน",
        "narrative": "ธาตูน้ำไหลรินอย่างช้าๆ เรื่องนี้ต้องการเวลาหลายเดือน เพราะพลังงานน้ำคืออารมณ์ ความรู้สึก และการเปลี่ยนแปลงที่ต้องค่อยๆ ไหลซึมซับเข้าไปในดิน",
    },
    "Swords": {
        "element": "ลม",
        "speed": "เร็วสุด",
        "unit": "วัน",
        "narrative": "ธาตูลมพัดผ่านอย่างรวดเร็ว เรื่องนี้จะเกิดขึ้นภายไม่กี่วัน เพราะพลังงานลมคือความคิด การสื่อสาร และเหตุการณ์ที่เปลี่ยนแปลงอย่างกะทันหัน",
    },
    "Pentacles": {
        "element": "ดิน",
        "speed": "ช้าสุด",
        "unit": "ปี",
        "narrative": "ธาตูดินทนทานและช้า เรื่องนี้อาจใช้เวลาหลายปี เพราะพลังงานดินคือสิ่งที่ตั้งถาวร การสั่งสม และผลที่ต้องใช้เวลาบ่มเพาะจนสุกงอม",
    },
}

NUMBER_QUANTITY: dict[str, str] = {
    "Ace":    "หนึ่งครั้ง — จุดเริ่มต้นใหม่ที่เป็นครั้งแรก",
    "Two":    "สองครั้ง — หรือสองเดือน/สองสัปดาห์ ขึ้นอยู่กับธาตู",
    "Three":  "สามครั้ง — หรือสามหน่วยเวลาของธาตูนั้น",
    "Four":   "สี่ครั้ง — หรือสี่หน่วยเวลา",
    "Five":   "ห้าครั้ง — หรือห้าหน่วยเวลา",
    "Six":    "หกครั้ง — หรือหกหน่วยเวลา",
    "Seven":  "เจ็ดครั้ง — หรือเจ็ดหน่วยเวลา",
    "Eight":  "แปดครั้ง — หรือแปดหน่วยเวลา",
    "Nine":   "เก้าครั้ง — หรือเก้าหน่วยเวลา",
    "Ten":    "สิบครั้ง — หรือสิบหน่วยเวลา หรือจุดจบของวงจร",
    "Page":   "เริ่มต้น — ยังไม่ชัดเจน ต้องรอดู",
    "Knight": "เคลื่อนที่ — เร็วกว่าปกติ ขึ้นอยู่กับธาตู",
    "Queen":  "เติบโต — ปานกลาง ต้องใช้เวลาทำความเข้าใจ",
    "King":   "สมบูรณ์ — ช้าแต่มั่นคง ผลที่ได้มีความยั่งยืน",
}


def timing_for_card(card_name: str) -> dict:
    """Return timing prediction for a Minor Arcana card."""
    parts = card_name.split(" of ")
    if len(parts) != 2:
        return {"unit": "ไม่ชัด", "narrative": "ไพ่ใหญ่ไม่มีเวลาที่แน่นอน — โชคชะตาเป็นผู้กำหนด"}
    rank, suit = parts[0], parts[1]
    speed_info = SUIT_SPEED.get(suit, {})
    quantity = NUMBER_QUANTITY.get(rank, "")
    unit = speed_info.get("unit", "ไม่ชัด")
    element = speed_info.get("element", "")
    speed_desc = speed_info.get("speed", "")
    speed_narrative = speed_info.get("narrative", "")

    return {
        "rank": rank,
        "suit": suit,
        "element": element,
        "speed": speed_desc,
        "unit": unit,
        "quantity": quantity,
        "narrative": f"{speed_narrative} ตัวเลข {rank} บอกว่า {quantity}",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. SPREADS — สเปรดทั้งหมด
# ═══════════════════════════════════════════════════════════════════════════

SPREADS: dict[str, dict] = {
    "single": {
        "name": "ไพ่เดียว",
        "size": 1,
        "positions": ["คำตอบ"],
        "narrative": "หยิบใบเดียวเพื่อตอบคำถามง่ายๆ หรือดูพลังงานประจำวัน เหมาะสำหรับคำถามที่ต้องการคำตอบรวดเร็ว",
    },
    "three_card": {
        "name": "สามใบ — อดีต/ปัจจุบัน/อนาคต",
        "size": 3,
        "positions": ["อดีต", "ปัจจุบัน", "อนาคต"],
        "narrative": "สเปรดคลาสสิกที่ครอบคลุมทุกมิติของเวลา ใบแรกบอกอดีตที่นำมา ใบกลางบอกสถานการณ์ปัจจุบัน ใบสุดท้ายบอกแนวโน้มอนาคต",
    },
    "past_present_future": {
        "name": "สามใบ — อดีต/ปัจจุบัน/อนาคต",
        "size": 3,
        "positions": ["อดีต", "ปัจจุบัน", "อนาคต"],
        "narrative": "เหมือน three_card แต่เน้นการเชื่อมโยงเหตุผลระหว่างช่วงเวลา ดูว่าอดีตส่งผลต่อปัจจุบันอย่างไร และปัจจุบันกำลังพาไปหาอนาคตแบบไหน",
    },
    "celtic_cross": {
        "name": "เซลติกครอส — สิบใบ",
        "size": 10,
        "positions": [
            "สถานการณ์ปัจจุบัน",
            "อุปสรรคที่ขวาง",
            "รากฐานที่ซ่อนอยู่",
            "อดีตที่ผ่านมา",
            "สิ่งที่เป็นไปได้",
            "อนาคตใกล้",
            "ตัวตนของผู้ถาม",
            "สิ่งรอบข้างที่มีผล",
            "ความหวังหรือความกลัว",
            "ผลลัพธ์สุดท้าย",
        ],
        "narrative": "สเปรดคลาสสิกที่ครอบคลุมทุกมิติของคำถาม ตั้งแต่รากฐาน อุปสรรค ความหวัง ไปจนถึงผลลัพธ์ เหมาะสำหรับคำถามที่ซับซ้อนหรือต้องการมองภาพรวม",
    },
    "love": {
        "name": "สามใบ — ความรัก",
        "size": 3,
        "positions": ["คุณ", "คู่ของคุณ", "ความสัมพันธ์"],
        "narrative": "สเปรดความรักที่ดูทั้งสองฝ่ายและพลังงานร่วม ใบแรกคือตัวคุณ ใบสองคืออีกฝ่าย ใบสามคือสิ่งที่เกิดขึ้นระหว่างกัน",
    },
    "relationship": {
        "name": "สามใบ — สัมพันธภาพ",
        "size": 3,
        "positions": ["คุณ", "เขา", "แนวโน้ม"],
        "narrative": "คลายความสัมพันธ์ว่าเป็นอย่างไร ใบแรกคือคุณในความสัมพันธ์นี้ ใบสองคือเขา ใบสามคือทิศทางที่กำลังจะเกิด",
    },
    "agenda": {
        "name": "เจ็ดใบ — สิ่งที่เขาอยากให้คุณรู้",
        "size": 7,
        "positions": [
            "สถานการณ์ที่เชื่อมคุณกับอีกฝ่าย",
            "สิ่งที่เขาอยากให้คุณเห็น",
            "สิ่งที่เขาอยากได้จริงๆ",
            "สิ่งที่เขาไม่พูดออกมา",
            "กลยุทธ์ที่เขาใช้",
            "ผลที่เขาหวังไว้",
            "ผลจริงที่จะเกิดขึ้น",
        ],
        "narrative": "สเปรดเจ็ดใบที่เปิดเผยแรงจูงใจที่ซ่อนอยู่ของอีกฝ่าย ทั้งสิ่งที่เขาแสดงออก สิ่งที่เขาปิดบัง และสิ่งที่เขาหวังว่าจะเกิด เหมาะสำหรับคำถามเรื่องความรักหรือความสัมพันธ์ที่ซับซ้อน",
    },
    "shadow": {
        "name": "สามใบ — เงามืด",
        "size": 3,
        "positions": ["สิ่งที่คุณซ่อน", "สิ่งที่ผู้อื่นเห็น", "สิ่งที่ต้องเผชิญ"],
        "narrative": "สเปรดที่มองเข้าไปในจิตใต้สำนึก ใบแรกคือสิ่งที่คุณปิดบังตัวเอง ใบสองคือสิ่งที่คนรอบข้างรับรู้ ใบสามคือสิ่งที่ต้องยอมรับและเผชิญ",
    },
    "chosen": {
        "name": "สามใบ — ทางเลือก",
        "size": 3,
        "positions": ["ทางเลือกที่หนึ่ง", "ทางเลือกที่สอง", "คำแนะนำ"],
        "narrative": "สเปรดสำหรับเปรียบเทียบสองทางเลือก ใบแรกกับสองคือพลังงานของแต่ละทาง ใบสามคือคำแนะนำว่าควรไปทางไหน",
    },
}


def get_spread(name: str) -> dict | None:
    """Return spread definition by key."""
    return SPREADS.get(name)


def list_spreads() -> list[dict]:
    """Return all available spreads."""
    return [{"key": k, **v} for k, v in SPREADS.items()]


# ═══════════════════════════════════════════════════════════════════════════
# 4. COURT CARDS ↔ ZODIAC — ไพ่ผู้คุมกับราศี
# ═══════════════════════════════════════════════════════════════════════════

COURT_ZODIAC: dict[str, dict] = {
    "Page of Wands": {
        "zodiac": "ธนุ / สิงห์ / เมษ",
        "element": "ไฟ",
        "role": "เด็กธาตูไฟ",
        "narrative": "พลังงานเริ่มต้นของธาตูไฟ เหมือนเด็กที่เพิ่งค้นพบโลก อยากรู้อยากเห็น สร้างสรรค์ และพร้อมจะลองผิดลองถูก เป็นนักเรียน ผู้ก่อตั้ง หรือคนที่เพิ่มเริ่มต้นโครงการใหม่",
    },
    "Knight of Wands": {
        "zodiac": "ธนุ",
        "element": "ไฟ",
        "role": "อัศวินไฟ",
        "narrative": "พุ่งไปข้างหน้าอย่างร้อนแรง หุนหันพลันแล่น กล้าเสี่ยง แต่บางทีก็ขาดความรอบคอบ เป็นนักสู้ ผู้บุกเบิก หรือคนที่ทำอะไรเร็วและฮึกเหิม",
    },
    "Queen of Wands": {
        "zodiac": "เมษ",
        "element": "ไฟ",
        "role": "ราชินีไฟ",
        "narrative": "แข็งแกร่ง มั่นคง อิสระ และเปล่งประกาย เป็นผู้หญิงที่รู้จักดูแลตัวเอง มีเสน่ห์ และไม่กลัวที่จะยืนเด่น เป็นผู้นำ นักธุรกิจ หรือแม่ที่เข้มแข็ง",
    },
    "King of Wands": {
        "zodiac": "สิงห์",
        "element": "ไฟ",
        "role": "ราชาไฟ",
        "narrative": "ผู้นำที่มองการณ์ไกล กล้าตัดสินใจ และขับเคลื่อนผู้อื่นด้วยวิสัยทัศน์ เปอร์โซน่าสิงห์ที่เต็มไปด้วยความมั่นใจ เป็นผู้บริหาร ผู้ก่อตั้ง หรือบิดาที่มีวิสัยทัศน์",
    },
    "Page of Cups": {
        "zodiac": "มีน / กรกฎ / พิจิก",
        "element": "น้ำ",
        "role": "เด็กธาตูน้ำ",
        "narrative": "พลังงานเริ่มต้นของธาตูน้ำ เหมือนเด็กที่เพิ่มเปิดใจรับความรู้สึก ฝัน จินตนาการ และศิลปะ เป็นศิลปิน นักเขียน หรือคนที่เพิ่มเริ่มต้นความสัมพันธ์",
    },
    "Knight of Cups": {
        "zodiac": "มีน",
        "element": "น้ำ",
        "role": "อัศวินน้ำ",
        "narrative": "ผู้ส่งสารแห่งความรัก นำเสนอความฝันและความรู้สึกอย่างงดงาม แต่บางทีก็เป็นภาพลวงตา เป็นคนรัก ผู้ชักชวน หรือคนที่พร้อมจะไปกับคุณที่ไหน",
    },
    "Queen of Cups": {
        "zodiac": "กรกฎ",
        "element": "น้ำ",
        "role": "ราชินีน้ำ",
        "narrative": "อ่อนโยน เห็นใจ และเข้าอกเข้าใจผู้อื่นอย่างลึกซึ้ง เป็นผู้หญิงที่รับฟังได้ดี มีเมตตา และเชื่อมโยงกับความรู้สึกได้ทั้งของตัวเองและผู้อื่น",
    },
    "King of Cups": {
        "zodiac": "พิจิก",
        "element": "น้ำ",
        "role": "ราชาน้ำ",
        "narrative": "ควบคุมอารมณ์ด้วยปัญญา รักษาสมดุลระหว่างหัวใจและเหตุผล เป็นผู้ชายที่ลึกซึ้งแต่ไม่ถูกความรู้สึกกลืนกิน เปี่ยมด้วยความเมตตาและความเข้าใจ",
    },
    "Page of Swords": {
        "zodiac": "มิถุน / ตุลย์ / กุมภ์",
        "element": "ลม",
        "role": "เด็กธาตูลม",
        "narrative": "พลังงานเริ่มต้นของธาตูลม เหมือนเด็กที่อยากรู้อยากเห็นทุกอย่าง ชอบตั้งคำถาม ค้นคว้า และถ่ายทอดความรู้ เป็นนักเรียน นักข่าว หรือผู้สื่อสาร",
    },
    "Knight of Swords": {
        "zodiac": "มิถุน",
        "element": "ลม",
        "role": "อัศวินลม",
        "narrative": "พุ่งไปข้างหน้าด้วยความคิดเฉียบขาด เร็ว ก้าวร้าว และพูดตรงๆ ไม่มีกั๊ก เป็นทหาร ทนาย หรือคนที่ใช้คำพูดเป็นอาวุธ",
    },
    "Queen of Swords": {
        "zodiac": "ตุลย์",
        "element": "ลม",
        "role": "ราชินีลม",
        "narrative": "มองโลกด้วยความชัดเจนและตรงไปตรงมา เด็ดขาดในคำพูด ไม่หลอกตัวเอง เป็นผู้หญิงที่เฉลียวฉลาด เป็นกันเอง และไม่กลัวที่จะพูดความจริง",
    },
    "King of Swords": {
        "zodiac": "กุมภ์",
        "element": "ลม",
        "role": "ราชาลม",
        "narrative": "ตัดสินใจด้วยเหตุผลอันแยบคม เป็นผู้นำที่ใช้ความยุติธรรมและปัญญานำทาง เป็นผู้พิพากษา อาจารย์ หรือผู้ที่ใช้กฎหมายและตรรกะเป็นเครื่องมือ",
    },
    "Page of Pentacles": {
        "zodiac": "กันย์ / มังกร / พฤษ",
        "element": "ดิน",
        "role": "เด็กธาตูดิน",
        "narrative": "พลังงานเริ่มต้นของธาตูดิน เหมือนเด็กที่เพิ่มเริ่มเรียนรู้เรื่องเงิน งาน และความมั่นคง เป็นนักเรียน ผู้ฝึกงาน หรือคนที่เพิ่มเริ่มต้นอาชีพ",
    },
    "Knight of Pentacles": {
        "zodiac": "กันย์",
        "element": "ดิน",
        "role": "อัศวินดิน",
        "narrative": "มุ่งมั่นค่อยเป็นค่อยไป ช้าแต่ชัด แม้ทางจะนิ่งแต่มั่นคงเหมือนภูเขา เป็นคนที่เชื่อถือได้ รักษาสัญญา และทำงานอย่างสม่ำเสมอ",
    },
    "Queen of Pentacles": {
        "zodiac": "มังกร",
        "element": "ดิน",
        "role": "ราชินีดิน",
        "narrative": "ดูแลทั้งบ้านและงานด้วยความอบอุ่น เป็นฐานที่มั่นที่เต็มไปด้วยการเลี้ยงดู เป็นแม่ เจ้าของกิจการ หรือผู้หญิงที่รู้จักสร้างความมั่นคงและแบ่งปัน",
    },
    "King of Pentacles": {
        "zodiac": "พฤษ",
        "element": "ดิน",
        "role": "ราชาดิน",
        "narrative": "ควบคุมทรัพย์ด้วยปัญญา มั่งคั่ง หนักแน่น และให้ความรู้สึกปลอดภัยแก่คนรอบข้าง เป็นนักธุรกิจ ผู้อุปถัมภ์ หรือบิดาที่สร้างมรดกให้ลูก",
    },
}


def court_card_zodiac(card_name: str) -> dict | None:
    """Return zodiac mapping for a Court Card."""
    return COURT_ZODIAC.get(card_name)


# ═══════════════════════════════════════════════════════════════════════════
# 5. COMBINATION RULES — กฎการอ่านคู่
# ═══════════════════════════════════════════════════════════════════════════

COMBINATION_RULES: dict[str, str] = {
    "same_suit": "ไพ่สองใบที่ธาตูเดียวกัน แสดงถึงพลังงานที่เข้มข้นในทิศทางนั้น เช่น Cups + Cups = ความรู้สึกที่ลึกซึ้งและเป็นไปได้ที่จะเป็นจริง",
    "same_number": "ไพ่สองใบที่ตัวเลขเดียวกัน (เช่น 3 of Cups + 3 of Wands) แสดงถึงจังหวะที่ตรงกัน เลขนั้นๆ คือจำนวนหรือระยะเวลาที่สำคัญ",
    "major_dominant": "ถ้า Major Arcana ปรากฏร่วมกับ Minor แสดงว่าโชคชะตากำลังเล่นบทสำคัญ เรื่องนี้ไม่ใช่เรื่องเล็กๆ",
    "court_people": "ถ้า Court Cards หลายใบปรากฏ แสดงว่ามีคนหลายคนเกี่ยวข้อง หรือมีอิทธิพลจากผู้อื่นมาก",
    "reversed_warning": "ไพ่กลับหัวสองใบขึ้นไป คือสัญญาณเตือนว่ามีอุปสรรคหรือความเข้าใจผิดที่ต้องแก้",
    "all_yes": "ถ้าไพ่ทุกใบเป็น Yes แสดงว่าสถานการณ์ไปในทิศทางที่ดี แต่อย่าประมาท",
    "all_no": "ถ้าไพ่ทุกใบเป็น No แสดงว่ายังไม่ถึงเวลา หรือต้องเปลี่ยนแผน",
    "mixed": "ถ้าไพ่ผสม Yes/No/Maybe แสดงว่ามีทั้งโอกาสและอุปสรรค ต้องดูว่าใบไหนแข็งแกร่งที่สุด",
    "swords_dominant": "ถ้า Swords เยอะสุด แสดงว่าปัญหาหรือความขัดแย้งคือหัวใจ ต้องใช้เหตุผลแก้",
    "cups_dominant": "ถ้า Cups เยอะสุด แสดงว่าความรู้สึกหรือความสัมพันธ์คือหัวใจ ต้องฟังใจ",
    "wands_dominant": "ถ้า Wands เยอะสุด แสดงว่าการงานหรือความสนใจคือหัวใจ ต้องลงมือทำ",
    "pentacles_dominant": "ถ้า Pentacles เยอะสุด แสดงว่าเงินหรือความมั่นคงคือหัวใจ ต้องวางแญบ",
}


def analyze_combination(cards: list[dict]) -> dict:
    """Analyze a set of drawn cards and return combination insights."""
    suits = {"Wands": 0, "Cups": 0, "Swords": 0, "Pentacles": 0}
    major_count = 0
    court_count = 0
    reversed_count = 0
    yes_count = 0
    no_count = 0
    maybe_count = 0

    for c in cards:
        name = c.get("card", "")
        orientation = c.get("orientation", "upright")

        if name in ["The Fool", "The Magician", "The High Priestess", "The Empress",
                     "The Emperor", "The Hierophant", "The Lovers", "The Chariot",
                     "Strength", "The Hermit", "Wheel of Fortune", "Justice",
                     "The Hanged Man", "Death", "Temperance", "The Devil",
                     "The Tower", "The Star", "The Moon", "The Sun",
                     "Judgement", "The World"]:
            major_count += 1
        elif " of " in name:
            suit = name.split(" of ")[-1]
            if suit in suits:
                suits[suit] += 1
            if name.split(" of ")[0] in ["Page", "Knight", "Queen", "King"]:
                court_count += 1

        if orientation == "reversed":
            reversed_count += 1

        yn = yes_no_answer(name, orientation)
        if yn["answer"] == "yes":
            yes_count += 1
        elif yn["answer"] == "no":
            no_count += 1
        else:
            maybe_count += 1

    # Determine dominant suit
    dominant_suit = max(suits, key=suits.get) if any(suits.values()) else ""
    dominant_count = suits.get(dominant_suit, 0)

    insights = []

    if major_count >= 2:
        insights.append(COMBINATION_RULES["major_dominant"])
    if court_count >= 2:
        insights.append(COMBINATION_RULES["court_people"])
    if reversed_count >= 2:
        insights.append(COMBINATION_RULES["reversed_warning"])
    if yes_count == len(cards) and len(cards) > 0:
        insights.append(COMBINATION_RULES["all_yes"])
    elif no_count == len(cards) and len(cards) > 0:
        insights.append(COMBINATION_RULES["all_no"])
    elif dominant_count >= 2:
        suit_key = {"Wands": "wands_dominant", "Cups": "cups_dominant",
                    "Swords": "swords_dominant", "Pentacles": "pentacles_dominant"}.get(dominant_suit, "")
        if suit_key in COMBINATION_RULES:
            insights.append(COMBINATION_RULES[suit_key])

    return {
        "suits": suits,
        "major_count": major_count,
        "court_count": court_count,
        "reversed_count": reversed_count,
        "yes_count": yes_count,
        "no_count": no_count,
        "maybe_count": maybe_count,
        "dominant_suit": dominant_suit,
        "dominant_count": dominant_count,
        "insights": insights,
    }


# ═══════════════════════════════════════════════════════════════════════════
# 6. REVERSED PATTERNS — รูปแบบความหมายไพ่กลับหัว
# ═══════════════════════════════════════════════════════════════════════════

REVERSED_PATTERNS: dict[str, str] = {
    "blocked": "พลังงานถูกกดหรือบล็อก — สิ่งที่ควรเป็นไปได้กลับติดขัด",
    "delayed": "สิ่งที่ควรเกิดขึ้นถูกเลื่อนออกไป — ต้องรอคอย",
    "inverted": "ความหมายพลิกผัน — จากดีเป็นไม่ดี หรือจากไม่ดีเป็นดี",
    "internalized": "พลังงานเป็นภายใน — ต้องมองหาคำตอบในตัวเอง",
    "exaggerated": "พลังงานเกินขนาด — ต้องปรับสมดุล",
    "released": "การปล่อยวาง — สิ่งที่ผูกมัดเริ่มคลายตัว",
    "denial": "การปฏิเสธ — ไม่ยอมรับความจริง",
    "shadow": "เงามืด — สิ่งที่ซ่อนอยู่กำลังโผล่มา",
}


# ═══════════════════════════════════════════════════════════════════════════
# 7. ELEMENT BALANCE — ธาตูและความสมดุล
# ═══════════════════════════════════════════════════════════════════════════

ELEMENT_BALANCE: dict[str, dict] = {
    "fire": {
        "suits": ["Wands"],
        "qualities": ["กระตือรือร้น", "สร้างสรรค์", "กล้าหาญ", "เร็ว"],
        "excess": "ร้อนรุ่ง หุนหันพลันแล่น ขาดความรอบคอบ",
        "lack": "ไร้แรงบันดาลใจ เฉื่อยชา ไม่มีไฟ",
    },
    "water": {
        "suits": ["Cups"],
        "qualities": ["อ่อนโยน", "เห็นใจ", "จินตนาการ", "ลึกซึ้ง"],
        "excess": "อารมณ์ผันผวน จมอยู่กับความรู้สึก มองโลกงมงาย",
        "lack": "ไร้ความรู้สึก เย็นชา ไม่เข้าใจคน",
    },
    "air": {
        "suits": ["Swords"],
        "qualities": ["ชัดเจน", "เฉลียวฉลาด", "สื่อสาร", "ตรรกะ"],
        "excess": "คิดมาก วิตกกังวล พูดเก่งแต่ทำไม่เป็น",
        "lack": "สับสน ไม่มีความคิด ขาดการสื่อสาร",
    },
    "earth": {
        "suits": ["Pentacles"],
        "qualities": ["มั่นคง", "ทะนุถนอม", "สัมฤทธิ์", "ยั่งยืน"],
        "excess": "ดื้อดึง ยึดติด โลภ กลัวการเปลี่ยนแปลง",
        "lack": "ไม่มั่นคง สับสน ขาดเป้าหมาย",
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# 8. NARRATIVE TEMPLATES — เทมเพลตการอ่าน
# ═══════════════════════════════════════════════════════════════════════════

NARRATIVE_TEMPLATES = {
    "opening": "ไพ่ที่ปรากฏบอกว่า",
    "middle": "สิ่งที่คุณกำลังเผชิญคือ",
    "closing": "คำแนะนำสุดท้ายคือ",
    "warning": "ระวังเรื่อง",
    "encouragement": "แต่ไม่ต้องกลัว เพราะ",
    "timing": "เวลาที่คาดหวังคือ",
    "element": "ธาตูที่โดดเด่นคือ",
    "court": "มีคนรอบข้างที่เป็น",
    "reversed": "ไพ่กลับหัวเตือนว่า",
    "combination": "ไพ่เหล่านี้เล่าเรื่องราวร่วมกันว่า",
}


# ═══════════════════════════════════════════════════════════════════════════
# FOOL'S JOURNEY — Major Arcana เป็นเรื่องราวชีวิต (v5)
# ═══════════════════════════════════════════════════════════════════════════

JOURNEY_ORDER = [
    {"card": "The Fool", "age": 0, "stage": "จุดเริ่มต้น — ยืนรอขอบหน้าผาพร้อมกระโดดสู่ที่ไม่รู้จัก ศักยภาพสูงสุดแต่ยังไม่มีประสบการณ์"},
    {"card": "The Magician", "age": 7, "stage": "เริ่มโตเรียนรู้มีพลังสร้างความจริง สิ่งที่ทำส่งผลต่อโลกรอบข้าง"},
    {"card": "The High Priestess", "age": 14, "stage": "ปลุกจิตใต้สำนึก รับรู้สิ่งที่มองไม่เห็น ความรู้ภายในลึกซึ้งกว่าสิ่งที่สัมผัสได้"},
    {"card": "The Empress", "age": 21, "stage": "ถูกเลี้ยงด้วยความรักและความห่วงใย ธรรมชาติแม่ ความอุดมสมบูรณ์ การสร้างสรรค์ผลิตผล"},
    {"card": "The Emperor", "age": 28, "stage": "เรียนรู้กฎระเบียบ โครงสร้าง วินัย การตัดสินใจเป็นผู้นำ ความมั่นคง"},
    {"card": "The Hierophant", "age": 35, "step": "สอนและถ่ายทอด สถาบัน ความเชื่อ ปรัชญาของสังคม การเรียนจากผู้เชี่ยวชาญ"},
    {"card": "The Lovers", "age": 42, "stage": "เลือกคู่ชีวิต การตัดสินใจตามค่านิยม ความรักแท้ ความสัมพันธ์ลึกซึ้ง"},
]

def journey_for_card(card_name: str) -> dict:
    """Return Fool's Journey stage for a Major Arcana card."""
    for entry in JOURNEY_ORDER:
        if entry["card"] == card_name:
            return entry
    return {"card": card_name, "age": 0, "stage": "ไม่อยู่ใน Fool's Journey มาตรฐาน"}


# ═══════════════════════════════════════════════════════════════════════════
# JOE'S 78-CARD SYSTEM (v6) — โครงสร้างลึกของไพ่
# ═══════════════════════════════════════════════════════════════════════════

# Minor Arcana = เหตุการณ์/ประสบการณ์ตามกาลอวกาศ
# Court Cards = คน (แบ่ง 4 ตำแหน่ง)
# Major Arcana = โชคชะตา (แบ่ง 3 Subtenories + 7 Triads ตามดาวเคราะห์ 7)

COURT_OFFICES = {
    "Page": "เด็กผู้นำ — ผู้รับข่าว ผู้เริ่มต้น พลังงานยังเป็นความหวัง",
    "Knight": "อัศวิน — ผู้ลุย ผู้เคลื่อนที่ พลังงานกำลังจะเป็นจริง",
    "Queen": "ราชินี — ผู้เลี้ยงดู ผู้ครอบครอง พลังงานเต็มที่และควบคุมได้",
    "King": "กษัตริย์ — ผู้ปกครอง ผู้ตัดสินใจ พลังงานถึงจุดสูงสุด เสถียร",
}

MAJOR_SUBTENORIES = {
    "Celestial": ["The Magician", "The High Priestess", "The Empress", "The Emperor", "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit", "Wheel of Fortune"],
    "Ego": ["Justice", "The Hanged Man", "Death", "Temperance", "The Devil", "The Tower", "The Star", "The Moon", "The Sun", "Judgement"],
    "Soul": ["The World", "The Fool"],
}

MAJOR_TRIADS = {
    "ดาวอังคาร (Mars)": ["The Tower", "The Devil", "The Emperor"],
    "ดาวพุธ (Mercury)": ["The Magician", "The Fool", "The Lovers"],
    "ดาวพฤหัส (Jupiter)": ["Wheel of Fortune", "The Sun", "The World"],
    "ดาวศุกร์ (Venus)": ["The Empress", "The Lovers", "Judgement"],
    "ดาวเสาร์ (Saturn)": ["The World", "The Hermit", "The Hanged Man"],
    "ดาวพระอาทิตย์ (Sun)": ["The Star", "Judgement", "The Sun"],
    "ดาวพระจันทร์ (Moon)": ["The High Priestess", "The Chariot", "The Moon"],
}


# ═══════════════════════════════════════════════════════════════════════════
# ANNUAL PERFECTIONS (v7) — ธีมชีวิตปีต่อปีแบบ Hellenistic
# ═══════════════════════════════════════════════════════════════════════════

# เทคนิคโบราณกรีก: เกิดมา = ปีที่ 1 (บ้าน 1), อายุ 1 = ปีที่ 2 (บ้าน 2)...
# ปีที่ N = (N mod 12) + 1 (ถ้า mod = 0 แสดงว่าเป็นบ้าน 12)

def annual_perfection(age: int) -> int:
    """Return the house number for a given age.
    Age 0 = 1st house, Age 1 = 2nd house, ..., Age 11 = 12th house,
    Age 12 = 1st house again, etc."""
    return (age % 12) + 1

def month_house(age: int, month: int) -> int:
    """Return the house number for a specific month of a specific age.
    month = 1-12 where 1 = birthday month.
    """
    base = annual_perfection(age)  # 1-12
    house = (base + month - 1) % 12
    return 12 if house == 0 else house

ANNUAL_PERFECTION_HOUSES = {
    1: "ปีแห่งการเริ่มต้น — ตัวตนใหม่ รูปลักษณ์ พลังชีวิต การมาเกิด",
    2: "ปีแห่งทรัพย์สิน — การเงิน ทรัพย์สมบัติ คุณค่าของตนเอง",
    3: "ปีแห่งการสื่อสาร — พี่น้อง เพื่อนบ้าน การเรียนรู้ การเดินทางใกล้",
    4: "ปีแห่งบ้าน — ครอบครัว บิดา รากฐานทางใจ อดีต",
    5: "ปีแห่งความสุข — ความรัก การสร้างสรรค์ บุตร งานอดิเรก",
    6: "ปีแห่งการงาน — การทำงาน กิจวัตร สุขภาพ การรับใช้",
    7: "ปีแห่งความสัมพันธ์ — คู่ชีวิต คู่ธุรกิจ การทำสัญญา ศัตรูที่ปรากฏ",
    8: "ปีแห่งการเปลี่ยนแปลง — การตาย มรดก เพศ ความลับ พลังอันซ่อนเร้น",
    9: "ปีแห่งการศึกษา — ปรัชญา การเดินทางไกล ศาสนา ความเชื่อ",
    10: "ปีแห่งการงานชื่อเสียง — อาชีพ ตำแหน่งทางสังคม มารดา",
    11: "ปีแห่งมิตรภาพ — เพื่อน ความหวัง การได้รับการสนับสนุน",
    12: "ปีแห่งความเจ็บปวด — การสูญเสีย สิ่งที่ซ่อนอยู่ ศัตรูลับ การเดินทางไกลไม่คาดฝัน",
}

def life_themes(age: int) -> dict:
    """Return the themes for a given age."""
    house = annual_perfection(age)
    return {
        "age": age,
        "house": house,
        "theme": ANNUAL_PERFECTION_HOUSES[house],
    }


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "YES_NO",
    "yes_no_answer",
    "SUIT_SPEED",
    "NUMBER_QUANTITY",
    "timing_for_card",
    "SPREADS",
    "get_spread",
    "list_spreads",
    "COURT_ZODIAC",
    "court_card_zodiac",
    "COMBINATION_RULES",
    "analyze_combination",
    "REVERSED_PATTERNS",
    "ELEMENT_BALANCE",
    "NARRATIVE_TEMPLATES",
    # Fool's Journey
    "JOURNEY_ORDER",
    "journey_for_card",
    # Joe's 78-card system
    "COURT_OFFICES",
    "MAJOR_SUBTENORIES",
    "MAJOR_TRIADS",
    # Annual Perfections
    "annual_perfection",
    "month_house",
    "ANNUAL_PERFECTION_HOUSES",
    "life_themes",
]
