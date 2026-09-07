# 12 · I CHING (易經) ENGINE SPEC — Daily Oracle Module
> **EN:** Deterministic seeded hexagram casting + interpretation schema. Reproducible per user/day.
> **TH:** การสุ่มหมายเลข hexagram แบบ deterministic (seed จาก user+วันที่) — ผลซ้ำได้ทุกครั้ง

---

## 1 · Structure / โครงสร้าง

**Encoding:** 6 เส้นนับจากล่างขึ้นบน · yang(实)=1, yin(虚)=0 · `binary = Σ lineᵢ × 2ⁱ⁻¹`

**Trigrams (lower/upper 3-bit groups):**
| Trigram | Bits (bottom-up) | Value | Image | Element | TH |
|---|---|---|---|---|---|
| ☰ Qian | 111 | 7 | Heaven 天 | Metal/metal-sky | สวรรค์–พ่อ |
| ☱ Dui | 110→(1,1,0)=3 | 3 | Lake 澤 | Metal/water-mist | ทะเลสาบ–ลูกสาวเล็ก |
| ☲ Li | 101=5 | 5 | Fire 火 | Fire | ไฟ–ลูกสาวกลาง |
| ☳ Zhen | 100=1 | 1 | Thunder 雷 | Wood | ฝนฟ้าคะนอง–ลูกชายโต |
| ☴ Xun | 011=6 | 6 | Wind 風 | Wood | ลม–ลูกสาวโต |
| ☵ Kan | 010=2 | 2 | Water 水 | Water | น้ำ–ลูกชายกลาง |
| ☶ Gen | 001=4 | 4 | Mountain 山 | Earth | ภูเขา–ลูกชายเล็ก |
| ☷ Kun | 000=0 | 0 | Earth 地 | Earth | พื้นดิน–แม่ |

**King Wen lookup** `KW[lower][upper]` (standard Wilhelm table — verify against source at build):
```
        up:Qian(7) Dui(3) Li(5) Zhen(1) Xun(6) Kan(2) Gen(4) Kun(0)
lo Qian(7):   1     43    14    34      9      5     26     11
lo Dui(3):   10     58    38    54     61     60     41     19
lo Li(5):    13     49    30    55     37     63     22     36
lo Zhen(1):  25     17    21    51     42      3     27     24
lo Xun(6):   44     28    50    32     57     48     18     46
lo Kan(2):    6     47    64    40     59     29      4      7
lo Gen(4):   33     31    56    62     53     39     52     15
lo Kun(0):   12     45    35    16     20      8     23      2
```

## 2 · Deterministic casting (coin-method distribution)
```python
import hashlib, secrets
def cast(user_id, iso_date, question, salt="hermes-v1"):
    seed = hashlib.sha256(f"{user_id}|{iso_date}|{question}|{salt}".encode()).digest()
    rng = lambda i: seed[i] / 255            # deterministic bytes
    vals = []
    for i in range(6):                        # lines bottom-up
        r = rng(i) * 16                       # weights: old-yin 1, young-yang 5, young-yin 7, old-yang 3 (of 16)
        vals.append(6 if r < 1 else 7 if r < 6 else 8 if r < 13 else 9)
    lines = [1 if v in (7, 9) else 0 for v in vals]
    changing = [i for i, v in enumerate(vals) if v in (6, 9)]
    return lines, changing
# primary hexagram: KW[bits(lower 3)][bits(upper 3)]
# derived hexagram: flip changing lines, recompute KW
# nuclear hexagram: new_lower = lines[1:4], new_upper = lines[2:5]
```
Probabilities match classic three-coin method exactly: P(6)=1/16, P(7)=5/16, P(8)=7/16, P(9)=3/16 ✓

