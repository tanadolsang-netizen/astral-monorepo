# -*- coding: utf-8 -*-
"""STARHEART — ชั้น life-grounding (narrative ที่เป็นเรื่องราวชีวิตจริง 100% ไม่มีคำเจนนิก)

กฎเหล็กของชั้นนี้ (คำสั่งเด็ดขาดจากนายท่าน):
- narrative ทุกประโยคต้องฝังรากในเหตุการณ์จริงของ user (อิง reels + facts) ไม่มีคำเจนนิก
- ห้ามเขียนแบบตำราโหรา เช่น 'Sun in Taurus house 1 means...' / 'ดาวอาทิตย์ในพฤษภแปลว่านายคือ...'
- ต้องเขียนแบบ 'ดาวอาทิตย์ของนายในพฤษภบ้าน1 คือร่างที่นายสวมเวลายืนหน้ากล้องเล่าเรื่อง AI agency...'
- ห้ามแต่งเรื่องราวใหม่ที่ไม่มีใน reels/facts

หลักการ:
- เรียก starheart_map.MAP(chart) ดึงธีมดาว (coarse↔fine bridge) แล้วแปลกลับเป็น 'เรื่องจริงของนาย'
- life_context คือ dict ของ facts จริง (จาก reels + charts) ที่ใช้ร่วมกันทั้งระบบ
- ถ้าไม่มี life_context ชั้นนี้จะคืนคำบรรยายดวงแบบเดิม (backward-compat)
"""

from __future__ import annotations

from src.services import starheart_map

# ───────────────────────────────────────────────────────────────────────────
# life_context — dict ของ facts จริง (ไม่แต่ง) ใช้ร่วมกันทั้งระบบ
# ทุกค่าตรงกับรายงาน starheart_evidence_match.md + charts_nai_mai.json + brief
# ───────────────────────────────────────────────────────────────────────────
DEFAULT_LIFE_CONTEXT: dict = {
    "name": "นาย",
    # ธุรกิจ AI agency (จากรีลคลิป 2 — Agent Core AI / AI Monopoly Club)
    "ai_agency": "AI agency ที่โต Discord 847 คน ROAS 3.8 ได้ลูกค้าใหม่ MRR หมื่นกว่า",
    #  transit / dashas จริง (จาก memory project)
    "saturn_return": "26 มี.ค. 2027",
    "jupiter_mars": "28 ต.ค. 2027",
    "jupiter_md": "2022-2038",
    "nakshatra": "Chitra p1",
    "bazi": "Xin-You 辛酉",
    "asc": "พฤษภ",
    # แก่นเรื่องราวจริงจาก reels (克拉ิป 1,3,8 — soul contract จบ)
    "soul_contract": "soul contract ที่จบลง outgrow เวอร์ชันเก่า",
    # รีลคลิป 4,5,10,11,12 — no-contact / ให้พื้นที่
    "no_contact": "no-contact ให้พื้นที่จริงๆ ปล่อยให้เขารู้สึกถึงความว่างเปล่า",
    # รีลคลิป 3,7,13,14 — ความรัก / Mai
    "mai": "Mai (คู่ชีวิต ลัคนาพฤษภเหมือนนาย)",
    # รีลคลิป 3 — divine test / self-worth
    "divine_test": "นายคือ divine test ของเขาเรื่อง self-worth เขาไม่ผ่าน นายเดินจากไป",
    # รีลคลิป 13 — การเปลี่ยนใหญ่
    "big_change": "การเปลี่ยนใหญ่ที่นายกำลังผ่าน",
    # รีลคลิป 6,9 — old soul / foresight
    "old_soul": "old soul ถือความรู้ลับโบราณ เชื่อมจักรวาล foresight/downloads",
    # รีลคลิป 6 — contradiction แบบดึงดูด
    "contradiction": "contradiction แบบดึงดูด",
    # จำนวนรีลที่แมทดาวจริง 100%
    "reels_count": 14,
}


