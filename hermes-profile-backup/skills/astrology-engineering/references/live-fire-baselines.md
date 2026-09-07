# Live-fire baselines (verified 2026-08-22, port 8001)

Expected outputs when gate-testing NEW-AI-REBORN endpoints with real birth data. Diff API responses against these; any drift = regression or ephemeris bug.

## POST /v1/bazi/pillars — Owner (1997-05-19, 05:45, tz+7)
```
pillars: year 丁丑 · month 乙巳 · day 辛酉 · hour 辛卯
jdn: 2450588
day_master: stem 辛, metal yin, label_th "โลหะหยิน"
```
Cross-tool: `lunar_python.Solar.fromYmdHms(1997,5,19,5,45,0).getLunar().getEightChar()` gives identical pillars.

## POST /v1/synastry/score — M × Mai (tropical, real coords)
Request: a = 1997-05-19 05:45 lat 13.36 lon 100.98 · b = 2001-08-18 22:32 lat 13.86 lon 100.52, tz+7.
```
top bond:      M Mars sextile Mai Venus   orb ≈ 0.59°   (spec 03 says .58)
stability glue: M Venus conj Mai Saturn    orb ≈ 3.44°
karmic method: dk_cross_check             (no nodal contact ≤5° — correct)
house_overlay: mutual_7th_asc = false     (correct AFTER Taurus-ASC fix; any "true" = stale Scorpio-ASC logic)
top friction:  M ASC square Mai Sun       orb ≈ 0.22°
dims snapshot (weights v spec03-section2+mercury-ext): chem 26 · bond 22 · stab 31 · comm 18 · growth 48 · karmic 60 · overall 34
```
Dims may shift when weights change — treat bonds/frictions/karmic/overlay rows as the stable contract.

## GET /v1/fusion/full/{name} — NEW ENDPOINT (2026-08-22)
Request: `GET /v1/fusion/full/M?lang=th&partner=mai`
```
person:
  today: {layers: {western_transits: 10 hits, vedic: {vimshottari: {mahadasha: Jupiter, antardasha: Saturn (ends ~2026-11-10)}, moon_today: {nakshatra: Mula}}, thai_bazi: {day: {weekday_th: "เสาร์", ruling_planet: "Saturn", lucky_number: 9}}}, verdicts: {career: 60, love: 56, money: 55, health: 65, growth: 56}, reading: {synthesis: "เสาร์: ...", domains: [...], language: "th"}}
  profile: {name: "M", natal: {...sidereal_bodies...}}
compatibility:
  dimensions: {chemistry: 26, emotional_bond: 40, stability: 47, communication: 26, growth: 63, karmic_pull: 60}
  overall: 44
  top_bonds: 3 (M Mars sextile Mai Venus 0.59°, M Moon sextile Mai Moon 1.58°, M Jupiter sextile Mai Mars 0.47°)
  frictions: 3 (M ASC square Mai Sun 0.22°, M Venus square Mai Mercury 2.0°, M Jupiter opp Mai Moon 2.26°)
  karmic: dk_cross_check
upcoming:
  best_days: 3 slots (top: 2026-08-27 06:00 score 1.62 favourable)
  shared_best: null
```
Note: `emotional_bond` dim now 40 (was 22) — identity-resonance fix adds points for Moon-Moon sextile.

## Known engine gap (FIXED 2026-08-22)
`test_identical_charts_score_higher_emotional_bond_than_opposite` now PASSES. The fix was adding `identity-resonance` kind in `_classify()` for same-planet conjunctions.