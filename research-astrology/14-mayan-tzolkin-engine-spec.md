# 14 · MAYAN DREAMSPELL / TZOLKIN ENGINE SPEC
> **EN:** v1 = Dreamspell (Argüelles) for clean integer math; classical Tzolkin (GMT 584283 correlation) documented as alt mode. Test case machine-computed AND verified against published tables.
> **TH:** v1 ใช้ Dreamspell — คณิตเป็นเลขจำนวนเต็มล้วน · test case คำนวณและ cross-check กับตารางเผยแพร่แล้ว

---

## 1 · Core arithmetic (verified)
```python
def jdn(y,m,d):
    a=(14-m)//12; y2=y+4800-a; m2=m+12*a-3
    return d+(153*m2+2)//5+365*y2+y2//4-y2//100+y2//400-32045

ANCHOR_JDN = jdn(1987,7,26)   # Dreamspell epoch NS1.0.1.1 = Kin 34 White Galactic Wizard (source-pinned 2026-08-23)
def kin(y,m,d):
    delta = jdn(y,m,d) - ANCHOR_JDN
    delta -= n_feb29_between(date(1987,7,26), date(y,m,d))  # authentic Dreamspell: 29 Feb = 0.0 Hunab Ku, bears NO kin
    return ((34 - 1 + delta) % 260) + 1
seal = ((kin-1) % 20) + 1     # 20 solar seals
tone = ((kin-1) % 13) + 1     # 13 galactic tones
```
**Test case 19 May 1997 (REVISED 2026-08-23):** JDN 2450588 · Δ3585 raw days − **3 skipped Feb-29s** (1988/1992/1996) = Δ3582 counted → **Kin 236 → Seal 16 YELLOW WARRIOR · Tone 2 LUNAR** under the authentic Law-of-Time rule.
⚠️ **[CONFLICT documented 2026-08-23]** naive continuous-count calculators — including zodiacroots.com, the original cross-check — print **Kin 239 Blue Overtone Storm** for this date because they let Feb 29 carry a kin. The authentic rule is confirmed by: lawoftime.org official calendar (26 Jul 2019 = Kin 14 White Magnetic Wizard; naive says 22), tortuga1320.com (epoch 26 Jul 1987 = NS1.0.1.1 Kin 34; "Blue Lunar Storm Year" from 26 Jul 2020 = Kin 119; naive says 128; DOOT 25 Jul 2032 = Kin 78) and Wikipedia/Dreamspell ("February 29 will always be 0.0 Hunab Ku… Nor is it one of the 260 galactic signatures"). Dual-convention test vectors → `data/dreamspell_testvectors.json`.
Classical-Tzolkin alt mode: `kin_gmt = ((jdn − 584283_corr) mod 260)` — constant pinned at build [VERIFY against mayan-calendar converters; Dreamspell ≠ classical count by design].

## 2 · Meaning data (fully written entries)
**Seals (20-order):** 1 Red Dragon(nurture/being) · 2 White Wind(spirit/breath-communication) · 3 Blue Night(abundance/dreaming) · 4 Yellow Seed(flowering/targets) · 5 Red Serpent(life-force/survival instinct) · 6 White World-Bridger(death/equality-opportunity) · 7 Blue Hand(accomplishment/healing-touch) · 8 Yellow Star(elegance/art-harmony) · 9 Red Moon(purify/universal water-flow) · 10 White Dog(love-heart-loyalty) · 11 Blue Monkey(magic/play-spontaneity) · 12 Yellow Human(free will/wisdom-influences) · 13 Red Skywalker(space/explorer-wakefulness) · 14 White Wizard(timelessness/receptivity-mage) · 15 Blue Eagle(vision/mind-planets) · 16 Yellow Warrior(intelligence-questioning-fearlessness) · 17 Red Earth(navigation/synchronicity) · 18 White Mirror(endless-ness/reflection-order) · **19 Blue Storm(self-generation/catalysis-transform)** · 20 Yellow Sun(enlighten/universal-fire-life)

