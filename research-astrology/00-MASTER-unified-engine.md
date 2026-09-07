# 00 · MASTER — Unified Astrology Engine Spec (แม่บทรวมทุกระบบ)
# Master specification: one engine, every divination science, present-moment precise

> **⚠️ CORRECTION 2026-08-22 / การแก้ไขสำคัญ:**
> **ลัคนาที่ถูกต้อง = พฤษภ (Taurus) ~25.9° tropical / ~2.2° sidereal — ไม่ใช่พิจิก**
> โน้ต natal chart 14 ส.ค. ของ vault ใช้ลัคนาพิจิก 25.96° ซึ่งมาจากบั๊ก sign-flip ในสูตร ASC
> ยืนยัน 3 ทางอิสระ: (1) คำนวณ first-principles ใหม่ (LST→RAMC→ASC) ได้ Taurus 25.9°
> (2) sanity check พระอาทิตย์ขึ้น: เกิด 05:45 ใกล้ sunrise (~05:52) → ASC ≈ องศาดวงอาทิตย์ (พฤษภ 28°) ✓
> (3) agent fix 15 ส.ค. 2026 + raw file taurus-ascendant ใน vault ใหม่
> **ผลต่อการอ่าน:** chart ruler = ศุกร์ (ไม่ใช่อังคาร) · ศุกร์เป็นเจ้าลัคนาในเรือนตัวเอง + Vargottama = แข็งแรงมาก
> house overlay ใน synastry เปลี่ยนทั้งชุด (ดู §3.3)

> **สถานะ / Status:** v1.0 — 22 ส.ค. 2026 (2569) · สังเคราะห์จาก vault ทั้งหมด + คำนวณ ephemeris จริง (JPL DE421) วันนี้
> **เป้าหมาย / Goal:** เอนจินดูดวงที่แม่นที่สุดของเรา — รวมทุกศาสตร์เป็นอันเดียว, ทุกด้านในชีวิต, ปัจจุบันเสมอ, user ไม่ต้องเดาเอง
> Goal: our most accurate fortune-telling app — all sciences fused into ONE engine, every life area, always present-moment, zero guesswork for users.

---

## 1 · ARCHITECTURE / สถาปัตยกรรม

```
INPUT (birth data: date, time±min, lat, lon, tz)
   ↓
[CORE COMPUTE LAYER] — single source of truth
   • Swiss Ephemeris (production) / JPL DE421+skyfield (validated fallback — both verified in this repo)
   • Timezone: IANA tz database via birth timestamp; store UTC offset explicitly
   • Ayanamsa: Lahiri with drift term: a(t) = 23.68° + (t_year − 1997) × 50.29″/yr
     (verified against vault scripts; error <0.01° for 1900–2100)
   • Outputs: tropical lon, sidereal lon, Asc/MC, house cusps (whole-sign for Vedic/Thai,
     Placidus optional for Western), retrograde flags, daily motion speeds
   ↓
[FIVE SPECIALIST ENGINES] — run in parallel on the same computed chart
   ① WESTERN NATAL    → personality, life areas, current transits (tropical)
   ② VEDIC PREDICTIVE → nakshatra, Vimshottari dasha timeline, D9, Ashtakavarga, Sade Sati (sidereal)
   ③ COMPATIBILITY    → synastry scoring + composite/Davison (two-chart)
   ④ THAI+Bazi        → ปีนักษัตร/ธาตุ, 4 pillars, เลขเจตา, ตรียัมปาไถ, clash years
   ⑤ TRANSIT/TIMING   → exact hit dates (this is what makes it "present-moment")
   ↓
[FUSION LAYER] — one voice, no contradictions shown to user
   ↓
[OUTPUT TEMPLATES] — dated, concrete sentences per life domain
   (career · love · money · health · family/home · spiritual growth)
```

---

## 2 · VERIFIED BASE DATA (test case = vault owner / เจ้าของ vault)

**เกิด / Born:** 19 พ.ค. 2540 (1997-05-19) 05:45 ICT · ชลบุรี (13.36N, 100.98E)

