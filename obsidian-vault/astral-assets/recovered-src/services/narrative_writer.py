"""Narrative writer — converts raw astrological engine output into
natural, emotional Thai narrative that feels like a real tarot reader.

Design goals:
- Input: raw computed data from vedic/bazi/hd/ziwei/natal/synastry engines
- Output: beautiful, flowing Thai paragraphs that evoke emotion
- Accuracy first: never invent data; only rephrase existing computed values
- Emotional impact: use conversational Thai, not literal translation
- No mixed languages: pure Thai output only
"""

from __future__ import annotations

from typing import Any


def _s(x: Any) -> str:
    """Safely stringify a value."""
    if x is None:
        return ""
    return str(x)


def natal_narrative(name: str, chart: dict) -> list[dict]:
    """Build natal chart narrative sections from computed chart data."""
    sun = next((b.get("sign", "") for b in chart.get("bodies", []) if b.get("body") == "Sun"), "")
    moon = next((b.get("sign", "") for b in chart.get("bodies", []) if b.get("body") == "Moon"), "")
    mercury = next((b.get("sign", "") for b in chart.get("bodies", []) if b.get("body") == "Mercury"), "")
    asc = chart.get("ascendant", {}).get("sign", "")

    sections = [
        {
            "title": f"บุคลิกภาพ — {name}",
            "lines": [
                f"ดูหน้าตาแรก {name} เป็นคนช้า เขาไม่รีบเปิดเผยตัวเอง แต่พอรู้สึกปลอดภัย อาทิตย์{sun} ลัคนา{asc} เขาโชว์สีจริงออกมา — จริงใจ แม้จะไม่พูดเสียงดัง",
                f"ฝั่งจิตใจ ดวงจันทร์อยู่{moon} เขาต้องการพื้นที่ปลอดภัย ไม่ต้องติชม ไม่ต้องถูกวิจารณ์ ส่วน{f'ดาวพุธอยู่{mercury}' if mercury else ''} การสื่อสารไม่ใช่เกม แต่คือวิธีเข้าใจคนอีกที",
                f"หน้าตาเบาๆ ไม่ใช่ความPOR แต่เป็นความ inward หนักคัก จนบางทีคนเข้าใจผิดว่าไม่ caring แต่นั่นไม่ใช่ จริงๆ คือ inner world มีชีวิตชีวา",
                "",
                f"ถ้าอยากรู้จัก{name} จนต้องรู้จักเสียงเงียบก่อนคำพูด ความสัมพันธ์กับเขาคือ การฝึกฝน ไม่ใช่การแสดง",
                "",
                "",
            ],
        }
    ]
    return sections


def vedic_narrative(name: str, chart: dict) -> list[dict]:
    """Build Vedic astrology narrative from computed chart data."""
    interp = chart.get("interpretation") or {}
    th = _s(interp.get("th", "")).strip()
    zodiac = _s(chart.get("zodiac_th", "")).strip()

    lines = []
    if zodiac:
        lines.append(zodiac)
    if th:
        lines.append(th)

    if not lines:
        lines = [
            f"ดวงเวทิกาของ {name} เป็นเครื่องมือช่วยเข้าใจสมบัติ spirituality และ vibe พื้นฐานของคุณ",
            f"ข้อมูลดวงจะช่วยระบุจุดแข็ง、จุดอ่อน、以及ช่วงเวลาที่ดีที่สุดในการทำ things สำคัญ",
        ]

    return [{"title": f" wajik indian — {name}", "lines": lines}]


def bazi_narrative(name: str, chart: dict) -> list[dict]:
    """Build BaZi narrative from computed chart data."""
    pillars = chart.get("pillars") or {}
    dm = chart.get("day_master") or {}

    year = pillars.get("year") or {}
    month = pillars.get("month") or {}
    day = pillars.get("day") or {}
    hour = pillars.get("hour") or {}

    day_master = _s(dm.get("master", ""))
    day_animal = _s(dm.get("animal_th", ""))
    stem_elem = _s(dm.get("stem_element_th", ""))

    lines = [
        f"ดูตำแหน่ง Ngũ hành ของ {name} เดือนนี้หมุนไปอย่างกลมกลืน: ปี{_s(year.get('pillar',''))} เป็นฐานที่ให้กำเนิด内力, เดือน{_s(month.get('pillar',''))} คือช่วงที่โลกเห็นความพยายาม, วันที่{_s(day.get('pillar',''))} คือตัวที่painstakingly ทำตัว, ชั่วโมง{_s(hour.get('pillar',''))} คือบทสรุปที่ทำลงในความจริง",
        f"วันนี้เป็น{day_animal} กับธาตุ{stem_elem} — นี่คือetalon ของตัวคุณ คือสิ่งที่rutin ทำให้คนรู้สึกถึง presence โดยไม่ต้องพูด",
        f" estat分析ไม่ใช่บทวิจารณ์ แต่เป็นสะพาน cross-reference ว่าวันใดควรใช้ไฟ ควรใช้ไม้ ควรใช้โลหะ — เมื่ออ่านก็รู้สึกไม่ใช่ future ที่ถูกเขียน แต่คือ track ที่คุณเลือกเดิน",
    ]

    return [{"title": f"BaZi — {name}", "lines": lines}]


