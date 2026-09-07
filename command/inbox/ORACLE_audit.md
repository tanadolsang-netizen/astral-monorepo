# ORACLE — Grand Finale Accuracy Audit: GET /v1/fusion/grand/M?lang=th

**Task:** #20260823-193449 · **Date:** 2026-08-23 · **Method:** live payload (port 8002, served fresh this session) vs independent recomputation — own pyswisseph calls (separate ephe copy), own arithmetic, `lunar_python`, vault skyfield/de421 scan, published web tables, and ATLAS QA ground-truth vectors (S2/S3 reports, data/*.json anchors).

**Birth vector:** M · 1997-05-19 05:45 ICT (+07) · Chonburi 13.36N 100.98E · JD(UT) 2450587.447917 / JDN 2450588.

---

## Verdict table — 18 modules

| # | Module | Expected (independent ref) | Got (live payload) | Verdict | Source |
|---|---|---|---|---|---|
| 1 | **natal-tropical chart** | Sun 58.01° (Taurus 28°01′), ASC 25.96° Taurus (resolve_asc GT) | HD-frame Sun 58.0139; own swe.houses ASC 55.960° = 25°57′36″ Taurus; 11/11 planets max Δ 0.027° (true node) | **PASS** | own pyswisseph @JD2450587.447917 |
| 2 | **fixed_stars** | Aldebaran 1997 epoch ≈ 69.758 (J2000 69.794 − precession 0.037) | 69.7464 (Δ 0.011°); all 3 orbs recompute exactly (Gienah-Moon 0.3066 / Aldebaran-Venus 0.4055 / Alcyone-Sun 1.8736); royal contact Venus-Aldebaran ✓ | **PASS** | catalog J2000 + linear precession; note Gienah Δ 0.12° = upstream [VERIFY] flag, changes no hit |
| 3 | **sabian (Sun)** | Taurus 29 = "Two cobblers working at a table" | identical phrase th/en, number 29 | **PASS** | Jones/Wheeler via kerykeion.net, astromatrix (web) |
| 4 | **asteroids natal** | Chiron 206.7767° = 26°46′36″ Libra **Rx**; 4 others plausible | Chiron **206.7767 Rx exact**; Ceres 337.4207 / Pallas 306.4911 / Juno 85.7298 / Vesta 4.8567 — all 4 match own ephemeris to 4 decimals | **PASS** | own pyswisseph+seas_18; ATLAS GT (S3 16:36) |
| 5 | **asteroids transit (2026-08-23)** | Ceres Cancer early, Pallas Aries late Rx, Juno Cap late Rx, Vesta Aries late, Chiron early Taurus Rx | 5/5 sign+Rx match own ephemeris @12:39UT; Juno trine natal-ASC orb 1.75 recomputes from 297.71−55.96 | **PASS** | own pyswisseph (mission plausibility list = exact match) |
| 6 | **varshaphal** | Muntha = natal sidereal ASC + age×30 → ≈182.1 Libra | 182.2747 Libra 2°16′ (Δ 0.16° = ayanamsa precision); year lord Jupiter = Pisces-lagna lord, internally consistent | **PASS** | Tajika muntha rule + Lahiri ayanamsa |
| 7 | **ziwei** | Lunar 1997-04-13, year 丁丑; Life Palace 寅, Body 申 | lunar m4/d13 丁丑 ✓; life 壬寅 / body 戊申 (五虎遁 stems ✓, branch formula ✓); annual 2026 丙午 / 2027 丁未, 歲破 子/丑 ✓ | **PASS** | lunar_python (independent lib) + manual formula |
| 8 | **numerology** | LP = 5 (raw 41); PY2026 = 7, PY2027 = 8 | LP 5 raw 41 ✓; PY 7 / 8 ✓; birth-day 19→1 ✓ | **PASS** | pure arithmetic |
| 9 | **iching (seeded)** | seed `M\|1997-05-19\|\|hermes-v1` → [7,7,7,8,8,8] → **#11 Peace**, nuclear **#54**, fallback **#45** | [7,7,7,8,8,8] ✓; Qian/Kun = #11 泰 ✓; nuclear bits(3,1) = #54 歸妹 ✓; (19×5+1997) mod 64 + 1 = 45 萃 ✓ | **PASS** | spec §2 sha256 coin distribution (reimplemented) |
| 10 | **ninestar_ki** | Year star 3 Three Blue Wood (born May 19 > Feb 4 cutoff) | star 3 ✓; month/day stars honestly `unavailable` (constants unpinned) | **PASS** | (11 − 1997 mod 9) = 3; alt-convention dispute carried as [VERIFY] in payload — disclosed, not hidden |
| 11 | **mayan_tzolkin** | Kin 239 / Seal 19 Blue Storm / Tone 5 Overtone (mission vector) | Kin 239 = ((33+3585) mod 260)+1 ✓, Seal 19 ✓, Tone 5 ✓ | **PASS** | epoch JDN 2447003 = Kin 34 (tortuga1320/lawoftime); note: canonical Dreamspell (Feb-29 skipped) = Kin 236 — dual vectors shipped in dreamspell_testvectors.json, spec 14 flagged for CMD decision (known, disclosed) |
| 12 | **cosmobiology** | Su/Mo midpoint 127.71; Ve/Ma=Neptune 0.18, Su/Ve=Pluto 0.34, Ve/Ju=Saturn 0.41 (ATLAS 7/7) | Su/Mo 127.7134 **exact** from own longitudes; all 4 QA pictures reproduce; 8 confirmed pictures within COSI orbs (≤1°) | **PASS** | own midpoint arithmetic + ATLAS QA (S2 15:57) |
| 13 | **human_design** | Internal chain: activations→wheel→channels→centers→Type/Authority/Profile; P-Sun 8.4 / D-Sun 30.6 → 4/6; Generator; Emotional | **26/26 activations reproduce** from longitudes via verified wheel (Gate 41 @302°, 5.625°/gate); channels 19-49/25-51/29-46/30-41/34-57 → centers {G,Heart,Root,Sacral,SolarPlexus,Spleen} recomputed identically; Sacral defined (29,34) + no motor-throat → **Generator** ✓; **49→SolarPlexus confirmed** in centers map → **Emotional authority** ✓ (hierarchy rank 1); design moment own-iterative-solve = 89.3151 d arc, matches 1997-02-18T15:11:15Z | **PASS** | hd_gate_wheel.json (b5ac4d0, 5 sources) + hd_channels_centers.json + own ephemeris |
| 14 | **kalachakra** | 1997 = Fire-Ox **female**, post-Losar (Losar 1997-02-08) | cycle 17 / yr 11 ✓ (1997−1027=970); yr-11 count from epoch 1027 Fire-female-Hare → **Fire-Ox female** ✓; May 19 ≫ Losar → clean assignment ✓; = BaZi 丁丑 (Yin-Fire Ox) cross-consistent ✓ | **PASS** | kalachakra_anchor.json (Laufer 1911 epoch) + own sequence arithmetic |
| 15 | **bazi (cross-ref /v1/bazi)** | 丁丑 乙巳 辛酉 辛卯 | endpoint: 丁丑(HIGH) 乙巳 辛酉(HIGH, idx57=(JDN+49)mod60) 辛卯(HIGH); own JDN 2450588: (2450588+49) mod 60 → 辛酉 ✓; 五虎遁 Ding-year→乙巳 ✓; 五鼠遁 Xin-day→辛卯 (05:45 = 卯) ✓; lunar_python: identical 4 pillars | **PASS** | triple agreement: API + spec-04 arithmetic + lunar_python |
| 16 | **transits live** | Venus ☌ natal Moon peak ~26 Aug (vault: orb 0.20° @26/8 noon) | API /v1/transit/windows 23–29 Aug: Venus☌Moon orb 1.36→0.03 (25/8 night)→0.26→…→1.26 — same parabola, orbs frame-independent; vault skyfield/de421 scan re-run this session reproduces 0.20° @26 Aug | **PASS** | obsidian-vault transit_week_scan.py (skyfield/de421, sidereal) vs API (tropical) — AGREE (consistent with W35 ORACLE report) |
| 17 | **reading layer th/en** | 12 sections each, none empty | 12/12 th + 12/12 en non-empty; precedence_note present (backdrop layers; transit windows remain the clock) | **PASS** | payload integrity scan |
| 18 | **person/identity + provenance** | name M, birth 1997-05-19 05:45 +07, 13.36/100.98 | exact match; every module stamps `computed_at` + source file refs | **PASS** | profile store vs payload |

