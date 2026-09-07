# 18 · TIBETAN / KALACHAKRA ENGINE SPEC — Element & Animal Days
> **EN:** v1 scope: the practical Tibetan calendrical layer (element-animal years, daily element/animal, Parkha = Tibetan I-Ching, Mewa = 9 magic-square colors — shares Lo Shu with NSK spec 13). Deterministic; sources pinned at build.
> **TH:** ชั้นปฏิทินทิเบต: ปีธาตุ+สัตว์ · วันธาตุ/สัตว์ · ปาร์ข่า (อี้จิงทิเบต) · เมวา (9 สี แชร์ Lo Shu กับ NSK)

---

## 1 · Year system
Tibetan years = 60-cycle (Rabjung): element (Wood/Fire/Earth/Iron/Water) × animal (12) × gender. Epoch: first Rabjung starts 1027 CE.
```python
def tibetan_year(y):
    i = (y - 4) % 60                    # 0 = Wood-Male-Mouse (Jia-Zi-equivalent phase)
    element = ["Wood","Fire","Earth","Iron","Water"][i // 2 % 5]
    animal  = ["Mouse","Ox","Tiger","Hare","Dragon","Snake",
               "Horse","Sheep","Monkey","Bird","Dog","Pig"][i % 12]
    gender  = "male" if i % 2 == 0 else "female"
    rabjung_cycle = (y - 1027)//60 + 1  # year 1 of every Rabjung = Fire-Female-Hare (1027 CE)
    year_in_cycle = ((y - 1027) % 60) + 1
    return element, animal, gender, rabjung_cycle, year_in_cycle
```
1997 → i=(1993)%60=13 → Fire · Ox · female → **Fire Ox (female), Rabjung cycle 17 / year 11** — consistent with Chinese Ding-Chou ✓ [VERIFIED 2026-08-23 → data/kalachakra_anchor.json]. ⚠️ The OLD printed code (`idx=(y−1027)%60`, Hare-start arrays → Wood-Ox male) had the wrong epoch PHASE: Rabjung year 1 = 1027 CE = **Fire-Female-Hare**, NOT Wood-Male-Tiger (the latter is the Chinese mekhor start). Do not reimplement the old phase.

## 2 · Daily element/animal
Tibetan almanac day = element+animal pair cycling; day starts at DAWN (5 a.m. local rule) not midnight [VERIFY]. Constants pinned from Tibetan almanac converter at build; then pure integer math like NSK.

## 3 · Mewa (nine mewa colors) — reuse NSK Lo Shu machinery
Birth mewa from year (same 9-cycle as Nine Star Ki but Tibetan color names: White, Black, Blue, Green, Yellow, White, Red, White, Red order differs [VERIFY table]) → personality + annual mewa movement = identical rotation logic as spec 13 — **engine shares one implementation, two label sets.**

## 4 · Parkha (8 parkha = bagua) — daily parkha from day-number mod 8; meaning matrix TH/EN (8 entries: Li/Sun/Kham/Kon/Chin/Tsi/Khun/Da — Tibetan names) [BUILD: pin from Tibetan astrology primer].

## 5 · Auspicious-day rules worth encoding (practical layer)
- Soe-nam (merit) days: 8th/10th/15th/25th/30th of lunar month → +practice bonus in app's spiritual domain
- Dharmapala days (29th) → clearing/letting-go actions
- Eclipse days → strong for mantra/practice (fuse with eclipse table spec 01)
[Pin exact lists from Kalachakra almanac at build.]

## 6 · Test case & templates
19 May 1997 → Tibetan year **Fire Ox female** (Rabjung cycle 17 / year 11; Losar 1997-02-08 Phugpa, so the label applies cleanly; aligns BaZi Ding-Chou ✓) · daily pair/mewa/parkha [BUILD after constants].
TH: *"ปีทิเบต: [element][animal] · วันนี้ [element/animal day] — [quality] · เมวา [n] [color]"* · EN mirror.

---

## Implementation Notes (QA 2026-08-23)

### Defined by this spec vs external data needed (ATLAS QA)
- **Defined here (structure, pure integer math once constants land):** 60-cycle Rabjung year = element×animal×gender, epoch 1027 CE; daily element/animal pair concept (day starts at dawn, 05:00 local rule); Mewa = reuse of spec 13 Lo Shu machinery with Tibetan color labels; Parkha = day-number mod 8 over 8 Tibetan bagua names; auspicious-day layers (Soe-nam 8/10/15/25/30 lunar · Dharmapala 29th · eclipse days fused with spec 01).
- **External data needed (every item still carries [VERIFY]/[BUILD]):**
  1. ~~Verified year-formula anchor~~ **DONE 2026-08-23** → `data/kalachakra_anchor.json` (epoch 1027 = Fire-female-Hare; formula validated against 9 published year anchors incl. Janson Table 1 and Tibetan Nuns Project calendars);
  2. Losar (Tibetan New Year) dates or a rule, to map Gregorian dates → Tibetan years;
  3. Tibetan almanac converter constants for the daily element/animal seed (+ confirm the dawn start);
  4. Verified Mewa birth-year color table (spec flags its own order as unverified);
  5. Parkha name/meaning matrix (Li/Sun/Kham/Kon/Chin/Tsi/Khun/Da);
  6. Exact merit/dharmapala lunar-day lists from a Kalachakra almanac.

### Ground truth (computable now, machine-checked)
- ~~**Internal contradiction:** running the spec's own `tibetan_year()` verbatim, 1997 → idx = 970%60 = **10** → element[10%5]=**Wood**, animal[10%12]=**Ox**, parity → **male** — but the text (and §6) claims **Fire Ox female**.~~ **RESOLVED 2026-08-23 (research-pinned):** the text target **Fire-Ox female** is CORRECT (Janson arXiv:1401.6285 Table 1: Losar 8 Feb 1997 opens Fire-Ox; = BaZi Ding-Chou ✓; M born after Losar so it applies cleanly). Root cause was an epoch-PHASE error: Rabjung year 1 = 1027 CE = **Fire-Female-Hare**, not Wood-Male-Tiger (that is the Chinese mekhor start). Corrected formula shipped in §1 + `data/kalachakra_anchor.json` (validates 1027/1935/1987/1991/1997/2008/2021/2026 against published tables). Do NOT implement either the old pseudocode or the "(Y−1026) mod 60 + Wood-Male-Tiger-start" variant — both give Wood-Ox male for 1997.
- Structural sanity OK: cycle length 60 = 5 elements × 12 animals; animal list starts Hare; gender alternates yearly — only the PHASE is broken, not the shape.
- Test case M (1997-05-19): born after Losar 1997-02-08 (Phugpa), so the year label applies cleanly — **Fire Ox (female)** CONFIRMED by source pin 2026-08-23 (`data/kalachakra_anchor.json`).

### Degradation rule
- Year lookup for Jan–mid-Feb dates (before Losar) WITHOUT a Losar table ⇒ return `{year: approximate|unavailable, reason}` — never silently assign the prior/new Tibetan year.
- Daily pair / Mewa / Parkha ⇒ `unavailable` until their constants are pinned — no ad-hoc seeding and no borrowing Chinese BaZi values for the Tibetan layer.
- Auspicious-days module degrades to the eclipse-day subset (via spec 01 fusion) when the lunar-day lists are unpinned; Soe-nam/Dharmapala stay hidden, not guessed.
