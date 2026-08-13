#!/usr/bin/env python3
"""Local setup routine for the Historical Cartography Research Advisor.

Creates the runtime state directory, validates that the Python package
imports, prints the effective configuration, and (optionally) bootstraps a
virtualenv and installs declared dependencies.

Usage:
    python scripts/setup_env.py            # check + state dirs + import smoke test
    python scripts/setup_env.py --install  # also create venv and pip install -r requirements.txt
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Local setup for the skill.")
    parser.add_argument("--install", action="store_true", help="create venv and install requirements.txt")
    parser.add_argument("--venv", default=".venv", help="venv directory name (default: .venv)")
    args = parser.parse_args()

    print("[setup] project root:", PROJECT_ROOT)

    # 1. Ensure runtime state dirs.
    from config import load_settings

    settings = load_settings()
    settings.paths.ensure_runtime_dirs()
    print("[setup] state dir ready:", settings.paths.state_dir)

    # 2. Import smoke test.
    try:
        from skill.registry import get_registry  # noqa: F401
        from skill.router import HistoricalCartographyRouter  # noqa: F401

        registry = get_registry()
        print(f"[setup] registry OK: {len(registry.advisors())} advisors, "
              f"{len(registry.tools())} tools, {len(registry.hooks())} hooks")
    except Exception as exc:
        print(f"[setup] FAILED import smoke test: {exc}", file=sys.stderr)
        return 2

    # 3. Print effective config.
    print(f"[setup] environment={settings.environment} log_level={settings.log_level}")
    print(f"[setup] llm.provider={settings.llm.provider} model={settings.llm.model}")
    print(f"[setup] flags.strict_disclaimer_mode={settings.flags.strict_disclaimer_mode}")

    # 4. Optional venv + install.
    if args.install:
        venv_path = PROJECT_ROOT / args.venv
        print("[setup] creating venv at", venv_path)
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        pip = str(venv_path / ("Scripts" / "pip.exe" if os.name == "nt" else "bin" / "pip"))
        reqs = PROJECT_ROOT / "requirements.txt"
        if reqs.exists():
            print("[setup] installing", reqs)
            subprocess.check_call([pip, "install", "-r", str(reqs)])
        else:
            print("[setup] no requirements.txt; skipping install")

    print("[setup] done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
