"""Mayan Dreamspell / Tzolkin — engine spec C:/AI/research-astrology/14.

v1 = Dreamspell (Argüelles) pure-integer arithmetic; classical GMT 584283
correlation documented as alt mode but its constant is [VERIFY]-unpinned →
degrades to ``correlation_constant_unpinned``.

Epoch (QA note a, re-verified): ``ANCHOR_JDN = jdn(1987, 7, 26) = 2447003``
(epoch day = Kin 34); ``kin = ((33 + delta) mod 260) + 1`` with
``delta = JDN(date) − ANCHOR_JDN``. ⚠️ Naive ``delta mod 260`` (= 205 for the
test case) is WRONG — dropping the Kin-34 epoch offset is an off-by-33 bug
class; always compute through the spec formula.

Ground truth (M, DOB 1997-05-19): JDN 2450588 → delta 3585 → Kin 239 ·
Seal 19 BLUE STORM (Cauac) · Tone 5 OVERTONE.
"""

from __future__ import annotations

from datetime import date as date_type, datetime, timezone


def jdn(y: int, m: int, d: int) -> int:
    """Julian Day Number at noon of the Gregorian calendar date."""
    a = (14 - m) // 12
    y2 = y + 4800 - a
    m2 = m + 12 * a - 3
    return d + (153 * m2 + 2) // 5 + 365 * y2 + y2 // 4 - y2 // 100 + y2 // 400 - 32045


ANCHOR_JDN = jdn(1987, 7, 26)  # Dreamspell epoch: 2447003, Kin 34
EPOCH_KIN = 34

# 20 solar seals in order (spec §2). keyword_th shipped only where the spec
# wrote it verbatim (test-case seal) — others stay None rather than invented.
SEALS: list[dict] = [
    {"number": 1, "name": "Red Dragon", "keyword_en": "nurture / being"},
    {"number": 2, "name": "White Wind", "keyword_en": "spirit / breath-communication"},
    {"number": 3, "name": "Blue Night", "keyword_en": "abundance / dreaming"},
    {"number": 4, "name": "Yellow Seed", "keyword_en": "flowering / targets"},
    {"number": 5, "name": "Red Serpent", "keyword_en": "life-force / survival instinct"},
    {"number": 6, "name": "White World-Bridger", "keyword_en": "death / equality-opportunity"},
    {"number": 7, "name": "Blue Hand", "keyword_en": "accomplishment / healing-touch"},
    {"number": 8, "name": "Yellow Star", "keyword_en": "elegance / art-harmony"},
    {"number": 9, "name": "Red Moon", "keyword_en": "purify / universal water-flow"},
    {"number": 10, "name": "White Dog", "keyword_en": "love / heart-loyalty"},
    {"number": 11, "name": "Blue Monkey", "keyword_en": "magic / play-spontaneity"},
    {"number": 12, "name": "Yellow Human", "keyword_en": "free will / wisdom-influences"},
    {"number": 13, "name": "Red Skywalker", "keyword_en": "space / explorer-wakefulness"},
    {"number": 14, "name": "White Wizard", "keyword_en": "timelessness / receptivity-mage"},
    {"number": 15, "name": "Blue Eagle", "keyword_en": "vision / mind-planets"},
    {"number": 16, "name": "Yellow Warrior", "keyword_en": "intelligence / questioning-fearlessness"},
    {"number": 17, "name": "Red Earth", "keyword_en": "navigation / synchronicity"},
    {"number": 18, "name": "White Mirror", "keyword_en": "endlessness / reflection-order"},
    {"number": 19, "name": "BLUE STORM", "cauac": True,
     "keyword_en": "self-generation / catalysis-transform",
     "keyword_th": "การเร่งปฏิกิริยา/สร้างพลังใหม่จากตัวเอง"},
    {"number": 20, "name": "Yellow Sun", "keyword_en": "enlighten / universal fire-life"},
]