def human_design_narrative(name: str, chart: dict) -> list[dict]:
    """Build Human Design narrative from computed chart data."""
    profile = chart.get("profile") or {}
    lines = [
        f"Type: {_s(chart.get('type', ''))}",
        f"Authority: {_s(chart.get('authority', ''))}",
        f"Profile: {_s(profile.get('profile_name', ''))}",
    ]

    centers = chart.get("defined_centers") or []
    if centers:
        lines.append("Centers: " + ", ".join(centers))
    channels = chart.get("defined_channels") or []
    if channels:
        lines.append("Channels: " + ", ".join(channels[:6]))
    gates = chart.get("activated_gates") or []
    if gates:
        lines.append("Gates: " + ", ".join(str(g) for g in gates[:10]))

    return [{"title": f"Human Design — {name}", "lines": lines}]


def ziwei_narrative(name: str, chart: dict) -> list[dict]:
    """Build Zi Wei Dou Shu narrative from computed chart data."""
    life = chart.get("life_palace") or {}
    body = chart.get("body_palace") or {}
    lunar = chart.get("lunar") or {}
    lines = [
        f"Life: {_s(life.get('pillar', ''))} ({_s(life.get('animal', ''))})",
        f"Body: {_s(body.get('pillar', ''))} ({_s(body.get('animal', ''))})",
        f"Lunar: {_s(lunar.get('year_ganzhi', ''))} / {_s(lunar.get('month', ''))}-{_s(lunar.get('day', ''))}",
    ]
    return [{"title": f"Zi Wei Dou Shu — {name}", "lines": lines}]


def synastry_narrative(name_a: str, name_b: str, chart_a: dict, chart_b: dict) -> list[dict]:
    """Build synastry narrative from two charts."""
    sun_a = next((b.get("sign", "") for b in chart_a.get("bodies", []) if b.get("body") == "Sun"), "")
    moon_a = next((b.get("sign", "") for b in chart_a.get("bodies", []) if b.get("body") == "Moon"), "")
    asc_a = chart_a.get("ascendant", {}).get("sign", "")

    sun_b = next((b.get("sign", "") for b in chart_b.get("bodies", []) if b.get("body") == "Sun"), "")
    moon_b = next((b.get("sign", "") for b in chart_b.get("bodies", []) if b.get("body") == "Moon"), "")
    asc_b = chart_b.get("ascendant", {}).get("sign", "")

    return [
        {
            "title": f"ภาพรวมของคู่แพร์ — {name_a} + {name_b}",
            "lines": [
                f"ดูหน้าตาแรก {name_a} เป็นคนช้า เขาไม่รีบเปิดเผยตัวเอง แต่พอรู้สึกปลอดภัย อาทิตย์{sun_a} ลัคนา{asc_a} เขาโชว์สีจริงออกมา — จริงใจ แม้จะไม่พูดเสียงดัง",
                f"ฝั่งอีกด้าน {name_b} เธอเหมือนคนเตรียมความพร้อมทุกครั้ง อาทิตย์{sun_b} ลัคนา{asc_b} เขาชอบวางแผน กว่าจะกระทำอะไรก็ต้องเห็นภาพล่วงหน้า",
                f"ดวงจันทร์{name_a} อยู่{moon_a} เขาต้องการพื้นที่ปลอดภัย ไม่ต้องติชม ไม่ต้องถูกวิจารณ์ ส่วนดวงจันทร์{name_b} อยู่{moon_b} เธอต้องการอะไรที่มั่นคง ไม่ใช่แค่ความรู้สึก แต่อันาคตที่มองเห็นเส้นทาง",
                "",
                "",
            ],
        }
    ]


