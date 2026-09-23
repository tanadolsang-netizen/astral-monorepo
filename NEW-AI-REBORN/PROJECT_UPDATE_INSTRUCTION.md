# 🌌 ASTRAL MONOREPO — Project Update Instruction

> **Last Updated**: 2026-09-13
> **Repo**: `tanadolsang-netizen/astral-monorepo` (GitHub)
> **Live**: `http://localhost:8001` (backend) · `http://localhost:8000` (preview)
> **Status**: ✅ All systems operational

---

## 📁 Repository Structure

```
C:/AI/NEW-AI-REBORN/
├── backend/                    # FastAPI backend (Python 3.11)
│   ├── src/
│   │   ├── main.py             # Entry point, router registration, i18n endpoint
│   │   ├── routers/            # API route modules
│   │   │   ├── natal.py        # Natal chart calculation
│   │   │   ├── tarot.py        # Tarot reading endpoints
│   │   │   ├── narrative_router.py  # Narrative text generation
│   │   │   └── ...             # 20+ other routers
│   │   └── services/
│   │       ├── narrative_lang.py      # ⭐ SINGLE SOURCE OF TRUTH for all display text
│   │       ├── tarot_knowledge.py     # 78-card tarot knowledge base
│   │       └── ...             # Other services
│   ├── i18n.json               # Exported i18n data (11 sections, ~12KB)
│   └── pyproject.toml          # Dependencies (uv managed)
├── landing/                    # Static frontend
│   ├── astral-landing.html     # ⭐ Main landing page (i18n-driven)
│   ├── astral-app/index.html   # Birth chart calculator app
│   ├── astral-chart.html       # Chart visualization
│   ├── astral-legacy.html      # Backup of original landing
│   └── index.html              # Symlink to astral-landing.html
└── (root)                      # Project root
```

---

## 🔑 Key Architecture Decisions

### 1. **narrative_lang.py = Single Source of Truth**
- **ALL** display text (Thai + English) lives in `narrative_lang.py`
- Exported via `export_i18n()` → `i18n.json` (11 sections)
- Frontend **MUST NOT** hardcode any display text
- Frontend loads `i18n.json` at startup → injects via `data-i18n` attributes
- Sections: `NAV`, `HERO`, `LANDING`, `SECTION`, `BUTTONS`, `FORM`, `RESULT`, `APP`, `TAROT`, `BIRTH_FORM`, `INTRO`

- Model: `sd_xl_base_1.0.safetensors` (6.9GB)
- Upscale: `4x-UltraSharp.pth` (66MB) for 4K output

### 3. **Scroll-Driven Storytelling Camera**
- 5 keyframes: Hero (top-down) → About (angle) → Features (edge-on) → Tarot (Jupiter) → Form (Earth)
- Three.js: godrays, lens flares, sprites, hemisphere light, physical lights, sky shaders, bloom
- 3D solar system: procedural shader sun, 8 planets + Moon + Saturn rings, asteroid/Kuiper belts, 5 comets, nebula

### 4. **Backend Serves Frontend**
- `GET /` → serves `landing/astral-landing.html`
- `GET /v1/i18n` → returns full i18n JSON (cached)
- No separate frontend server needed for production

---

## 🚀 How to Run

### Backend
```bash
cd C:/AI/NEW-AI-REBORN/backend
uv run uvicorn src.main:app --host 0.0.0.0 --port 8001
```

```bash
# Already running at http://127.0.0.1:8188
```

