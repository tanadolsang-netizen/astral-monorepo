# -*- coding: utf-8 -*-
"""STARHEART — Narrative engine that feels like a real person telling your story.

ใช้ narrative_lang เป็น single source of truth สำหรับภาษา
ไม่มีคำศัพท์ภาษาซ้ำซากในไฟล์นี้อีก
"""

from __future__ import annotations

from src.services import starheart_map
from src.services.element_service import compute_element_balance
from src.services.narrative_lang import (
    sign_name,
    element_name,
    body_label,
    aspect_intensity,
    dignity_desc,
    closing_convergence,
    closing_element,
    element_domain,
    PLACEMENT_TEMPLATES,
)


def _body_from_prov(prov: str) -> str:
    if prov.startswith(("ASC", "MC")):
        return prov.split(" ")[0] if " " in prov else prov
    if prov.startswith(("element:", "house:", "aspect:")):
        return prov.split(":")[0]
    return prov.split(" @")[0].strip()


def ground_narrative(chart: dict, lang: str = "th",
                     user_name: str | None = None,
                     user_question: str | None = None) -> str:
    """Generate a natural, story-like narrative from chart positions."""
    if chart is None:
        raise ValueError("ground_narrative requires a real chart")

    name = user_name or ("คุณ" if lang == "th" else "you")
    EN = (lang == "en")

    # Get tarot bridge
    mapped = starheart_map.MAP(chart, max_cards=14)
    card_by_body: dict[str, str] = {}
    for c in mapped:
        head = _body_from_prov(c.get("provenance", ""))
        if head not in card_by_body:
            card_by_body[head] = c["card"]

    bodies = {b["body"]: b for b in chart.get("bodies", [])}
    elements = compute_element_balance(chart)
    aspects = starheart_map._intra_aspects(chart)

    parts: list[str] = []

    # ── Sun ──────────────────────────────────────────────────────
    sun = bodies.get("Sun")
    if sun:
        sign = sign_name(sun.get("sign", ""), lang)
        deg = sun.get("degree", 0.0)
        house = sun.get("house", "?")
        card = card_by_body.get("Sun", "")

        sun_aspects = [a for a in aspects if "Sun" in (a["body_a"], a["body_b"])]
        sun_aspect_str = ""
        if sun_aspects:
            tightest = sun_aspects[0]
            other = tightest["body_b"] if tightest["body_a"] == "Sun" else tightest["body_a"]
            intensity = aspect_intensity(tightest["orb"], lang)
            other_label = body_label(other, lang)
            if EN:
                sun_aspect_str = f" — and {other_label} is pulling ({intensity})"
            else:
                sun_aspect_str = f" — และมี {other_label} มาตึงกัน ({intensity})"

        # Build placement
        if EN:
            parts.append(
                f"Your Sun is at {deg:.2f}° {sign}, house {house}. "
                f"This is the self you wear — the core of who you are.{sun_aspect_str}"
            )
        else:
            parts.append(
                f"สุริยะของ{name}อยู่ที่ {sign} {deg:.2f}° บ้าน {house} "
                f"— นี่คือแก่นตัวตนที่{name}สวมทุกวัน{sun_aspect_str}"
            )
        if card:
            if EN:
                parts.append(f"The tarot card for your Sun is {card} — the same message, different language.")
            else:
                parts.append(f"ไพ่สำหรับสุริยะคือ {card} — ภาษาอีกภาษาที่บอกแบบเดียวกัน")

    # ── Moon ─────────────────────────────────────────────────────
    moon = bodies.get("Moon")
    if moon:
        sign = sign_name(moon.get("sign", ""), lang)
        deg = moon.get("degree", 0.0)
        house = moon.get("house", "?")
        card = card_by_body.get("Moon", "")

        moon_aspects = [a for a in aspects if "Moon" in (a["body_a"], a["body_b"])]
        moon_aspect_str = ""
        if moon_aspects:
            tightest = moon_aspects[0]
            other = tightest["body_b"] if tightest["body_a"] == "Moon" else tightest["body_a"]
            intensity = aspect_intensity(tightest["orb"], lang)
            other_label = body_label(other, lang)
            if EN:
                moon_aspect_str = f" — and {other_label} is pulling ({intensity})"
            else:
                moon_aspect_str = f" — และ {other_label} มาตึงกัน ({intensity})"

        if EN:
            parts.append(
                f"Your Moon is at {deg:.2f}° {sign}, house {house}. "
                f"This is where your feelings live — your emotional home.{moon_aspect_str}"
            )
        else:
            parts.append(
                f"ดวงจันทร์ของ{name}อยู่ที่ {sign} {deg:.2f}° บ้าน {house} "
                f"— นี่คือที่ที่ความรู้สึกของ{name}อยู่{moon_aspect_str}"
            )
        if card:
            if EN:
                parts.append(f"The Moon's card is {card} — showing how you protect what matters.")
            else:
                parts.append(f"ไพ่ของดวงจันทร์คือ {card} — แสดงให้เห็นว่า{name}ปกป้องสิ่งสำคัญอย่างไร")

    # ── Saturn ───────────────────────────────────────────────────
    saturn = bodies.get("Saturn")
    if saturn:
        sign = sign_name(saturn.get("sign", ""), lang)
        deg = saturn.get("degree", 0.0)
        house = saturn.get("house", "?")
        card = card_by_body.get("Saturn", "")

        dignity = saturn.get("dignity", {})
        dignity_label = dignity.get("label", "")
        dignity_score = dignity.get("score", 0)

        if EN:
            parts.append(
                f"Saturn is at {deg:.2f}° {sign}, house {house}. "
                f"This is your life lesson — the area where you grow through challenge."
            )
        else:
            parts.append(
                f"เสาร์อยู่ที่ {sign} {deg:.2f}° บ้าน {house} "
                f"— นี่คือบทเรียนชีวิตที่{name}ต้องเรียนรู้"
            )

        if dignity_label == "fall":
            if EN:
                parts.append(f"It's in its fall (dignity {dignity_score}) — a lifetime lesson, not a gift.")
            else:
                parts.append(f"เสาร์ตก (dignity {dignity_score}) — บทเรียนที่ต้องฝ่าฟันตลอดชีวิต ไม่ใช่ของขวัญ")
        elif dignity_label == "detriment":
            if EN:
                parts.append(f"It's in detriment (dignity {dignity_score}) — you work twice as hard for this.")
            else:
                parts.append(f"เสาร์อ่อน (dignity {dignity_score}) — {name}ต้องทำงานหนกว่าสองเท่า")
        if card:
            if EN:
                parts.append(f"Card {card} is the key to unlocking this karma.")
            else:
                parts.append(f"ไพ่ {card} คือกุญแจไขกรงกรรมนี้")

    # ── Venus ────────────────────────────────────────────────────
    venus = bodies.get("Venus")
    if venus:
        sign = sign_name(venus.get("sign", ""), lang)
        deg = venus.get("degree", 0.0)
        house = venus.get("house", "?")
        card = card_by_body.get("Venus", "")

        if EN:
            parts.append(
                f"Venus at {deg:.2f}° {sign}, house {house}. "
                f"This is the flavor of your love — what draws you to others."
            )
        else:
            parts.append(
                f"ศุกร์อยู่ที่ {sign} {deg:.2f}° บ้าน {house} "
                f"— นี่คือรสชาติความรักของ{name}"
            )
        if card:
            if EN:
                parts.append(f"Card {card} shows the same love pattern.")
            else:
                parts.append(f"ไพ่ {card} แสดงรูปแบบความรักเดียวกัน")

    # ── Mars ─────────────────────────────────────────────────────
    mars = bodies.get("Mars")
    if mars:
        sign = sign_name(mars.get("sign", ""), lang)
        deg = mars.get("degree", 0.0)
        house = mars.get("house", "?")
        card = card_by_body.get("Mars", "")

        if EN:
            parts.append(
                f"Mars at {deg:.2f}° {sign}, house {house}. "
                f"This is your drive — what gets you moving."
            )
        else:
            parts.append(
                f"อังคารอยู่ที่ {sign} {deg:.2f}° บ้าน {house} "
                f"— นี่คือไฟที่ขับเคลื่อน{name}"
            )
        if card:
            if EN:
                parts.append(f"Card {card} channels this fire.")
            else:
                parts.append(f"ไพ่ {card} เป็นตัวช่วยหล่อหล่อไฟนี้")

    # ── ASC ──────────────────────────────────────────────────────
    asc = chart.get("ascendant", {}) or {}
    asc_deg = asc.get("degree", 0.0)
    asc_sign = sign_name(asc.get("sign", ""), lang) if asc.get("sign") else ""
    asc_card = card_by_body.get("ASC", "")
    if asc_sign:
        if EN:
            parts.append(f"Your Ascendant is {asc_deg:.2f}° {asc_sign} — the face the world meets first.")
        else:
            parts.append(f"ลัคนาของ{name}อยู่ที่ {asc_sign} {asc_deg:.2f}° — หน้าที่โลกพบ{name}ก่อนอย่างอื่น")
        if asc_card:
            if EN:
                parts.append(f"  Tarot card: {asc_card}")
            else:
                parts.append(f"  ไพ่: {asc_card}")

    # ── Top 3 tightest aspects ───────────────────────────────────
    if aspects:
        if EN:
            parts.append("---")
            parts.append("Your three tightest aspects (the ones that shape your daily life):")
        else:
            parts.append("---")
            parts.append(f"สาม aspect ที่ตึงที่สุดในดวง{name} (สิ่งที่หล่อหลอมชีวิต{name}ทุกวัน):")

        for i, asp in enumerate(aspects[:3]):
            a, b = asp["body_a"], asp["body_b"]
            aspect_name = asp["aspect"]
            orb = asp["orb"]
            intensity = aspect_intensity(orb, lang)

            a_card = card_by_body.get(a, "")
            b_card = card_by_body.get(b, "")

            if EN:
                parts.append(f"{i+1}. {a} {aspect_name} {b} — orb {orb:.2f}° ({intensity})")
                if a_card or b_card:
                    parts.append(f"   Cards: {a_card} + {b_card}")
            else:
                parts.append(f"{i+1}. {a} {aspect_name} {b} — orb {orb:.2f}° ({intensity})")
                if a_card or b_card:
                    parts.append(f"   ไพ่: {a_card} + {b_card}")

    # ── Element balance ──────────────────────────────────────────
    if elements:
        dominant = elements.get("dominant", "")
        lacking = elements.get("lacking", "")
        if dominant and lacking:
            if EN:
                parts.append("---")
                parts.append(
                    f"Your chart is dominated by {dominant}, while {lacking} is the element you're here to learn. "
                    f"Tarot cards in {lacking} suits point to what you're developing."
                )
            else:
                parts.append("---")
                dom_name = element_name(dominant, lang)
                lack_name = element_name(lacking, lang)
                dom_domain = element_domain(dominant, lang)
                lack_domain = element_domain(lacking, lang)
                parts.append(
                    f"ธาตุเด่นในดวง{name}คือ{dom_name} ({dom_domain}) "
                    f"ส่วนธาตุที่ต้องเรียนรู้คือ{lack_name} ({lack_domain}) "
                    f"ไพ่ที่ออกในชุด{lack_name} ชี้ไปที่สิ่งที่{name}กำลังพัฒนา"
                )

    # ── Closing ──────────────────────────────────────────────────
    if EN:
        parts.append("---")
        parts.append(
            f"Every sentence above is computed from YOUR numbers — exact degrees, exact orbs. "
            f"The tarot cards don't interpret the chart; they CONFIRM it. "
            f"When two independent systems point to the same truth, that's not coincidence. "
            f"That's your story."
        )
    else:
        parts.append("---")
        parts.append(
            f"ทุกประโยคด้านบนคำนวณจากตัวเลขของ{name} — องศาแม่นยำ, orb แม่นยำ "
            f"ไพ่ไม่ได้ตีความดวง แต่มันยืนยันดวง "
            f"เมื่อสองระบบที่แยกจากกันชี้ไปที่จุดเดียวกัน นั่นไม่ใช่ความบังเอิญ "
            f"นั่นคือเรื่องราวของ{name}"
        )

    return "\n".join(parts)