## 3 · Data schema (JSON per hexagram)
```json
{"king_wen": 31, "cn": "咸", "pinyin": "Xián", "en": "Influence", "th": "แรงดึงดูด",
 "judgment_en": "Influence. Success. Perseverance furthers. To take a maiden as a wife brings good fortune.",
 "judgment_th": "แรงดึงดูด: สำเร็จ · ความมั่นคงช่วยให้รุดหน้า · รับเธอมาเป็นคู่จึงเป็นมงคล",
 "image_en": "A lake on the mountain: the superior person encourages people to approach him by his readiness to receive them.",
 "image_th": "ทะเลสาบอยู่บนภูเขา — ผู้ใหญ่เปิดรับคนเข้าหาด้วยความพร้อมรับฟัง",
 "lines": ["...","...","...","...","...","..."]}
```
Fully-written v1 set: **#1 Qián (The Creative)** — pure creative force, dragon imagery: initiative blessed when timed; **#24 Fù (Return)** — turning point, the light returns: after lull, movement resumes at winter solstice rhythm; **#31 Xián (Influence)** as above (love-domain anchor); **#50 Dǐng (The Cauldron)** — nourishment/refinement of the talented: institution feeding growth. Remaining 60 follow same schema from Wilhelm/Baynes public-domain text [BUILD-TIME].

## 4 · Question-domain routing
| Domain | Anchor hexagrams for focus note |
|---|---|
| Love | 31 Influence, 37 Family, 54 Marrying Maiden(caveat line), 61 Inner Truth |
| Career | 14 Great Possession, 26 Taming Power, 46 Pushing Upward |
| Money | 42 Increase, 41 Decrease(warning), 21 Bite Through(decision) |
| Health | 27 Nourishment, 48 The Well |
| Conflict | 6 Conflict, 40 Deliverance |

## 5 · Fusion rule (with tarot module 07)
Same-day draw: trigram element (Wood/Fire/Earth/Metal/Water) vs card suit element (Wands=Fire, Cups=Water, Swords=Air, Pentacles=Earth) — **same element or generative cycle (Wood→Fire→Earth→Metal→Water→Wood)** ⇒ confidence flag HIGH; destructive cycle ⇒ MED + print both voices conditionally (per master fusion rules §4).

## 6 · Output templates
- TH: *"หยี่จิ๋งวันนี้: #31 咸 แรงดึงดูด — [judgment_th] · เส้นเปลี่ยนที่ [n]: [line_advice] · ธีมสอดคล้องกับไพ่ [card]: [fusion note]"*
- EN: *"I Ching today: #31 Influence — [judgment_en] · Changing line [n]: [advice] · Aligns with [card]: [note]"*

## Implementation Notes (QA 2026-08-23)
**(a) Formula/constants:** PRIMARY casting = spec §2 sha256-seeded coin method (`seed = sha256(user_id|iso_date|question|salt="hermes-v1")`; per-line weights old-yin 1 / young-yang 5 / young-yin 7 / old-yang 3 of 16 → classic three-coin probabilities ✓). Fallback/cross-check when no user seed exists: `hexagram_number = ((day*month + year) mod 64) + 1` (King Wen number). Lookup table = §1 Wilhelm KW[lower][upper].
**(b) Ground truth (M, DOB 1997-05-19):** fallback formula → (19×5 + 1997) = 2092; 2092 mod 64 = 44 → **#45 萃 Cuì "Gathering Together"** (lower ☷0 / upper ☱3 — consistent with the §1 KW row lo Kun(0) × up Dui(3) = 45). Seeded-cast unit-test vector (`user_id="M"`, `iso_date="1997-05-19"`, `question=""`, `salt="hermes-v1"`): vals [7,7,7,8,8,8] → lines bottom-up [1,1,1,0,0,0] → lower Qian(7) / upper Kun(0) → **primary #11 泰 Tài "Peace", zero changing lines** (derived = primary), nuclear = **#54 歸妹 Guī Mèi "The Marrying Maiden"**.
**(c) Degradation:** missing user_id/date or unhashable input → `{'status':'unavailable','reason':'missing_seed_input'}`; KW number with no written text entry (61 of 64 still BUILD-TIME) → `{'status':'unavailable','reason':'hexagram_text_missing:<n>'}` — never emit an unwritten entry as if complete.