### Tropical (สากล)
| จุด | ราศี | องศา |
|---|---|---|
| Sun | Taurus พฤษภ | 28.05° |
| Moon | Libra ตุลย์ | 17.37° |
| Asc | **Taurus พฤษภ (แก้แล้ว — ไม่ใช่พิจิก)** | ~25.9° |
| Mercury | Taurus | 3.38° |
| Venus | Gemini (**chart ruler!**) | 10.15° |
| Mars | Virgo | 19.32° |
| Jupiter | Aquarius | 21.21° |
| Saturn | Aries (**fall**) | 16.08° |
| Uranus | Aquarius | 8.70° |
| Neptune | Capricorn | 29.92° |
| Pluto | Sagittarius | 4.45° |
| NN/Rahu | Virgo | 25.75° |
| MC | Aquarius | 16.43° |

### Sidereal Lahiri (ไทย/เวท)
| ดาว | ราศี | องศา | หมายเหตุ |
|---|---|---|---|
| อาทิตย์ | พฤษภ | 4.37° | |
| จันทร์ | กันย์ | 23.69° | **นักษัตร Chitra pada 1** (verify แล้ว 2.7% เข้า Chitra) |
| ลัคนา | **พฤษภ (แก้แล้ว)** | ~2.2° | chart ruler = ศุกร์ |
| พุธ | เมษ | 9.70° | |
| ศุกร์ | พฤษภ | 16.47° | **Domicile + Vargottama (D9 พฤษภเช่นกัน — คำนวณยืนยัน)** |
| อังคาร | สิงห์ | 25.64° | |
| พฤหัสฯ | มังกร | 27.53° | **Fall** |
| เสาร์ | มีน | 22.40° | |
| ราหู/เกตุ | กันย์/มีน | 2.07° | |

### ปีนักษัตร / Chinese year
ปีฉลู ธาตุไฟ (Fire Ox, Ding Chou 丁丑) — BaZi 4 เสาเต็ม (verify แล้วด้วย anchor คู่): ปี Ding-Chou 丁丑 · เดือน Yi-Si 乙巳 · **วัน Xin-You 辛酉 (Day Master ศุกร์ยิน — โลหะเครื่องประดับ, แข็งแรงจากไตรกาศมัตสย 巳酉丑 ครบ!)** · ชั่วโมง Xin-Mao 辛卯 — รายละเอียดใน `04-thai-bazi-engine-spec.md`

---

## 3 · VERIFIED PREDICTIVE TIMELINE (คำนวณสด 22 ส.ค. 2026 — แทนที่ตัวเลขเดิมใน vault)

### 3.1 Vimshottari Dasha (คำนวณใหม่แม่นยำ — `verify_calcs.py`)
| Mahadasha | เริ่ม | จบ |
|---|---|---|
| Mars (balance 6.81y) | เกิด 1997 | 2004-03-10 |
| Rahu | 2004-03-10 | 2022-03-10 |
| **Jupiter ← ปัจจุบัน** | **2022-03-10** | **2038-03-10** |
| Saturn | 2038-03-10 | 2057-03-10 |

**Antardasha ภายใน Jupiter MD:**
| AD | ช่วง | โทน |
|---|---|---|
| Ju-Ju | 2022-03 → 2024-04 | ขยายฐาน |
| **Ju-Sa ← NOW** | **2024-04-28 → 2026-11-10** | กดดัน/พิสูจน์โครงสร้าง (Saturn fall-sidereal ซ้อน) |
| Ju-Me | 2026-11-10 → 2029-02-16 | เปลี่ยนเฟส: สื่อสาร/เทคโนโลยี/การเงินไหลลื่นขึ้น |
| Ju-Ve | 2030-01 → 2032-09 | ช่วงศุกร์ (Venus domicile+vargottama) = peak ความรัก/ครอบครัว |

### 3.2 Exact transit hit dates (`transit_hits.py` — JPL DE421, แม่นระดับวัน)

