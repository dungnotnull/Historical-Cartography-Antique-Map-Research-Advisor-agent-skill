"""Shared schema builders used by every tool."""
from __future__ import annotations

from typing import Any


def _string_schema(description: str, *, enum: list[str] | None = None) -> dict[str, Any]:
    schema: dict[str, Any] = {"type": "string", "description": description}
    if enum:
        schema["enum"] = enum
    return schema


def _object_schema(
    description: str,
    properties: dict[str, Any],
    *,
    required: list[str] | None = None,
    additional_properties: bool = False,
) -> dict[str, Any]:
    return {
        "type": "object",
        "description": description,
        "properties": properties,
        "required": required or [],
        "additionalProperties": additional_properties,
    }


def _array_schema(items: dict[str, Any], *, description: str = "") -> dict[str, Any]:
    return {"type": "array", "description": description, "items": items}
