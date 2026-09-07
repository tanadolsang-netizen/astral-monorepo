# 16 · VARSHAPHAL / TAJIKA ENGINE SPEC — Vedic Solar Return (annual forecast)
> **EN:** Tajika-Varshaphal = yearly chart cast at the exact moment the transiting Sun returns to its natal sidereal position. Deterministic; complements Western solar return (already in repo `returns_service.py`).
> **TH:** วรรษผล = ดวงปีจากจังหวะที่ดวงอาทิตย์โคจรกลับมาตำแหน่งสายพระเวทเดิม — deterministic · เสริมชั้น annual forecast ของแอพ

---

## 1 · Casting algorithm
```python
# 1) find t where sidereal Sun(t) == natal sidereal Sun lon (Lahiri), between birthday Y and Y+1
#    solve by Newton iteration on swe.calc_ut(SUN); precision ±1 min
# 2) cast full chart at that UTC instant, birth location (or current residence — engine setting)
# 3) Tajika aspects: only conjunction/opposition/trine/square/sextile with ORB in MINUTES of arc:
#    conjunction 60'? no — Tajika orbs: application/separation measured in degrees: conj 12°? 
#    standard: Drishti values — conj/opp 100%, trine 75%? [PIN at build from Tajika texts: Keshava Iyer]
```
**Year lord (Varshesha) selection — the core deterministic rule:** candidate planets = lagna lord, Moon-sign lord, year-natal 10th-lord… simplified v1 rule (Muntha-based): compute **Muntha** (progressed ascendant: advance natal ASC by (age mod 360)? correct formula: Muntha = natal ASC − (age × 30°)) then Year Lord = strongest planet by Pancha-Vargiya Bala among {lagna lord, Muntha lord, 10th lord}. Ship full strength routine or lookup via library.

## 2 · Sahamas (Tajika lots) — key set with formulas
| Saham | Formula (day birth) | Meaning |
|---|---|---|
| Punya (fortune) | Lagna + Jupiter − Sun | overall year fortune |
| Raja (authority) | Saturn + Sun − Jupiter? [verify] | position/power |
| Putra (children) | Jupiter + Moon − ... [verify per text] | children |
| Vivaha (marriage) | Lagna + Venus − Moon? [verify male/female swap] | marriage events |
*(pin exact classical formulas from Neelakantha's TajikNeelkanthi at build — same pattern as Arabic Lots spec 09)*

## 3 · Interpretation pipeline (encodeable order)
1. Varsha lagna + its lord condition → year's body/theme
2. Year Lord strength & house → dominant flavor
3. Muntha sign/house + planets there → where luck accumulates this year
4. Sahams activated by conjunction ≤1° → event areas
5. Mudda dasha (annual Vimshottari variant, proportional) → month-level timing within the year
6. Cross-fuse: Varshaphal themes must not contradict master fusion rules §4 — transit windows remain the clock.

## 4 · Test case (owner, year 2026–2027)
Natal sidereal Sun = Taurus 4.37° → Solar-return-2026 instant ≈ **14 May 2026** [RUNTIME solve exact HH:MM]; 2027 return ≈ 14 May 2027 (3 days before Saturn Return peak 26 Mar→no—Mar is earlier; note ordering: SR-2027 lands AFTER Saturn Return peak). Engine prints both charts' lagna/Muntha/Year-Lord once runtime solver exists; regression test asserts return-date drift <1 day/year.

## 5 · Output templates
TH: *"วรรษผล 2569–70: ลัคนาปี = [sign], มุณฐะ = [house] — [theme]. ปีเจ้าชู้(Year Lord)=[planet]: [flavor]. เดือนที่[m]: [Mudda line]"*
EN mirror. Confidence: HIGH for casting, MED for interpretation layer.

## Implementation Notes (QA 2026-08-23)
**(a) Solar Return search window:** transit Sun returns to natal Sun longitude within [birthday-1d, birthday+1d] of target year; solve by bisection on solar longitude diff (precision <=0.01°). Muntha: SR ascendant advanced by (age mod 12) houses from SR Lagna. Year lord: planet with highest pancha-paksha dignity among SR lagna lord / Muntha lord / 7th lord candidates per Tajika rules in this spec.
**(b) Ground truth (M):** SR 2026 window ≈ 2026-05-18..20 (Sun returns to natal Taurus 4.4° sidereal ≈ 34.2° abs). Verify varshaphal.years[2026].sr_jd exists in live output.
**(c) Degradation:** ephemeris unavailable → {'status':'unavailable','reason':...}.
