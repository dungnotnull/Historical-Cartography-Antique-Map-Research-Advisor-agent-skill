"""Skill registry: registration, resolution, execution, validation.

The registry is the single source of truth for which sub-advisors, tools and
hooks are available. It enforces uniqueness of names/ids, validates that every
registered component satisfies its base-class contract, and offers resolution
helpers (by id, by keyword match) used by the router.

Design notes
------------
* Components are **instances**, not classes, so they can carry their own
  state/reference data when needed (e.g. a tool with a loaded lookup table).
* The registry is a process-wide singleton via :func:`get_registry`, but a
  fresh :class:`SkillRegistry` can be constructed for tests.
* Registration is idempotent on name; re-registering the same name replaces
  the component (useful for hot-reloading references in dev).
"""
from __future__ import annotations

from threading import RLock
from typing import Any

from .base import Hook, SubAdvisor, Tool
from .errors import RoutingError, ToolNotFoundError


class SkillRegistry:
    """In-memory registry of sub-advisors, tools and hooks."""

    def __init__(self) -> None:
        self._advisors: dict[str, SubAdvisor] = {}
        self._tools: dict[str, Tool] = {}
        self._hooks: list[Hook] = []
        self._lock = RLock()

    # -- registration -----------------------------------------------------

    def register_advisor(self, advisor: SubAdvisor) -> SubAdvisor:
        if not isinstance(advisor, SubAdvisor):
            raise TypeError("advisor must be a SubAdvisor instance.")
        if not advisor.id:
            raise ValueError("Advisor must define a non-empty 'id'.")
        with self._lock:
            self._advisors[advisor.id] = advisor
        return advisor

    def register_tool(self, tool: Tool) -> Tool:
        if not isinstance(tool, Tool):
            raise TypeError("tool must be a Tool instance.")
        if not tool.name:
            raise ValueError("Tool must define a non-empty 'name'.")
        with self._lock:
            self._tools[tool.name] = tool
        return tool

    def register_hook(self, hook: Hook) -> Hook:
        if not isinstance(hook, Hook):
            raise TypeError("hook must be a Hook instance.")
        if not hook.name:
            raise ValueError("Hook must define a non-empty 'name'.")
        with self._lock:
            self._hooks.append(hook)
        return hook

    # -- resolution -------------------------------------------------------

    def advisors(self) -> list[SubAdvisor]:
        with self._lock:
            return list(self._advisors.values())

    def advisor(self, advisor_id: str) -> SubAdvisor:
        try:
            return self._advisors[advisor_id]
        except KeyError as exc:
            raise RoutingError(
                f"No sub-advisor registered with id {advisor_id!r}.",
                details={"available": list(self._advisors)},
            ) from exc

    def tools(self) -> list[Tool]:
        with self._lock:
            return list(self._tools.values())

    def tool(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"No tool registered with name {name!r}.",
                details={"available": list(self._tools)},
            ) from exc

    def hooks(self) -> list[Hook]:
        with self._lock:
            return list(self._hooks)

    def hooks_for(self, event: str) -> list[Hook]:
        return [h for h in self.hooks() if not h.events or event in h.events]

    def invoke_tool(self, name: str, arguments: dict[str, Any], *, ctx: Any) -> dict[str, Any]:
        tool = self.tool(name)
        from .tools.validation import validate_arguments
        validate_arguments(tool, arguments)
        ctx.emit("tool.invoke.start", {"tool": name, "arguments": arguments})
        try:
            result = tool.run(arguments, ctx=ctx)
        except Exception as exc:
            ctx.emit("tool.invoke.error", {"tool": name, "error": str(exc)})
            raise
        ctx.emit("tool.invoke.end", {"tool": name})
        return result

    # -- inspection -------------------------------------------------------

    def describe(self) -> dict[str, Any]:
        """Return a JSON-serialisable manifest of the registry contents."""
        return {
            "advisors": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "methodologies": list(a.methodologies),
                    "keywords": list(a.keywords),
                    "references": list(a.references),
                    "tools": list(a.tools),
                }
                for a in self.advisors()
            ],
            "tools": [t.schema().to_openai_tool() for t in self.tools()],
            "hooks": [{"name": h.name, "events": list(h.events)} for h in self.hooks()],
        }

    def reset(self) -> None:
        """Clear all registrations (mainly for tests)."""
        with self._lock:
            self._advisors.clear()
            self._tools.clear()
            self._hooks.clear()


# ---------------------------------------------------------------------------
# Singleton + default registration
# ---------------------------------------------------------------------------


_REGISTRY: SkillRegistry | None = None
_REGISTRY_LOCK = RLock()


def get_registry() -> SkillRegistry:
    """Return the process-wide registry, populating defaults on first access."""
    global _REGISTRY
    with _REGISTRY_LOCK:
        if _REGISTRY is None:
            _REGISTRY = SkillRegistry()
            _register_defaults(_REGISTRY)
        return _REGISTRY


def _register_defaults(registry: SkillRegistry) -> None:
    """Register the default sub-advisors, tools and hooks for this skill."""
    # Local imports to avoid importing every subsystem at module import time.
    from .agents import (
        AuthenticationReferralAdvisor,
        CartobibliographyAdvisor,
        PrintTechniqueDatingAdvisor,
        ProjectionHistoryAdvisor,
        ProvenanceMaterialsAdvisor,
        ToponymyBoundaryAdvisor,
    )
    from .hooks import LifecycleLoggerHook, StateSnapshotHook
    from .tools import (
        CartobibliographicLookupTool,
        PrintTechniqueLookupTool,
        ProjectionTimelineTool,
        ToponymLookupTool,
        WatermarkLookupTool,
        MaterialAnalysisLookupTool,
    )

    # Tools first so advisors can reference them by name.
    for tool in (
        PrintTechniqueLookupTool(),
        ProjectionTimelineTool(),
        ToponymLookupTool(),
        WatermarkLookupTool(),
        CartobibliographicLookupTool(),
        MaterialAnalysisLookupTool(),
    ):
        registry.register_tool(tool)

    for advisor in (
        PrintTechniqueDatingAdvisor(),
        CartobibliographyAdvisor(),
        ProjectionHistoryAdvisor(),
        ToponymyBoundaryAdvisor(),
        ProvenanceMaterialsAdvisor(),
        AuthenticationReferralAdvisor(),
    ):
        registry.register_advisor(advisor)

    registry.register_hook(LifecycleLoggerHook())
    registry.register_hook(StateSnapshotHook())


__all__ = ["SkillRegistry", "get_registry"]


