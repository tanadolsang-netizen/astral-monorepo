"""Gene Keys engine — Profile (Activation/ Venus / Pearl sequences).

Gene Keys map IChing hexagrams onto the zodiac wheel (Ra Uru Hu's
Rave Mandala as used by Richard Rudd's Gene Keys). Deterministic:
zodiac longitude -> Gate -> Gene Key -> Shadow/Gift/Siddhi triad.

The 64-gate zodiac mapping is canonical public knowledge (the Rave
Mandala wheel starts Gate 41 at 02°00' Aquarius and runs in the
reverse IChing "Fu" order). Implemented natively; MIT-clean.
"""
from __future__ import annotations

# The Rave Mandala gate order, starting from Gate 41 at 2° Aquarius,
# proceeding backwards through the IChing sequence.
_GATE_ORDER = [
    41, 19, 13, 49, 30, 55, 37, 63, 22, 36, 25, 17,
    21, 51, 42, 3, 27, 24, 2, 23, 8, 20, 16, 35,
    45, 12, 15, 52, 39, 53, 62, 56, 31, 33, 7, 4,
    29, 59, 40, 64, 47, 6, 46, 18, 48, 57, 32, 50,
    28, 44, 1, 43, 14, 34, 9, 5, 26, 11, 10, 58,
    38, 54, 61, 60,
]
_GATE_START_LON = 302.0   # 2° Aquarius = 300+2

# Each gate's Gene Key: Shadow -> Gift -> Siddhi (Richard Rudd)
_GK = {
    41: ("Fantasy", "Anticipation", "Emergence"),
    19: ("Wanting", "Sensitivity", "Sacrifice"),
    13: ("Discord", "Discernment", "Sympathy"),
    49: ("Rejection", "Revolution", "Rebirth"),
    30: ("Desire", "Lightness", "Rapture"),
    55: ("Moodiness", "Freedom", "Freedom"),
    37: ("Weakness", "Equality", "Tenderness"),
    63: ("Doubt", "Inquiry", "Truth"),
    22: ("Greediness", "Graciousness", "Grace"),
    36: ("Crisis", "Humanity", "Compassion"),
    25: ("Constriction", "Acceptance", "Universal Love"),
    17: ("Opinions", "Farsightedness", "Omnisience"),
    21: ("Control", "Authority", "Sovereignty"),
    51: ("Agitation", "Initiative", "Awakening"),
    42: ("Expectation", "Detachment", "Celebration"),
    3: ("Confusion", "Innovation", "Ordering"),
    27: ("Selfishness", "Altruism", "Selflessness"),
    24: ("Addiction", "Rationalization", "Transformation"),
    2: ("Dislocation", "Orientation", "Unity"),
    23: ("Complexity", "Simplicity", "Assimilation"),
    8: ("Mediocrity", "Solidarity", "Style"),
    20: ("Superficiality", "Presence", "Divinity"),
    16: ("Indifference", "Versatility", "Mastery"),
    35: ("Hunger", "Progress", "Bounteousness"),
    45: ("Rejection", "Education", "Communion"),
    12: ("Vanity", "Fairness", "Discrimination"),
    15: ("Dullness", "Extremes", "Flower"),
    52: ("Stress", "Stillness", "Mountains"),
    39: ("Provocation", "Emotion", "Reverence"),
    53: ("Impatience", "Superabundance", "Preservation"),
    62: ("Intellect", "Detail", "Impeccability"),
    56: ("Distraction", "Enrichment", "Intoxication"),
    31: ("Arrogance", "Democracy", "Humility"),
    33: ("Forgetting", "Mindfulness", "Revelation"),
    7: ("Division", "Guidance", "Virtue"),
    4: ("Intolerance", "Understanding", "Forgiveness"),
    29: ("Half-Heartedness", "Devotion", "Devotion"),
    59: ("Lack", "Openness", "Transparency"),
    40: ("Exhaustion", "Resolve", "Divine Will"),
    64: ("Confusion", "Imagination", "I Ching"),
    47: ("Oppression", "Transmutation", "Transfiguration"),
    6: ("Conflict", "Diplomacy", "Peace"),
    46: ("Seriousness", "Determination", "Ecstasy"),
    18: ("Judgment", "Integrity", "Perfection"),
    48: ("Inadequacy", "Resourcefulness", "Well"),
    57: ("Unease", "Clarity", "Gentleness"),
    32: ("Failure", "Preservation", "Veneration"),
    50: ("Corruption", "Equilibrium", "Joyfulness"),
    28: ("Struggle", "Totality", "Immortality"),
    44: ("Interference", "Alertness", "Synarchy"),
    1: ("Entropy", "Freshness", "Beauty"),
    43: ("Deafness", "Insight", "Realization"),
    14: ("Compromise", "Competence", "Bounteousness"),
    34: ("Force", "Strength", "Power"),
    9: ("Inertia", "Vitality", "Invincibility"),
    5: ("Impatience", "Patience", "Timelessness"),
    26: (" Dishonesty", "Artistry", "Ingenuity"),
    11: ("Obscurity", "Ideality", "Light"),
    10: ("Self-Obsession", "Naturalness", "Being"),
    58: ("Restlessness", "Vitality", "Bliss"),
    38: ("Strife", "Stubbornness", "Honor"),
    54: ("Ambition", "Aspiration", "Matrimony"),
    61: ("Psychosis", "Inspiration", "Sanctity"),
    60: ("Limitation", "Realism", "Wisdom"),
}

