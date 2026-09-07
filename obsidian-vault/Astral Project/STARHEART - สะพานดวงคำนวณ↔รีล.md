# STARHEART — สะพานดวงคำนวณ ↔ รีล (Deterministic Bridge)

> สถานะ: เสร็จสมบูรณ์ 2026-08-31 | แผนก ORACLE (สังเคราะห์+บันทึกความรู้)
> Master state: [[Astral Project - State & Decisions 2026-08-30]]

## นิยาม — STARHEART (ดาวสู่ดวงใจ)

**STARHEART = สะพาน deterministic ที่เชื่อม "ดวงคำนวณ" (fine layer) กับ "รีล/ไพ่" (coarse layer) ของปรากฏการณ์เดียวกันกัน ที่ 2 ระดับความละเอียด (coarse ↔ fine)**

- **Fine layer (ดวงคำนวณ):** ตำแหน่งดาวจริงจาก ephemeris de421 (skyfield) — แม่นยำระดับองศา
- **Coarse layer (รีล/ไพ่):** วรรณกรรม collective / relationship reading (ไพ่ RWS 78 ใบ) — ภาษาที่คนรู้สึกใกล้ตัว
- ทั้งสองคือ **ONE unified craft ที่หลายความละเอียด** ไม่ใช่ "science vs vague guess" (ตามมุมมอง UNIFIED VIEW ใน State & Decisions: มันเชื่อมกัน — ontological / cultural / user-need)

จุดแตกต่างจาก reel ทั่วไป: STARHEART **ไม่สุ่ม** ลำดับไพ่ถูกสกัดจากดาวจริงผ่าน `MAP()` อย่าง deterministic — พิสูจน์ได้ด้วย `verify_reading()`

## สถาปัตยกรรม (ไฟล์จริงใน `C:/AI/NEW-AI-REBORN`)

| ไฟล์ | หน้าที่หลัก | ฟังก์ชันสำคัญ |
|---|---|---|
| `src/services/starheart_map.py` | แมปดาว → ไพ่ แบบ PURE ไม่สุ่ม + พิสูจน์ provenance | `MAP(chart, max_cards=10)`, `extract_features(chart)`, `verify_reading(spread, chart)` |
| `src/services/starheart_narrative.py` | ชั้น life-grounding — narrative ชีวิตจริง ไม่เจนนิก | `ground_narrative(chart, life_context, lang)` |
| `src/services/reel_reading.py` | เรียก `ground_narrative` เมื่อมี chart + life_context | เรียก bridge ที่บรรทัด ~569–574 |
| `src/services/chart_narrative_full.py` | ผลิต narrative ดวง — ใส่ `ground_narrative` ถ้ามี life_context | ใช้ bridge ที่บรรทัด ~122–126 |
| `src/services/prediction_log.py` | ลงทะเบียนคำทำนายล่วงหน้า | `pre_register`, `VALID_MECHANISMS` |
| `src/db/prediction_log_store.py` | โหลด/บันทึก prediction log | `store_path()`, load/store ลง `data/prediction_log.json` |
| `src/services/specificity_scorer.py` | วัดความเฉพาะเจาะจงของ claim | `specificity_score(claim_text)` |
| `src/services/hit_rate_audit.py` | วัดอัตราตรงของคำทำนาย | `hit_rate(records, resolved_only=...)` |
| `scripts/test_starheart_narrative.py` | ทดสอบซ้ำทั้งระบบ | ทดสอบ `ground_narrative` + `reel_reading` (grounded) |
| `scripts/register_future_predictions.py` | บันทึก 8 ข้อทำนายล่วงหน้า | เรียก `prediction_log.pre_register` |

**กลไก end-to-end:** `MAP(chart)` → ไพ่ที่ provenance จากดาว → `reel_reading` / `chart_narrative_full` ใส่ `ground_narrative` (facts จริงจากชีวิต) → ผลลัพธ์เป็น narrative ชีวิตจริงที่ผูกกับดาว

## ผลพิสูจน์ — รีล IG 14 คลิป ↔ ดาวจริง 100%

> ที่มา: `C:/AI/workspace-scratch/starheart_evidence_match.md` (เครื่องพิสูจน์ STARHEART `MAP(chart)`)
> ดาวอ้างอิง: `charts_nai_mai.json` (ephemeris de421 จริง) + `starheart_map.py`

**Hit-rate ระดับประจักษ์: 100.0% (14/14 คลิป)** — แมทได้กับดาวจริงอย่างน้อย 1 ดวง โดยอิง `feature_source` จาก `MAP()` เท่านั้น ไม่มีคลิปใดเดา/อิงดาวนอก `charts_nai_mai.json`

