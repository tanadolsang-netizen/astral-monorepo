"""
Behavior layer — the "recommendation engine" of Astral.

Co-Star's secret sauce (from their own FAQ):

  "We choose which transits to surface on your home screen based on your
   past behavior within the app. For example, if you always look at your
   6th/10th house or Saturn transits, we assume that's because you're a
   workaholic and show you more of those transits — and sometimes show you
   less because you should go outside more."

This is the missing piece between our engine (83 services) and the
snippet library. We track which engines/triggers the user engages with,
and use those signals to:

  1. Weight snippet selection (career-heavy users get more career snippets)
  2. Weight engine selection (a user who opens KP every day sees more KP
     content in their daily digest)
  3. Modulate tone — a user who reads melancholic content during a
     difficult period gets LIGHTER content (the "go outside more" effect)

Design:
  - SQLite table user_behavior_log (migration 003)
  - Log every meaningful interaction: engine viewed, snippet shown,
    reading opened, push tapped, detail scrolled
  - Derive weights from a rolling window (default: last 30 days)
  - Weight decay: older interactions count less
"""

from __future__ import annotations

import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("astral.behavior")

# Same DB as notification_service — shared SQLite file
DB_PATH = Path(__file__).resolve().parents[2] / "astral.db"

# Behavior tags that the snippet library uses — the axes we weight on
BEHAVIOR_TAGS = (
    "career",
    "love",
    "self",
    "social",
    "money",
    "health",
    "creativity",
    "spiritual",
)

# Engines the user can engage with — for engine-level weighting
ENGINES = (
    "western",
    "vedic",
    "kp",
    "jaimini",
    "chinese",
    "bazi",
    "ziwei",
    "qmdj",
    "tarot",
    "gene_keys",
    "parans",
    "synastry",
    "composite",
    "fusion",
)

# Interaction kinds we log
INTERACTION_KINDS = (
    "view_engine",      # user opened a specific engine's page
    "view_snippet",     # user saw a specific snippet in their reading
    "open_reading",     # user opened the full daily reading
    "tap_push",         # user tapped a push notification
    "share_reading",    # user shared their reading (screenshot/export)
    "scroll_detail",    # user scrolled deep into a long reading
    "search_topic",     # user searched for a specific topic
    "explore_friend",   # user explored a friend's chart
)

# Rolling window for weight derivation (seconds) — 30 days
WEIGHT_WINDOW_SECONDS = 30 * 24 * 3600

# Decay factor: interactions older than the window count 0; within the
# window, weight decays linearly from 1.0 (now) to 0.0 (30 days ago)
_DECAY_WINDOW = WEIGHT_WINDOW_SECONDS


@dataclass
class BehaviorWeights:
    """Derived weights for a user — tag weights + engine weights."""

    user_id: str
    tag_weights: dict[str, float] = None  # type: ignore[assignment]
    engine_weights: dict[str, float] = None  # type: ignore[assignment]
    interaction_count: int = 0

    def __post_init__(self) -> None:
        if self.tag_weights is None:
            self.tag_weights = {t: 0.5 for t in BEHAVIOR_TAGS}
        if self.engine_weights is None:
            self.engine_weights = {e: 0.5 for e in ENGINES}


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# ---------------------------------------------------------------------------
# Logging interactions
# ---------------------------------------------------------------------------


def log_interaction(
    user_id: str,
    kind: str,
    engine: str | None = None,
    trigger: str | None = None,
    snippet_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Log one user interaction.

    kind must be in INTERACTION_KINDS. engine/trigger/snippet_id/tags are
    optional context — the more you log, the better the weights.
    """
    if kind not in INTERACTION_KINDS:
        logger.warning("Unknown interaction kind: %s", kind)
        return

    import json

    con = _connect()
    try:
        con.execute(
            """
            INSERT INTO user_behavior_log
                (user_id, kind, engine, trigger, snippet_id, tags, metadata, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                user_id,
                kind,
                engine,
                trigger,
                snippet_id,
                ",".join(tags) if tags else None,
                json.dumps(metadata) if metadata else None,
            ),
        )
        con.commit()
    except sqlite3.Error as exc:
        logger.error("Failed to log interaction: %s", exc)
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Weight derivation
# ---------------------------------------------------------------------------


def _decay(age_seconds: float) -> float:
    """Linear decay from 1.0 (now) to 0.0 (window end)."""
    if age_seconds >= _DECAY_WINDOW:
        return 0.0
    return max(0.0, 1.0 - (age_seconds / _DECAY_WINDOW))


