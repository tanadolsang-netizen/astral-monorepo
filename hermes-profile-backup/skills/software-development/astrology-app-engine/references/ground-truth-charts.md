# Ground-Truth Charts — regression fixtures

Any astrology calculation must reproduce these numbers EXACTLY before shipping.
Sources: vault natal notes + verify_calcs.py (C:/AI/research-astrology/) + pytest tests/test_fusion_engine.py.

## Chart M — vault owner

Born **19 May 1997, 05:45 ICT (UTC+7)**, Chonburi (13.36N, 100.98E).

### Tropical
| Body | Position |
|---|---|
| Sun | Taurus 28.05° |
| Moon | Libra 17.37° |
| ASC | Scorpio 25.96° |
| Mercury | Taurus 3.38° |
| Venus | Gemini 10.15° |
| Mars | Virgo 19.32° |
| Saturn | Aries 16.08° |
| North Node | Virgo 25.75° |

### Sidereal (Lahiri)
ASC Scorpio 2.28° · Sun Taurus 4.37° · Moon Virgo 23.69° · Mercury Aries 9.70° · Venus Taurus 16.47° · Mars Leo 25.64° · Jupiter Capricorn 27.53° · Saturn Pisces 22.40° · Rahu Virgo 2.07° / Ketu Pisces 2.07°

### Derived (verified by code)
- Moon sidereal lon = 173.69° → nakshatra **Chitra pada 1** (2.7% elapsed), lord Mars
- Vimshottari: Mars balance 6.81y → Rahu MD 2004–2022 → **Jupiter MD 2022-03 → 2038-03**; Jupiter-Saturn AD ≈2024.33–2026.86; Jupiter-Mercury AD next; Saturn MD starts 2038
- D9 Navamsha: Venus Taurus→Taurus = **Vargottama** (strongest Venus condition); Sun→Aquarius, Moon→Leo, Mercury→Gemini, Mars→Scorpio, Jupiter→Virgo, Saturn→Capricorn
- Chara Karaka (7 scheme): AK=Jupiter 27.53 · AmK=Mars 25.64 · BK=Moon 23.69 · MK=Saturn 22.40 · PuK=Venus 16.47 · GK=Mercury 9.70 · **DK=Sun 4.37**
- BaZi year pillar: **Ding-Chou 丁丑 (Fire Ox)** — Lichun cutoff satisfied (May > Feb 4); clash partner Goat → **2027 (Ding-Wei Fire Goat) = ชงปีเกิด**
- ตรียัมปาไถ for 19-05-1997: day 1+9=10→**1**, month **5**, year 1+9+9+7=26→**8**, total 1+5+8=14→**5**

## Chart Mai

Born **18 Aug 2001, 22:32 ICT**, Nonthaburi (~13.86N, 100.52E). Tropical: Sun Leo 25.74° · Moon Leo 18.95° (Sun-Moon conj ~7° orb) · ASC Taurus 6.34° · Venus Cancer 19.90° · Mercury Virgo 8.15° · Mars Sagittarius 20.74° · Saturn Gemini 13.59°.

## Known synastry M×Mai (verified aspects)

- Mai Venus Cancer 19.9 **sextile** M Mars Virgo 19.32 (orb 0.58)
- M Venus Gemini 10.15 **conjunct** Mai Saturn Gemini 13.59 (orb 3.44)
- Mai ASC Taurus 6.34 conj M Mercury Taurus 3.38 (~3°)
- Mutual whole-sign 7th-house ASC overlay (Taurus/Scorpio axis)
- Friction: M Sun square Mai Sun+Moon; M ASC Scorpio square Leo stellium
- Mai Venus in M's 9th house; M Venus in Mai's 2nd/3rd

## Fusion API sanity output (22 Aug 2026 live run)

Saturn opp natal Moon (orb 3.59) → love domain "structuring" · Sun square natal Sun exact → health "activating" · verdicts career 56 / love 56 / money 55 / health 61 / growth 56 · weekday Saturday → ruler Saturn, lucky number 9.
