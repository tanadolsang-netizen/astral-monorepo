# 02 · VEDIC ENGINE SPEC — Jyotish Predictive Module
> **EN:** Deterministic, implementable rules for the app's Vedic engine. Every formula ports 1:1 to Python. Test case = vault owner (19 May 1997, 05:45 ICT, Chonburi) whose numbers are already machine-verified by `verify_calcs.py`.
> **TH:** กฎการทำงานแบบ deterministic สำหรับเอนจินสายพระเวท ทุกสูตร port เป็น Python ได้ตรงๆ · ดวงทดสอบ = เจ้าของ vault (19 พ.ค. 2540, 05:45 น. ชลบุรี) — ตัวเลขผ่านการคำนวณจริงแล้วทั้งหมด

---

## 0. Input contract / สัญญาอินพุต
```
birth_local: ISO datetime, tz offset hours, lat, lon
pipeline:    skyfield + JPL DE421 (offline) → ecliptic longitudes
ayanamsa:    Lahiri ≈ 23.68 + (year_frac − 1997) × (50.29/3600)   # drift term included
sid_lon      = (trop_lon − ayanamsa) mod 360
```
⚠️ ทุกการอ้าง "ราศี" ในโมดูลนี้ = **sidereal Lahiri เท่านั้น** ห้ามผสม tropical

---

## 1. Nakshatra — ตาราง 27 นักษัตร + อัลกอริทึม

**EN:** Each nakshatra = exactly 13°20′ (= 40/3 °). Absolute sidereal longitude → index & pada:

```python
SPAN = 360/27                      # 13.333333°
idx  = int(lon // SPAN)            # 0..26
pada = int(((lon % SPAN) / SPAN) * 4) + 1   # 1..4
frac_into = (lon % SPAN) / SPAN             # for dasha balance
```

| # | Nakshatra | ช่วง (abs °) | Lord | | # | Nakshatra | ช่วง (abs °) | Lord |
|---|---|---|---|---|---|---|---|---|
| 1 | Ashwini | 0.000–13.333 | Ketu | | 15 | Swati | 186.667–200.000 | Rahu |
| 2 | Bharani | 13.333–26.667 | Venus | | 16 | Vishakha | 200.000–213.333 | Jupiter |
| 3 | Krittika | 26.667–40.000 | Sun | | 17 | Anuradha | 213.333–226.667 | Saturn |
| 4 | Rohini | 40.000–53.333 | Moon | | 18 | Jyeshtha | 226.667–240.000 | Mercury |
| 5 | Mrigashira | 53.333–66.667 | Mars | | 19 | Mula | 240.000–253.333 | Ketu |
| 6 | Ardra | 66.667–80.000 | Rahu | | 20 | P.Ashadha | 253.333–266.667 | Venus |
| 7 | Punarvasu | 80.000–93.333 | Jupiter | | 21 | U.Ashadha | 266.667–280.000 | Sun |
| 8 | Pushya | 93.333–106.667 | Saturn | | 22 | Shravana | 280.000–293.333 | Moon |
| 9 | Ashlesha | 106.667–120.000 | Mercury | | 23 | Dhanishta | 293.333–306.667 | Mars |
| 10 | Magha | 120.000–133.333 | Ketu | | 24 | Shatabhisha | 306.667–320.000 | Rahu |
| 11 | P.Phalguni | 133.333–146.667 | Venus | | 25 | P.Bhadrapada | 320.000–333.333 | Jupiter |
| 12 | U.Phalguni | 146.667–160.000 | Sun | | 26 | U.Bhadrapada | 333.333–346.667 | Saturn |
| 13 | Hasta | 160.000–173.333 | Moon | | 27 | Revati | 346.667–360.000 | Mercury |
| 14 | **Chitra** | **173.333–186.667** | **Mars** | | | | | |