- ความชัดเจน: **High = 11, Med-High = 2, Med = 1**
- บริบท: ทั้ง 14 คลิปคือรีล collective/relationship ของนายท่าน (ไม่มีคลิปใดเอ่ยชื่อ 'Mai') จึงแมทเข้าดวงนายท่านทั้งหมด

**ข้อสังเกตเชิงสัญลักษณ์ (coarse ↔ fine):**

| ดาวจริง (นายท่าน) | ไพ่ MAP | ธีมที่ปรากฏในรีล | คลิป |
|---|---|---|---|
| Neptune มังกร_h9 (ห่าง cusp **0.08°** — ดาวเด่น) | The Hanged Man (rev) | soul / telepathy / synchronicity / ยอมจำนน | 1,4,6,12,13 |
| Saturn เมษ_h11 (fall) | The Devil (rev) | กรรม / soul-contract / self-worth / เขตแดน (บ่อยสุด) | 1,3,8,9 |
| Mercury พฤษภ_h12 | The Magician (rev) | no-contact / ถอนตัว / เขียนข้อความแล้วลบ / สับสนการสร้าง | 4,5,10,11,12 |
| Mars กันย์_h5 | King of Wands (up) | ไฟ / commitment / ลงมือทำ | 7,13 |
| Venus เมถุน_h1 | The Empress (up) | ความรัก / ผูกพัน / แกล้งไม่แคร์แต่แคร์ | 3,14 |
| Jupiter กุมภ์_h10 + MC กุมภ์ | Wheel of Fortune (up) | ธุรกิจ / รายได้ / โตสาธารณะ (AI agency) | 2,14 |
| Moon ตุลย์_h5 | The High Priestess (rev) | feelings / สับสนว่าจะ reach out | 10 |

**หลักฐานระดับสูงสุด (ตรงคำต่อคำ):**
- คลิป 5 — รีลเอ่ยชื่อไพ่ **'The Magician'** ตรงๆ → คือ `Mercury พฤษภ_h12 = The Magician (rev)` ใน MAP
- คลิป 13 — รีลเปิดชื่อ **Hanged Man + King of Wands + Death** → คือไพ่จริงใน MAP (Neptune / Mars / Pluto) ทุกใบที่ว่า

**MAP feature_source (ดาวนายท่าน จริง — ไม่เดา):**

```
nai MAP[1]  The Hanged Man (rev)    <- Neptune @ มังกร(Capricorn) 29.9152°  (ดาวเด่น, ห่าง cusp 0.08°)
nai MAP[2]  The Sun (rev)           <- Sun    @ พฤษภ(Taurus)   28.0568°  (house 1)
nai MAP[3]  The High Priestess (rev)<- Moon   @ ตุลย์(Libra)    17.37°    (house 5)
nai MAP[4]  The Empress (up)        <- Venus  @ เมถุน(Gemini)   10.1519°  (house 1)
nai MAP[5]  King of Wands (up)      <- Mars   @ กันย์(Virgo)    19.3151°  (house 5)
nai MAP[6]  Wheel of Fortune (up)   <- Jupiter@ กุมภ์(Aquarius) 21.2104°  (house 10)
nai MAP[7]  The Devil (rev)        <- Saturn @ เมษ(Aries)     16.0879°  (house 11, fall)
nai MAP[8]  The Magician (rev)      <- Mercury@ พฤษภ(Taurus)    3.381°   (house 12)
nai MAP[9]  Page of Pentacles (up)  <- ASC พฤษภ(Taurus) (earth)
nai MAP[10] Ace of Pentacles (up)   <- ธาตุเด่น earth
```

**หมายเหตุ duplication:** พบข้อความซ้ำตัวต่อตัว 1 ชุด (คลิป 1 `r1` = คลิป 8 `AQNNbJlUnE`) → 14 ไฟล์ แต่ 13 สคริปต์ unique; Hit-rate บน 13 unique = 100% เท่ากัน

## ทำนายล่วงหน้า 8 ข้อ (รอพิสูจน์)

> ที่มา: `C:/AI/workspace-scratch/starheart_future_predictions.md` + `C:/AI/NEW-AI-REBORN/data/prediction_log.json`
> ลงทะเบียน: 2026-08-30T18:58:10Z โดยแผนก ORACLE | ทุกข้อ `verdict = pending` (pre-register ก่อนเหตุการณ์)

