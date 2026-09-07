---
title: Astral
emoji: ⭐
colorFrom: purple
colorTo: indigo
sdk: docker
app_port: 7860
tags:
  - astrology
  - fastapi
  - react
  - vite
  - astral
license: mit
pinned: false
---

# Astral — โหราศาสตร์ครบวงจร

ดูดวงชะตา, ไพ่ทาโรต์, ดูคู่ Synastry, เวดิก, มูฮูร์ตะ, AI Reading, Horary, Bazi, Transit และอีก 30+ engines

## Features
- 🌟 Natal Chart (Western + Sidereal)
- 🔮 Tarot Reading
- 💞 Synastry (ดูคู่)
- 🪐 Vedic Astrology
- ⏳ Muhurta
- 🤖 AI Reading
- 🔮 Horary
- 🐉 Bazi / Chinese Zodiac
- 📊 Transit & Progression

## API Endpoints
- `/v1/natal/compute` — Natal chart calculation
- `/v1/tarot/draw` — Tarot card drawing
- `/v1/synastry/cross-aspects` — Synastry aspects
- `/v1/vedic/chart` — Vedic chart
- `/v1/muhurta/find` — Auspicious timing
- `/v1/ai/reading` — AI-powered reading
- `/v1/horary/ask` — Horary astrology
- `/v1/bazi/pillars` — Four Pillars
- `/v1/chinese/zodiac` — Chinese zodiac
- `/v1/transit/current` — Current transits
- `/ready` — Health check

## Tech Stack
- **Backend:** FastAPI + Kerykeion + PyEphem + Swiss Ephemeris
- **Frontend:** React + Vite + Pure CSS animations
- **Deploy:** Hugging Face Spaces (Docker)
