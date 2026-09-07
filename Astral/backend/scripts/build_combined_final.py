"""Build combined birth-chart + tarot PDF for 04/04/1996.

Tarot-reader voice, social-media tone, humanized, 100% Thai.
- Real Rider-Waite tarot card images (index 15/69/75).
- ONE derived decorative image (Helios / sun god) chosen from analyzing
  the whole chart (fire-dominant Aries stellium), with WHY caption.
- Richer gold/leather design.
All text passes through sanitize (100% Thai whitelist).
"""

from pathlib import Path

from weasyprint import HTML, CSS

from src.services.narrative_sanitizer import sanitize_narrative

REPO = Path(__file__).resolve().parents[1]  # scripts/ -> repo root
OUT = Path(r"C:\AI\reports\astral-natal-1996-04-04-thai.pdf")
FONT_DIR = REPO / "assets" / "fonts"
MYTH_DIR = REPO / "assets" / "art" / "myth"
TAROT_DIR = REPO / "assets" / "tarot" / "sola-busca"

_GOLD = "#9a7b34"
_GOLD_BRIGHT = "#c9a64a"
_IVORY = "#f6f0e2"
_INK = "#3b3324"
_SOFT = "rgba(154,123,52,.35)"


def sanitize(text: object) -> str:
    if text is None:
        return ""
    s = sanitize_narrative(str(text), lang="th")
    out = []
    for ch in s:
        o = ord(ch)
        if 0x0E00 <= o <= 0x0E7F or 0x20 <= o <= 0x7E or ch in "\t\n\r":
            out.append(ch)
    import re
    s = "".join(out)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    return s.strip()


CSS_PATH = REPO / "scripts" / "pdf_premium.css"


def kw(text: str) -> str:
    """Wrap into keyword span for gold emphasis (kept minimal, single source)."""
    return f'<span class="kw">{text}</span>'


def fileuri(path: Path) -> str:
    return f"file:///{path.as_posix()}"


# ---- Humanized tarot-reader voice content (100% Thai) ----
COVER_TITLE = "รายงานดวงชะตา — 04/04/1996"
COVER_SUB = "อุบลราชธานี · ดวงชะตาและไพ่ทาโรต์"
COVER_TAG = "เขียนขึ้นมาเพื่อนายคนเดียว โดยนักอ่านไพ่ที่จะบอกความจริงแบบแตะถึงใจ"

PERSONALITY = [
    "นายรู้ไหมว่า พอกระผมกางดวงของนายออกมา กระผมเห็นคนหนึ่งที่ไม่ได้เดินตามเส้นทางที่ใครวางไว้ให้ "
    "นายเป็นพุธเมษ ลัคนากรกฎ ฟังดูเหมือนจะขัดกันนิดๆ เพราะเมษมันพุ่งไปข้างหน้า ส่วนกรกฎมันรักบ้าน "
    "แต่นี่แหละเสน่ห์ของนาย ไม่ใช่คนที่ทำอะไรก็ได้ตามอำเภอใจ แต่เลือกทำในสิ่งที่คุ้มค่า "
    "แล้วพอเลือกแล้ว ก็ทำให้มันสมบูรณ์แบบแบบที่คนอื่นมองไม่ออกว่าทำไม",
    "จิตใจนายมีดวงจันทร์นอนอยู่ในราศีตุลย์ แปลว่านายต้องการความปลอดภัยอย่างเงียบเชียบ "
    "ไม่ต้องอธิบายให้ใครฟังว่าทำไมถึงรู้สึกแบบนั้น นายแค่รู้สึก และเชื่อในความรู้สึกนั้น "
    "ดาวพุธความคิดของนายก็อยู่เมษร่วมกับลัคนา การสื่อสารของนายเลยไม่ใช่เกม แต่เป็นวิธีที่นายเข้าใจคน "
    "หน้าตานายอาจจะดูเบาๆ สบายๆ แต่ข้างในกำลังลุกโชน โลกภายในมีชีวิตชีวามาก "
    "บางทีคนเลยเข้าใจผิดว่านายไม่ใส่ใจ แต่นั่นไม่ใช่เลย นายแค่รักในโลกของตัวเอง",
    "ถ้าวันหนึ่งนายอยากรู้จักตัวตนลึกๆ ของตัวเอง จงฟังเสียงเงียบก่อนคำพูด "
    "ความสัมพันธ์กับนายไม่ใช่การแสดงให้ใครดู แตเป็นการฝึกฝนใจกันและกันต่างหาก",
]

