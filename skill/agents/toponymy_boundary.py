"""ToponymyBoundaryAdvisor — historical toponymy & boundary history as a dating aid.

Operationalizes historical-toponymy / place-name change and political-boundary
history analysis via the ``toponym_lookup`` tool. Distilled from the applied
case-study sources (Edney on British India; Barber/Harper on political
content) listed in SECOND-BRAIN-KNOWLEDGE-PAPER.md.
"""
from __future__ import annotations

from typing import Any

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import confidence_from, invoke_tool, mentions


_PLACE_CUES = (
    "constantinople", "istanbul", "persia", "iran", "ceylon", "sri lanka",
    "bombay", "mumbai", "petrograd", "leningrad", "st petersburg",
    "saint petersburg", "new amsterdam", "new york", "new spain", "mexico",
    "united provinces", "batavian", "kingdom of holland", "peking",
    "beijing", "bombay", "to", "place name", "place-name", "toponym",
    "renamed", "boundary", "boundaries", "border", "frontier",
)
_REGION_CUES = (
    "north america", "south asia", "middle east", "eastern europe",
    "western europe", "east asia", "anatolia",
)


class ToponymyBoundaryAdvisor(SubAdvisor):
    id = "toponymy_boundary"
    name = "Toponymy & Boundary-History Advisor"
    description = (
        "Uses historical place-name changes and political-boundary history as "
        "a map-dating aid (e.g. New Amsterdam→New York 1664; Petrograd 1914-24)."
    )
    methodologies = ("historical toponymy / place-name change analysis",)
    keywords = _PLACE_CUES + _REGION_CUES
    references = (
        "Edney (1997), Mapping an Empire (applied historical-content dating)",
        "Barber & Harper (2010), Magnificent Maps (political-content analysis)",
        "Barber (ed.) (2005), The Map Book",
    )
    tools = ("toponym_lookup",)

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        place_cues = mentions(prompt, *_PLACE_CUES)
        region_cues = mentions(prompt, *_REGION_CUES)

        tools_invoked: list[str] = []
        matches: list[dict[str, Any]] = []
        # Query each distinct place/region cue; merge results.
        queried: set[str] = set()
        if ctx.settings.flags.enable_tool_invocation:
            for cue in place_cues + region_cues:
                if not cue or cue in queried or cue in {"to"}:
                    continue
                queried.add(cue)
                mode = "region" if cue in _REGION_CUES else "auto"
                result = invoke_tool("toponym_lookup", {"query": cue, "match_mode": mode}, ctx=ctx)
                for rec in result.get("matches", []):
                    if rec not in matches:
                        matches.append(rec)
            if queried:
                tools_invoked.append("toponym_lookup")

        evidence: list[dict[str, Any]] = []
        for rec in matches:
            variants = rec.get("variants", [])
            evidence.append({
                "type": "toponym_record",
                "place": rec.get("place"),
                "region": rec.get("region"),
                "variants": [v.get("name") for v in variants],
                "source": "toponym_lookup tool (applied cartographic-history cases)",
            })

        findings: list[dict[str, Any]] = []
        signals: list[bool] = []
        for rec in matches:
            findings.append({
                "methodology": "historical toponymy / place-name change analysis",
                "finding": f"{rec.get('place')}: {rec.get('dating_rule')}",
                "confidence_basis": "matched toponym record with dated variants",
            })
            signals.append(True)
        if not matches and (place_cues or region_cues):
            findings.append({
                "methodology": "historical toponymy / place-name change analysis",
                "finding": (
                    f"Cues detected ({', '.join(place_cues + region_cues)}) but no dated "
                    "variant matched in the reference table. Treat the place-name present on "
                    "the map as a terminus post quem for that name and a terminus ante quem "
                    "for its successor."
                ),
                "confidence_basis": "cue without table match",
            })
            signals.append(True)
        if not place_cues and not region_cues:
            findings.append({
                "methodology": "historical toponymy / place-name change analysis",
                "finding": (
                    "No toponym cue supplied. Recommended steps: (1) transcribe all place-names "
                    "on the map; (2) cross-check against known rename dates; (3) note political "
                    "boundaries (e.g. colony vs independent state) as additional dating axes."
                ),
                "confidence_basis": "no signal — advisory checklist issued",
            })

        confidence = confidence_from(*signals)
        return AdvisorResult(
            advisor=self.id,
            methodology="historical toponymy / place-name change analysis",
            summary=(
                "Applied historical-toponymy / boundary-history dating methodology. "
                + (f"Matched {len(matches)} toponym record(s). " if matches else "No toponym record matched. ")
                + (f"Cues: {', '.join(place_cues + region_cues)}." if (place_cues or region_cues) else "")
            ),
            evidence=evidence,
            findings=findings,
            confidence=confidence,
            requires_professional_referral=False,
            authentication_triggers=[],
            references_used=list(self.references),
            tools_invoked=tools_invoked,
            notes=[
                "A place-name is a terminus post quem for that name and a terminus ante quem "
                "for its successor; combine with political-boundary history for tighter dating.",
            ],
        )
