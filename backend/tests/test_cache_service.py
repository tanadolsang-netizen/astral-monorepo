"""Tests for the Redis cache layer (shared ephemeris state).

Cache behaviour is exercised with a fake Redis client (no server needed):
hit, miss->compute+store, corrupt-entry recovery, key schema, tz bucketing,
and date invalidation.
"""

import json

import pytest

from src.services import cache_service as cs


class FakeRedis:
    def __init__(self):
        self.store = {}
        self.ttls = {}
        self.fail_get = False
        self.fail_set = False

    def get(self, key):
        if self.fail_get:
            raise RuntimeError("simulated redis get failure")
        return self.store.get(key)

    def setex(self, key, ttl, value):
        if self.fail_set:
            raise RuntimeError("simulated redis set failure")
        self.store[key] = value
        self.ttls[key] = ttl

    def scan_iter(self, pattern, count=100):
        import fnmatch

        return [k for k in list(self.store) if fnmatch.fnmatch(k, pattern)]

    def delete(self, *keys):
        n = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                n += 1
        return n

    def info(self, section):
        return {"keyspace_hits": 10, "keyspace_misses": 2}


@pytest.fixture(autouse=True)
def reset_client():
    cs._redis_client = FakeRedis()
    cs._redis_checked = True
    yield
    cs._redis_client = None
    cs._redis_checked = False


# --- key schema ------------------------------------------------------------

def test_cache_key_format():
    assert cs.cache_key("2026-10-10", "UTC+7", "Moon", "position") == (
        "ephem:2026-10-10:UTC+7:Moon:position"
    )


def test_tz_bucketing_whole_hours():
    assert cs.tz_group_for(7.0) == "UTC+7"
    assert cs.tz_group_for(-5.0) == "UTC-5"
    assert cs.tz_group_for(5.5) == "UTC+6"  # same bucket as UTC+6


def test_same_tz_bucket_shares_key():
    assert cs.cache_key("2026-10-10", cs.tz_group_for(7.0), "Sun", "position") == (
        cs.cache_key("2026-10-10", cs.tz_group_for(7.4), "Sun", "position")
    )


# --- cache-aside -----------------------------------------------------------

def test_miss_computes_and_stores():
    calls = []

    def compute():
        calls.append(1)
        return {"lon": 120.5}

    key = "ephem:2026-10-10:UTC+7:Moon:position"
    result = cs.get_or_compute(key, compute, ttl=3600)

    assert result == {"lon": 120.5}
    assert len(calls) == 1
    assert json.loads(cs._redis_client.store[key]) == {"lon": 120.5}
    assert cs._redis_client.ttls[key] == 3600


def test_hit_skips_compute():
    cs._redis_client.store["k1"] = json.dumps({"cached": True})

    def compute():
        raise AssertionError("compute must not run on cache hit")

    assert cs.get_or_compute("k1", compute) == {"cached": True}


def test_corrupt_entry_recomputes():
    cs._redis_client.store["k1"] = "{not valid json"
    result = cs.get_or_compute("k1", lambda: {"fresh": 1})
    assert result == {"fresh": 1}
    # corrupt entry overwritten with valid json
    assert json.loads(cs._redis_client.store["k1"]) == {"fresh": 1}


def test_get_failure_falls_back_to_compute():
    cs._redis_client.fail_get = True
    assert cs.get_or_compute("k", lambda: "value") == "value"


def test_set_failure_still_returns_value():
    cs._redis_client.fail_set = True
    assert cs.get_or_compute("k", lambda: "value") == "value"


# --- typed helpers ---------------------------------------------------------

def test_get_ephemeris_cached_uses_schema_key():
    cs.get_ephemeris_cached("2026-10-10", 7.0, "Venus", "position", lambda: {"sign": "Scorpio"})
    assert "ephem:2026-10-10:UTC+7:Venus:position" in cs._redis_client.store


def test_get_transit_cached_uses_all_bucket():
    cs.get_transit_cached("2026-10-10", 7.0, lambda: {"aspects": []})
    assert "ephem:2026-10-10:UTC+7:all:transit" in cs._redis_client.store
    assert cs._redis_client.ttls["ephem:2026-10-10:UTC+7:all:transit"] == (
        cs.TRANSIT_TTL_SECONDS
    )


# --- invalidation ----------------------------------------------------------

def test_invalidate_date_drops_matching_entries():
    client = cs._redis_client
    client.store["ephem:2026-10-10:UTC+7:Moon:position"] = "1"
    client.store["ephem:2026-10-10:UTC+7:all:transit"] = "2"
    client.store["ephem:2026-10-11:UTC+7:Moon:position"] = "3"  # other date

    assert cs.invalidate_date("2026-10-10") == 2
    assert "ephem:2026-10-10:UTC+7:Moon:position" not in client.store
    assert "ephem:2026-10-11:UTC+7:Moon:position" in client.store


def test_invalidate_date_no_matches():
    assert cs.invalidate_date("1999-01-01") == 0


# --- no-redis mode ---------------------------------------------------------

def test_no_redis_connected_stats():
    cs._redis_client = None
    cs._redis_checked = False
    cs.REDIS_URL = ""
    assert cs.cache_stats() == {"connected": False}


def test_no_redis_invalidate_returns_zero():
    cs._redis_client = None
    cs._redis_checked = False
    cs.REDIS_URL = ""
    assert cs.invalidate_date("2026-10-10") == 0