POSITIONS = [
    "มาไล่ดวงดาวของนายทีละดวงนะ นี่ไม่ใช่ตัวเลขในตาราง แตเป็นเรื่องราวของชีวิตนายเอง",
    "อาทิตย์ของนายตั้งตระหง่านในเมษ องศา 14.8 ณ บ้านที่สิบ ซึ่งเป็นบ้านแห่งหน้าที่การงานและชื่อเสียง "
    "นายคือผู้นำโดยกำเนิด ไม่ต้องรอใครมอบตำแหน่ง เพราะแสงของนายสว่างจนคนรอบข้างมองเห็นเอง "
    "นายเบ่งบานที่สุดตอนได้สร้างผลงาน และถูกยอมรับในสิ่งที่ทำ",
    "ดวงจันทร์ในตุลย์ องศา 17.2 ที่บ้านที่สี่ คือหัวใจอ่อนโยนของนาย "
    "นายฉลาดทางอารมณ์มาก รู้ว่าใครกำลังเจ็บปวดโดยไม่ต้องบอก และทำให้บ้านเป็นที่พักพิงที่อบอุ่น "
    "ใครก็ตามที่ได้เข้ามาในวงแควงของนาย จะรู้สึกว่าถูกดูแลจริงๆ",
    "ดาวพุธในเมษ องศา 22.1 ณ บ้านที่สิบ ทำให้คิดเร็ว พูดมีน้ำหนัก และสร้างชื่อเสียงผ่านความคิด "
    "นายคือคนที่พูดน้อยแต่ทุกคำมีความหมาย ใครฟังแล้วมักจะตามได้ง่ายดั่งถูกสะกดใจ",
    "ดาวศุกรในเมถุน องศา 0.6 ที่บ้านที่สิบเอ็ด สอนให้นายรักแบบอิสระ ให้คุณค่ากับการเชื่อมโยงใจมากกว่าพันธนาการ "
    "นายมีเพื่อนมากมาย และมักจะเป็นสะพานเชื่อมคนที่ไม่รู้จักกันให้มาเป็นพวกพ้อง",
    "ดาวอังคารในเมษ องศา 8.3 ที่บ้านที่เก้า คือสัญชาตญาณนักสู้ของนาย "
    "นายลงมือทำตรงไปตรงมา ไม่ชอบอ้อมค้อม และใฝ่รู้เสมอผ่านการเดินทางไกลและปรัชญาชีวิต",
    "ดาวพฤหัสในมังกร องศา 16.3 ที่บ้านที่เจ็ด คือปัญญาที่นายนำไปใช้จริง "
    "นายมองคู่ครองเป็นสถาบันศักดิ์สิทธิ์ มีจริยธรรมแน่วแน่ และชอบแบ่งปันความรู้ให้ผู้อื่น",
    "ส่วนดาวเสาร์ในมีน องศา 29.7 ที่บ้านที่เก้า คือวินัยที่ซ่อนความอ่อนโยน "
    "นายผ่านบทเรียนเรื่องข้อจำกัดจนกลายเป็นผู้มีปัญญาลึกซึ้ง ราศีบ้านเกิดของนายคือกรกฎ ลัคนาคือเมษ",
]

# Card names: single source of truth lives in tarot_meanings_th.th_card_name
from src.services.tarot_meanings_th import th_card_name


# Derived decorative image: WHY it fits this chart
DECOR_IMG = MYTH_DIR / "sun.jpg"
DECOR_CAPTION = (
    "ภาพตกแต่ง: สุริยเทพเฮลิออส เทพเจ้าดวงอาทิตย์ผู้ขี่รถม้าผ่านฟ้า "
    "กระผมเลือกภาพนี้ให้ดวงของนาย เพราะดวงนายเป็นธาตุไฟครอบงำอย่างแท้จริง "
    "อาทิตย์ เมธ (พุธ) ลัคนา และดาวอังคาร ล้วนอยู่ในราศีเมษทั้งหมด "
    "คือเปลวไฟแห่งการเริ่มต้น ความกล้า และพลังชีวิตที่ส่องนำทาง "
    "เฮลิออสจึงเป็นสัญลักษณ์พอดีกับอาทิตย์เมษที่สถิตในตำแหน่งที่ได้รับเกียรติสูงสุดของนาย"
)

