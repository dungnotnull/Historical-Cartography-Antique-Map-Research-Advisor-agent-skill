"""Chain-of-thought router.

The router is the entry point of the skill. For each user prompt it:

1. **Classifies intent** using a transparent keyword + methodology mapping,
   emitting an explicit chain-of-thought rationale (so the routing decision
   is auditable, not a black box).
2. **Selects one or more sub-advisors** from the registry, ranked by
   relevance; the always-on :class:`AuthenticationReferralAdvisor` is
   appended to every substantive request.
3. **Executes** the selected advisors (sequentially to keep state sharing
   deterministic and token budgets observable) and **aggregates** their
   structured results into a single report.
4. **Enforces the standing disclaimer** and the professional-referral guard
   on the final aggregated output.

When :attr:`Settings.flags.enable_chain_of_thought_routing` is ``False`` the
router falls back to a simple keyword match without emitting the explicit
rationale block (useful for benchmarking).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .base import AdvisorResult, SubAdvisor
from .context import SkillContext
from .disclaimer import DisclaimerPolicy
from .errors import DisclaimerViolation, RoutingError
from .logging_utils import fingerprint, get_logger
from .registry import SkillRegistry, get_registry


@dataclass
class RouterDecision:
    """Structured, auditable routing decision."""

    request_id: str
    rationale: str
    selected_advisors: list[str]
    reasoning_steps: list[str]
    fallback_used: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AggregatedReport:
    """Final aggregated report returned to the caller."""

    request_id: str
    user_prompt_fingerprint: str
    disclaimer: str
    referral_block: str
    routing: RouterDecision
    advisor_results: list[AdvisorResult] = field(default_factory=list)
    synthesis: str = ""
    requires_professional_referral: bool = False
    authentication_triggers: list[str] = field(default_factory=list)
    elapsed_ms: int = 0
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "user_prompt_fingerprint": self.user_prompt_fingerprint,
            "disclaimer": self.disclaimer,
            "referral_block": self.referral_block,
            "requires_professional_referral": self.requires_professional_referral,
            "authentication_triggers": list(self.authentication_triggers),
            "routing": self.routing.to_dict(),
            "advisor_results": [r.to_dict() for r in self.advisor_results],
            "synthesis": self.synthesis,
            "elapsed_ms": self.elapsed_ms,
            "notes": list(self.notes),
        }


class HistoricalCartographyRouter:
    """Top-level router that orchestrates sub-advisors."""

    GUARD_ADVISOR_ID = "authentication_referral"

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        *,
        disclaimer_policy: DisclaimerPolicy | None = None,
    ) -> None:
        self.registry = registry or get_registry()
        self.disclaimer_policy = disclaimer_policy or DisclaimerPolicy(strict=True)
        self.log = get_logger()

    # -- routing ----------------------------------------------------------

    def route(self, prompt: str, *, ctx: SkillContext | None = None) -> RouterDecision:
        ctx = ctx or SkillContext.for_prompt(prompt, settings=self._settings())
        candidates = self.registry.advisors()
        if not candidates:
            raise RoutingError("Registry has no sub-advisors registered.")

        # Exclude the guard advisor from scoring; it is always appended.
        scored = [
            (adv, adv.match_score(prompt))
            for adv in candidates
            if adv.id != self.GUARD_ADVISOR_ID
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)

        steps: list[str] = []
        if ctx.settings.flags.enable_chain_of_thought_routing:
            steps.append(
                "Step 1 — Decompose the request into the five core cartographic-research "
                "methodologies (print-technique dating, cartobibliography, projection "
                "history, toponymy/boundary history, provenance/materials)."
            )
            steps.append("Step 2 — Score each sub-advisor by keyword/methodology overlap with the prompt.")
            steps.append(
                "Step 3 — Select every advisor whose score indicates direct relevance; "
                "if none score above zero, select the highest-scoring advisor as a best-effort match."
            )
            steps.append(
                "Step 4 — Always append the AuthenticationReferralAdvisor as a guard so "
                "formal-authentication/referral language is never missing."
            )

        selected: list[SubAdvisor] = []
        rationale_parts: list[str] = []
        for adv, score in scored:
            if score > 0:
                selected.append(adv)
                rationale_parts.append(
                    f"{adv.id} (score={score}): matched on keywords "
                    f"{self._matched_keywords(adv, prompt)}."
                )

        if not selected and scored:
            adv, score = scored[0]
            selected.append(adv)
            rationale_parts.append(
                f"No strong keyword matches; defaulting to best-effort advisor {adv.id} "
                f"(score={score})."
            )

        # Always append the guard advisor.
        guard = self.registry.advisor(self.GUARD_ADVISOR_ID)
        selected.append(guard)

        rationale = (
            "Routed based on explicit methodology/keyword overlap. "
            + " ".join(rationale_parts)
            + f" {guard.id} appended unconditionally as the authentication/referral guard."
        ).strip()

        decision = RouterDecision(
            request_id=ctx.request_id,
            rationale=rationale,
            selected_advisors=[a.id for a in selected],
            reasoning_steps=steps,
            fallback_used=not bool(rationale_parts),
        )
        ctx.emit("router.decision", decision.to_dict())
        return decision

    # -- execution --------------------------------------------------------

    def execute(self, prompt: str, *, ctx: SkillContext | None = None) -> AggregatedReport:
        ctx = ctx or SkillContext.for_prompt(prompt, settings=self._settings())
        self.log.info(
            "router.execute.start",
            extra={"request_id": ctx.request_id, "prompt_fingerprint": fingerprint(prompt)},
        )
        ctx.emit("request.start", {"prompt_fingerprint": fingerprint(prompt)})

        decision = self.route(prompt, ctx=ctx)
        results: list[AdvisorResult] = []
        for advisor_id in decision.selected_advisors:
            advisor = self.registry.advisor(advisor_id)
            ctx.emit("advisor.start", {"advisor": advisor_id})
            try:
                result = advisor.advise(prompt, ctx=ctx)
            except Exception as exc:
                self.log.error(
                    "advisor.error",
                    extra={"advisor": advisor_id, "error": str(exc)},
                )
                ctx.emit("advisor.error", {"advisor": advisor_id, "error": str(exc)})
                # Graceful degradation: record the failure as a low-confidence note
                # rather than aborting the whole request.
                result = AdvisorResult(
                    advisor=advisor_id,
                    methodology="error_fallback",
                    summary=f"Sub-advisor {advisor_id} failed and was skipped: {exc}",
                    confidence="low",
                    notes=["advisor execution failed; downstream synthesis may be incomplete"],
                )
            results.append(result)
            ctx.emit("advisor.end", {"advisor": advisor_id, "confidence": result.confidence})

        # Aggregate referral signals across all advisors.
        triggers: list[str] = []
        requires_referral = False
        for r in results:
            if r.requires_professional_referral:
                requires_referral = True
            for t in r.authentication_triggers:
                if t not in triggers:
                    triggers.append(t)

        # Disclaimer handling (strict by default).
        try:
            disclaimer = self.disclaimer_policy.require_disclaimer(prompt)
        except DisclaimerViolation as violation:
            self.log.warning(
                "disclaimer.refusal",
                extra={"request_id": ctx.request_id, "details": violation.details},
            )
            disclaimer = self.disclaimer_policy.require_disclaimer("")  # user-request-scrubbed
            results.append(
                AdvisorResult(
                    advisor="disclaimer_guard",
                    methodology="policy",
                    summary="User requested removal of the standing disclaimer; refused in strict mode.",
                    confidence="high",
                    notes=[violation.message],
                )
            )

        synthesis = self._maybe_synthesize(prompt, results, ctx=ctx)
        report = AggregatedReport(
            request_id=ctx.request_id,
            user_prompt_fingerprint=fingerprint(prompt),
            disclaimer=disclaimer,
            referral_block=self.disclaimer_policy.referral_block() if requires_referral else "",
            routing=decision,
            advisor_results=results,
            requires_professional_referral=requires_referral,
            authentication_triggers=triggers,
            elapsed_ms=ctx.elapsed_ms(),
            synthesis=synthesis,
            notes=[],
        )
        ctx.emit("request.end", {"elapsed_ms": report.elapsed_ms})
        self.log.info(
            "router.execute.end",
            extra={
                "request_id": ctx.request_id,
                "elapsed_ms": report.elapsed_ms,
                "advisors": decision.selected_advisors,
                "requires_referral": requires_referral,
            },
        )
        return report

    # -- helpers ----------------------------------------------------------

    def _maybe_synthesize(self, prompt: str, results: list[AdvisorResult], *, ctx: SkillContext) -> str:
        """Optionally call the LLM to produce a short natural-language synthesis.

        Returns "" when no provider is configured or the call fails — the
        structured advisor results remain the source of truth regardless.
        """
        try:
            from .llm import get_llm_client
            client = get_llm_client()
            if client is None:
                return ""
            summaries = "; ".join(f"{r.advisor}: {r.summary}" for r in results)
            system = (
                "You are a historical-cartography research assistant. Synthesize the "
                "structured advisor findings into one concise paragraph. Always restate "
                "that this is general/analytical information, not a certified authentication "
                "or valuation, and that formal authentication requires an accredited map "
                "appraiser or cartographic-history specialist."
            )
            user = f"User question: {prompt}\n\nAdvisor findings: {summaries}"
            text = client.complete(system=system, user=user)
            return text or ""
        except Exception:
            return ""

    def _settings(self):
        # Imported lazily to avoid a hard dependency at module import time
        # (useful when registry is constructed in tests with stub settings).
        from config import load_settings

        return load_settings()

    @staticmethod
    def _matched_keywords(advisor: SubAdvisor, prompt: str) -> list[str]:
        lowered = prompt.lower()
        return [kw for kw in advisor.keywords if kw in lowered]


__all__ = ["RouterDecision", "AggregatedReport", "HistoricalCartographyRouter"]
