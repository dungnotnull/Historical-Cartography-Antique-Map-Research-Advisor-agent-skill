"""AuthenticationReferralAdvisor — always-on professional-referral guard.

This advisor is appended to *every* substantive request by the router. Its
job is not to analyse the map but to enforce the standing disclaimer policy
of this domain: formal authentication or valuation of a significant antique
map must be verified by an accredited map appraiser or cartographic-history
specialist. Distilled from IMCoS (2020) guidelines.

When authentication/valuation intent is detected it sets
``requires_professional_referral = True`` and lists explicit triggers; even
without such intent it returns the standing referral reminder so the guard
is never silent.
"""
from __future__ import annotations

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import mentions


_INTENT_WORDS = (
    "authentic", "authentication", "authenticate", "genuine", "fake",
    "forgery", "forged", "real", "original", "value", "valued", "valuation",
    "appraisal", "appraise", "appraiser", "worth", "sell", "selling",
    "insurance", "insure", "invest", "investment", "certified", "certificate",
    "guarantee", "guaranteed",
)


class AuthenticationReferralAdvisor(SubAdvisor):
    id = "authentication_referral"
    name = "Authentication & Referral Guard"
    description = (
        "Always-on guard enforcing the standing disclaimer and professional-"
        "referral policy for antique-map authentication/valuation."
    )
    methodologies = ("authentication/referral guard policy",)
    keywords = _INTENT_WORDS
    references = (
        "IMCoS (2020), Guidelines on Map Authentication and Valuation",
    )
    tools: tuple[str, ...] = ()

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        intent_cues = mentions(prompt, *_INTENT_WORDS)
        triggers: list[str] = []

        if intent_cues:
            triggers.append(
                f"Authentication/valuation intent detected ({', '.join(intent_cues)}). "
                "This skill cannot authenticate or value a map; refer to an accredited map "
                "appraiser or cartographic-history specialist."
            )
        # Material/value signals that always require referral regardless of wording.
        if any(word in prompt.lower() for word in ("significant", "rare", "expensive", "museum", "donate")):
            triggers.append(
                "The map is described as significant/rare/museum-grade: formal "
                "authentication and valuation by an accredited specialist are required."
            )

        requires_referral = bool(triggers)
        summary = (
            "Standing referral guard applied. "
            + ("Professional referral REQUIRED: " + " ".join(triggers) if requires_referral
               else "No authentication/valuation intent detected; standing disclaimer still applies.")
        )

        findings = [{
            "methodology": "authentication/referral guard policy",
            "finding": (
                "Per IMCoS (2020) guidelines and the skill's standing policy, any formal "
                "authentication or valuation of a significant antique map must be performed "
                "by an accredited map appraiser or cartographic-history specialist. This skill "
                "provides general/analytical research support only."
            ),
            "confidence_basis": "standing policy (IMCoS 2020)",
        }]

        return AdvisorResult(
            advisor=self.id,
            methodology="authentication/referral guard policy",
            summary=summary,
            evidence=[],
            findings=findings,
            confidence="high",
            requires_professional_referral=requires_referral,
            authentication_triggers=triggers,
            references_used=list(self.references),
            tools_invoked=[],
            notes=[
                "This advisor is appended unconditionally by the router to guarantee the "
                "disclaimer/referral language is never missing from a substantive response.",
            ],
        )
