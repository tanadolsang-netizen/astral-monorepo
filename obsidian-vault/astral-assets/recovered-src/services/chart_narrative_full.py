"""Full bilingual (th/en) natal-chart narrative — deep, precise, long-form.

Single source for the premium PDF's chart section. Computes:
  - each planet: sign + degree + house + dignity + lived expression (long)
  - houses 1–12 themes touched by the chart
  - intra-chart aspects (conjunction/square/trine/sextile/opposition)
  - elemental balance (fire/earth/air/water)

Returns one merged prose block per language (no disjoint section labels),
written in a reader's warm, precise voice.
"""
from __future__ import annotations

from src.services.chart_service import compute_chart
from src.services.aspects import ASPECTS, ORBS, _angular_sep
from src.services.element_service import compute_element_balance, _DOMAIN as _ELEMENT_DOMAIN_TH

# ── Thai / English shared maps ──
_SIGN_TH = {
    "เมษ(Aries)": "เมษ", "พฤษภ(Taurus)": "พฤษภ", "เมถุน(Gemini)": "เมถุน",
    "กรกฎ(Cancer)": "กรกฎ", "สิงห์(Leo)": "สิงห์", "กันย์(Virgo)": "กันย์",
    "ตุลย์(Libra)": "ตุลย์", "พิจิก(Scorpio)": "พิจิก", "ธนู(Sagittarius)": "ธนู",
    "มังกร(Capricorn)": "มังกร", "กุมภ์(Aquarius)": "กุมภ์", "มีน(Pisces)": "มีน",
}
_SIGN_EN = {
    "เมษ(Aries)": "Aries", "พฤษภ(Taurus)": "Taurus", "เมถุน(Gemini)": "Gemini",
    "กรกฎ(Cancer)": "Cancer", "สิงห์(Leo)": "Leo", "กันย์(Virgo)": "Virgo",
    "ตุลย์(Libra)": "Libra", "พิจิก(Scorpio)": "Scorpio", "ธนู(Sagittarius)": "Sagittarius",
    "มังกร(Capricorn)": "Capricorn", "กุมภ์(Aquarius)": "Aquarius", "มีน(Pisces)": "Pisces",
}
_HOUSE_TH = {
    1: "บ้านที่หนึ่ง — รูปกายและบุคลิกภายนอก", 2: "บ้านที่สอง — ทรัพย์สินและค่านิยม",
    3: "บ้านที่สาม — การสื่อสารและพี่น้อง", 4: "บ้านที่สี่ — รากฐานและครอบครัว",
    5: "บ้านที่ห้า — ความรักและการสร้างสรรค์", 6: "บ้านที่หก — สุขภาพและการงานประจำ",
    7: "บ้านที่เจ็ด — คู่ครองและหุ้นส่วน", 8: "บ้านที่แปด — การแปลงโฉมและทรัพย์มรดก",
    9: "บ้านที่เก้า — ปรัชญาและการเดินทางไกล", 10: "บ้านที่สิบ — อาชีพและชื่อเสียง",
    11: "บ้านที่สิบเอ็ด — มิตรและความปรารถนา", 12: "บ้านที่สิบสอง — จิตใต้สำนึกและการสละ",
}
_HOUSE_EN = {
    1: "House 1 — physical body and outer persona", 2: "House 2 — possessions and values",
    3: "House 3 — communication and siblings", 4: "House 4 — roots and family",
    5: "House 5 — love and creativity", 6: "House 6 — health and daily work",
    7: "House 7 — partner and partnerships", 8: "House 8 — transformation and legacy",
    9: "House 9 — philosophy and long journeys", 10: "House 10 — career and reputation",
    11: "House 11 — friends and wishes", 12: "House 12 — subconscious and surrender",
}
# planet human role
_PLANET_TH = {
    "Sun": "อาทิตย์คือแก่นแท้และจุดมุ่งหมายในชีวิต",
    "Moon": "ดวงจันทร์คือความรู้สึกภายในและความต้องการความปลอดภัย",
    "Mercury": "ดาวพุธคือวิธีคิดและการสื่อสาร",
    "Venus": "ดาวศุกรคือความรักและสิ่งที่ดึงดูดใจ",
    "Mars": "ดาวอังคารคือสัญชาตญาณการลงมือทำและพลังขับเคลื่อน",
    "Jupiter": "ดาวพฤหัสคือปัญญาและความเจริญเติบโต",
    "Saturn": "ดาวเสาร์คือวินัย บทเรียน และโครงสร้างชีวิต",
}
_PLANET_EN = {
    "Sun": "The Sun is your core essence and life purpose",
    "Moon": "The Moon is your inner feeling and need for safety",
    "Mercury": "Mercury is how you think and communicate",
    "Venus": "Venus is love and what draws you in",
    "Mars": "Mars is your drive and how you take action",
    "Jupiter": "Jupiter is wisdom and growth",
    "Saturn": "Saturn is discipline, lessons, and life structure",
}
_DIGNITY_TH = {
    "domicile": "อยู่ในเรือนเกษตรตนเอง (แข็งแรงมั่นคง)",
    "exaltation": "อยู่ในจุดเผาเอาหน้า (เจริญสุดขีด)",
    "detriment": "อยู่ในเรือนศัตรู (ต้องระวังด้านอ่อนไหว)",
    "fall": "อยู่ในจุดตก (พลังถูกบีบให้ต้องระวัง)",
    "peregrine": "เป็นดาวเดินทาง (ทำหน้าที่เป็นกลาง)",
}
_DIGNITY_EN = {
    "domicile": "in its own domicile (strong and steady)",
    "exaltation": "in its exaltation (thriving at its peak)",
    "detriment": "in its detriment (a tender spot to watch)",
    "fall": "in its fall (power squeezed, handle with care)",
    "peregrine": "peregrine (acting in a neutral role)",
}
_ASPECT_TH = {
    "conjunction": "ร่วมกัน", "sextile": "หกเหลี่ยม", "square": "สี่เหลี่ยม",
    "trine": "สามเหลี่ยม", "opposition": "ตรงข้าม",
}
_ASPECT_EN = {
    "conjunction": "in conjunction", "sextile": "in sextile", "square": "in square",
    "trine": "in trine", "opposition": "in opposition",
}
_ELEMENT_TH = {"Fire": "ไฟ", "Earth": "ดิน", "Air": "ลม", "Water": "น้ำ"}
_ELEMENT_EN = {"Fire": "Fire", "Earth": "Earth", "Air": "Air", "Water": "Water"}
_ELEMENT_DOMAIN_TH = {
    "Fire": "ความกระตือรือร้นและการริเริ่ม", "Earth": "ความมั่นคงและการลงมือทำ",
    "Air": "ความคิดและการเชื่อมโยง", "Water": "ความรู้สึกและจินตนาการ",
}


