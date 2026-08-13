"""Schema-based tool-argument validation.

Validates the ``arguments`` passed to a tool against the tool's
``ToolSchema.parameters`` (a JSON-Schema ``object`` shape). Uses ``jsonschema``
when available, else a built-in fallback that checks ``required`` keys, enum
constraints, and basic types. Raises :class:`SchemaValidationError` on failure
so callers get a structured, auditable error rather than a silent bad call.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool
from ..errors import SchemaValidationError

try:  # pragma: no cover - exercised when jsonschema is installed
    import jsonschema  # type: ignore
    _HAVE_JSONSCHEMA = True
except Exception:  # pragma: no cover - fallback path
    _HAVE_JSONSCHEMA = False


def validate_arguments(tool: Tool, arguments: Mapping[str, Any]) -> None:
    """Validate ``arguments`` against ``tool.schema().parameters``.

    Raises :class:`SchemaValidationError` with a list of human-readable
    violations if validation fails.
    """
    schema = tool.schema().parameters
    if _HAVE_JSONSCHEMA:
        try:
            jsonschema.validate(dict(arguments), schema)
            return
        except jsonschema.ValidationError as exc:
            raise SchemaValidationError(
                f"Tool {tool.name!r} argument validation failed: {exc.message}",
                details={"tool": tool.name, "path": list(exc.absolute_path)},
            ) from exc
    _fallback_validate(tool.name, arguments, schema)


def _fallback_validate(tool_name: str, arguments: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
    errors: list[str] = []
    properties = schema.get("properties", {})
    required = schema.get("required", [])
    allowed = set(properties.keys())

    for req in required:
        if req not in arguments:
            errors.append(f"missing required argument '{req}'")

    allow_extra = schema.get("additionalProperties", False)
    if not allow_extra:
        for key in arguments:
            if key not in allowed:
                errors.append(f"unexpected argument '{key}'")

    for key, value in arguments.items():
        if key not in properties:
            continue
        subschema = properties[key]
        t = subschema.get("type")
        if t == "string" and not isinstance(value, str):
            errors.append(f"argument '{key}' must be a string, got {type(value).__name__}")
        if t == "array" and not isinstance(value, (list, tuple)):
            errors.append(f"argument '{key}' must be an array")
        if t == "object" and not isinstance(value, dict):
            errors.append(f"argument '{key}' must be an object")
        if "enum" in subschema and value not in subschema["enum"]:
            errors.append(f"argument '{key}'={value!r} not in enum {subschema['enum']}")

    if errors:
        raise SchemaValidationError(
            f"Tool {tool_name!r} argument validation failed",
            details={"tool": tool_name, "errors": errors},
        )
