# 07 · TAROT ENGINE SPEC — Daily Card & Spreads Module
> **EN:** Deterministic seeded tarot engine (RWS deck). Same user + same day = same cards, always replayable.
> **TH:** เอนจินทาโรต์แบบ deterministic — user เดิม + วันเดียวกัน = ไพ่ชุดเดิมเสมอ (ตรวจซ้ำได้)

---

## 1 · Deck structure (Rider-Waite-Smith, 78 cards)
- **22 Major Arcana** (0 Fool → 21 World) — astrological correspondences: 0 Fool=Uranus, 1 Magician=Mercury, 2 High Priestess=Moon, 3 Empress=Venus, 4 Emperor=Aries, 5 Hierophant=Taurus, 6 Lovers=Gemini, 7 Chariot=Cancer, 8 Strength=Leo, 9 Hermit=Virgo, 10 Wheel=Jupiter, 11 Justice=Libra, 12 Hanged Man=Neptune, 13 Death=Scorpio, 14 Temperance=Sagittarius, 15 Devil=Capricorn, 16 Tower=Mars, 17 Star=Aquarius, 18 Moon=Pisces, 19 Sun=Sun, 20 Judgement=Pluto, 21 World=Saturn
- **56 Minor Arcana:** Wands=Fire (Aries/Leo/Sag) · Cups=Water (Cancer/Scorpio/Pisces) · Swords=Air (Gemini/Libra/Aquarius) · Pentacles=Earth (Taurus/Virgo/Capricorn); Ace–10 = decan progression, Courts = Page/Knight/Queen/King

## 2 · Reversal policy (v1 — ONE choice, deterministic)
**Chosen: "no reversals; shadow meaning folded upright."** Justification: (a) reproducible UX — users comparing replays see identical text; (b) biddytarot methodology in vault treats reversal as *context-dependent intensity*, which the engine already expresses via the transit-fusion confidence flag; (c) halves the interpretation corpus to maintain at launch. Reversal layer = v2 feature flag (50% coin-flip from seed byte 78).

## 3 · Deterministic seeding (Fisher–Yates)
```python
import hashlib
def draw_cards(user_id, iso_date, spread, salt="hermes-tarot-v1", n=1):
    seed = hashlib.sha256(f"{user_id}|{iso_date}|{spread}|{salt}".encode()).digest()
    deck = list(range(78))
    for i in range(77, 0, -1):                 # Fisher-Yates from seed bytes
        j = seed[i % len(seed)] % (i + 1)
        deck[i], deck[j] = deck[j], deck[i]
    return deck[:n]
```
Replay property: identical inputs → identical shuffle (verified by test vectors [BUILD-TIME: assert two calls equal]).

## 4 · Spreads (v1)
| Spread | Positions |
|---|---|
| Daily single | 1 = theme of day |
| Three-card | 1 Past · 2 Present · 3 Trajectory |
| Relationship (5) | 1 You · 2 Them · 3 Bond-now · 4 Block · 5 Direction |
| Celtic Cross (10) | 1 Heart · 2 Crossing · 3 Root · 4 Recent past · 5 Crown · 6 Near future · 7 Self · 8 Environment · 9 Hopes/fears · 10 Outcome |
| Yes/No | card polarity table: upright Majors 0–17 = yes-leaning, 13 Death/15 Devil/16 Tower = "no-as-warning", courts = "ask again with action" — full 78-row polarity JSON [BUILD-TIME from Waite text] |

