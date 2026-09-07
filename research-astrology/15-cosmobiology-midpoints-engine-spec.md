# 15 · COSMOBIOLOGY ENGINE SPEC — Midpoint Module (Ebertin-style)
> **EN:** Deterministic midpoint/cosmobiology engine per Reinhold Ebertin's *Combination of Stellar Influences* (Kombination der Gestirneinflüsse, 1940) conventions: shortest-arc midpoints, 90° dial, hard-aspect timing, principal-principle keywords. Tropical zodiac ONLY (cosmobiology is a Western system — never mix sidereal, see spec 01 ⚠️). Test case = M (1997-05-19 05:45 Chonburi), natal points machine-verified in 00-MASTER §2; M×Mai composite cross-ref spec 03.
> **TH:** เอนจินจุดกึ่งกลาง (คอสโมไบโอโลยี) ตามแนวไรน์ฮอลด์ เอเบอร์ติน หนังสือ *Combination of Stellar Influences* (1940): กึ่งกลางโค้งสั้น · ไดอัล 90° · จับเวลาด้วยมุมคับเท่านั้น · ใช้ระบบ tropical เท่านั้น ห้ามผสม sidereal · ดวงทดสอบ = M (ตัวเลข natal verify แล้วใน 00-MASTER §2) · composite คู่ M×ไหม อ้าง spec 03

---

## 1. Midpoint math / คณิตศาสตร์จุดกึ่งกลาง
```python
def midpoint(a, b):                    # shortest arc, wrap-safe — reuse 1:1 from spec 03 §3
    d = (b − a) % 360
    return (a + d/2) % 360 if d <= 180 else (a − (360−d)/2) % 360

def indirect(m):                       # crossed/indirect midpoint = ตรงข้ามของ direct
    return (m + 180) % 360             # valid contact point บนไดอัล เทียบเท่า direct

def angdiff(a, b):                     # มุมจริงที่เล็กที่สุด (reuse spec 01)
    x = abs(a − b) % 360
    return min(x, 360 − x)

# A + M = B structure (planetary picture): C sits ON midpoint(A,B) ⇔ A/B = C
# ⇔ angdiff(C, midpoint(A,B)) ≤ orb  OR  angdiff(C, indirect(A,B)) ≤ orb
hit = lambda c, m, orb: angdiff(c, m) <= orb or angdiff(c, (m+180)%360) <= orb
```
**Orbs (Ebertin COSI norms / ตามธรรมเนียมเอเบอร์ติน):**
| Tier | Orb | ใช้เมื่อ |
|---|---|---|
| Tight / แน่น | **≤ 1°** | natal picture ยืนยัน, transit trigger |
| Working / ใช้งาน | **≤ 2°** | สแกนหา candidate, synastry overlay |

**Direct vs indirect:** direct = กึ่งกลางโค้งสั้นระหว่างดาวสองดวง · indirect = จุดตรงข้าม (+180°) — บนไดอัล 90° ทั้งคู่คือตำแหน่งเดียวกัน ⇒ เอนจินเก็บ `(pair, direct_lon)` แล้วทดสอบ `c` กับทั้งสองข้างเสมอ
**90° dial sorting:** `dial = sorted(lon % 90)` — ดาวที่อยู่ตำแหน่งไดอัลเดียวกัน (±orb) = รูปภาพกึ่งกลาง แปลงกลับเป็น conj/square/opp ตอน render
**Data model:** `{a, b, direct: deg, indirect: deg, hits: [{point, side, orb}]}` ต่อทุก pair C(13,2)

## 2. Rule table — 20 core combinations / ตารางกฎ 20 คู่หลัก
Principal principle ตามแนว COSI — one-liner ต่อคู่ (EN + TH):

