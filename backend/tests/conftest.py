"""Shared test fixtures: reset in-memory state between tests.

The FastAPI app keeps module-level state (rate limiter, i18n cache) that
persists across TestClient requests. With 550+ tests hammering the same
client IP, the public rate limit (60 req/min) trips mid-suite and turns
unrelated tests flaky. This fixture clears that state before each test.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Clear the in-memory rate limiter before every test."""
    from src.main import rate_limiter

    rate_limiter._requests.clear()
    yield
    rate_limiter._requests.clear()
