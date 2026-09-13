# -*- coding: utf-8 -*-
"""NARRATIVE_LANG — เครื่องมือภาษากลาง (Single Source of Truth ทั้งระบบ)

ทุกข้อความที่ผู้ใช้เห็น — ทุกปุ่ม ทุกหัวข้อ ทุกคำอธิบาย — อยู่ที่นี่ที่เดียว:
- ชื่อราศี ดาว ธาตุ (astrology data)
- Nav labels, buttons, hero text (landing UI)
- Result page labels (result UI)
- Error messages, loading states (app text)
- House zones, aspect intensity, dignity (narrative engine)

การเพิ่มภาษาให้มี 2 ไฟล์:
1. แปล/เพิ่มค่าใน DICT ของไฟล์นี้ (Python backend)
2. Export ให้ frontend: python narrative_lang.py --export > i18n.json

ไม่มีการ hardcode string ใน JSX/Python อื่นอีก — ข้อความทั้งหมด = narrative_lang
"""
from __future__ import annotations

import json
import sys
from typing import Literal

_LANG = Literal["th", "en"]

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: ASTROLOGY DATA — คำศัพท์โหราศาสตร์ทุกอย่าง
# ═══════════════════════════════════════════════════════════════════════════

# 1.1 Sign Names — ชื่อราศี 12 ตัว
SIGN_NAMES: dict[str, dict[str, str]] = {
    "Aries":       {"th": "เมษ", "en": "Aries"},
    "Taurus":      {"th": "พฤษภ", "en": "Taurus"},
    "Gemini":      {"th": "เมถุน", "en": "Gemini"},
    "Cancer":      {"th": "กรกฎ", "en": "Cancer"},
    "Leo":         {"th": "สิงห์", "en": "Leo"},
    "Virgo":       {"th": "กันย์", "en": "Virgo"},
    "Libra":       {"th": "ตุลย์", "en": "Libra"},
    "Scorpio":     {"th": "พิจิก", "en": "Scorpio"},
    "Sagittarius": {"th": "ธนู", "en": "Sagittarius"},
    "Capricorn":   {"th": "มังกร", "en": "Capricorn"},
    "Aquarius":    {"th": "กุมภ์", "en": "Aquarius"},
    "Pisces":      {"th": "มีน", "en": "Pisces"},
}

# Sign symbols — สัญลักษณ์ราศี
SIGN_SYMBOLS: dict[str, str] = {
    "Aries": "♈", "Taurus": "♉", "Gemini": "♊", "Cancer": "♋",
    "Leo": "♌", "Virgo": "♍", "Libra": "♎", "Scorpio": "♏",
    "Sagittarius": "♐", "Capricorn": "♑", "Aquarius": "♒", "Pisces": "♓",
}

# 1.2 Element Names — ชื่อธาตุ
ELEMENT_NAMES: dict[str, dict[str, str]] = {
    "fire":  {"th": "ไฟ", "en": "Fire"},
    "earth": {"th": "ดิน", "en": "Earth"},
    "air":   {"th": "ลม", "en": "Air"},
    "water": {"th": "น้ำ", "en": "Water"},
}

# ธาตุ → ชุดไพ่
SUIT_MAP: dict[str, str] = {
    "fire": "Wands", "earth": "Pentacles", "air": "Swords", "water": "Cups",
}

# ราศี → ธาตุ
SIGN_ELEMENT: dict[str, str] = {
    "Aries": "fire", "Leo": "fire", "Sagittarius": "fire",
    "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth",
    "Gemini": "air", "Libra": "air", "Aquarius": "air",
    "Cancer": "water", "Scorpio": "water", "Pisces": "water",
}

# 1.3 Body Labels — ชื่อดาว/ตำแหน่ง
BODY_LABELS: dict[str, dict[str, str]] = {
    "Sun":     {"th": "สุริยะ", "en": "Sun"},
    "Moon":    {"th": "ดวงจันทร์", "en": "Moon"},
    "Mercury": {"th": "พุธ", "en": "Mercury"},
    "Venus":   {"th": "ศุกร์", "en": "Venus"},
    "Mars":    {"th": "อังคาร", "en": "Mars"},
    "Jupiter": {"th": "พฤหัส", "en": "Jupiter"},
    "Saturn":  {"th": "เสาร์", "en": "Saturn"},
    "Uranus":  {"th": "ยูเรนัส", "en": "Uranus"},
    "Neptune": {"th": "เนปจูน", "en": "Neptune"},
    "Pluto":   {"th": "พลูโต", "en": "Pluto"},
    "ASC":     {"th": "ลัคนา", "en": "Ascendant"},
    "MC":      {"th": "ฟ้ากลาง", "en": "Midheaven"},
}

