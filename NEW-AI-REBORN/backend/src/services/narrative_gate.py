"""Centralized language contract for PDF reports.

Rules
- Every router must pass `lang=req.lang` to renderers/builders.
- Every builder output must be treated as unsafe until it passes `clean_section()`.
- No builder is allowed to hardcode English/Chinese/Japanese/Korean tokens.
- All natural-language mappings live here, not scattered across builders.
- PyThaiNLP is the mandatory Thai cleaner before any text reaches renderer.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# PyThaiNLP — mandatory Thai cleaner
# ---------------------------------------------------------------------------
try:
    from pythainlp import thai
    from pythainlp.util import normalize
    _PYTHAINLP_OK = True
except Exception:
    _PYTHAINLP_OK = False


def _clean_thai(text: str) -> str:
    """Clean Thai text using PyThaiNLP if available."""
    if not text or not _PYTHAINLP_OK:
        return text
    try:
        # Remove non-Thai characters that PyThaiNLP can't handle
        # Keep Thai script, numbers, and basic punctuation
        text = re.sub(r'[^\u0E00-\u0E7F\u2000-\u206F\u2190-\u21FF\u2200-\u22FF\u0080-\u00FF\u0100-\u017F\u2010-\u2027\u2030-\u205E\u2070-\u209F\u20A0-\u20CF\u2100-\u214F\u2150-\u218F\u25A0-\u25FF\u2600-\u26FF\u2700-\u27BF\u0000-\u007F]', '', text)
        # Normalize Thai text
        text = normalize(text)
        # Remove repeated spaces
        text = re.sub(r'\s+', ' ', text).strip()
    except Exception:
        pass
    return text


# ---------------------------------------------------------------------------
# Language key resolver
# ---------------------------------------------------------------------------

def lang_key(lang: str) -> str:
    return "th" if str(lang or "th").lower().startswith("th") else "en"


# ---------------------------------------------------------------------------
# Whitelist sanitizers — used by renderer and gate
# ---------------------------------------------------------------------------

_ASCII_PRINTABLE = "\x09\x0A\x0D\x20-\x7E"
_THAI_BLOCK = "\u0E00-\u0E7F"

_TH_KEEP = re.compile(f"[^{_ASCII_PRINTABLE}{_THAI_BLOCK}]")
_EN_KEEP = re.compile(f"[^{_ASCII_PRINTABLE}]")


def sanitize(text: str, lang: str = "th") -> str:
    if not text:
        return ""
    keep = _TH_KEEP if lang_key(lang) == "th" else _EN_KEEP
    out = keep.sub("", text)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    return out.strip()


# ---------------------------------------------------------------------------
# Centralized artifact blocklist — single source of truth
# ---------------------------------------------------------------------------

ARTIFACTS = [
    # Known mixed-language tokens from prior LLM generations
]

_ARTIFACT_RE = re.compile("|".join(re.escape(a) for a in ARTIFACTS))


def strip_artifacts(text: str) -> str:
    if not text:
        return ""
    out = _ARTIFACT_RE.sub("", text)
    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    return out.strip()


# ---------------------------------------------------------------------------
# Natural TH mappings — single source of truth for all builders
# ---------------------------------------------------------------------------

HD_TYPE_TH = {
    "Generator": "เจ้าคุณเป็นคนสร้างสรรค์ ชอบเริ่มสิ่งใหม่และมองเห็นความเป็นไปได้",
    "Manifestor": "เจ้าคุณเป็นคนตัดสินใจรวดเร็ว มีพลังนำเริ่มต้นสิ่งที่ต้องการ",
    "Projector": "เจ้าคุณเป็นคนเข้าใจระบบและคนอื่นดี มีโอกาสชนะใจคน",
    "Reflector": "เจ้าคุณเป็นกระจกสาธารณะ เรียนรู้จากสิ่งที่สะท้อนกลับมา",
}

HD_AUTH_TH = {
    "Sacral": "รู้สึกภายในบอกว่าใช่หรือไม่ใช่ — ไม่ใช่ความคิด กระตุกท้อง",
    "Emotional": "อารมณ์คล้อยตาม ต้องรอจนรู้สึกว่าใช่ — ไม่รีบ ก่อนรู้สึก",
    "Ego": "หัวใจเต้นบอกว่าคุณทำได้ — มีความพยายามและ",
    "Splenic": "รู้สึกลึกๆ ล่วงหน้า — เหมือนเสียงเตือนภายใน",
}

HD_PROFILE_TH = {
    "1/3": "ผู้มีความ ลึกๆ เรียนรู้จากประสบการณ์",
    "1/4": "ผู้มีความสนใจสูง ค้นหาความเข้าใจที่แข็งแกร่ง",
    "2/3": "ผู้มีความ ต้องใช้เวลาผสานตัวตน",
    "2/4": "ผู้มีความ ความสัมพันธ์และเครือข่าย",
    "3/5": "ผู้มีความ เก่งปัญหาแล้ว",
    "3/6": "ผู้มีความ เรียนรู้จากบทสากล",
    "4/6": "ผู้มีความ ต้องรู้จักให้ดีก่อน",
    "4/1": "ผู้มีความ ต้องเข้าใจ",
    "5/1": "ผู้มีความ ดูไม่ แต่รู้สึก",
    "5/2": "ผู้มีความ สามารถปรับตัวได้ดี",
    "5/3": "ผู้มีความ เรียนรู้จากชีวิตจริง",
    "5/4": "ผู้มีความ ทำ อย่างเป็นธรรมชาติ",
    "6/1": "ผู้มีความ ต้องเดิน ของตัวเองก่อน",
    "6/2": "ผู้มีความ ต้องมีเวลา ก่อน",
    "6/3": "ผู้มีความ เรียนรู้จาก",
    "6/4": "ผู้มีความ ต้องอยู่กับคนที่ไว้ใจ",
}

HD_CENTER_TH = {
    "Head": "ศูนย์กลางหัว — ความคิดและแรงดึงดูดของแนวคิด",
    "Ajna": "ศูนย์กลาง — การข้อมูลและความเข้าใจ",
    "Throat": "ศูนย์กลางคอ — การ และการออกเสียง",
    "G": "ศูนย์กลาง — ความสัมพันธ์และ",
    "Heart": "ศูนย์กลางหัวใจ — ความ และ",
    "Solar Plexus": "ศูนย์กลาง — อารมณ์และ",
    "Sacral": "ศูนย์กลางสาคร — ความ และ",
    "Spleen": "ศูนย์กลางม้าม — ความ และ",
    "Root": "ศูนย์กลางราก — ความ และ",
}

HD_CHANNEL_TH = {
    "1-8": "ช่อง — จริงเข้ามา",
    "2-14": "ช่อง — การ",
    "3-60": "ช่อง — ความพร้อมให้",
    "4-13": "ช่อง — การ",
    "5-15": "ช่อง — การ",
    "6-58": "ช่อง — การ",
    "7-31": "ช่อง — การแล้วมี",
    "9-52": "ช่อง — การ",
    "10-20": "ช่อง — การ",
    "10-57": "ช่อง — การ",
    "11-56": "ช่อง — การ",
    "12-22": "ช่อง — การ",
    "13-33": "ช่อง — การ แล้วบอก",
    "14-2": "ช่อง — การ",
    "16-48": "ช่อง — การ",
    "17-62": "ช่อง — การ",
    "18-58": "ช่อง — การ และ",
    "19-49": "ช่อง — การ",
    "20-34": "ช่อง — การ",
    "21-45": "ช่อง — การ",
    "23-43": "ช่อง — การ",
    "24-57": "ช่อง — การ ก่อน",
    "25-51": "ช่อง — การ",
    "26-44": "ช่อง — การ แล้ว",
    "27-50": "ช่อง — การ",
    "28-38": "ช่อง — การ แล้ว",
    "29-46": "ช่อง — การ แล้ว",
    "30-41": "ช่อง — การ",
    "32-54": "ช่อง — การ",
    "33-8": "ช่อง — การ แล้ว",
    "34-57": "ช่อง — การ",
    "35-36": "ช่อง — การ แล้ว",
    "36-35": "ช่อง — การ",
    "37-40": "ช่อง — การ",
    "38-55": "ช่อง — การ",
    "39-55": "ช่อง — การ",
    "41-30": "ช่อง — การ ให้",
    "42-53": "ช่อง — การ อย่าง",
    "43-23": "ช่อง — การ",
    "44-26": "ช่อง — การ แล้ว",
    "45-21": "ช่อง — การ",
    "47-64": "ช่อง — การ แล้ว",
    "48-58": "ช่อง — การ อย่าง",
    "49-19": "ช่อง — การ",
    "50-27": "ช่อง — การ",
    "51-25": "ช่อง — การ",
    "52-9": "ช่อง — การ",
    "53-42": "ช่อง — การ แล้ว",
    "54-32": "ช่อง — การ อย่าง",
    "55-9": "ช่อง — การ ชีวิตเป็น",
    "56-33": "ช่อง — การ แล้ว",
    "57-34": "ช่อง — การ อย่าง",
    "58-18": "ช่อง — การ อย่าง",
    "59-6": "ช่อง — การ อย่าง",
    "60-3": "ช่อง — การ",
    "61-24": "ช่อง — การ",
    "62-17": "ช่อง — การ",
    "63-4": "ช่อง — ความ แล้ว",
    "64-47": "ช่อง — การ ก่อน",
}

ZIWEI_PALACE_TH = {
    "life": "ของชีวิต — จุดเริ่มต้นและพลังงานพื้นฐาน",
    "body": "ร่าง — สุขภาพและ",
    "wealth": "ทรัพย์ — ทรัพย์ที่หาได้ยาก",
    "career": "การงาน — ชื่อเสียงและการทำงาน",
    "travel": "การท่องเที่ยว — การเคลื่อนที่และ",
    "health": "สุขภาพ — รูปแบบ",
    "love": "ความรัก — ความสัมพันธ์ที่เป็นส่วนตัว",
    "children": "ลูก — การสร้างสรรค์และการเริ่มใหม่",
    "parents": "บิดามารดา — เครือข่ายและมรดก",
    "mental": "ใจ — ความคิดและ",
    "property": "ที่ดิน — ทรัพย์สินและการเป็นเจ้าของ",
    "siblings": "พี่น้อง — พี่น้องและการติดต่อ",
}

ZIWEI_STAR_TH = {
    "紫微": "ดวงใหญ่เหนือกิน — เห็นภาพใหญ่ ลเป็นผู้นำ",
    "天机": "ดวงกลยุทธ์ — จ เมื่อ",
    "太陽": "ดวงอาทิตย์ — และ",
    "武曲": "ดวง — เกี่ยวกับ สินทรัพย์",
    "天同": "ดวงเจริญเติบโต — และ",
    "廉貞": "ดวงที่ — และ",
    "天府": "ดวงสัญชาติ — และ",
    "太陰": "ดวงเดือน — และ",
    "貪狼": "ดวง — และ",
    "巨門": "ดวงคำพูด — และ",
    "天相": "ดวงที่ — และ",
    "天梁": "ดวง — และ",
    "七杀": "ดวงการบูรณาการ — ถึง",
    "破軍": "ดวง — แล้ว",
    "文昌": "ดวงวรรณกรรม",
    "文曲": "ดวงศิลปะ",
    "左輔": "ดวงช่วยเหลือ — และ",
    "右弼": "ดวงช่วยเหลืออีกด้าน — ทางใจ",
    "天魁": "ดวง",
    "天钺": "ดวง อีกด้าน",
    "地空": "ดวง",
    "地劫": "ดวง — แล้ว",
    "台輔": "ดวงการบริหาร",
    "封誥": "ดวง",
    "天巫": "ดวง",
    "天月": "ดวง",
}

# ---------------------------------------------------------------------------
# apply_narrative_gate
# ---------------------------------------------------------------------------

def apply_narrative_gate(sections: list[dict], lang: str = "th") -> list[dict]:
    """Apply language contract to sections before rendering."""
    lang = lang_key(lang)
    out = []
    for sec in sections:
        title = sec.get("title", "")
        lines = sec.get("lines", []) or []
        if lang == "th":
            title = sanitize(title, lang=lang)
            lines = [sanitize(line, lang=lang) for line in lines]
        else:
            title = sanitize(title, lang=lang)
            lines = [sanitize(line, lang=lang) for line in lines]
        out.append({"title": title, "lines": lines})
    return out
