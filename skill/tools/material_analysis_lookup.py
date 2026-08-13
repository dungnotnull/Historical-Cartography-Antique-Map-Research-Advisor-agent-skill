"""MaterialAnalysisLookupTool — paper & ink material-analysis reference.

Distilled from:
* Hunter (1978), *Papermaking: The History and Technique of an Ancient Craft*
* Whatman / paper-conservation literature (wove paper, c.1757)
* Gettens & Stout (1966), *Painting Materials: A Short Encyclopaedia*

Provides three dated material tables — paper fibre, paper type (laid/wove),
and pigment chronology — each usable as a terminus post quem for the *paper*
or for the *colouring* (which may postdate the print by decades). See
RESEARCH-PAPER-KNOWLEDGE-BRAIN.md entries 19-21.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from ..errors import ToolExecutionError
from .base import _array_schema, _object_schema, _string_schema


PAPER_FIBRE: list[dict[str, Any]] = [
    {
        "id": "rag",
        "label": "Rag (linen/cotton) paper",
        "date_range": "pre-c.1850 (dominant before wood-pulp)",
        "principle": (
            "Rag fibre predates wood-pulp paper. A rag-paper map is consistent with pre-c.1850 "
            "manufacture; absence of wood-pulp is a fast material terminus post quem check."
        ),
        "dating_implication": "Rag fibre alone does not upper-bound the date, but wood-pulp fibre upper-bounds to post-c.1850.",
    },
    {
        "id": "wood_pulp",
        "label": "Wood-pulp (mechanical/chemical) paper",
        "date_range": "c.1850 onward (common from mid-19th c.)",
        "principle": (
            "Wood-pulp paper becomes common only from c.1850. Its presence is a strong terminus "
            "post quem: the paper (and therefore the map printed on it) cannot predate c.1850."
        ),
        "dating_implication": "Wood-pulp fibre ⇒ paper post-c.1850 (and thus the map post-c.1850).",
    },
]

PAPER_TYPE: list[dict[str, Any]] = [
    {
        "id": "laid",
        "label": "Laid paper (visible chain lines)",
        "date_range": "dominant pre-c.1800 (used throughout, but characteristic before wove)",
        "principle": (
            "Laid paper shows chain and laid lines from the wire mould; dominant before wove "
            "paper. Useful as a supporting axis: laid paper is consistent with pre-c.1800 but "
            "persists later, so it is not a hard TPQ on its own."
        ),
        "dating_implication": "Laid paper supports a pre-c.1800 date but does not require it.",
    },
    {
        "id": "wove",
        "label": "Wove paper (smooth, no chain lines)",
        "date_range": "c.1757 onward (Whatman, England)",
        "principle": (
            "Wove paper uses a woven wire mesh leaving no chain lines; introduced by Whatman "
            "from c.1757 and common thereafter. Its presence is a terminus post quem: c.1757."
        ),
        "dating_implication": "Wove paper ⇒ paper post-c.1757.",
    },
]

PIGMENT: list[dict[str, Any]] = [
    {
        "id": "prussian_blue",
        "label": "Prussian blue",
        "introduced": "c.1704",
        "principle": (
            "Prussian blue (ferric ferrocyanide) was the first modern synthetic pigment, "
            "discovered c.1704. Its presence in hand-colouring is a terminus post quem for the "
            "colouring: c.1704."
        ),
        "dating_implication": "Prussian blue in the colouring ⇒ colouring post-c.1704 (the print may be older).",
    },
    {
        "id": "chrome_yellow",
        "label": "Chrome yellow (lead chromate)",
        "introduced": "c.1797",
        "principle": "Chrome yellow available from c.1797; a TPQ for colouring.",
        "dating_implication": "Chrome yellow in colouring ⇒ colouring post-c.1797.",
    },
    {
        "id": "synthetic_ultramarine",
        "label": "Synthetic ultramarine",
        "introduced": "1828",
        "principle": (
            "Synthetic ultramarine (Guimet process) commercially available from 1828; a strong "
            "TPQ for colouring and a useful discriminator from natural ultramarine."
        ),
        "dating_implication": "Synthetic ultramarine in colouring ⇒ colouring post-1828.",
    },
]


_TABLES = {
    "paper_fibre": PAPER_FIBRE,
    "paper_type": PAPER_TYPE,
    "pigment": PIGMENT,
}
_TABLE_ENUM = list(_TABLES.keys()) + ["all"]


class MaterialAnalysisLookupTool(Tool):
    name = "material_analysis_lookup"
    description = (
        "Look up paper/ink material-analysis dating indicators: paper fibre (rag vs wood-pulp), "
        "paper type (laid vs wove), and pigment chronology (Prussian blue c.1704, chrome yellow "
        "c.1797, synthetic ultramarine 1828). Each is a terminus post quem for the paper or the "
        "colouring (which may postdate the print)."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for material-analysis lookup.",
            {
                "table": _string_schema(
                    "Which table to query.",
                    enum=_TABLE_ENUM,
                ),
                "id": _string_schema(
                    "Optional specific record id within the table (e.g. 'wood_pulp', 'wove', 'prussian_blue').",
                ),
            },
            required=["table"],
        )
        output = _object_schema(
            "Material-analysis lookup result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "records": _array_schema(_object_schema("A material-analysis record.", {})),
                "match_count": _string_schema("Number of records returned."),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        table = (arguments.get("table") or "all").strip().lower()
        if table not in _TABLE_ENUM:
            raise ToolExecutionError(
                f"Unknown material table {table!r}.",
                details={"valid": _TABLE_ENUM},
            )
        record_id = str(arguments.get("id") or "").strip().lower()

        if table == "all":
            records: list[dict[str, Any]] = []
            for tbl_name, tbl in _TABLES.items():
                for rec in tbl:
                    out = dict(rec)
                    out["table"] = tbl_name
                    records.append(out)
        else:
            records = [dict(rec) for rec in _TABLES[table]]
            for rec in records:
                rec["table"] = table

        if record_id:
            records = [rec for rec in records if rec.get("id") == record_id]

        ctx.state.setdefault("material_queries", []).append({"table": table, "id": record_id})
        return {
            "query": {"table": table, "id": record_id},
            "records": records,
            "match_count": len(records),
        }
