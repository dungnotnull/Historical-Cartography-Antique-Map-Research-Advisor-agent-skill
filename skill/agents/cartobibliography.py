"""CartobibliographyAdvisor — state/edition identification & attribution.

Operationalizes cartobibliographic methodology (state/edition/issue
identification and publisher/engraver attribution) via the
``cartobibliographic_lookup`` tool. Distilled from Tooley (1978),
Koeman/van der Krogt, Karrow (1993), and Goss (1990).
"""
from __future__ import annotations

from typing import Any

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import any_mention, confidence_from, invoke_tool, mentions


_MAKER_WORDS = (
    "ortelius", "mercator", "hondius", "blaeu", "blauw", "janssonius",
    "jansson", "sanson", "jaillot", "homann", "seutter", "coronelli",
)
_EDITION_WORDS = (
    "edition", "state", "issue", "atlas", "theatrum", "novus atlas",
    "atlas maior", "atlas minor", "imprint", "title-page", "title page",
    "plate", "re-issue", "reissue",
)


class CartobibliographyAdvisor(SubAdvisor):
    id = "cartobibliography"
    name = "Cartobibliography Advisor"
    description = (
        "Identifies map state/edition/issue and attributes publisher/engraver "
        "using cartobibliographic methodology."
    )
    methodologies = ("cartobibliography methodology (state/edition/issue identification)",)
    keywords = _MAKER_WORDS + _EDITION_WORDS
    references = (
        "Tooley (1978), Tooley's Dictionary of Mapmakers",
        "Koeman (1967-71) / van der Krogt (1997-2011), Atlantes Neerlandici",
        "Karrow (1993), Mapmakers of the Sixteenth Century",
        "Goss (1990), Blaeu's The Grand Atlas",
    )
    tools = ("cartobibliographic_lookup",)

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        maker_cues = mentions(prompt, *_MAKER_WORDS)
        edition_cues = mentions(prompt, *_EDITION_WORDS)

        tools_invoked: list[str] = []
        maker_records: list[dict[str, Any]] = []
        if ctx.settings.flags.enable_tool_invocation and (maker_cues or edition_cues):
            # Query with the first maker cue; also try an atlas fragment.
            atlas_fragment = ""
            for cue in edition_cues:
                if cue in {"theatrum", "novus atlas", "atlas maior", "atlas minor"}:
                    atlas_fragment = cue
                    break
            result = invoke_tool(
                "cartobibliographic_lookup",
                {"maker": maker_cues[0] if maker_cues else "", "atlas": atlas_fragment},
                ctx=ctx,
            )
            maker_records = result.get("matches", [])
            tools_invoked.append("cartobibliographic_lookup")

        evidence: list[dict[str, Any]] = []
        for rec in maker_records:
            evidence.append({
                "type": "maker_record",
                "maker": rec.get("name"),
                "active": rec.get("active"),
                "role": rec.get("role"),
                "source": "cartobibliographic_lookup tool (Tooley/Koeman/van der Krogt)",
            })

        findings: list[dict[str, Any]] = []
        signals: list[bool] = []
        if maker_records:
            for rec in maker_records:
                findings.append({
                    "methodology": "cartobibliography methodology",
                    "finding": (
                        f"{rec.get('name')} (active {rec.get('active')}). "
                        f"State/edition note: {rec.get('state_edition_notes')}"
                    ),
                    "confidence_basis": "maker matched in reference table",
                })
            signals.append(True)
        if edition_cues and not maker_records:
            findings.append({
                "methodology": "cartobibliography methodology",
                "finding": (
                    f"Edition/state cues detected ({', '.join(edition_cues)}) but no maker "
                    "matched. Identify the imprint and title-page, then re-query; map-count and "
                    "title-page variants are the primary edition discriminators (e.g. Theatrum 1570 vs later)."
                ),
                "confidence_basis": "edition cue without maker match",
            })
            signals.append(True)
        if not maker_cues and not edition_cues:
            findings.append({
                "methodology": "cartobibliography methodology",
                "finding": (
                    "No maker/edition cue supplied. Recommended steps: (1) read the imprint "
                    "and title-page; (2) count the maps; (3) note cartouche signatures and "
                    "plate-acquisition history; (4) query the tool with the maker surname."
                ),
                "confidence_basis": "no signal — advisory checklist issued",
            })

        triggers: list[str] = []
        if any_mention(prompt, ("authentic", "authentication", "genuine", "fake", "forgery", "value", "appraisal")):
            triggers.append("Authentication/valuation intent: cartobibliography supports attribution, not certified authentication.")

        confidence = confidence_from(*signals)
        return AdvisorResult(
            advisor=self.id,
            methodology="cartobibliography methodology (state/edition/issue identification)",
            summary=(
                "Applied cartobibliographic methodology (state/edition identification + "
                "publisher/engraver attribution). "
                + (f"Maker cues: {', '.join(maker_cues)}. " if maker_cues else "No maker cue. ")
                + (f"Edition cues: {', '.join(edition_cues)}." if edition_cues else "No edition cue.")
            ),
            evidence=evidence,
            findings=findings,
            confidence=confidence,
            requires_professional_referral=bool(triggers),
            authentication_triggers=triggers,
            references_used=list(self.references),
            tools_invoked=tools_invoked,
            notes=[
                "Plate-acquisition history (e.g. Mercator→Hondius, Hondius→Blaeu) is critical "
                "for distinguishing original editions from re-issues.",
            ],
        )