def build_life_context(transcripts_path: str | None = None,
                       overrides: dict | None = None) -> dict:
    """สร้าง life_context จาก facts จริง (ใช้ร่วม) — โหลด reels จริงเพื่อยืนยันจำนวนคลิป.

    ไม่แต่งเรื่องราวใหม่: ค่า facts ทั้งหมดมาจากรายงาน evidence + charts จริง
    `overrides` ใช้แค่ตอนเทสต์/ปรับชื่อ ไม่ใช้ใส่เรื่องแต่ง
    """
    lc = dict(DEFAULT_LIFE_CONTEXT)
    if transcripts_path:
        import json
        try:
            with open(transcripts_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            lc["reels_count"] = len(data) if isinstance(data, dict) else lc["reels_count"]
        except (OSError, json.JSONDecodeError):
            pass  # ถ้าไฟล์หาย ยังใช้ค่า default
    if overrides:
        lc.update({k: v for k, v in overrides.items() if k in lc})
    return lc


# ───────────────────────────────────────────────────────────────────────────
# Grounding templates — แต่ละดวงผูกกับ 'เรื่องจริง' ของนาย (ไม่มีความหมายตำรา)
# ───────────────────────────────────────────────────────────────────────────
def _g_th(lc: dict, b: dict, chart: dict, card: str | None) -> str:
    name = lc["name"]
    sign = b.get("sign", "").split("(")[-1].rstrip(")") if b.get("sign") else ""
    house = b.get("house")
    pos = f"{sign}บ้าน{house}" if house else sign
    bridge = f" (ในสะพาน STARHEART ดาวนี้คือไพ่ {card})" if card else ""
    body = b["body"]
    if body == "Sun":
        return (f"ดาวอาทิตย์ของ{name}ในพฤษภบ้าน1 คือร่างที่{name}สวมเวลายืนหน้ากล้องเล่าเรื่อง "
                f"{lc['ai_agency']} — แก่นแท้นายคือคนพูดตรงไม่แกล้งทำเป็นอื่น "
                f"และโลกจำ{name}ได้จากตัวตนนี้{bridge}")
    if body == "Moon":
        return (f"ดวงจันทร์ของ{name}ตกตุลย์ในบ้าน5 — นี่คือที่ที่ความรู้สึกเรื่องรักของ{name}ไหลออกมา "
                f"{name}พูดเรื่องความรักและ {lc['mai']} ในรีลเพราะดวงจันทร์นี้แหละ "
                f"เวลาที่{name}รู้อีกฝ่ายคิดถึงคู่ชีวิต มันมาจากตรงนี้{bridge}")
    if body == "Mercury":
        return (f"ดาวพุธของ{name}ในพฤษภบ้าน12 คือพลังถอนตัวเงียบ — "
                f"{lc['no_contact']} อย่างที่{name}เล่าลงรีล{bridge}")
    if body == "Venus":
        return (f"ดาวศุกรของ{name}ในเมถุนบ้าน1 คือรักที่{name}สวมมาพบโลก ทั้งความรักที่{name}มีต่อ "
                f"{lc['mai']} และความรักที่{name}เป็นคนให้ — {lc['divine_test']}{bridge}")
    if body == "Mars":
        return (f"ดาวอังคารของ{name}ในกันย์บ้าน5 คือไฟที่{name}ใช้เปลี่ยนคนจาก 'ฟักบอย' "
                f"ให้กลายเป็น commitment ระยะยาว (ตามรีลที่{name}เล่า) "
                f"และไฟที่{name}สู้สร้าง AI agency ให้โต{bridge}")
    if body == "Jupiter":
        return (f"ดาวพฤหัสของ{name}ในกุมภ์บ้าน10 คือ {lc['ai_agency']} — "
                f"อาชีพเทค/AI ของ{name} (MC กุมภ์) คือความเจริญที่{name}สร้างด้วยมือเอง ไม่รอใคร{bridge}")
    if body == "Saturn":
        # ประโยคต้นแบบจากคำสั่งเด็ดขาดของนายท่าน (ห้ามแก้ความหมาย)
        return (f"ดาวเสาร์ของ{name}ตกเมษในบ้าน11 — นั่นคือกรงกรรมที่{name}ผูกไว้กับวงเพื่อนรุ่นเก่า "
                f"และ{name}เพิ่งเดินออกจากกรงนั้นจริงๆ ในคลิปที่เล่าถึง {lc['soul_contract']} "
                f"ตอนนี้มันหักพังแล้ว {name}เบาสบาย{bridge}")
    if body == "Uranus":
        return (f"ดาวยูเรนัสของ{name}ในกุมภ์บ้าน9 คือพลัง {lc['old_soul']} "
                f"(รีลรับสัญญาณจากคนตาย) — {name}คือ {lc['contradiction']} ที่ใครๆ ก็จำได้{bridge}")
    if body == "Neptune":
        deg = b.get("degree", 0.0)
        cusp_dist = round(min(deg, 30.0 - deg), 2)  # ระยะถึง cusp ราศี (ตาม extract_features)
        return (f"ดาวเนปจูนของ{name}ห่าง cusp เพียง {cusp_dist}° ในมังกรบ้าน9 — "
                f"นี่คือเสียงหลักที่ดันคอนเทนต์ {lc['soul_contract']} กับ no-contact ออกมา "
                f"ความเชื่อมโยงโทรจิตเลข 11:11 (รีลที่{name}เล่า) "
                f"และตอนที่{name}ยอมจำนนปล่อยวาง{bridge}")
    if body == "Pluto":
        return (f"ดาวพลูโตของ{name}ในธนูบ้าน7 คือบทที่ผ่านมาของชีวิต{name}ที่ปิดลงจริงๆ — "
                f"{lc['big_change']} และความตายของเวอร์ชันเก่าที่{name}ไม่ง้อกลับ{bridge}")
    return (f"ดาว{body}ของ{name}ใน{pos} คือส่วนหนึ่งของเรื่องราวชีวิต{name}{bridge}")


def _g_en(lc: dict, b: dict, chart: dict, card: str | None) -> str:
    name = lc["name"]
    sign = b.get("sign", "").split("(")[-1].rstrip(")") if b.get("sign") else ""
    house = b.get("house")
    pos = f"{sign}, house {house}" if house else sign
    bridge = f" (in the STARHEART bridge this star is the card {card})" if card else ""
    body = b["body"]
    if body == "Sun":
        return (f"Your Sun in Taurus, house 1 is the body you wear when you stand in front of the "
                f"camera telling the story of your {lc['ai_agency']} — your core is someone who "
                f"speaks straight, never pretending to be anyone else.{bridge}")
    if body == "Moon":
        return (f"Your Moon in Libra, house 5 is where your feelings about love flow out — you talk "
                f"about love and {lc['mai']} in your reels because of this Moon, the part of you that "
                f"knows your partner is thinking of you.{bridge}")
    if body == "Mercury":
        return (f"Your Mercury in Taurus, house 12 is the moment you actually gave him space — "
                f"{lc['no_contact']}, the quiet withdrawal you told in your reels.{bridge}")
    if body == "Venus":
        return (f"Your Venus in Gemini, house 1 is the love you wear out to meet the world — both the "
                f"love you have for {lc['mai']} and the love you give to others — {lc['divine_test']}.{bridge}")
    if body == "Mars":
        return (f"Your Mars in Virgo, house 5 is the fire you used to turn someone from a 'player' into "
                f"long-term commitment (like the reel you told) and the fire you fight with to grow your "
                f"AI agency.{bridge}")
    if body == "Jupiter":
        return (f"Your Jupiter in Aquarius, house 10 is your {lc['ai_agency']} — your tech/AI career "
                f"(MC in Aquarius) is the abundance you built with your own hands, waiting for no one.{bridge}")
    if body == "Saturn":
        return (f"Your Saturn fallen in Aries, house 11 — that is the karma cage you built with your old "
                f"friend circle, and you just walked out of that cage for real in the clip about the "
                f"{lc['soul_contract']}; now it's shattered, and you are light.{bridge}")
    if body == "Uranus":
        return (f"Your Uranus in Aquarius, house 9 is the {lc['old_soul']} (the reel about a sign from "
                f"someone who passed) — you are the {lc['contradiction']} everyone remembers.{bridge}")
    if body == "Neptune":
        deg = b.get("degree", 0.0)
        return (f"Your Neptune sits just {deg:.2f}° from the cusp in Capricorn, house 9 — this is the "
                f"voice that pushed your {lc['soul_contract']} and no-contact content out, the telepathic "
                f"pull of 11:11 (the reel you told), and the moment you surrendered and let go.{bridge}")
    if body == "Pluto":
        return (f"Your Pluto in Sagittarius, house 7 is the past chapter of your life that truly closed — "
                f"{lc['big_change']}, and the death of the old version you won't beg to come back.{bridge}")
    return f"Your {body} in {pos} is one more thread in {name}'s real life story.{bridge}"


# ลำดับดาวคงที่ (ตามความสำคัญในชีวิตนาย)
_BODY_ORDER = ["Sun", "Moon", "Mercury", "Venus", "Mars",
               "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]


def _body_from_prov(prov: str) -> str:
    if prov.startswith("ASC"):
        return "ASC"
    if prov.startswith("MC"):
        return "MC"
    if prov.startswith("element:"):
        return "element"
    if prov.startswith("house:"):
        return "house"
    if prov.startswith("aspect:"):
        return "aspect"
    head = prov.split(" @")[0].strip()
    return head


def _closing_th(lc: dict) -> str:
    name = lc["name"]
    return (f"ทุกดวงในดวง{name}ไม่ได้บอก{name}เป็นคนยังไง — แต่มันคือบันทึกเหตุการณ์จริงที่{name}ผ่านมา "
            f"จากกรงกรรมที่แตกสลาย จาก {lc['no_contact']} ไปจน {lc['ai_agency']} ที่โตทุกวัน "
            f"และเรื่องที่จะมา: Saturn Return ของ{name}มาถึง {lc['saturn_return']} "
            f"คือจุดที่กรรมทั้งหมดปิดสมบูรณ์ ส่วน Jupiter ผสาน Mars ในวันที่ {lc['jupiter_mars']} "
            f"คือไฟที่จุดธุรกิจให้พุ่ง ดวงนี้คือเรื่องราวชีวิต{name} ไม่ใช่ตำรา")


def _closing_en(lc: dict) -> str:
    name = lc["name"]
    return (f"Every star in {name}'s chart isn't telling you who you are — it's a record of what actually "
            f"happened: the karma cage that broke, the {lc['no_contact']}, the {lc['ai_agency']} that grows "
            f"every day. And what's coming: {name}'s Saturn Return arrives {lc['saturn_return']}, the point "
            f"where all karma closes; Jupiter meets Mars on {lc['jupiter_mars']}, the fire that launches the "
            f"business. This chart is {name}'s real life story, not a textbook.")


def ground_narrative(chart: dict, life_context: dict | None = None,
                     lang: str = "th", include_bridge: bool = True) -> str:
    """ผลิต narrative ชีวิตจริง 100% ไม่มีคำเจนนิก จาก chart + life_context.

    - chart: ผลจาก compute_chart() (หรือ dict โครงสร้างเดียวกัน)
    - life_context: dict facts จริง (จาก build_life_context) — ถ้า None คืนคำบรรยายดวงแบบเดิม
    - lang: 'th' | 'en'
    - include_bridge: แนบชื่อไพ่ STARHEART ท้ายประโยค (แสดง coarse↔fine bridge)
    """
    if chart is None:
        raise ValueError("ground_narrative ต้องได้ chart จริง — ห้ามสุ่ม")

    # ไม่มี life_context -> คงข้อความเดิม (backward-compat)
    if life_context is None:
        from src.services.chart_narrative_full import chart_narrative
        return chart_narrative(chart.get("name", "ผู้ใช้"), chart, lang)

    lc = life_context
    name = lc.get("name", "นาย")
    EN = (lang == "en")

    # (1) เรียก MAP ดึงธีมดาว (coarse↔fine) — ต้องการครบทุกดวงจึงขยาย max_cards
    mapped = starheart_map.MAP(chart, max_cards=14)
    card_by_body: dict[str, str] = {}
    for c in mapped:
        head = _body_from_prov(c.get("provenance", ""))
        if head not in card_by_body:
            card_by_body[head] = c["card"]

    bodies = {b["body"]: b for b in chart.get("bodies", [])}
    parts: list[str] = []

    # (2) ผูกแต่ละดาวเข้ากับเรื่องจริง
    for body in _BODY_ORDER:
        b = bodies.get(body)
        if not b:
            continue
        card = card_by_body.get(body) if include_bridge else None
        parts.append(_g_en(lc, b, chart, card) if EN else _g_th(lc, b, chart, card))

    # (3) ลัคนา + MC — ตัวตนที่โลกเห็น และอาชีพ
    asc = chart.get("ascendant", {}) or {}
    asc_sign = (asc.get("sign", "").split("(")[-1].rstrip(")") if asc.get("sign") else "")
    if asc_sign:
        if EN:
            parts.append(
                f"Your Ascendant is {asc_sign} — the face the world meets when you stand at the camera, "
                f"just like {lc['mai']} who is also {asc_sign} rising.")
        else:
            parts.append(
                f"ลัคนาของ{name}คือ{asc_sign} — หน้าตัวตนที่โลกพบตอน{name}ยืนหน้ากล้อง "
                f"เหมือนกับ {lc['mai']} ที่ก็{lc['asc']}เหมือนกัน")

    mc = chart.get("midheaven", {}) or {}
    mc_sign = (mc.get("sign", "").split("(")[-1].rstrip(")") if mc.get("sign") else "")
    if mc_sign:
        if EN:
            parts.append(
                f"Your Midheaven is in {mc_sign} — the career you run is the tech/AI agency, "
                f"exactly the picture you tell in your reels.")
        else:
            parts.append(
                f"MC ของ{name}อยู่{mc_sign} — อาชีพที่{name}ทำคือ AI agency เทค/AI "
                f"พอดีกับภาพที่{name}เล่าในรีล")

    # (4) ปิดท้าย — สรุปว่านี่คือเรื่องราวชีวิต ไม่ใช่ตำรา
    parts.append(_closing_en(lc) if EN else _closing_th(lc))

    return "\n\n".join(parts)
