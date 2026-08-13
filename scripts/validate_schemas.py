#!/usr/bin/env python3
"""Validate JSON schemas and the live registry manifest.

Two passes:
1. Parse every ``assets/schemas/*.json`` file as valid JSON.
2. Build a manifest from the live registry (``registry.describe()``) and
   structurally validate it against ``skill.schema.json`` and the tool/hook
   schemas, using ``jsonschema`` if installed, else a built-in fallback
   validator that checks required keys + enum constraints.

Usage:
    python scripts/validate_schemas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
SCHEMAS_DIR = PROJECT_ROOT / "assets" / "schemas"

try:
    import jsonschema  # type: ignore
    _HAVE_JSONSCHEMA = True
except Exception:
    _HAVE_JSONSCHEMA = False


def _basic_validate(instance: dict, schema: dict, path: str = "") -> list[str]:
    """Minimal fallback validator: required keys + enum + const + type checks."""
    errors: list[str] = []
    for req in schema.get("required", []):
        if req not in instance:
            errors.append(f"{path or '<root>'}: missing required key '{req}'")
    defs = schema.get("$defs", {})
    for key, subschema in schema.get("properties", {}).items():
        if key not in instance:
            continue
        value = instance[key]
        here = f"{path}.{key}" if path else key
        t = subschema.get("type")
        if t == "string" and not isinstance(value, str):
            errors.append(f"{here}: expected string, got {type(value).__name__}")
        if t == "boolean" and not isinstance(value, bool):
            errors.append(f"{here}: expected boolean")
        if t == "integer" and not isinstance(value, int):
            errors.append(f"{here}: expected integer")
        if "enum" in subschema and value not in subschema["enum"]:
            errors.append(f"{here}: {value!r} not in enum {subschema['enum']}")
        if "const" in subschema and value != subschema["const"]:
            errors.append(f"{here}: expected const {subschema['const']!r}, got {value!r}")
    return errors


def validate_instance(instance: dict, schema: dict, label: str) -> list[str]:
    if _HAVE_JSONSCHEMA:
        try:
            jsonschema.validate(instance, schema)
            return []
        except jsonschema.ValidationError as exc:
            return [f"{label}: {exc.message} (at {list(exc.absolute_path)})"]
    return _basic_validate(instance, schema, label)


def main() -> int:
    # 1. Parse every schema file.
    schemas: dict[str, dict] = {}
    failures: list[str] = []
    for jf in sorted(SCHEMAS_DIR.glob("*.json")):
        try:
            schemas[jf.stem] = json.loads(jf.read_text(encoding="utf-8"))
            print(f"[validate] schema parsed: {jf.name}")
        except json.JSONDecodeError as exc:
            failures.append(f"{jf.name}: invalid JSON: {exc}")
    if failures:
        for f in failures:
            print(f"[validate] FAIL {f}", file=sys.stderr)
        return 2

    # 2. Build live registry manifest.
    from skill.registry import get_registry

    registry = get_registry()
    manifest = {
        "name": "historical-cartography-research-advisor",
        "version": "1.0.0",
        "description": "Historical cartography & antique map research advisor skill.",
        "domain": "Historical Cartography",
        "disclaimer_required": True,
        "sub_advisors": [
            {
                "id": a.id, "name": a.name, "description": a.description,
                "methodologies": list(a.methodologies), "keywords": list(a.keywords),
                "references": list(a.references), "tools": list(a.tools),
            }
            for a in registry.advisors()
        ],
        "tools": [t.schema().to_openai_tool() for t in registry.tools()],
        "hooks": [{"name": h.name, "events": list(h.events)} for h in registry.hooks()],
        "references": [],
    }

    skill_schema = schemas.get("skill")
    if skill_schema:
        errs = validate_instance(manifest, skill_schema, "skill.manifest")
        if errs:
            failures.extend(errs)
        else:
            print("[validate] skill.manifest valid against skill.schema.json")

    # Validate each tool against tool.schema.json (input_schema/output_schema keys).
    tool_schema = schemas.get("tool")
    if tool_schema:
        # tool.schema.json uses 'input_schema'/'output_schema'; to_openai_tool already emits those.
        for tool in manifest["tools"]:
            errs = validate_instance(tool, tool_schema, f"tool.{tool.get('name')}")
            if errs:
                failures.extend(errs)
        if not any("tool." in f for f in failures):
            print(f"[validate] {len(manifest['tools'])} tool(s) valid against tool.schema.json")

    hook_schema = schemas.get("hook")
    if hook_schema:
        for hook in manifest["hooks"]:
            errs = validate_instance(hook, hook_schema, f"hook.{hook.get('name')}")
            if errs:
                failures.extend(errs)
        if not any("hook." in f for f in failures):
            print(f"[validate] {len(manifest['hooks'])} hook(s) valid against hook.schema.json")

    if failures:
        print("\n[validate] VALIDATION FAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 2
    print(f"[validate] all schemas OK (jsonschema={'yes' if _HAVE_JSONSCHEMA else 'fallback'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
