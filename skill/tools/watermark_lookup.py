"""WatermarkLookupTool — watermark reference for paper dating & provenance.

Distilled from:
* Heawood (1932), *Watermarks Mainly of the 17th and 18th Centuries*
* General paper-history knowledge underpinning the skill.

Watermarks (produced by wire designs sewn onto the paper mould) are strong
terminus post quem indicators: a paper cannot predate its watermark's
introduction at a given mill. The handler matches by motif, paper mill, or
 approximate year, returning dating and provenance guidance.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from .base import _array_schema, _object_schema, _string_schema


WATERMARKS: list[dict[str, Any]] = [
    {
        "motif": "fleur-de-lis",
        "mills": ["Angoumois (France)"],
        "date_range": "c.1580-1690",
        "description": "Fleur-de-lis in a shield, often with a pendant monogram; common on French paper.",
        "dating_note": "A fleur-de-lis watermark in an Angoumois paper is consistent with c.1580-1690.",
        "provenance_note": "French paper origin; supports attribution to French-printed atlases.",
    },
    {
        "motif": "posthorn",
        "mills": ["Dutch (Veluwe / Gelderland)"],
        "date_range": "c.1660-1750",
        "description": "A coiled posthorn, often with a crown and initials; Dutch paper-house mark.",
        "dating_note": "Posthorn watermarks are strongly associated with Dutch paper c.1660-1750.",
        "provenance_note": "Dutch paper origin; consistent with Dutch golden-age atlas printing.",
    },
    {
        "motif": "arms_of_amsterdam",
        "mills": ["Amsterdam paper mills"],
        "date_range": "c.1680-1750",
        "description": "Three saltire-crosses of Amsterdam, often in a crowned shield.",
        "dating_note": "Amsterdam arms watermark points to c.1680-1750 Dutch paper.",
        "provenance_note": "Amsterdam origin; useful for attributing Blaeu/Hondius-era re-issues.",
    },
    {
        "motif": "pro_patria",
        "mills": ["Dutch (various)"],
        "date_range": "c.1660-1750",
        "description": "A maid ('Pro Patria') holding a lance and hat, often with the motto.",
        "dating_note": "Pro Patria watermark is a classic Dutch paper mark c.1660-1750.",
        "provenance_note": "Dutch paper origin; common in 17th-c. Dutch atlas papers.",
    },
    {
        "motif": "foolscap",
        "mills": ["Dutch / German / English"],
        "date_range": "c.1550-1850 (long-lived; sub-types vary)",
        "description": "A jester's cap with bells, often with initials and a '5'/'4' countermark.",
        "dating_note": "Foolscap is long-lived; sub-variant and countermark date it more tightly.",
        "provenance_note": "Widely used; countermark initials (e.g. GR, IV) refine provenance.",
    },
    {
        "motif": "crowned_gr",
        "mills": ["English (Kent / Surrey mills)"],
        "date_range": "c.1714-1830 (George I-IV reigns)",
        "description": "Crowned 'GR' cipher with countermark initials; English royal paper.",
        "dating_note": "Crowned GR watermark is consistent with English paper c.1714-1830.",
        "provenance_note": "English paper origin; supports attribution to English-printed maps.",
    },
    {
        "motif": "lunette",
        "mills": ["Italian / French"],
        "date_range": "c.1620-1720",
        "description": "Crescent/lunette shape, often with initials; Italian/French paper.",
        "dating_note": "Lunette watermarks point to c.1620-1720 Mediterranean paper.",
        "provenance_note": "Italian or French paper origin.",
    },
    {
        "motif": "double_c_or_crowned_c",
        "mills": ["Swiss / German"],
        "date_range": "c.1600-1700",
        "description": "Crowned 'C' or double-C monogram; central European paper.",
        "dating_note": "Crowned-C watermarks consistent with c.1600-1700 Swiss/German paper.",
        "provenance_note": "Central European paper origin.",
    },
    {
        "motif": "anchor_in_circle",
        "mills": ["Southern European (Italian / Spanish)"],
        "date_range": "c.1540-1600",
        "description": "An anchor enclosed in a circle, sometimes with a countermark initial; Briquet-class 16th-c. mark.",
        "dating_note": "Anchor-in-circle watermarks point to c.1540-1600 Southern European paper (Briquet).",
        "provenance_note": "Italian or Spanish paper origin; supports attribution to Mediterranean printing.",
    },
    {
        "motif": "bulls_head",
        "mills": ["German / Swiss"],
        "date_range": "c.1470-1600",
        "description": "A bull's head (sometimes with a cross or flower above), a classic Briquet 15th-16th c. mark.",
        "dating_note": "Bull's-head watermarks are consistent with c.1470-1600 German/Swiss paper (Briquet).",
        "provenance_note": "German/Swiss paper origin; common in early northern European printing.",
    },
]


class WatermarkLookupTool(Tool):
    name = "watermark_lookup"
    description = (
        "Look up a paper watermark by motif, paper mill, or approximate year. "
        "Returns the typical date range and provenance guidance. Watermarks are a "
        "strong terminus post quem: paper cannot predate its watermark."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for watermark lookup.",
            {
                "motif": _string_schema("Watermark motif to match, e.g. 'posthorn', 'foolscap'."),
                "mill": _string_schema("Paper mill / origin to match, e.g. 'Dutch', 'Amsterdam'."),
                "year": _string_schema("Approximate year, to find watermarks plausibly in use by then."),
            },
        )
        output = _object_schema(
            "Watermark lookup result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "matches": _array_schema(_object_schema("A matched watermark record.", {})),
                "match_count": _string_schema("Number of matches."),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        motif = str(arguments.get("motif") or "").strip().lower()
        mill = str(arguments.get("mill") or "").strip().lower()
        year = arguments.get("year")
        target_year = _parse_year(year) if year not in (None, "") else None

        matches: list[dict[str, Any]] = []
        for record in WATERMARKS:
            if motif and motif not in str(record.get("motif", "")).lower():
                continue
            if mill:
                mills_blob = " ".join(record.get("mills", [])).lower()
                if mill not in mills_blob:
                    continue
            if target_year is not None:
                start, end = _parse_range(record.get("date_range", ""))
                if start is not None and end is not None and not (start <= target_year <= end):
                    continue
            matches.append(dict(record))

        ctx.state.setdefault("watermark_queries", []).append(
            {"motif": motif, "mill": mill, "year": year}
        )
        return {
            "query": {"motif": motif, "mill": mill, "year": year},
            "matches": matches,
            "match_count": len(matches),
        }


def _parse_year(value: Any) -> int | None:
    import re

    match = re.search(r"(\d{3,4})", str(value))
    return int(match.group(1)) if match else None


def _parse_range(text: str) -> tuple[int | None, int | None]:
    import re

    nums = [int(n) for n in re.findall(r"\d{3,4}", str(text))]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], nums[0]
    return None, None

