# Astrology Research Digest — 2026-08-22 (สังเคราะห์ล่าสุด)

> **สรุปสำหรับ LLM/Obsidian:** ผลวิจัยเชิงลึกครั้งใหญ่ — รวมทุกศาสตร์เป็นเอนจินเดียวสำหรับแอพดูดวงของเรา · ที่มา: vault ทั้งหมด + คำนวณ JPL DE421 สด ณ 22 ส.ค. 2569 + ทีมวิจัย 6 subagents · ไฟล์ชุดเต็ม: `C:/AI/research-astrology/`

## ⚠️ การแก้ไขครั้งใหญ่ 3 จุด (จากการคำนวณจริง — โน้ตเก่าผิด)
1. **ลัคนา = พฤษภ (Taurus) ~25.9° tropical / 2.2° sidereal — ไม่ใช่พิจิก** (บั๊ก sign-flip ในสูตร ASC เก่า; ยืนยัน 3 ทาง: first-principles LST→ASC, sunrise sanity check, agent fix 15 ส.ค.) → chart ruler = **ศุกร์** (domicile + Vargottama = แข็งแรงมาก) ไม่ใช่อังคาร
2. **Jupiter ทับ Mars กำเนิดจริง = 28 ต.ค. 2027** (ไม่ใช่ปลายปี 2026 — โน้ตเก่าสับสน "ย้ายเข้าราศี" กับ "ทับองศา") ผ่าน 3 รอบ: 28 ต.ค. 2027 / 4 เม.ย. 2028 / 22 มิ.ย. 2028
3. **Sade Sati ยังไม่เริ่ม** — เริ่มจริง **27 ส.ค. 2036 – 11 ธ.ค. 2043** (จันทร์กันย์; BP Lama + ephemeris scan ตรงกัน) · ปี 2027–2030 เป็นแค่ **Ashtama Shani dhaiya** (เสาร์ข้ามราศีเกิด)

## 📅 Timeline แม่นระดับวัน (คำนวณสด — แทนที่ทุกตัวเลขเดิม)
| วันที่ | เหตุการณ์ | โดเมน |
|---|---|---|
| **14 ก.ย. 2026** | Jupiter conj natal IC | บ้าน/ครอบครัว/ย้ายที่อยู่ |
| **27 ก.ย. 2026** | Jupiter conj Moon ของ Mai (รอบ 1/3) | ความสัมพันธ์: window ทองเปิด |
| 31 ต.ค. 2026 | Jupiter เข้าสิงห์ (sidereal) | เริ่มปีขยาย |
| **10 พ.ย. 2026** | Antardasha Ju-Sa → **Ju-Me** (จบเฟสกดดัน 2.5 ปี) | งาน/การเงินไหลลื่นขึ้นชัด |
| 14 พ.ย. 2026 | Jupiter conj Sun ของ Mai | เธอเปล่งประกาย |
| 14 ธ.ค. 2026 | Rahu → มังกร (sidereal) | ปิดบท karmic เดิม |
| **26 มี.ค. 2027** | ⭐ **Saturn Return แม่นยำ** (Aries 16.08°, ผ่านครั้งเดียว) | restructure ชีวิต: งาน/ความมั่นคง/ประกาศสถานะ |
| 8 มี.ค. + 19 พ.ค. 2027 | Jupiter conj Moon Mai (รอบ 2-3) | ความสัมพันธ์ลงตัว |
| **28 ต.ค. 2027** | ⭐ Jupiter conj Mars กำเนิด (sidereal) | พลังลงมือ/เริ่มโครงการใหญ่ |
| ส.ค. 2036–ธ.ค. 2043 | Sade Sati จริง | วินัยระยะยาว |