**TH (test case):** *"Kin 239 — พายุสีน้ำเงินโอเวอร์โทน: การเปลี่ยนผ่านที่มีพลัง — เปล่งอำนาจภายใน ความมั่นใจ และคำสั่งจากด้านใน · ธาตุ: การเร่งปฏิกิริยา/สร้างพลังใหม่จากตัวเอง"*
**EN:** "Kin 239 — Blue Overtone Storm: empowered transformation; radiating authority, confidence, inner command."

**Tones (all 13):** 1 Magnetic(purpose-unify) · 2 Lunar(challenge-polarize) · 3 Electric(service-bond) · 4 Self-Existing(define-form) · **5 Overtone(empower-radiate)** · 6 Rhythmic(balance-organize) · 7 Resonant(attune-channel) · 8 Galactic(integrity-harmonize) · 9 Solar(pulse-realize-intention) · 10 Spectral(liberate-dissolve) · 11 Planetary(manifest-perfect) · 12 Crystal(dedicate-gather) · 13 Cosmic(endure-transcend-presence)

## 3 · Compatibility quick-rule
Same seal = mirror kin (+8 resonance, risk: echo-chamber) · Same color family (Red initates/White refines/Blue transforms/Yellow ripens) = complementary rhythm (+5) · Tone sum 13 = "companion tones" (+4). Cross-ref spec 03 output contract.

## 4 · Output templates
- TH: *"ลายเซ็นกาแล็กซีของคุณ: Kin 239 พายุน้ำเงินเสียงที่ 5 — [meaning_th] · วันนี้ Kin [n]: [daily seal/tone line]"*
- EN: *"Your galactic signature: Kin 239, Blue Overtone Storm — [meaning_en] · Today's Kin [n]: [line]"*
Implementation: pure integers; ship `seals[20]`, `tones[13]` JSON; daily-Kin generator reuses `kin(today)`.

## Implementation Notes (QA 2026-08-23)
**(a) Formula/constants:** Dreamspell v1 arithmetic re-verified: `ANCHOR_JDN = jdn(1987,7,26) = 2447003` (epoch day = **Kin 34**); `kin(y,m,d) = ((33 + delta) mod 260) + 1` with `delta = JDN(date) − ANCHOR_JDN`. `seal = ((kin−1) mod 20) + 1`; `tone = ((kin−1) mod 13) + 1`. Local calendar date governs (time-of-day ignored). Classical-GMT alt-mode correlation still [VERIFY] at build.
**(b) Ground truth (M, DOB 1997-05-19) — REVISED 2026-08-23:** the naive `delta mod 260` = 205 bug stands fixed by the Kin-34 epoch offset (+33). Research then exposed a SECOND defect class in that fix as originally framed: an offset-corrected raw-day count still over-counts by one per elapsed Feb 29, because authentic Dreamspell assigns Feb 29 no kin ("0.0 Hunab Ku"). Canonical authentic result: **Kin 236 · Seal 16 YELLOW WARRIOR · Tone 2 LUNAR**; the previously cross-checked **Kin 239 Blue Overtone Storm** reproduces only under the naive continuous-count convention used by zodiacroots-style web calculators (`second_source_confirmed: false` for 239). [CONFLICT] fully documented with sources and dual-convention vectors in `data/dreamspell_testvectors.json`. Engine must pick one explicitly — recommended canonical: authentic skip-leap rule; expose naive mode behind a flag only if web-calculator parity is a product requirement.
**(c) Degradation:** invalid/out-of-range dates → `{'status':'unavailable','reason':'invalid_birth_date'}`; missing seals/tones JSON entry → `{'status':'unavailable','reason':'seal_or_tone_data_missing'}`; classical mode requested before its constant is pinned → `{'status':'unavailable','reason':'correlation_constant_unpinned'}`.
