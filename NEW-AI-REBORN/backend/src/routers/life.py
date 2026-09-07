"""Life Report — unified narrative weaving all astrology systems into one story.

The philosophy: every system (Natal, Vedic, Tarot, Chinese, Bazi) is a different
language describing the SAME life events. When they all point to the same thing,
that's not a coincidence — that's the user's real story showing through.
"""
from datetime import date, time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.services.chart_service import compute_chart
from src.services.element_service import compute_element_balance
from src.services.starheart_map import MAP
from src.services.starheart_narrative import ground_narrative
from src.services.reel_reading import reel_reading
from src.services.narrative_lang import (
    sign_name,
    house_zone,
    element_domain,
    closing_convergence,
    closing_element,
)

router = APIRouter()



class LifeRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    date: date
    time: time
    tz_offset_hours: float = Field(default=7.0)
    lat: float = Field(default=13.7563)
    lon: float = Field(default=100.5018)
    system: str = Field(default="tropical")
    lang: str = Field(default="th")
    question: str = Field(default="")


@router.post("")
async def life_report(req: LifeRequest):
    """Weave all astrology systems into one coherent life narrative."""
    try:
        # 1. Compute natal chart
        chart = compute_chart(
            name=req.name,
            date=req.date,
            time=req.time,
            tz_offset_hours=req.tz_offset_hours,
            lat=req.lat,
            lon=req.lon,
            system=req.system,
        )
        
        if not chart or not chart.get("bodies"):
            raise HTTPException(status_code=400, detail="Chart computation failed")
        
        # 2. STARHEART mapping (chart → tarot, deterministic)
        mapped = MAP(chart, max_cards=14)
        card_by_body = {}
        for c in mapped:
            prov = c.get("provenance", "")
            head = prov.split(" @")[0].strip() if " @" in prov else prov
            if head not in card_by_body:
                card_by_body[head] = c["card"]
        
        # 3. Tarot draw (3-card spread, seeded from chart for determinism)
        seed_value = sum(b.get("absolute_deg", 0) for b in chart.get("bodies", []))
        tarot_result = reel_reading(
            name=req.name,
            spread="three_card",
            seed=int(seed_value * 100) % 10000,
            element_balance=compute_element_balance(chart),
        )
        
        # 4. Grounded narrative (chart-only, no hardcoded facts)
        narrative = ground_narrative(chart, lang=req.lang, user_name=req.name, user_question=req.question)
        
        # 5. Extract key themes from each system
        bodies = {b["body"]: b for b in chart.get("bodies", [])}
        elements = compute_element_balance(chart)
        
        # 6. Build woven themes (where systems agree)
        woven_themes = _weave_themes(chart, tarot_result, card_by_body, req.lang)
        
        return {
            "name": req.name,
            "chart": chart,
            "tarot": tarot_result,
            "starheart_map": mapped,
            "narrative": narrative,
            "themes": woven_themes,
            "elements": elements,
            "caveat": "นี่คือเรื่องราวชีวิตของคุณ ไม่ใช่ตำราโหราศาสตร์ — ทุกระบบชี้มาที่จุดเดียวกัน นั่นไม่ใช่ความบังเอิญ",
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Computation failed: {exc}") from exc


_sign_name_th = lambda s: sign_name(s, "th")

def _weave_themes(chart: dict, tarot_result: dict, card_by_body: dict, lang: str) -> list[dict]:
    """Find where multiple systems point to the same theme — natural language."""
    themes = []
    EN = (lang == "en")
    
    # Sun = core identity
    sun = next((b for b in chart.get("bodies", []) if b["body"] == "Sun"), None)
    if sun:
        sun_card = card_by_body.get("Sun", "")
        deg = sun.get("degree", 0.0)
        sign = _sign_name_th(sun.get("sign", "")) if sun.get("sign") else ""
        house = sun.get("house", "?")
        
        if EN:
            natal_desc = f"Sun at {deg:.2f}° {sign}, house {house}"
            meaning = f"Your Sun is at {deg:.2f}° {sign} — the core of who you are."
            if sun_card:
                meaning += f" The tarot card {sun_card} tells the same story."
        else:
            natal_desc = f"สุริยะ {sign} {deg:.2f}° บ้าน {house}"
            meaning = f"สุริยะอยู่ที่ {sign} {deg:.2f}° — แก่นตัวตนของคุณ"
            if sun_card:
                meaning += f" ไพ่ {sun_card} เล่าเรื่องเดียวกัน"
        
        themes.append({
            "domain": "แก่นตัวตน" if not EN else "Core Identity",
            "natal": natal_desc,
            "tarot": sun_card,
            "meaning": meaning,
        })
    
    # Moon = emotional world
    moon = next((b for b in chart.get("bodies", []) if b["body"] == "Moon"), None)
    if moon:
        moon_card = card_by_body.get("Moon", "")
        deg = moon.get("degree", 0.0)
        sign = _sign_name_th(moon.get("sign", "")) if moon.get("sign") else ""
        house = moon.get("house", "?")
        
        if EN:
            natal_desc = f"Moon at {deg:.2f}° {sign}, house {house}"
            meaning = f"Your Moon is at {deg:.2f}° {sign} — where your feelings live."
            if moon_card:
                meaning += f" Card {moon_card} shows the same emotional pattern."
        else:
            natal_desc = f"จันทร์ {sign} {deg:.2f}° บ้าน {house}"
            meaning = f"ดวงจันทร์อยู่ที่ {sign} {deg:.2f}° — ที่ที่ความรู้สึกอยู่"
            if moon_card:
                meaning += f" ไพ่ {moon_card} แสดงรูปแบบอารมณ์เดียวกัน"
        
        themes.append({
            "domain": "โลกความรู้สึก" if not EN else "Emotional World",
            "natal": natal_desc,
            "tarot": moon_card,
            "meaning": meaning,
        })
    
    # Saturn = life lesson
    saturn = next((b for b in chart.get("bodies", []) if b["body"] == "Saturn"), None)
    if saturn:
        saturn_card = card_by_body.get("Saturn", "")
        deg = saturn.get("degree", 0.0)
        sign = _sign_name_th(saturn.get("sign", "")) if saturn.get("sign") else ""
        house = saturn.get("house", "?")
        
        dignity = saturn.get("dignity", {})
        dignity_label = dignity.get("label", "")
        dignity_score = dignity.get("score", 0)
        zone_desc = house_zone(house, lang)
        
        if EN:
            natal_desc = f"Saturn at {deg:.2f}° {sign}, house {house}"
            meaning = f"Saturn at {deg:.2f}° {sign} — your life lesson."
            if dignity_label == "fall":
                meaning += f" It's in its fall (dignity {dignity_score}) — a lifetime lesson, not a gift."
            elif dignity_label == "detriment":
                meaning += f" It's in detriment (dignity {dignity_score}) — you work twice as hard."
            meaning += f" In house {house}, this speaks of {zone_desc}."
            if saturn_card:
                meaning += f" Card {saturn_card} is the key."
        else:
            natal_desc = f"เสาร์ {sign} {deg:.2f}° บ้าน {house}"
            meaning = f"เสาร์อยู่ที่ {sign} {deg:.2f}° — บทเรียนชีวิต"
            if dignity_label == "fall":
                meaning += f" เสาร์ตก (dignity {dignity_score}) — บทเรียนตลอดชีวิต ไม่ใช่ของขวัญ"
            elif dignity_label == "detriment":
                meaning += f" เสาร์อ่อน (dignity {dignity_score}) — ต้องทำงานหนกว่าสองเท่า"
            meaning += f" ในบ้าน {house} มันพูดถึง{zone_desc}"
            if saturn_card:
                meaning += f" ไพ่ {saturn_card} คือกุญแจ"
        
        themes.append({
            "domain": "บทเรียนชีวิต" if not EN else "Life Lesson",
            "natal": natal_desc,
            "tarot": saturn_card,
            "meaning": meaning,
        })
    
    # Venus = love
    venus = next((b for b in chart.get("bodies", []) if b["body"] == "Venus"), None)
    if venus:
        venus_card = card_by_body.get("Venus", "")
        deg = venus.get("degree", 0.0)
        sign = _sign_name_th(venus.get("sign", "")) if venus.get("sign") else ""
        house = venus.get("house", "?")
        zone_desc = house_zone(house, lang)
        
        if EN:
            natal_desc = f"Venus at {deg:.2f}° {sign}, house {house}"
            meaning = f"Venus at {deg:.2f}° {sign} — the flavor of your love. In house {house}, it speaks of {zone_desc}."
            if venus_card:
                meaning += f" Card {venus_card} shows the same pattern."
        else:
            natal_desc = f"ศุกร์ {sign} {deg:.2f}° บ้าน {house}"
            meaning = f"ศุกร์อยู่ที่ {sign} {deg:.2f}° — รสชาติความรัก ในบ้าน {house} มันพูดถึง{zone_desc}"
            if venus_card:
                meaning += f" ไพ่ {venus_card} แสดงรูปแบบเดียวกัน"
        
        themes.append({
            "domain": "ความรัก" if not EN else "Love",
            "natal": natal_desc,
            "tarot": venus_card,
            "meaning": meaning,
        })
    
    # Mars = drive
    mars = next((b for b in chart.get("bodies", []) if b["body"] == "Mars"), None)
    if mars:
        mars_card = card_by_body.get("Mars", "")
        deg = mars.get("degree", 0.0)
        sign = _sign_name_th(mars.get("sign", "")) if mars.get("sign") else ""
        house = mars.get("house", "?")
        zone_desc = house_zone(house, lang)
        
        if EN:
            natal_desc = f"Mars at {deg:.2f}° {sign}, house {house}"
            meaning = f"Mars at {deg:.2f}° {sign} — your drive. In house {house}, it speaks of {zone_desc}."
            if mars_card:
                meaning += f" Card {mars_card} channels this fire."
        else:
            natal_desc = f"อังคาร {sign} {deg:.2f}° บ้าน {house}"
            meaning = f"อังคารอยู่ที่ {sign} {deg:.2f}° — ไฟที่ขับเคลื่อน ในบ้าน {house} มันพูดถึง{zone_desc}"
            if mars_card:
                meaning += f" ไพ่ {mars_card} หล่อหล่อไฟนี้"
        
        themes.append({
            "domain": "ไฟและการลงมือ" if not EN else "Fire and Drive",
            "natal": natal_desc,
            "tarot": mars_card,
            "meaning": meaning,
        })
    
    return themes

def _narrative_weave(chart: dict, tarot_result: dict, card_by_body: dict, lang: str) -> str:
    """Generate narrative paragraphs from chart + tarot."""
    EN = (lang == "en")
    
    sun = next((b for b in chart.get("bodies", []) if b["body"] == "Sun"), None)
    moon = next((b for b in chart.get("bodies", []) if b["body"] == "Moon"), None)
    saturn = next((b for b in chart.get("bodies", []) if b["body"] == "Saturn"), None)
    
    parts = []
    
    if sun:
        sign = _sign_name_th(sun.get("sign", "")) if sun.get("sign") else ""
        sun_card = card_by_body.get("Sun", "")
        if EN:
            parts.append(f"Your Sun is at {sun.get('degree', 0):.2f}° {sign} — the core of who you are.")
            if sun_card:
                parts.append(f" The tarot card {sun_card} tells the same story.")
        else:
            parts.append(f"สุริยะอยู่ที่ {sign} {sun.get('degree', 0):.2f}° — แก่นตัวตนของคุณ")
            if sun_card:
                parts.append(f" ไพ่ {sun_card} เล่าเรื่องเดียวกัน")
    
    if moon:
        sign = _sign_name_th(moon.get("sign", "")) if moon.get("sign") else ""
        moon_card = card_by_body.get("Moon", "")
        if EN:
            parts.append(f"Your Moon is at {moon.get('degree', 0):.2f}° {sign} — where your feelings live.")
            if moon_card:
                parts.append(f" Card {moon_card} shows the same emotional pattern.")
        else:
            parts.append(f"ดวงจันทร์อยู่ที่ {sign} {moon.get('degree', 0):.2f}° — ที่ที่ความรู้สึกอยู่")
            if moon_card:
                parts.append(f" ไพ่ {moon_card} แสดงรูปแบบอารมณ์เดียวกัน")
    
    if saturn:
        sign = _sign_name_th(saturn.get("sign", "")) if saturn.get("sign") else ""
        saturn_card = card_by_body.get("Saturn", "")
        dignity = saturn.get("dignity", {})
        dignity_label = dignity.get("label", "")
        dignity_score = dignity.get("score", 0)
        if EN:
            parts.append(f"Saturn at {saturn.get('degree', 0):.2f}° {sign} — your life lesson.")
            if dignity_label == "fall":
                parts.append(f" It's in its fall (dignity {dignity_score}) — a lifetime lesson, not a gift.")
        else:
            parts.append(f"เสาร์อยู่ที่ {sign} {saturn.get('degree', 0):.2f}° — บทเรียนชีวิต")
            if dignity_label == "fall":
                parts.append(f" เสาร์ตก (dignity {dignity_score}) — บทเรียนตลอดชีวิต ไม่ใช่ของขวัญ")
        if saturn_card:
            if EN:
                parts.append(f" Card {saturn_card} is the key.")
            else:
                parts.append(f" ไพ่ {saturn_card} คือกุญแจ")
    
    if EN:
        parts.append(f"Every sentence above is computed from YOUR numbers — exact degrees, exact orbs. The tarot cards don't interpret the chart; they CONFIRM it.")
    else:
        parts.append(f"ทุกประโยคด้านบนคำนวณจากตัวเลขของคุณ — องศาแม่นยำ, orb แม่นยำ ไพ่ไม่ได้ตีความดวง แต่มันยืนยันดวง")
    
    return "\n".join(parts)


def _sun_meaning(sun: dict, card: str, lang: str) -> str:
    sign = sun.get("sign", "").split("(")[-1].rstrip(")") if sun.get("sign") else ""
    house = sun.get("house", "")
    if lang == "th":
        return f"ตัวตนแท้ของคุณคือ {sign} ในบ้าน {house} — ไพ่ {card} ชี้ว่านี่คือสิ่งที่คุณมาเพื่อทำในชีวิตนี้"
    return f"Your true self is {sign} in house {house} — the card {card} points to what you came here to do"


def _moon_meaning(moon: dict, card: str, lang: str) -> str:
    sign = moon.get("sign", "").split("(")[-1].rstrip(")") if moon.get("sign") else ""
    house = moon.get("house", "")
    if lang == "th":
        return f"ความรู้สึกของคุณไหลผ่าน {sign} บ้าน {house} — ไพ่ {card} บอกว่าคุณปกป้องหัวใจตัวเองอย่างไร"
    return f"Your feelings flow through {sign} in house {house} — the card {card} shows how you protect your heart"


def _saturn_meaning(saturn: dict, card: str, lang: str) -> str:
    sign = saturn.get("sign", "").split("(")[-1].rstrip(")") if saturn.get("sign") else ""
    house = saturn.get("house", "")
    if lang == "th":
        return f"เสาร์ใน {sign} บ้าน {house} คือกรงกรรมที่คุณผูกไว้ — ไพ่ {card} คือกุญแจไขกรง"
    return f"Saturn in {sign} house {house} is the karma cage you built — the card {card} is the key to unlock it"


def _venus_meaning(venus: dict, card: str, lang: str) -> str:
    sign = venus.get("sign", "").split("(")[-1].rstrip(")") if venus.get("sign") else ""
    house = venus.get("house", "")
    if lang == "th":
        return f"ความรักของคุณมีรสชาติ {sign} บ้าน {house} — ไพ่ {card} คือสิ่งที่คุณกำลังเรียนรู้เรื่องหัวใจ"
    return f"Your love has the flavor of {sign} in house {house} — the card {card} is what you're learning about the heart"
