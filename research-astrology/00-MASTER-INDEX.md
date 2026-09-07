# 00 · MASTER INDEX — Unified Fortune Engine
> **เป้าหมาย:** แอพดูดวงที่แม่นที่สุด — รวมทุกศาสตร์เป็นเอนจินเดียว ตอบทุกด้านของชีวิต ณ ปัจจุบัน **user ไม่ต้องเดาเอง**
> **Status:** ✅ spec v1.0 — spec บนดิสก์ครบ 14 ไฟล์ (01–07, 09–15 · ไม่มีไฟล์ 08 = ยังอยู่คิว wave 2) · อัปเดต 22 ส.ค. 2026 — index นี้คือแผนที่กลาง

---

## 1. สถาปัตยกรรมเอนจิน (Unified Architecture)

```
INPUT: วันเกิด + เวลาเกิด + พิกัด (+ tz auto-detect)
   │
   ▼
┌─────────────────────────────────────────────┐
│ CORE CHART COMPUTATION (deterministic)      │
│ ephemeris: JPL DE421 offline via skyfield    │
│ ayanamsa: Lahiri = 23.68 + (Y−1997)·50.29″/y│
│ output: tropical + sidereal + ASC + houses   │
└──────────────┬──────────────────────────────┘
               │ แจกจ่ายตำแหน่งให้ engine ทั้งหมด (spec 01–15)
   ┌───────────┼───────────────┬──────────────────┐
   ▼           ▼               ▼                  ▼
[01 TRANSIT] [02 VEDIC]   [03 SYNASTRY]     [04 THAI/BAZI]
   + specs 05–15: ziwei · human design · tarot · fixed stars/Sabian/Lots ·
     asteroids · numerology · i-ching · nine-star ki · mayan · cosmobiology
  วันนี้–      dasha, D9,    คู่/ความสัมพันธ์   ปีนักษัตร, 4 เสา,
  ปีนี้        sade sati,    scoring+timing    เลขเจตา, ตรียัมปาไถ
               karaka
   └───────────┴───────┬───────┴──────────────────┘
                       ▼
            FUSION LAYER (กฎ precedence §3)
                       ▼
       OUTPUT CONTRACT: ประโยคภาษาไทย/อังกฤษ ที่มี
       • วันที่เป๊ะ • domain ชีวิต • confidence
       • ไม่มีคำกำกวม — user ไม่ต้องตีความเอง
```

## 2. ไฟล์ในชุดนี้

