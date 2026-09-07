# React Native Static Scan Patterns — astral-expo QA

Quick static scanner for React Native apps that catches common error classes
without running the app. Derived from the 2026-09-05 QA pass on astral-expo.

## What it catches

1. **Missing `TextInput` import** — the #1 crash cause in this app. Every screen
   using `<TextInput>` must have `TextInput` in its react-native import block.
   Scan: if `TextInput` appears in the file body but NOT in any of the first 5
   lines (where imports live), it's a crash waiting to happen.

2. **CJK characters in Thai/English text** — copy-paste contamination from
   Chinese/Japanese sources. Regex: `[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]`.
   Found in: i18n.js, ChatScreen.js, ChartInterpretationScreen.js, ThaiScreen.js.

3. **`setInterval` + `Animated.loop` memory leak** — a pattern where
   `Animated.loop` animations are wrapped in a `setInterval` that restarts them
   every N ms. The interval never gets cleared properly and compounds the
   animation count. Fix: call `.start()` once in `useEffect`, stop in cleanup.

## Scanner (drop into terminal)

```python
import re, os

def scan_rn_app(src_dir="src"):
    issues = []
    for root, _, files in os.walk(src_dir):
        for f in files:
            if not f.endswith((".js", ".tsx", ".ts")):
                continue
            path = os.path.join(root, f)
            c = open(path, encoding="utf-8").read()
            # Missing TextInput import
            if "TextInput" in c:
                head = " ".join(c.split("\n")[:5])
                if "TextInput" not in head:
                    issues.append((path, "CRITICAL: TextInput used but not imported"))
            # CJK contamination
            for i, line in enumerate(c.split("\n"), 1):
                cjk = re.findall(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]', line)
                if cjk:
                    issues.append((path, f"ERROR L{i}: CJK {cjk[:3]}"))
            # setInterval + Animated memory leak
            if "setInterval" in c and "Animated" in c:
                issues.append((path, "PERF: setInterval + Animated likely leak"))
    return issues
```

## Usage notes

- Run after every `patch`/`write_file` batch and before committing.
- The CJK regex is intentionally broad — it catches ALL CJK including chars
  that might legitimately appear in comments or test fixtures. Review each hit.
- The TextInput check uses the first 5 lines as the import window; adjust if
  your files use multi-line imports or different import organization.

## Reference fixes (2026-09-05)

| File | Error | Fix |
|------|-------|-----|
| `src/screens/NatalScreen.js` | Missing TextInput import | Add `TextInput` to import |
| `src/screens/ChatScreen.js` | Missing TextInput import + CJK | Fix import + remove CJK |
| `src/screens/ChartInterpretationScreen.js` | CJK 本質 | Remove CJK |
| `src/screens/ThaiScreen.js` | CJK 结构 | Remove CJK |
| `src/i18n.js` | CJK 结构 (×2) | Replace with `วันเวลาและโหราศาสตร์` |
| `src/components/Starfield.tsx` | setInterval + 800 Animated | Remove setInterval, start once |
