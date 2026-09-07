---
name: code-change-verification
description: 'Verify edits and subagent output before trusting them.'
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, mac, windows]
---

# Code Change Verification

## Overview

Fix attempts, subagent writes, and patch/edit tools can leave files in partial or broken states without the tool reporting a hard failure. Treat every mutation as unverified until confirmed by read-back checks.

## When to Use

- After `delegate_task` returns
- After `patch`, `write_file`, or any file mutation
- Before running downstream tests/builds
- When a test suite surfaces cascading import/syntax/runtime errors

## Rules

1. **Subagent outputs are claims, not facts.** Re-dispatch, report failure, or leave a partial result without verifying the artifact. Count the produced items/cards/modules against ground truth.
2. **Read back after writing.** Use `read_file` on the affected region before the next step. Do not trust the write tool’s success flag alone.
3. **Compile-check Python immediately.** `python -m py_compile <file>` catches partial edits, stray commas, and indentation drift fast.
4. **Patch is not infallible on Unicode/dense strings.** If `patch` cannot match, switch to a targeted `terminal` Python rewrite or a small `write_file` rather than retrying with larger quoted blocks.
5. **Fix root-cause order first.** Collection/syntax/import errors mask real behavior. Fix those before fixing assertions or behavior.
6. **Validate dataset-driven generators.** After generating names, IDs, or rows from a dataset, assert the count and a sample against the source before using those values as dict keys or route parameters.

## Quick Checks

```bash
python -m py_compile src/<file>.py
python - <<'PY'
from pathlib import Path
p = Path('src/<file>.py')
text = p.read_text(encoding='utf-8')
print('lines', text.count('\n'))
print(text[:500])
PY
```

## Static Scan for Web/Mobile Apps

For React Native / React web apps, run a static scan after every batch of UI edits
to catch common error classes before they hit runtime. See
`references/rn-static-scan-patterns.md` for the full scanner script and
astral-expo reference fixes.

Key patterns to grep for:
- **Missing imports** — component used in JSX but not in the import block
- **CJK contamination** — `[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff]` in string literals
- **Animation leaks** — `setInterval` + `Animated.loop` without proper cleanup
