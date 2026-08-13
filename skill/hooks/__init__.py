"""Lifecycle & state hooks for the skill.

Hooks subscribe to named events emitted via :meth:`SkillContext.emit`. The
bus dispatches synchronously (events are cheap and ordering matters for
state snapshots); a failing hook logs and continues so a misbehaving hook
can never break the request pipeline.
"""
from __future__ import annotations

from .lifecycle import HookBus, LifecycleLoggerHook
from .state_sync import StateSnapshotHook

__all__ = ["HookBus", "LifecycleLoggerHook", "StateSnapshotHook"]
