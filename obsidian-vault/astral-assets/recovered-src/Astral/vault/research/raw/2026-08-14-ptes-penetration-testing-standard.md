---
source_type: article
url: https://kirkpatrickprice.com/blog/stages-of-penetration-testing-according-to-ptes/
referenced_date: 2026-08-14
synthesized_into: "[[HTB Methodology]]"
---

# Raw source: "The 7 Stages of Penetration Testing According to PTES" — KirkpatrickPrice

**URL:** https://kirkpatrickprice.com/blog/stages-of-penetration-testing-according-to-ptes/
**Retrieved:** 2026-08-14 via WebFetch (cross-checked against the PTES technical standard itself at pentest-standard.org, which was unreachable at fetch time — content matches other independent summaries of PTES).

## What PTES is

The Penetration Testing Execution Standard (PTES) — a methodology developed and maintained by a group of information security practitioners, used as a baseline framework for structuring a professional penetration test end to end (not tool-specific; a process framework). Referenced by compliance regimes like PCI DSS, HIPAA, ISO 27001 as an accepted testing methodology.

## The 7 stages

1. **Pre-Engagement Interactions** — scope, rules of engagement, timelines, legal/compliance sign-off agreed before any testing starts; testers assemble the tools/OS/software needed for the agreed scope.
2. **Intelligence Gathering (recon)** — client-provided info plus tester-collected OSINT/footprinting on the target org, systems, infrastructure (passive and active).
3. **Threat Modeling** — prioritize where to focus based on business assets, business processes, and the capabilities of relevant threat communities — not just "scan everything equally."
4. **Vulnerability Analysis** — identify, validate, and assess the security risk of discovered flaws (distinguishes "found a scanner hit" from "confirmed this is real and exploitable").
5. **Exploitation** — attempt to breach the weak points identified above, confirming impact rather than just theoretical risk.
6. **Post-Exploitation** — once inside, assess the value of the compromised asset for further access (lateral movement, data of interest, persistence) — this is the closest formal analogue to HTB's "privesc" phase, generalized beyond just privilege escalation.
7. **Reporting** — both an executive-level report (business risk, non-technical) and a technical report (methodology used, vulnerabilities found, remediation) — the deliverable that turns the engagement into something actionable for the client.

## Relevance to this vault

Maps closely onto the 5-phase workflow in [[HTB Methodology]] (Recon → Enumerate → Foothold → Privesc → Loot), but PTES is the formal/professional-engagement superset: it adds two phases the personal-CTF note doesn't need (Pre-Engagement — irrelevant when there's no client — and Threat Modeling as an explicit prioritization step before diving in), and splits "Loot" conceptually across Post-Exploitation + Reporting. Confirms the personal note's phase structure isn't ad hoc — it's a compressed, CTF-appropriate version of an industry-standard process, missing only the parts that don't apply outside a real client engagement (scoping, legal sign-off, formal write-up-for-a-client reporting).