⚠️ **CORRECTIONS vs vault notes / แก้ไขจากโน้ตเดิม:**
1. ~~"Jupiter ทับ Mars กำเนิดปลายปี 2026"~~ → **ไม่จริง**: Jupiter แค่*ย้ายเข้าราศี*สิงห์ 31 ต.ค. 2026 แต่**ทับองศา Mars กำเนิด (sidereal Leo 25.64°) จริงๆ = 28 ต.ค. 2027** (ผ่าน 3 ครั้ง: 2027-10-28, 2028-04-04, 2028-06-22 — retrograde triple-pass)
2. **Saturn Return แม่นยำ = 26 มี.ค. 2027 (ผ่านครั้งเดียว, no triple-pass)** — โน้ตเดิมบอก "ก.พ.-เม.ย. 2026 Saturn เข้าเมษ" ถูกส่วน ingress แต่จุด exact conj คือ 26 มี.ค. 2027

| วันที่ | เหตุการณ์ | โดเมนชีวิต | Engine |
|---|---|---|---|
| **2026-09-14** | Jupiter conj natal IC (Leo 16.43°) | บ้าน/ครอบครัว/ย้ายที่อยู่ | Western |
| **2026-09-27** | Jupiter conj Mai's Moon (Leo 18.95°) #1 | ความสัมพันธ์: อารมณ์เธอเปิด/อบอุ่น | Compat |
| **2026-10-31** | Jupiter เข้าสิงห์ (sidereal) | เริ่มปีขยาย | Vedic |
| **2026-11-10** | Antardasha Ju-Sa → Ju-Me | จบเฟสกดดัน 2.5 ปี → เฟสสื่อสาร/งานดีขึ้นชัด | Vedic |
| **2026-11-14** | Jupiter conj Mai's Sun (Leo 25.74°) #1 | ความสัมพันธ์: เธอเปล่งประกาย/โอกาสของเธอ | Compat |
| 2026-12-14 | Rahu → มังกร (sidereal) | แกน karmic ขยับ | Vedic |
| **2027-03-08** | Jupiter conj Mai Moon #2 (retro pass) | ความสัมพันธ์: รอบสะท้อน | Compat |
| **2027-03-26** | ⭐ **Saturn Return exact** (Aries 16.08°) | ชีวิต restructure จริงจัง: งาน/ความรับผิดชอบ/ประกาศสถานะ | Western |
| 2027-05-19 | Jupiter conj Mai Moon #3 (วันเกิด owner!) | ความสัมพันธ์ | Compat |
| **2027-10-28** | ⭐ **Jupiter conj natal Mars** (sidereal Leo 25.64°) #1 | พลังลงมือ/ความกล้าถูกขยาย — เริ่มโครงการใหญ่ | Vedic/Western |
| 2028-04-04 / 06-22 | Jupiter-Mars passes #2 #3 | ปิดรอบขยาย | — |
| ~Jun 2027+ | Saturn เข้า sidereal Leo → **Ashtama Shani dhaiya** (8th-from-Moon, เข้มข้น มิ.ย. 2027–เม.ย. 2030) — *Sade Sati จริง: 27 ส.ค. 2036 → 11 ธ.ค. 2043 (verify: BP Lama + scan)* | ช่วงทดสอบ/บริหารพลังงาน | Vedic |

### 3.3 House overlay — แก้ใหม่ทั้งชุดตามลัคนาพฤษภ / House overlay corrected for Taurus Asc

**Tropical whole-sign (Asc พฤษภทั้งคู่):**
- **ดวงอาทิตย์+พุธของ M ตกเรือน 1 ของ Mai** (พฤษภ) — เขาคือ "ตัวตน" ที่เธอรับเข้ามาใน identity
- **Sun+Moon ของ Mai ตกเรือน 4 ของ M** (สิงห์) — เธอคือ "บ้าน/ความอบอุ่น" ของเขา
- M Moon → เรือน 6 ของ Mai · Mai Venus (กรกฎ) → เรือน 3 ของ M · Mai Saturn → เรือน 2 ของ M (Venus-Saturn glue ยังอยู่)
- ~~โน้ตเดิม "Asc สวนกัน = mutual 7th house"~~ ผิด — จริงๆ **Asc ทั้งคู่ราศีเดียวกัน (พฤษภ)** = conjunct Asc overlay