| # | Pair | Principal principle (EN) | หลักหลัก (TH) |
|---|---|---|---|
| 1 | **Sun/Moon** | Vitality–emotion axis: body and soul act as one | แกนชีพจร–จิตใจ: กายกับใจเป็นหนึ่ง |
| 2 | **Sun/Venus** | Love of life; self shines through joy | รักชีวิต: ตัวตนเปล่งประกายผ่านความสุข |
| 3 | **Venus/Mars** | Passion; raw attraction | ความหลงใหล: แรงดึงดูดดิบ |
| 4 | **Sun/Saturn** | Endurance vs obstacle; self built by discipline | อดทนสู้อุปสรรค: วินัยหล่อหลอมตัวตน |
| 5 | **Jupiter/Saturn** | Expansion meets its limit; growth needs frame | ขยายพบขอบเขต: เติบโตต้องมีกรอบ |
| 6 | **Mars/Saturn** | Discipline vs frustration; strength under compression | วินัย–คับขัน: แรงถูกบีบ ต้องบริหาร |
| 7 | **Uranus/Pluto** | Force of change; upheaval that rebuilds from root | แรงเปลี่ยนผ่านรุนแรง: ปฏิวัติจากราก |
| 8 | **Moon/Venus** | Affection; warmth, comfort-seeking | ความเอ็นดู: ใจอ่อนโยน แสวงหาความสบาย |
| 9 | **Mercury/Uranus** | Quick insight; lightning intuition | สติปัญญาไว: มโนทัศน์ฉับพลัน |
| 10 | **Venus/Saturn** | Loyalty tested; love proven over time/duty | ความภักดีถูกทดสอบ: รักผ่านเวลาและภาระ |
| 11 | **Mars/Pluto** | Drive-power; unstoppable force | แรงขับมหาศาล: ลงมือแล้วไม่หยุด |
| 12 | **Jupiter/Pluto** | Big power; game-scale ambition | อำนาจใหญ่: ฟางสุดท้ายระดับเปลี่ยนเกม |
| 13 | **Sun/Jupiter** | Success–growth; optimism, health expanding | สำเร็จ–เติบโต: โชคและสุขภาพขยายตัว |
| 14 | **Moon/Saturn** | Solemn feeling; disciplined, lonely depth | ใจจริงจังเก็บเงียบ: อารมณ์มีวินัย/เหงาลึก |
| 15 | **Venus/Neptune** | Romance & idealization; love as dream (watch projection) | โรแมนซ์เลือนราง: รักแบบฝัน — ระวังมองเกินจริง |
| 16 | **Mars/Uranus** | Sudden action; fast, decisive, accident-prone | ลงมือฉับพลัน: เร็วและเด็ดขาด ระวังหน้ามือ |
| 17 | **Saturn/Pluto** | Endurance through crisis; pressure that rebuilds | ทนผ่านวิกฤต: กดดันลึกเพื่อสร้างใหม่ |
| 18 | **Mercury/Saturn** | Serious mind; deep structured thinking | ความคิดจริงจัง: คิดลึก ช้าแต่แน่ |
| 19 | **Moon/Mars** | Emotional drive; feelings push action | อารมณ์ขับเคลื่อน: ใจร้อน ลงมือตามใจ |
| 20 | **Venus/Pluto** | Fascination; magnetic, consuming attraction | เสน่ห์เหนี่ยวรั้ง: ดึงดูดแบบหลงใหลลึก |

### Transit activation rule / กฎหน้าต่างเปิดใช้งาน
```python
TRIG_ASPECTS = (0, 90, 180)            # cosmobiology counts HARD contacts only (dial-equivalent)
ACTIVATION_ORB = 1.0                   # ≤1° = activation window; ≤2° = approaching/leaving tail
```
- **Rule:** transit planet reaching **≤1°** of any natal/composite midpoint axis (conj OR square OR opp — same dial position) ⇒ combination's principal principle FIRES during the window. Soft trine/sextile = ไม่นับ (COSI timing convention).
- **Window length by mover:** Moon ±ชม.–1 วัน · Sun/Mercury/Venus ≈ ±2–4 วัน · Mars ≈ 1–2 สัปดาห์ · Jupiter ≈ 2 สัปดาห์–2 เดือน (นับ retro triple-pass) · Saturn/outer ≈ 1–4 เดือน (triple-pass ปกติ)
- **Amplifier:** จันทร์ใหม่/เด็ดขาด/คราส ตกบน midpoint ≤1° = วัน mark เหตุการณ์ (event-day marker)
- **Priority stack:** transit→midpoint ที่มี natal picture อยู่แล้ว (§3) = แรงสุด เรียงก่อนใน report

## 3. WORKED EXAMPLE — M's chart / ตัวอย่างคำนวณจริง (tropical, 00-MASTER §2)
Input points (abs °): Sun 58.05 · Moon 197.37 · Mercury 33.38 · Venus 70.15 · Mars 169.32 · Jupiter 321.21 · Saturn 16.08 · Uranus 308.70 · Neptune 299.92 · Pluto 244.45 · NN 175.75 · MC 316.43 · ASC ~55.90 *(corrected Taurus ASC — supersedes old buggy Scorpio value)*

