# FastAPI ASGI app factory
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

# Must run before any integration module reads env vars (stripe_client sets
# stripe.api_key at import time), and before the routers package pulls those
# integrations in transitively.
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .routers import natal, transit, synastry, branches, payments, health, auth, notifications, dashboard, memory, tarot, horary, western, fusion, fusion_profile, fusion_full, fusion_grand, bazi, chinese, reports, vedic, muhurta, chat, accuracy
from .routers import new_engines
from .routers import sky, research
from .integrations.supabase_client import init_supabase
from .integrations.stripe_client import init_stripe

ENV = os.getenv("ENV", "dev")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

# Validate ENV at startup — fail fast if misconfigured
_VALID_ENVS = {"dev", "staging", "prod"}
if ENV not in _VALID_ENVS:
    raise RuntimeError(f"ENV must be one of {_VALID_ENVS}, got '{ENV}'")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("SUPABASE_URL"):
        init_supabase()
    if os.getenv("STRIPE_SECRET_KEY"):
        init_stripe()
    yield


app = FastAPI(
    title="Astral Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Rate limiting: 100 requests per minute per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter

# Global exception handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error."},
    )

# A wildcard origin ("*") is incompatible with allow_credentials=True per the
# fetch/CORS spec (browsers reject the response outright), so dev mode still
# needs an explicit allowlist rather than "*".
_default_dev_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS or (_default_dev_origins if ENV == "dev" else ["https://astral.app"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
app.include_router(natal.router, prefix="/v1/natal", tags=["natal"])
app.include_router(transit.router, prefix="/v1/transit", tags=["transit"])
app.include_router(synastry.router, prefix="/v1/synastry", tags=["synastry"])
app.include_router(branches.router, prefix="/v1/branches", tags=["branches"])
app.include_router(dashboard.router, prefix="/v1/dashboard", tags=["dashboard"])
app.include_router(payments.router, prefix="/v1/payments", tags=["payments"])
app.include_router(notifications.router, prefix="/v1/notifications", tags=["notifications"])
app.include_router(memory.router, prefix="/v1/memory", tags=["memory"])
app.include_router(tarot.router, prefix="/v1/tarot", tags=["tarot"])
app.include_router(horary.router, prefix="/v1/horary", tags=["horary"])
app.include_router(western.router, prefix="/v1/western", tags=["western"])
app.include_router(fusion.router, prefix="/v1/fusion", tags=["fusion"])
app.include_router(fusion_profile.router, prefix="/v1/fusion", tags=["fusion-profile"])
app.include_router(fusion_full.router, tags=["fusion-full"])
app.include_router(fusion_grand.router, tags=["fusion-grand"])
app.include_router(bazi.router, prefix="/v1/bazi", tags=["bazi"])
app.include_router(chinese.router, prefix="/v1/chinese", tags=["chinese"])
app.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
app.include_router(vedic.router, prefix="/v1/vedic", tags=["vedic"])
app.include_router(muhurta.router, prefix="/v1/muhurta", tags=["muhurta"])
app.include_router(chat.router, prefix="/v1/chat", tags=["chat"])
app.include_router(accuracy.router, prefix="/v1/accuracy", tags=["accuracy"])
app.include_router(new_engines.tr, prefix="/v1/hellenistic", tags=["hellenistic"])
app.include_router(new_engines.av, prefix="/v1/ashtakavarga", tags=["ashtakavarga"])
app.include_router(new_engines.al, prefix="/v1/arabic-lots", tags=["arabic-lots"])
app.include_router(new_engines.dh, prefix="/v1/draconic-harmonics", tags=["draconic-harmonics"])
app.include_router(new_engines.acg, prefix="/v1/astrocartography", tags=["astrocartography"])
app.include_router(new_engines.mt, prefix="/v1/mahataksa", tags=["mahataksa"])
app.include_router(new_engines.jm, prefix="/v1/jaimini", tags=["jaimini"])
app.include_router(new_engines.pr, prefix="/v1/prashna", tags=["prashna"])
app.include_router(new_engines.qm, prefix="/v1/qmdj", tags=["qmdj"])
app.include_router(new_engines.dlr, prefix="/v1/daliuren", tags=["daliuren"])
app.include_router(new_engines.fs, prefix="/v1/flying-stars", tags=["flying-stars"])
app.include_router(new_engines.sa, prefix="/v1/solar-arc", tags=["solar-arc"])
app.include_router(new_engines.ft, prefix="/v1/fusion-transparency", tags=["fusion"])
app.include_router(new_engines.rt, prefix="/v1/rectification", tags=["rectification"])
app.include_router(new_engines.ur, prefix="/v1/uranian", tags=["uranian"])
app.include_router(new_engines.ta, prefix="/v1/timing", tags=["timing"])
app.include_router(new_engines.kp, prefix="/v1/kp", tags=["kp"])
app.include_router(new_engines.cm, prefix="/v1/chomangkala-v2", tags=["numerology"])
app.include_router(new_engines.bn, prefix="/v1/bench", tags=["bench"])
app.include_router(new_engines.sar, prefix="/v1/sa-rectifier", tags=["rectification"])
app.include_router(new_engines.kk, prefix="/v1/kakshya", tags=["ashtakavarga"])
app.include_router(new_engines.br, prefix="/v1/parans", tags=["fixed-stars"])
app.include_router(new_engines.rv, prefix="/v1/reel-video", tags=["reel"])
app.include_router(new_engines.gk, prefix="/v1/genekeys", tags=["gene-keys"])
app.include_router(sky.router, prefix="/v1/sky", tags=["sky"])
app.include_router(research.router, prefix="/v1/research", tags=["research"])
