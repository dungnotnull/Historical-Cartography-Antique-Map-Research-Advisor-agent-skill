"""Shared helpers for sub-advisors.

Kept dependency-free and small so each advisor can focus on its methodology.
"""
from __future__ import annotations

import re
from typing import Any, Iterable

from ..context import SkillContext
from ..registry import get_registry


def mentions(text: str, *keywords: str) -> list[str]:
    """Return the lowercase keywords from ``keywords`` that appear in ``text``."""
    lowered = text.lower()
    return [kw for kw in keywords if kw and kw in lowered]


def any_mention(text: str, keywords: Iterable[str]) -> bool:
    return bool(mentions(text, *keywords))


def invoke_tool(name: str, arguments: dict[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
    """Invoke a registered tool by name through the registry (audited + logged)."""
    return get_registry().invoke_tool(name, arguments, ctx=ctx)


def extract_year(text: str) -> int | None:
    """Pull the first plausible 3-4 digit map year (1500-2050) from free text."""
    for match in re.finditer(r"\b(\d{3,4})\b", text):
        year = int(match.group(1))
        if 1400 <= year <= 2050:
            return year
    return None


def confidence_from(*signals: bool) -> str:
    """Map a set of boolean evidence signals to a coarse confidence label."""
    true_count = sum(1 for s in signals if s)
    if true_count >= 3:
        return "high"
    if true_count >= 1:
        return "medium"
    return "low"