**Three notable natal midpoints:**
| Midpoint | คำนวณ | ผลลัพธ์ |
|---|---|---|
| **Sun/Moon** (vitality-emotion axis) | d=(197.37−58.05)=139.32≤180 → 58.05+69.66 | **127.71° = สิงห์ 7°43′** |
| **Venus/Mars** (passion) | d=(169.32−70.15)=99.17 → 70.15+49.59 | **119.74° = กรกฎ 29°44′** |
| **Sun/Venus** (love-life joy) | d=12.10 → 58.05+6.05 | **64.10° = เมถุน 4°06′** |

**Natal planet-on-midpoint pictures (scan all pairs × all points, orb ≤2°):**
| Picture (A/B = C) | Midpoint | Contact | Orb | Reading |
|---|---|---|---|---|
| **Ve/Ma = Ne** (indirect) | 119.74 กรกฎ 29°44′ | Neptune 299.92 opp | **0.19°** 🔥 | passion idealized — แรงดึงดูดแบบโรแมนซ์เลือนราง |
| **Su/Ve = Pl** (indirect) | 64.10 เมถุน 4°06′ | Pluto 244.45 opp | **0.35°** | joy fused with fascination — ความสุขผูกกับแรงหลงใหลลึก |
| **Ve/Ju = Sa** (direct) | 15.68 เมษ 15°41′ | Saturn 16.08 conj | **0.40°** | warm generosity under self-restraint |
| **Su/Mo = Ur** (indirect) | 127.71 สิงห์ 7°43′ | Uranus 308.70 opp | **0.99°** | vitality axis electrified — ตัวตน-ใจต้องการอิสระ/เหตุการณ์ฉับพลัน |

*(Regression test: engine must reproduce these 4 pictures + orbs from raw longitudes above.)*
**90-dial sort (lon%90):** Sa 16.08 · Mo 17.37 · Ne 29.92 · Me 33.38 · Ur 38.70 · MC 46.43 · Ju 51.21 · ASC 55.90 · Su 58.05 · Pl 64.45 · Ve 70.15 · Ma 79.32 · NN 85.75 — adjacent dial pairs <2° apart are candidate pictures.

## 4. Relationship add-on — composite IS a midpoint chart / composite = แผนที่กึ่งกลางทั้งแผน
- Every composite point = `midpoint(A_natal, B_natal)` — full formula + Davison distinction ใน **spec 03 §3** (cross-ref). Midpoint engine นี้คือ sub-routine ของ composite builder.
- **Relationship heart / ใจกลางความสัมพันธ์** = composite Sun/Moon midpoint — จุดวัดว่า "หัวใจ" ของความสัมพันธ์ตั้งอยู่ตรงไหน และ transit อะไรกดมัน

**Computed for M×Mai composite (cross-ref spec 03 §3):**
```python
midpoint(101.90,        # composite Sun Cancer 11°54'
         168.1667)      # composite Moon Virgo 18°10'
# d = 66.2667 ≤ 180 → 101.90 + 33.1333 = 135.0333
# = **Leo 15°02′ (สิงห์ 15°02′)** ✅ machine-verified
```
- **Commitment-window trigger:** transit hard-contact (≤1°, มุม 0/90/180) ถึง สิงห์ 15°02′ (หรือ square ตุลย์ 15° / opp ลมกรด 15°) ⇒ หน้าต่างตัดสินใจผูกพัน — ต่อยอด detector ของ spec 03 §5 (Jupiter/Saturn movers สำคัญสุด) · ⚠️ track tropically only — ห้ามหา sidereal equivalent ข้ามระบบ
- Engine rule: composite heart joins the daily scan target list beside natal midpoints (`targets += [135.03]`)

