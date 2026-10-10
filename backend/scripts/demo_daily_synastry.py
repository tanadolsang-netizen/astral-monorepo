"""E2E demo script — user + partner, daily reading + synastry profile.

Usage:
    cd /c/AI/backend && ./.venv/Scripts/python.exe scripts/demo_daily_synastry.py
"""
from __future__ import annotations

import asyncio
import json
import sys
from datetime import date, time
from pathlib import Path

# add backend/ to sys.path so `src` is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.models.chart import ChartRequest  # noqa: E402
from src.services.chart_service import compute_chart  # noqa: E402
from src.services.synastry_scoring import compute_synastry_profile  # noqa: E402
from src.services.content_engine import generate_daily  # noqa: E402
from src.services.geocoder_service import geocode  # noqa: E402
from src.services.transit_service import compute_transits_to_natal  # noqa: E402


USER = dict(
    name="นายท่าน",
    date=date(1997, 5, 19),
    time=time(5, 45),
    lat=13.36,
    lon=100.98,
    tz_offset_hours=7.0,
)
PARTNER = dict(
    name="คุณไม้",
    date=date(2001, 8, 18),
    time=time(22, 32),
    lat=13.86,
    lon=100.51,
    tz_offset_hours=7.0,
)


def _pretty(title: str, payload: dict) -> None:
    print(f"\n{'=' * 70}")
    print(title)
    print("=" * 70)
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def run_daily(label: str, data: dict, birth_chart: dict) -> None:
    """Generate a daily reading using transit-to-natal contacts.

    This is the real Co-Star-style personalization: instead of asking
    'what sign is the Moon in today' (which is the same for everyone),
    we ask 'which of today's transits are touching MY natal chart'.
    """
    print(f"\n=== DAILY — {label} ===")
    contacts = compute_transits_to_natal(
        natal_chart=birth_chart,
        lat=data["lat"],
        lon=data["lon"],
        tz_offset_hours=data["tz_offset_hours"],
    )
    top = contacts[:5]
    print("Top active transits to your natal:")
    for c in top:
        print(f"  {c['transit']} {c['aspect']} natal {c['natal']} "
              f"(orb {c['orb']}°) weight={c['impact_weight']}")

    c = generate_daily(
        user_id=f"demo_{label}",
        lat=data["lat"],
        lon=data["lon"],
        tz_offset_hours=data["tz_offset_hours"],
        enrichments={
            "natal_sun_sign": birth_chart["bodies"][1]["sign"],
            "natal_moon_sign": birth_chart["bodies"][2]["sign"],
            "natal_asc_sign": birth_chart["ascendant"]["sign"],
            "natal_bodies": {
                b["body"]: {"sign": b["sign"], "degree": b["degree"]}
                for b in birth_chart["bodies"]
            },
            "top_transits": [
                f"transit_{c_['transit']}_{c_['aspect']}_{c_['natal']}"
                for c_ in top
            ],
        },
    )
    print(f"Epigram: {c.epigram}")
    print(f"Mood: {c.mood} | Triggers: {c.triggers}")
    print(f"Engines: {c.engines_used} | Moon: {c.moon_sign}")
    print(f"\nBody:\n{c.body}")
    print(f"\nทำ: {', '.join(c.do_list)}")
    print(f"ไม่ทำ: {', '.join(c.dont_list)}")
    return c


def run_natal(label: str, data: dict) -> dict:
    print(f"\n=== NATAL — {label} ===")
    chart = compute_chart(
        name=data["name"],
        date=data["date"],
        time=data["time"],
        lat=data["lat"],
        lon=data["lon"],
        tz_offset_hours=data["tz_offset_hours"],
        system="tropical",
    )
    asc = chart["ascendant"]
    print(f"Asc: {asc['sign']} {asc['degree']:.2f}°")
    for b in chart["bodies"]:
        print(f"  {b['body']}: {b['sign']} {b['degree']:.2f}°")
    return chart


def main() -> None:
    print("ASTRAL DEMO — Daily Reading + Synastry")
    print(f"User: {USER['date']} {USER['time']} UTC+{USER['tz_offset_hours']}")
    print(f"Partner: {PARTNER['date']} {PARTNER['time']} UTC+{PARTNER['tz_offset_hours']}")

    # Geocode the district/province into real coordinates
    user_geo = geocode("เมืองชลบุรี", "ชลบุรี")
    partner_geo = geocode("เมืองนนทบุรี", "นนทบุรี")
    if user_geo:
        USER["lat"], USER["lon"] = user_geo.lat, user_geo.lon
        print(f"Geocoded USER: {user_geo.display_name} ({user_geo.lat}, {user_geo.lon})")
    if partner_geo:
        PARTNER["lat"], PARTNER["lon"] = partner_geo.lat, partner_geo.lon
        print(f"Geocoded PARTNER: {partner_geo.display_name} ({partner_geo.lat}, {partner_geo.lon})")

    # 1. Daily readings — compute natal charts first, then pass them in
    chart_a = compute_chart(
        name=USER["name"], date=USER["date"], time=USER["time"],
        lat=USER["lat"], lon=USER["lon"], tz_offset_hours=USER["tz_offset_hours"],
        system="tropical",
    )
    chart_b = compute_chart(
        name=PARTNER["name"], date=PARTNER["date"], time=PARTNER["time"],
        lat=PARTNER["lat"], lon=PARTNER["lon"], tz_offset_hours=PARTNER["tz_offset_hours"],
        system="tropical",
    )
    run_daily("คุณ (นายท่าน)", USER, chart_a)
    run_daily("คุณไม้", PARTNER, chart_b)

    # 2. Synastry
    profile = compute_synastry_profile(chart_a, chart_b)

    print("\n" + "=" * 70)
    print("SYNASTRY — คู่ของคุณ")
    print("=" * 70)
    print(f"Overall: {profile['overall']}")
    print("\nDimensions:")
    for dim, val in profile["dimensions"].items():
        print(f"  {dim}: {val}")
    print("\nTop bonds:")
    for b in profile["top_bonds"][:5]:
        print(f"  {b}")
    print("\nFrictions:")
    for f in profile["frictions"][:5]:
        print(f"  {f}")
    print(f"\nKarmic: {profile['karmic']['method']}")
    if profile["karmic"].get("notes"):
        for n in profile["karmic"]["notes"][:3]:
            print(f"  {n}")


if __name__ == "__main__":
    main()
