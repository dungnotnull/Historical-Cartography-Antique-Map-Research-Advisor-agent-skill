"""State synchronisation hook.

Captures a rolling snapshot of the per-request ``ctx.state`` at key events
and persists a small JSON summary under ``Settings.paths.state_dir``. This
gives downstream tooling (and the user) an auditable trail of intermediate
advisor state without re-running the pipeline.

It deliberately only snapshots at a small whitelist of events to avoid
writing a file on every emit.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from ..base import Hook
from ..context import SkillContext
from ..logging_utils import get_logger


_SNAPSHOT_EVENTS = {"advisor.end", "router.decision", "request.end"}


class StateSnapshotHook(Hook):
    name = "state_snapshot"
    events = tuple(_SNAPSHOT_EVENTS)

    def __init__(self, state_dir: Path | None = None) -> None:
        self._log = get_logger()
        self._state_dir = state_dir

    def _resolve_dir(self, ctx: SkillContext) -> Path:
        return self._state_dir or ctx.settings.paths.state_dir

    def handle(self, event: str, payload: dict[str, Any], *, ctx: SkillContext) -> None:
        if event not in _SNAPSHOT_EVENTS:
            return
        target_dir = self._resolve_dir(ctx)
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            snapshot = {
                "event": event,
                "request_id": ctx.request_id,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "state": ctx.state,
                "payload": payload,
            }
            path = target_dir / f"{ctx.request_id}.jsonl"
            with path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(snapshot, default=str, ensure_ascii=False) + "\n")
        except Exception as exc:  # pragma: no cover - defensive
            self._log.warning(
                "state_snapshot.error",
                extra={"request_id": ctx.request_id, "error": str(exc)},
            )
