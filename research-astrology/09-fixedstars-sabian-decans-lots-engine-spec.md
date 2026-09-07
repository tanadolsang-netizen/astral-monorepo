# 09 · FIXED STARS + SABIAN SYMBOLS + DECANS + ARABIC LOTS — ENGINE SPEC
> **EN:** Depth-layer add-on module. All values J2000 epoch; runtime must precession-adjust: lon(t) = lon_J2000 + (year − 2000) × 50.29″/yr (for 1997: −0.25°).
> **TH:** โมดูลเสริมความลึก 4 ชั้น · ค่าดาวฤกษ์ทั้งหมดเป็น J2000 — รันไทม์ต้องปรับ precession (+50.29″/ปี; ปี 1997 ลบ ~0.25°)

---

## 1 · FIXED STARS / ดาวฤกษ์

**Orb rules:** conj กับ luminaries (Sun/Moon) ≤ 1° · กับดาวเคราะห์ ≤ 30′ · กับ ASC/MC ≤ 1°. นอกเหนือจากนี้ = ไม่นับ (ห้ามยืด)

| Star | J2000 lon | Test-case contact | Orb | Verdict |
|---|---|---|---|---|
| **Aldebaran** (royal, Watcher of East) | 9°47′ Gemini | **Venus 10.15° Gemini** | **0°28′** | ✅ **HIT — chart ruler on a Royal Star** |
| Gienah (γ Corvus, the Raven) | 17°06′ Libra | **Moon 17.37° Libra** | **0°19′** | ✅ HIT [VERIFY exact J2000 value] |
| Alcyone (Pleiades) | 29°58′ Taurus | Sun 28.05° Taurus | 1°56′ | ⚠️ zone-only (Pleiades cluster 28 Tau–0 Gem) — mention as "Pleiades zone", no formal aspect |
| Regulus (royal) | 29°50′ Leo (2000) → 0° Vir (2012) | NN 25.75° Vir | ~4° | ❌ miss — do not force |
| Antares 9°46′ Sag · Fomalhaut 3°52′ Pis · Sirius 14°05′ Can · Spica 23°50′ Lib · Deneb Algedi 23°33′ Cap | — | — | >2° | ❌ all miss |

**Meaning templates:**
- **Venus–Aldebaran (TH):** "ศุกร์ผู้เป็นเจ้าลัคนาขึ้นบนดาวหลวงอัลดีบารัน — เสน่ห์ที่ได้มาพร้อมมาตรฐาน: ประสบความสำเร็จด้านความรัก/ศิลปะ/ทรัพย์เมื่อรักษาความซื่อตรง แต่ถ้าล่อลวง/โกง ดาวหลวงจะทวงคืนรวดเร็ว"
- **Venus–Aldebaran (EN):** "Chart-ruler Venus on royal Aldebaran: charisma with integrity attached — success in love/art/finance through honor; the royal star revokes quickly if integrity breaks."
- **Moon–Gienah (TH):** "จันทร์บนกีเอนาห์ นกเรเวน — สัญชาตญาณอ่านคนเป็น ฉลาดส่งสาร ระวังเล่าเรื่องเกินจริงเวลาอารมณ์พลิก"
- Sources: Brady, *Brady's Book of Fixed Stars*; constellations-of-words.com tables. [VERIFY both J2000 longitudes against source at build time]

**Engine rule:** star table = JSON `[{name, lon_j2000, mag, meaning_en, meaning_th}]`; runtime adds precession; contact check only conj (no aspects to stars).

## 2 · SABIAN SYMBOLS (Jones/Rudhyar — 360 phrases)
**Indexing:** `degree = ceil(planet_deg)` (28.05° Taurus → Taurus 29). Source: Rudhyar, *An Astrological Mandala* [VERIFY phrases verbatim at build time].

