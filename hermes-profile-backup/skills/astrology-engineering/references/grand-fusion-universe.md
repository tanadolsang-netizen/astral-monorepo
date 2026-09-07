# Grand Fusion "Universe" — engine architecture + verified data sources

State as of 2026-08-23. Repo: C:/AI/NEW-AI-REBORN (commit 0de9fe1+). 187 tests passed, 1 skipped. 32 endpoints.

## Architecture (4 layers)
1. PROFILE — fusion_profile.py store (PUT /v1/fusion/profile/{name}); reading by name via /v1/fusion/today/by-name/{name}; optional {"on":"YYYY-MM-DD"} body pins the date (injectable clock — never derive from datetime.now() in tests). Rectification service infers birth time from life events when time unknown.
2. CORE COMPUTE — chart_service (skyfield+DE421), per-science modules in src/services/grand/ (fixed_stars, varshaphal, ziwei, asteroids, numerology, iching, ninestar_ki, mayan_tzolkin, cosmobiology, human_design, kalachakra) + synastry_scoring + window_service.
3. FUSION LAYER — precedence: exact-transit > varshaphal > dasha > progression > BaZi tone > numerology tone > other tones. Conflicts are NEVER averaged; they go to a `tensions[]` array verbatim.
4. OUTPUT — one JSON: person/snapshot/core{}/extended{}/synthesis(1 paragraph TH)/tensions/key_dates/confidence.

## Standing rules
- Graceful degradation is first-class: any module without data returns {'status':'unavailable','reason':...} — never raises, never fakes. "ตอบว่าไม่มีข้อมูล ดีกว่าตอบผิดด้วยความมั่นใจ".
- QA notes in specs OVERRIDE printed spec text where flagged ([VERIFY]/[CONFLICT]/NEEDS-DATA). Specs live in C:/AI/research-astrology/, notes appended as '## Implementation Notes (QA 2026-08-23)'.
- Verified data files land in C:/AI/research-astrology/data/ with source URL for every constant; conflicts recorded both sides as [CONFLICT].

## Module status (post phase-4, live-verified)
REAL: fixed_stars (Royal Stars J2000 + Sabian), varshaphal (SR window ±1d birthday, Muntha), ziwei (Life/Body Palace via lunar-python; M = 壬寅/戊申 ✓ BaZi 丁丑 cross-check), numerology (Life Path M=5), iching (seeded cast vector 'M|1997-05-19||hermes-v1' → #11 Peace, nuclear #54), ninestar_ki (M=Star 3 Blue Wood; [VERIFY] constant dispute carried in output), mayan_tzolkin (Kin 239 Blue Storm Tone 5), cosmobiology (66 midpoint pairs; Sun/Moon mid sidereal = Cancer 13.85°).
GRACEFUL-UNAVAILABLE (correct behavior): asteroids (needs Swiss ephe files — de421 has no Chiron/asteroids; pyswisseph installed but ephe data missing), human_design Type/Authority (needs verified gate→center + 36-channel table), kalachakra year constants (spec self-contradicts).

## Three defect case studies (ATLAS research, commit d9c3a96) — the pattern for "verify before implement"
1. HD wheel had only 63 entries — Gate 33 missing entirely; worked examples reproduced 0/6 even after fixing the table (examples were fabricated independently). Fix: verified Rave Mandala order from 5 independent sources into data/hd_gate_wheel.json; replaced spec's example values with machine-computed ones. Lesson: example values in a spec can be wrong independently of its formula — recompute them, don't trust them.
2. Kalachakra epoch phase: spec text said Fire-Ox-female for 1997, its own pseudocode gave Wood-Ox-male. Root cause: Rabjung cycle 1 = 1027 CE = Fire-female-Hare (NOT Chinese Wood-Male-Tiger start); correct anchor i=(Y−4)%60 validated on 9 published anchors; 1997 post-Losar(8 Feb) = Fire-Ox female ✓ matches BaZi 丁丑. Lesson: adjacent systems legitimately differ because year-start shifts (Losar vs Lichun vs Jan 1) — document which applies when instead of picking a side.
3. Mayan Dreamspell off-by-33: naive (days_since_epoch mod 260) ignores that the epoch day itself is Kin 34. Correct: kin=((33+delta) mod 260)+1 → M = Kin 239 Blue Storm Tone 5 (matches zodiacroots.com). Lesson: always cross-check one date against an external published calculator and keep it as a permanent test vector (data/dreamspell_testvectors.json).
Meta-rule from all three: "ดีกว่าบอกว่ายังไม่มีข้อมูล กว่าตอบผิดด้วยความมั่นใจ" — unavailable beats confidently-wrong.

## Verification stack (how we KNOW numbers are right)
Three independent engines must agree: Skyfield+DE421 (NASA/JPL), Swiss Ephemeris Moshier (vedic_deep/vedic_verify.py — industry standard), lunar-python + JDN arithmetic (BaZi day=(JDN+49)%60). Plus two-system regression: vault scan script vs API windows must agree aspect-for-aspect (W35/W36 did, incl. Venus☌natal-Moon 0.20° on 2026-08-26). Accuracy boundary stated honestly to users: ephemeris ±0.01° is physics; interpretation rules are tradition; house-system choice is philosophy not correctness.

## Known remaining gaps
- asteroids real compute needs Swiss ephe files (seas_18.se1 etc.) downloaded into an ephe/ dir + swe.set_ephe_path(); ATLAS researching exact files/body constants (Chiron=15? asteroid bodies via SE_AST_OFFSET 10000+n?).
- HD Type/Authority needs verified gate→9-centers map + 36 channel pairs; Profile lines (P-Sun/D-Sun gate.line) unlock first once hd_gate_wheel.json is wired (design moment = Sun −88° solar arc ≈89.3d back, iterate ephemeris).
- CI workflow (.github/workflows/ci.yml) written but push blocked: GitHub OAuth token lacks `workflow` scope — user must run `gh auth refresh -h github.com -s workflow` interactively, then plain git push works.
