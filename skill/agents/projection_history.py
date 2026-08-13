"""ProjectionHistoryAdvisor — map-projection history as a dating aid.

Operationalizes the history-of-map-projections methodology via the
``projection_timeline`` tool, treating a projection as a terminus post quem.
Distilled from Snyder (1993) and the History of Cartography series.
"""
from __future__ import annotations

from typing import Any

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import confidence_from, extract_year, invoke_tool, mentions


_PROJECTION_WORDS = (
    "mercator", "conic", "azimuthal", "sinusoidal", "stereographic",
    "orthographic", "bonne", "lambert", "robinson", "projection",
    "ptolemaic", "trapezoidal",
)
_PROJECTION_MAP = {
    "mercator": "mercator",
    "sinusoidal": "sinusoidal",
    "stereographic": "stereographic",
    "orthographic": "orthographic",
    "bonne": "bonne",
    "lambert": "lambert_conformal_conic",
    "robinson": "robinson",
    "ptolemaic": "ptolelemaic_conic",
    "trapezoidal": "ptolelemaic_conic",
    "conic": "ptolelemaic_conic",
    "azimuthal": "stereographic",
}


class ProjectionHistoryAdvisor(SubAdvisor):
    id = "projection_history"
    name = "Map-Projection History Advisor"
    description = (
        "Uses map-projection history as a dating aid: a map cannot predate "
        "the projection it uses (terminus post quem)."
    )
    methodologies = ("history of map projections",)
    keywords = _PROJECTION_WORDS
    references = (
        "Snyder (1993), Flattening the Earth: Two Thousand Years of Map Projections",
        "Woodward (ed.), The History of Cartography, Vol. 1-6",
    )
    tools = ("projection_timeline",)

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        cues = mentions(prompt, *_PROJECTION_WORDS)
        year = extract_year(prompt)

        tools_invoked: list[str] = []
        records: list[dict[str, Any]] = []
        consistency: dict[str, Any] = {"compatible": "unknown", "reason": "No projection specified."}

        projection_id = self._first_projection(cues)
        if ctx.settings.flags.enable_tool_invocation and projection_id:
            result = invoke_tool(
                "projection_timeline",
                {"projection": projection_id, "map_year": year if year is not None else ""},
                ctx=ctx,
            )
            records = result.get("projections", [])
            consistency = result.get("consistency", consistency)
            tools_invoked.append("projection_timeline")

        evidence: list[dict[str, Any]] = []
        for rec in records:
            evidence.append({
                "type": "projection_record",
                "projection": rec.get("id"),
                "invented": rec.get("invented"),
                "inventor": rec.get("inventor"),
                "source": "projection_timeline tool (Snyder 1993)",
            })

        findings: list[dict[str, Any]] = []
        signals: list[bool] = []
        if records:
            rec = records[0]
            findings.append({
                "methodology": "history of map projections",
                "finding": (
                    f"Projection {rec.get('id')} invented {rec.get('invented')} by "
                    f"{rec.get('inventor')}. {rec.get('dating_implication')}"
                ),
                "confidence_basis": "projection matched in timeline",
            })
            signals.append(True)
            if consistency.get("compatible") == "no":
                findings.append({
                    "methodology": "history of map projections",
                    "finding": f"Consistency check FAILED: {consistency.get('reason')}",
                    "confidence_basis": "terminus post quem violation",
                })
                signals.append(True)
            elif consistency.get("compatible") == "yes" and year is not None:
                findings.append({
                    "methodology": "history of map projections",
                    "finding": f"Consistency check passed: {consistency.get('reason')}",
                    "confidence_basis": "year on/after invention",
                })
                signals.append(True)
        if not cues:
            findings.append({
                "methodology": "history of map projections",
                "finding": (
                    "No projection cue supplied. Identify the projection (graticule shape: "
                    "straight vs curved meridians; pole as point vs line) then query the tool "
                    "to obtain a terminus post quem."
                ),
                "confidence_basis": "no signal — advisory checklist issued",
            })

        confidence = confidence_from(*signals)
        return AdvisorResult(
            advisor=self.id,
            methodology="history of map projections",
            summary=(
                "Applied history-of-map-projections methodology (terminus post quem). "
                + (f"Projection cues: {', '.join(cues)}. " if cues else "No projection cue. ")
                + (f"Year {year}: consistency={consistency.get('compatible')}." if year is not None else "")
            ),
            evidence=evidence,
            findings=findings,
            confidence=confidence,
            requires_professional_referral=False,
            authentication_triggers=[],
            references_used=list(self.references),
            tools_invoked=tools_invoked,
            notes=["A projection date is a necessary, not sufficient, dating condition."],
        )

    @staticmethod
    def _first_projection(cues: list[str]) -> str:
        for cue in cues:
            if cue in _PROJECTION_MAP:
                return _PROJECTION_MAP[cue]
        return ""