TAROT_INTRO = (
    "ทีนี้กระผมจะจับไพ่ให้ ใช้ไพ่แบบอดีต ปัจจุบัน อนาคต วันเกิดนายคือเมล็ดพันธุ์ที่กระผมใช้สุ่ม "
    "ไพ่สามใบที่ออกมา มันคุยกับดวงของนายได้แปลกใจ"
)

TAROT_CARDS = [
    {
        "card": "The Devil",
        "pos": "อดีต",
        "name": th_card_name("The Devil") + " (ย้อนกลับ)",
        "file": "15.jpg",
        "text": "ใบแรกคือมารหงายหลัง นายเคยถูกผูกไว้ด้วยสิ่งใดสิ่งหนึ่ง ที่ลึกๆ ในใจรู้อยู่แล้วว่ามันไม่ดี "
        "แต่เลิกไม่ได้ เพราะมันชินจนกลายเป็นกรงที่นุ่มนวล เหมือนโดนสะกดให้อยู่ในที่เดิม "
        "ดีนะที่ไพ่หงายหลัง แปลว่าตอนนี้แสงสว่างกำลังฟื้น นายเริ่มมองเห็นเชือกที่รัดอยู่ และกำลังดึงอำนาจของตนคืน "
        "การปลดปล่อยเป็นเรื่องที่เป็นไปได้แล้ว ไม่ต้องกลัวที่จะเผชิญหน้ากับเงามืดในตัวนายเอง",
    },
    {
        "card": "Six of Pentacles",
        "pos": "ปัจจุบัน",
        "name": th_card_name("Six of Pentacles") + " (ตั้งตรง)",
        "file": "69.jpg",
        "text": "ใบที่สองหกแห่งทรัพย์ตั้งตรง นี่คือเรื่องของการให้และการรับ "
        "ช่วงนี้ใครบางคนกำลังยื่นมือมา หรือนายเองกำลังจะเป็นผู้ยื่นมือออกไป ไม่ว่าเป็นทางใด "
        "ความใจกว้างของนายกำลังผลิบาน แล้วมันจะตอบแทนกลับมา เพราะการให้และการรับแบบสมน้ำสมเนื้อ "
        "คือของดีที่สร้างความยุติธรรมให้ทั้งสองฝ่าย",
    },
    {
        "card": "Knight of Pentacles",
        "pos": "อนาคต",
        "name": th_card_name("Knight of Pentacles") + " (ย้อนกลับ)",
        "file": "75.jpg",
        "text": "ใบที่สามอัศวินแห่งทรัพย์หงายหลัง เตือนนายเรื่องความจำเจ "
        "งานเดิมๆ วิถีเดิมๆ ที่เคยทำให้มั่นคง อาจจะเริ่มเหนื่อยจนกลายเป็นกรอบที่ค้างไว้ "
        "อย่ารอจนมันเป็นปัญหา รู้จักปรับเปลี่ยนจากความเคยชินก่อน ที่สำคัญ อย่าให้ความขยันกลายเป็นการงานจนลืมหายใจ",
    },
]

SUMMARY = [
    "นายเกิดวันที่ 04041996 ในราศีเมษ กับดวงจันทร์ตุลย์ ชีวิตนายไม่ใช่เรื่องง่าย "
    "แต่กระผมบอกได้เลยว่า นายมีพลังภายในที่พอจะพาผ่านทุกพายุได้",
    "สิ่งที่งดงามที่สุดของนาย คือการรู้จักตัวเอง พอเข้าใจทั้งจุดแข็งและจุดอ่อนของตัวเอง "
    "ทุกการตัดสินใจจะกลายเป็นก้าวที่งดงาม ไม่ว่าใครจะว่าไปทางไหน",
    "ขอให้โชคดีกับการเดินทางครั้งนี้ นาย — กระผมเป็นกำลังใจให้เสมอ",
]