| Point | Degree | Symbol (EN) | TH |
|---|---|---|---|
| Sun | Taurus 29 | "Two cobblers working at a table" | "ช่างทำรองเท้าสองคนกำลังทำงานที่โต๊ะเดียวกัน — ความชำนาญผ่านการฝีมือช่าง ทำงานเป็นทีมเงียบๆ คุณค่ามาจากความละเอียด" |
| Moon | Libra 18 | "Two men placed under arrest" | "ชายสองคนถูกจับกุม — บทเรียนอารมณ์: ผลจากการฝ่าฝืนกติกาสังคม/ความยุติธรรม ต้องรับผิดร่วมกัน ใคร่ครวญเรื่องขอบเขต" |
| ASC | Taurus 26 | "A Spanish gallant serenades his beloved" | "หนุ่มสเปนเซเรนาเดขับกล่อมคนรัก — บุคลิกภายนอกโรแมนติกมีศิลป์ กล้าแสดงความรู้สึกแบบมีริทึมของตัวเอง" |
| MC | Aquarius 17 | "A watchdog standing guard" | "สุนัขเฝ้ายามปกป้องเจ้านาย — อาชีพ/ภาพลักษณ์: ผู้พิทักษ์ระบบ/เทคโนโลยีที่เชื่อถือได้ มาตรฐานสูงเรื่องความภักดี" |

**Engine rule:** `sabian[sign*30 + ceil(deg)]` → JSON array 360 entries; output = 1 sentence appended to natal reading.

## 3 · DECANS (Chaldean faces)
Test-case **Sun = Taurus 3rd decan (20–30°) — Saturn face**: "material mastery through patience and structure; builds slowly but permanently; distrust of shortcuts." TH: "ทศาที่ 3 ของพฤษภ ปกครองโดยเสาร์ — เชี่ยวชาญวัตถุด้วยความอดทนและโครงสร้าง สร้างช้าแต่มั่นคง ไม่เชื่อทางลัด"
Engine: decan ruler = Chaldean sequence per element (fire: Mars/Sun/Venus; earth: Mercury/Saturn/Jupiter; air: Saturn? — use standard Chaldean order table [VERIFY]; water: Mars/Sun/Venus pattern by sign start). Ship as lookup table.

## 4 · ARABIC LOTS (Hermetic)
**Sect flag:** birth 05:45 vs sunrise ~05:52 → Sun below horizon → **nocturnal (borderline 7 min)** → engine computes BOTH and labels "sect-uncertain".

| Lot | Day formula | Night formula | Test case (day) | Test case (night) |
|---|---|---|---|---|
| Fortune | ASC + Moon − Sun | ASC + Sun − Moon | **15.25° Libra** | **6.61° Capricorn** |
| Spirit | ASC + Sun − Moon | ASC + Moon − Sun | 6.61° Capricorn | 15.25° Libra |
| Marriage (male chart, Hermes/Paulus) | ASC + Venus − Saturn | same (some swap) | **20.00° Cancer** | 20.00° Cancer |

**⭐ Cross-check discovery:** **Mai's natal Venus = 19.90° Cancer — conj M's Lot of Marriage 20.00° Cancer, orb 0.10°.** [VERIFY formula against Paulus Alexandrinus translation] If confirmed at build time, add to compat engine as karmic-marriage significator (+8 weight, same scale as 03 spec).
Sources: Paulus Alexandrinus, *Introductory Matters*; astro.com Lots documentation.

## 5 · Output integration (max 1 sentence per layer)
- TH: "ดาวฤกษ์: [Aldebaran sentence] · ซาเบียน: [degree phrase] · ดีแคน: [decan sentence] · ลอต: [Fortune/Marriage sentence]"
- EN: same order. Confidence: stars HIGH (orb strict), Sabian MED (symbolic layer), Lots MED (sect uncertainty flagged).

## Implementation Notes (QA 2026-08-23)
**(a) Constants:**
- Royal Stars J2000 ecliptic longitudes: Aldebaran 9.8° Gemini (69.8° abs), Regulus 29.8° Leo (149.8°), Antares 9.7° Sagittarius (249.7°), Fomalhaut 3.8° Pisces (333.8°). Apply ~50.3"/yr precession note; orb rule <=2°.
- Sabian: 360 symbols, index = floor(degree_in_sign)+1, per sign Aries 1..Pisces 30.
**(b) Ground truth (M):** Sun Taurus 4.4° sidereal → Sabian "Taurus 5: A widow at fresh graves shed light on past" family (verify against table in module); ASC Taurus 2.2° → Taurus 3 tier. Royal star check runs on tropical positions.
**(c) Degradation:** missing table entry → {'symbol': 'Sabian symbol N of <sign>'}; module never raises.
