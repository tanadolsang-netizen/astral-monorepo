"""Build ComfyUI prompts from astrological chart data."""

from __future__ import annotations

import random
from typing import Any

# Thai-to-English keyword mapping for image generation (cosmic/art terms)
THEME_KEYWORDS: dict[str, list[str]] = {
    "zodiac_aries": ["ram", "fiery", "red crimson", "volcanic", "desert dawn", "solar flare"],
    "zodiac_taurus": ["bull", "emerald", "meadow", "flowers blooming", "soft earth", "golden light"],
    "zodiac_gemini": ["twins", "dual", "silver mercury", "wind", "feathers", "mirrors"],
    "zodiac_cancer": ["crab", "moonlit", "silver blue", "ocean tide", "pearl", "motherhood"],
    "zodiac_leo": ["lion", "golden sun", "throne", "majesty", "solar crown", "fire"],
    "zodiac_virgo": ["maiden", "wheat harvest", "green meadow", "precision", "earth", "doves"],
    "zodiac_libra": ["scales", "balance", "rose pink", "sunset", "harmony", "art"],
    "zodiac_scorpio": ["scorpion", "phoenix", "deep crimson", "underwater", "transform", "mystery"],
    "zodiac_sagittarius": ["archer centaur", "arrow", "purple galaxy", "forest", "adventure", "fire"],
    "zodiac_capricorn": ["sea goat", "mountain peak", "grey stone", "ancient", "time", "snow"],
    "zodiac_aquarius": ["water bearer", "electric blue", "stars", "futuristic", "crystal", "aurora"],
    "zodiac_pisces": ["fish", "ocean dream", "lavender mist", "ethereal", "spiritual", "cosmic water"],
}

ELEMENT_KEYWORDS: dict[str, list[str]] = {
    "fire": ["flames", "solar", "ember", "warm glow", "phoenix fire", "sunset blaze"],
    "earth": ["mountains", "forest", "crystal cave", "ancient stone", "moss", "roots"],
    "air": ["clouds", "wind", "sky", "feathers", "floating", "breath"],
    "water": ["ocean", "rain", "river", "mist", "deep blue", "tide"],
}

PLANET_KEYWORDS: dict[str, list[str]] = {
    "sun": ["solar crown", "golden light", "radiant", "core of being", "divine spark"],
    "moon": ["moonlit", "silver", "dreams", "tides", "inner world", "reflection"],
    "mercury": ["winged", "mercurial", "silver swift", "messengers", "stars align"],
    "venus": ["rose", "beauty", "love", "harmony", "art", "emerald light"],
    "mars": ["warrior", "crimson", "flame", "battle", "iron", "energy"],
    "jupiter": ["king", "thunder", "wisdom", "purple", "expansion", "royal"],
    "saturn": ["time", "ring", "ancient", "shadow", "discipline", "obsidian"],
    "uranus": ["electric", "revolution", "crystal", "sudden light", "cosmic"],
    "neptune": ["dream", "ocean", "mist", "illusion", "spiritual", "lavender"],
    "pluto": ["underworld", "phoenix", "transform", "obsidian", "mystery", "void"],
}

HOUSE_KEYWORDS: dict[int, list[str]] = {
    1: ["self", "mirror", "identity", "dawn horizon"],
    2: ["treasure", "gold", "hands", "value"],
    3: ["scrolls", "messengers", "twin paths", "wind"],
    4: ["ancestral home", "roots", "moonlit garden", "sanctuary"],
    5: ["stage", "children", "creative fire", "festival"],
    6: ["healing", "garden", "service", "light through leaves"],
    7: ["union", "mirror", "balanced scales", "sacred partnership"],
    8: ["underworld", "transformation", "phoenix", "depths"],
    9: ["journey", "mountain temple", "star path", "wisdom"],
    10: ["throne", "summit", "crown", "monument"],
    11: ["stars", "community", "aurora", "vision"],
    12: ["ocean", "dreams", "mist", "infinite"],
}

NEGATIVE_PROMPT = (
    "text, watermark, logo, signature, border, frame, "
    "low quality, blurry, deformed, ugly, duplicate, "
    "bad anatomy, bad proportions, extra limbs, "
    "cartoon, anime, sketch, drawing, illustration, "
    "oversaturated, underexposed, grainy, noisy"
)