# 1.4 House Zones — ความหมายบ้าน 1-12
HOUSE_ZONES: dict[int, dict[str, str]] = {
    1:  {"th": "จุดเริ่มต้นตัวตน — สิ่งที่คุณสวมก่อนออกสู่โลก", "en": "self-identity"},
    2:  {"th": "จุดค่าของสิ่งที่มี — สิ่งที่คุณถือไว้", "en": "values and possessions"},
    3:  {"th": "จุดคำและเรื่องใกล้ — สิ่งที่คุณคิดและพูด", "en": "communication and thought"},
    4:  {"th": "จุดราก — ที่ที่คุณมา", "en": "roots and home"},
    5:  {"th": "จุดรักและการสร้าง — ที่ที่คุณเป็นตัวเองมากที่สุด", "en": "love and creation"},
    6:  {"th": "จุดงานและร่างกาย — สิ่งที่คุณทำทุกวัน", "en": "work and body"},
    7:  {"th": "จุดคนสำคัญ — คนที่เดินเข้ามาเป็นส่วนหนึ่งของคุณ", "en": "key people and partners"},
    8:  {"th": "จุดการเปลี่ยน — สิ่งที่ตายและเกิดใหม่", "en": "transformation"},
    9:  {"th": "จุดความเชื่อ — สิ่งที่คุณมองไกลออกไป", "en": "beliefs and far horizons"},
    10: {"th": "จุดอาชีพ — สิ่งที่คุณมาเพื่อทำ", "en": "career and calling"},
    11: {"th": "จุดเพื่อนและความหวัง — สิ่งที่คุณหวังและคนที่ช่วย", "en": "friends and hopes"},
    12: {"th": "จุดสิ่งซ่อน — ที่ที่คุณปล่อยให้หลุดลอย", "en": "the hidden and subconscious"},
}

# 1.5 Aspect Intensity
ASPECT_INTENSITY: dict[str, dict[float, str]] = {
    "th": {1.0: "แนบแน่น", 3.0: "ตึง — รู้สึกได้ทุกวัน", 6.0: "ชัด — เห็นได้ชัด", 10.0: "พอรู้สึก", 999.0: "เบา — แต่ยังมีอยู่"},
    "en": {1.0: "tight — exact", 3.0: "tight — felt daily", 6.0: "clear — distinctly felt", 10.0: "noticeable", 999.0: "light — but present"},
}

# 1.6 Dignity Descriptions
DIGNITY_DESC: dict[str, dict[str, dict[str, str]]] = {
    "fall":      {"th": "ตก (dignity {score}) — บทเรียนที่ต้องฝ่าฟันตลอดชีวิต ไม่ใช่ของขวัญ", "en": "in its fall (dignity {score}) — a lifetime lesson"},
    "detriment": {"th": "อ่อน (dignity {score}) — {name}ต้องทำงานหนกว่าสองเท่า", "en": "in detriment (dignity {score}) — you work twice as hard"},
}

# 1.7 Element Domains
ELEMENT_DOMAINS: dict[str, dict[str, str]] = {
    "fire":  {"th": "แรงผลักดัน การลงมือทำ ความกล้า", "en": "drive, initiative, courage"},
    "earth": {"th": "ความมั่นคง ความอดทน การทำจริงเป็นระบบ", "en": "stability, persistence, practical action"},
    "air":   {"th": "ความคิด การสื่อสาร การเชื่อมโยงผู้คน", "en": "thought, communication, connection"},
    "water": {"th": "อารมณ์ ความสัมพันธ์ สัญชาตญาณ", "en": "emotion, relationships, intuition"},
}

# 1.8 Placement Templates (narrative engine)
PLACEMENT_TEMPLATES: dict[str, dict[str, dict[str, str]]] = {
    "Sun": {
        "th": {"core": "สุริยะของ{name}อยู่ที่ {sign} {deg:.2f}° บ้าน {house} — นี่คือแก่นตัวตนที่{name}สวมทุกวัน", "with_tarot": "ไพ่สำหรับสุริยะคือ {card}"},
        "en": {"core": "Your Sun is at {deg:.2f}° {sign}, house {house}. This is the core of who you are.", "with_tarot": "Your tarot card is {card}"},
    },
    "Moon": {
        "th": {"core": "ดวงจันทร์ของ{name}อยู่ที่ {sign} {deg:.2f}° บ้าน {house} — นี่คือที่ที่ความรู้สึกของ{name}อยู่", "with_tarot": "ไพ่ของดวงจันทร์คือ {card}"},
        "en": {"core": "Your Moon is at {deg:.2f}° {sign}, house {house}. This is where your feelings live.", "with_tarot": "The Moon's card is {card}"},
    },
    "Saturn": {
        "th": {"core": "เสาร์อยู่ที่ {sign} {deg:.2f}° บ้าน {house} — นี่คือบทเรียนชีวิตที่{name}ต้องเรียนรู้", "with_tarot": "ไพ่ {card} คือกุญแจไขกรงกรรมนี้"},
        "en": {"core": "Saturn is at {deg:.2f}° {sign}, house {house}. This is your life lesson.", "with_tarot": "Card {card} is the key."},
    },
    "Venus": {
        "th": {"core": "ศุกร์อยู่ที่ {sign} {deg:.2f}° บ้าน {house} — นี่คือรสชาติความรักของ{name}", "with_tarot": "ไพ่ {card} แสดงรูปแบบความรักเดียวกัน"},
        "en": {"core": "Venus at {deg:.2f}° {sign}, house {house}. This is the flavor of your love.", "with_tarot": "Card {card} shows the same pattern."},
    },
    "Mars": {
        "th": {"core": "อังคารอยู่ที่ {sign} {deg:.2f}° บ้าน {house} — นี่คือไฟที่ขับเคลื่อน{name}", "with_tarot": "ไพ่ {card} เป็นตัวช่วยหล่อหล่อไฟนี้"},
        "en": {"core": "Mars at {deg:.2f}° {sign}, house {house}. This is your drive.", "with_tarot": "Card {card} channels this fire."},
    },
}

