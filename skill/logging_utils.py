"""Structured logging utilities.

Produces JSON-line logs when ``enable_structured_logging`` is on (the default),
otherwise plain text. A single module-level logger named ``hcra`` is used so
downstream services can capture it uniformly. Logs never include the raw user
prompt body — only a short hash — to avoid leaking potentially sensitive
research material into log pipelines.
"""
from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from typing import Any

_CONFIGURED = False
_LOGGER_NAME = "hcra"


def configure_logging(level: str = "INFO", *, structured: bool = True) -> logging.Logger:
    """Idempotently configure the ``hcra`` logger and return it."""
    global _CONFIGURED
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level.upper())
    # Replace handlers on reconfigure so tests can swap modes.
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    handler: logging.Handler
    if structured:
        handler = _StructuredStreamHandler(sys.stderr)
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    _CONFIGURED = True
    return logger


def get_logger() -> logging.Logger:
    logger = logging.getLogger(_LOGGER_NAME)
    if not _CONFIGURED:
        return configure_logging()
    return logger


def fingerprint(text: str, *, length: int = 12) -> str:
    """Return a short non-reversible hash of ``text`` for safe logging."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return digest[:length]


class _StructuredStreamHandler(logging.StreamHandler):
    """Emit one JSON object per log record on a single line."""

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D401 - logging API
        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Attach any structured extras the caller added via ``logger.info(..., extra=...)``.
        for key, value in record.__dict__.items():
            if key in {"args", "msg", "levelname", "levelno", "pathname", "filename",
                       "module", "exc_info", "exc_text", "stack_info", "lineno",
                       "funcName", "created", "msecs", "relativeCreated", "thread",
                       "threadName", "processName", "process", "name", "taskName"}:
                continue
            if key.startswith("_"):
                continue
            payload[key] = value
        if record.exc_info:
            payload["exc"] = self.format(record)
        try:
            self.stream.write(json.dumps(payload, default=str, ensure_ascii=False) + "\n")
            self.flush()
        except Exception:  # pragma: no cover - logging must never raise
            self.handleError(record)
