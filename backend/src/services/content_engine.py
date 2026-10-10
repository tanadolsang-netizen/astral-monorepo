"""
Content engine — the Co-Star-style assembly pipeline, our version.

This is the orchestrator that ties together:

  1. transit_service.compute_now()        → shared ephemeris (cached via Redis)
  2. cache_service.get_ephemeris_cached() → Redis cache-aside
  3. snippet_library.assemble()           → snippet selection + assembly
  4. behavior_layer.get_weights()         → personalization weights
  5. notification_service.send_daily()    → push delivery

The pipeline (matching Co-Star's 6-step model, but engine-driven):

  Step 1: Data Ingestion
    - Fetch shared ephemeris from Redis cache (or compute via
      transit_service if cache miss)
    - Extract Moon sign, retrogrades, aspects from the cached data

  Step 2: Enrichment (our addition — Co-Star doesn't have this)
    - If the user has Vedic dasha active, add Vedic trigger
    - If KP star lord changed, add KP trigger
    - If BaZi month branch changed, add BaZi trigger
    - If user drew a tarot card today, add tarot trigger
    - This is where our 83 engines SHINE — Co-Star has ~10 aspects,
      we have every engine that computes anything

  Step 3: Trigger derivation
    - snippet_library.derive_triggers(day) → list of trigger keys

  Step 4: Snippet selection (with behavior weighting)
    - behavior_layer.get_weights(user_id) → tag weights
    - snippet_library.assemble(triggers, weights) → Reading

  Step 5: Mood modulation (the "go outside more" effect)
    - behavior_layer.modulate_mood() → adjusted mood

  Step 6: Delivery
    - notification_service.send_daily_transit() → push + log

Our advantage over Co-Star:
  - Co-Star's content mapping is a static JSON query into a snippet
    library tagged by ~10 Western aspects
  - Ours is DYNAMIC — every engine that computes anything can contribute
    a trigger. Vedic dasha, KP sign lord, BaZi month branch, Gene Keys
    gate activation, tarot draw — all feed into the same assembler.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from src.services.behavior_layer import (
    get_weights,
    log_interaction,
    modulate_mood,
    BehaviorWeights,
)
from src.services.snippet_library import (
    Reading,
    assemble,
    derive_triggers,
    build_day_from_transit,
)
from src.services.transit_service import compute_now

logger = logging.getLogger("astral.content_engine")

# Bangkok coordinates as global fallback (same as notification_service)
_BANGKOK_LAT = 13.8591
_BANGKOK_LON = 100.5217


@dataclass
class DailyContent:
    """The fully assembled daily content for one user."""

    user_id: str
    epigram: str
    body: str
    do_list: tuple[str, ...]
    dont_list: tuple[str, ...]
    mood: str
    triggers: tuple[str, ...]
    snippet_ids: tuple[str, ...]
    engines_used: tuple[str, ...]
    moon_sign: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "user_id": self.user_id,
            "epigram": self.epigram,
            "body": self.body,
            "do": list(self.do_list),
            "dont": list(self.dont_list),
            "mood": self.mood,
            "triggers": list(self.triggers),
            "snippet_ids": list(self.snippet_ids),
            "engines_used": list(self.engines_used),
            "moon_sign": self.moon_sign,
        }


def generate_daily(
    user_id: str,
    lat: float | None = None,
    lon: float | None = None,
    tz_offset_hours: float = 7.0,
    enrichments: dict[str, Any] | None = None,
    exclude_snippet_ids: set[str] | None = None,
) -> DailyContent:
    """Generate personalized daily content for one user.

    This is the main entry point — called by the scheduler worker for
    every user whose transit time has arrived.

    Args:
      user_id: the user to generate content for
      lat, lon: user's birth coordinates (fallback: Bangkok)
      tz_offset_hours: user's timezone offset
      enrichments: optional pre-computed engine data (Vedic dasha, KP
        lord, BaZi month, tarot draw, gene keys gate). If not provided,
        only Western transit triggers fire.
      exclude_snippet_ids: snippets already shown today (dedup)

    Returns:
      DailyContent — the assembled reading ready for push delivery.
    """
    # Step 1: Fetch shared ephemeris (cached via Redis)
    # In production, this would use cache_service.get_ephemeris_cached()
    # For now, call compute_now directly (cache wiring happens at the
    # worker level — see worker_batch.py)
    transit = compute_now(
        lat=lat or _BANGKOK_LAT,
        lon=lon or _BANGKOK_LON,
        tz_offset_hours=tz_offset_hours,
    )

    # Step 2: Build the "day" dict from transit output
    day = build_day_from_transit(transit)

    # Step 2b: Enrichment — merge in engine-specific triggers
    if enrichments:
        day.update(enrichments)

    # Step 3: Derive triggers
    triggers = derive_triggers(day)

    # Step 4: Get behavior weights + assemble
    weights = get_weights(user_id)
    reading: Reading = assemble(
        triggers=triggers,
        behavior_weights=weights.tag_weights,
        exclude_ids=exclude_snippet_ids,
    )

    # Step 5: Mood modulation
    modulated_mood = modulate_mood(reading.mood, weights)

    # Determine which engines contributed triggers
    engines_used: set[str] = set()
    for t in triggers:
        if t.startswith("moon_") or t.startswith("aspect_") or t.startswith("planet_retro_"):
            engines_used.add("western")
        elif t.startswith("dasha_shift_"):
            engines_used.add("vedic")
        elif t.startswith("kp_sign_lord_"):
            engines_used.add("kp")
        elif t.startswith("bazi_"):
            engines_used.add("bazi")
        elif t.startswith("tarot_"):
            engines_used.add("tarot")
        elif t.startswith("gene_keys_"):
            engines_used.add("gene_keys")

    # Step 6: Log the snippet views (feeds back into behavior layer)
    for sid in reading.snippet_ids:
        log_interaction(
            user_id=user_id,
            kind="view_snippet",
            snippet_id=sid,
            trigger=triggers[0] if triggers else None,
        )

    return DailyContent(
        user_id=user_id,
        epigram=reading.epigram,
        body=reading.body,
        do_list=reading.do_list,
        dont_list=reading.dont_list,
        mood=modulated_mood,
        triggers=tuple(triggers),
        snippet_ids=reading.snippet_ids,
        engines_used=tuple(sorted(engines_used)),
        moon_sign=day.get("moon_sign"),
    )


def generate_for_scheduler(
    user_id: str,
    prefs: Any,
    enrichments: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """Scheduler entry point — generates content AND sends push.

    This wraps generate_daily + notification_service.send_daily_transit
    into one call, so the worker batch just calls this for every due
    user. Returns the notification log entry, or None if deduped.
    """
    from datetime import datetime, timezone
    from src.services.notification_service import (
        send_daily_transit,
        already_sent_today,
    )

    now_utc = datetime.now(timezone.utc)

    # Dedup check — never send twice in one day
    if already_sent_today(user_id, "daily_transit", now_utc):
        logger.info("Skipping %s — already sent today", user_id)
        return None

    # Generate content
    content = generate_daily(
        user_id=user_id,
        lat=getattr(prefs, "lat", None),
        lon=getattr(prefs, "lon", None),
        tz_offset_hours=getattr(prefs, "tz_offset_hours", 7.0),
        enrichments=enrichments,
    )

    # Compose the push message from the assembled reading
    title = content.epigram
    body_text = f"{content.body}\n\nทำ: {', '.join(content.do_list)}\nไม่ทำ: {', '.join(content.dont_list)}"

    # Send via notification_service (handles dedup + logging + push)
    # content_override = (headline, body, payload)
    entry = send_daily_transit(
        user_id=user_id,
        now_utc=now_utc,
        content_override=(title, body_text, {
            "kind": "daily_transit",
            "mood": content.mood,
            "triggers": list(content.triggers),
            "snippet_ids": list(content.snippet_ids),
            "engines_used": list(content.engines_used),
        }),
    )

    # Log the push tap for behavior tracking
    log_interaction(
        user_id=user_id,
        kind="tap_push",
        engine="western" if "western" in content.engines_used else None,
        tags=list(content.triggers)[:1] if content.triggers else None,
    )

    return entry


def _unused() -> None:
    pass
