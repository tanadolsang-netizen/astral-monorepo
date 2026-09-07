---
source_type: article
url: https://news.ycombinator.com/item?id=47656181
referenced_date: 2026-08-14
synthesized_into: "[[LLM Wiki Pattern]]"
---

# Raw source: "Show HN: LLM Wiki – Open-Source Implementation of Karpathy's LLM Wiki"

**URL:** https://news.ycombinator.com/item?id=47656181 (also see the related thread https://news.ycombinator.com/item?id=48351115, "Karpathy LLM Wiki pattern integrated into Obsidian agentic workflow")
**Retrieved:** 2026-08-14 via WebFetch + WebSearch.

## What this covers (new angle vs. existing raw sources)

The existing two raw sources on this topic are both explainer videos of the pattern itself. This is the **community-implementation angle** the task specifically asked to check for: independent open-source builds and Hacker News discussion of people actually running the pattern, not another explanation of what it is.

- Submitter (Lucas Astorian) built an open-source implementation that ingests arbitrary document formats (PDF, Word, Excel, etc.), converts them to indexed markdown, and exposes the wiki to Claude over MCP so the agent can autonomously manage/edit/link/cite pages — i.e., the MCP-server route to the pattern, vs. this vault's approach of instructions in `CLAUDE.md` plus an ordinary Claude Code session.
- A separate, larger data point found via search: Hacker News user vbarsoum applied the pattern to three business books (~155K words) at chapter-level granularity and got 210 concept pages with ~4,600 cross-references and reported "unprompted synthesis across sources" — i.e. the compounding/cross-referencing behavior Karpathy claims actually shows up in practice at a scale bigger than this vault currently has (this vault: ~19 notes).
- A named critique from HN user qaadika, worth noting directly: the bookkeeping work Karpathy proposes outsourcing to the LLM (filing, cross-referencing, summarizing) is arguably *where genuine understanding forms* for a human — i.e. automating it away may remove the part of the process that was actually valuable, not just the tedious part.

## Relevance to this vault

This is the piece [[LLM Wiki Pattern]] doesn't currently have: evidence the pattern holds up at scale (vbarsoum's 210-page/4,600-cross-reference result) beyond the toy demos in the two video sources, plus a substantive counter-argument (qaadika's) that the vault's own note doesn't currently engage with. Worth a short addition under a "criticism / open question" heading rather than treating the pattern as unambiguously validated — directly actionable for this vault since the human here (per `CLAUDE.md`/native memory) already does the curation/direction-setting Karpathy says is the human's remaining job, so the qaadika critique is a question of whether *that* curation role is enough, or whether writing notes by hand still matters for some kinds of learning.
