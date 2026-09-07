# ORACLE Regression Report — Week 35 (23–29 Aug 2026)

**สรุปผู้บริหาร (TH):** สองระบบ **AGREE** — วันพีคซ้ำเดิม 26–27 ส.ค. ทั้งแผนภูมิเดี่ยว (M) และหน้าต่าง shared (M + Mai) ดรายเวอร์หลักครบทั้งสามตัวในทั้งสองระบบ
**Executive summary (EN):** Independent vault scan (skyfield/de421, sidereal-Lahiri) vs backend API (port 8002, tropical) **agree**: peak days 26–27 Aug reproduced; all three key drivers present in both.

---

## 1) Best-day consensus / ฉันทามติวันที่ดีที่สุด

**Anchor: Venus conj natal-Moon (M)** — ✅ เชื่อมั่นซ้ำได้ / reproduced

| ระบบ | ผลลัพธ์ |
|---|---|
| Vault scan (จุดสุดสัปดาห์ เที่ยงวัน) | แคบสุด **26 ส.ค. orb 0.20°** (25 ส.ค. 0.67°, 27 ส.ค. 1.06°) |
| API (สุ่ม 06/12/20 น.) | แคบสุด orb **0.03° @ 25/8 ค่ำ**, 0.39° @ 26/8 เช้า → จุดตรงเป๊ะอยู่ช่วงกลางคืน 25→26 ส.ค. |

→ ทั้งคู่ชี้พีคเดียวกันที่ **26 ส.ค.** (สอดคล้อง anchor เดิม "~26 Aug") ✓

**API daily best (M):** วันเดียวที่ rating "favourable" คือ **26 ส.ค. (+1.53, กลางวัน)** และ **27 ส.ค. (+1.62, เช้า)** — วันอื่น neutral/caution

**Shared window (M + Mai) top 3 (API):**
1. **27 ส.ค. กลางวัน (12:00)** — combined **5.88** (A +1.34 / B +4.54)
2. **26 ส.ค. ค่ำ (20:00)** — combined **5.62** (A +1.17 / B +4.45)
3. **26 ส.ค. กลางวัน (12:00)** — combined **5.27** (A +1.53 / B +3.74)

→ Top slots กระจุกที่ **26–27 ส.ค.** เหมือน regression สัปดาห์ก่อน ✓

## 2) Driver overlap / ดรายเวอร์ซ้อนทับ

| Driver | Vault scan | API | สรุป |
|---|---|---|---|
| **Pluto □ Mercury (M)** | ทุกวัน, orb 0.49–0.61° | ทุก slot, orb 0.07–0.20° | ✅ ตรงกันทั้งสัปดาห์ |
| **Sun △ Mercury (M)** | พีค **27 ส.ค. orb 0.19°** (25–29 มีทั้งหมด) | พีค **27 ส.ค. เช้า orb 0.03°** (11 slots) | ✅ พีควันเดียวกัน |
| **Jupiter ✶ Venus (M)** | ทุกวัน 23–29, orb 0.90°→2.18° (แคบสุด 23 ส.ค.) | เฉพาะ 3 slots แรก (~23 ส.ค.), orb 1.25–1.38° | ⚠️ เห็นพร้อมกันช่วงต้นสัปดาห์ แต่ API ตัดทิ้งหลัง ~24 ส.ค. (น่าจะ cutoff orb แน่นกว่า vault ที่ใช้ ≤2.5°) — ไม่ใช่ความขัดแย้งเชิงดาว แต่เป็นเกณฑ์ orb |

**Mai-side (vault):** Venus ✶ natal-Moon แคบสุด 28 ส.ค. (0.39°) / Venus □ natal-Venus แคบสุด 29 ส.ค. (0.27°) — สอดคล้องกับที่ score_b ของ API พุ่งสูงสุดช่วง 26–27 ส.ค. และคงสูงเข้าสุดสัปดาห์

## 3) หมายเหตุเชิงวิธี / Method notes

- ระบบ A เป็น **sidereal/Lahiri**, ระบบ B รัน **tropical** ตามคำสั่ง — orb เทียบได้เพราะเป็นระยะห่างเชิงมุม (frame-independent) ส่วนตำแหน่งราศีต่างกันตาม ayanamsa ตามคาด
- Orb ต่างกัน ~0.3–0.5° จาก sampling (vault: เที่ยงวัน 12:00 +07; API: 06/12/20 น.) และ ephemeris/pipeline คนละตัว — ทิศทางและวันพีคตรงกันทุกจุด
- ไฟล์: `C:/AI/obsidian-vault/scripts/transit_week_scan_w35.py` (สำเนาใหม่, range(23,30), ต้นฉบับไม่ถูกแตะ); raw API JSON เก็บที่ `%LOCALAPPDATA%/Temp/api_windows_M.json`, `api_windows_shared.json`

## Verdict

**AGREE — พีค 26–27 ส.ค. (Venus-Moon conj แคบสุด ~26 ส.ค.; shared top = 27/8 กลางวัน, 26/8 ค่ำ/กลางวัน); drivers ครบ 3/3 ทั้งสองระบบ (Jupiter✶Venus เห็นเฉพาะต้นสัปดาห์ใน API จาก orb cutoff)**

---
*เพื่อการไตร่ตรองและความบันเทิงเท่านั้น ไม่ใช่คำแนะนำทางการแพทย์ กฎหมาย หรือการเงิน / For reflection and entertainment only.*
