# ปีนักษัตรไทย (Thai Year-Animal Zodiac)

**Slug:** `thai-zodiac-animals` · **Origin:** Shared with the Chinese 12-year
cycle, adapted into Thai and wider Southeast Asian tradition. Powers
`frontend/src/lib/thaiZodiac.ts` and `frontend/src/components/
ThaiZodiacWidget.tsx` on the app's home page.

## Overview

This is a **separate system** from the sun-sign zodiac used in
[[western-tropical]] and [[thai-horoscope]] — it assigns one of 12 animals
to an entire birth *year* (tied to the Thai/Chinese lunar new year boundary,
typically in late January or February) rather than a 30° slice of the
ecliptic at birth. Most Thai people know their year-animal fluently even
without knowing their Western sun sign; it's the more culturally load-bearing
system for casual identity and small talk in Thailand.

## The Twelve Animals

| ลำดับ | สัตว์ | ไทย | English |
|---|---|---|---|
| 1 | 🐀 | ชวด | Rat |
| 2 | 🐂 | ฉลู | Ox |
| 3 | 🐅 | ขาล | Tiger |
| 4 | 🐇 | เถาะ | Rabbit |
| 5 | 🐉 | มะโรง | Dragon |
| 6 | 🐍 | มะเส็ง | Snake |
| 7 | 🐎 | มะเมีย | Horse |
| 8 | 🐐 | มะแม | Goat |
| 9 | 🐒 | วอก | Monkey |
| 10 | 🐓 | ระกา | Rooster |
| 11 | 🐕 | จอ | Dog |
| 12 | 🐖 | กุน | Pig |

## Calendar note

The cycle turns over at the Thai/Chinese lunar new year, not January 1st —
someone born in early January or late January through mid-February should
check which side of that year's lunar boundary their birthday falls on.
`thaiZodiacForYear()` in this app uses the CE calendar year as a simplified
approximation (`(year - 2020) % 12` indexed from the most recent Rat year,
2020-01-25 to 2021-02-11) — precise enough for a quick lookup, but not exact
for people born in the January/February boundary window. A future revision
should take the exact lunar new year date per year rather than the calendar
year.

## Buddhist year (พ.ศ.)

Thailand's civil calendar counts years from the Buddha's death, 543 years
ahead of the Common Era (`buddhistYear(ceYear) = ceYear + 543`) — 2026 CE is
พ.ศ. 2569. Official documents, ID cards, and most everyday date references in
Thailand use พ.ศ., not CE, which is why the widget surfaces both.

## Pairing with sun-sign astrology

Traditional Thai fortune-telling often reads the year-animal alongside a sun
sign or Thai horoscope placement rather than choosing one system — the
animal year speaks to broad generational/collective traits, while
[[thai-horoscope]] or [[western-tropical]] speaks to individual birth-moment
placement. Neither replaces the other.

## Caveats

Provided for reflection and entertainment; not medical, legal, or financial
advice.
