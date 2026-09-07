# Worked example — ORACLE acceptance-gate report (P0 gate, 22 Aug 2026)

Structure worth copying: verdict first, then root causes ranked with file:line fix pointers, then git state, then an ordered fix sequence. Filed via `dispatch.py report ORACLE "<summary>"`; full text archived at `C:/AI/research-astrology/S3-report-P0-gate.md`.

```
Verdict: P0 gate NOT passed — 137/142 tests green, 5 failed (3 root causes)

Root causes:
1. bazi_service.py:166 typo 'ยิน' -> 'หยิน' (kills 2 BaZi tests;
   pillars themselves correct: 丁丑/乙巳/辛酉/辛卯 matches lunar-python)
2. Lichun confidence: impl returns HIGH, spec/test require MEDIUM when
   |date - Lichun| <= 7 days
3. synastry emotional_bond inverted: identical-chart 65 < opposite-chart 79
   -> inspect CAPACITY/HARMONIC tables in synastry_scoring.py
   (acceptance-standard issue: identical charts must outrank opposites)
4. OPEN QUESTION to CMD: tarot tilted_toward test expects 'earth', impl gives
   'air' — tilt basis (personal planets only? include ASC/MC?) is undefined
   in specs; needs arbitration, not a blind code fix.

Git state: Fusion Engine uncommitted (M main.py, ?? bazi_service.py,
?? synastry_scoring.py, ?? tests/test_bazi.py, ?? tests/test_synastry_score.py)

Fix order: (1) typo -> rerun -> expect 3 failures, (2) confidence rule,
(3) emotional_bond inversion, (4) arbitrate tilt basis, then single commit+push,
then ORACLE re-runs full regression as P3 live-fire.
```

Notes: evidence came from actually running `.venv/Scripts/python.exe -m pytest -q`, grepping the failing asserts, and reading the implicated source lines — never from trusting prior sessions' claims that tests were green.