def get_weights(user_id: str) -> BehaviorWeights:
    """Derive behavior weights from the rolling 30-day window.

    Algorithm:
      - Query all interactions in the window.
      - For each interaction, decay its weight by age.
      - Sum weights per tag and per engine.
      - Normalize to 0.0-1.0 (if any interactions exist; otherwise 0.5).
    """
    con = _connect()
    try:
        cutoff = int(time.time()) - WEIGHT_WINDOW_SECONDS
        rows = con.execute(
            """
            SELECT kind, engine, tags,
                   CAST(strftime('%s', created_at) AS INTEGER) AS ts
            FROM user_behavior_log
            WHERE user_id = ?
              AND CAST(strftime('%s', created_at) AS INTEGER) >= ?
            """,
            (user_id, cutoff),
        ).fetchall()
    finally:
        con.close()

    if not rows:
        return BehaviorWeights(user_id=user_id, interaction_count=0)

    tag_sums: dict[str, float] = {}
    engine_sums: dict[str, float] = {}
    now = time.time()

    for row in rows:
        ts = row["ts"]
        if ts is None:
            continue  # skip rows with unparseable timestamps
        age = now - ts
        w = _decay(age)

        # Engine weight
        if row["engine"]:
            engine_sums[row["engine"]] = engine_sums.get(row["engine"], 0.0) + w

        # Tag weight (only if tags were logged)
        if row["tags"]:
            for tag in row["tags"].split(","):
                tag = tag.strip()
                if tag in BEHAVIOR_TAGS:
                    tag_sums[tag] = tag_sums.get(tag, 0.0) + w

    # Normalize to 0.0-1.0
    def _norm(sums: dict[str, float], defaults: tuple[str, ...]) -> dict[str, float]:
        if not sums:
            return {k: 0.5 for k in defaults}
        max_val = max(sums.values())
        if max_val == 0:
            return {k: 0.5 for k in defaults}
        return {k: round(sums.get(k, 0.0) / max_val, 3) for k in defaults}

    return BehaviorWeights(
        user_id=user_id,
        tag_weights=_norm(tag_sums, BEHAVIOR_TAGS),
        engine_weights=_norm(engine_sums, ENGINES),
        interaction_count=len(rows),
    )


# ---------------------------------------------------------------------------
# Content modulation — the "go outside more" effect
# ---------------------------------------------------------------------------


def modulate_mood(
    base_mood: str,
    weights: BehaviorWeights,
    melancholic_intensity: float = 0.0,
) -> str:
    """Adjust the mood of a snippet based on user behavior.

    Co-Star's insight: if a user is engaging heavily with difficult
    content (melancholic, intense, rebellious) — especially during a
    hard period — the app should SOMETIMES show them lighter content
    instead. "Go outside more."

    We implement this as:
      - If the user has a lot of 'melancholy' + 'intense' interactions
        (indicating they might be in a hard time) AND the base mood is
        also heavy, we flip to a lighter mood 30% of the time.
      - Lighter moods: 'playful', 'romantic', 'patient'
    """
    heavy_moods = {"melancholy", "intense", "rebellious", "defiant"}
    light_moods = {"playful", "romantic", "patient", "ambitious"}

    if base_mood not in heavy_moods:
        return base_mood

    # If the user is heavily engaging with heavy content, sometimes lighten
    heavy_tag_weight = max(
        weights.tag_weights.get("self", 0.0),
        weights.tag_weights.get("spiritual", 0.0),
    )
    if heavy_tag_weight > 0.7:
        # Deterministic-ish modulation based on user_id hash + day
        # (avoids random for testability; flips ~30% of the time)
        import hashlib

        seed = f"{weights.user_id}:{base_mood}"
        h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        if (h % 100) < 30:
            return "playful"

    return base_mood


# ---------------------------------------------------------------------------
# Snapshot helpers (for tests + admin endpoints)
# ---------------------------------------------------------------------------


def get_interaction_count(user_id: str, days: int = 30) -> int:
    """Total interactions for a user in the last N days."""
    con = _connect()
    try:
        cutoff = int(time.time()) - (days * 24 * 3600)
        row = con.execute(
            "SELECT COUNT(*) AS n FROM user_behavior_log WHERE user_id = ? AND strftime('%s', created_at) >= ?",
            (user_id, cutoff),
        ).fetchone()
        return row["n"] if row else 0
    finally:
        con.close()


def clear_user_history(user_id: str) -> None:
    """Wipe a user's behavior history (GDPR-style delete)."""
    con = _connect()
    try:
        con.execute("DELETE FROM user_behavior_log WHERE user_id = ?", (user_id,))
        con.commit()
    finally:
        con.close()