## 5. Output templates TH/EN — one-line activations for daily/monthly forecasts
```
TH: "{ดาว} {มุม} จุดกึ่งกลาง {A}/{B} กำเนิด ({ราศี} {องศา}) — {ธีมคู่ดาว} (orb {x}°) หน้าต่าง: {date_start}–{date_end}"
EN: "{planet} {aspect} natal {A}/{B} midpoint ({sign} {deg}°) — {principal principle fires} (orb {x}°); window: {dates}"

Daily TH ex:  "ดวงจันทร์ ☌ จุดกึ่งกลาง อาทิตย์/จันทร์ กำเนิด (สิงห์ 7°43′) — วันนี้ใจกับตัวตนตรงกัน เหมาะตัดสินใจเรื่องส่วนตัว (orb 0.8°)"
Daily EN ex:  "Moon conj natal Sun/Moon midpoint (Leo 7°43′) — body and mind aligned; decide personal matters today (orb 0.8°)."
Monthly TH ex:"{เดือน}: {ดาว} กด จุดกึ่งกลาง {A}/{B} ≤1° ช่วง {dates} — ธีม '{หลักหลัก}' เปิดใช้งาน วันแรงสุด {exact_date}"
Relate TH ex: "หน้าต่างใจกลางความสัมพันธ์ (composite Su/Mo สิงห์ 15°02′): {ดาว} เข้า ≤1° ช่วง {dates} — เหมาะขอผูกพัน/ตัดสินใจร่วมกัน"
```
House rules (same contract as specs 01/02/03): ห้ามคำกำกวม ("อาจจะ/เหมือนว่า") · ทุกบรรทัดมี มุม+orb+วันที่ · Confidence tag: HIGH (คำนวณจริง) | MEDIUM (interpretation) · max 2 midpoint lines/day (sort by orb then planet speed) เพื่อไม่ให้ user overload

---
*Feeds: `/v1/midpoints/*`, composite builder in `/v1/synastry/*` · sibling: 01-transit · 02-vedic · 03-synastry · 04-thai-bazi · master: 00-MASTER-unified-engine.md*

---

## Implementation Notes (QA 2026-08-23)

### Midpoint-tree formulas/constants (canonical form)
- Build: fix a stable sorted point order, enumerate every unordered pair i<j — C(13,2) = **78 pairs** for the full natal set.
- Direct midpoint, shortest arc, wrap-safe (algebraically identical to `(a+b)/2` with 180° handling):
  `d=(b−a)%360; direct = (a+d/2)%360 if d≤180 else (a+d/2−180)%360`; `indirect=(direct+180)%360`. Always test contactor `c` against BOTH sides: `hit = angdiff(c,direct)≤orb or angdiff(c,indirect)≤orb`.
- Orbs: scan/build the tree at the working tier **≤2°**; a picture counts as confirmed and a transit fires only at the tight tier **≤1°** vs natal planets & angles (hard contacts 0/90/180 only — COSI timing convention, §2).
- Frame rule: midpoint arithmetic is frame-independent (a constant ayanamsa shifts both endpoints and midpoint equally), but **hit tests must compare longitudes in ONE frame** — this engine is tropical-only (header ⚠️ stands).

### Ground truth (machine-recomputed 2026-08-23 — PASS)
- §3 midpoints reproduce exactly: Sun/Moon **127.71** (Leo 7°43′) · Venus/Mars **119.735→119.74** (Cancer 29°44′) · Sun/Venus **64.10** (Gemini 4°06′) · Venus/Jupiter **15.68** via the wrap branch (Aries 15°41′) ✓.
- All four natal pictures reproduce with unrounded orbs: Ve/Ma=Ne **0.185°** (prints 0.19) · Su/Ve=Pl **0.35°** · Ve/Ju=Sa **0.40°** · Su/Mo=Ur **0.99°** ✓ — the §3 regression set is valid as written.
- Cross-frame demo (CMD-requested sidereal pair): Sun **34.2°** + Moon **173.5°** sidereal abs (Lahiri ≈23.85° in 1997) → naive average **103.85° = Cancer 13.85° sidereal** ✓ (no wrap needed: Δ139.3° ≤180). Equals tropical Sun/Moon midpoint 127.71° − 23.85° = 103.86° — 0.01° gap is input rounding; frame-shift property verified. Arithmetic demo only; engine output stays tropical.
- Wrap regression: Jupiter/Saturn straddles 0° Aries → direct **348.645°**, indirect **168.645°** — never average naively across 0°.

### Degradation rule
- Fewer than 2 valid planetary longitudes ⇒ no tree; return empty `hits` with reason.
- Birth time unknown ⇒ ASC/MC unavailable ⇒ drop angle contacts, keep planet-only scan (flag output `angles: skipped`).
- Ephemeris failure on either endpoint ⇒ drop that pair — never interpolate.
- Never widen orbs past COSI norms to manufacture hits; the §5 cap (max 2 midpoint lines/day, sort by orb then planet speed) still applies in degraded mode.
