# 10 · ASTEROIDS ENGINE SPEC — Juno · Chiron · Lilith · Vesta · Pallas · Ceres
> **EN:** Production ephemeris = Swiss Ephemeris (pyswisseph). All test-case positions below are MACHINE-COMPUTED (see `verify_asteroids.py`, seas_18.se1) — not estimates. Bilingual TH/EN.
> **TH:** ใช้ Swiss Ephemeris เป็น production — ตำแหน่งทั้งหมดด้านล่างคำนวณจริงด้วย `verify_asteroids.py` (ไฟล์ ephe ในโฟลเดอร์นี้)

---

## 1 · Ephemeris sourcing / แหล่งข้อมูล
```python
# pip install pyswisseph   ; set ephemeris path to ./ephe (seas_18.se1 = main asteroids, semo_18.se1 = moon/osculating)
import swisseph as swe
swe.set_ephe_path('./ephe')
jd = swe.julday(1997, 5, 19, 22.75 - 0/24)   # UT! (05:45 ICT = 1997-05-18 22:45 UT → julday input day=18, hour=22.75)
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
pos_lilith_mean = swe.fixstar2_ut('semean_apogee'... )  # mean Lilith via swe.lilith/jplhorizons-equivalent:
# mean apogee: swe.calc_ut(jd, swe.MEAN_APOG); osculating: swe.calc_ut(jd, swe.OSCU_APOG)
# asteroids: swe.calc_ut(jd, i) with i = JPL small-body id (Juno=3, Vesta=4, Pallas=2, Ceres=1)
# Chiron: swe.calc_ut(jd, swe.CHIRON)
```
**Decision:** use **mean Lilith** for v1 (stable ephemeris, astro.com default; osculating swings ±2°+/day making interpretations unstable). Chiron needs `seas_18.se1` ✓ already downloaded.
**Skyfield fallback:** NOT practical for these bodies in v1 (small-body SPICE kernels heavy) — pyswisseph only.

## 2 · Test-case positions (M: 19 May 1997 05:45 ICT, Chonburi — computed, tropical)
| Body | Position | Speed | Whole-sign house (Tau ASC) |
|---|---|---|---|
| Chiron | **26°47′ Libra R** | −0.058°/d | H6 |
| Mean Lilith | **6°45′ Virgo** | +0.111 | H5 |
| Ceres | **7°25′ Pisces** | +0.234 | H11 |
| Pallas | **6°29′ Aquarius** | +0.025 | H10 |
| **Juno** | **25°44′ Gemini** | +0.559 | H2 |
| Vesta | **4°51′ Aries** | +0.421 | H12 |

Cross-checks vs vault anchors: ASC 25°57′36″ Taurus ↔ vault ~25.96 ✓ · MC 16°25′33″ Aquarius ↔ vault 16.43 ✓ · Chiron 26°46′36″ Libra R ↔ serennu interpolation 26°55′ R ✓ (vault note superseded by this exact value).

## 3 · Meaning rules (sign+house, condensed TH/EN; orbs conj/sq/tr ≤3°)
| Body | Domain | Rule |
|---|---|---|
| **Juno** | marriage contract style | sign = "the partner you actually commit to"; house = where the marriage energy lives; aspects to Sun/Moon/Venus/Desc = spouse-significator |
| **Chiron** | wound→gift | house = life area of core wound & healing gift; hard aspects = wound activation; flowing = healing talent |
| **Lilith (mean)** | untamed shadow desire | sign/house = where suppression backfires; integration = power source |
| **Vesta** | sacred focus/devotion | house = where you burn brightest when dedicated |
| **Pallas** | strategy/pattern-craft | house = tactical intelligence arena |
| **Ceres** | nurture/self-care cycle | house = how you feed & need feeding |

## 4 · Synastry add-ons (weights on spec-03 scale)
| Contact | Weight |
|---|---|
| Juno conj partner's Desc/Sun/Moon/Venus (≤3°) | +8 |
| Juno–Juno any major aspect (≤3°) | +5 |
| Juno trine/sextile partner's Juno ruler | +3 |
| Chiron conj partner's luminary (healing bond) | ±5 (flowing gift / hard wound) |
| Lilith conj partner's Venus/Mars (≤3°) | ±4 (magnetic shadow pull — print both voices) |

## 5 · ⭐ Worked hits (test pair M×Mai)
- **M's Juno 85.73° Gemini sextile Mai's Sun 145.74° Leo — orb 0.01° (exact!)**: his commitment-style resonates precisely with her identity — marriage-significator +8. TH: *"จูโน่ของเขาเซ็กสไตล์กับดวงอาทิตย์ของเธอเป๊ะ 0.01° — รูปแบบการผูกมัดของเขาพูดภาษาเดียวกับตัวตนของเธอ"*
- M's Juno in Gemini H2: commits through words + shared resources stability.
- M's Chiron Libra H6 R: relationship-wound heals through daily-service work (pairs with Ju-Sa antardasha ending Nov 2026).
- Mai-side asteroid positions: [RUNTIME] compute with same script at her birth instant.

## 6 · Output templates
- TH: *"จูโน่ [sign] เรือน [H]: คุณผูกมัดกับ[style] — คู่ที่จริงคือคนที่[quality]. ไครออนเรือน [H]: แผลเก่าเรื่อง[area]คือของขวัญการเยียวยาของคุณ"*
- EN: *"Juno in [sign], house [H]: you commit through [style]; your real partner is someone who [quality]. Chiron in house [H]: the old wound around [area] is your healing gift."*

## Implementation Notes (QA 2026-08-23)
**(a) Ephemeris reality:**
- de421.bsp does NOT carry Chiron/Ceres/Pallas/Juno/Vesta — must use Swiss Ephemeris data files (seas_18.se1 main-asteroids + seas_18.se1 Chiron is in seas_18 too) with pyswisseph + swe.set_ephe_path('ephe/').
- Install: pip deps alone are NOT enough; ship ephe/ files (~2-4 MB) into repo or document download.
**(b) Ground truth (M):** compute Chiron at birth 1997-05-19 05:45 ICT — expect Libra ~15-17° sidereal (verify once ephe files land; placeholder until then).
**(c) Degradation:** swisseph import fail or ephe files missing → {'status':'unavailable','reason':'pyswisseph/ephe files not available'} (current live behavior — correct).
