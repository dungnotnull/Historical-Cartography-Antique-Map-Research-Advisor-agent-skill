"""ProvenanceMaterialsAdvisor — provenance & paper/ink material analysis.

Operationalizes provenance research (watermarks, ownership marks, prior-sale
records) and paper/ink material-analysis principles via the
``watermark_lookup`` tool. Distilled from Heawood (1932) and the material-
analysis principles in SECOND-BRAIN-KNOWLEDGE-PAPER.md. Material analysis for
authenticity is explicitly flagged as requiring a professional.
"""
from __future__ import annotations

from typing import Any

from ..base import AdvisorResult, SubAdvisor
from ..context import SkillContext
from .util import any_mention, confidence_from, extract_year, invoke_tool, mentions


_WATERMARK_WORDS = (
    "watermark", "water mark", "foolscap", "posthorn", "fleur-de-lis",
    "arms of amsterdam", "pro patria", "crowned gr", "lunette", "countermark",
    "paper", "mould", "mold", "chain lines", "laid lines",
)
_PROVENANCE_WORDS = (
    "provenance", "ownership", "ownership mark", "bookplate", "ex libris",
    "collector", "sale", "auction", "catalogue", "catalog", "stamp",
    "inscription", "annotation", "marginalia",
)
_MATERIAL_WORDS = (
    "ink", "oxidation", "bleed", "show-through", "showthrough", "foxing",
    "condition", "fiber", "fibre", "rag", "vellum", "parchment",
    "wood-pulp", "wood pulp", "prussian blue", "ultramarine", "chrome yellow",
    "pigment", "colour", "color", "colouring", "coloring",
    "hand-coloured", "hand-colored", "hand-colour", "hand-color",
    "laid paper", "wove paper", "laid", "wove",
)