### Preview (optional, for static testing)
```bash
cd C:/AI/NEW-AI-REBORN/landing
python -m http.server 8000
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page (i18n-driven) |
| `/v1/i18n` | GET | Full i18n JSON (all display text) |
| `/v1/natal/...` | POST | Natal chart calculation |
| `/v1/tarot/...` | POST | Tarot reading |
| `/v1/narrative/...` | POST | Narrative text generation |
| `/docs` | GET | Swagger API documentation |

---

## 📝 How to Add/Edit Display Text

### Step 1: Edit `narrative_lang.py`
```python
# In the appropriate section (e.g., LANDING), add/modify:
LANDING: dict[str, dict[str, str]] = {
    "my_new_key": {"th": "ข้อความไทย", "en": "English text"},
    # ...
}
```

### Step 2: Re-export i18n.json
```bash
cd C:/AI/NEW-AI-REBORN/backend
python -c "from src.services.narrative_lang import export_i18n; import json; json.dump(export_i18n(), open('i18n.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)"
```

### Step 3: Add `data-i18n` to HTML
```html
<h1 data-i18n="LANDING.my_new_key">ข้อความไทย (fallback)</h1>
```

### Step 4: Restart backend
```bash
pkill -f 'uv run.*uvicorn'
cd C:/AI/NEW-AI-REBORN/backend && uv run uvicorn src.main:app --host 0.0.0.0 --port 8001
```

---


### Generate Request
```bash
  -H "Content-Type: application/json" \
  -d '{"date":"1997-05-19","time":"05:45","lat":13.3611,"lon":100.9847,"name":"ณัฐ"}'
```
Response: `{"job_id":"job_xxxx","prompt":"cosmic garden..."}`

### Poll Status
```bash
```

### View Image
```
```

---

## 🃏 78-Card Tarot Generation

- **Script**: `C:/AI/generate_78_tarot_4k.py`
- **Style**: Cosmic garden (Kim Krans inspired, original art — no copyright)
- **Resolution**: 1024×1536 → 4× upscale → ~4096×6144
- **Time**: ~2-3 hours for 78 cards on RTX 5060 8GB

---

## 🌐 Deployment

### Render.com (Preferred)
- Backend serves frontend at single URL `/`
- No separate frontend service
- `render.yaml` removed (contained secrets) — deploy via dashboard

### Vercel (Not Used)
- 100MB file size limit — too restrictive
- User has account but project not deployed there

---

## 🔧 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | (not set) | LLM API key (optional) |

---

## 📊 Current State

- **Backend**: ✅ Running on port 8001
- **Landing Page**: ✅ HTTP 200, i18n injection working (51 points)
- **i18n Endpoint**: ✅ Returns 11 sections, 43+ LANDING keys
- **78-Card Generation**: ⏳ Background process (status unclear)

---

## 🚨 Known Issues / TODO

1. **78-card generation**: Background process may have completed or errored — needs verification
2. **Render deployment**: Not yet deployed — needs dashboard setup
3. **LLM integration**: `OPENROUTER_API_KEY` not set — LLM returns None
4. **Frontend hardcode check**: Only "ASTRAL" brand text remains English (acceptable)

---

## 📚 Related Paths

- **Obsidian Vault**: `C:/AI/obsidian-vault/` (git-pushed state)
- **Research Specs**: `C:/AI/research-astrology/` (01-15)
- **Command Bus**: `C:/AI/command/dispatch.py`
- **Frontend (Expo)**: `C:/AI/astral-expo/` (React Native app)
- **Hermes Agent**: `C:/Users/ADMIN/AppData/Local/hermes/`

---

## 👤 User Birth Data (Verified)

- **User**: 19 May 1997, 05:45 ICT, Chonburi
- **Partner 'Mai'**: 18 Aug 2001, 22:32 ICT, Nonthaburi
- **Asc**: Taurus (verified)
- **Saturn Return**: 26 Mar 2027
- **Jupiter-Mars**: 28 Oct 2027

---

## 🎯 Quality Standard

> **TOP 1%** — Cinematic/photorealistic, not "potato computer" game quality.
> Worth $1,000,000. Light must be realistic — no banding, no visible stripes.
> Full HD 4K output expected.

---

*This document is the single source of truth for project state and update instructions.*
*Edit this file when architecture changes.*
