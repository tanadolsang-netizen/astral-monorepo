"""สร้างภาพ tarot/cosmic ด้วย Bing Image Creator (ฟรี)
   ใช้ cookie จาก bing.com สำหรับ authentication
   15 boosts/วัน (แต่ใช้ได้ไม่จำกัดแบบช้าลง)"""

import os
import json
import time
import requests
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ASSETS = REPO / "assets" / "generated"
ASSETS.mkdir(parents=True, exist_ok=True)

# ── Bing Image Creator API ──
BING_CREATE_URL = "https://www.bing.com/images/create"
BING_COOKIE = os.environ.get("BING_COOKIE", "")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,th;q=0.8",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.bing.com",
    "Referer": "https://www.bing.com/images/create",
}

if BING_COOKIE:
    HEADERS["Cookie"] = BING_COOKIE


def generate_bing(prompt: str, negative: str = "") -> bytes | None:
    """เรียก Bing Image Creator API สร้างภาพ 1 รูป"""
    payload = {
        "prompt": prompt,
        "negative_prompt": negative or "blurry, bad quality, distorted",
        "width": 768,
        "height": 1152,  # tarot card ratio 2:3
    }

    try:
        # Step 1: Submit generation request
        r = requests.post(
            BING_CREATE_URL,
            headers=HEADERS,
            data=payload,
            timeout=30,
            allow_redirects=True,
        )

        if r.status_code == 200:
            # Parse response — Bing returns JSON with image URLs or redirect
            try:
                data = r.json()
                # Extract image URL from response
                if "image_urls" in data:
                    img_url = data["image_urls"][0]
                elif "url" in data:
                    img_url = data["url"]
                elif "images" in data and data["images"]:
                    img_url = data["images"][0].get("url", "")
                else:
                    # Try to find image URL in redirect
                    img_url = r.url

                if img_url:
                    # Download the image
                    time.sleep(2)  # Wait for generation
                    img_r = requests.get(img_url, timeout=60)
                    if img_r.status_code == 200:
                        return img_r.content

            except json.JSONDecodeError:
                # Response might be HTML with embedded image
                if "image" in r.text.lower():
                    # Try to extract image URL from HTML
                    import re
                    img_match = re.search(r'https://[^"\']+\.(?:png|jpg|jpeg|webp)', r.text)
                    if img_match:
                        img_r = requests.get(img_match.group(), timeout=60)
                        if img_r.status_code == 200:
                            return img_r.content

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
    print("🎴 สร้าง Major Arcana 22 ใบ ด้วย Bing Image Creator...")

    if not BING_COOKIE:
        print("\n⚠️  ไม่พบ BING_COOKIE ใน environment variable")
        print("   1. ไปที่ https://www.bing.com/images/create")
        print("   2. เปิด DevTools (F12) → Application → Cookies")
        print("   3. คัดลอก cookie ทั้งหมด")
        print("   4. ตั้งค่า: export BING_COOKIE='...'")
        return

    for name, prompt in MAJOR_ARCANA:
        fname = ASSETS / f"major_{name.lower().replace(' ','_')}.png"
        if fname.exists():
            print(f"  {name} — มีแล้ว, skip")
            continue
        print(f"  กำลังสร้าง {name}...")
        img = generate_bing(prompt, negative="text, watermark, signature, blurry, bad anatomy")
        if img:
            fname.write_bytes(img)
            print(f"    → {fname.name}")
        else:
            print(f"    ล้มเหลว")
        time.sleep(3)  # Rate limit

    print("\n✅ เสร็จแล้ว — ภาพอยู่ใน assets/generated/")


if __name__ == "__main__":
    main()
