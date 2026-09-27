"""Export Astral local DB to portable JSON backups under db/backups/."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

from src.integrations.local_db import _connect

OUT = Path(__file__).resolve().parent.parent / "db/backups"
OUT.mkdir(parents=True, exist_ok=True)


def dump_table(name: str) -> list[dict]:
    con = _connect()
    con.row_factory = dict_factory = lambda c, r: {k: r[k] for k in c.keys()}
    rows = con.execute(f"SELECT * FROM {name}").fetchall()
    con.close()
    return rows


def export() -> dict[str, Path]:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    paths: dict[str, Path] = {}
    for table in ["profiles", "charts", "memory", "research_corpus", "sessions"]:
        rows = dump_table(table)
        out = OUT / f"{table}_{stamp}.json"
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        paths[table] = out
    print("exported:", [str(v) for v in paths.values()])
    return paths


if __name__ == "__main__":
    export()
