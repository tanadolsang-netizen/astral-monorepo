# 06 · HUMAN DESIGN ENGINE SPEC
> **EN:** Deterministic HD chart algorithm. Personality = natal moment; Design = planetary positions when Sun was 88° solar arc BEFORE birth (~88–89 days earlier). Test case: M, 19 May 1997 05:45 ICT Chonburi.
> **TH:** อัลกอริทึม Human Design แบบ deterministic — Personality = เวลาเกิด, Design = ตำแหน่งดาวเมื่อดวงอาทิตย์โคจรถอยไป 88° (~88-89 วันก่อนเกิด)

---

## 1 · Gate wheel (zodiac longitude → gate/line)
The 64-gate mandala starts at **Gate 41 beginning at 02°00′ Aquarius** (the start of the "quarter of initiation"). Standard gate order around the ecliptic (each gate = 5.625° = 360/64; each line = 0.9375°):

```
Order from 2° Aquarius — VERIFIED 2026-08-23 vs ≥3 independent web sources → data/hd_gate_wheel.json:
41,19,13,49,30,55,37,63,22,36,25,17,21,51,42,3,    (Quarter of Initiation · 302°–032° · Aquarius 2° → Taurus 2°)
27,24,2,23,8,20,16,35,45,12,15,52,39,53,62,56,     (Quarter of Civilization · 032°–122° · Taurus 2° → Leo 2°)
31,33,7,4,29,59,40,64,47,6,46,18,48,57,32,50,      (Quarter of Mutation · 122°–212° · Leo 2° → Scorpio 2°)
28,44,1,43,14,34,9,5,26,11,10,58,38,54,61,60       (Quarter of Duality · 212°–302° · Scorpio 2° → Aquarius 2°)
```
[VERIFIED 2026-08-23: full 64-order pinned (Gate 33 restored at index 33, Leo 7°37′30″–13°15′). Order prefix + degree math confirmed by gethumandesign.com & satyori.com; Gate 33 start-degree 7°37′ Leo confirmed by thehumandesign.com; neighborhood 56→31→33→7→4 confirmed by two independent Sun-transit logs (jamielpalmer.com 2022, yvettemayer.com 2024). Minor prose discrepancy on gethumandesign.com ("Gate 41 at end of Capricorn") recorded as [CONFLICT-NOTE] in the JSON; 302° anchor retained per satyori + Rave New Year ~Jan 22.]

```python
def lon_to_gate_line(lon):          # lon in degrees 0-360 tropical
    offset = (lon - 302.0) % 360     # 2° Aquarius = 302°
    gate_idx = int(offset // 5.625)
    line      = int((offset % 5.625) // 0.9375) + 1
    return GATE_ORDER[gate_idx], line
```

## 2 · Worked test case (Personality side)
| Planet | Lon | Gate calc | Result |
|---|---|---|---|
| Sun | 58.05° | offset=(58.05−302)%360=116.05 → idx=20 → GATE_ORDER[20] | **Gate 24, line 4** |
| Moon | 197.37° | offset=255.37 → idx=45 | **Gate 12, line 4** |
| Venus | 70.15° | idx=23 | **Gate 2, line 3** |
| Mars | 199.32° | idx=46 | **Gate 15, line 1** |
| Jupiter | 321.21° | offset=79.21 → idx=14 | **Gate 42, line 3** |
| Saturn | 16.08° | idx=7 | **Gate 63, line 4** |

*(Sun at Taurus 28.05 = late gate zone — boundary math re-checked 2026-08-23 against the verified wheel: Sun lands **Gate 8.4**, not 24.4.)*

**RE-RUN vs verified wheel (2026-08-23): the claimed outputs above do NOT reproduce (0/6) — the printed gate values were wrong independently of the old missing-Gate-33 table defect.** Machine-computed authoritative values from `data/hd_gate_wheel.json`: Sun 58.05°→**Gate 8.4** · Moon 197.37°→**57.3** · Venus 70.15°→**16.5** · Mars 199.32°→**57.5** · Jupiter 321.21°→**49.3** (offset typo confirmed: 19.21, not 79.21) · Saturn 16.08°→**51.2**. Sanity anchor: Gate 8 spans 54.5°–60.125° (Taurus 24.5°–Gemini 0.1°) ⇒ Sun transits Gate 8 ≈ May 15–20, consistent with published gate-date calendars. §2 table to be regenerated from ephemeris + this wheel at build.