class ProvenanceMaterialsAdvisor(SubAdvisor):
    id = "provenance_materials"
    name = "Provenance & Materials Advisor"
    description = (
        "Supports provenance research (watermarks, ownership marks, prior-sale "
        "records) and explains paper/ink material-analysis principles for "
        "authenticity assessment."
    )
    methodologies = (
        "provenance research methodology (watermark analysis, ownership-mark research)",
        "paper/ink material-analysis principles",
    )
    keywords = _WATERMARK_WORDS + _PROVENANCE_WORDS + _MATERIAL_WORDS
    references = (
        "Heawood (1932), Watermarks Mainly of the 17th and 18th Centuries",
        "IMCoS (2020), Guidelines on Map Authentication and Valuation",
    )
    tools = ("watermark_lookup", "material_analysis_lookup")

    def advise(self, prompt: str, *, ctx: SkillContext) -> AdvisorResult:
        watermark_cues = mentions(prompt, *_WATERMARK_WORDS)
        provenance_cues = mentions(prompt, *_PROVENANCE_WORDS)
        material_cues = mentions(prompt, *_MATERIAL_WORDS)
        year = extract_year(prompt)

        tools_invoked: list[str] = []
        matches: list[dict[str, Any]] = []
        if ctx.settings.flags.enable_tool_invocation and watermark_cues:
            motif = self._first_motif(watermark_cues)
            result = invoke_tool(
                "watermark_lookup",
                {"motif": motif, "mill": "", "year": year if year is not None else ""},
                ctx=ctx,
            )
            matches = result.get("matches", [])
            tools_invoked.append("watermark_lookup")

        material_records: list[dict[str, Any]] = []
        if ctx.settings.flags.enable_tool_invocation and material_cues:
            mat_result = invoke_tool("material_analysis_lookup", {"table": "all"}, ctx=ctx)
            material_records = mat_result.get("records", [])
            if "material_analysis_lookup" not in tools_invoked:
                tools_invoked.append("material_analysis_lookup")

        evidence: list[dict[str, Any]] = []
        for rec in matches:
            evidence.append({
                "type": "watermark_record",
                "motif": rec.get("motif"),
                "mills": rec.get("mills"),
                "date_range": rec.get("date_range"),
                "source": "watermark_lookup tool (Heawood 1932)",
            })
        for rec in material_records:
            evidence.append({
                "type": "material_record",
                "table": rec.get("table"),
                "id": rec.get("id"),
                "label": rec.get("label"),
                "date_range": rec.get("date_range") or rec.get("introduced"),
                "source": "material_analysis_lookup tool (Hunter/Whatman/Gettens&Stout)",
            })

        findings: list[dict[str, Any]] = []
        signals: list[bool] = []
        if matches:
            for rec in matches:
                findings.append({
                    "methodology": "provenance research methodology",
                    "finding": (
                        f"Watermark '{rec.get('motif')}' ({rec.get('date_range')}, "
                        f"{rec.get('mills')}). {rec.get('dating_note')} "
                        f"{rec.get('provenance_note')}"
                    ),
                    "confidence_basis": "watermark matched in reference table",
                })
            signals.append(True)
        elif watermark_cues:
            findings.append({
                "methodology": "provenance research methodology",
                "finding": (
                    f"Watermark cue(s) detected ({', '.join(watermark_cues)}) but no match. "
                    "Document the motif exactly (and any countermark/initials) and re-query; "
                    "compare against Heawood-style catalogues."
                ),
                "confidence_basis": "cue without table match",
            })
            signals.append(True)
        if provenance_cues:
            findings.append({
                "methodology": "provenance research methodology",
                "finding": (
                    f"Provenance cue(s) detected ({', '.join(provenance_cues)}). Build a "
                    "provenance chain: ownership marks → bookplates → sale/auction catalogue "
                    "records → prior collector attributions. Each link is a dating/attribution "
                    "data point but not proof of authenticity."
                ),
                "confidence_basis": "provenance cue",
            })
            signals.append(True)
        if material_cues:
            findings.append({
                "methodology": "paper/ink material-analysis principles",
                "finding": (
                    f"Material cue(s) detected ({', '.join(material_cues)}). Paper fiber (rag "
                    "vs wood-pulp: wood-pulp post-c.1850), ink oxidation/bleed, chain-line "
                    "spacing, and condition are material-analysis indicators. Definitive "
                    "material authentication requires laboratory / specialist examination."
                ),
                "confidence_basis": "material cue",
            })
            signals.append(True)
        if material_records:
            tpqs = []
            for rec in material_records:
                dr = rec.get("date_range") or rec.get("introduced")
                if dr:
                    tpqs.append(f"{rec.get('label')}: {dr}")
            findings.append({
                "methodology": "paper/ink material-analysis principles",
                "finding": (
                    "Material-analysis reference applied. Dated indicators: "
                    + "; ".join(tpqs)
                    + ". Each is a terminus post quem for the paper or the colouring "
                    "(colouring may postdate the print by decades)."
                ),
                "confidence_basis": "material_analysis_lookup records",
            })
            signals.append(True)
        if not (watermark_cues or provenance_cues or material_cues):
            findings.append({
                "methodology": "provenance research methodology",
                "finding": (
                    "No provenance/material cue supplied. Recommended steps: (1) note any "
                    "watermark (hold to light); (2) record ownership marks/annotations; "
                    "(3) trace prior sale records; (4) assess paper type and ink condition."
                ),
                "confidence_basis": "no signal — advisory checklist issued",
            })

        triggers: list[str] = []
        if any_mention(prompt, ("authentic", "authentication", "genuine", "fake", "forgery", "value", "appraisal", "worth")):
            triggers.append(
                "Material/provenance analysis for authenticity requires laboratory or "
                "specialist examination — refer to an accredited map appraiser."
            )

        confidence = confidence_from(*signals)
        return AdvisorResult(
            advisor=self.id,
            methodology="provenance research methodology + paper/ink material-analysis principles",
            summary=(
                "Applied provenance research + paper/ink material-analysis methodology. "
                + (f"Watermark matches: {len(matches)}. " if matches else "No watermark match. ")
                + (f"Cues: {', '.join(watermark_cues + provenance_cues + material_cues)}." if (watermark_cues or provenance_cues or material_cues) else "")
            ),
            evidence=evidence,
            findings=findings,
            confidence=confidence,
            requires_professional_referral=bool(triggers),
            authentication_triggers=triggers,
            references_used=list(self.references),
            tools_invoked=tools_invoked,
            notes=[
                "Watermark = strong terminus post quem for the paper, not the map image.",
                "Wood-pulp paper postdates c.1850 — a quick material dating axis.",
            ],
        )

    @staticmethod
    def _first_motif(cues: list[str]) -> str:
        mapping = {
            "foolscap": "foolscap", "posthorn": "posthorn",
            "fleur-de-lis": "fleur-de-lis", "arms of amsterdam": "arms_of_amsterdam",
            "pro patria": "pro_patria", "crowned gr": "crowned_gr",
            "lunette": "lunette",
        }
        for cue in cues:
            if cue in mapping:
                return mapping[cue]
        return ""


