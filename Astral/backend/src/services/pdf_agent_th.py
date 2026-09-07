"""PDF writing specialist agent — Thai narrative only."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.services.synastry_scoring import compute_synastry_profile
from src.services.element_service import compute_element_balance
from src.services.tarot_service import draw_spread
from src.services.tarot_downloader import get_card_path, ensure_deck_ready


@dataclass(frozen=True)
class Persona:
    name: str
    sun: str
    moon: str
    mercury: str
    asc: str


@dataclass(frozen=True)
class CoupleContext:
    a: Persona
    b: Persona
    score: int = 0
    top_bond: str = ""
    top_dimension: str = ""
    top_friction: str = ""


def _seed(name_a: str, name_b: str, spread: str) -> int:
    return int(hashlib.sha256(f"{name_a}|{name_b}|{spread}".encode()).hexdigest()[:8], 16)


def section_overview(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"ดูหน้าตาแรก {a.name} เป็นคนช้า เขาไม่รีบเปิดเผยตัวเอง แต่พอรู้สึกปลอดภัย อาทิตย์{a.sun} ลัคนา{a.asc} เขาโชว์สีจริงออกมา — จริงใจ แม้จะไม่พูดเสียงดัง",
        f"ฝั่งอีกด้าน {b.name} เธอเหมือนคนเตรียมความพร้อมทุกครั้ง อาทิตย์{b.sun} ลัคนา{b.asc} เขาชอบวางแผน กว่าจะกระทำอะไรก็ต้องเห็นภาพล่วงหน้า",
        f"ทั้งสองมาพบกันไม่ได้เผลอเลย มันไม่ใช่เรื่องบังเอิญ แต่เป็นเรื่องที่แต่ละคนเตรียมไม่รู้สึก ทั้งชีวิตได้กลั่นกรองเป็นแบบนี้ จนวันหนึ่งเจอกัน ก็รู้ทันทีว่าใช่",
        f"ดวงจันทร์{a.name} อยู่{a.moon} เขาต้องการพื้นที่ปลอดภัย ไม่ต้องติชม ไม่ต้องถูกวิจารณ์ ส่วนดวงจันทร์{b.name} อยู่{b.moon} เธอต้องการอะไรที่มั่นคง ไม่ใช่แค่ความรู้สึก แต่อันาคตที่มองเห็นเส้นทาง",
        "",
        "",
    ]


def section_bonds(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"ลองนึกภาพคืนหนึ่ง{a.name} เหนื่อยกับภาระหน้าที่ สะดุดไซร้จะดึงออกจากโลก แทนที่จะโทรหา{b.name} กดสายรับแทน — ไม่ใช่เพราะควร แต่เพราะรู้สึกว่าเขาต้องการคนอยู่ใกล้ๆ มันไม่ใช่ดราม่า แต่คือจุดติดกันที่แท้จริง",
        f"จุดแข็งคือดวงจันทร์ทั้งสองมองเห็นโลกไม่ตรงข้ามเลย — {a.name} ต้องการความปลอดภัยทางใจที่มีโครงสร้าง {b.name} ต้องการระบบและการวางแผน การอยู่ด้วยไม่ได้แปลว่าไม่มีปัญหา แต่คือปัญหาที่เขารู้จักวิธีแก้ด้วยกัน",
        f"ดาวพุธ{a.name} อยู่{a.mercury} ร่วมกับลัคนา{b.name} การสื่อสารไม่เคยเป็นปัญหา ทั้งสองคิดคล้ายกัน แม้ออกเสียงไม่เหมือนกัน ใครเป็นคนช้า ใครเป็นคนmeasured ก็ฟังเข้าใจกันเสมอ",
        "",
        "",
    ]


def section_frictions(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"ไม่มีคู่ไหนไร้แรงเสียดทาน — คู่นี้ก็ไม่ยกเว้น แต่วิธีรับมือแตกต่าง: สมมติเสียงเถียงที่เพื่อนบ้านต้องเงียบไปทั้งห้อง นั่นไม่ใช่สาเหตุให้ร้องไห้ แต่เป็นสัญญาณว่าต้องปรับ การที่อังคารชนกันไม่ได้แปลว่าความรักพ่ายแพ้ แต่แปลว่ากำลังฝึกซ้ำวิธีต่อสู้กับกัน",
        f"ลัคนา{a.name} {a.asc} ศอกชนกับอาทิตย์{b.name} {b.sun} เป็นการดึงดูดรุนแรง — ไม่ใช่รุนแรงจนทำร้าย แต่รุนแรงจนอยากรู้จักอีก คนภายนอกเข้าใจไม่ได้ เพราะดูเหมือนเกินไป แต่คู่นี้รู้ว่ามันคือความ ardent",
        f"สรุปแรงเสียดทานทั้งหมด: ไม่ใช่จุดที่ร้ายแรงจนแก้ไม่ได้ แต่เป็นงานที่ต้องทำด้วยกัน ถ้ารู้จักหยุดพัก ถ้ารู้จักพูดก่อนทำ ความขัดแย้งไม่สะสม กลายเป็น ประวัติศาสตร์ ที่สองคนร่วมกันสร้าง",
        "",
        "",
    ]


def section_score(ctx: CoupleContext) -> list[str]:
    score = ctx.score
    return [
        f"สรุปคะแนน: {score}/100 — ไม่ใช่เลขสูงสุด แต่คือเลขที่บอกว่า ความสัมพันธ์ นี้มี พื้นที่เติบโต อยู่เหนือ comfort zone",
        f"จุดที่เด่นที่สุด: {ctx.top_bond} — {ctx.top_dimension} — สี่เหลี่ยมนี้คือเหตุผลที่เขายึดเหนี่ยวอยู่ไม่ใช่แค่เหตุผลที่ตกหลุมรัก",
        f"___ chemistry + การสื่อสาร + ความมั่นคง ครบสามเสาหลัก และแรงเสียดทานที่เหลือเป็น เส้นทางการเรียนรู้ ที่คู่นี้เดินผ่านกันได้ — {score} คะแนนไม่ใช่ การพ่ายแพ้ แต่นี้คือ ความสัมพันธ์ ที่ไม่ง่าย แต่คุ้ม",
        "",
        "",
    ]


def section_advice(ctx: CoupleContext) -> list[str]:
    a, b = ctx.a, ctx.b
    return [
        f"รักไม่ได้แพ้เพราะคนไม่ใช่กัน แต่แพ้เพราะพูดคนละภาษา — {a.name} รักผ่านการกระทำ การอยู่ข้างๆ การไม่มีเสียงก็พอ ส่วน{b.name} รักผ่านคำพูด การยืนยัน การบอกว่าอะไรสำคัญ",
        f"สำหรับ{a.name}: ให้{b.name} รู้สึก ได้ยิน — ไม่ต้องอธิบายยาว ต้องการแค่หนึ่งประโยคที่บอกว่า เธอสำคัญ การบอกความรู้สึกก็ไม่ทำให้อ่อน",
        f"สำหรับ{b.name}: ความเงียบของ{a.name} ไม่ใช่ไม่ใส่ใจ — แต่คือภาษารักแบบเต่าที่ช้าแต่ไม่เคยหัก ถ้า{b.name} บอกว่า ไม่รู้ว่าเขารู้สึกอะไร ลองไม่ใช่บังคับให้พูด แต่อยู่ด้วยกันเฉยๆ",
        f"ร่วมกัน: จองเวลาคุยกันตอนอารมณ์สงบ หลังความดราม่า 3 นาทีก่อนเริ่มพูด — ดาวอังคารทั้งสองที่เถียงแรง ก็คือดาวที่ passionate กัน เช่นกัน ถ้าเปลี่ยนหัวข้อคุยเบาๆ เป็นคำชมเชย วันรุ่งขึ้น คู่นี้ไม่เคยน่าเบื่อ",
        "",
    ]


def build_synastry_sections(
    name_a: str,
    name_b: str,
    chart_a: dict,
    chart_b: dict,
    spread: str = "three_card",
) -> tuple[list[dict], str, str]:
    def _sign(body_name: str, chart: dict) -> str:
        for b in chart.get("bodies", []):
            if b.get("body") == body_name:
                return b.get("sign", "")
        return ""

    sun_a = _sign("Sun", chart_a)
    moon_a = _sign("Moon", chart_a)
    mercury_a = _sign("Mercury", chart_a)
    asc_a = chart_a.get("ascendant", {}).get("sign", "")

    sun_b = _sign("Sun", chart_b)
    moon_b = _sign("Moon", chart_b)
    mercury_b = _sign("Mercury", chart_b)
    asc_b = chart_b.get("ascendant", {}).get("sign", "")

    a_p = Persona(name_a, sun_a, moon_a, mercury_a, asc_a)
    b_p = Persona(name_b, sun_b, moon_b, mercury_b, asc_b)

    profile = compute_synastry_profile(chart_a, chart_b)
    score = int(profile.get("overall", 0))
    top_bonds = profile.get("top_bonds", [])
    top = top_bonds[0] if top_bonds else {}
    frictions = profile.get("frictions", [])
    top_friction = frictions[0] if frictions else {}

    ctx = CoupleContext(
        a=a_p,
        b=b_p,
        score=score,
        top_bond=top.get("pair", ""),
        top_dimension=top.get("dimension", ""),
        top_friction=top_friction.get("aspect", ""),
    )

    sections = [
        {"title": f"ภาพรวมของคู่แพร์ — {name_a} + {name_b}", "lines": section_overview(ctx)},
        {"title": f"✨ พันธะที่แนบแน่น — จุดแข็งที่ช่วยอยู่ด้วยกันได้นาน", "lines": section_bonds(ctx)},
        {"title": f"⚡ จุดที่ต้องเรียนรู้ — แรงเสียดทานที่ทำให้โตไปด้วยกัน", "lines": section_frictions(ctx)},
        {"title": f"🔮 คะแนนความเข้ากันได้ — {score}/100", "lines": section_score(ctx)},
        {"title": f"💌 คำแนะนำจากหมอดู — ให้เธอเลือกฟังข้อไหนก็ได้", "lines": section_advice(ctx)},
    ]

    seed_a = _seed(name_a, name_b, spread)
    seed_b = _seed(name_b, name_a, spread)
    cards_a = draw_spread(name_a, spread=spread, seed=seed_a, element_balance=compute_element_balance(chart_a))
    cards_b = draw_spread(name_b, spread=spread, seed=seed_b, element_balance=compute_element_balance(chart_b))

    def _tarot_html(cards, title):
        rows = []
        for c in cards:
            path = get_card_path(c["card"])
            if path:
                img_src = f"file:///{path.as_posix()}"
                img_html = f"<div class=\"tcard-img\"><img src=\"{img_src}\" alt=\"{c['card']}\"/></div>"
            else:
                img_html = ""
            rows.append(f"""
              <div class="tcard">
                {img_html}
                <div class="tcard-pos">{c['position']}</div>
                <div class="tcard-name">🃏 {c['card']}</div>
                <div class="tcard-mean">{c['meaning']}</div>
              </div>""")
        return f'<div class="trow-head">{title}</div><div class="trow">{"".join(rows)}</div>'

    tarot_html = _tarot_html(cards_a["cards"], f"ไพ่ประจำตัวของ {name_a}") + '<div style="height:4mm"></div>' + _tarot_html(cards_b["cards"], f"ไพ่ประจำตัวของ {name_b}")
    tarot_title = f"ไพ่เทพนิยายประจำตัว — {name_a} ♥ {name_b}"

    return sections, tarot_html, tarot_title


def _persona_from_chart(name: str, chart: dict) -> Persona:
    import re

    def _sign(body_name: str) -> str:
        for b in chart.get("bodies", []):
            if b.get("body") == body_name:
                sig = b.get("sign", "") or ""
                # strip latin parenthetical e.g. "เมษ(Aries)" -> "เมษ"
                sig = re.sub(r"\([^)]*\)", "", sig).strip()
                return sig
        return ""
    asc = chart.get("ascendant", {}).get("sign", "") or ""
    asc = re.sub(r"\([^)]*\)", "", asc).strip()
    return Persona(
        name=name,
        sun=_sign("Sun"),
        moon=_sign("Moon"),
        mercury=_sign("Mercury"),
        asc=asc,
    )


def build_natal_sections(name: str, chart: dict) -> list[dict]:
    persona = _persona_from_chart(name, chart)
    return [
        {
            "title": f"บุคลิกภาพ — {name}",
            "lines": [
                f"{name} ดูหน้าตาแรก คนพวกนี้ พุธ{persona.sun} ลัคนา{persona.asc} — ไม่ใช่คนที่ทำอะไรก็ได้ เอาล่ะ แต่เลือกทำอย่างที่คุ้มค่า",
                f"จิตใจ（ดวงจันทร์）อยู่{persona.moon} — ต้องการที่ปลอดภัย ไม่ต้องอธิบายว่าทำไม",
                f"ดาวพุธ（ความคิด） อยู่ราศี{persona.mercury} ร่วมกับลัคนา — การสื่อสารไม่ใช่เกม แต่คือวิธีเข้าใจคนอีกที",
                f"หน้าตาเบาๆ ไม่ใช่ใจลอยเลย แต่เป็นความเจใสร้อนแรง จนบางทีคนเข้าใจผิดว่าไม่ใส่ใจ แต่นั่นไม่ใช่ จริงๆ คือโลกภายในมีชีวิตชีวา",
                "",
                "ถ้าอยากรู้จักเขา จนต้องรู้จักเสียงเงียบก่อนคำพูด ความสัมพันธ์กับเขาคือ การฝึกฝน ไม่ใช่การแสดง",
                "",
                "",
            ],
        }
    ]


def build_composite_sections(name_a: str, name_b: str, chart_a: dict, chart_b: dict) -> list[dict]:
    from src.services.composite_service import compute_composite
    composite = compute_composite(chart_a, chart_b)
    sun = next((b["sign"] for b in composite.get("bodies", []) if b["body"] == "Sun"), "")
    moon = next((b["sign"] for b in composite.get("bodies", []) if b["body"] == "Moon"), "")
    asc = composite.get("ascendant", {}).get("sign", "")
    return [
        {
            "title": f"ดาว midpoint ของ {name_a} + {name_b} / ภาพรวม energy คู่",
            "lines": [
                f"{name_a} + {name_b} ดวง composite อาทิตย์{sun} จันทร์{moon} ลัคนา{asc} — คู่นี้ไม่ใช่สองคนแยกกัน แต่เป็นตัวใหม่ที่เกิดจากจุดตรงกลางของทั้งสอง",
                f"พลังงานไม่ใช่บวกตรงๆ แต่เป็นบรรทัดฐานที่ทั้งสองพอจะเข้าใจกัน — ที่นี่ composite ทำให้ความสัมพันธ์กลายเป็นมนุษยธรรมanskte",
                f" composite chart ไม่ใช่ 'super couple' แต่คือแผนที่ความสัมพันธ์ที่ทั้งสองต้องพัฒนาร่วมกัน",
                "",
                "",
            ],
        }
    ]


def build_transit_sections(name: str, natal_chart: dict, transits: list[dict]) -> list[dict]:
    hits = transits[:8]
    return [
        {
            "title": f"transit now — {name} / ดาวปัจจุบันกำลังหล่นหลับ",
            "lines": [
                f"ดวงปัจจุบันของ{name} ไม่เคยนอน — มี {len(hits)} จุดที่ดาวสะเทือนวงกลม",
                f"ทิศทางที่สำคัญ: ดาวเสาร์/ดาวพฤหัสบดี/พลังงานจัดการ โดน aspect จากดาวปัจจุบัน ไม่ใช่ลงโทษ แต่เป็น การเตือน",
                f"จังหวะที่ควรระวัง: ถ้า Jupiter/Saturn โดน aspect จากปัจจุบัน ให้ระวังการเปลี่ยนที่อยู่อาศัย/การเงินกะพริบ — จุดนี้คือ การลงทุนที่คุณเลือกเอง",
                "",
                "",
            ],
        }
    ]


def build_muhurta_sections(action: str, windows: list[dict]) -> list[dict]:
    top = windows[:3]
    if not top:
        return [{"title": f"muhurta — {action}", "lines": ["ไม่พบช่วงมงคลในช่วงนี้", ""]}]
    return [
        {
            "title": f"muhurta — {action} / เลือกวันมงคล",
            "lines": [
                f"ช่วงมงคลสำหรับ {action}: {top[0]['when_local']} — score {top[0]['score']} — เหตุผล: {'; '.join(top[0].get('reasons_th', [])[:2])}",
                f"ตัวที่สอง: {top[1]['when_local'] if len(top) > 1 else '-'} — score {top[1]['score'] if len(top) > 1 else '-'} — เหตุผล: {'; '.join(top[1].get('reasons_th', [])[:2]) if len(top) > 1 else '-'}",
                f"ตัวที่สาม: {top[2]['when_local'] if len(top) > 2 else '-'} — score {top[2]['score'] if len(top) > 2 else '-'} — เหตุผล: {'; '.join(top[2].get('reasons_th', [])[:2]) if len(top) > 2 else '-'}",
                "",
                "",
            ],
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
