import os
import logging
import time
import uuid
from contextlib import asynccontextmanager
from collections import defaultdict
from threading import Lock

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("astral")

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

ENV = os.getenv("ENV", "dev")

# ── Rate Limiter (in-memory, per-IP) ─────────────────────────
class RateLimiter:
    """Simple sliding-window rate limiter with per-path-prefix limits."""

    def __init__(self):
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def _cleanup(self, timestamps: list[float], window: int) -> list[float]:
        """Remove timestamps outside the window."""
        now = time.time()
        return [t for t in timestamps if now - t < window]

    def is_allowed(self, key: str, max_requests: int, window: int = 60) -> bool:
        """Check if request is allowed under rate limit."""
        with self._lock:
            timestamps = self._requests[key]
            timestamps = self._cleanup(timestamps, window)
            self._requests[key] = timestamps
            if len(timestamps) >= max_requests:
                return False
            timestamps.append(time.time())
            return True

    def get_retry_after(self, key: str, window: int = 60) -> int:
        """Get seconds until next request is allowed."""
        with self._lock:
            timestamps = self._requests.get(key, [])
            if not timestamps:
                return 0
            oldest = min(timestamps)
            retry = window - (time.time() - oldest)
            return max(1, int(retry))

rate_limiter = RateLimiter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Astral backend starting...")
    yield
    logger.info("Astral backend shutting down...")

app = FastAPI(
    title="Astral Backend",
    version="3.0.0",
    lifespan=lifespan,
)

# ── Request ID ──────────────────────────────────────────────
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# ── Request Logging Middleware ──────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log method, path, status code, and response time."""
    start_time = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed_ms,
    )
    response.headers["X-Response-Time-Ms"] = f"{elapsed_ms:.1f}"
    return response

# ── Security Headers Middleware ─────────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'"
    )
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
        "magnetometer=(), microphone=(), payment=(), usb=()"
    )
    return response

# ── Rate Limiting Middleware ─────────────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limits: 10 req/min for auth, 60 req/min for public."""
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path

    # Determine rate limit based on path
    if path.startswith("/v1/auth"):
        limit = 10
        key = f"auth:{client_ip}"
    else:
        limit = 60
        key = f"public:{client_ip}"

    if not rate_limiter.is_allowed(key, max_requests=limit, window=60):
        retry_after = rate_limiter.get_retry_after(key, window=60)
        logger.warning(
            "Rate limit exceeded: %s %s (ip=%s, limit=%d/min)",
            request.method, path, client_ip, limit,
        )
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded. Please slow down.",
                "retry_after": f"{retry_after} seconds",
            },
            headers={"Retry-After": str(retry_after)},
        )

    return await call_next(request)

# ── CORS ─────────────────────────────────────────────────────
# In production, restrict origins to specific domains
if ENV in ("prod", "production"):
    _cors_origins = [
        "https://astral.onrender.com",
        "https://astral.app",
        "https://www.astral.app",
    ]
else:
    # Development: allow localhost and common dev ports
    _cors_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)

# ── Routers (all API v1) ─────────────────────────────────────
from .routers import natal, transit, synastry, branches, payments, health, auth, notifications, dashboard, memory, tarot, horary, western, fusion, fusion_profile, fusion_full, fusion_grand, bazi, chinese, reports, vedic, muhurta, chat, accuracy, life, sky, research, comfyui
from .routers import new_engines, narrative_router, grand_narrative_router, ai_router, image_tools

