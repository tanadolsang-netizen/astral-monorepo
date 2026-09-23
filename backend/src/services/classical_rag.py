"""RAG-lite: classical public-domain interpretation corpus for chat grounding.

Corpus ships as bundled JSONL (offline). Retrieval = keyword scoring over
entries; the chat router can prepend matched passages to LLM context.

Texts (public domain):
- Ptolemy, Tetrabiblos (Ashmand 1822 tr.)
- William Lilly, Christian Astrology (1647)
- Parashara, BPHS (Santhanam-style summaries, PD translation excerpts)

Each entry: {id, source, topic_keys: [...], th, en}
"""
from __future__ import annotations

import json
from pathlib import Path

_CORPUS_PATH = Path(__file__).parent / "corpus" / "classical_corpus.jsonl"
_cache: list[dict] | None = None


def _load() -> list[dict]:
    global _cache
    if _cache is None:
        if not _CORPUS_PATH.exists():
            _cache = []
        else:
            _cache = [json.loads(line) for line in
                      _CORPUS_PATH.read_text(encoding="utf-8").splitlines()
                      if line.strip()]
    return _cache


def retrieve(query: str, top_k: int = 3,
             min_score: float = 1.0) -> list[dict]:
    """Keyword-scored retrieval. Score = number of topic-key hits."""
    q = query.lower()
    scored = []
    for entry in _load():
        score = sum(1 for k in entry.get("topic_keys", []) if k in q)
        # also match against en text body
        score += sum(1 for w in set(q.split())
                     if len(w) > 3 and w in entry.get("en", "").lower())
        if score >= min_score:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [e for _, e in scored[:top_k]]


def build_context_block(query: str, top_k: int = 3) -> str:
    """Formatted context block for the LLM prompt; '' if nothing matches."""
    hits = retrieve(query, top_k=top_k)
    if not hits:
        return ""
    lines = ["[Classical references — ground your reading in these:]"]
    for h in hits:
        lines.append(f"— {h['source']}: {h.get('en', '')[:400]}")
    return "\n".join(lines)


def corpus_stats() -> dict:
    c = _load()
    sources = {}
    for e in c:
        sources[e["source"]] = sources.get(e["source"], 0) + 1
    return {"entries": len(c), "sources": sources}