**Formal resolution — Hasta vs Chitra borderline / ตัดสินกรณีใกล้เขต:**
- **TH:** จันทร์ดวงทดสอบ = 173.69° ≥ 173.3333° → **Chitra pada 1 เด็ดขาด** (เข้าไปในเขต 0.357°) จันทร์เคลื่อน ~0.009°/นาที ดังนั้นเวลาเกิดต้องคลาดไป**เกิน ~40 นาที**จึงจะหล่นไป Hasta — เกิน margin ความไม่แน่นอนของเวลาเกิด (~ไม่กี่นาที) ⇒ สรุปได้แบบ deterministic: **Chitra p1, dasha lord = Mars**
- **EN:** Moon 173.69° is inside Chitra by 0.357°; birth-time uncertainty of ±10 min shifts Moon ±0.09° ⇒ verdict robust. Rule for engine: report nakshatra + distance-to-boundary; flag "borderline" only if margin < 0.15°.

---

## 2. Vimshottari Dasha — คณิตศาสตร์เป๊ะ

```
lords order : Ketu Venus Sun Moon Mars Rahu Jupiter Saturn Mercury
years       :  7    20    6   10   7    18    16      19     17     (=120)
balance_at_birth = (1 − frac_into_nakshatra) × years[lord_of_moon_nakshatra]
MD start_k = cumulative from birth; AD within MD: dur(MD_L, AD_l) = years[MD_L]×years[AD_l]/120,
             sequence starts at AD = MD lord; PD recurses identically.
```
**Verified test-case output / ผลคำนวณจริง (ground truth):**
| Period | Start | End |
|---|---|---|
| Mars MD (balance 6.81y) | birth 1997-05-19 | 2004-03-10 |
| Rahu MD | 2004-03-10 | 2022-03-10 |
| **Jupiter MD** | **2022-03-10** | **2038-03-10** |
| — Jupiter-Saturn AD ← *NOW (Aug 2026)* | 2024-04-28 | 2026-11-10 |
| — Jupiter-Mercury AD | 2026-11-10 | 2029-02-16 |
| — Jupiter-Ketu AD | 2029-02-16 | 2030-01-22 |
| — Jupiter-Venus AD | 2030-01-22 | 2032-09-22 |
| Saturn MD | 2038-03-10 | 2057-03-10 |

Engine rule: always print current MD+AD with dates and the next transition date. Jupiter = MD lord while owner's Jupiter sits Capricorn (**fall**, sidereal) → theme "ผลต้องแลกด้วยความพยายาม" consistent with dignity analysis.

---

## 3. Navamsha D9 + Vargottama detector

**Two equivalent mappings (engine implements both, asserts equal):**
```python
# A) Parashari element-counting
part  = int(deg_in_sign // (30/9))
start = sign_idx if sign_idx % 3 == 0 else (sign_idx + 8) % 12 if sign_idx % 3 == 1 else (sign_idx + 4) % 12
d9_A  = (start + part) % 12
# B) Continuous
d9_B  = int((sign_idx*30 + deg_in_sign) // (30/9)) % 12
assert d9_A == d9_B
vargottama = (d9 == sign_idx)
```
**Test-case D9 (verified):** Venus Tau→Tau **VARGOTTAMA** · Sun→Aqu · Moon→Leo · Merc→Gem · Mars→Sco · Jup→Vir · Sat→Cap · Rahu→Cap · Ketu→Can

**Reading rules (marriage):** Venus condition in D9 = how D1 love-signature delivers under real conditions; vargottama Venus = strongest possible stability of the love/values axis; DK planet compared against partner's luminaries (see §6 cross-check).

---

## 4. Ashtakavarga / Sarvashtakavarga

- **Bindu tables:** canonical source = BPHS (Parashara) standard benefic-point tables; total = 337 bindus over 12 signs always (sanity check in CI). Encode as CSV asset `ashtakavarga_bindus.csv`; compute per-planet contributions then Sarvashtakavarga sum.
- **Thresholds (vidhata.app + vault convention):**
  - **TH:** ≥35 เยี่ยม · 30–34 ดี · 25–29 ปานกลาง · 20–24 ระวังเริ่มโครงการใหญ่ในเรือนนั้น · <20 อ่อนแอ เลี่ยงเริ่มเรื่องใหญ่
  - **EN:** ≥35 excellent · 30–34 good · 25–29 mixed · 20–24 caution · <20 weak — transit results through a sign scale with its SAV score.
