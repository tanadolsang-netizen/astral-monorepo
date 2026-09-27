# Astral Backend
Offline astrology backend for the Astra-competitive app. Powered by skyfield ephemeris + multi-branch knowledge base.

## Local setup
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload
```
