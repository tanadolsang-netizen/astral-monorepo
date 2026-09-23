"""Centralized legal/ethical disclaimers — FTC-consistent framing."""

from __future__ import annotations

DISCLAIMER_TH = (
    "เนื้อหาเพื่อการไตร่ตรองและความบันเทิง ไม่ใช่คำแนะนำทางการแพทย์ "
    "การเงิน หรือกฎหมาย โปรดใช้วิจารณญาณในการตัดสินใจ"
)
DISCLAIMER_EN = (
    "For reflection and entertainment only. Not medical, financial, "
    "or legal advice. Please use your own judgment."
)

# categories we refuse to answer with fortune-telling
REFUSAL_CATEGORIES = {
    "medical": {
        "keywords": ["มะเร็ง", "ป่วย", "โรค", "ยา", "รักษา", "ผ่าตัด",
                     "cancer", "diagnos", "medicine", "surgery", "cure"],
        "th": ("เรื่องสุขภาพควรปรึกษาแพทย์นะครับ — ด้านโหราศาสตร์ชวนดูแลตัวเองได้ "
               "แต่ไม่ใช่การวินิจฉัย 🙏"),
        "en": "Health questions belong to doctors. Astrology can't diagnose.",
    },
    "finance_specific": {
        "keywords": ["หุ้น", "คริปโต", "bitcoin", "stock", "crypto",
                     "ลงทุนตัวไหน", "forex"],
        "th": ("การลงทุนเฉพาะตัวควรปรึกษาผู้เชี่ยวชาญด้านการเงินครับ "
               "ดวงมองภาพรวมการเงินได้ แต่ไม่ชี้หุ้นตัวใดตัวหนึ่ง"),
        "en": "Specific investments need a licensed advisor; I read general money climate only.",
    },
    "death_prediction": {
        "keywords": ["ตาย", "เสียชีวิต", "อายุขัยถึง", "when will i die",
                     "death date"],
        "th": "อาจารย์ไม่ทำนายเรื่องความตายครับ — ชีวิตที่เหลือให้ใช้อย่างมีค่าดีกว่า",
        "en": "I don't predict death. Let's focus on living well.",
    },
    "pregnancy_prediction": {
        "keywords": ["ตั้งครรภ์", "ท้อง", "pregnant", "conceive"],
        "th": "เรื่องการตั้งครรภ์ควรปรึกษาแพทย์ครับ ดวงไม่ใช่เครื่องมือการแพทย์",
        "en": "Pregnancy is a medical matter, not an astrology one.",
    },
}


def detect_refusal(message: str) -> str | None:
    """Return refusal category key if the message hits a guarded topic."""
    low = message.lower()
    for cat, spec in REFUSAL_CATEGORIES.items():
        if any(k in low for k in spec["keywords"]):
            return cat
    return None


def refusal_reply(category: str, lang: str = "th") -> str:
    spec = REFUSAL_CATEGORIES.get(category)
    if not spec:
        return ""
    return spec["th"] if lang == "th" else spec["en"]


def wrap_with_disclaimer(text: str, lang: str = "th") -> str:
    disc = DISCLAIMER_TH if lang == "th" else DISCLAIMER_EN
    return f"{text}\n\n— {disc}"
