#!/usr/bin/env python3
"""BaZi verification via lunar-python — generates fixtures for 04-thai-bazi-engine-spec.

Computes the 4 pillars for both test cases and derives the EXACT
JDN -> sexagenary day-pillar offset constant, so the engine never guesses.

Run:  pip install lunar-python && python verify_bazi.py
"""
from lunar_python import Solar


def jdn(y: int, m: int, d: int) -> int:
    """Gregorian calendar date -> Julian Day Number."""
    a = (14 - m) // 12
    y2, m2 = y + 4800 - a, m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"


def gz_index(gz: str) -> int:
    """Sexagenary cycle index (0 = 甲子) of a GanZhi pair like '丁丑'."""
    s, b = STEMS.index(gz[0]), BRANCHES.index(gz[1])
    return next(i for i in range(60) if i % 10 == s and i % 12 == b)


CASES = [
    (1997, 5, 19, 5, 45, "OWNER 1997-05-19 05:45 ICT Chonburi"),
    (2001, 8, 18, 22, 32, "MAI   2001-08-18 22:32 ICT Nonthaburi"),
]

if __name__ == "__main__":
    print("lunar-python verification — 22 Aug 2026\n")
    for y, mo, d, h, mi, label in CASES:
        ec = Solar.fromYmdHms(y, mo, d, h, mi, 0).getLunar().getEightChar()
        pillars = [ec.getYear(), ec.getMonth(), ec.getDay(), ec.getTime()]
        j = jdn(y, mo, d)
        di = gz_index(pillars[2])
        offset = (di - j) % 60
        polarity = "yang" if di % 2 == 0 else "yin"
        print(f"{label}")
        print(f"  pillars Y/M/D/H : {' '.join(pillars)}")
        print(f"  JDN = {j} · day index = {di}  =>  day pillar = (JDN + {offset}) mod 60")
        print(f"  day master = {pillars[2][0]} ({polarity})\n")