for router, prefix, tags in [
    (health.router, "", ["health"]),
    (auth.router, "/v1/auth", ["auth"]),
    (natal.router, "/v1/natal", ["natal"]),
    (transit.router, "/v1/transit", ["transit"]),
    (synastry.router, "/v1/synastry", ["synastry"]),
    (branches.router, "/v1/branches", ["branches"]),
    (dashboard.router, "/v1/dashboard", ["dashboard"]),
    (payments.router, "/v1/payments", ["payments"]),
    (notifications.router, "/v1/notifications", ["notifications"]),
    (memory.router, "/v1/memory", ["memory"]),
    (tarot.router, "/v1/tarot", ["tarot"]),
    (horary.router, "/v1/horary", ["horary"]),
    (western.router, "/v1/western", ["western"]),
    (fusion.router, "/v1/fusion", ["fusion"]),
    (fusion_profile.router, "/v1/fusion", ["fusion-profile"]),
    (fusion_full.router, "", ["fusion-full"]),
    (fusion_grand.router, "", ["fusion-grand"]),
    (bazi.router, "/v1/bazi", ["bazi"]),
    (chinese.router, "/v1/chinese", ["chinese"]),
    (reports.router, "/v1/reports", ["reports"]),
    (vedic.router, "/v1/vedic", ["vedic"]),
    (muhurta.router, "/v1/muhurta", ["muhurta"]),
    (chat.router, "/v1/chat", ["chat"]),
    (accuracy.router, "/v1/accuracy", ["accuracy"]),
    (life.router, "/v1/life", ["life"]),
    (sky.router, "/v1/sky", ["sky"]),
    (research.router, "/v1/research", ["research"]),
    (narrative_router.router, "", ["narrative"]),
    (grand_narrative_router.router, "", ["grand-narrative"]),
    (ai_router.router, "", ["ai-narrative"]),
    (new_engines.tr, "/v1/hellenistic", ["hellenistic"]),
    (new_engines.av, "/v1/ashtakavarga", ["ashtakavarga"]),
    (new_engines.al, "/v1/arabic-lots", ["arabic-lots"]),
    (new_engines.dh, "/v1/draconic-harmonics", ["draconic-harmonics"]),
    (new_engines.acg, "/v1/astrocartography", ["astrocartography"]),
    (new_engines.mt, "/v1/mahataksa", ["mahataksa"]),
    (new_engines.jm, "/v1/jaimini", ["jaimini"]),
    (new_engines.pr, "/v1/prashna", ["prashna"]),
    (new_engines.qm, "/v1/qmdj", ["qmdj"]),
    (new_engines.dlr, "/v1/daliuren", ["daliuren"]),
    (new_engines.fs, "/v1/flying-stars", ["flying-stars"]),
    (new_engines.sa, "/v1/solar-arc", ["solar-arc"]),
    (new_engines.ft, "/v1/fusion-transparency", ["fusion"]),
    (new_engines.rt, "/v1/rectification", ["rectification"]),
    (new_engines.ur, "/v1/uranian", ["uranian"]),
    (new_engines.ta, "/v1/timing", ["timing"]),
    (new_engines.kp, "/v1/kp", ["kp"]),
    (new_engines.cm, "/v1/chomangkala-v2", ["numerology"]),
    (new_engines.bn, "/v1/bench", ["bench"]),
    (new_engines.sar, "/v1/sa-rectifier", ["rectification"]),
    (new_engines.kk, "/v1/kakshya", ["ashtakavarga"]),
    (new_engines.br, "/v1/parans", ["fixed-stars"]),
    (new_engines.rv, "/v1/reel-video", ["reel"]),
    (new_engines.gk, "/v1/genekeys", ["gene-keys"]),
    (comfyui.router, "/v1/comfyui", ["comfyui"]),
    (image_tools.router, "/v1/image", ["image-tools"]),
]:
    app.include_router(router, prefix=prefix, tags=tags)

# ── Serve ComfyUI Output Images ─────────────────────────────
import os
comfyui_output_dir = os.getenv("COMFYUI_OUTPUT_DIR", r"C:/Users/ADMIN/Documents/comfy/ComfyUI/output")
if os.path.exists(comfyui_output_dir):
    app.mount("/comfyui-output", StaticFiles(directory=comfyui_output_dir), name="comfyui-output")
    logger.info("Serving ComfyUI output from %s", comfyui_output_dir)

# ── Static Files (Landing Page) ─────────────────────────────
import os
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── i18n Endpoint ─────────────────────────────────────────────
from pathlib import Path as _Path

_i18n_cache: dict | None = None

@app.get("/v1/i18n", include_in_schema=False)
async def get_i18n():
    global _i18n_cache
    if _i18n_cache is None:
        i18n_path = _Path(__file__).parent.parent / "i18n.json"
        if i18n_path.exists():
            import json
            with open(i18n_path, "r", encoding="utf-8") as f:
                _i18n_cache = json.load(f)
        else:
            _i18n_cache = {}
    return JSONResponse(_i18n_cache)

# ── Landing Page ─────────────────────────────────────────────
import os

# Serve landing page from ../landing/ directory (not backend/static/)
landing_dir = os.path.dirname(os.path.abspath(__file__))
_landing_path = os.path.normpath(os.path.join(landing_dir, "..", "..", "landing"))

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def landing_page():
    for fname in ("astral-landing.html", "index.html"):
        index_path = os.path.join(_landing_path, fname)
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(content="""
    <!DOCTYPE html><html><head><title>Astral</title></head>
    <body style="background:#000;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0">
    <div style="text-align:center"><h1>Astral API</h1><p>Online — <a href="/docs" style="color:#8b5cf6">Docs</a></p></div>
    </body></html>
    """)

# ── API Info (JSON) ──────────────────────────────────────────
@app.get("/api", include_in_schema=False)
async def api_info():
    return JSONResponse({
        "service": "Astral API",
        "status": "online",
        "version": "3.0.0",
        "docs": "/docs",
        "endpoints": {
            "astrology": ["/v1/natal", "/v1/transit", "/v1/synastry", "/v1/vedic", "/v1/western"],
            "ai": ["/v1/ai/reading", "/v1/chat", "/v1/narrative"],
            "tools": ["/v1/tarot", "/v1/horary", "/v1/bazi", "/v1/chinese"],
        }
    })