*(Sade Sati: ยืนยันแล้ว **27 ส.ค. 2036 (Saturn→Simha) – 11 ธ.ค. 2043 (Saturn→Vrischika)**; ingresses ระหว่างทาง: Kanya 22 ต.ค. 2038, Tula 27 ม.ค. + 25 ก.ย. 2041 — BP Lama table + ephemeris scan ตรงกันทุกวัน · dhaiya ใกล้สุด: มิ.ย. 2027–เม.ย. 2030)*

---

## 4 · FUSION RULES / กฎการหลอมรวม (one voice per user)

**Precedence when systems disagree (จากสูงไปต่ำ):**
1. **Dasha context wins on THEME** (Vedic): สิ่งที่เกิดได้ต้องเป็นสิ่งที่ dasha "สัญญา" ไว้ก่อน — transit อื่นที่ขัดธีม = ลดน้ำหนัก
2. **Exact transit date wins on WHEN** (Western/Vedic gochar): วันที่ event ใช้ hit-date จาก ephemeris เสมอ ไม่ใช้ "ช่วงราศี"
3. **BaZi element advice wins on WHAT-TO-DO** (ปฏิบัติ): สี/ทิศ/กิจกรรมที่แนะนำในแต่ละวัน-ปี ใช้ favorable elements
4. **Thai numerology wins on PERSONAL DAY COLOR** (เลขเจตา/ตรียัมปาไถ): รายวัน
5. **Conflicts phrased as sequence, never contradiction:** เช่น dasha บอกโต, Saturn Return บอกกดดัน → "โครงสร้างเก่าถูกทดสอบเพื่อรองรับการโต (Ju-Sa→Ju-Me switch 10 พ.ย. 2026)"

**Output contract ต่อ user ต่อวัน/สัปดาห์/เดือน:**
- ทุกประโยคต้องมี **วันที่/ช่วงวันที่** + **โดเมนชีวิต** + **action ชัดเจน**
- ห้ามคำกำกวม ("อาจจะ", "ดูเหมือน") — ใช้ "ช่วง X ถึง Y: ..." 
- Confidence tag ทุก prediction: HIGH (exact hit, 2+ system agree) / MED (single system) / LOW (pattern-level)

---

## 5 · LIFE-DOMAIN COVERAGE MAP (ครบทุกด้าน — ไม่มีช่องว่าง)

| Domain | Primary engine | Secondary | Example output |
|---|---|---|---|
| 💼 Career | Vedic dasha + MC transits | BaZi output element, 10th house AV score | "Ju-Me AD เริ่ม 10 พ.ย. 2026: งานสื่อสาร/เทคโนโลยีขยับ ช่วง 27 เดือน" |
| ❤️ Love | Compatibility engine | Venus dasha periods, Jupiter-on-Venus/7th transits | "27 ก.ย.–14 พ.ย. 2026: window ทองของคู่ (Ju on her Moon→Sun)" |
| 💰 Money | BaZi wealth stars + Jupiter cycles | 2nd/11th house transits, Ashtakavarga | |
| 🏠 Home/Family | IC transits, 4th house | Ju conj IC 14 ก.ย. 2026, BaZi hour pillar | |
| 🩺 Health | Medical astrology map | Sade Sati stress windows, Saturn transits 6th | |
| 🧘 Spiritual | Nodes axis + Ketu periods | Chitra nakshatra themes, meditation timing (Panchang) | |

---

## 6 · CHILD SPECS (ไฟล์ลูกในโฟลเดอร์นี้)

| ไฟล์ | Engine | สถานะ |
|---|---|---|
| `01-transits-2026-2027.md` | Timing engine | subagent running |
| `02-vedic-deep-dive.md` | Vedic predictive engine | subagent running |
| `03-synastry-engine-spec.md` | Compatibility engine | subagent running |
| `04-thai-bazi-engine-spec.md` | Thai+BaZi engine | subagent running |
| `verify_calcs.py` / `transit_hits*.py` | Reference implementations (runnable!) | ✅ verified today |

---
*หมายเหตุวิธีวิทยา: ตำแหน่ง/วันที่ทั้งหมดในเอกสารนี้คำนวณจาก JPL DE421 ผ่าน skyfield (repo scripts) — ส่วนการตีความเป็นกรอบโหราศาสตร์เพื่อการใคร่ครวญ ไม่ใช่ข้อเท็จจริงทางวิทยาศาสตร์*
