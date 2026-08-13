"""ToponymLookupTool — historical toponymy / place-name change reference.

Distilled from general cartographic-history knowledge and the applied
case-study sources in SECOND-BRAIN-KNOWLEDGE-PAPER.md (e.g. Edney on British
India; Barber/Harper on political content). Place-name changes are a strong
dating aid: a map using an old toponym postdates that toponym's introduction
and predates (or overlaps) its official replacement.

The handler matches either a place name (returning its historical variants
with date ranges) or a region (returning the toponym changes within it).
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from .base import _array_schema, _object_schema, _string_schema


# Each entry: a place with chronologically ordered name variants.
TOPONYMS: list[dict[str, Any]] = [
    {
        "place": "New York City (USA)",
        "region": "North America",
        "variants": [
            {"name": "New Amsterdam", "period": "1624-1664", "note": "Dutch colonial name."},
            {"name": "New York", "period": "1664 onward", "note": "Renamed after English capture in 1664."},
        ],
        "dating_rule": "A map labelled 'New Amsterdam' dates to 1624-1664; 'New York' to 1664 onward.",
    },
    {
        "place": "Istanbul (Turkey)",
        "region": "Middle East / Anatolia",
        "variants": [
            {"name": "Constantinople", "period": "c.330-1930 (official Western use)", "note": "Roman/Byzantine/Ottoman Western name."},
            {"name": "Istanbul", "period": "officially 1930 onward", "note": "Turkish postal service adopted 'Istanbul' officially in 1930."},
        ],
        "dating_rule": "'Constantinople' on a Western map is consistent with pre-1930; 'Istanbul' official usage is post-1930.",
    },
    {
        "place": "Iran (Persia)",
        "region": "Middle East",
        "variants": [
            {"name": "Persia", "period": "Western usage to 1935", "note": "Reza Shah requested foreign use of 'Iran' in 1935."},
            {"name": "Iran", "period": "1935 onward (Western official)", "note": "Adopted gradually in Western cartography from 1935."},
        ],
        "dating_rule": "Western maps labelled 'Persia' pre-1935; 'Iran' from c.1935.",
    },
    {
        "place": "Sri Lanka",
        "region": "South Asia",
        "variants": [
            {"name": "Ceylon", "period": "1815-1972", "note": "British colonial and dominion name."},
            {"name": "Sri Lanka", "period": "1972 onward", "note": "Republic name adopted 1972."},
        ],
        "dating_rule": "'Ceylon' on a map is consistent with 1815-1972; 'Sri Lanka' post-1972.",
    },
    {
        "place": "Mumbai (India)",
        "region": "South Asia",
        "variants": [
            {"name": "Bombay", "period": "c.1661-1995", "note": "British colonial / state name."},
            {"name": "Mumbai", "period": "1995 onward", "note": "Renamed by Maharashtra state government in 1995."},
        ],
        "dating_rule": "'Bombay' consistent with pre-1995; 'Mumbai' post-1995.",
    },
    {
        "place": "Saint Petersburg (Russia)",
        "region": "Eastern Europe",
        "variants": [
            {"name": "Saint Petersburg", "period": "1703-1914", "note": "Founded by Peter the Great 1703."},
            {"name": "Petrograd", "period": "1914-1924", "note": "Renamed at WWI onset (anti-German sentiment)."},
            {"name": "Leningrad", "period": "1924-1991", "note": "Renamed after Lenin's death."},
            {"name": "Saint Petersburg", "period": "1991 onward", "note": "Restored after USSR dissolution."},
        ],
        "dating_rule": "Four distinct labels: Petrograd=1914-1924, Leningrad=1924-1991 — a tight dating axis.",
    },
    {
        "place": "Mexico (former Viceroyalty)",
        "region": "North America",
        "variants": [
            {"name": "New Spain", "period": "1521-1821", "note": "Spanish colonial viceroyalty."},
            {"name": "Mexico (independent)", "period": "1821 onward", "note": "Independence 1821."},
        ],
        "dating_rule": "'New Spain' on a map = 1521-1821; independent 'Mexico' post-1821.",
    },
    {
        "place": "Dutch Republic",
        "region": "Western Europe",
        "variants": [
            {"name": "United Provinces / Republic of the Seven United Netherlands", "period": "1581-1795", "note": "Dutch Republic."},
            {"name": "Batavian Republic", "period": "1795-1806", "note": "French client state."},
            {"name": "Kingdom of Holland", "period": "1806-1810", "note": "Under Louis Bonaparte."},
        ],
        "dating_rule": "United Provinces labeling = 1581-1795; useful for dating Dutch golden-age atlases.",
    },
    {
        "place": "Beijing (China)",
        "region": "East Asia",
        "variants": [
            {"name": "Peking / Beijing", "period": "varies by Western romanization", "note": "'Peking' common in Western maps pre-c.1979; 'Beijing' pinyin adopted c.1979."},
        ],
        "dating_rule": "Western 'Peking' spelling common pre-c.1979; 'Beijing' pinyin post-c.1979.",
    },
]


class ToponymLookupTool(Tool):
    name = "toponym_lookup"
    description = (
        "Look up historical place-name variants and their date ranges as a map-dating aid. "
        "Match by place name (e.g. 'Constantinople', 'Bombay') or by region "
        "(e.g. 'South Asia', 'Eastern Europe')."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for toponym lookup.",
            {
                "query": _string_schema("A place name or region to match (case-insensitive substring)."),
                "match_mode": _string_schema(
                    "How to interpret 'query'.",
                    enum=["auto", "place", "region"],
                ),
            },
            required=["query"],
        )
        output = _object_schema(
            "Toponym lookup result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "matches": _array_schema(_object_schema("A matched toponym record with variants and a dating rule.", {})),
                "match_count": _string_schema("Number of matching toponym records."),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        query = str(arguments.get("query") or "").strip().lower()
        mode = (arguments.get("match_mode") or "auto").strip().lower()
        if not query:
            matches: list[dict[str, Any]] = []
        else:
            matches = [
                dict(record)
                for record in TOPONYMS
                if self._matches(record, query, mode)
            ]
        ctx.state.setdefault("toponym_queries", []).append(query)
        return {
            "query": {"query": query, "match_mode": mode},
            "matches": matches,
            "match_count": len(matches),
        }

    @staticmethod
    def _matches(record: dict[str, Any], query: str, mode: str) -> bool:
        place = str(record.get("place", "")).lower()
        region = str(record.get("region", "")).lower()
        variant_names = [str(v.get("name", "")).lower() for v in record.get("variants", [])]
        if mode == "place":
            return query in place or any(query in v for v in variant_names)
        if mode == "region":
            return query in region
        # auto: match anywhere
        return (
            query in place
            or query in region
            or any(query in v for v in variant_names)
        )