# 1.9 Closing Templates
CLOSING_TEMPLATES: dict[str, dict[str, str]] = {
    "th": {
        "convergence": "ทุกประโยคด้านบนคำนวณจากตัวเลขของ{name} — องศาแม่นยำ, orb แม่นยำ ไพ่ไม่ได้ตีความดวง แต่มันยืนยันดวง",
        "element_summary": "ธาตุเด่นในดวง{name}คือ{dominant} ({dominant_domain}) ส่วนธาตุที่ต้องเรียนรู้คือ{lacking} ({lacking_domain})",
    },
    "en": {
        "convergence": "Every sentence above is computed from YOUR numbers — exact degrees, exact orbs.",
        "element_summary": "Your chart is dominated by {dominant} ({dominant_domain}), while {lacking} ({lacking_domain}) is what you're here to learn.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: LANDING PAGE UI — ข้อความทั้งหมดบนหน้าแรก
# ═══════════════════════════════════════════════════════════════════════════

NAV: dict[str, dict[str, str]] = {
    "home":      {"th": "หน้าแรก", "en": "Home"},
    "natal":     {"th": "ดูดวงชะตา", "en": "Natal Chart"},
    "tarot":     {"th": "ไพ่ทาโรต์", "en": "Tarot"},
    "synastry":  {"th": "ดูคู่", "en": "Synastry"},
    "vedic":     {"th": "เวดิก", "en": "Vedic"},
    "horary":    {"th": "มูฮูร์ตะ", "en": "Horary"},
    "ai":        {"th": "AI Reading", "en": "AI Reading"},
    "login":     {"th": "เข้าสู่ระบบ", "en": "Login"},
    "signup":    {"th": "สมัครสมาชิก", "en": "Sign Up"},
}

HERO: dict[str, dict[str, str]] = {
    "pill":         {"th": "✦ ดูดวงแบบโหรหลวงเคยมองฟ้า", "en": "✦ Read fortunes like ancient astrologers"},
    "title1":       {"th": "ดาวแต่ละดวง", "en": "Each star"},
    "title2":       {"th": "ล้วนมี", "en": "all has"},
    "title3":       {"th": "คำบอก", "en": "words to tell"},
    "title4":       {"th": "ให้คุณ", "en": "for you"},
    "description":  {"th": "วันที่คุณลืมตามาเกิด ดาวแต่ละดวงจัดเรียงตัวเองให้พอดีจนคุณได้เห็น — แล้วมันก็เล่าได้ว่าคุณมาเพื่ออะไร จะไปรักใคร และช่วงไหนที่ฟ้าจะมอบของขวัญให้คุณ",
                     "en": "The day you were born, the stars arranged themselves just so you could see — and then they told what you came for, who you'll love, and when the sky will gift you"},
    "cta_primary":  {"th": "ให้ดาวเล่าให้คุณฟัง", "en": "Let the stars tell your story"},
    "cta_secondary":{"th": "✦ เลื่อนลงเพื่อเริ่มการเดินทางท่ามกลางดวงดาว ✦", "en": "✦ Scroll to begin your journey among the stars ✦"},
    "scroll_hint":  {"th": "เลื่อนลง", "en": "Scroll"},
    "loading":      {"th": "กำลังโหลดจักรวาล...", "en": "Loading the cosmos..."},
}

# ── LANDING: ข้อความเฉพาะหน้า Landing ──
LANDING: dict[str, dict[str, str]] = {
    # Tagline
    "tagline":              {"th": "ภาษาที่ท้องฟ้าจารซ้านไว้", "en": "The language the sky has written"},
    "hero_subtitle":        {"th": "อ่านดวงชะตาผ่าน โหราศาสตร์ และ ไพ่ทาโรต์ ด้วยปัญญาประดิษฐ์ที่เข้าใจจักรวาล",
                             "en": "Read your destiny through astrology & tarot with AI that understands the cosmos"},
    "hero_cta":             {"th": "เริ่มต้นดูดวง", "en": "Start Reading"},
    "hero_scroll":          {"th": "เลื่อนเพื่อสำรวจ", "en": "Scroll to explore"},
    "story_sun_title":      {"th": "หนึ่ง — ดวงอาทิตย์", "en": "One — The Sun"},
    "story_sun_subtitle":   {"th": "แสงแห่ง ตัวตน", "en": "Light of Identity"},
    "story_sun_desc":       {"th": "ดวงอาทิตย์คือหัวใจของระบบสุริยะ — เช่นเดียวกับตัวตนที่แท้จริงของคุณในจักรวาล มันคือแสงสว่างที่บอกว่าคุณมาเพื่อเป็นใคร",
                             "en": "The Sun is the heart of the solar system — like your true identity in the universe"},
    "story_planets_title":  {"th": "สอง — ดวงดาว", "en": "Two — The Planets"},
    "story_planets_subtitle": {"th": "ทั้งแปดดวง เล่าเรื่องราว", "en": "Eight planets tell the story"},
    "story_planets_desc":   {"th": "ดาวพุธ ดาวศุกร์ ดาวอังคาร ดาวพฤหัส ดาวเสาร์ ดาวยูเรนัส ดาวเนปจูน ดาวพลูโต — แต่ละดวงคือบทบาทในละครเรื่องชีวิตคุณ",
                             "en": "Mercury Venus Mars Jupiter Saturn Uranus Neptune Pluto — each a role in your life's play"},
    "story_tarot_title":    {"th": "สาม — ไพ่ทาโรต์", "en": "Three — Tarot"},
    "story_tarot_subtitle": {"th": "เจ็ดสิบแปดใบ เปิดเผยความลับ", "en": "Seventy-eight cards reveal secrets"},
    "story_tarot_desc":     {"th": "ไพ่ทาโรต์เจ็ดสิบแปดใบ คือกระจกสะท้อนจิตใจ ตั้งแต่นักเดินทางผู้เริ่มต้นการผจญภัย ไปจนถึงโลกแห่งความสมบูรณ์",
                             "en": "Seventy-eight tarot cards — a mirror of the mind"},
    "stat_tarot":           {"th": "๗๘ ไพ่ทาโรต์", "en": "78 Tarot Cards"},
    "stat_houses":          {"th": "๑๒ บ้าน", "en": "12 Houses"},
    "stat_planets":         {"th": "๑๐ ดวงดาว", "en": "10 Planets"},
    "stat_chart":           {"th": "๓๖๐° แผนที่ดวงชะตา", "en": "360° Natal Chart"},
    "capabilities_title":   {"th": "ความสามารถ", "en": "Capabilities"},
    "capabilities_subtitle": {"th": "ความสามารถที่ครอบคลุมทุกมิติโหราศาสตร์", "en": "Comprehensive astrology capabilities"},
    "cap_natal_title":      {"th": "แผนที่ดวงชะตา", "en": "Natal Chart"},
    "cap_natal_desc":       {"th": "แผนที่ชะตาวันเกิดสามร้อยหกสิดองศา แสดงตำแหน่งดาวครบถ้วน",
                             "en": "360-degree natal chart showing complete planetary positions"},
    "cap_tarot_title":      {"th": "การอ่านไพ่ทาโรต์", "en": "Tarot Reading"},
    "cap_tarot_desc":       {"th": "ไพ่เจ็ดสิบแปดใบ อ่านได้ทุกด้าน ทั้งงาน ความรัก การเงิน",
                             "en": "Seventy-eight cards for career, love, and finance"},
    "cap_synastry_title":   {"th": "การมองเห็นคู่", "en": "Synastry"},
    "cap_synastry_desc":    {"th": "วิเคราะห์ความเข้ากันระหว่างสองจิตวิญญาณ",
                             "en": "Analyze the connection between two souls"},
    "cap_transit_title":    {"th": "ดาวเคลื่อนที่", "en": "Transits"},
    "cap_transit_desc":     {"th": "ดูพลังงานดาวเคลื่อนที่ในปัจจุบัน",
                             "en": "See current planetary energy movements"},
    "cap_solar_title":      {"th": "บ้านธรณีประจำปี", "en": "Annual Solar Return"},
    "cap_solar_desc":       {"th": "คาดการณ์รายปีผ่านบ้านธรณีประจำตัว",
                             "en": "Yearly forecast through solar houses"},
    "result_thai_pure":     {"th": "ภาษาที่ท้องฟ้าจารซ้านไว้", "en": "Written in the sky's language"},
    "result_subtitle":      {"th": "ผลลัพธ์ภาษาไทยบริสุทธิ์ สไตล์ไพ่ทาโรต์", "en": "Pure Thai results, tarot-style"},
    "form_name":            {"th": "ชื่อของคุณ", "en": "Your Name"},
    "form_dob":             {"th": "วันเกิด", "en": "Date of Birth"},
    "form_time":            {"th": "เวลาเกิด", "en": "Time of Birth"},
    "form_place":           {"th": "สถานที่เกิด", "en": "Place of Birth"},
    "form_submit":          {"th": "สร้างภาพดวงชะตาของคุณ", "en": "Generate Your Cosmic Art"},
    "loading_generate":     {"th": "กำลังสร้างภาพดวงชะตาด้วยคอสมิก...", "en": "Generating your cosmic destiny art..."},
    "loading_timeout":      {"th": "การสร้างภาพใช้เวลานานเกินไป กรุณาลองใหม่", "en": "Generation timed out, please retry"},
    "loading_fail":         {"th": "การสร้างภาพล้มเหลว", "en": "Generation failed"},
    "loading_connect_fail": {"th": "การเชื่อมต่อล้มเหลว กรุณาลองใหม่", "en": "Connection failed, please retry"},
    "art_title":            {"th": "ภาพดวงชะตาของคุณ", "en": "Your Cosmic Art"},
    "art_uniqueness":       {"th": "ภาพนี้สร้างจากข้อมูลดวงชะตาของคุณ — ไม่มีใครเหมือนคุณในจักรวาลนี้",
                             "en": "This image was generated from your unique birth chart — no one else in the universe is like you"},
    "footer":               {"th": "อัสตรัล — ภาษาที่ท้องฟ้าจารซ้านไว้ — ๒๕๖๙", "en": "Astral — Written in the sky's language — 2026"},
}

SECTION: dict[str, dict[str, str]] = {
    "01_title":     {"th": "ดูดวงชะตา", "en": "Natal Chart"},
    "01_desc":      {"th": "วันเกิดของคุณ คือเข็มทิศชี้ทางมาเกิด — เราจะบอกว่าคุณมีของดีซ่อนที่ไหน", "en": "Your birthday is a compass — we'll show you where your gifts hide"},
    "02_title":     {"th": "ไพ่ทาโรต์", "en": "Tarot"},
    "02_desc":      {"th": "ไพ่ 78 ใบจากสำนักโบราณ — สิ่งที่ออกมาไม่ใช่คำทำนายเลื่อนลอย แต่เป็นเสียงที่สะท้อนสิ่งที่คุณกังวลอยู่", 
                     "en": "78 cards from ancient schools — not vague prophecies, but reflections of your worries"},
    "03_title":     {"th": "มูฮูร์ตะ", "en": "Horary"},
    "03_desc":      {"th": "มีเรื่องสำคัญจะทำใช่ไหม — เราจะหาชั่วโมงที่ดาวยืนรับรอง ให้สิ่งที่คุณเริ่มตั้งต้นนั้นเป็นสิริมงคล", 
                     "en": "Starting something important? We'll find the hour the stars support you"},
    "04_title":     {"th": "เวดิก", "en": "Vedic"},
    "04_desc":      {"th": "มองผ่านตำราโบราณอินเดีย ดาวจะเลื่อนไปตำแหน่งที่แท้จริงตามฤดูกาล", "en": "Through ancient Indian texts — stars shift to their true seasonal positions"},
    "05_title":     {"th": "ดูคู่ Synastry", "en": "Synastry"},
    "05_desc":      {"th": "เมื่อดวงคุณไปพบดวงเขา จะเกิดกระแสไฟบางอย่าง — เราจะบอกว่าสองดวงนี้ช่วยกันหรือต้องระวัง", 
                     "en": "When your chart meets theirs — we'll tell if these two stars help each other"},
}

BUTTONS: dict[str, dict[str, str]] = {
    "cta":          {"th": "เริ่มต้นใช้งาน", "en": "Get Started"},
    "login":        {"th": "เข้าสู่ระบบ", "en": "Login"},
    "signup":       {"th": "สมัครสมาชิก", "en": "Sign Up"},
    "logout":       {"th": "ออกจากระบบ", "en": "Logout"},
    "save":         {"th": "บันทึก", "en": "Save"},
    "cancel":       {"th": "ยกเลิก", "en": "Cancel"},
    "close":        {"th": "ปิด", "en": "Close"},
    "back":         {"th": "ย้อนกลับ", "en": "Back"},
    "next":         {"th": "ถัดไป", "en": "Next"},
    "submit":       {"th": "ส่ง", "en": "Submit"},
    "download":     {"th": "ดาวน์โหลด", "en": "Download"},
    "share":        {"th": "แชร์", "en": "Share"},
    "read_more":    {"th": "อ่านต่อ", "en": "Read More"},
    "loading":      {"th": "กำลังโหลด...", "en": "Loading..."},
    "calculating":  {"th": "กำลังคำนวณ...", "en": "Calculating..."},
}

FORM: dict[str, dict[str, str]] = {
    "name":         {"th": "ชื่อ", "en": "Name"},
    "date":         {"th": "วันเกิด", "en": "Birth Date"},
    "time":         {"th": "เวลาเกิด", "en": "Birth Time"},
    "location":     {"th": "สถานที่เกิด", "en": "Birth Location"},
    "question":     {"th": "คำถาม", "en": "Your Question"},
    "system":       {"th": "ระบบ", "en": "System"},
    "tropical":     {"th": "Tropical (ตะวันตก)", "en": "Tropical (Western)"},
    "sidereal":     {"th": "Sidereal (เวดิก)", "en": "Sidereal (Vedic)"},
    "name_placeholder": {"th": "ใส่ชื่อของคุณ", "en": "Enter your name"},
    "date_placeholder": {"th": "วัน/เดือน/ปี", "en": "DD/MM/YYYY"},
    "time_placeholder": {"th": "ชั่วโมง:นาที", "en": "HH:MM"},
    "question_placeholder": {"th": "พิมพ์คำถามของคุณ...", "en": "Type your question..."},
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: RESULT PAGE UI — ข้อความในหน้าผลลัพธ์
# ═══════════════════════════════════════════════════════════════════════════

RESULT: dict[str, dict[str, str]] = {
    "title":            {"th": "เรื่องราวที่ดาวเล่าให้คุณฟัง", "en": "The story the stars tell you"},
    "loading":          {"th": "กำลังอ่านดวงชะตา...", "en": "Reading your chart..."},
    "narrative_title":  {"th": "เรื่องราวจากดาว", "en": "Story from the Stars"},
    "tarot_title":      {"th": "ไพ่ที่ออกมาสำหรับคุณ", "en": "Your Tarot Cards"},
    "elements_title":   {"th": "ธาตุในดวง", "en": "Elements"},
    "aspects_title":    {"th": "Aspects", "en": "Aspects"},
    "houses_title":     {"th": "บ้าน", "en": "Houses"},
    "caveat":           {"th": "นี่คือเรื่องราวชีวิตของคุณ ไม่ใช่ตำราโหราศาสตร์ — ทุกระบบชี้มาที่จุดเดียวกัน นั่นไม่ใช่ความบังเอิญ", 
                         "en": "This is your life story, not a textbook — every system points to the same truth"},
    "download_pdf":     {"th": "อ่านรายงานที่ฟ้าฝากมา", "en": "Download Report"},
    "share_result":     {"th": "แชร์ผลลัพธ์", "en": "Share"},
    "new_reading":      {"th": "ดูดวงใหม่", "en": "New Reading"},
    "error_generic":    {"th": "เกิดข้อผิดพลาด — ลองใหม่อีกครั้ง", "en": "Something went wrong — try again"},
    "no_data":          {"th": "กรุณากรอกข้อมูลวันเกิดก่อน", "en": "Please enter your birth data first"},
    "ai_reading":       {"th": "AI Reading", "en": "AI Reading"},
    "ai_button":        {"th": "ขอ AI อ่านเพิ่ม", "en": "Ask AI"},
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: APP / COMMON UI — ข้อความทั่วไปในแอพ
# ═══════════════════════════════════════════════════════════════════════════

APP: dict[str, dict[str, str]] = {
    "app_name":         {"th": "Astral", "en": "Astral"},
    "tagline":          {"th": "โหราศาสตร์ครบวงจร", "en": "Complete Astrology System"},
    "loading":          {"th": "กำลังโหลด...", "en": "Loading..."},
    "error":            {"th": "ข้อผิดพลาด", "en": "Error"},
    "success":          {"th": "สำเร็จ", "en": "Success"},
    "warning":          {"th": "คำเตือน", "en": "Warning"},
    "info":             {"th": "ข้อมูล", "en": "Info"},
    "yes":              {"th": "ใช่", "en": "Yes"},
    "no":               {"th": "ไม่", "en": "No"},
    "confirm":          {"th": "ยืนยัน", "en": "Confirm"},
    "required":         {"th": "จำเป็น", "en": "Required"},
    "optional":         {"th": "ไม่จำเป็น", "en": "Optional"},
    "enable_js":        {"th": "ต้องเปิด JavaScript เพื่อใช้งาน 3D ดวงดาวได้", "en": "Please enable JavaScript for 3D star rendering"},
    "motion_on":        {"th": "แอนิเมชันเปิดอยู่ — คลิกเพื่อปิด", "en": "Animation on — click to turn off"},
    "motion_off":       {"th": "แอนิเมชันปิดอยู่ — คลิกเพื่อเปิด", "en": "Animation off — click to turn on"},
    "motion_toggle_on": {"th": "เปิดแอนิเมชัน", "en": "Turn On Animation"},
    "motion_toggle_off":{"th": "ปิดแอนิเมชัน", "en": "Turn Off Animation"},
    "drag_hint":        {"th": "✦ ลากเพื่อหมุน · Scroll เพื่อซูม ✦", "en": "✦ Drag to rotate · Scroll to zoom ✦"},
    "daily":            {"th": "ดาวประจำวัน", "en": "Daily Planets"},
    "solar_system":     {"th": "ระบบสุริยะ", "en": "Solar System"},
    "calculating":      {"th": "กำลังคำนวณดวง...", "en": "Calculating chart..."},
    "loading_data":     {"th": "กำลังโหลดข้อมูลดาว...", "en": "Loading celestial data..."},
    "chart_life":       {"th": "ตำแหน่งดวงในชะตาคุณ", "en": "Positions in your chart"},
    "chart_sky":        {"th": "ตำแหน่งดวงท้องฟ้า", "en": "Positions in the sky"},
}

# Tarot specific
TAROT: dict[str, dict[str, str]] = {
    "title":        {"th": "ไพ่ทาโรต์", "en": "Tarot"},
    "draw":         {"th": "สับไพ่", "en": "Draw Cards"},
    "spread_3":     {"th": "ไพ่ 3 ใบ", "en": "3 Cards"},
    "celtic_cross": {"th": "Celtic Cross", "en": "Celtic Cross"},
    "love":         {"th": "ไพ่ความรัก", "en": "Love Spread"},
    "career":       {"th": "ไพ่การงาน", "en": "Career Spread"},
    "three_card_desc": {"th": "โบกไพ่แล้วตั้งคำถามใจ — ไพ่สามใบนี้จะตอบสิ่งที่คุณอยากรู้", "en": "Shuffle and set your intention — these three cards answer your question"},
    "your_cards":   {"th": "ไพ่ของคุณ", "en": "Your Cards"},
    "meaning":      {"th": "ความหมาย", "en": "Meaning"},
    "upright":      {"th": "หงาย", "en": "Upright"},
    "reversed":     {"th": "คว่ำ", "en": "Reversed"},
    "click_flip":   {"th": "คลิกเพื่อพลิกไพ่", "en": "Click to flip"},
}

# Birth data form
BIRTH_FORM: dict[str, dict[str, str]] = {
    "title":            {"th": "ข้อมูลการเกิด", "en": "Birth Data"},
    "name_label":       {"th": "ชื่อของคุณ", "en": "Your Name"},
    "date_label":       {"th": "วันเกิด", "en": "Date of Birth"},
    "time_label":       {"th": "เวลาเกิด", "en": "Time of Birth"},
    "place_label":      {"th": "สถานที่เกิด", "en": "Place of Birth"},
    "get_location":     {"th": "ใช้ตำแหน่งปัจจุบัน", "en": "Use current location"},
    "calculate":        {"th": "คำนวณดวง", "en": "Calculate"},
    "name_required":    {"th": "กรุณากรอกชื่อ", "en": "Name is required"},
    "date_required":    {"th": "กรุณากรอกวันเกิด", "en": "Date is required"},
    "time_required":    {"th": "กรุณากรอกเวลาเกิด", "en": "Time is required"},
    "place_required":   {"th": "กรุณากรอกสถานที่เกิด", "en": "Place is required"},
}

# Tarot section
INTRO: dict[str, dict[str, str]] = {
    "prepare":  {"th": "✦ เตรียมพร้อมลอยสู่ท้องฟ้า ✦", "en": "✦ PREPARE FOR TAKEOFF ✦"},
    "system":   {"th": "ระบบโหราศาสตร์ครบวงจร", "en": "THE COSMIC SYSTEM"},
}

# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API — ฟังก์ชันที่ module อื่นเรียกใช้
# ═══════════════════════════════════════════════════════════════════════════

def sign_name(sign_str: str, lang: _LANG = "th") -> str:
    """แปลงชื่อราศีเป็นภาษาที่ต้องการ. รูปแบบ: 'Taurus', 'พฤษภ(Taurus)', 'พฤษภ'"""
    if "(" in sign_str:
        inner = sign_str.split("(")[-1].rstrip(")")
        for en_name, names in SIGN_NAMES.items():
            if inner.lower() == en_name.lower():
                return names.get(lang, inner)
        return inner
    if sign_str in SIGN_NAMES:
        return SIGN_NAMES[sign_str].get(lang, sign_str)
    for en_name, names in SIGN_NAMES.items():
        if names.get("th") == sign_str:
            return names.get(lang, sign_str)
    return sign_str


def element_name(elem: str, lang: _LANG = "th") -> str:
    """แปลงชื่อธาตุ. รับได้ทั้ง 'fire' และ 'ไฟ'"""
    if elem in ELEMENT_NAMES:
        return ELEMENT_NAMES[elem].get(lang, elem)
    for en_name, names in ELEMENT_NAMES.items():
        if names.get("th") == elem or names.get("en", "").lower() == elem.lower():
            return names.get(lang, elem)
    return elem


def body_label(body: str, lang: _LANG = "th") -> str:
    """ชื่อดาว/ตำแหน่ง"""
    return BODY_LABELS.get(body, {}).get(lang, body)


def house_zone(house: int, lang: _LANG = "th") -> str:
    """คำอธิบายบ้าน"""
    return HOUSE_ZONES.get(house, {}).get(lang, "")


def aspect_intensity(orb: float, lang: _LANG = "th") -> str:
    """ระดับความตึงของ aspect ตาม orb"""
    thresholds = ASPECT_INTENSITY.get(lang, ASPECT_INTENSITY["th"])
    for limit, desc in sorted(thresholds.items()):
        if orb <= limit:
            return desc
    return thresholds.get(999.0, "")


def dignity_desc(label: str, score: int, name: str = "", lang: _LANG = "th") -> str:
    """คำอธิบาย dignity (fall/detriment)"""
    if label in DIGNITY_DESC:
        return DIGNITY_DESC[label][lang].format(score=score, name=name)
    return ""


def house_zone_text(house: int, lang: _LANG = "th") -> str:
    """'ในบ้าน X มันพูดถึง...'"""
    zone = house_zone(house, lang)
    if lang == "th":
        return f"ในบ้าน {house} มันพูดถึง{zone}"
    return f"In house {house}, this speaks of {zone}"


def element_domain(elem: str, lang: _LANG = "th") -> str:
    """'แรงผลักดัน การลงมือทำ...'"""
    if elem in ELEMENT_DOMAINS:
        return ELEMENT_DOMAINS[elem].get(lang, "")
    for en_name, names in ELEMENT_NAMES.items():
        if names.get("th") == elem:
            return ELEMENT_DOMAINS.get(en_name, {}).get(lang, "")
    return ""


def closing_convergence(name: str, lang: _LANG = "th") -> str:
    """ประโยคปิด — convergence truth"""
    return CLOSING_TEMPLATES[lang]["convergence"].format(name=name)


def closing_element(name: str, dominant: str, lacking: str, lang: _LANG = "th") -> str:
    """ประโยคปิด — element balance"""
    return CLOSING_TEMPLATES[lang]["element_summary"].format(
        name=name,
        dominant=element_name(dominant, lang),
        lacking=element_name(lacking, lang),
        dominant_domain=element_domain(dominant, lang),
        lacking_domain=element_domain(lacking, lang),
    )


def placement_template(body: str, template_key: str, lang: _LANG = "th") -> str | None:
    """ดึง template สำหรับดาว + key ที่ต้องการ"""
    return PLACEMENT_TEMPLATES.get(body, {}).get(lang, {}).get(template_key)


def suit_for_element(elem: str) -> str:
    """ธาตุ → ชุดไพ่"""
    return SUIT_MAP.get(elem, "Wands")


def sign_element(sign: str) -> str:
    """ราศี → ธาตุ"""
    th_en = {v["th"]: k for k, v in SIGN_NAMES.items()}
    if sign in th_en:
        sign = th_en[sign]
    return SIGN_ELEMENT.get(sign, "earth")


# ── Frontend Export ─────────────────────────────────────────────────────
def export_i18n() -> dict:
    """Export ข้อความทั้งหมดเป็น dict สำหรับ frontend (JSON)"""
    sections = [
        "NAV", "HERO", "LANDING", "SECTION", "BUTTONS", "FORM",
        "RESULT", "APP", "TAROT", "BIRTH_FORM", "INTRO",
    ]
    data: dict[str, dict[str, dict[str, str]]] = {}
    for section_name in sections:
        section_data = globals().get(section_name)
        if isinstance(section_data, dict):
            data[section_name] = section_data
    return data


if __name__ == "__main__":
    if "--export" in sys.argv:
        data = export_i18n()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    elif "--export-signs" in sys.argv:
        print(json.dumps(SIGN_NAMES, ensure_ascii=False, indent=2))
    elif "--export-elements" in sys.argv:
        print(json.dumps(ELEMENT_NAMES, ensure_ascii=False, indent=2))
    elif "--export-bodies" in sys.argv:
        print(json.dumps(BODY_LABELS, ensure_ascii=False, indent=2))
    elif "--export-houses" in sys.argv:
        print(json.dumps({str(k): v for k, v in HOUSE_ZONES.items()}, ensure_ascii=False, indent=2))
    else:
        print("Usage: python narrative_lang.py --export")
        print("  --export           Export all UI strings as JSON")
        print("  --export-signs     Export sign names")
        print("  --export-elements  Export element names")
        print("  --export-bodies    Export body labels")
        print("  --export-houses    Export house zones")