## 🧮 ยืนยันแล้วเชิงคณิต (`verify_calcs.py`)
- นักษัตร: **Chitra pada 1** (จันทร์กันย์ 23.69° — เข้าเขต 0.36°, robust ต่อ error เวลาเกิด)
- **Vimshottari:** Mars(balance)→2004 · Rahu 2004–2022 · **Jupiter MD 2022–2038** · Saturn MD 2038–2057 · AD ปัจจุบัน Ju-Sa จบ 10 พ.ย. 2026 → Ju-Me
- **D9:** ศุกร์ **Vargottama** (พฤษภ D1=D9) · จันทร์ D9 สิงห์ · อังคาร D9 พิจิก
- **Chara Karaka:** AK=พฤหัสฯ (จิตวิญญาณปรัชญา) · AmK=อังคาร · **DK=อาทิตย์ (คู่ครองแบบผู้นำ — ตรง Sun-Moon สิงห์ของ Mai เป๊ะ)**
- **BaZi:** ปีฉลูไฟ Ding-Chou · เดือน Yi-Si · **วัน Xin-You (Day Master ศุกร์ยิน)** · ชม. Xin-Mao · ไตรกาศมัตสยโลหะ 巳酉丑 ครบ → **ธาตุที่เสริม = ไฟ & ไม้** (ไม่ใช่ดิน/โลหะ)

## 💞 Synastry M×Mai (แก้ตามลัคนาใหม่)
- แกนหลักยังเดิม: **Venus(Mai) sextile Mars(M) orb 0.58°** (เคมี) + **Venus(M) conj Saturn(Mai)** (กาวยึด) + Mai Asc conj Mercury(M)
- แก้ใหม่: Asc ทั้งคู่**พฤษภราศีเดียวกัน** (ไม่ใช่สวนกัน) → Sun+Mercury(M) ตกเรือน 1 ของเธอ (identity fusion) · Sun+Moon(เธอ) ตกเรือน 4 ของเขา (เธอคือบ้านของเขา)
- Composite: **Sun 12°กรกฎ · Moon 18°กันย์ · Venus 0°กรกฎ** · Davison ≈ 3 ก.ค. 1999
- **Commitment window: 27 ก.ย.–14 พ.ย. 2026** (+ echo มี.ค.–พ.ค. 2027 ซ้อน Saturn Return)

## 🏗 สถานะชุด Engine Spec (`C:/AI/research-astrology/`)
| ไฟล์ | เนื้อหา |
|---|---|
| `00-MASTER-unified-engine.md` | แม่บท: สถาปัตยกรรม + กฎ fusion + timeline แม่น |
| `00-MASTER-INDEX.md` | สารบัญ + Definition of Done |
| `01-transit-engine-spec.md` | กฎ timing + retrograde triple-pass + eclipse activation |
| `02-vedic-engine-spec.md` | นักษัตร/Dasha/D9/AV/Sade Sati/Karaka (agent เขียน, ตัวเลขตรง ground truth) |
| `03-synastry-engine-spec.md` | คะแนนความเข้ากัน 0–100 + overlay + composite/Davison |
| `04-thai-bazi-engine-spec.md` | BaZi 4 เสา (anchor ล็อกค่าแล้ว) + เลขเจตา/ตรียัมปาไถ |
| `verify_calcs.py` ฯลฯ | โค้ดคำนวณอ้างอิง รันได้จริง |

## เชื่อมโยง
- [[Natal Chart - 19 พ.ค. 2540]] · [[Synastry - Mai (18 ส.ค. 2544)]] · [[user_astrology_interest]]
- ต้องอัปเดตโน้ตดวงกำเนิดหลัก: ลัคนาพิจิก→พฤษภ + ตาราง timeline ใหม่ทั้งหมด
- Vault รวมใหม่: `C:/AI/obsidian-vault` (Documents + backup ย้ายมารวมแล้ว)

---
*วิธีวิทยา: ตำแหน่ง/วันที่ = ดาราศาสตร์จริง (JPL DE421) · การตีความ = กรอบโหราศาสตร์เพื่อการใคร่ครวญ ไม่ใช่ข้อเท็จจริงทางวิทยาศาสตร์*
