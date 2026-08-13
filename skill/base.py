"""Abstract base classes for agents, tools and hooks.

These define the contracts the registry validates against. Keeping them in
one module avoids scattered ABC definitions and makes the registry code easy
to follow.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Sequence

from .context import SkillContext


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------


@dataclass
class ToolSchema:
    """JSON-Schema-ish description of a tool's arguments and output.

    ``parameters`` follows the JSON-Schema ``object`` shape so it can be
    validated with :func:`scripts.validate_schemas` and surfaced to an LLM
    as a function/tool definition.
    """

    name: str
    description: str
    parameters: dict[str, Any]
    output: dict[str, Any]

    def to_openai_tool(self) -> dict[str, Any]:
        """Render as an OpenAI/Anthropic-style tool/function definition."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
            "output_schema": self.output,
        }


class Tool(ABC):
    """Executable tool with a schema and a pure-Python handler."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def schema(self) -> ToolSchema:
        """Return the static JSON-schema description of this tool."""

    @abstractmethod
    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        """Execute the tool and return a JSON-serialisable result dict."""


# ---------------------------------------------------------------------------
# Hooks
# ---------------------------------------------------------------------------


HookCallable = Callable[[str, dict[str, Any], SkillContext], None]


class Hook(ABC):
    """A hook subscribes to named events and runs side-effects."""

    name: str = ""
    events: tuple[str, ...] = ()

    @abstractmethod
    def handle(self, event: str, payload: dict[str, Any], *, ctx: SkillContext) -> None:
        ...


# ---------------------------------------------------------------------------
# Agents / sub-advisors
# ---------------------------------------------------------------------------


@dataclass
class AdvisorResult:
    """Structured output produced by a sub-advisor."""

    advisor: str
    methodology: str
    summary: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    confidence: str = "medium"  # low | medium | high
    requires_professional_referral: bool = False
    authentication_triggers: list[str] = field(default_factory=list)
    references_used: list[str] = field(default_factory=list)
    tools_invoked: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "advisor": self.advisor,
            "methodology": self.methodology,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "findings": list(self.findings),
            "confidence": self.confidence,
            "requires_professional_referral": self.requires_professional_referral,
            "authentication_triggers": list(self.authentication_triggers),
            "references_used": list(self.references_used),
            "tools_invoked": list(self.tools_invoked),
            "notes": list(self.notes),
        }


class SubAdvisor(ABC):
    """A specialised sub-advisor invoked by the chain-of-thought router."""

    id: str = ""
    name: str = ""
    description: str = ""
    methodologies: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()

    @abstractmethod
    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        """Produce a structured :class:`AdvisorResult` for ``prompt``."""

    def match_score(self, prompt: str) -> int:
        """Heuristic relevance score in ``[0, 100]``; used by the router fallback."""
        lowered = prompt.lower()
        hits = sum(1 for kw in self.keywords if kw in lowered)
        return min(100, hits * 25)


__all__ = [
    "ToolSchema",
    "Tool",
    "Hook",
    "HookCallable",
    "SubAdvisor",
    "AdvisorResult",
]
