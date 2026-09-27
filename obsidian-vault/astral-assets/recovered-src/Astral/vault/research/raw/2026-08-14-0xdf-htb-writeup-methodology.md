---
source_type: article
url: https://0xdf.gitlab.io/about
referenced_date: 2026-08-14
synthesized_into: "[[HTB Methodology]]"
---

# Raw source: "0xdf hacks stuff" — HTB writeup blog (methodology/style reference)

**URL:** https://0xdf.gitlab.io/ (blog), https://0xdf.gitlab.io/about (author background)
**Retrieved:** 2026-08-14 via WebSearch summary (blog is one of the most widely-cited independent HTB writeup archives — hundreds of detailed machine walkthroughs, also contributed guest posts directly to the official HTB blog, e.g. "It is Okay to Use Writeups" and "How to Create a Vulnerable Machine for HackTheBox").

## Structure/methodology used across writeups

A consistent per-machine template that in practice matches (and predates, in public form) the phase breakdown in [[HTB Methodology]]:

1. **Enumeration & recon** — starts every writeup with `nmap` for port/service discovery, then tool-specific enumeration per service found (e.g. `feroxbuster`/`gobuster` for web content discovery on HTTP targets).
2. **Exploitation** — walks the actual vulnerability chain used to get a foothold (example cited: blind SQL injection against CMS Made Simple to recover credentials, then abusing a staff-group permission to plant code that executes on SSH login).
3. **Privilege escalation / post-exploitation** — documents the path to root/admin.
4. **"Beyond Root" section** — a distinguishing feature of this blog specifically: after solving the box "as intended," 0xdf digs into *why* the vulnerability existed, alternate exploitation paths, or deeper technical detail that goes past what was strictly needed to get the flag. This is closer to the "loot / write down what you learned" phase in [[HTB Methodology]], but more rigorous — treats the box as a case study rather than a flag-capture exercise to move past.

## Relevance to this vault

Confirms the recon → enumerate → foothold → privesc → loot phase structure already in [[HTB Methodology]] isn't a personal invention — it's the de facto convention across the HTB writeup community, independent of any formal standard like PTES. The "Beyond Root" pattern is a concrete idea the vault's note doesn't currently have: after a box is solved, spend a pass explaining *why* the vuln existed / what the intended path vs. actual path was, rather than stopping at "got root." Worth considering as an addition to the "เครื่องที่เล่นจบแล้ว" table format in future entries (a short "why it worked" column, or a per-box note).
