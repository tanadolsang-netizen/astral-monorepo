-- Migration 003: Behavior layer table
-- Tracks user interactions to drive personalized content weighting.
-- Co-Star pattern: "We choose which transits to surface based on your
-- past behavior within the app."

CREATE TABLE IF NOT EXISTS user_behavior_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    kind TEXT NOT NULL,
    engine TEXT,
    trigger TEXT,
    snippet_id TEXT,
    tags TEXT,
    metadata TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Index for the weight-derivation query (user + time window)
CREATE INDEX IF NOT EXISTS idx_behavior_user_time
    ON user_behavior_log (user_id, created_at);

-- Index for engine-level analytics
CREATE INDEX IF NOT EXISTS idx_behavior_engine
    ON user_behavior_log (engine);

-- Index for snippet analytics (which snippets get engagement)
CREATE INDEX IF NOT EXISTS idx_behavior_snippet
    ON user_behavior_log (snippet_id);