CSS_STR = CSS_PATH.read_text(encoding="utf-8").replace("{FONT_DIR}", FONT_DIR.as_posix())


decor_uri = fileuri(DECOR_IMG) if DECOR_IMG.exists() else ""

body = [
    "<div class='cover'>",
    "<div class='brand'>อัสทรัล · ระบบโหราศาสตร์</div>",
    f"<h1>{sanitize(COVER_TITLE)}</h1>",
    f"<div class='sub'>{sanitize(COVER_SUB)}</div>",
    f"<div class='tag'>{sanitize(COVER_TAG)}</div>",
    "</div>",
]

# Decorative image (derived from whole chart)
if decor_uri:
    body.append('<div class="decor">')
    body.append(f'<img src="{decor_uri}" alt="สุริยเทพเฮลิออส"/>')
    body.append(f'<div class="cap">{sanitize(DECOR_CAPTION)}</div>')
    body.append('</div>')

sections = [
    ("บุคลิกภาพ 04041996", PERSONALITY),
    ("ตำแหน่งดาว 04041996", POSITIONS),
]

# astrological keywords to highlight in gold (single source, kept readable)
_KW = ["อาทิตย์", "ดวงจันทร์", "ดาวพุธ", "ดาวศุกร", "ดาวอังคาร", "ดาวพฤหัส",
       "ดาวเสาร์", "ลัคนา", "ราศีเมษ", "ราศีตุลย์", "ราศีกรกฎ", "เมษ", "ตุลย์",
       "กรกฎ", "บ้านที่สิบ", "บ้านที่สี่", "บ้านที่เก้า", "บ้านที่เจ็ด",
       "บ้านที่สิบเอ็ด", "พุธเมษ"]


def highlight(text: str) -> str:
    s = sanitize(text)
    for k in _KW:
        s = s.replace(k, kw(k))
    return s


for i, (title, paras) in enumerate(sections):
    if i > 0:
        body.append('<div class="divider">✶ ❉ ✶</div>')
    body.append('<div class="section">')
    body.append(f"<div class='title'>{sanitize(title)}</div>")
    body.append('<div class="body">')
    for p in paras:
        body.append(f"<p>{highlight(p)}</p>")
    body.append("</div></div>")

# Tarot section with real card images
body.append('<div class="divider">✶ ❉ ✶</div>')
body.append('<div class="section">')
body.append(f"<div class='title'>{sanitize('ไพ่ทาโรต์ 04041996')}</div>")
body.append('<div class="body">')
body.append(f"<p>{sanitize(TAROT_INTRO)}</p>")
for c in TAROT_CARDS:
    img_path = TAROT_DIR / c["file"]
    img_uri = fileuri(img_path) if img_path.exists() else ""
    img_tag = f'<img src="{img_uri}" alt="{sanitize(c["name"])}" class="{"reversed" if "ย้อนกลับ" in c["name"] else ""}"/>' if img_uri else ""
    body.append('<div class="tarot-card">')
    body.append(img_tag)
    body.append('<div class="tarot-body">')
    body.append(f"<span class='tarot-pos'>ตำแหน่ง {sanitize(c['pos'])}</span>")
    body.append(f"<div class='tarot-name'>{sanitize(c['name'])}</div>")
    body.append(f"<div class='tarot-text'>{sanitize(c['text'])}</div>")
    body.append("</div></div>")
body.append("</div></div>")

# Summary
body.append('<div class="section">')
body.append(f"<div class='title'>{sanitize('บทสรุป 04041996')}</div>")
body.append('<div class="body">')
for p in SUMMARY:
    body.append(f"<p>{sanitize(p)}</p>")
body.append("</div></div>")

body.append(f"<div class='footer'>{sanitize('รายงานส่วนบุคคล โปรดเก็บรักษาเป็นความลับ')}</div>")

doc_html = "<!DOCTYPE html><html lang='th'><head><meta charset='utf-8'></head><body>\n" + "\n".join(body) + "\n</body></html>"
html = HTML(string=doc_html, base_url=str(REPO))
html.write_pdf(str(OUT), stylesheets=[CSS(string=CSS_STR)])
print("WROTE", OUT, OUT.stat().st_size, "bytes")