def _intra_aspects(chart: dict) -> list[dict]:
    bodies = [b for b in chart["bodies"] if b["body"] in _PLANET_TH]
    res = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            a, b = bodies[i], bodies[j]
            sep = _angular_sep(a["absolute_deg"], b["absolute_deg"])
            for name, ang in ASPECTS.items():
                orb = abs(sep - ang)
                if orb <= ORBS[name]:
                    res.append({
                        "a": a["body"], "b": b["body"], "aspect": name,
                        "orb": round(orb, 1),
                    })
                    break
    res.sort(key=lambda r: r["orb"])
    return res


def chart_narrative(name: str, chart: dict, lang: str = "th",
                    life_context: dict | None = None) -> str:
    """บรรยายดวงแบบเต็ม (th/en).

    ถ้ามี life_context (facts จริงจาก reels) จะเรียก starheart_narrative.ground_narrative
    เพื่อผลิต narrative ชีวิตจริง 100% ไม่มีคำเจนนิก — ถ้าไม่มี คงข้อความดั้งเดิม (backward-compat)
    """
    if life_context is not None:
        from src.services.starheart_narrative import ground_narrative
        ctx = dict(life_context)
        ctx.setdefault("name", name)
        return ground_narrative(chart, ctx, lang)
    EN = (lang == "en")
    sign_of = _SIGN_EN if EN else _SIGN_TH
    house_of = _HOUSE_EN if EN else _HOUSE_TH
    planet_of = _PLANET_EN if EN else _PLANET_TH
    dignity_of = _DIGNITY_EN if EN else _DIGNITY_TH
    aspect_of = _ASPECT_EN if EN else _ASPECT_TH
    element_of = _ELEMENT_EN if EN else _ELEMENT_TH

    bodies = {b["body"]: b for b in chart["bodies"]}
    asc = chart["ascendant"]
    asc_s = sign_of.get(asc["sign"], asc["sign"])
    order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

    parts = []
    if EN:
        parts.append(
            f"{name}'s chart opens with the Ascendant in {asc_s}, the mask the world meets first. "
            "Now let us walk through each planet as a living thread of your story.")
    else:
        parts.append(
            f"ดวงของ{name}เปิดมาด้วยลัคนาอยู่ราศี{asc_s} นี่คือหน้ากากแรกที่โลกพบ "
            f"ต่อไปกระผมจะเล่าดาวแต่ละดวงเป็นเส้นเรื่องที่มีชีวิตของ{name}")

    for ob in order:
        b = bodies.get(ob)
        if not b:
            continue
        s = sign_of.get(b["sign"], b["sign"])
        dign = b.get("dignity", {})
        label = dign.get("label", "peregrine")
        dign_txt = dignity_of.get(label, "")
        house = b["house"]
        house_txt = house_of.get(house, f"House {house}")
        if EN:
            para = (
                f"{planet_of[ob]} sits in {s} at {b['degree']:.1f}°, "
                f"resident in {house_txt} — {dign_txt}. "
                f"This places {ob}'s energy into the arena of {house_txt.split('—')[-1].strip()}, "
                f"so its gifts and lessons show up there in your everyday life."
            )
        else:
            planet_th = {
                "Sun": "อาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
                "Venus": "ดาวศุกร", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัส",
                "Saturn": "ดาวเสาร์",
            }.get(ob, ob)
            para = (
                f"{planet_of[ob]} สถิตในราศี{s} องศา {b['degree']:.1f}° "
                f"พำนักอยู่{house_txt} — {dign_txt} "
                f"จึงส่งพลังของ{planet_th}เข้าไปในเวทีแห่ง{house_txt.split('—')[-1].strip()} "
                f"ให้คุณเห็นทั้งของดีและบทเรียนของมันในชีวิตประจำวัน"
            )
        parts.append(para)

    # aspects (woven in)
    asp = _intra_aspects(chart)
    if asp:
        if EN:
            lines = []
            for r in asp[:5]:
                lines.append(
                    f"{r['a']} and {r['b']} stand {aspect_of[r['aspect']]} "
                    f"(orb {r['orb']}°), a tension or flow that colors how those two parts of you meet.")
            parts.append(
                "Between the planets, a few relationships stand out: " + " ".join(lines))
        else:
            planet_th_map = {
                "Sun": "อาทิตย์", "Moon": "ดวงจันทร์", "Mercury": "ดาวพุธ",
                "Venus": "ดาวศุกร", "Mars": "ดาวอังคาร", "Jupiter": "ดาวพฤหัส",
                "Saturn": "ดาวเสาร์",
            }
            lines = []
            for r in asp[:5]:
                a = planet_th_map.get(r["a"], r["a"])
                b = planet_th_map.get(r["b"], r["b"])
                lines.append(
                    f"{a}และ{b}อยู่{aspect_of[r['aspect']]} "
                    f"(เบี่ยง {r['orb']}°) แรงเสียดทานหรือกระแสนี้หล่อหลอมให้สองส่วนนั้นของ{name}พบกัน")
            parts.append("ระหว่างดาวด้วยกัน มีความสัมพันธ์เด่นๆ เกิดขึ้น เช่น " + " ".join(lines))

    # elemental balance (woven in)
    bal = compute_element_balance(chart)
    dom_key = bal["dominant"].capitalize()
    lac_key = bal["lacking"].capitalize()
    dom_th = {"Fire": "ไฟ", "Earth": "ดิน", "Air": "ลม", "Water": "น้ำ"}.get(dom_key, bal["dominant"])
    lac_th = {"Fire": "ไฟ", "Earth": "ดิน", "Air": "ลม", "Water": "น้ำ"}.get(lac_key, bal["lacking"])
    dom_domain = _ELEMENT_DOMAIN_TH.get(dom_key, bal["dominant"])
    dom_domain_en = {"Fire": "drive and initiative", "Earth": "stability and grounded action",
                     "Air": "thought and connection", "Water": "feeling and intuition"}.get(dom_key, bal["dominant"])
    if EN:
        parts.append(
            f"Elementally, {bal['dominant']} leads your chart while {bal['lacking']} is thinnest. "
            f"{bal['dominant']} brings {dom_domain_en} energy; "
            f"nurturing a little more {bal['lacking']} would round out the picture.")
    else:
        parts.append(
            f"ในมุมธาตุ ธาตุ{dom_th}นำดวงของ{name} ในขณะที่ธาตุ{lac_th}บางที่สุด "
            f"ธาตุ{dom_th}มอบพลังด้าน{dom_domain} "
            f"หากเพิ่มธาตุ{lac_th}เข้าไปอีกเล็กน้อย ภาพรวมจะสมดุลขึ้น")

    return "\n\n".join(parts)
