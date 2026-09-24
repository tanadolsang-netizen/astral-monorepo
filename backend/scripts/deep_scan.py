"""Deep code scan: feed every backend source file to local Qwen3 for analysis.

Writes per-file results to scan_results/ (resumable), then aggregates into
FULL_CODE_ANALYSIS.md. Skips files already scanned (resume support).
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

BACKEND = Path("C:/AI/backend")
SRC = BACKEND / "src"
OUT_DIR = BACKEND / "scan_results"
OUT_DIR.mkdir(exist_ok=True)

OLLAMA = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen3-8b-uc:latest"

PROMPT = """/no_think
You are a senior code auditor. Analyze this Python file from an astrology backend (FastAPI).

Report format (be terse, max 200 words):
BUGS: real logic errors (wrong math, wrong types, off-by-one, race conditions)
DEAD: unused imports/functions/vars
RISK: security or data-loss risks
SMELL: design issues worth refactoring
OK: if file is clean, say "CLEAN" and one line why

File: {path} ({lines} lines)

```python
{code}
```"""


def scan_one(py: Path) -> dict:
    out_file = OUT_DIR / (str(py.relative_to(BACKEND)).replace("\\", "_").replace("/", "_") + ".json")
    if out_file.exists():
        data = json.loads(out_file.read_text(encoding="utf-8"))
        if data.get("analysis", "").strip():  # only trust non-empty cached results
            return {"path": str(py), "cached": True}
        out_file.unlink()  # empty/stale result → rescan

    code = py.read_text(encoding="utf-8", errors="replace")
    if len(code) > 60_000:  # cap ~60KB per file
        code = code[:60_000] + "\n# ... TRUNCATED ..."
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT.format(path=py, lines=code.count(chr(10)) + 1, code=code)}],
        "max_tokens": 2500,  # thinking model: leave room for reasoning + content
        "temperature": 0.2,
    }
    for attempt in range(3):
        try:
            r = requests.post(OLLAMA, json=payload, timeout=300)
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            out_file.write_text(json.dumps({"path": str(py), "analysis": content}, ensure_ascii=False), encoding="utf-8")
            return {"path": str(py), "ok": True}
        except Exception as e:
            if attempt == 2:
                out_file.write_text(json.dumps({"path": str(py), "error": str(e)}, ensure_ascii=False), encoding="utf-8")
                return {"path": str(py), "error": str(e)}
            time.sleep(3 * (attempt + 1))
    return {"path": str(py), "error": "unreachable"}


def main() -> None:
    files = sorted(SRC.rglob("*.py"))
    files = [f for f in files if "__pycache__" not in str(f)]
    print(f"Scanning {len(files)} files", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=2) as ex:  # 2 concurrent: 8B model on one GPU
        for res in ex.map(scan_one, files):
            done += 1
            status = "cached" if res.get("cached") else ("ok" if res.get("ok") else "ERR " + res.get("error", "")[:60])
            print(f"[{done}/{len(files)}] {status} {Path(res['path']).name}", flush=True)

    # Aggregate
    results = []
    for jf in sorted(OUT_DIR.glob("*.json")):
        results.append(json.loads(jf.read_text(encoding="utf-8")))

    md = ["# FULL CODE ANALYSIS — Backend Deep Scan (Qwen3 local)", "",
          f"- Files scanned: {len(results)}",
          f"- Generated: {time.strftime('%Y-%m-%d %H:%M')}",
          f"- Model: {MODEL} (Ollama local)", ""]
    issues = 0
    for r in results:
        a = r.get("analysis", "")
        clean = "CLEAN" in a[:120].upper()
        if not clean:
            issues += 1
        md.append(f"## {r['path']}")
        md.append("")
        md.append(a.strip() or "(no output)")
        md.append("")
    md.insert(4, f"- Files with findings: {issues}")
    (BACKEND / "FULL_CODE_ANALYSIS.md").write_text("\n".join(md), encoding="utf-8")
    print(f"\nDONE: {len(results)} files, {issues} with findings → FULL_CODE_ANALYSIS.md", flush=True)


if __name__ == "__main__":
    main()
