"""Observability: structured JSON logging, request ID & timing middleware, metrics.

Public API:
    setup_logging() -> None  — call before FastAPI app is created
    get_request_id_context_var() -> ContextVar[str]
    RequestIDMiddleware, RequestTimingMiddleware, MetricsMiddleware
    metrics_registry — thread-safe counters / histogram totals
"""

from __future__ import annotations

import os
import time
import uuid
from contextvars import ContextVar
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

# ---------------------------------------------------------------------------
# Structured JSON logging
# ---------------------------------------------------------------------------

_logged = False


def setup_logging() -> None:
    """Configure the root logger to emit JSON lines to stdout.

    Safe to call multiple times — guarded by module-level flag.
    Respects LOG_LEVEL env var (default INFO).
    """
    global _logged
    if _logged:
        return

    try:
        from pythonjsonlogger import jsonlogger  # type: ignore[import-untyped]
    except ImportError:
        # Fallback: plain stdlib if package not available
        import logging
        logging.basicConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        _logged = True
        return

    import logging

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s",
        rename_fields={"asctime": "timestamp", "levelname": "level"},
    )
    handler.setFormatter(fmt)

    root = logging.getLogger()
    # Replace existing handlers so we don't double-log
    for h in list(root.handlers):
        root.removeHandler(h)
    root.addHandler(handler)
    root.setLevel(level)

    # Quiet noisy libraries
    for noisy in ("uvicorn.access", "uvicorn.error"):
        logging.getLogger(noisy).setLevel(level + 10)

    _logged = True


# ---------------------------------------------------------------------------
# Request ID
# ---------------------------------------------------------------------------

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    return _request_id_ctx.get()


def _new_request_id() -> str:
    return uuid.uuid4().hex[:12]


# ---------------------------------------------------------------------------
# Metrics (in-memory, single-process)
# ---------------------------------------------------------------------------

from collections import defaultdict
from threading import Lock

_metrics_lock = Lock()
_counters: dict[str, int] = defaultdict(int)
_histogram_total: dict[str, float] = defaultdict(float)


class MetricsRegistry:
    """Thread-safe in-memory counters for /metrics endpoint."""

    @staticmethod
    def increment(name: str, amount: int = 1) -> None:
        with _metrics_lock:
            _counters[name] += amount

    @staticmethod
    def histogram(name: str, value: float) -> None:
        with _metrics_lock:
            _histogram_total[name] += value

    @staticmethod
    def snapshot() -> dict:
        with _metrics_lock:
            return {
                "counters": dict(_counters),
                "histogram_total": dict(_histogram_total),
            }


metrics_registry = MetricsRegistry()


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

def get_logger(name: str):
    """Get a logger with request_id injected via filter."""
    import logging
    logger = logging.getLogger(name)

    class RequestIDFilter(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
            record.request_id = _request_id_ctx.get()  # type: ignore[attr-defined]
            return True

    if not any(isinstance(f, RequestIDFilter) for f in logger.filters):
        logger.addFilter(RequestIDFilter())

    return logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID; echo it back in the response header X-Request-ID."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        rid = request.headers.get("x-request-id") or _new_request_id()
        token = _request_id_ctx.set(rid)
        try:
            response = await call_next(request)
            response.headers["x-request-id"] = rid
            return response
        finally:
            _request_id_ctx.reset(token)


class RequestTimingMiddleware(BaseHTTPMiddleware):
    """Log request start/finish with duration, status, path, method."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        logger = get_logger("astral.request")
        start = time.perf_counter()

        # Log start
        logger.info("request_started", extra={
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query),
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        })

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception:
            status = 500
            raise
        finally:
            duration = time.perf_counter() - start
            level = "info" if status < 500 else "error"
            getattr(logger, level)(
                "request_finished",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status,
                    "duration_ms": round(duration * 1000, 2),
                },
            )

            # Update metrics
            metrics_registry.increment("requests_total")
            metrics_registry.increment(f"status_{status // 100}xx")
            if status >= 400:
                metrics_registry.increment("errors_total")
            metrics_registry.histogram("request_duration_seconds", duration)

        # Add timing header (outside finally: response is bound only on success path)
        response.headers["x-response-time-ms"] = f"{(time.perf_counter() - start) * 1000:.2f}"

        return response


# ---------------------------------------------------------------------------
# Register middleware on a FastAPI app
# ---------------------------------------------------------------------------

_app_startup_time: Optional[float] = None


def attach_observability(app: FastAPI) -> None:
    """Attach observability middleware, /health, /metrics, and startup logging."""
    global _app_startup_time

    app.add_middleware(RequestTimingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/health", tags=["observability"])
    async def health() -> JSONResponse:
        import asyncio
        import sys

        uptime_seconds: Optional[float] = None
        if _app_startup_time is not None:
            uptime_seconds = round(time.time() - _app_startup_time, 2)

        return JSONResponse({
            "status": "ok",
            "version": app.version,
            "uptime_seconds": uptime_seconds,
            "python": sys.version.split()[0],
        })

    @app.get("/metrics", tags=["observability"])
    async def metrics() -> JSONResponse:
        snapshot = metrics_registry.snapshot()
        snapshot["uptime_seconds"] = (
            round(time.time() - _app_startup_time, 2)
            if _app_startup_time is not None
            else None
        )
        return JSONResponse(snapshot)

    @app.on_event("startup")
    async def _startup():
        global _app_startup_time
        _app_startup_time = time.time()
        logger = get_logger("astral.startup")
        route_count = len([r for r in app.routes if hasattr(r, "methods")])
        logger.info(
            "service_started",
            extra={
                "service": app.title,
                "version": app.version,
                "route_count": route_count,
                "environment": os.getenv("ENV", "dev"),
            },
        )