_ZODIAC_DEGREE_TO_GK_OFFSET = {
    # Aries 0° is at wheel position: (0 - 302 +360)%360 /5 = 11.6 → index 11.6→12th entry
}


def _lon_to_gate(lon_zodiac: float) -> tuple[int, float]:
    """Zodiac longitude -> (gate, position-in-gate fraction)."""
    offset = (float(lon_zodiac) - _GATE_START_LON) % 360
    idx = int(offset // 5)          # each gate spans 5° of zodiac? No —
    # Rave mandala: 360°/64 gates ≈ 5.625° per gate
    idx = int(offset // (360 / 64))
    frac = (offset % (360 / 64)) / (360 / 64)
    return _GATE_ORDER[idx % 64], frac


def _line_from_frac(frac: float) -> int:
    """Gate line 1-6 from fractional position within gate."""
    return min(6, max(1, int(frac * 6) + 1))


def gene_key_for(lon_zodiac: float) -> dict:
    gk_no, frac = _lon_to_gate(lon_zodiac)
    shadow, gift, siddhi = _GK.get(gk_no, ("—", "—", "—"))
    return {"gate": gk_no, "gene_key": gk_no, "line": _line_from_frac(frac),
            "shadow": shadow, "gift": gift, "siddhi": siddhi}


def gene_keys_profile(sun_lon: float, earth_lon: float | None = None,
                      moon_lon: float | None = None,
                      asc_lon: float | None = None) -> dict:
    """Core profile: Life's Work (sun), Evolution (earth), Radiance (moon),
    Purpose (asc). Earth = sun+180."""
    if earth_lon is None:
        earth_lon = (sun_lon + 180) % 360

    seq = {
        "lifes_work": gene_key_for(sun_lon),
        "evolution": gene_key_for(earth_lon),
    }
    if moon_lon is not None:
        seq["radiance"] = gene_key_for(moon_lon)
    if asc_lon is not None:
        seq["purpose"] = gene_key_for(asc_lon)

    lw = seq["lifes_work"]
    th = (f"Life's Work ของคุณคือ Gene Key {lw['gene_key']} "
          f"({lw['shadow']} → {lw['gift']} → {lw['siddhi']}) — "
          f"เส้นทางจากเงาสู่ของขวัญสู่การรู้แจ้งของดวงวิญญาณคุณ")
    en = (f"Life's Work: GK {lw['gene_key']} "
          f"({lw['shadow']} → {lw['gift']} → {lw['siddhi']}).")

    return {
        "system": "gene-keys",
        "profile": seq,
        "interpretation": {"th": th, "en": en},
    }