## 3 · Design date & remaining pipeline
- Design moment: Sun 88° before 58.05° = 330.05° (Pisces 0.05) → ~**19 Feb 1997 ±1 day** [RUNTIME: solve exact timestamp via ephemeris iteration].
- At runtime: compute all 13 points (Sun Earth Moon N&S Nodes + Mercury→Pluto) × {Personality, Design} → 26 activations.
- **Centers defined** by completing channels (36 channel pairs list [VERIFY against standard table]) → **Type decision tree:** Sacral defined? → Generator (motor+throat manifesting? → Mg) ; no Sacral but motor-to-Throat → Manifestor ; nothing to throat but ≥1 center → Projector ; zero defined → Reflector.
- **Authority order:** Solar Plexus > Sacral > Spleen > Ego > G > Mental-projected.
- Profile = P-Sun line / D-Sun line.

## 4 · Output templates
- TH: *"Type: [X] — กลยุทธ์: [strategy] · Authority: [Y] — ตัดสินใจด้วย[how] · Profile [a/b]: [theme]"*
- EN mirror. Confidence: gate mapping **HIGH** (wheel source-pinned 2026-08-23 → `data/hd_gate_wheel.json`; residual risk now sits in ephemeris/design-moment precision), Type/Authority HIGH once centers computed from verified channels.

## 5 · Implementation notes
- `gates.json` (order+boundaries), `channels.json` (36 pairs→centers), `centers.json` (9 centers).
- Free libs: search github `human-design` js/python packages [VERIFY existence]; fallback = implement from tables above.
- Verify final chart against humdes.com / geneticmatrix.com for the test case before shipping (expected published values [RUNTIME-CHECK]).

---

## Implementation Notes (QA 2026-08-23)

### Explicit scope statement (ATLAS QA)
- **Minimal REAL scope:** Profile lines (`P-Sun line / D-Sun line`) are computable **only** with (1) a verified 64-gate wheel table AND (2) ephemeris access to solve the Design moment (Sun −88° solar arc). Status: **NEEDS-DATA** — see blockers below.
- **Fallback verdict:** deriving `Type` via simple center approximation (guessing defined centers from planet/sign heuristics instead of full 26-activation → channel → center completion) is **NOT reliable** — one mis-mapped gate breaks channel completion and flips Type. ⇒ Engine must **return `unavailable`**, not an approximation.
- Full pipeline (26 activations → 36 channels → 9 centers → Type/Authority/Profile) remains the target once the data lands.

### Ground truth (computable now, machine-checked)
- Formula boundary math itself is sound: lon = 302.00° → slot 0 / Gate 41 / line 1 ✓; wrap just below 302° lands on the last slot ✓; lines tile each 5.625° gate into 6 × 0.9375° ✓.
- ~~**BLOCKER — §1 wheel table is defective:** the four rows flatten to **63 entries, not 64 — Gate 33 appears nowhere** (no duplicates).~~ **RESOLVED 2026-08-23:** verified 64-gate Rave Mandala order (Gate 33 restored at index 33, Leo 7°37′30″–13°15′) delivered to `data/hd_gate_wheel.json` with 5 source URLs; spec §1 table corrected in place.
- ~~**§2 worked example is irreproducible from §1's table: 0/6 planets match** under the printed formula — Sun idx20 → table gives **8.4** (claims 24.4) · Moon idx45 → **32.3** (12.4) · Venus idx22 → **16.5** (2) · Mars idx45 → **32.5** (15) · Saturn idx13 → **51.2** (63). Jupiter "matches" only through an offset typo (spec prints 79.21 where 321.21−302 = **19.21**).~~ **RESOLVED 2026-08-23:** with the VERIFIED wheel the claimed outputs still fail 0/6 (see corrected values under §2) — the section-2 output values themselves were wrong, not just the table. §1 is now source-pinned and trustworthy for gate/line lookup; remaining pre-ship check unchanged: verify a full chart against humdes.com / geneticmatrix once ephemeris lands.
- Design-moment estimate consistent: 88° ÷ mean solar motion (≈0.9856°/d) ≈ **89.3 days** back from 1997-05-19 → **~Feb 18–19 1997** ✓ (spec's ±1 d is honest); exact timestamp still needs ephemeris iteration since daily solar speed varies ≈0.953–1.019°/d.

### Degradation rule
- Wheel unverified OR ephemeris unavailable ⇒ whole-chart call returns `{status: unavailable, reason}` — no partial gate output, no Type guess.
- After the wheel pin: emit Type/Authority/Profile **only** from the complete 26-activation computation; if any activation can't be computed, degrade to `unavailable` for Type/Authority/Profile (a single missing activation can break channels) while reporting the activations that did compute.
- Profile output additionally requires BOTH Sun gate-lines (Personality + Design) — if either is missing ⇒ Profile `unavailable`, never round to a neighboring line.
