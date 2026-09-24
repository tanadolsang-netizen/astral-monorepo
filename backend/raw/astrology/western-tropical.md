# Western Tropical Astrology

**Slug:** `western-tropical` · **Origin:** Hellenistic Egypt/Mesopotamia,
formalized in Ptolemy's *Tetrabiblos* (2nd century CE), the basis for
`system=tropical` in this app's `/v1/natal/compute` endpoint.

## Overview

The tropical zodiac is anchored to the **seasons**, not the visible
constellations. 0° Aries is fixed at the moment of the March equinox every
year, regardless of which constellation the Sun actually appears in front of.
Because of axial precession (the slow 26,000-year wobble of Earth's spin
axis), tropical sign boundaries have drifted about 24° away from the
constellations they were named after since antiquity — this is the same 24°
gap referenced as the "ayanamsa" in [[vedic-sidereal]] and
[[thai-horoscope]].

## The Ten Bodies

This app computes: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus,
Neptune, Pluto (`src/services/chart_service.py:BODIES`). Uranus, Neptune, and
Pluto were only discoverable after 1781/1846/1930 respectively, so they have
no place in the classical Hellenistic or Vedic systems — traditions built
before their discovery use the seven classical "planets" (Sun through
Saturn) exactly like the Thai Nawagraha system, minus Rahu/Ketu.

## The Twelve Signs

Aries, Taurus, Gemini, Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius,
Capricorn, Aquarius, Pisces — each a fixed 30° slice of the ecliptic
starting from the equinox point. Each sign has an element (fire/earth/
air/water), a modality (cardinal/fixed/mutable), and a ruling planet.

## Houses and the Ascendant

The **Ascendant** (rising sign) is the zodiac degree crossing the eastern
horizon at the moment of birth — it depends on birth *time and location*,
not just date, which is why `ChartRequest` requires `time`, `lat`, and `lon`
(see `src/models/chart.py`). This app's `compute_ascendant()` uses local
sidereal time (via Greenwich Mean Sidereal Time) and the standard right
ascension of the midheaven formula to derive it — the same spherical
trigonometry underlies every house system, though house-*division* methods
(Placidus, Whole Sign, Equal) differ in how they carve the remaining 11
houses between angles; this app currently computes only the Ascendant angle,
not full house cusps.

## Aspects

Angular relationships between two bodies' ecliptic longitudes are read as
aspects — conjunction (0°), sextile (60°), square (90°), trine (120°),
opposition (180°) — each with an allowed "orb" of deviation. This app's
`/v1/synastry/cross-aspects` endpoint (`src/services/aspects.py`) computes
these between two charts to describe a relationship's dynamics: trines and
sextiles are traditionally read as harmonious, squares and oppositions as
tension that drives growth, and conjunctions as blended, amplified energy.

## Caveats

Provided for reflection and entertainment; not medical, legal, or financial
advice.
