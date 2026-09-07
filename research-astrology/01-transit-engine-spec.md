# 01 · TRANSIT ENGINE SPEC — Present-Moment Timing Module
> **EN:** Deterministic rules for computing "what the sky is doing to you today". Every formula ports 1:1 to Python. Test case = vault owner (1997-05-19 05:45 ICT, Chonburi) + Mai (2001-08-18 22:32 ICT, Nonthaburi); all dates below machine-verified with JPL DE421 (`transit_hits.py`, `transit_week_scan.py`).
> **TH:** กฎ deterministic สำหรับ "วันนี้ท้องฟ้าทำอะไรกับคุณ" · ดวงทดสอบ = เจ้าของ vault + ไหม · ทุกวันที่ด้านล่างคำนวณจริงด้วย DE421

---

## 0. Input contract / สัญญาอินพุต
```
natal:      birth_local ISO + tz + lat/lon → chart via skyfield DE421 (offline)
now:        UTC datetime
pipeline:   ecliptic longitudes → tropical + sidereal (Lahiri ≈ 23.68 + (year−1997)×50.29″/yr)
houses:     whole-sign from sidereal ASC
```
⚠️ ห้ามเทียบ tropical กับ sidereal ข้ามระบบในทุกสูตร

## 1. Aspect grid / ตารางมุม
```python
ASPECTS = {0:'conj', 60:'sextile', 90:'square', 120:'trine', 180:'opp'}
MAX_ORB = {'Sun':8,'Moon':8,'Mercury':6,'Venus':6,'Mars':6,'Jupiter':6,'Saturn':6,'Uranus':4,'Neptune':4,'Pluto':4}
# daily-scan mode: orb ≤ 2.5° (สแกนรายวันใช้ orb ตายตัว 2.5°)
angdiff(a,b) = min(|a−b| mod 360, 360 − |a−b| mod 360)
```
**Polarity rule / กฎเชิงบวกลบ:** polarity = ดาว × มุม (ไม่ใช่ความรู้สึก) — square/opp = กระตุ้นแรง "ต้องจัดการ" · trine/sextile = ลื่นไหล "ได้เปรียบ" · conj = ขึ้นกับธรรมชาติดาว
**Orb decay:** weight = w_planet × (1 − orb/MAX_ORB) — linear, 0 ที่ขอบ

## 2. Daily scan algorithm / อัลกอริทึมสแกนรายวัน (จาก `transit_week_scan.py` ที่รันจริง)
```python
for day at 12:00 local:
    movers = [Sun..Pluto] (+ mean node: Ω = 125.04452 − 0.0529538·d, d = days since J2000)
    for tp in movers, np in [Sun,Moon,Mercury,Venus,Mars,ASC]:
        if orb(angdiff(sid(tp), natal_sid(np))) ≤ 2.5: emit hit sorted by orb
    moon → whole-sign house of the day
```
Output ต่อวัน: จันทร์เรือนใด + hits เรียงตาม orb + ingress ของ Mercury/Venus/Mars ในหน้าต่าง

## 3. Verified hit dates 2026–2028 (ground truth — แทนที่ตัวเลขเดิมใน vault)
⚠️ **CORRECTIONS vs vault notes เดิม:** (1) ~~"Jupiter ทับ Mars ปลาย 2026"~~ → ingress สิงห์ 31 ต.ค. 2026 แต่ทับองศา Mars จริง = **28 ต.ค. 2027** (triple-pass 2027-10-28 / 2028-04-04 / 2028-06-22) (2) Saturn Return exact = **26 มี.ค. 2027 ผ่านครั้งเดียว**

| วันที่ | เหตุการณ์ | โดเมน |
|---|---|---|
| 2026-09-14 | Jupiter conj natal IC (สิงห์ 16.43°) | บ้าน/ครอบครัว |
| 2026-09-27 | Jupiter conj จันทร์ไหม #1 | ความสัมพันธ์ |
| 2026-10-31 | Jupiter → สิงห์ (sidereal) | เริ่มปีขยาย |
| 2026-11-10 | AD Ju-Sa → Ju-Me (ดู spec 02) | จบเฟสกดดัน |
| 2026-11-14 | Jupiter conj อาทิตย์ไหม #1 | โอกาสของเธอ |
| 2026-12-14 | Rahu → มังกร (sidereal) | แกน karmic ขยับ |
| 2027-03-08 | Jupiter conj จันทร์ไหม #2 (retro) | รอบสะท้อน |
| **2027-03-26** | ⭐ **Saturn Return exact** (เมษ 16.08°) | restructure ชีวิต |
| 2027-05-19 | Jupiter conj จันทร์ไหม #3 (วันเกิดเจ้าของ) | ความสัมพันธ์ |
| 2027-06-03 | Saturn → เมษ sidereal (retro กลับ 2027-10-20, สุดท้าย 2028-02-23) | **Ashtama Shani เริ่ม** (ไม่ใช่ Sade Sati — ดู spec 02 §5) |
| 2027-10-28 | Jupiter conj อังคารกำเนิด #1 | ลงมือทำได้ใหญ่ |

**Stations เสาร์ (จาก agent log, ICT):** Rx 2026-07-26 @ 14°44′ เมษ · Direct 2026-12-10 @ 07°55′ เมษ · Rx 2027-08-09 @ 27°52′ · Direct 2027-12-24 @ 21°01′
**Eclipses ใกล้สุด:** สุริยุปราคาเต็มดวง 2026-08-12 @ 20°01′ สิงห์ · จันทรุปราคา 2027-02-20 มีน (penumbral)
**Mercury Rx 2026:** 26 ก.พ.–20 มี.ค. (มีน) · 29 มิ.ย.–23 ก.ค. (กรกฎ) · 24 ต.ค.–13 พ.ย. (พิจิก)

## 4. Fusion precedence / ลำดับน้ำหนักเมื่อรวม 3 ศาสตร์
**transit (แม่นระดับวัน) > dasha (ระดับเดือน) > BaZi day tone** — ความขัดแย้งรายงานเป็น tension ไม่เฉลี่ยทิ้ง

## 5. Output templates (ไม่มีคำกำกวม)
```
TH: "{ดาว} {มุมไทย} กับ{จุดกำเนิด} — {polarity phrase} (เหลือ {orb}°) ฉากหลัง: {AD}"
EN: "{planet} {aspect} natal-{point} — {action verb} ({orb}° applying); backdrop: {AD}"
Window: "วันที่ดีที่สุดของ {หน้าต่าง}: {date} — {top hit by weight}"
Confidence: HIGH (คำนวณจริง) | MEDIUM (interpretation) ทุกบรรทัด
```
---
*Feeds: `/v1/fusion/today`, `/v1/fusion/window` · sibling: 02-vedic · 03-synastry · 04-thai-bazi · master: 00-MASTER-unified-engine.md*
