# Astral Backend — Security Audit Report

**Date:** 2025-06-23  
**Scope:** `C:/AI/NEW-AI-REBORN/backend/src/`  
**Auditor:** Automated review (Hermes subagent)

---

## Executive Summary

The backend delegates authentication to **Supabase Auth** (not custom JWT), which is a sound architectural choice. SQL injection risk is low — all queries use parameterized placeholders. However, several endpoints in `ai_router.py` have **IDOR vulnerabilities** that allow any unauthenticated caller to read another user's events, correlations, preferences, and feedback stats by guessing or enumerating `user_id` values.

Severity legend: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low | ⚪ Informational

---

## 1. Authentication & JWT

| Check | Status | Detail |
|-------|--------|--------|
| JWT secret handling | ⚪ N/A | App does not issue JWTs — Supabase Auth handles token generation and signing |
| Token expiry | ⚪ N/A | Managed by Supabase (configurable in Supabase dashboard) |
| Refresh token rotation | ⚪ N/A | Managed by Supabase |
| Password hashing (bcrypt/argon) | ⚪ N/A | Supabase Auth handles hashing internally (bcrypt with cost factor 10+) |
| Login brute-force protection | 🟢 Good | Rate limiter: 10 req/min per IP on `/v1/auth/*` |
| Signup brute-force protection | 🟢 Good | Same 10 req/min limit covers `/signup` |
| `/me` endpoint validation | 🟢 Good | Validates Bearer token via `get_current_user()` → Supabase `auth.get_user(token)` |
| Auth required on sensitive routes | 🟡 Mixed | Dashboard, memory, payments use `_require_user`. AI router endpoints do NOT (see IDOR). |

