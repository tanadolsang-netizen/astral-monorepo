# Vedic / Jyotiṣa Sidereal Astrology

**Slug:** `vedic-sidereal` · **Origin:** Ancient India; the direct ancestor
of [[thai-horoscope]], the basis for `system=sidereal` in this app's
`/v1/natal/compute` endpoint.

## Overview

Jyotiṣa ("science of light") measures zodiac positions against the actual
background stars (sidereal), not the seasons (tropical) — see
[[western-tropical]] for the contrast. Because the two zeropoints have
drifted apart over the centuries, a sidereal chart shifts every body back by
the **ayanamsa**, currently around 24°. This app implements the most common
reference point, the **Lahiri ayanamsa**, via `lahiri_ayanamsa()` in
`src/services/chart_service.py` — a linear approximation anchored near 23.68°
in 1997 and drifting by about 50.29 arcseconds per year (the measured rate of
axial precession).

```python
def lahiri_ayanamsa(year_frac: float) -> float:
    return 23.68 + (year_frac - 1997) * (50.29 / 3600)
```

## Grahas (the Nine Planets)

Jyotiṣa uses the same nine grahas as Thai Nawagraha — Surya (Sun), Chandra
(Moon), Mangala (Mars), Budha (Mercury), Guru/Brihaspati (Jupiter), Shukra
(Venus), Shani (Saturn), Rahu and Ketu (the lunar nodes) — predating the
telescope-discovered outer planets. Rahu and Ketu are always exactly 180°
apart, since both mark the same orbital-crossing line seen from opposite
ends.

## Nakshatras: the 27 Lunar Mansions

Jyotiṣa's most distinctive layer is the **nakshatra** system: the ecliptic
is divided into 27 segments of 13°20' each, tracking the Moon's roughly
27.3-day sidereal orbit. Each nakshatra carries its own mythology, ruling
deity, and character themes, and is used for `muhurta` (electional timing)
much like the Thai `ดวงพิชัยสงคราม` timing tradition referenced in
[[thai-horoscope]]. This app does not yet compute nakshatra placements —
only sign (rāśi) and degree.

## Dashas: Planetary Periods

Rather than reading the whole chart as static, Jyotiṣa sequences a person's
life into **dasha** periods — multi-year spans ruled by one graha at a time
(the most common system, Vimshottari, cycles through a fixed 120-year
sequence). This is a significant structural difference from Western
astrology, which more often reads *transits* against a static natal chart
rather than pre-sequencing life into ruled eras.

## Ascendant (Lagna)

Computed the same way structurally as the Western Ascendant — local
sidereal time plus spherical trigonometry against birth latitude — but
expressed in sidereal coordinates, so a Vedic Lagna and a tropical Ascendant
for the same birth data will show different signs even though the underlying
math (`compute_ascendant()`) is shared in this app's implementation.

## Caveats

Provided for reflection and entertainment; not medical, legal, or financial
advice.
