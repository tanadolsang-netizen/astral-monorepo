#!/usr/bin/env python3
"""Smoke test for narrative_gate: feed dirty sections, assert clean output."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src"))

from services.narrative_gate import apply_narrative_gate


def main() -> int:
    dirty = [
        {
            "title": "Grand Summary — May",
            "lines": [
                "cuatro palos painstakingly กับธาตุ etalon rutin",
                "Day Master:  estat分析 cross-reference future track",
            ],
        }
    ]
    cleaned = apply_narrative_gate(dirty, lang="th")
    for sec in cleaned:
        for line in sec.get("lines", []):
            assert "\x00" not in line, "null byte in output"
            assert "cuatro palos" not in line, f"artifact survived: {line}"
            assert "painstakingly" not in line, f"en artifact survived: {line}"
            assert "estat分析" not in line, f"mixed artifact survived: {line}"
    print("OK: narrative gate cleaned dirty TH input")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