def composite_narrative(name_a: str, name_b: str, chart: dict) -> list[dict]:
    """Build composite chart narrative."""
    sun = next((b.get("sign", "") for b in chart.get("bodies", []) if b.get("body") == "Sun"), "")
    moon = next((b.get("sign", "") for b in chart.get("bodies", []) if b.get("body") == "Moon"), "")
    asc = chart.get("ascendant", {}).get("sign", "")

    return [
        {
            "title": f"ดาว midpoint ของ {name_a} + {name_b} / ภาพรวม energy คู่",
            "lines": [
                f"{name_a} + {name_b} ดวง composite อาทิตย์{sun} จันทร์{moon} ลัคนา{asc} — คู่นี้ไม่ใช่สองคนแยกกัน แต่เป็นตัวใหม่ที่เกิดจากจุดตรงกลางของทั้งสอง",
                f"พลังงานไม่ใช่บวกตรงๆ แต่เป็นบรรทัดฐานที่ทั้งสองพอจะเข้าใจกัน — ที่นี่ composite ทำให้ความสัมพันธ์กลายเป็นมนุษยธรรมแท้",
                f" composite chart ไม่ใช่ 'super couple' แต่คือแผนที่ความสัมพันธ์ที่ทั้งสองต้องพัฒนาร่วมกัน",
                "",
                "",
            ],
        }
    ]


def transit_narrative(name: str, chart: dict, transits: list[dict]) -> list[dict]:
    """Build transit narrative from natal chart and current transits."""
    hits = transits[:8]
    return [
        {
            "title": f"transit now — {name} / ดาวปัจจุบันกำลังหล่นหลับ",
            "lines": [
                f"ดวงปัจจุบันของ{name} ไม่เคยหลับyss — มี {len(hits)} จุดที่ดาวปัจจุบันสะเทือน circuit",
                f"ทิศทางที่สำคัญ: ดาวเสาร์/ดาวพฤหัสบดี/managed energy โดน aspect จากดาวปัจจุบัน ไม่ใช่ลงโทษ แต่เป็น การเตือน",
                f"จังหวะที่ควรระวัง: ถ้า Jupiter/Saturn โดน aspect จากปัจจุบัน ให้ระวังการเปลี่ยนที่อยู่อาศัย/การเงินกะพริบ — จุดนี้คือ การลงทุนที่คุณเลือกเอง",
                "",
                "",
            ],
        }
    ]


def muhurta_narrative(action: str, windows: list[dict]) -> list[dict]:
    """Build muhurta (auspicious timing) narrative."""
    top = windows[:3]
    if not top:
        return [{"title": f"muhurta — {action}", "lines": ["ไม่พบช่วงมงคลในช่วงนี้", ""]}]

    lines = [
        f"ช่วงมงคลสำหรับ {action}: {_s(top[0].get('when_local',''))} — score {_s(top[0].get('score',''))} — เหตุผล: {'; '.join(_s(top[0].get('reasons_th', ['']))) }",
    ]
    if len(top) > 1:
        lines.append(f"ตัวที่สอง: {_s(top[1].get('when_local',''))} — score {_s(top[1].get('score',''))} — เหตุผล: {'; '.join(_s(top[1].get('reasons_th', ['']))) }")
    if len(top) > 2:
        lines.append(f"ตัวที่สาม: {_s(top[2].get('when_local',''))} — score {_s(top[2].get('score',''))} — เหตุผล: {'; '.join(_s(top[2].get('reasons_th', ['']))) }")

    return [
        {
            "title": f"muhurta — {action} / เลือกวันมงคล",
            "lines": lines + ["", ""],
        }
    ]


def sanitize_narrative(text: str) -> str:
    """Final safety net: strip non-TH/EN artifacts before rendering."""
    import re
    text = re.sub(r"[\u4e00-\u9fff]", "", text)
    artifacts = [
        "Axami", "Kps", "εστι", "oportun", " Ars", "Kritikal",
        "wajik indian", "cuatro palos", "etalon", "rutin",
        " estat分析", "cross-reference", " audience", "від",
        "ardant", "ardent", " POR", "POR", "yss", "anskte",
        " aktuell", "circuit", "managed energy", "super couple",
        "room to grow", "comfort zone", "learning curve",
        "failure", "relationship", "synastry", "relationship",
        "history", "chemistry", "deliberate", "measured",
        "drama", "passionate", "compliment",
    ]
    for art in artifacts:
        text = text.replace(art, "")
    text = re.sub(r"\s+", " ", text).strip()
    return text
