#!/usr/bin/env python3
"""Interactive demo CLI for the Historical Cartography Research Advisor.

Runs the router end-to-end and prints the aggregated report as formatted
JSON. Useful for smoke-testing the skill without a model provider.

Usage:
    python scripts/demo_cli.py "your map-research question"
    python scripts/demo_cli.py                 # runs a built-in example prompt
    python scripts/demo_cli.py --pretty "..."  # indented JSON (default)
    python scripts/demo_cli.py --compact "..."
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXAMPLE_PROMPT = (
    "I have a copper-engraved map with a visible platemark, using the Mercator "
    "projection, labelled Constantinople, on paper with a posthorn watermark. "
    "It appears to be by Blaeu. Is it genuine and what is it worth?"
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo CLI for the skill.")
    parser.add_argument("prompt", nargs="?", default=EXAMPLE_PROMPT, help="map-research question")
    parser.add_argument("--compact", action="store_true", help="compact JSON output")
    args = parser.parse_args()

    from skill.router import HistoricalCartographyRouter

    router = HistoricalCartographyRouter()
    report = router.execute(args.prompt)
    dump = json.dumps(report.to_dict(), ensure_ascii=False, indent=None if args.compact else 2)
    print(dump)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