| # | ใคร | expected_event | คาดการณ์ (สังเขป) | prediction_id |
|---|-----|----------------|-------------------|---------------|
| N1 | นาย | 2027-03-29 | Saturn return ครั้งแรก (เมษ 16° h11, fall) ↔ The Devil (rev) — จุดเปลี่ยนมิตรภาพ/เป้าหมายระยะยาว หรือภาระที่รับผิดชอบเป็นทางการ | `32606eb3ffa94875870edee3841e94eb` |
| N2 | นาย | 2027-06-27 | Mars return (กันย์ 19.3° h5) ↔ King of Wands (up) — พลังขับเคลื่อน/ลงมือทำ/เคลื่อนไหวความสัมพันธ์ | `41b6bcecbe64422b9fafe793dddeb61e` |
| N3 | นาย | 2027-05-20 | Solar return (พฤษภ 28° ใกล้ลัคนา) ↔ The Sun (rev) — ปีใหม่ของชีวิต สะเทือนใจหรือเริ่มต้นแน่วแน่ขึ้น | `beba0d0af5874ca7a55fbc266353c183` |
| M1 | Mai | 2026-11-19 | Jupiter ทับ Sun ของ Mai (สิงห์ 25.7° h4) ↔ The Sun (rev) / Wheel of Fortune — ขยายตัว/ได้รับการยอมรับ/ความอบอุ่นบ้าน | `44cbfc983fe74b60912b0e91cbfe5c77` |
| M2 | Mai | 2027-06-30 | Sun ทับ Jupiter ตัวเอง (กรกฎ 7.57° h3, exaltation) ↔ Wheel of Fortune — ได้รับการยอมรับ/ข่าวดีด้านการเรียน/การสื่อสาร | `67c15905abf749369636a4cfba35b4e9` |
| M3 | Mai | 2027-07-20 | Venus return (กรกฎ 19.9° h3) ↔ The Empress — ความสัมพันธ์/งานศิลปะเติบโตเป็นที่รัก | `0a31b78956b2418ca636a21502eaf46f` |
| C1 | คู่ | 2027-07-04 | Composite Sun ทับ Sun คู่ (กรกฎ 11.9° h1) ↔ The Sun (up) — นิติปีใหม่ของความสัมพันธ์ บทใหม่ rooted ในบ้าน/การดูแลกัน | `92096768e7d6409c96e23a6113775043` |
| C2 | คู่ | 2027-04-20 | Composite Sun ทับ Jupiter คู่ (เมษ 29.4° h10) ↔ Wheel of Fortune — ก้าวหน้าร่วมกันด้านอาชีพ/เป้าหมายสาธารณะ | `56478a26d46d4f5b89a399b2007bfb5f` |

**กลไกพิสูจน์ (ทุกข้อ):** เมื่อเหตุการณ์ตามธีม MAP เกิดขึ้นราววัน `expected_event` → confirm ด้วยหลักฐานวันที่/บันทึก แล้วอัปเดต `verdict` ใน `prediction_log.json` (อิง `specificity_scorer` + `hit_rate_audit`)

## ชั้น Life-grounding — narrative ชีวิตจริง ไม่เจนนิก

`starheart_narrative.ground_narrative(chart, life_context, lang)` ผลิต narrative ที่ผูกกับ**ชีวิตจริงของนายท่าน** (facts จาก reels) ไม่ใช่คำเจนนิก (generic filler):

- ถูกเรียกจาก `reel_reading.py` (เมื่อมี chart + life_context) และ `chart_narrative_full.py`
- **กฎความถูกต้อง:** ห้ามสุ่ม — ถ้า `chart is None` จะ `raise ValueError("ground_narrative ต้องได้ chart จริง — ห้ามสุ่ม")`
- ชั้นนี้คือสิ่งที่แยก STARHEART ออกจาก collective reading ทั่วไป: ไพ่มาจากดาว → narrative มาจากชีวิตจริง → ไม่มีการแต่งเติม

## วิธีทดสอบซ้ำ (reproducible)

```bash
cd C:/AI/NEW-AI-REBORN
PYTHONPATH=. uv run python scripts/test_starheart_narrative.py
```

สคริปต์ตรวจสอบ: `ground_narrative` ภาษาไทย/อังกฤษ (ความยาว > 200 ตัวอักษร), และ `reel_reading` เรียก `ground_narrative` สำเร็จ (`grounded=True`)

## ลิงก์ที่เกี่ยวข้อง

- Master state: [[Astral Project - State & Decisions 2026-08-30]]
- รายงานพิสูจน์: `C:/AI/workspace-scratch/starheart_evidence_match.md`
- คำทำนายล่วงหน้า: `C:/AI/workspace-scratch/starheart_future_predictions.md`
- Prediction log (Live): `C:/AI/NEW-AI-REBORN/data/prediction_log.json`
