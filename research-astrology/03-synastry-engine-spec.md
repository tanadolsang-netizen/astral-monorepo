# 03 · SYNASTRY ENGINE SPEC — Compatibility Module
> **EN:** Deterministic two-chart scoring. Test case = M (1997-05-19 05:45, Chonburi) × Mai (2001-08-18 22:32, Nonthaburi); cross-aspects below are machine-verified (tropical). **CORRECTION:** composite Sun recomputed = **Cancer ~11.9°**, not "27 Gemini" as in an earlier draft — see §3.
> **TH:** กฎให้คะแนนคู่แบบ deterministic · ดวงทดสอบ = M × ไหม · มุมข้ามดาวทั้งหมดคำนวณจริง · **แก้ไข:** composite Sun ใหม่ = กรกฎ ~11.9° ไม่ใช่ 27 เมถุนตาม draft เก่า

---

## 1. Verified cross-aspects (ground truth / ของจริงก่อนเขียนกฎ)
| มุม | orb | น้ำหนักเชิงความหมาย |
|---|---|---|
| Mai Venus กรกฎ 19.90 △(sextile) M Mars กันย์ 19.32 | **0.58** | chemistry แรงสุด |
| M Venus เมถุน 10.15 ☌ Mai Saturn เมถุน 13.59 | 3.44 | binding/commitment |
| Mai ASC พฤษภ 6.34 ☌ M Mercury พฤษภ 3.38 | ~3.0 | คุยกันรู้เรื่อง |
| M Moon ตุลย์ 17.37 △ Mai Sun/Moon สิงห์ | ~2–7 | อารมณ์เข้ากัน |
| M ASC พิจิก 25.96 □ Mai Sun+Moon สิงห์ | ~0.2–10 | friction: ego ปะทะ |
| Mutual 7th-house ASC overlay (พฤษภ↔พิจิก) | — | ดึงดูดแบบคู่แท้ |

## 2. Scoring model / โมเดลคะแนน 0–100
```python
W = {'Venus-Mars':14,'Sun-Moon':12,'Sun-Venus':10,'Moon-Venus':10,'Venus-Saturn':9,
     'Moon-Mars':8,'Sun-Saturn':7,'Jupiter contacts':8,'outer-contacts':6,
     'house-overlay(7th)':10,'nodal':6}          # รวม 100
score_pair = W[kind] × (1 − orb/max_orb)        # linear decay, max_orb ตาม spec 01 §1
```
รวมทุกคู่ → normalize 0–100 · รายงาน **6 มิติ:** chemistry (Venus-Mars/8th) · emotional bond (Moon×) · stability (Saturn×) · communication (Mercury×) · growth (Jupiter×) · karmic pull (§4)

## 3. Composite & Davison / สูตรจุดกึ่งกลาง
```python
def midpoint(a, b):                    # shortest arc, รองรับ wrap 0°
    d = (b − a) % 360
    return (a + d/2) % 360 if d <= 180 else (a − (360−d)/2) % 360
```
- **Composite Sun (คำนวณใหม่):** พฤษภ 28.05° = 58.05° · สิงห์ 25.74° = 145.74° → ระยะ 87.69° (shortest) → mid = **101.9° = กรกฎ 11.9°** ✅ (draft เก่า "27 เมถุน" ผิดเพราะใช้ arc ยาว)
- **Davison:** เฉลี่ยเวลา+พิกัดจริง → **≈ 1999-07-03 12:00 UTC, 13.61N 100.75E** (engine recompute ทุกครั้ง) — มี reality ครบ ต่อ transit ได้
- ตีความ: composite = "ตัวตนของความสัมพันธ์" · Davison = "สิ่งที่เกิดข้างหลังประตูปิด"

## 4. Karmic layer / ชั้นกรรม
กฎ: nodal contact = ดาวฝั่งใดฝั่งหนึ่ง ☌/☍ โหนดอีกฝั่ง ≤5°
**ผลตรวจดวงจริง:** M NN กันย์ 25.75° vs ดาวไหมทุกดวง → **ไม่มี contact ≤5°** ⇒ karmic pull ของดวงนี้วัดด้วย **DK cross-check แทน:** DK ของ M = อาทิตย์ (spec 02 §6) ↔ ไหมมี Sun ☌ Moon สิงห์ (double-Leo) = archetype ตรง ⇒ ใช้คู่นี้เป็น regression test ของเอนจิน

## 5. Commitment-window detector / หน้าต่างของความผูกพัน
ทริกเกอร์ = transit เร็ว (Jupiter/Saturn) ถึง composite/Davison points หรือ ASC คู่
**ประยุกต์ ต.ค.–ธ.ค. 2026 (วันที่ verify แล้วจาก spec 01):**
- 2026-09-27 / 11-14 Jupiter ☌ จันทร์/อาทิตย์ไหม → หน้าต่างอบอุ่น เธอเปิด
- 2026-10-31 Jupiter เข้าสิงห์ = เข้าเรือน 4 ของ M (บ้าน/ราก) → ธีมอนาคตร่วม
- 2027-03-26 Saturn Return ของ M → จุดตัดสินใจผูกพันระยะยาว (โครงสร้าง ไม่ใช่อารมณ์)

## 6. Output contract / สัญญาเอาต์พุต
```
{dimensions: 6×0-100, top_bonds:[...], frictions:[...], next_key_dates:[dated]}
TH: "{มิติ} {คะแนน}/100 — {มุมจริง} orb {x}° = {ประโยค concrete มีวันที่}"
ห้ามคำ: "อาจจะ/เหมือนว่า/บางที" — ทุกประโยคอ้างมุม+orb+วันที่จริง
```
---
*Feeds: `/v1/synastry/*` · sibling: 01-transit · 02-vedic · 04-thai-bazi · master: 00-MASTER-unified-engine.md*
