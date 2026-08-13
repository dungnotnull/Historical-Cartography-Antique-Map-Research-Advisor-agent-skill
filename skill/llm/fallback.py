"""Deterministic fallback engine.

When the LLM client returns ``None`` (no backend configured or all retries
failed), sub-advisors can still produce a structured answer using this engine,
which derives an :class:`AdvisorResult` deterministically from the advisor's
declared keywords/references/tools and any tool output already gathered.

This guarantees the skill never dead-ends: even with zero model access, the
output is structured, methodology-named, disclaimer-compliant, and auditable.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from ..registry import get_registry


class FallbackEngine:
    """Synthesises a minimal but structured result without an LLM call."""

    def __init__(self, advisor: SubAdvisor) -> None:
        self.advisor = advisor

    def synthesize(self, prompt: str, *, ctx: SkillContext, tool_outputs: Mapping[str, dict[str, Any]] | None = None) -> AdvisorResult:
        tool_outputs = tool_outputs or {}
        matched_keywords = [kw for kw in self.advisor.keywords if kw in prompt.lower()]

        evidence: list[dict[str, Any]] = []
        for tool_name, output in tool_outputs.items():
            evidence.append({
                "type": "tool_output",
                "tool": tool_name,
                "summary": self._summarize_output(output),
            })

        findings = [{
            "methodology": ", ".join(self.advisor.methodologies),
            "finding": (
                f"Deterministic fallback synthesis (no LLM available). "
                f"Matched keyword cues: {', '.join(matched_keywords) or 'none'}. "
                f"Reference basis: {', '.join(self.advisor.references[:2])}. "
                "Invoke the declared tools for concrete dating evidence."
            ),
            "confidence_basis": "keyword + tool-output heuristics (no model)",
        }]

        # Carry through any referral triggers the advisor's own advise() would set
        # by re-using the advisor's real advise() output if available.
        try:
            real = self.advisor.advise(prompt, ctx=ctx)
            return AdvisorResult(
                advisor=self.advisor.id,
                methodology=real.methodology,
                summary=real.summary + " [fallback: deterministic path used]",
                evidence=real.evidence + evidence,
                findings=real.findings,
                confidence=real.confidence,
                requires_professional_referral=real.requires_professional_referral,
                authentication_triggers=real.authentication_triggers,
                references_used=real.references_used,
                tools_invoked=real.tools_invoked,
                notes=real.notes + ["LLM unavailable; deterministic fallback engine used."],
            )
        except Exception as exc:
            return AdvisorResult(
                advisor=self.advisor.id,
                methodology=", ".join(self.advisor.methodologies),
                summary=f"Fallback engine (advisor.advise failed: {exc}).",
                evidence=evidence,
                findings=findings,
                confidence="low",
                references_used=list(self.advisor.references),
                notes=["fallback: advisor.advise raised; minimal structured result returned."],
            )

    @staticmethod
    def _summarize_output(output: Mapping[str, Any]) -> str:
        for key in ("matches", "techniques", "projections"):
            if key in output:
                items = output[key]
                return f"{len(items)} {key} record(s)"
        return "tool output available in evidence"
