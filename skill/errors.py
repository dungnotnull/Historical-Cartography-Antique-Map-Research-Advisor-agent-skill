"""Domain error hierarchy for the skill.

All errors derive from :class:`SkillError` so callers can catch the whole
family with a single ``except``. Errors carry structured ``details`` so they
can be surfaced to users and logged as JSON without string-parsing.
"""
from __future__ import annotations

from typing import Any, Mapping


class SkillError(Exception):
    """Base class for all skill-raised errors."""

    code: str = "skill_error"

    def __init__(self, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details: dict[str, Any] = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "details": self.details}


class ConfigError(SkillError):
    code = "config_error"


class RoutingError(SkillError):
    code = "routing_error"


class ToolExecutionError(SkillError):
    code = "tool_execution_error"


class ToolNotFoundError(ToolExecutionError):
    code = "tool_not_found"


class SchemaValidationError(SkillError):
    code = "schema_validation_error"


class LLMError(SkillError):
    code = "llm_error"


class DisclaimerViolation(SkillError):
    """Raised when output would violate the standing disclaimer policy."""

    code = "disclaimer_violation"


class ReferenceMissingError(SkillError):
    code = "reference_missing"