- **House-7 rule:** SAV(house7) < ~24 → delays/effort in partnership; gap house7−house1 large positive → partner may dominate.
- Engine prints per-house verdict only for houses the user asks about (career=h10, love=h5/h7, money=h2/h11, health=h6).

---

## 5. Saturn-from-Moon detectors — ⚠️ แก้ข้อสรุปเดิมของ vault

```python
def saturn_doshas(natal_moon_sign, saturn_sign):
    d = (saturn_sign - natal_moon_sign) % 12
    return {'sade_sati_phase': {11:'rise',0:'peak',1:'set'}.get(d),
            'dhaiya': d in (3, 7),        # 4th / 8th from Moon
            'ashtama_shani': d == 7, 'kantaka_shani': d in (1,2)}
```

**Corrected timeline for Moon-Virgo test case (sidereal Lahiri ingresses):**
| Event | Date | Status |
|---|---|---|
| Saturn → sidereal Pisces (7th from Moon) | 2025-03-29 | neutral for Moon-doshas |
| Saturn → sidereal Aries (8th) | **2027-06-03** (retro back 2027-10-20, final 2028-02-23) | **Ashtama Shani / 8th-dhaiya starts ~mid-2027 → runs to ~2030** |
| Saturn → Leo (12th) = **true Sade Sati begin** | **≈ mid-2037** | rise phase |
| Sade Sati ends (exits Libra) | ≈ 2044 | — |

> **EN correction:** earlier drafts said "Sade Sati starts 2027" — wrong. Mid-2027 brings **Ashtama Shani** (Saturn 8th from Moon: transformation/pressure period), NOT Sade Sati (which requires 12th/1st/2nd = Leo/Virgo/Libra, reached ~2037).
> **TH แก้ไข:** กลาง 2027 คือ **อัษฎมะเสารีย์** (เสาร์ที่ 8 นับจากจันทร์กันย์) — ช่วงกดดัน/เปลี่ยนผ่านลึก ไม่ใช่ซาเดซาติ ซาเดซาติจริงเริ่มราว 2037 จบราว 2044
> *(Ingress dates: drikpanchang-standard values; re-verify against drikpanchang.com before app release — confidence HIGH, source-check pending)*

---

## 6. Chara Karaka (Jaimini 7-scheme)

```python
rank planets (Sun..Saturn, exclude nodes) by degree-within-sign DESC
roles = AK(soul), AmK(career), BK, MK, PuK, GK, DK(spouse)
# 8-scheme variant includes Rahu (degree counted 30−deg) — engine ships 7-scheme default
```
**Verified:** AK=Jupiter 27.53° · AmK=Mars 25.64° · BK=Moon · MK=Saturn · PuK=Venus · GK=Mercury · **DK=Sun 4.37°**

Meanings: AK-Jupiter = soul path via philosophy/teaching, lesson = true wisdom vs borrowed doctrine · DK-Sun = spouse magnetic/leader-type, pushes ego-growth. **Cross-validation:** partner Mai carries Sun-conj-Moon in Leo (double-Leo leadership signature) — DK reading matches observed partner archetype ⇒ use this pairing as the engine's regression test.

---

## 7. Output templates (app-facing, no vague words)

```
TH: "ช่วง {AD_lord} ภายในมหาทศา {MD_lord} ({ad_start} – {ad_end}) เน้นผลด้าน{domain} — จุดเปลี่ยนถัดไป {next_transition}"
EN: "{MD_lord} mahadasha / {AD_lord} antardasha until {date}: expect {domain} focus; next shift {date}."
Dosha alert: "Ashtama Shani begins {date}: pressure on shared finances & deep change; avoid new debt launches between {window}."
Confidence: every line carries {confidence: HIGH|MEDIUM|source-pending}
```

---
*Feeds: NEW-AI-REBORN `/v1/*` endpoints · sibling specs: 01-transit · 03-synastry · 04-thai-bazi · master: 00-MASTER-INDEX.md*
