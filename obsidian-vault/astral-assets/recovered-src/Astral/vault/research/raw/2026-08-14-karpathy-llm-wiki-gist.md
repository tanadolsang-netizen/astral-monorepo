---
source_type: article
url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
referenced_date: 2026-08-14
synthesized_into: "[[LLM Wiki Pattern]]"
---

# Raw source: Andrej Karpathy's original "LLM Wiki" gist (primary source)

**URL:** https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
**Retrieved:** 2026-08-14 via WebFetch.

## Why this is a genuinely new archive, not a duplicate

The two existing raw sources on this topic (`raw/2026-08-12-llm-wiki-pattern-walkthrough.md`, `raw/2026-08-13-karpathy-llm-wiki-teachers-tech.md`) are both **secondary** — third-party YouTube walkthroughs describing the pattern. Neither is the primary text itself. This is Karpathy's actual gist, read directly.

## Core content (matches what the two video sources already captured, confirming their accuracy)

- Central line: **"the wiki is a persistent, compounding artifact"** — replaces RAG's re-derive-every-query model with build-once-then-maintain.
- **Three-layer architecture**: raw sources (immutable, LLM reads but never modifies) → the wiki (LLM-owned markdown: entity pages, concept summaries, cross-references) → the schema (a `CLAUDE.md`-style rules document constraining the agent to be "a disciplined wiki maintainer rather than a generic chatbot").
- **Three operations**: Ingest (new source → LLM reads, extracts, updates 10-15 existing pages potentially, flags contradictions, logs it), Query (retrieve relevant pages, synthesize with citations, optionally file the analysis back as a new page), Lint (periodic health check: contradictions, stale claims, orphan pages, missing cross-references).
- **index.md / log.md**: content catalog with summaries, vs. append-only chronological operation log.
- Why it beats human-maintained wikis: **"LLMs don't get bored, don't forget to update a cross-reference, and can touch 15 files in one pass."**

## New detail not present in the two existing raw sources

- Karpathy explicitly calls the pattern **"intentionally abstract"** — implementation specifics are left to the reader's domain/preferences, which is a partial explanation for why two independent YouTube creators (and this vault) each converged on slightly different concrete folder layouts while agreeing on the same core three-layer model.
- Comment-thread edge cases the gist itself (or its discussion) surfaces, not covered by the two video summaries: **wikis citing themselves at scale (~1000+ files)** becoming a real failure mode, the need for a **human review gate** so AI-generated contradictions don't quietly become "what the org believes," and the risk of the wiki drifting from **underlying reality changing** (e.g. code changing) without the wiki being told.

## Relevance to this vault

Confirms [[LLM Wiki Pattern]]'s synthesis is faithful to the actual primary source, not just to two derivative video explainers. The "human review gate" and "wiki drifting from reality" caveats are worth a short addition to that note's "ข้อจำกัด" section — this vault currently has no explicit review-gate step (Claude both writes and lints the wiki solo), and no mechanism for detecting when a synthesized note's source claim has gone stale because the *real-world thing* changed (as opposed to a newer document contradicting an older one, which the existing lint process does cover).