| ไฟล์ | สาย | เนื้อหา | สถานะ |
|---|---|---|---|
| `01-transit-engine-spec.md` | Western transit + eclipse + node | pipeline, rule table→domain, orbs, retro triple-pass — วันทั้งหมด verify ด้วย DE421/skyfield (`transit_hits.py`) | ✅ |
| `02-vedic-engine-spec.md` | Vedic/Jyotish | nakshatra, Vimshottari, D9/vargottama, Ashtakavarga, Sade Sati (แก้: 2027=Ashtama Shani, Sade Sati ~2037), Chara Karaka — ground truth: `verify_calcs.py` (DE421) | ✅ |
| `03-synastry-engine-spec.md` | Compatibility | weighted scoring 0–100, house overlay (แก้ overlay ใหม่ทั้งชุดหลังแก้ลัคนา), composite/Davison (Sun = Cancer 11°54′ — แก้จาก Gemini), karmic nodes, commitment windows — cross-aspects DE421-verified (tropical) | ✅ |
| `04-thai-bazi-engine-spec.md` | ไทย + จีน | BaZi 4 เสา verify ด้วย lunar-python + JDN day-pillar offset **+49** (`verify_bazi.py`; 丁丑/乙巳/辛酉/辛卯), ชง-ฮับ, เลขเจตา, ตรียัมปาไถ | ✅ |
| `00-MASTER-unified-engine.md` | แม่บทฉบับรวม (agent legacy, มี timeline exact dates) | architecture + verified data + predictive timeline | ✅ |
| `verify_*.py` × 3 · `transit_hits*.py` · `resolve_asc.py` · `ephe/` × 3 | assets: ground-truth scripts + Swiss Ephemeris data | รายการเต็ม + หน้าที่ → **§2a Assets** | ✅ |
| `05-ziwei-doushu-engine-spec.md` | จีน-ดาวม่วง 紫微斗數 | casting + 12 palaces + 四化 + 大限 (lunar-python verified) | ✅ |
| `06-human-design-engine-spec.md` | Human Design | gate wheel (Gate 41 @ 02° Aquarius), Type/Authority/Profile, worked gates | ⚠️ pending verification |
| `07-tarot-engine-spec.md` | ทาโรต์ | seeded RNG (Fisher–Yates), spreads, card JSON schema, astro-fusion — deterministic, ไม่พึ่ง ephemeris | ✅ |
| `09-fixedstars-sabian-decans-lots-engine-spec.md` | ดาวฤกษ์+Sabian | Venus-Aldebaran hit, Lots computed (Marriage orb .1° w/ Mai Venus); ⚠️ Gienah รอ exact J2000 [VERIFY] | ✅ |
| `10-asteroids-engine-spec.md` | ดาวเคราะห์น้อย | Swiss Ephemeris computed positions; M Juno sextile Mai Sun 0.01° | ✅ |
| `11-numerology-engine-spec.md` | เลขศาสตร์ตะวันตก | LP5/BD1/PY26=7 worked + Thai cross-link | ✅ |
| `12-iching-engine-spec.md` | อี้จิง 易經 | King Wen table + coin-probability casting | ✅ |
| `13-ninestar-ki-engine-spec.md` | ญี่ปุ่น 九星気学 | star formulas + Lo Shu movement — constant dispute (1997→3 vs 6) unresolved | ⚠️ pending verification |
| `14-mayan-tzolkin-engine-spec.md` | มายา Dreamspell | Kin 239 Blue Overtone Storm (verified vs published table) | ✅ |
| `15-cosmobiology-midpoints-engine-spec.md` | Cosmobiology | Ebertin midpoints, 7/7 numbers machine-reproduced | ✅ |
| *(wave 2 queued)* | — | Varshaphal/Tajika · Electional spec · Tibetan Kalachakra · **08 Birth-time-unknown fallback** | 📋 |

**Test case กลางทุกไฟล์ต้องผ่าน:** ดวงเจ้าของ vault (19 พ.ค. 2540) + ดวง Mai (18 ส.ค. 2544) — ตัวเลข verify แล้วทั้ง tropical/sidereal

### 2a · Assets บนดิสก์ — verify scripts + ephe/

| ไฟล์ | หน้าที่ | spec ที่อ้าง |
|---|---|---|
| `verify_calcs.py` | ground truth natal/Vimshottari/dasha (JPL DE421 via skyfield) | 02 · §4 |
| `verify_bazi.py` | BaZi 4 เสา — lunar-python + JDN arithmetic (day-pillar offset +49) | 04 · 05 |
| `verify_asteroids.py` | Juno/Chiron/Lilith/Vesta/Pallas/Ceres — pyswisseph + `./ephe` | 10 |
| `transit_hits.py` · `transit_hits2.py` | สแกน transit วันจริง (DE421) | 01 |
| `resolve_asc.py` | ASC first-principles (LST→RAMC→ASC) — ยืนยันลัคนาพฤษภ 25.96° | 00-MASTER-unified |
| `ephe/seas_18.se1` | Swiss Ephemeris data — main asteroids | 10 |
| `ephe/semo_18.se1` | Swiss Ephemeris data — moon/osculating elements | 10 |
| `ephe/sepl_18.se1` | Swiss Ephemeris data — main planets | 10 |

> ⚠️ ช่องว่างที่รู้ตัว: **ไม่มีไฟล์ spec 08** (Birth-time-unknown fallback — คิว wave 2) · spec 01 อ้าง `transit_week_scan.py` ซึ่ง**ยังไม่มีบนดิสก์** (มีแค่ `transit_hits.py` / `transit_hits2.py`)