## 5 · Card JSON schema (5 fully written; remaining 73 same schema from public-domain Waite text)
```json
{"id": 0, "name": "The Fool", "cn_arc": "major", "element": "air", "astro": "Uranus",
 "upright": {"kw_en": ["beginnings","innocence","leap of faith"], "kw_th": ["จุดเริ่มต้น","ความบริสุทธิ์","ก้าวกระโดดด้วยศรัทธา"],
   "love": "A fresh start asks for trust before proof.", "love_th": "จุดเริ่มใหม่ต้องการความไว้ใจก่อนหลักฐาน",
   "career": "Say yes to the untested path; pack light.", "career_th": "ตอบตอบทางที่ยังไม่มีใครทดสอบ — เดินเบาๆ",
   "money": "Speculative but survivable if small.", "money_th": "เสี่ยงได้แต่ต้องเล็กพอที่จะรอด",
   "health": "New routine begins well if started gently.", "health_th": "เริ่มกิจวัตรใหม่ได้ดีถ้าเริ่มแบบนุ่มนวล"}},
{"id": 1, "name": "The Magician", "element": "air", "astro": "Mercury",
 "upright": {"kw_en": ["manifestation","skill","focus"], "kw_th": ["การปั้นให้เป็นจริง","ฝีมือ","สมาธิ"],
   "love": "Communicate desire clearly; you hold all the tools.", "love_th": "พูดสิ่งที่ต้องการให้ชัด — ทุกเครื่องมืออยู่ในมือ",
   "career": "Pitch it now; your skill is visible.", "career_th": "นำเสนอตอนนี้เลย ฝีมือกำลังถูกมองเห็น",
   "money": "Turn skill into invoice.", "money_th": "แปลงฝีมือเป็นรายได้",
   "health": "Discipline over the body works now.", "health_th": "วินัยกับร่างกายให้ผลตอนนี้"}},
{"id": 2, "name": "The High Priestess", "element": "water", "astro": "Moon",
 "upright": {"kw_en": ["intuition","mystery","inner voice"], "kw_th": ["สัญชาตญาณ","ความลึกลับ","เสียงข้างใน"],
   "love": "Something unspoken wants listening, not solving.", "love_th": "มีบางอย่างไม่ได้พูด — ฟัง อย่ารีบแก้",
   "career": "Hold your plan one more cycle before revealing.", "career_th": "เก็บแผนไว้อีกหนึ่งรอบก่อนเปิดเผย",
   "money": "Hidden info: read the fine print.", "money_th": "มีข้อมูลซ่อนอยู่ — อ่านตัวเล็กให้ครบ",
   "health": "Sleep and dreams carry the signal.", "health_th": "การนอนและฝันคือสัญญาณ"}},
{"id": 16, "name": "The Tower", "element": "mars", "astro": "Mars",
 "upright": {"kw_en": ["upheaval","revelation","necessary collapse"], "kw_th": ["การพังทลาย","การเปิดเผย","การล้มที่จำเป็น"],
   "love": "A false structure breaks so a true one can stand.", "love_th": "โครงสร้างเทียมพัง เพื่อของจริงจะยืนได้",
   "career": "Sudden change of structure — do not cling.", "career_th": "โครงสร้างเปลี่ยนฉับพลัน — อย่าเกาะ",
   "money": "Cut losses fast; rebuild on rock.", "money_th": "ตัดขาดทุนไว แล้วสร้างใหม่บนหิน",
   "health": "Address the ignored warning now.", "health_th": "จัดการสัญญาณเตือนที่เมินไว้ตอนนี้"}},
{"id": 78, "name": "Ten of Pentacles", "element": "earth", "astro": "Mercury/Virgo decan",
 "upright": {"kw_en": ["legacy","family wealth","long-term security"], "kw_th": ["มรดก","ทรัพย์ตระกูล","ความมั่นคงระยะยาว"],
   "love": "Family blessing energy; think generations.", "love_th": "พลังพรใจจากครอบครัว — คิดระยะข้ามรุ่น",
   "career": "Build the institution, not the gig.", "career_th": "สร้างสถาบัน ไม่ใช่งานชิ้นเดียว",
   "money": "Long-horizon assets favored.", "money_th": "สินทรัพย์ระยะยาวได้เปรียบ",
   "health": "Ancestral patterns: check family history.", "health_th": "แพทเทิร์นจากสายเลือด — เช็คประวัติครอบครัว"}}
```

## 6 · Astro-tarot fusion (with 01-transit module)
```
if transit_hit_today exists AND card.element matches transit body's element:
    confidence = HIGH, template adds: "ไพ่ [X] ตรงธาตุกับ transit [Y] ที่กำลังชน [natal point]"
elif card.element in generative-cycle(transit element): confidence = MED+
```
Example (test case): transit Jupiter over natal IC (fire) + daily card = Tower (Mars/fire) → HIGH flag.

## 7 · Output templates
- Daily TH: *"ไพ่ประจำวัน: [ชื่อไทย] — [kw_th] · [facet line by user's chosen focus] · [fusion note]"*
- Daily EN: *"Card of the day: [Name] — [keywords] · [facet line] · [fusion note]"*
- Spread TH/EN: per-position lines joined with "·", ending with synthesis sentence (1 line max).
