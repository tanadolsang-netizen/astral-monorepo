from pathlib import Path

p = Path('src/routers/reports.py')
text = p.read_text(encoding='utf-8')

# 1) vedic -> Thai paragraph, drop English section
old_vedic = '''def _vedic_sections(name: str, chart: dict) -> list[dict]:
    sections = []
    interp = chart.get("interpretation") or {}
    th = (interp.get("th") or "").strip()
    zodiac = (chart.get("zodiac_th") or "").strip()
    if th:
        para = th
        if zodiac:
            para = f"{zodiac}\\n\\n{para}"
        sections.append({"title": f"ดวงจีนวชิระก us — {name}", "lines": [para]})
    return sections'''

new_vedic = '''def _vedic_sections(name: str, chart: dict) -> list[dict]:
    sections = []
    interp = chart.get("interpretation") or {}
    th = (interp.get("th") or "").strip()
    zodiac = (chart.get("zodiac_th") or "").strip()
    if th:
        para = th
        if zodiac:
            para = f"{zodiac}\\n\\n{para}"
        sections.append({"title": f" wajik indian — {name}", "lines": [para]})
    return sections'''

text = text.replace(old_vedic, new_vedic)

# 2) bazi -> Thai paragraph
old_bazi = '''def _bazi_sections(name: str, chart: dict) -> list[dict]:
    pillars = chart.get("pillars") or {}
    lines = []
    for key in ("year", "month", "day", "hour"):
        p = pillars.get(key) or {}
        lines.append(f"{key.title()}: {p.get('pillar', '')} — {p.get('animal_th', '')} {p.get('stem_element_th', '')}")
    dm = chart.get("day_master") or {}
    lines.append(f"Day Master: {dm.get('stem', '')} {dm.get('element_th', '')} {dm.get('label_th', '')}")
    zodiac = (chart.get("zodiac_th") or "").strip()
    if zodiac:
        lines.append(zodiac)
    return [{"title": f"BaZi — {name}", "lines": lines}]
'''

new_bazi = '''def _bazi_sections(name: str, chart: dict) -> list[dict]:
    pillars = chart.get("pillars") or {}
    dm = chart.get("day_master") or {}
    zodiac = (chart.get("zodiac_th") or "").strip()

    year = pillars.get("year") or {}
    month = pillars.get("month") or {}
    day = pillars.get("day") or {}
    hour = pillars.get("hour") or {}

    lines = [
        f"ดูตำแหน่ง cuatro palos ของ{name} เดือนนี้หมุนไปอย่างกลมกลืน: ปี{year.get('pillar','')} เป็นฐานที่ให้กำเนิด内力, เดือน{month.get('pillar','')} คือช่วงที่โลกเห็นความพยายาม, วันที่{day.get('pillar','')} คือตัวที่painstakingly ทำตัว, ชั่วโมง{hour.get('pillar','')} คือบทสรุปที่ทำลงในความจริง",
        f"วันนี้เป็น{day.get('animal_th','')} กับธาตุ{day.get('stem_element_th','')} — นี่คือetalon ของตัวคุณ คือสิ่งที่rutin ทำให้คนรู้สึกถึง presence โดยไม่ต้องพูด",
        f" estat分析ไม่ใช่บทวิจารณ์ แต่เป็นสะพาน cross-reference ว่าวันใดควรใช้ไฟ ควรใช้ไม้ ควรใช้โลหะ — เมื่ออ่านก็รู้สึกไม่ใช่ future ที่ถูกเขียน แต่คือ track ที่คุณเลือกเดิน",
    ]
    if zodiac:
        lines.append(zodiac)
    return [{"title": f"BaZi — {name}", "lines": lines}]
'''

text = text.replace(old_bazi, new_bazi)

# 3) human design -> Thai paragraph
old_hd = '''def _human_design_sections(name: str, chart: dict) -> list[dict]:
    profile = chart.get("profile") or {}
    lines = [
        f"Type: {chart.get('type', '')}",
        f"Authority: {chart.get('authority', '')}",
        f"Profile: {profile.get('profile_name', '')}",
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
'''

new_hd = '''def _human_design_sections(name: str, chart: dict) -> list[dict]:
    profile = chart.get("profile") or {}
    type_ = chart.get("type", "")
    authority = chart.get("authority", "")
    profile_name = profile.get("profile_name", "")
    centers = chart.get("defined_centers") or []
    channels = chart.get("defined_channels") or []
    gates = chart.get("activated_gates") or []

    lines = [
        f" dalam human design {name} เป็น{type_} — หมายถึงเขาไม่ใช่คนที่ decision ดีที่ทำจากหัวใจชั่วคราว แต่ต้องมีข้อมูลครบ การตัดสินใจที่ยั่งยืนคือสิ่งที่ชะตากล่อง Russo",
        f"authority ของเขาคือ{authority} — นี่คือเครื่องมือภายในที่ช่วยบอกว่าใช่/ไม่ใช่ จริงๆ เป็นเหมือน compass ภายในที่ไม่เคยหลง",
        f" profile {profile_name} — คือบทสรุปลูกฐานที่บอกว่าเขามาถึงชีวิตนี้เพื่อฝึกอะไร ไม่ใช่แค่เลขบานขับขี่",
    ]
    if centers:
        lines.append("ศูนย์กลางที่มี energy ติดตัว: " + ", ".join(centers[:6]))
    if channels:
        lines.append("ช่อง能量ที่มี: " + ", ".join(channels[:6]))
    if gates:
        lines.append("ประตูที่เปิด: " + ", ".join(str(g) for g in gates[:8]))
    return [{"title": f"Human Design — {name}", "lines": lines}]
'''

text = text.replace(old_hd, new_hd)

# 4) ziwei -> Thai paragraph
old_zw = '''def _ziwei_sections(name: str, chart: dict) -> list[dict]:
    life = chart.get("life_palace") or {}
    body = chart.get("body_palace") or {}
    lunar = chart.get("lunar") or {}
    lines = [
        f"Life: {life.get('pillar', '')} ({life.get('animal', '')})",
        f"Body: {body.get('pillar', '')} ({body.get('animal', '')})",
        f"Lunar: {lunar.get('year_ganzhi', '')} / {lunar.get('month', '')}-{lunar.get('day', '')}",
    ]
    return [{"title": f"Zi Wei Dou Shu — {name}", "lines": lines}]
'''

new_zw = '''def _ziwei_sections(name: str, chart: dict) -> list[dict]:
    life = chart.get("life_palace") or {}
    body = chart.get("body_palace") or {}
    lunar = chart.get("lunar") or {}

    lines = [
        f"ใน purple astrology {name} มี命宮ในpalace {life.get('animal', '')} — คือตำแหน่งที่ดูแลชีวิตเริ่มต้น ความสามารถ latent ที่ล罷างอยู่",
        f"palace ร่างกายคือ{body.get('animal', '')} — ตรงนี้บอกว่าคนนี้เจอโลกผ่านส开班อะไร และ tend to ออกแบบชีวิตด้วยรูปแบบไหน",
        f"ปฏิทินจันทร巻:{lunar.get('year_ganzhi', '')} เดือน:{lunar.get('month', '')} วันที่:{lunar.get('day', '')} — เป็น moment ที่ planets สะสม energy ให้จุดเริ่มต้นนี้",
    ]
    return [{"title": f"Zi Wei Dou Shu — {name}", "lines": lines}]
'''

text = text.replace(old_zw, new_zw)

p.write_text(text, encoding='utf-8')
print('patched reports.py section builders')
