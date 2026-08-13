#!/usr/bin/env python3
"""Seed the local knowledge-base index from the references/ directory.

Builds a JSON index of every reference markdown file (path, title, size,
methodology tags) under ``references/`` and writes it to
``.skill_state/knowledge_base_index.json``. The index is consumed by
ingestion tooling and can be used as a lightweight RAG grounding manifest.

Usage:
    python scripts/seed_knowledge_base.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = PROJECT_ROOT / "references"
STATE_DIR = PROJECT_ROOT / ".skill_state"
INDEX_PATH = STATE_DIR / "knowledge_base_index.json"


def extract_title(text: str) -> str:
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def extract_tags(text: str) -> list[str]:
    tags: list[str] = []
    for m in re.finditer(r"methodolog(?:y|ies)[:\-]\s*([^\n]+)", text, re.IGNORECASE):
        for piece in re.split(r"[;,/]", m.group(1)):
            piece = piece.strip().strip(".")
            if piece and piece.lower() not in {"none"}:
                tags.append(piece)
    return tags


def main() -> int:
    if not REFERENCES_DIR.exists():
        print("[seed] references/ not found", file=sys.stderr)
        return 2
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for md in sorted(REFERENCES_DIR.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        entries.append({
            "path": str(md.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "title": extract_title(text),
            "size_bytes": md.stat().st_size,
            "tags": extract_tags(text),
        })

    INDEX_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[seed] indexed {len(entries)} reference file(s) -> {INDEX_PATH.relative_to(PROJECT_ROOT)}")
    for e in entries:
        print(f"  - {e['path']}  ({e['size_bytes']} bytes)  tags={e['tags']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