# 13 galactic tones in order (spec §2).
TONES: list[dict] = [
    {"number": 1, "name": "Magnetic", "keyword_en": "purpose-unify"},
    {"number": 2, "name": "Lunar", "keyword_en": "challenge-polarize"},
    {"number": 3, "name": "Electric", "keyword_en": "service-bond"},
    {"number": 4, "name": "Self-Existing", "keyword_en": "define-form"},
    {"number": 5, "name": "Overtone", "keyword_en": "empower-radiate"},
    {"number": 6, "name": "Rhythmic", "keyword_en": "balance-organize"},
    {"number": 7, "name": "Resonant", "keyword_en": "attune-channel"},
    {"number": 8, "name": "Galactic", "keyword_en": "integrity-harmonize"},
    {"number": 9, "name": "Solar", "keyword_en": "pulse-realize-intention"},
    {"number": 10, "name": "Spectral", "keyword_en": "liberate-dissolve"},
    {"number": 11, "name": "Planetary", "keyword_en": "manifest-perfect"},
    {"number": 12, "name": "Crystal", "keyword_en": "dedicate-gather"},
    {"number": 13, "name": "Cosmic", "keyword_en": "endure-transcend-presence"},
]


def kin_of(y: int, m: int, d: int) -> tuple[int, int]:
    """(kin, delta_days) through the spec epoch formula."""
    delta = jdn(y, m, d) - ANCHOR_JDN
    kin = ((EPOCH_KIN - 1 + delta) % 260) + 1
    return kin, delta


def _seal(kin: int) -> dict:
    n = ((kin - 1) % 20) + 1
    row = SEALS[n - 1]
    out = {k: v for k, v in row.items() if k != "cauac"}
    return out


def _tone(kin: int) -> dict:
    n = ((kin - 1) % 13) + 1
    return dict(TONES[n - 1])


def compute_mayan_tzolkin(
    birth_date: date_type | str | None,
    today: date_type | None = None,
) -> dict:
    """Dreamspell signature for a birth date + today's daily Kin."""
    if birth_date is None or (isinstance(birth_date, str) and not birth_date.strip()):
        return {"status": "unavailable", "reason": "missing_birth_date"}
    try:
        bd = (
            birth_date
            if isinstance(birth_date, date_type)
            else date_type.fromisoformat(str(birth_date)[:10])
        )
    except ValueError:
        return {"status": "unavailable", "reason": "invalid_birth_date"}

    kin, delta = kin_of(bd.year, bd.month, bd.day)
    seal, tone = _seal(kin), _tone(kin)

    td = today or datetime.now(timezone.utc).date()
    t_kin, _ = kin_of(td.year, td.month, td.day)

    _seal_parts = seal["name"].split()
    # Conventional Dreamspell word order: <color> <tone> <creature>,
    # e.g. "Blue Overtone Storm" (spec §2 test-case rendering).
    signature_en = (
        f"Kin {kin} — {_seal_parts[0].capitalize()} "
        f"{tone['name']} {' '.join(w.capitalize() for w in _seal_parts[1:])}"
    ).rstrip()

    return {
        "status": "ok",
        "system": "dreamspell_v1",
        "kin": kin,
        "seal": seal,
        "tone": tone,
        "signature_en": signature_en,
        "signature_th": (
            f"Kin {kin} — {seal['name']} เสียงที่ {tone['number']} ({tone['name']})"
        ),
        "epoch": {
            "anchor_jdn": ANCHOR_JDN,
            "anchor_kin": EPOCH_KIN,
            "birth_jdn": jdn(bd.year, bd.month, bd.day),
            "delta_days": delta,
            "note": (
                "naive delta mod 260 drops the Kin-34 epoch offset "
                "(off-by-33 bug class) — always use ((33+delta) mod 260)+1"
            ),
        },
        "daily_kin": {
            "date": td.isoformat(),
            "kin": t_kin,
            "seal": _seal(t_kin)["name"],
            "tone": _tone(t_kin)["name"],
        },
        "classical_gmt": {
            "status": "unavailable",
            "reason": "correlation_constant_unpinned",
        },
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
