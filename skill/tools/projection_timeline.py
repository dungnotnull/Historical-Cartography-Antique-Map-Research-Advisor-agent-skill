"""ProjectionTimelineTool — history-of-map-projections timeline.

Distilled from:
* Snyder (1993), *Flattening the Earth: Two Thousand Years of Map Projections*
* History of Cartography, Vol. 1-6 (Woodward, ed.)

A projection's presence on a map is a *terminus post quem* dating aid: a map
cannot use a projection invented after it was made. The handler returns the
invention date, inventor, characteristic use periods, and the dating
implication for the requested projection (or the whole timeline).
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from ..errors import ToolExecutionError
from .base import _array_schema, _object_schema, _string_schema


PROJECTIONS: dict[str, dict[str, Any]] = {
    "ptolelemaic_conic": {
        "id": "ptolelemaic_conic",
        "label": "Ptolemaic conic / Trapezoidal",
        "invented": "c.150 AD (Ptolemy, Geography)",
        "inventor": "Claudius Ptolemy",
        "use_period": "Revived in printed Ptolemy editions, 1477 (Bologna) - c.1600",
        "description": "Conic/trapezoidal approximation with straight meridians and curved parallels.",
        "dating_implication": (
            "A trapezoidal Ptolemaic-style projection on a printed map points to the early "
            "Ptolemy tradition (1477-1570s) rather than a contemporary survey."
        ),
    },
    "stereographic": {
        "id": "stereographic",
        "label": "Stereographic (azimuthal conformal)",
        "invented": "Antiquity (Ptolemy describes it; Hipparchus credited)",
        "inventor": "Hipparchus / Ptolemy",
        "use_period": "Renaissance star charts and polar maps; continuous use",
        "description": "Azimuthal, conformal; preserves angles, distorts area toward the edge.",
        "dating_implication": "Not strongly date-discriminating; common across periods for polar/star maps.",
    },
    "orthographic": {
        "id": "orthographic",
        "label": "Orthographic (azimuthal perspective)",
        "invented": "Antiquity (described by Ptolemy)",
        "inventor": "Ptolemy",
        "use_period": "Renaissance globes and perspective world maps; 16th-17th c. decorative use",
        "description": "Perspective view from infinity; looks like a globe photograph.",
        "dating_implication": "Popular for decorative world maps 16th-17th c.; weak dating axis alone.",
    },
    "mercator": {
        "id": "mercator",
        "label": "Mercator (cylindrical conformal)",
        "invented": "1569 (Gerardus Mercator, world map of 1569)",
        "inventor": "Gerardus Mercator",
        "use_period": "Slow adoption 1569-c.1600; dominant for navigation from c.17th c. onward",
        "description": "Rhumb lines are straight; conformal; polar area inflates strongly.",
        "dating_implication": (
            "A map using the Mercator projection cannot predate 1569. Widespread use of "
            "Mercator for nautical charts is consistent with the 17th century and later."
        ),
    },
    "sinusoidal": {
        "id": "sinusoidal",
        "label": "Sinusoidal (Sanson-Flamsteed / Mercator equal-area)",
        "invented": "c.1570 (attributed to Cini / later Sanson)",
        "inventor": "Cini / Nicolas Sanson",
        "use_period": "17th-18th century French school (Sanson, Flamsteed)",
        "description": "Equal-area; meridians are sine curves, parallels are straight.",
        "dating_implication": "Sinusoidal use points to 17th-18th c., especially French cartography.",
    },
    "bonne": {
        "id": "bonne",
        "label": "Bonne (pseudoconic equal-area)",
        "invented": "1752 (Rigobert Bonne)",
        "inventor": "Rigobert Bonne",
        "use_period": "Late 18th century (French marine/atlas cartography)",
        "description": "Equal-area pseudoconic; parallels are concentric arcs, meridians curved.",
        "dating_implication": "Use of the Bonne projection postdates 1752; common in late-18th-c. French atlases.",
    },
    "lambert_conformal_conic": {
        "id": "lambert_conformal_conic",
        "label": "Lambert conformal conic",
        "invented": "1772 (Johann Heinrich Lambert)",
        "inventor": "Johann Heinrich Lambert",
        "use_period": "19th-20th century national mapping (e.g. France, USA)",
        "description": "Conformal conic with two standard parallels.",
        "dating_implication": "Use of Lambert conformal conic postdates 1772; characteristic of modern state surveys.",
    },
    "robinson": {
        "id": "robinson",
        "label": "Robinson (pseudocylindrical compromise)",
        "invented": "1963 (Arthur H. Robinson)",
        "inventor": "Arthur H. Robinson",
        "use_period": "1963 onward (Rand McNally, NGS)",
        "description": "Compromise pseudocylindrical; tabulated coordinates, not a closed formula.",
        "dating_implication": "A Robinson-projection map postdates 1963 — a strong modern-date signal.",
    },
}

_PROJECTION_ENUM = list(PROJECTIONS.keys()) + ["all"]


class ProjectionTimelineTool(Tool):
    name = "projection_timeline"
    description = (
        "Look up the invention date, inventor, use period and dating implication of a "
        "map projection (e.g. mercator, conic, azimuthal). A projection is a terminus "
        "post quem: a map cannot predate the projection it uses."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for projection-timeline lookup.",
            {
                "projection": _string_schema(
                    "Projection id, or 'all' for the whole timeline.",
                    enum=_PROJECTION_ENUM,
                ),
                "map_year": _string_schema("Optional claimed/observed year of the map, for consistency check."),
            },
            required=["projection"],
        )
        output = _object_schema(
            "Projection-timeline result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "projections": _array_schema(_object_schema("A projection record.", {})),
                "consistency": _object_schema(
                    "If map_year was given, whether the projection could have been used by that year.",
                    {
                        "compatible": _string_schema("yes | no | unknown"),
                        "reason": _string_schema("Explanation of the compatibility verdict."),
                    },
                ),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        projection = (arguments.get("projection") or "all").strip().lower()
        if projection not in _PROJECTION_ENUM:
            raise ToolExecutionError(
                f"Unknown projection {projection!r}.",
                details={"valid": _PROJECTION_ENUM},
            )
        map_year = arguments.get("map_year")

        if projection == "all":
            records = [dict(v) for v in PROJECTIONS.values()]
        else:
            records = [dict(PROJECTIONS[projection])]

        consistency = {"compatible": "unknown", "reason": "No map_year supplied."}
        if map_year not in (None, "") and projection != "all":
            year = _parse_year(map_year)
            invented_year = _parse_year(PROJECTIONS[projection]["invented"])
            if year is not None and invented_year is not None:
                if year >= invented_year:
                    consistency = {
                        "compatible": "yes",
                        "reason": f"Map year {year} is on/after {projection} invention ({invented_year}).",
                    }
                else:
                    consistency = {
                        "compatible": "no",
                        "reason": (
                            f"Map claimed year {year} predates {projection} invention "
                            f"({invented_year}); either the year or the projection attribution is wrong."
                        ),
                    }

        ctx.state.setdefault("projection_queries", []).append(projection)
        return {
            "query": {"projection": projection, "map_year": map_year},
            "projections": records,
            "consistency": consistency,
        }


def _parse_year(value: Any) -> int | None:
    """Extract the first 3-4 digit year from a free-text string like '1569' or 'c.150 AD'."""
    text = str(value)
    # Look for a 3-4 digit number; handle 'AD'/'c.' prefixes and BCE by sign.
    import re

    match = re.search(r"(\d{3,4})\s*(AD|CE|BCE|BC)?", text, re.IGNORECASE)
    if not match:
        return None
    num = int(match.group(1))
    era = (match.group(2) or "").upper()
    if era in {"BC", "BCE"}:
        return -num
    return num