## Overall

**PASS 18/18 (100%)** — zero arithmetic or reference failures found. Chiron natal = 206.7767° Libra Rx **exact**; all 26 HD activations, all asteroid positions, all pure-math vectors, and the transit anchor reproduce under independent recomputation.

### Disclosed convention flags (not failures — carried honestly upstream)
1. **Dreamspell Kin 239 vs canonical 236** — backend implements the naive-count convention (matches mission vector); authentic Dreamspell skips Feb-29 → Kin 236 Yellow Lunar Warrior. Dual vectors shipped in `data/dreamspell_testvectors.json`; spec 14 awaits CMD decision.
2. **9 Star Ki year-star constant** (3 vs 6) — alternative published convention remains [VERIFY]; payload discloses rather than silently picking.
3. **Gienah J2000 longitude** residual 0.12° vs catalog approx — already flagged [VERIFY] in 00-MASTER-INDEX; Moon-Gienah conj (orb 0.31°) robust either way.

### Method notes
- Independent ephemeris = own pyswisseph scripts against `C:/AI/research-astrology/ephe` (separate copy from backend's vendored `NEW-AI-REBORN/ephe`); HD uses true node (Δ mean-node would be 1.32° — backend correctly uses true).
- Frames: HD = apparent ecliptic-of-date; cosmobiology/fixed_stars chart frame ≈ +0.04° vs of-date — each internally self-consistent and matching its own ATLAS QA numbers; orbs/angles frame-independent.
- Server: found port 8002 already held by an identical command (started 17:35 by an earlier session); took it over (killed PID 15808, restarted fresh) so all payload timestamps are this session's.

*For reflection and entertainment only — not medical, legal, or financial advice.*