def build_prompt_from_chart(chart: dict[str, Any]) -> str:
    """Build a cosmic storytelling prompt from computed chart data.

    Takes the output of chart_service.compute_chart() and converts
    planetary positions, aspects, and dignities into SDXL keywords.
    """
    keywords: list[str] = []
    description_parts: list[str] = []

    # 1. Rising sign sets the overall tone
    asc = chart.get("ascendant", {})
    asc_sign = asc.get("sign", "").lower()
    if asc_sign in THEME_KEYWORDS:
        keywords.extend(random.sample(THEME_KEYWORDS[asc_sign], min(3, len(THEME_KEYWORDS[asc_sign]))))
        description_parts.append(f"ascendant in {asc_sign}")

    # 2. Sun sign core
    sun = chart.get("sun", {})
    sun_sign = sun.get("sign", "").lower()
    if sun_sign in THEME_KEYWORDS:
        keywords.extend(random.sample(THEME_KEYWORDS[sun_sign], min(2, len(THEME_KEYWORDS[sun_sign]))))
    if sun_sign in PLANET_KEYWORDS:
        keywords.extend(random.sample(PLANET_KEYWORDS[sun_sign], min(2, len(PLANET_KEYWORDS[sun_sign]))))
    description_parts.append(f"sun in {sun_sign}")

    # 3. Moon sign emotional tone
    moon = chart.get("moon", {})
    moon_sign = moon.get("sign", "").lower()
    if moon_sign in THEME_KEYWORDS:
        keywords.extend(random.sample(THEME_KEYWORDS[moon_sign], min(2, len(THEME_KEYWORDS[moon_sign]))))
    if moon_sign in PLANET_KEYWORDS:
        keywords.append(random.choice(PLANET_KEYWORDS["moon"]))
    description_parts.append(f"moon in {moon_sign}")

    # 4. Dominant element
    elements = chart.get("elements", {})
    if elements:
        dominant = max(elements, key=lambda k: elements.get(k, 0))
        if dominant in ELEMENT_KEYWORDS:
            keywords.extend(random.sample(ELEMENT_KEYWORDS[dominant], min(3, len(ELEMENT_KEYWORDS[dominant]))))
            description_parts.append(f"dominant {dominant}")

    # 5. Planet in dignities (exaltation, rulership, detriment, fall)
    planets = chart.get("planets", {})
    for planet_name, planet_data in planets.items():
        dignity = planet_data.get("dignity", "")
        if dignity in ("exaltation", "rulership"):
            planet_lower = planet_name.lower()
            if planet_lower in PLANET_KEYWORDS:
                keywords.append(random.choice(PLANET_KEYWORDS[planet_lower]))
            description_parts.append(f"{planet_name} in {dignity}")

    # 6. Strong aspects (conjunction, trine, square, opposition)
    aspects = chart.get("aspects", [])
    for aspect in aspects[:5]:  # Top 5 aspects
        atype = aspect.get("type", "")
        p1 = aspect.get("planet1", "").lower()
        p2 = aspect.get("planet2", "").lower()
        if atype == "conjunction":
            keywords.append("fusion")
        elif atype == "trine":
            keywords.append("harmony")
        elif atype == "square":
            keywords.append("tension")
        elif atype == "opposition":
            keywords.append("duality")

    # 7. House emphasis
    for planet_name, planet_data in planets.items():
        house = planet_data.get("house")
        if house and house in HOUSE_KEYWORDS:
            keywords.append(random.choice(HOUSE_KEYWORDS[house]))

    # Build final cosmic prompt
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_keywords: list[str] = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)

    # Cosmic storytelling scene description
    scene_prefix = (
        "cosmic astrological storytelling scene, "
        "celestial cosmic journey, mystical cosmos, "
        "zodiac wheel glowing in deep space, "
        "golden cosmic energy, ethereal nebula, "
        "sacred geometry, ancient star map, "
        "photorealistic, cinematic lighting, "
        "volumetric god rays, deep space, "
        "8k uhd, masterpiece, hyperdetailed"
    )

    keywords_str = ", ".join(unique_keywords[:15])  # Cap at 15 keywords for SDXL

    prompt = f"{scene_prefix}, {keywords_str}"
    return prompt


def get_negative_prompt() -> str:
    return NEGATIVE_PROMPT


def build_prompt_for_tarot_card(card_name: str, card_meaning: str) -> str:
    """Build a prompt for a specific tarot card illustration."""
    return (
        f"cosmic tarot illustration of {card_name}, "
        f"theme: {card_meaning}, "
        f"cosmic garden style, kim krans inspired, "
        f"celestial watercolor, gold leaf, "
        f"mystical, ethereal, deep space background, "
        f"photorealistic, 8k uhd, masterpiece"
    )
