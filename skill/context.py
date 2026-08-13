"""Execution context shared by the router, sub-advisors, tools and hooks.

A :class:`SkillContext` is constructed once per user request and threaded
through the call graph. It carries:

* the loaded :class:`Settings`;
* a structured logger;
* the per-request hook emitter;
* a mutable ``state`` dict for sub-advisors to stash intermediate results
  (e.g. evidence collected by one advisor and consumed by another);
* token/turn budgets so sub-advisors can self-limit context usage.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from config import Settings, load_settings

from .logging_utils import get_logger


@dataclass
class TokenBudget:
    """Soft budget for prompt tokens consumed during a single request.

    Sub-advisors SHOULD check :meth:`remaining` before assembling large
    reference excerpts and fall back to a summary when exhausted.
    """

    limit: int = 24000
    used: int = 0

    def consume(self, n: int) -> None:
        if n < 0:
            raise ValueError("Cannot consume a negative token count.")
        self.used += n

    def remaining(self) -> int:
        return max(0, self.limit - self.used)


@dataclass
class SkillContext:
    """Per-request execution context."""

    request_id: str
    user_prompt: str
    settings: Settings = field(default_factory=load_settings)
    logger: Any = field(default=None)
    state: dict[str, Any] = field(default_factory=dict)
    token_budget: TokenBudget = field(default_factory=TokenBudget)
    started_at: float = field(default_factory=time.time)
    hook_bus: Any = field(default=None)

    def __post_init__(self) -> None:
        if self.logger is None:
            self.logger = get_logger()
        # Lazy-import to avoid a circular import with skill.hooks.
        if self.hook_bus is None:
            from .hooks import HookBus  # local import: hooks -> context would cycle

            self.hook_bus = HookBus(enabled=self.settings.flags.enable_hook_events)

    @classmethod
    def for_prompt(cls, user_prompt: str, *, settings: Settings | None = None) -> "SkillContext":
        settings = settings or load_settings()
        return cls(
            request_id=str(uuid.uuid4()),
            user_prompt=user_prompt,
            settings=settings,
        )

    def emit(self, event: str, payload: dict[str, Any] | None = None) -> None:
        """Emit a lifecycle/state event through the hook bus."""
        if self.hook_bus is not None:
            self.hook_bus.emit(event, payload or {}, ctx=self)

    def elapsed_ms(self) -> int:
        return int((time.time() - self.started_at) * 1000)
