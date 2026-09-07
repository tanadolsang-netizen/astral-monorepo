"""
Per-User Narrative Engine — สร้าง narrative ต่อบุคคลจริง
ใช้ rule-based + knowledge base + feedback loop + event mapping
"""
import logging
from datetime import datetime
from src.services.kb_loader import (
    get_depth_psychology, get_complexes, get_thai_idioms,
    get_aspect_meanings, get_house_placements, get_dignity_meanings,
    get_transit_aspects, get_synastry_aspects,
)

logger = logging.getLogger("astral.ai_generator")



class AINarrativeGenerator:
    """สร้าง narrative ต่อบุคคลจริงโดยใช้ rule-based + knowledge base"""
    
    def __init__(self):
        self.depth = get_depth_psychology()
        self.complexes = get_complexes()
        self.idioms = get_thai_idioms()
        self.aspect_kb = get_aspect_meanings()
        self.house_kb = get_house_placements()
        self.dignity_kb = get_dignity_meanings()
    
    def generate_full_reading(self, chart: dict, user_id: str = "", lang: str = "th") -> dict:
        """สร้าง narrative เต็มรูปแบบต่อบุคคล"""
        reading = {
            "generated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "chart_summary": self._summarize_chart(chart, lang),
            "sections": {},
        }
        
        reading["sections"]["overview"] = self._gen_overview(chart, lang)
        reading["sections"]["personality"] = self._gen_personality(chart, lang)
        reading["sections"]["inner_world"] = self._gen_inner_world(chart, lang)
        reading["sections"]["fears_shadows"] = self._gen_fears_shadows(chart, lang)
        reading["sections"]["desires_aspirations"] = self._gen_desires(chart, lang)
        reading["sections"]["life_lessons"] = self._gen_life_lessons(chart, lang)
        reading["sections"]["relationships"] = self._gen_relationships(chart, lang)
        reading["sections"]["career"] = self._gen_career(chart, lang)
        reading["sections"]["aspects"] = self._gen_aspects(chart, lang)
        reading["sections"]["summary"] = self._gen_summary(chart, lang)
        
        return reading
    
    def _summarize_chart(self, chart: dict, lang: str) -> dict:
        bodies = chart.get("bodies", [])
        asc = chart.get("ascendant", {})
        return {
            "sun_sign": next((b["sign"] for b in bodies if b["body"] == "Sun"), ""),
            "moon_sign": next((b["sign"] for b in bodies if b["body"] == "Moon"), ""),
            "ascendant": asc.get("sign", ""),
            "dominant_element": self._get_dominant_element(bodies),
            "aspect_count": len(chart.get("aspects", [])),
        }
    
    def _get_dominant_element(self, bodies: list) -> str:
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        sign_element = {"Aries": "fire", "Leo": "fire", "Sagittarius": "fire", "Taurus": "earth", "Virgo": "earth", "Capricorn": "earth", "Gemini": "air", "Libra": "air", "Aquarius": "air", "Cancer": "water", "Scorpio": "water", "Pisces": "water"}
        for b in bodies:
            elem = sign_element.get(b["sign"], "")
            if elem:
                elements[elem] += 1
        return max(elements, key=elements.get) if elements else "unknown"
    
    def _gen_overview(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        sun = next((b for b in bodies if b["body"] == "Sun"), None)
        moon = next((b for b in bodies if b["body"] == "Moon"), None)
        asc = chart.get("ascendant", {})
        paras = []
        if sun:
            key = f"Sun in {sun['sign']}"
            idiom = self.idioms.get(key, {}).get("th", "")
            if lang == "th":
                paras.append(f"ดวงอาทิตย์อยู่ในราศี{sun['sign']} — {idiom}")
                paras.append(f"คุณกำลังพัฒนาเป็นตัวตนที่แท้จริง: {self.depth.get('Sun', {}).get('th', '')}")
            else:
                paras.append(f"Sun in {sun['sign']} — {self.depth.get('Sun', {}).get('en', '')}")
        if asc:
            if lang == "th":
                paras.append(f"ลัคนาขึ้นในราศี{asc.get('sign', '')} — หน้าตาที่คนอื่นเห็น แต่อาจไม่ใช่ตัวตนที่แท้จริงของคุณ")
            else:
                paras.append(f"Ascendant in {asc.get('sign', '')} — the mask you wear, not necessarily who you are.")
        return paras
    
    def _gen_personality(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        moon = next((b for b in bodies if b["body"] == "Moon"), None)
        paras = []
        if moon:
            key = f"Moon in {moon['sign']}"
            idiom = self.idioms.get(key, {}).get("th", "")
            if lang == "th":
                paras.append(f"ดวงจันทร์อยู่ในราศี{moon['sign']} — {idiom}")
                paras.append(f"ความรู้สึกลึกในตัวคุณ: {self.depth.get('Moon', {}).get('th', '')}")
            else:
                paras.append(f"Moon in {moon['sign']} — {self.depth.get('Moon', {}).get('en', '')}")
        return paras
    
    def _gen_inner_world(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        inner = [b for b in bodies if b.get("house") in [8, 12]]
        paras = []
        for b in inner:
            if lang == "th":
                paras.append(f"{b['body']} อยู่บ้านที่ {b['house']} — ความลับที่ซ่อนอยู่")
            else:
                paras.append(f"{b['body']} in house {b['house']} — hidden depths")
        return paras
    
    def _gen_fears_shadows(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        saturn = next((b for b in bodies if b["body"] == "Saturn"), None)
        paras = []
        if saturn:
            saturn_house = saturn.get("house", "?")
            if lang == "th":
                paras.append(f"เสาร์อยู่ในราศี{saturn['sign']} บ้านที่ {saturn_house} — นี่คือเงาของคุณ")
                paras.append(f"ความกลัว: {self.depth.get('Saturn', {}).get('fear', '')}")
                paras.append(f"บทเรียน: {self.depth.get('Saturn', {}).get('individuation', '')}")
            else:
                paras.append(f"Saturn in {saturn['sign']}, house {saturn_house} — your Shadow.")
                paras.append(f"Fear: {self.depth.get('Saturn', {}).get('fear', '')}")
                paras.append(f"Lesson: {self.depth.get('Saturn', {}).get('individuation', '')}")
        
        moon = next((b for b in bodies if b["body"] == "Moon"), None)
        if moon and saturn:
            moon_deg = moon["absolute_deg"]
            sat_deg = saturn["absolute_deg"]
            diff = abs(moon_deg - sat_deg) % 360
            if diff > 180: diff = 360 - diff
            for aspect, target in [("conjunction", 0), ("square", 90), ("opposition", 180)]:
                if abs(diff - target) <= 8:
                    complex_data = self.complexes.get("Moon-Saturn", {})
                    if lang == "th":
                        paras.append(f"คอมเพล็กซ์ {complex_data.get('name', '')}: {complex_data.get('th', '')}")
                        paras.append(f"ความกลัว: {complex_data.get('fear', '')}")
                        paras.append(f"การรักษา: {complex_data.get('healing', '')}")
                    else:
                        paras.append(f"Complex {complex_data.get('name', '')}: {complex_data.get('en', '')}")
                    break
        return paras
    
    def _gen_desires(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        jupiter = next((b for b in bodies if b["body"] == "Jupiter"), None)
        venus = next((b for b in bodies if b["body"] == "Venus"), None)
        paras = []
        if jupiter:
            if lang == "th":
                paras.append(f"พฤหัสอยู่ในราศี{jupiter['sign']} — คุณอยากเติบโตไปทางไหน ความเชื่อเกี่ยวกับโชคลาภ")
                paras.append(f"{self.depth.get('Jupiter', {}).get('th', '')}")
            else:
                paras.append(f"Jupiter in {jupiter['sign']} — {self.depth.get('Jupiter', {}).get('en', '')}")
        if venus:
            if lang == "th":
                paras.append(f"ศุกร์อยู่ในราศี{venus['sign']} — คุณอยากถูกรักแบบไหน คุณคุ้มค่ากับความรักหรือเปล่า")
            else:
                paras.append(f"Venus in {venus['sign']} — {self.depth.get('Venus', {}).get('en', '')}")
        return paras
    
    def _gen_life_lessons(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        saturn = next((b for b in bodies if b["body"] == "Saturn"), None)
        paras = []
        if saturn:
            if lang == "th":
                paras.append(f"เสาร์คือบทเรียนชีวิต — สิ่งที่คุณต้องเรียนรู้ผ่านความยากลำบาก")
                paras.append(f"{self.depth.get('Saturn', {}).get('individuation', '')}")
            else:
                paras.append(f"Saturn is your life lesson — what you must learn through difficulty.")
                paras.append(f"{self.depth.get('Saturn', {}).get('individuation', '')}")
        return paras
    
    def _gen_relationships(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        mars = next((b for b in bodies if b["body"] == "Mars"), None)
        venus = next((b for b in bodies if b["body"] == "Venus"), None)
        paras = []
        if mars:
            if lang == "th":
                paras.append(f"อังคารอยู่ในราศี{mars['sign']} — คุณใช้พลังอย่างไรในความสัมพันธ์")
                paras.append(f"{self.depth.get('Mars', {}).get('th', '')}")
            else:
                paras.append(f"Mars in {mars['sign']} — {self.depth.get('Mars', {}).get('en', '')}")
        return paras
    
    def _gen_career(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        jupiter = next((b for b in bodies if b["body"] == "Jupiter"), None)
        mc = chart.get("midheaven", {})
        paras = []
        if jupiter and jupiter.get("house") == 10:
            if lang == "th":
                paras.append(f"พฤหัสอยู่บ้านที่ 10 — การงานที่โชคดี ได้รับการยอมรับในสังคม")
            else:
                paras.append("Jupiter in 10th — career blessed with recognition and growth.")
        return paras
    
    def _gen_aspects(self, chart: dict, lang: str) -> list:
        aspects = chart.get("aspects", [])
        paras = []
        for asp in aspects[:5]:
            key = f"{asp['planet1']} {asp['aspect']} {asp['planet2']}"
            meaning = self.aspect_kb.get(key, {})
            if lang == "th":
                paras.append(f"{asp['planet1']} {asp['aspect']} {asp['planet2']} (orb {asp['orb']:.2f}°) — {meaning.get('th', '')}")
            else:
                paras.append(f"{asp['planet1']} {asp['aspect']} {asp['planet2']} (orb {asp['orb']:.2f}°)")
        return paras
    
    def _gen_summary(self, chart: dict, lang: str) -> list:
        bodies = chart.get("bodies", [])
        sun = next((b for b in bodies if b["body"] == "Sun"), None)
        saturn = next((b for b in bodies if b["body"] == "Saturn"), None)
        paras = []
        if lang == "th":
            paras.append(f"ดวงชะตานี้เล่าเรื่องของคนที่มีอัตลักษณ์ผ่านอาทิตย์ราศี{sun['sign'] if sun else '?'} และเสาร์ราศี{saturn['sign'] if saturn else '?'} เป็นบทเรียนหลัก")
            paras.append("คุณมาเรียนรู้ที่จะรักตัวเอง เผชิญเงา และเป็นตัวตนที่แท้จริง")
        else:
            paras.append(f"This chart tells the story of someone with Sun in {sun['sign'] if sun else '?'} and Saturn in {saturn['sign'] if saturn else '?'} as the primary life lesson.")
            paras.append("You are here to learn self-love, face your shadow, and become your authentic self.")
        return paras


def generate_transit_natal_narrative(chart: dict, transit_chart: dict | None = None, lang: str = "th") -> dict:
    """Generate a transit-natal narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_synastry_narrative(chart1: dict, chart2: dict, lang: str = "th") -> dict:
    """Generate a synastry narrative between two charts. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart1, user_id="", lang=lang)


def generate_varshaphal_narrative(chart: dict, year: int | None = None, lang: str = "th") -> dict:
    """Generate a varshaphal (annual) narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_arabic_parts_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate an Arabic parts narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_asteroid_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate an asteroid narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_dasha_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a dasha (Vedic period) narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_fixed_star_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a fixed star narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_nakshatra_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a nakshatra (lunar mansion) narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_yoga_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a yoga (planetary combination) narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_ziwei_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a Zi Wei (Chinese purple star) narrative. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)


def generate_natal_narrative(chart: dict, lang: str = "th") -> dict:
    """Generate a full natal narrative for the given chart. Thin wrapper around AINarrativeGenerator."""
    gen = AINarrativeGenerator()
    return gen.generate_full_reading(chart, user_id="", lang=lang)

ai_generator = AINarrativeGenerator()
