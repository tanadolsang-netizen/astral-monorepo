# 04 · THAI + BAZI ENGINE SPEC — ปีนักษัตร · ชง · ตรียัมปาไถ Module
> **EN:** Deterministic Chinese/Thai layer. All pillars below computed with `lunar-python` and cross-verified by JDN arithmetic (`verify_bazi.py`, 22 Aug 2026). Test case = Owner 1997-05-19 05:45 ICT + Mai 2001-08-18 22:32 ICT.
> **TH:** ชั้นจีน-ไทยแบบ deterministic · ทุกเสาคำนวณจริงด้วย lunar-python + ตรวจซ้ำด้วยสูตร JDN

---

## 1. Four Pillars derivation / วิธีหา 4 เสา (port 1:1)
```python
# YEAR: Lichun cutoff (≈4-5 ก.พ.) — ก่อน Lichun ใช้ปีก่อน
# MONTH: ตาม solar term + 五虎遁 (month stem จาก year stem)
# DAY:   day_pillar_index = (JDN + 49) % 60        ← ค่าคงที่ verify แล้ว 2 ดวง
#        JDN = สูตร Gregorian มาตรฐาน (ดู verify_bazi.py)
# HOUR:  ช่วง 2 ชม./เสา + 五鼠遁 (hour stem จาก day stem); 05:45 = 卯 Mao (05–07)
```
**Ground truth (คำนวณจริง):**
| คน | ปี | เดือน | วัน | ชั่วโมง | Day Master |
|---|---|---|---|---|---|
| เจ้าของ | 丁丑 ฉลูไฟ | 乙巳 | **辛酉** | 辛卯 | **辛 โลหะหยิน** |
| ไหม | 辛巳 | 丙申 | 癸丑 | 癸亥 | **癸 น้ำหยิน** |

JDN ยืนยัน: Owner JDN=2450588 → day index 57 (辛酉) · Mai JDN=2452140 → index 49 (癸丑) — offset **49 ทั้งคู่**

## 2. Day Master & favorable elements / ตัวยืนและธาตุที่เอื้อ
- เจ้าของ 辛 (โลหะหยิน = เพชร/ของประณีต) เกิดเดือน 巳 (ไฟเป็นเจ้าเดือน) → โลหะถูกหลอม: ธาตุเอื้อ = **ดินชุ่ม (丑/辰) + โลหะ** · ระวังไฟแรง
- ไหม 癸 (น้ำหยิน = หยดน้ำ/ฝน) เกิดเดือน 申 (โลหะเจ้าเดือน ผลิตน้ำ) → ธาตุเอื้อ = **โลหะ + น้ำ** · ระวังดินก้อนใหญ่ถมทับ
- ขั้นตอน encode: (1) เดือนกำเนิดกำหนดเจ้าเดือน (2) นับ support vs drain ของ 4 เสา (3) เลือก 喜用神 = ธาตุที่ปรับสมดุล — calculation HIGH, interpretation MEDIUM

## 3. Interaction rules + yearly generator / กฎชน-หนู-ปี
```python
CLASH ชง = {子↔午, 丑↔未, 寅↔申, 卯↔酉, 辰↔戌, 巳↔亥}
HARM หาย = {子↔未, 丑↔午, 寅↔巳, 卯↔辰, 申↔亥, 酉↔戌}
```
| ปี | เสา | ต่อฉลูไฟ (เจ้าของ) | ต่อปีระ (ไหม) |
|---|---|---|---|
| 2026 | 丙午 ม้าไฟ | **丑午 หาย (harm)** — ระวังคนใกล้ตัวหักหลัง/สุขภาพเล็ก ๆ | 午↔巳 กลาง ๆ |
| 2027 | 丁未 แพะไฟ | **丑未 ชง (clash)** — ปีเปลี่ยนแปลงใหญ่ ขยับที่อยู่/โครงสร้าง | 未↔巳 กลาง ๆ |

## 4. Thai layer / ชั้นไทย
- **ผู้คุณวัน + เลขนำโชค:** อาทิตย์→อาทิตย์(1) · จันทร์→จันทร์(2) · อังคาร→อังคาร(3) · พุธ→พุธ(4) · พฤหัส→พฤหัส(5) · ศุกร์→ศุกร์(6) · **เสาร์→เสาร์(9)** — เจ้าของเกิดวันเสาร์ → ผู้คุณ Saturn เลข 9 ✅ (ตรง fusion test)
- **ตรียัมปาไถ (ยืนยันใน fusion test = 1-5-8-5):** วัน 1+9=10→**1** · เดือน 0+5=**5** · ปี ค.ศ. 1+9+9+7=26→**8** · รวม 1+5+8=14→**5** (สายชู/เสนีย์/มหาอุดร)
- **เลขเจตา 7 หลัก:** ลด วัน-เดือน-ปี(พ.ศ. 2540→2+5+4+0=11→2) เป็นหลักเดียวแล้วเรียง 7 ตำแหน่ง — ⚠️ ปฐมฐานปีใช้ พ.ศ. หรือ ค.ศ. ยังต้องเทียบตำราอ้างอิงก่อนปล่อย prod (source-check pending)
- **อายุเนื่อง:** ระบบนับอายุแบบไทยโบราณสำหรับเลือกปีเสี่ยง — summary เท่านั้น ยังไม่ encode

## 5. Cross-system synthesis / รวมสามระบบ
precedence เดียวกับ spec 01 §4: transit > dasha > BaZi tone · BaZi ให้ "โทนวัน/ปี" (ชง/harm/ธาตุ) ไม่ override วันที่ transit แม่น · ขัดแย้ง = tension แยกประโยค

## 6. Output templates
```
TH: "ปี {ชื่อเสาไทย}: ฉลู{ชง/หาย}{สัตว์} — {ผล concrete} · ธาตุเอื้อปีนี้: {ธาตุ}"
TH: "วัน{วัน}: ผู้คุณ{ดาว} เลขนำโชค {เลข} · ตรียัมปาไถ {3 ตัว}"
EN: "{year} {pillar}: Ox-{clash/harm}-{animal} — {dated consequence}; favorable element: {element}"
Confidence: HIGH (เสา/ชง/ตรียัม) | MEDIUM (ธาตุเอื้อ) | pending (เลขเจตาฐานปี)
```
---
*Feeds: `/v1/fusion/today` (BaZi layer) · fixtures: `verify_bazi.py` · sibling: 01 · 02 · 03 · master: 00-MASTER-unified-engine.md*
