"""สร้างภาพ tarot/cosmic ด้วย Hugging Face Inference API (ฟรี)
   เก็บภาพไว้ใน Astral/assets/ สำหรับใช้ใน frontend
   Models: SDXL, FLUX (ฟรี tier เพียงพอ)"""

import os
import json
import requests
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ASSETS = REPO / "assets" / "generated"
ASSETS.mkdir(parents=True, exist_ok=True)

HF_API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

HF_TOKEN = os.environ.get("HF_TOKEN", "")

headers = {"Authorization": f"Bearer {HF_TOKEN}"} if HF_TOKEN else {}

def generate(prompt: str, negative: str = "", steps: int = 30) -> bytes | None:
    """เรียก HF Inference API สร้างภาพ 1 รูป"""
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative or "blurry, bad quality, distorted",
            "num_inference_steps": steps,
            "width": 768,
            "height": 1152,  # tarot card ratio 2:3
        }
    }
    try:
        r = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            return r.content
        print(f"  Error {r.status_code}: {r.text[:200]}")
        return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

# ── Major Arcana 22 ใบ ──
MAJOR_ARCANA = [
    ("The Fool",     "A wanderer at cliff edge, golden staff in hand, small dog at heels, sunrise behind, cosmic nebula sky, tarot card art, gold leaf, regency style"),
    ("The Magician", "A figure with one hand raised to the sky, the other pointing to the earth, infinity symbol above head, tarot card art, mystical, gold and crimson"),
    ("The High Priestess", "A veiled woman seated between two pillars, crescent moon at feet, scroll in lap, tarot card art, purple and silver"),
    ("The Empress",  "A pregnant woman in a lush garden, crown of stars, Venus symbol, flowing gown, tarot card art, fertility and abundance"),
    ("The Emperor",  "A stern king on a stone throne, ram heads on armrests, scepter in hand, tarot card art, authority and structure"),
    ("The Hierophant", "A religious figure with raised hand in blessing, two acolytes before him, twin pillars, tarot card art, spiritual wisdom"),
    ("The Lovers",   "A man and woman with an angel above, tree of knowledge, mountain behind, tarot card art, love and choice"),
    ("The Chariot",  "A warrior in a chariot pulled by two sphinxes, starry canopy, tarot card art, willpower and triumph"),
    ("Strength",     "A woman gently closing a lion's mouth, infinity symbol above, flowers, tarot card art, inner strength"),
    ("The Hermit",   "An old man on a mountain peak holding a lantern, snowy peaks, tarot card art, solitude and guidance"),
    ("Wheel of Fortune", "A great wheel in the sky with sphinx, snake, and jackal, tarot card art, fate and cycles"),
    ("Justice",      "A figure with sword and scales, seated between pillars, tarot card art, fairness and truth"),
    ("The Hanged Man", "A man hanging upside down from a T-shaped cross, serene expression, halo, tarot card art, surrender and new perspective"),
    ("Death",        "A skeleton knight on a white horse, scythe in hand, sunrise behind, tarot card art, transformation and renewal"),
    ("Temperance",   "An angel with one foot on land, one in water, pouring water between two cups, tarot card art, balance and patience"),
    ("The Devil",    "A horned figure over two chained pentagrams, inverted torch, tarot card art, bondage and materialism"),
    ("The Tower",    "A lightning-struck tower with figures falling, flames and smoke, tarot card art, sudden upheaval"),
    ("The Star",     "A naked woman kneeling by a pool, pouring water, one large star and seven small stars above, tarot card art, hope and inspiration"),
    ("The Moon",     "A moon with a face, two towers, a dog and wolf howling, crayfish from water, tarot card art, illusion and subconscious"),
    ("The Sun",      "A radiant sun with a face, a child on a white horse, sunflowers, tarot card art, joy and success"),
    ("Judgement",    "An angel blowing a trumpet, figures rising from graves, mountain backdrop, tarot card art, rebirth and reckoning"),
    ("The World",    "A dancing figure wreathed in a mandorla, four corner symbols, tarot card art, completion and wholeness"),
]

def main():
    print("🎴 สร้าง Major Arcana 22 ใบ...")
    for name, prompt in MAJOR_ARCANA:
        fname = ASSETS / f"major_{name.lower().replace(' ','_')}.png"
        if fname.exists():
            print(f"  {name} — มีแล้ว, skip")
            continue
        print(f"  กำลังสร้าง {name}...")
        img = generate(prompt, negative="text, watermark, signature, blurry, bad anatomy")
        if img:
            fname.write_bytes(img)
            print(f"    → {fname.name}")
        else:
            print(f"    ล้มเหลว")

    print("\n✅ เสร็จแล้ว — ภาพอยู่ใน assets/generated/")

if __name__ == "__main__":
    main()