## 3. กฎ FUSION — เมื่อหลายระบบบอกไม่ตรงกัน (draft v1)

1. **Timing ใช้ transit/dasha เป็นนาฬิกาหลัก** — ระบบอื่นให้ "ธีม" ไม่ให้ "วัน"
2. **Domain routing:** ความรัก → synastry + Venus-transit; การงาน → MC/Saturn/Jupiter + AmK; การเงิน → house 2/11 + BaZi favorable element; สุขภาพ → house 6 + ธาตุ; จิตวิญญาณ → Ketu/house 12 + AK
3. **เสียงที่ชนกัน:** ถ้า 2 ระบบให้ polarity ตรงข้าม (เช่น transit ดี / ปีนักษัตรชง) → พิมพ์ทั้งคู่แบบมีเงื่อนไข: *"ช่วง X โอกาสเปิดในเรื่อง A แต่ต้องบริหารความเสี่ยง B — เลี่ยงการตัดสินใจใหญ่ในวันที่ Y"*
4. **ห้ามสังเคราะห์ข้ามระบบราศี** (tropical ≠ sidereal — ห้ามเทียบราศีตรงๆ ข้ามระบบ ยกเว้นใน layer ที่กำหนดไว้ชัด)
5. ทุก output ต้องมี `confidence` และ `source_system` กำกับ

## 4. ข้อมูลดิบที่ verify แล้ว (single source of truth)

### Owner — M (19 พ.ค. 2540, 05:45 ICT, ชลบุรี 13.36N 100.98E)
- Tropical: ☉ พฤษภ 28.05° · ☽ ตุลย์ 17.37° · **ASC พฤษภ 25.96°** (แก้บั๊กจากพิจิกแล้ว 15 ส.ค. 2026) · ♀ เมถุน 10.15° · ♂ กันย์ 19.32° · ♄ เมษ 16.08° · ☊ กันย์ 25.75°
- Sidereal Lahiri: ASC พฤษภ 2.28° · ☉ พฤษภ 4.37° · ☽ **กันย์ 23.69° (Chitra p1)** · ♂ สิงห์ 25.64° · ♃ มังกร 27.53° · ♄ มีน 22.40° · ☊ กันย์ 2.07°
- Vimshottari (verify_calcs.py): Rahu MD 2004→2022 · **Jupiter MD 2022-03-10→2038-03-10** · AD ปัจจุบัน Jupiter-Saturn จน 2026-11-10 → Jupiter-Mercury
- Karaka: **AK=พฤหัส, DK=อาทิตย์** (คู่ = ผู้นำ/magnetic — cross-check กับ Sun-Moon Leo ของ Mai ✓) · **Venus Vargottama** (พฤษภ D1=D9)
- ปีนักษัตร: ฉลู ธาตุไฟ (Fire Ox)

### Mai (18 ส.ค. 2544, 22:32 ICT, นนทบุรี 13.86N 100.52E)
- Tropical: ☉ สิงห์ 25.74° · ☽ สิงห์ 18.95° (Sun conj Moon ~7°) · ASC พฤษภ 6.34° · ♀ กรกฎ 19.90° · ☿ กันย์ 8.15° · ♂ ธนู 20.74° · ♄ เมถุน 13.59°

## 5. Definition of Done (ของชุด spec ทั้งหมด)

- [ ] ทุกไฟล์ bilingual TH/EN ครบทุก section
- [ ] ทุกสูตรมี pseudo-code ที่ port เป็น Python ได้ตรงๆ
- [ ] Test case ผ่านครบทุกไฟล์ (ตัวเลขตรงกับ verify_calcs.py)
- [ ] วันที่ทุกวันที่มีแหล่งอ้างอิง หรือคำนวณจาก ephemeris — ห้ามเดา
- [ ] Output template ไม่มีคำกำกวม ("อาจ", "น่าจะ" ใช้ได้เฉพาะกับ confidence ที่ระบุ)

---
*Research Dept · started 22 Aug 2026 · feeds: NEW-AI-REBORN backend (`C:/AI/NEW-AI-REBORN`) + Astral app*