**Findings:**
- **No custom JWT implementation** — the app correctly relies on Supabase Auth. The `access_token` returned from `sign_in_with_password` is a Supabase JWT (RS256, signed by Supabase's JWKS endpoint). `get_current_user()` calls `_supabase.auth.get_user(token)` which verifies the token server-side.
- **`/me` endpoint** (auth.py:66) returns the raw token to the caller. This is standard (it echoes back the token the client already has), but the endpoint also silently returns `user=None` on failure rather than raising 401 — clients must check the response body.
- No logout/revocation endpoint — session termination is client-side (token deletion). Refresh tokens can be revoked in Supabase dashboard.

**Recommendations:**
- Consider returning 401 from `/me` when the token is invalid, so clients don't need to parse the body.
- Add an explicit `/logout` endpoint that calls `supabase.auth.sign_out()` to invalidate the refresh token server-side.

---

## 2. CORS Configuration

| Check | Status | Detail |
|-------|--------|--------|
| Origin whitelist (prod) | 🟢 Good | 3 explicit origins: `astral.onrender.com`, `astral.app`, `www.astral.app` |
| Origin whitelist (dev) | 🟢 Good | localhost on ports 3000, 5173, 8080 |
| Credentials allowed | 🟢 Good | `allow_credentials=True` needed for Bearer token auth |
| Wildcard origin | 🟢 None | No `*` in production CORS |
| Allowed methods | 🟢 Good | GET, POST, PUT, DELETE, PATCH, OPTIONS |
| Allowed headers | 🟢 Good | Authorization, Content-Type, X-Request-ID |

**Findings:**
- CORS is correctly environment-gated via the `ENV` variable.
- In production, the origin list is hardcoded — if you add a new frontend domain, it must be added to `main.py` (no runtime configuration).

**Recommendations:**
- Consider loading CORS origins from an env var (e.g., `CORS_ORIGINS=https://a.com,https://b.com`) for flexibility without code deploys.

---

## 3. Hardcoded Secrets

| Check | Status | Detail |
|-------|--------|--------|
| `sk-` patterns | 🟢 None found | |
| `password = "..."` | 🟢 None found | |
| `secret = "..."` | 🟢 None found | |
| `api_key = "..."` | 🟢 None found | |
| `.env` usage | 🟢 Good | `load_dotenv()` in `main.py`, `supabase_client.py` |
| Service role key | 🟢 Good | `SUPABASE_SERVICE_ROLE_KEY` read from env only |
| Supabase URL | 🟢 Good | `SUPABASE_URL` read from env only |

**Findings:**
- No hardcoded secrets detected in any Python file.
- All sensitive values are loaded via `os.getenv()`.

**Recommendations:**
- Add a pre-commit hook (e.g., `detect-secrets`) to prevent accidental secret commits.

---

## 4. SQL Injection

| File | Risk | Detail |
|------|------|--------|
| `services/user_service.py` | 🟢 Low | All queries use `?` parameterized placeholders |
| `services/event_service.py` | 🟢 Low | All queries use `?` placeholders |
| `services/feedback_service.py` | 🟢 Low | All queries use `?` placeholders |
| `services/hermes_memory_service.py` | 🟢 Low | SQLite FTS query uses `?` placeholders |
| `services/chart_store.py` | 🟢 Low | Supabase client uses parameterized `.eq()`, `.insert()` |
| `integrations/supabase_client.py` | 🟢 Low | Supabase query builder (parameterized by design) |

**Findings:**
- All raw SQL queries use parameterized `?` placeholders. No f-strings or `.format()` calls in SQL contexts.
- The Supabase Python client builds parameterized queries internally.

**Recommendations:**
- None — current practice is correct. Maintain this when adding new queries.

---

## 5. IDOR (Insecure Direct Object Reference) 🔴

This is the most significant finding.

### Vulnerable Endpoints

| Endpoint | File:Line | Issue |
|----------|-----------|-------|
| `GET /v1/ai/events/{user_id}` | `ai_router.py:112` | No auth. Any caller can pass any `user_id` and retrieve that user's life events |
| `GET /v1/ai/correlations/{user_id}` | `ai_router.py:122` | No auth. Any caller can retrieve any user's transit-event correlations |
| `GET /v1/ai/preferences/{user_id}` | `ai_router.py:132` | No auth. Any caller can read any user's preferences |
| `GET /v1/ai/feedback/stats?user_id=X` | `ai_router.py:84` | No auth. Any caller can query feedback stats for any user |
| `POST /v1/ai/feedback` | `ai_router.py:66` | No auth. `user_id` is untrusted input — can submit feedback as any user |
| `POST /v1/ai/event` | `ai_router.py:93` | No auth. `user_id` is untrusted — can record events as any user |
| `POST /v1/ai/reading` | `ai_router.py:46` | No auth. `user_id` query param is optional and untrusted |

### Root Cause

The `ai_router.py` endpoints accept `user_id` as a path parameter or query parameter **without verifying that the authenticated user owns that ID**. The underlying services (`event_service.py`, `feedback_service.py`, `user_service.py`) filter by `user_id` but never compare it against the authenticated user's ID.

### Contrast with Secure Routes

The dashboard, memory, and payments routers use `_require_user` which validates the Bearer token and extracts the real `user.id`. The ai_router does not.

### Exploitation Scenario

1. Attacker knows or guesses a `user_id` (UUID or short string).
2. `GET /v1/ai/events/{victim_user_id}` returns all life events with descriptions, dates, and significance.
3. `GET /v1/ai/correlations/{victim_user_id}` reveals transit-event correlations (personal timing data).
4. No authentication token required.

### Recommendations (Priority: High)

1. **Add `_require_user` to `ai_router.py`** and compare `user.id` against the path/query `user_id` parameter. Return 403 if they don't match.
2. **Or better**: remove `user_id` from the route entirely and derive it from the authenticated user (e.g., `GET /v1/ai/events` with auth).
3. Apply the same fix to `event_service.py`, `feedback_service.py`, and `user_service.py` as defense-in-depth.

```python
# Example fix for ai_router.py
async def get_events(_: User = Depends(_require_user)):
    return event_service.get_events(_.id, category="")
```

---

## 6. Rate Limiting

| Check | Status | Detail |
|-------|--------|--------|
| Implementation | 🟢 Good | Sliding window, per-IP, in-memory |
| Auth endpoint limit | 🟢 Good | 10 req/min per IP |
| Public endpoint limit | 🟢 Good | 60 req/min per IP |
| 429 response | 🟢 Good | Includes `Retry-After` header |
| Distributed deployment | 🟡 Medium | In-memory limiter resets per-instance; ineffective if load-balanced across multiple workers |

**Recommendations:**
- For production with multiple instances, use a Redis-backed rate limiter (e.g., `slowredis` or `fastapi-limiter` with Redis backend).
- Consider stricter limits on `/v1/auth/signup` (e.g., 3/min) to prevent bulk account creation.

---

## 7. Security Headers

| Header | Value | Status |
|--------|-------|--------|
| `X-Content-Type-Options` | `nosniff` | 🟢 Good |
| `X-Frame-Options` | `DENY` | 🟢 Good |
| `Content-Security-Policy` | `default-src 'self'` | 🟢 Good |
| `X-XSS-Protection` | `1; mode=block` | 🟢 Good |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | 🟢 Good |
| `Permissions-Policy` | All sensors disabled | 🟢 Good |
| `Strict-Transport-Security` | Missing | 🟡 Medium |

**Recommendations:**
- Add `Strict-Transport-Security: max-age=31536000; includeSubDomains` in production (behind HTTPS).
- The CSP `connect-src 'self'` may block the frontend if the API and frontend are on different origins — verify the frontend can still call the API.

---

## 8. Error Handling & Information Leakage

| Check | Status | Detail |
|-------|--------|--------|
| Stack traces to client | 🟢 Good | Generic 500 messages, errors logged server-side |
| Supabase errors to client | 🟡 Medium | `payments.py:29` returns `str(exc)` to client — could leak internal config details |

**Recommendations:**
- In production, sanitize exception messages before returning to client. Use a generic "Internal error" message and log the real exception.

---

## 9. Legal Protection ⚪→🟠

| Check | Status | Detail |
|-------|--------|--------|
| Disclaimer (entertainment/educational) | 🟡 Partial | `services/caveat.py` + `disclaimers.py` define caveats, but **only appended to AI/chat responses** — not surfaced at signup, reading entry points, or on a dedicated page |
| Limitation of liability | ❌ Missing | No code, no page, no text found anywhere in project |
| Terms & Conditions page | ❌ Missing | No `terms`, `t&c`, or equivalent page in landing SPA (`astral-landing`), Expo app (`astral-expo`), or backend |
| Privacy Policy page | ❌ Missing | No privacy page in any frontend or backend directory |
| Consent / accept checkbox | ❌ Missing | No modal, checkbox, or "I agree" flow at signup, birth-data entry, or first reading |
| Birth-data sensitivity (PDPA/GDPR) | ❌ No compliance layer | Birth date/time/name + natal charts + transit events stored with no consent record, no retention policy, no delete/export endpoint |
| PDPA lawful basis / purpose | ❌ Missing | No documented lawful basis for processing; no "right to deletion" or "right to portability" mechanism |
| Data deletion endpoint | ❌ Missing | No `DELETE /v1/user/me` or similar to erase user data on demand |
| Consent log | ❌ Missing | No timestamped log of what the user agreed to and when |
| Cookie / tracking consent | ❌ Missing | No cookie banner or preference center (relevant if analytics or tracking is added later) |

### What Exists

- `services/caveat.py`: defines `CAVEAT_TH` / `CAVEAT_EN` constants — appended only to AI chat replies (`routers/chat.py:106`).
- `services/disclaimers.py`: defines `detect_refusal` + `refusal_reply` (medical/legal/financial refusal wording) — used only in chat path.
- `routers/chat.py:107`: appends disclaimer text only when an LLM is the reply source.

### What's Missing (Gap Analysis)

1. **No legal wrapper around the core astrology service** — readings, natal charts, tarot, bazi, synastry, transits, and compatibility reports contain zero client-facing disclaimer or liability text in the response payload or UI.
2. **No T&C acceptance at account creation** — Supabase Auth signup (`/v1/auth/signup`) takes only email/password; no record that the user accepted any terms.
3. **No Privacy Policy** — the app collects birth data (date, time, timezone, name), email, preferences, reading history, and payment info, but has no published policy explaining what is collected, why, how long it is kept, or with whom it is shared.
4. **No PDPA/GDPR mechanisms** — birth data is "sensitive personal data" under most frameworks; no consent record, no data retention schedule, no endpoint for data export or erasure.
5. **No consent for sensitive advice domains** — AI chat answers health/legal/finance questions with rule-based fallback; refusal logic exists but no explicit consent was obtained to process those queries.

### Recommendations (Priority: High for a Public-Facing Product)

1. **Create a Disclaimer Modal** shown on first visit (and re-shown after major updates):
   - Must state: "For entertainment and educational purposes only. Not medical, legal, or financial advice. Not a substitute for professional consultation."
   - Must require explicit "I acknowledge" click before proceeding.
   - Store acceptance timestamp + version in user profile (consent log).

2. **Create a Terms & Conditions page** (linked from signup, landing page footer, and app settings):
   - Must include limitation of liability clause (no guarantee of accuracy; no liability for decisions made based on readings).
   - Must include intellectual property notice (AI-generated interpretations are not professional advice).
   - Must include governing law clause (Thailand, since PDPA applies).

3. **Create a Privacy Policy page** (linked from signup, settings, and footer):
   - Must disclose what personal data is collected (email, birth date/time, name, location, reading history, payment info).
   - Must state the purpose (astrology readings, personalization, subscription management).
   - Must state retention period (e.g., 12 months after account deletion).
   - Must state third-party processors (Supabase, Stripe, AI providers like Groq/Pollinations — especially if data is sent to external AI APIs).
   - Must provide contact for data requests.

4. **Add PDPA compliance endpoints**:
   - `GET /v1/user/data-export` — returns all user data in machine-readable format (JSON).
   - `DELETE /v1/user/me` — erases all user data with confirmation (right to erasure).
   - Store consent log (`consents` table): `{user_id, consent_type, version, accepted_at, ip_address}`.

5. **Add consent record at signup** — extend `/v1/auth/signup` to accept `terms_accepted: bool` and `privacy_accepted: bool`; reject signup if either is false.

6. **Add disclaimer text to all reading responses** (natal chart, tarot, bazi, synastry, transit) — not just AI chat. Append a short caveat to every reading payload so it surfaces in the UI.

7. **Audit AI provider data sharing** — `routers/chat.py` sends user birth data to Groq/Pollinations. The Privacy Policy must explicitly disclose this and the user must consent to it (especially for PDPA, which requires consent for cross-border data transfer).

8. **Add data retention job** — periodic cleanup of readings, events, and charts older than N days for inactive users; document the policy.

9. **Add cookie/tracking consent** — if analytics (Google Analytics, PostHog, etc.) or ad pixels are added later, a consent banner is required under PDPA/ePrivacy.

---

## Summary Action Items

| Priority | Item |
|----------|------|
| 🔴 **Critical** | Fix IDOR in `ai_router.py` — add auth to all endpoints accepting `user_id` |
| 🟠 **High** | Sanitize exception messages in production error responses |
| 🟠 **High** | Create Disclaimer Modal (first-visit, explicit consent) |
| 🟠 **High** | Create Privacy Policy page (PDPA compliance for birth data) |
| 🟠 **High** | Add consent record at signup (terms + privacy acceptance) |
| 🟠 **High** | Add `DELETE /v1/user/me` data erasure endpoint (PDPA right to deletion) |
| 🟡 **Medium** | Create Terms & Conditions page (limitation of liability, governing law) |
| 🟡 **Medium** | Add HSTS header for production |
| 🟡 **Medium** | Move CORS origins to env var for flexibility |
| 🟡 **Medium** | Add Redis-based rate limiting for multi-instance deployments |
| 🟡 **Medium** | Add `GET /v1/user/data-export` endpoint (PDPA data portability) |
| 🟡 **Medium** | Audit AI provider data sharing — document cross-border data transfer |
| 🟢 **Low** | Add `/logout` endpoint for server-side token revocation |
| 🟢 **Low** | Add `detect-secrets` pre-commit hook |
| 🟢 **Low** | Return 401 from `/me` on invalid token instead of 200 with empty body |
| 🟢 **Low** | Add data retention job for inactive users |
| 🟢 **Low** | Add disclaimer text to all reading responses (not just AI chat) |
