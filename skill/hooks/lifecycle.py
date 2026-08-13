"""Hook bus + lifecycle logging hook."""
from __future__ import annotations

from typing import Any

from ..base import Hook
from ..context import SkillContext
from ..logging_utils import get_logger


class HookBus:
    """Synchronous event bus backed by the registry's hooks.

    The bus is intentionally tiny: it looks up hooks that subscribe to the
    emitted event (or to all events when ``events`` is empty) and invokes
    them in registration order. Exceptions are isolated per hook.
    """

    def __init__(self, *, enabled: bool = True) -> None:
        self.enabled = enabled
        self._log = get_logger()
        self._emitted: list[tuple[str, dict[str, Any]]] = []

    def emit(self, event: str, payload: dict[str, Any], *, ctx: SkillContext) -> None:
        if not self.enabled:
            return
        self._emitted.append((event, payload))
        # Lazy registry lookup to avoid import cycles.
        from ..registry import get_registry

        for hook in get_registry().hooks_for(event):
            try:
                hook.handle(event, payload, ctx=ctx)
            except Exception as exc:  # pragma: no cover - defensive
                self._log.warning(
                    "hook.error",
                    extra={"hook": hook.name, "event": event, "error": str(exc)},
                )

    def history(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self._emitted)


class LifecycleLoggerHook(Hook):
    name = "lifecycle_logger"
    events: tuple[str, ...] = ()  # subscribe to all events

    def __init__(self) -> None:
        self._log = get_logger()

    def handle(self, event: str, payload: dict[str, Any], *, ctx: SkillContext) -> None:
        self._log.debug(
            "lifecycle.event",
            extra={"event": event, "request_id": ctx.request_id, "payload": payload},
        )
