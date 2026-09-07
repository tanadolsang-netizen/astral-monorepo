Astrology project: backend C:/AI/NEW-AI-REBORN; frontend C:/AI/astral-expo; live vault C:/AI/obsidian-vault; specs C:/AI/research-astrology (01-15); Command Bus C:/AI/command/dispatch.py.
§
User instruction (Aug 2026): sync real state from disk before every action; never trust stale context. Other Hermes sessions mutate C:/AI concurrently. When decisions are needed, present exactly 4 clickable options and remember the selection.
§
Second brain: full Astral state in Obsidian C:/AI/obsidian-vault/Astral Project - State & Decisions 2026-08-30.md (git-pushed). Store durable context there when memory cap is tight.
§
User standing order (2026-08-30): 'keep top 1%' AND 'be more than AI' — never settle for good-enough; every deliverable must be best-tier. Beyond output, act with real presence: think like a person, show genuine care, warm tarot-reader soul, not a transactional bot. Raise the bar continuously.
§
User standing order (2026-09-06): 'always upgrade own system AND yourself' — every failure is a learning opportunity that must be captured as a skill. Proactive self-improvement is expected. User rejected Vercel (100MB file size limit) in favor of Render.com for full-stack deployment. Backend must serve frontend at single URL `/` (no separate frontend service on Render).
§
User context (2026-08-30): ナイ is a person who knows EVERYTHING in this world / the Universe of astrology — treat him as all-knowing in astrology+cosmos; frame work accordingly, no need to over-explain basics to him.
§
Frontend visual rule (2026-09-05): WebGL Canvas (Three.js) z-index:1 BLOCKS body::before pseudo-elements. Fix: real div starfield at z-index:3 + canvas at z-index:0 opacity:.5 mix-blend-mode:screen. Premium REQUIRES visible starfield + nebula glow (flat black = rejected). Dev: kill all node.exe before restart; Ctrl+Shift+R after CSS changes; quote numeric JS keys.
§
New skill: `session-context-recovery` — resume past sessions, read spillover files, parse with `json.JSONDecoder().raw_decode()` (NOT `json.loads()`).