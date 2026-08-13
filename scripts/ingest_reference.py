#!/usr/bin/env python3
"""Ingest a new reference markdown file into references/ and refresh the index.

Validates that the file is a non-empty markdown file with a top-level ``#``
title, copies it into ``references/`` (or a named subfolder), and re-runs the
indexer so the knowledge-base manifest stays current.

Usage:
    python scripts/ingest_reference.py path/to/new-reference.md
    python scripts/ingest_reference.py path/to/new-reference.md --subfolder prompts
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFERENCES_DIR = PROJECT_ROOT / "references"


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a reference markdown file.")
    parser.add_argument("source", help="path to the .md file to ingest")
    parser.add_argument("--subfolder", default="", help="optional subfolder under references/")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists() or not source.is_file():
        print(f"[ingest] source not found: {source}", file=sys.stderr)
        return 2
    if source.suffix.lower() != ".md":
        print(f"[ingest] only .md files are supported", file=sys.stderr)
        return 2

    text = source.read_text(encoding="utf-8", errors="replace")
    if not text.strip():
        print("[ingest] file is empty", file=sys.stderr)
        return 2
    if not re.search(r"^#\s+.+$", text, re.MULTILINE):
        print("[ingest] file has no top-level '# title'", file=sys.stderr)
        return 2

    dest_dir = REFERENCES_DIR / args.subfolder if args.subfolder else REFERENCES_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / source.name
    if dest.exists():
        print(f"[ingest] destination already exists: {dest.relative_to(PROJECT_ROOT)}", file=sys.stderr)
        return 2
    shutil.copy2(source, dest)
    print(f"[ingest] copied -> {dest.relative_to(PROJECT_ROOT)}")

    # Re-index.
    seed = PROJECT_ROOT / "scripts" / "seed_knowledge_base.py"
    subprocess.check_call([sys.executable, str(seed)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
