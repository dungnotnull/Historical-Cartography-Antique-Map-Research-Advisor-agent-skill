"""PrintTechniqueLookupTool — print-technique dating reference.

Distilled from:
* Woodward (1975), *Five Centuries of Map Printing*
* Verner (1965), *Copperplate Printing*
* Woodward (1996), *Maps as Prints in the Italian Renaissance*

The handler returns dating evidence for a given technique (or all
techniques), including typical date ranges, visual/diagnostic features, and
what each feature implies for map dating. Output is deterministic so advisor
reasoning stays reproducible.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from ..errors import ToolExecutionError
from .base import _array_schema, _object_schema, _string_schema


# Each entry encodes the operational dating principle, not just a label.
TECHNIQUES: dict[str, dict[str, Any]] = {
    "woodcut": {
        "id": "woodcut",
        "label": "Woodcut (relief / woodblock)",
        "date_range": "c.1450 - c.1600 (dominant for maps pre-c.1550; persists for cheap prints after)",
        "invented": "Woodblock printing known in Europe from c.1400; applied to maps from the 1470s.",
        "principle": (
            "Raised lines print ink on the surface; the white areas are carved away. "
            "Diagonals and lettering often show the characteristic parallel 'grain' of the "
            "knife/grain direction. A woodcut map almost always predates c.1600."
        ),
        "diagnostic_features": [
            "Parallel, slightly irregular knife-cut lines (no burin swelling)",
            "Lettering may be hand-inserted or show wood-grain texture",
            "No platemark / no plate-tone",
            "Coarse hatch tones, limited fine detail",
            "Block may show wear or cracks in later states",
        ],
        "dating_implication": (
            "If a map is confirmed woodcut, it is almost certainly pre-c.1600; "
            "a woodcut Ptolemy-style map points to 1470s-1560s editions."
        ),
        "common_producers": ["Hartmann Schedel (Nuremberg Chronicle, 1493)", "Sebastian Münster (Cosmographia, 1540s)"],
    },
    "copper_engraving": {
        "id": "copper_engraving",
        "label": "Copper-plate engraving (intaglio, burin)",
        "date_range": "c.1500 - c.1820 (dominant map medium c.1550-c.1820)",
        "invented": "Intaglio copper engraving in Europe from c.1430s; dominant for maps from c.1550.",
        "principle": (
            "Lines are incised into a copper plate with a burin and hold ink below the surface; "
            "the plate is wiped and pressed under high pressure, leaving a platemark. "
            "Copper is soft: plates wear, so later impressions of the same plate lose line quality — "
            "useful for state/edition sequencing."
        ),
        "diagnostic_features": [
            "Visible platemark (indented rectangle around the image)",
            "Sharp, swelling burin lines with clean line-ends",
            "Fine cross-hatching and lettering engraved directly",
            "Possible plate-tone in the recesses",
            "Line thinning / loss of detail in late impressions (plate wear)",
        ],
        "dating_implication": (
            "A clean, crisp copper impression is consistent with an early state; "
            "a worn impression suggests a later state or re-issue. Copper plates "
            "were largely replaced by steel-facing from c.1822."
        ),
        "common_producers": ["Ortelius", "Mercator", "Blaeu", "Hondius", "Janssonius"],
    },
    "etching": {
        "id": "etching",
        "label": "Etching (acid-bitten intaglio)",
        "date_range": "c.1600 onward (used alongside engraving)",
        "invented": "Etching as a print medium from c.1500 (Dürer); common for maps from the 17th c.",
        "principle": (
            "Lines are drawn through an acid-resistant ground and bitten by acid, giving freer, "
            "more fluid lines than the burin. Often combined with engraving on the same plate."
        ),
        "diagnostic_features": [
            "Free, flowing, slightly irregular lines",
            "Often combined with engraved lettering (mixed technique)",
            "Platemark present (still intaglio)",
        ],
        "dating_implication": "An etched map is consistent with c.1600 onward; not a primary dating axis on its own.",
        "common_producers": ["Wenceslaus Hollar", "some Italian and Dutch cartographers"],
    },
    "steel_engraving": {
        "id": "steel_engraving",
        "label": "Steel engraving / steel-faced copper",
        "date_range": "c.1822 onward",
        "invented": "Steel-facing of copper plates from c.1822 (Jacob Perkins); pure steel plates mid-19th c.",
        "principle": (
            "Steel is harder than copper, so it yields very large editions with almost no wear. "
            "Lines are extremely fine and crisp even in late impressions. A uniformly crisp, "
            "very fine-line intaglio map in a large-run atlas is consistent with post-c.1822."
        ),
        "diagnostic_features": [
            "Extremely fine, uniform lines, even in late impressions",
            "Very large editions without plate wear",
            "Platemark present",
        ],
        "dating_implication": "Uniformly fine, unworn intaglio across many atlas copies points to c.1822 onward.",
        "common_producers": ["Society for the Diffusion of Useful Knowledge (SDUK)", "ARL cartographers"],
    },
    "lithography": {
        "id": "lithography",
        "label": "Lithography (planographic)",
        "date_range": "c.1796 invented; common for maps from c.1820s onward",
        "invented": "Alois Senefelder, Munich, c.1796; map use grows from c.1820.",
        "principle": (
            "Image is drawn with greasy ink on a limestone (or zinc) surface; water repels ink from "
            "non-image areas. No platemark. Crayon/wash tones and a 'drawn' rather than engraved "
            "look are characteristic. A lithographed map is essentially post-c.1820."
        ),
        "diagnostic_features": [
            "No platemark",
            "Crayon / wash / tusche tones; 'drawn' line quality",
            "Possible transfer-line offset from a transfer paper",
            "Tonal areas achieved by stipple or wash rather than cross-hatch",
        ],
        "dating_implication": (
            "If a map is confirmed lithograph, it postdates c.1796 and is practically post-c.1820. "
            "Chromolithography (multi-colour) is mid-to-late 19th century."
        ),
        "common_producers": ["19th-c. government survey offices", "Perthes (Justus Perthes Gotha)"],
    },
}

_TECHNIQUE_ENUM = list(TECHNIQUES.keys()) + ["all"]


class PrintTechniqueLookupTool(Tool):
    name = "print_technique_lookup"
    description = (
        "Look up a historical map printing/printing-technique and return its "
        "typical date range, diagnostic visual features, and dating implications "
        "(woodcut, copper engraving, etching, steel engraving, lithography)."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for print-technique lookup.",
            {
                "technique": _string_schema(
                    "Technique id to look up, or 'all' for the whole table.",
                    enum=_TECHNIQUE_ENUM,
                ),
                "observed_features": _array_schema(
                    _string_schema("A visual feature observed on the map, e.g. 'platemark'."),
                    description="Optional observed features to match against diagnostic_features.",
                ),
            },
            required=["technique"],
        )
        output = _object_schema(
            "Print-technique dating reference result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "techniques": _array_schema(_object_schema("A technique record.", {})),
                "matched_by_feature": _array_schema(
                    _string_schema("Technique id whose diagnostics include an observed feature."),
                    description="Techniques whose diagnostic features intersect the observed features.",
                ),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        technique = (arguments.get("technique") or "all").strip().lower()
        if technique not in _TECHNIQUE_ENUM:
            raise ToolExecutionError(
                f"Unknown technique {technique!r}.",
                details={"valid": _TECHNIQUE_ENUM},
            )
        observed = [str(f).strip().lower() for f in (arguments.get("observed_features") or [])]

        if technique == "all":
            records = [dict(v) for v in TECHNIQUES.values()]
        else:
            records = [dict(TECHNIQUES[technique])]

        matched_by_feature: list[str] = []
        if observed:
            for rec in records:
                diagnostics = " ".join(rec.get("diagnostic_features", [])).lower()
                if any(feat and _feature_present(feat, diagnostics) for feat in observed):
                    if rec["id"] not in matched_by_feature:
                        matched_by_feature.append(rec["id"])

        ctx.state.setdefault("print_technique_queries", []).append(technique)
        return {
            "query": {"technique": technique, "observed_features": observed},
            "techniques": records,
            "matched_by_feature": matched_by_feature,
        }


_NEGATIONS = {"no", "without", "absent", "absence", "lacks", "lacking", "not"}


def _feature_present(feature: str, diagnostics: str) -> bool:
    """Return True only if ``feature`` appears and is not negated locally.

    Catches false positives like matching ``"platemark"`` against the phrase
    ``"No platemark"``, where the feature is present in text but absent on the
    map. We scan for the feature token and check the preceding two words for a
    negation; if negated, we do not count it as a positive match.
    """
    if not feature:
        return False
    tokens = diagnostics.split()
    for idx, token in enumerate(tokens):
        if feature in token:
            window = tokens[max(0, idx - 2):idx]
            if any(neg in window for neg in _NEGATIONS):
                continue
            return True
    return False
