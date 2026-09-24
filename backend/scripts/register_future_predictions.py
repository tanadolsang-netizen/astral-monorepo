"""ORACLE: pre-register 8 real forward predictions (nai + mai + composite).

All expected_event dates are derived from REAL transits computed with the
project's own ephemeris (skyfield/de421) — no invented stars. Each prediction
is anchored to a MAP() theme (real star -> card provenance) and a concrete
transit conjunction inside the 3-12 month window from 2026-08-31.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

from src.services.ephemeris import earth, eph, ts
from src.services.starheart_map import MAP
from src.services.prediction_log import pre_register

CHARTS_PATH = "C:/AI/workspace-scratch/charts_nai_mai.json"
REPORT_PATH = "C:/AI/workspace-scratch/starheart_future_predictions.md"

charts = json.load(open(CHARTS_PATH))
nai = charts["nai"]
mai = charts["mai"]

# ---- midpoint composite chart (standard composite technique) ----
def _mid(a, b):
    x = (a - b + 180) % 360 - 180
    return (b + x / 2) % 360

def _msign(deg):
    s = ['เมษ(Aries)','พฤษภ(Taurus)','เมถุน(Gemini)','กรกฎ(Cancer)','สิงห์(Leo)',
         'กันย์(Virgo)','ตุลย์(Libra)','พิจิก(Scorpio)','ธนู(Sagittarius)','มังกร(Capricorn)',
         'กุมภ์(Aquarius)','มีน(Pisces)']
    return s[int(deg // 30)]

comp = {
    "name": "นาย+Mai (composite midpoint)",
    "system": "tropical",
    "datetime_utc": nai["datetime_utc"],
    "bodies": [],
    "ascendant": {},
    "houses": nai["houses"],
}
bn = {b["body"]: b for b in nai["bodies"]}
bm = {b["body"]: b for b in mai["bodies"]}
for body in bn:
    md = _mid(bn[body]["absolute_deg"], bm[body]["absolute_deg"])
    comp["bodies"].append({
        "body": body, "sign": _msign(md), "degree": round(md % 30, 4),
        "absolute_deg": round(md, 4), "house": bn[body].get("house"),
        "dignity": bn[body]["dignity"],
    })
asc = _mid(nai["ascendant"]["absolute_deg"], mai["ascendant"]["absolute_deg"])
comp["ascendant"] = {"body": "ASC", "sign": _msign(asc), "degree": round(asc % 30, 4),
                     "absolute_deg": round(asc, 4)}

# ---- real transit conjunction finder (project ephemeris) ----
PLANETS = {
    "Sun": "sun", "Moon": "moon", "Mercury": "mercury", "Venus": "venus",
    "Mars": "mars", "Jupiter": "jupiter barycenter", "Saturn": "saturn barycenter",
    "Uranus": "uranus barycenter", "Neptune": "neptune barycenter", "Pluto": "pluto barycenter",
}

def _lon(target, when):
    t = ts.from_datetime(when)
    pos = earth.at(t).observe(eph[target])
    _, lo, _ = pos.ecliptic_latlon()
    return lo.degrees % 360

def find_conj(planet, natal_deg, start, end, mode="min"):
    """Return (date, sep) of the transit-to-natal conjunction.
    mode='min' -> tightest separation; mode='first' -> first pass < 0.8 deg."""
    d = start
    best = None
    first_hit = None
    while d <= end:
        sep = abs((_lon(PLANETS[planet], d) - natal_deg + 540) % 360 - 180)
        if best is None or sep < best[1]:
            best = (d.date(), round(sep, 3))
        if mode == "first" and first_hit is None and sep < 0.8:
            first_hit = (d.date(), round(sep, 3))
        d += timedelta(days=1)
    return first_hit or best

START = datetime(2026, 9, 1, tzinfo=timezone.utc)
END = datetime(2027, 9, 1, tzinfo=timezone.utc)
CREATED = datetime.now(timezone.utc)

# ---- MAP themes (real) ----
map_nai = {c["card"]: c for c in MAP(nai, max_cards=10)}
map_mai = {c["card"]: c for c in MAP(mai, max_cards=10)}
map_comp = {c["card"]: c for c in MAP(comp, max_cards=10)}

# ---- compute the 8 real expected_event dates ----
dates = {
    "N1": find_conj("Saturn", bn["Saturn"]["absolute_deg"], START, END, "min"),   # Saturn return (real: 2027)
    "N2": find_conj("Mars", bn["Mars"]["absolute_deg"], START, END, "min"),       # Mars return (King of Wands)
    "N3": find_conj("Sun", bn["Sun"]["absolute_deg"], START, END, "min"),          # Solar return
    "M1": find_conj("Jupiter", bm["Sun"]["absolute_deg"], START, END, "min"),      # Jupiter on mai Sun (real)
    "M2": find_conj("Sun", bm["Jupiter"]["absolute_deg"], START, END, "min"),      # Sun on mai natal Jupiter
    "M3": find_conj("Venus", bm["Venus"]["absolute_deg"], START, END, "min"),      # Venus return
    "C1": find_conj("Sun", [b["absolute_deg"] for b in comp["bodies"] if b["body"] == "Sun"][0], START, END, "min"),
    "C2": find_conj("Sun", [b["absolute_deg"] for b in comp["bodies"] if b["body"] == "Jupiter"][0], START, END, "min"),
}

# ---- 8 claims (Thai, specific, tied to MAP theme + real transit) ----
claims = {
    "N1": (
        f"ราว {dates['N1'][0]} ดาวเสาร์โคจรกลับมาทับดาวเสาร์ตัวเองของนาย (ราศีเมษ 16° บ้านที่ 11 — ตก/ fall) "
        f"ในเหตุการณ์ Saturn return ครั้งแรกของชีวิต ตรงกับธีม {map_nai['The Devil']['card']} "
        f"({map_nai['The Devil']['orientation']}) ที่ MAP แมปจากดาวเสาร์ตกในราศีเมษบ้านที่ 11 ของนาย "
        f"คาดการณ์: จุดเปลี่ยนเรื่องมิตรภาพ/เป้าหมายระยะยาว หรือภาระที่ต้องรับผิดชอบอย่างเป็นทางการ"
    ),
    "N2": (
        f"ราว {dates['N2'][0]} ดาวอังคารโคจรทับดาวอังคารตัวเองของนาย (กันย์ 19.3° บ้านที่ 5 — "
        f"การสร้างสรรค์/ความรัก) ในเหตุการณ์ Mars return ตรงกับธีม {map_nai['King of Wands']['card']} "
        f"({map_nai['King of Wands']['orientation']}) ที่ MAP แมปจากดาวอังคารในราศีกันย์บ้านที่ 5 ของนาย "
        f"คาดการณ์: ช่วงที่พลังขับเคลื่อนและการลงมือทำเด่นชัด มีการแสดงออกเชิงสร้างสรรค์ "
        f"หรือความเคลื่อนไหวเรื่องความสัมพันธ์ที่จุดชนวน"
    ),
    "N3": (
        f"ราว {dates['N3'][0]} ดวงอาทิตย์โคจรกลับมาทับดวงอาทิตย์เดิมของนาย (พฤษภ 28° — ใกล้ลัคนา) "
        f"คือสุริยะคติใหม่ประจำปี ตรงกับธีม {map_nai['The Sun']['card']} "
        f"({map_nai['The Sun']['orientation']}) ที่ MAP แมปจากดาวอาทิตย์เด่นในราศีพฤษภบ้านที่ 1 ของนาย "
        f"คาดการณ์: ปีใหม่ของชีวิตบุคคลที่มีเหตุการณ์สะเทือนใจ หรือการเริ่มต้นที่มองโลกเย็นลงแต่แน่วแน่ขึ้น"
    ),
    "M1": (
        f"ราว {dates['M1'][0]} ดาวพฤหัสโคจรทับดวงอาทิตย์ของ Mai (สิงห์ 25.7° บ้านที่ 4) — benefic ใหญ่ทับจุดตัวตน "
        f"ตรงกับธีม {map_mai['The Sun']['card']} ({map_mai['The Sun']['orientation']}) และ "
        f"{map_mai['Wheel of Fortune']['card']} ที่ MAP แมปจากดาวอาทิตย์/พฤหัสของ Mai "
        f"คาดการณ์: ช่วงขยายตัว ได้รับการยอมรับ หรือความอบอุ่นเรื่องบ้าน/ครอบครัว"
    ),
    "M2": (
        f"ราว {dates['M2'][0]} ดวงอาทิตย์โคจรทับดาวพฤหัสตัวเองของ Mai (กรกฎ 7.57° บ้านที่ 3 — "
        f"การสื่อสาร/การเรียน ณ จุดตำแหน่ง exaltation) ตรงกับธีม {map_mai['Wheel of Fortune']['card']} "
        f"ที่ MAP แมปจากดาวพฤหัสในราศีกรกฎบ้านที่ 3 (exaltation) ของ Mai "
        f"คาดการณ์: ช่วงที่ได้รับการยอมรับหรือขยายโอกาสด้านการเรียน/การสื่อสาร หรือข่าวดีเรื่องความรู้"
    ),
    "M3": (
        f"ราว {dates['M3'][0]} ดาวศุกร์โคจรทับดาวศุกร์ตัวเองของ Mai (กรกฎ 19.9° บ้านที่ 3 — การสื่อสาร/พี่น้อง) "
        f"ตรงกับธีม {map_mai['The Empress']['card']} ที่ MAP แมปจากดาวศุกร์ในราศีกรกฎบ้านที่ 3 ของ Mai "
        f"คาดการณ์: ช่วงที่ความสัมพันธ์หรือการแสดงออกด้านศิลปะ/คำพูดเติบโตและเป็นที่รัก"
    ),
    "C1": (
        f"ราว {dates['C1'][0]} ดวงอาทิตย์โคจรทับดวงอาทิตย์คู่ (composite Sun กรกฎ 11.9° บ้านที่ 1) "
        f"คือนิติปีใหม่ของความสัมพันธ์ ตรงกับธีม {map_comp['The Sun']['card']} "
        f"({map_comp['The Sun']['orientation']}) ที่ MAP แมปจากดวงอาทิตย์คู่ในราศีกรกฎบ้านที่ 1 "
        f"คาดการณ์: ช่วงเริ่มต้นบทใหม่ของคู่ ที่ rooted ในบ้าน/การดูแลกัน"
    ),
    "C2": (
        f"ราว {dates['C2'][0]} ดวงอาทิตย์โคจรทับดาวพฤหัสคู่ (composite Jupiter เมษ 29.4° บ้านที่ 10 — เป้าหมายร่วม) "
        f"ตรงกับธีม {map_comp['Wheel of Fortune']['card']} ที่ MAP แมปจากดาวพฤหัสคู่ในบ้านที่ 10 "
        f"คาดการณ์: โอกาสก้าวหน้าร่วมกันด้านอาชีพ/เป้าหมายสาธารณะ หรือการตกลงเดินหน้าโครงการคู่"
    ),
}

# chart used for each fingerprint
chart_for = {"N1": nai, "N2": nai, "N3": nai,
             "M1": mai, "M2": mai, "M3": mai,
             "C1": comp, "C2": comp}

order = ["N1", "N2", "N3", "M1", "M2", "M3", "C1", "C2"]
registered = []
for k in order:
    rec = pre_register(
        chart_for[k],
        claims[k],
        dates[k][0].isoformat(),
        created_at=CREATED,
    )
    registered.append((k, rec))
    print(f"REGISTERED {k} -> {rec['prediction_id']}  expected={dates[k][0]} sep={dates[k][1]}")

# ---- write report ----
lines = []
lines.append("# ORACLE — คำทำนายล่วงหน้าจริง 8 ข้อ (STARHEART bridge)")
lines.append("")
lines.append(f"สร้างเมื่อ: {CREATED.isoformat()}  |  ผู้บันทึก: แผนก ORACLE")
lines.append("สะพาน: STARHEART (chart ↔ tarot deterministic) | ดาวอิงจาก ephemeris จริง (de421/skyfield)")
lines.append("กลไก: ทุกข้อ pre_register ก่อนเหตุการณ์ (created_at < expected_event) แล้วปล่อยเวลาพิสูจน์")
lines.append("")
lines.append("## สรุป 8 ข้อ")
lines.append("")
lines.append("| # | ใคร | คาดการณ์ | expected_event | ธีม MAP (ดาวจริง) | กลไกพิสูจน์ |")
lines.append("|---|-----|-----------|----------------|----------------------|--------------|")

def mech(k):
    if k == "N1": return "เมื่อนายรับภาระ/ตำแหน่งอย่างเป็นทางการราววันนั้น (สัญญา/บทบาทใหม่) → confirm ด้วยหลักฐานวันที่"
    if k == "N2": return "เมื่อนายมีการลงมือทำ/แสดงออกเชิงสร้างสรรค์ หรือความเคลื่อนไหวเรื่องความสัมพันธ์ที่จุดชนวนราววันนั้น → confirm ด้วยหลักฐาน"
    if k == "N3": return "เมื่อเกิดเหตุการณ์สะเทือนใจหรือจุดเริ่มตนใหม่ในปีนักษัตรราววันเกิด → confirm ด้วยบันทึก"
    if k == "M1": return "เมื่อMaiได้รับการยอมรับ/ความอบอุ่นเรื่องบ้านราววันนั้น → confirm ด้วยหลักฐาน"
    if k == "M2": return "เมื่อMaiได้รับการยอมรับหรือข่าวดีด้านการเรียน/การสื่อสารราววันนั้น → confirm ด้วยหลักฐาน"
    if k == "M3": return "เมื่อความสัมพันธ์/งานศิลปะของMaiเติบโตเป็นที่รักราววันนั้น → confirm ด้วยหลักฐาน"
    if k == "C1": return "เมื่อคู่เริ่มบทใหม่ที่ rooted ในบ้าน/การดูแลกันราววันนั้น → confirm ด้วยหลักฐาน"
    if k == "C2": return "เมื่อคู่ก้าวหน้าร่วมกันด้านอาชีพ/โครงการสาธารณะราววันนั้น → confirm ด้วยหลักฐาน"

for k in order:
    who = {"N": "นาย", "M": "Mai", "C": "คู่"}[k[0]]
    lines.append(f"| {k} | {who} | {claims[k][:60]}… | {dates[k][0]} | (ดูรายละเอียดด้านล่าง) | {mech(k)} |")

lines.append("")
lines.append("## รายละเอียดแต่ละข้อ + กลไกพิสูจน์")
lines.append("")
for k in order:
    lines.append(f"### {k}")
    lines.append("")
    lines.append(f"**claim:** {claims[k]}")
    lines.append("")
    lines.append(f"**expected_event:** {dates[k][0].isoformat()}  (ระยะห่างดาวจากจุดnatal ~{dates[k][1]}°)")
    lines.append("")
    lines.append(f"**กลไกพิสูจน์:** {mech(k)}")
    lines.append("")
    lines.append(f"**prediction_id:** {dict(registered)[k]['prediction_id']}")
    lines.append("")

report = "\n".join(lines)
with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write(report)

print("\nREPORT written:", REPORT_PATH)
print("TOTAL REGISTERED:", len(registered))
