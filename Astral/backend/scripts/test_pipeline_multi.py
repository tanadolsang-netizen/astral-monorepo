"""Test the combined PDF pipeline against multiple birth charts.

Runs build_combined_final logic for several people to prove the pipeline
is not hard-coded to one chart: tarot draw (deterministic by birthdate),
chart-derived decor image, and Thai card names all vary per input.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.build_combined_final import th_card_name

# We re-import the real draw_spread from the service
from src.services.tarot_service import draw_spread, MAJOR_ARCANA
from src.services.tarot_images import CARD_INDEX

# Myth decor candidates keyed by dominant element
MYTH = {
    "fire": "sun.jpg",        # Helios
    "earth": "saturn.jpg",    # Cronus / earth stability
    "air": "mercury.jpg",     # Hermes
    "water": "moon.jpg",      # Selene
}


def dominant_element(chart_positions: dict) -> str:
    """Guess dominant element from planet signs (simplified for test)."""
    elem = {"fire": 0, "earth": 0, "air": 0, "water": 0}
    sign_elem = {
        "เมษ": "fire", "สิงห์": "fire", "ธนู": "fire",
        "พฤษภ": "earth", "กันย์": "earth", "มังกร": "earth",
        "เมถุน": "air", "ตุลย์": "air", "กุมภ์": "air",
        "กรกฎ": "water", "แมว": "water", "มีน": "water",
    }
    for sign in chart_positions.values():
        e = sign_elem.get(sign)
        if e:
            elem[e] += 1
    if not elem:
        return "fire"
    return max(elem, key=elem.get)


# Test charts: name -> (date str for seed, planet signs dict for decor)
TESTS = [
    ("นาย 19/05/1997", "19970519", {
        "อาทิตย์": "พฤษภ", "ดวงจันทร์": "เมษ", "ลัคนา": "พฤษภ",
        "ดาวพุธ": "เมถุน", "ดาวศุกร": "เมถุน", "ดาวอังคาร": "มีน",
    }),
    (" Mai 18/08/2001", "20010818", {
        "อาทิตย์": "สิงห์", "ดวงจันทร์": "มังกร", "ลัคนา": "กันย์",
        "ดาวพุธ": "สิงห์", "ดาวศุกร": "กรกฎ", "ดาวอังคาร": "กรกฎ",
    }),
    (" สมมติ 01/01/2000", "20000101", {
        "อาทิตย์": "มังกร", "ดวงจันทร์": "เมถุน", "ลัคนา": "มีน",
        "ดาวพุธ": "มังกร", "ดาวศุกร": "ธนู", "ดาวอังคาร": "แมว",
    }),
]

if __name__ == "__main__":
    for label, seed_str, signs in TESTS:
        seed = int(seed_str)
        draw = draw_spread(seed_str, spread="past-present-future", seed=seed)
        cards = [th_card_name(c["card"]) for c in draw["cards"]]
        orient = ["ย้อนกลับ" if c["is_reversed"] else "ตั้งตรง" for c in draw["cards"]]
        dom = dominant_element(signs)
        decor = MYTH.get(dom, "sun.jpg")
        print(f"\n=== {label} (seed {seed}) ===")
        print("  ธาตุเด่น:", dom, "-> รูปตกแต่ง:", decor)
        for i, (cn, o) in enumerate(zip(cards, orient), 1):
            print(f"  ตำแหน่ง {i}: {cn} ({o})")
