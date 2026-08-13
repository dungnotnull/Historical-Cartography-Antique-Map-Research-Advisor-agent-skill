"""PrintTechniqueDatingAdvisor — print-technique dating methodology.

Operationalizes the print-technique dating methodology (woodcut → copper
engraving → steel engraving → lithography chronology) using the
``print_technique_lookup`` tool. Distilled from Woodward (1975), Verner
(1965), and Woodward (1996) — see references/print-technique-dating.md.
"""
from __future__ import annotations

from typing import Any

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import any_mention, confidence_from, extract_year, invoke_tool, mentions


_OBSERVATION_FEATURES = (
    "platemark", "platemark", "no platemark", "wood-grain", "wood grain",
    "burin", "cross-hatching", "hatching", "crayon", "wash", "stipple",
    "plate-tone", "plate tone", "fine lines", "coarse", "lithograph",
    "engraving", "woodcut", "relief", "intaglio",
)

_TECHNIQUE_WORDS = (
    "woodcut", "woodblock", "copper", "engraving", "engraved", "intaglio",
    "lithograph", "lithography", "etching", "etched", "steel", "relief",
    "platemark", "plate mark",
)


class PrintTechniqueDatingAdvisor(SubAdvisor):
    id = "print_technique_dating"
    name = "Print-Technique Dating Advisor"
    description = (
        "Dates and attributes maps using printing-technique evidence "
        "(woodcut, copper engraving, etching, steel engraving, lithography)."
    )
    methodologies = ("print-technique dating methodology",)
    keywords = _TECHNIQUE_WORDS
    references = (
        "Woodward (1975), Five Centuries of Map Printing",
        "Verner (1965), Copperplate Printing",
        "Woodward (1996), Maps as Prints in the Italian Renaissance",
    )
    tools = ("print_technique_lookup",)

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        techniques_named = mentions(prompt, *_TECHNIQUE_WORDS)
        observed = [f for f in _OBSERVATION_FEATURES if f in prompt.lower()]
        # De-duplicate observed features while preserving order.
        seen: set[str] = set()
        observed_unique = [f for f in observed if not (f in seen or seen.add(f))]

        tool_result: dict[str, Any] = {}
        tools_invoked: list[str] = []
        if ctx.settings.flags.enable_tool_invocation:
            technique_arg = "all" if not techniques_named else self._first_known_technique(techniques_named)
            tool_result = invoke_tool(
                "print_technique_lookup",
                {"technique": technique_arg, "observed_features": observed_unique},
                ctx=ctx,
            )
            tools_invoked.append("print_technique_lookup")

        records = tool_result.get("techniques", [])
        matched = tool_result.get("matched_by_feature", [])

        evidence: list[dict[str, Any]] = []
        findings: list[dict[str, Any]] = []
        for rec in records:
            evidence.append({
                "type": "technique_record",
                "technique": rec.get("id"),
                "date_range": rec.get("date_range"),
                "source": "print_technique_lookup tool (distilled from Woodward/Verner)",
            })

        # Build a dating finding when a technique is named or matched by feature.
        dating_signals: list[str] = []
        if techniques_named:
            findings.append({
                "methodology": "print-technique dating methodology",
                "finding": (
                    f"Request names technique cue(s): {', '.join(techniques_named)}. "
                    "Confirm the technique visually before dating; the tool's date_range "
                    "gives the chronology bracket."
                ),
                "confidence_basis": "keyword cue in user prompt",
            })
            dating_signals.append(True)
        if matched:
            findings.append({
                "methodology": "print-technique dating methodology",
                "finding": (
                    f"Observed features {observed_unique} are consistent with: "
                    f"{', '.join(matched)}. Use the diagnostic_features checklist to "
                    "discriminate further (e.g. platemark present ⇒ intaglio; absent ⇒ woodcut/lithography)."
                ),
                "confidence_basis": "feature-to-technique match",
            })
            dating_signals.append(True)
        if not techniques_named and not matched:
            findings.append({
                "methodology": "print-technique dating methodology",
                "finding": (
                    "No specific technique or visual feature was supplied. Recommended "
                    "checklist: (1) platemark present? (2) line quality burin vs crayon? "
                    "(3) wood-grain? (4) wash/stipple tones? Then re-query the tool."
                ),
                "confidence_basis": "no signal — advisory checklist issued",
            })

        year = extract_year(prompt)
        if year is not None:
            findings.append({
                "methodology": "print-technique dating methodology",
                "finding": (
                    f"User-supplied/observed year {year}. Cross-check against the "
                    "technique date_range; e.g. a lithograph cannot predate c.1796, "
                    "a steel engraving cannot predate c.1822."
                ),
                "confidence_basis": "year cross-check",
            })
            dating_signals.append(True)

        # Material analysis for authenticity must be referred to a professional.
        triggers: list[str] = []
        if any_mention(prompt, ("authentic", "authentication", "genuine", "fake", "forgery", "value", "appraisal")):
            triggers.append("Authenticity/valuation intent detected: print-technique evidence alone cannot authenticate.")

        confidence = confidence_from(*dating_signals)
        return AdvisorResult(
            advisor=self.id,
            methodology="print-technique dating methodology",
            summary=(
                "Applied print-technique dating methodology (woodcut → copper engraving → "
                "steel engraving → lithography chronology). "
                + (f"Technique cues: {', '.join(techniques_named)}. " if techniques_named else "No explicit technique cue. ")
                + (f"Feature matches: {', '.join(matched)}." if matched else "No feature matches.")
            ),
            evidence=evidence,
            findings=findings,
            confidence=confidence,
            requires_professional_referral=bool(triggers),
            authentication_triggers=triggers,
            references_used=list(self.references),
            tools_invoked=tools_invoked,
            notes=[
                "Print-technique evidence is a strong terminus post quem but not a proof of authenticity.",
            ],
        )

    @staticmethod
    def _first_known_technique(named: list[str]) -> str:
        mapping = {
            "woodcut": "woodcut", "woodblock": "woodcut",
            "copper": "copper_engraving", "engraving": "copper_engraving",
            "engraved": "copper_engraving", "intaglio": "copper_engraving",
            "lithograph": "lithography", "lithography": "lithography",
            "etching": "etching", "etched": "etching",
            "steel": "steel_engraving",
        }
        for cue in named:
            if cue in mapping:
                return mapping[cue]
        return "all"
