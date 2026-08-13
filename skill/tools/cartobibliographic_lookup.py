"""CartobibliographicLookupTool — publisher/engraver & atlas reference.

Distilled from:
* Tooley (1978), *Tooley's Dictionary of Mapmakers*
* Koeman (1967-71) / van der Krogt (1997-2011), *Atlantes Neerlandici*
* Karrow (1993), *Mapmakers of the Sixteenth Century*
* Goss (1990), *Blaeu's The Grand Atlas*

Supports cartobibliographic state/edition identification and
publisher/engraver attribution: match by maker/publisher surname or atlas
title. Returns active period, key atlases, plate-acquisition history, and
state/edition identification notes.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..base import Tool, ToolSchema
from ..context import SkillContext
from .base import _array_schema, _object_schema, _string_schema


MAKERS: list[dict[str, Any]] = [
    {
        "id": "ortelius",
        "name": "Abraham Ortelius",
        "active": "1547-1598",
        "role": "cartographer / publisher (Antwerp)",
        "key_works": ["Theatrum Orbis Terrarum (1570, first modern atlas)"],
        "plate_history": "Theatrum plates later acquired by the Plantin/Moretus firm and by Jan Baptist Vrients.",
        "state_edition_notes": (
            "Theatrum editions expand over time: the 1570 editio princeps has 53 maps; later "
            "editions add maps, so map-count and map set identify edition tightly."
        ),
        "attribution_keywords": ["ortelius", "theatrum", "epitome"],
    },
    {
        "id": "mercator",
        "name": "Gerardus Mercator",
        "active": "1537-1594",
        "role": "cartographer / engraver (Duisburg)",
        "key_works": ["World map of 1569 (Mercator projection)", "Atlas sive Cosmographicae Meditationes (1595, posthumous)"],
        "plate_history": "Mercator's atlas plates were sold to Jodocus Hondius (c.1604) and re-issued.",
        "state_edition_notes": (
            "Post-1604 'Mercator-Hondius' editions are re-issues; the title-page and Hondius's "
            "engraved maps distinguish them from the 1595 Mercator original."
        ),
        "attribution_keywords": ["mercator", "atlas sive", "hondius"],
    },
    {
        "id": "hondius",
        "name": "Jodocus Hondius (and family)",
        "active": "1587-1629 (Jodocus); continued by Hendrik",
        "role": "engraver / publisher (Amsterdam)",
        "key_works": ["Mercator-Hondius Atlas (1606 onward)", "Atlas Minor"],
        "plate_history": "Acquired Mercator plates c.1604; added his own maps. Later plates passed to Janssonius.",
        "state_edition_notes": "Hondius name on title-page + Mercator-Hondius maps = 1606 onward editions.",
        "attribution_keywords": ["hondius", "mercator-hondius", "atlas minor"],
    },
    {
        "id": "blaue",
        "name": "Willem Jansz. Blaeu / Joan Blaeu",
        "active": "1596-1673 (firm)",
        "role": "publisher / cartographer (Amsterdam)",
        "key_works": ["Novus Atlas (1635 onward)", "Atlas Maior (1662-1665)"],
        "plate_history": "Bought Hondius plates c.1629; Joan Blaeu expanded to Atlas Maior.",
        "state_edition_notes": (
            "Atlas Maior 1662-65 is the high point; the firm's plates were largely sold after the "
            "1672 fire and the firm's decline. Volume-count identifies edition."
        ),
        "attribution_keywords": ["blaeu", "blauw", "novus atlas", "atlas maior"],
    },
    {
        "id": "janssonius",
        "name": "Jan Janssonius",
        "active": "1612-1664",
        "role": "publisher (Amsterdam)",
        "key_works": ["Atlas Novus / Atlas Maior (11-volume, 1657-58)"],
        "plate_history": "Inherited/acquired Hondius plates; rival of Joan Blaeu.",
        "state_edition_notes": "Janssonius maps closely mimic Blaeu; title-page and cartouche signatures distinguish them.",
        "attribution_keywords": ["janssonius", "jansson", "atlas novus"],
    },
    {
        "id": "sanson",
        "name": "Nicolas Sanson (and heirs)",
        "active": "1627-1667 (Nicolas); firm into early 18th c.",
        "role": "cartographer (Paris)",
        "key_works": ["Cartes générales de toutes les parties du monde (1654)"],
        "plate_history": "Sanson plates passed to Hubert Jaillot and then to the De Vaugondy firm.",
        "state_edition_notes": "Sanson's sinusoidal projection and Paris cartouche style are period markers (mid-17th c.).",
        "attribution_keywords": ["sanson", "jaillot", "cartes générales"],
    },
    {
        "id": "homann",
        "name": "Johann Baptist Homann (and heirs)",
        "active": "1702-1763 (firm to c.1848)",
        "role": "publisher (Nuremberg)",
        "key_works": ["Grosser Atlas (c.1716 onward)"],
        "plate_history": "Heirs continued as 'Homann Heirs' from 1730.",
        "state_edition_notes": "'Homann Heirs' imprint dates a map to post-1730; 'J.B. Homann' imprint to c.1702-1730.",
        "attribution_keywords": ["homann", "homann heirs", "grosser atlas"],
    },
    {
        "id": "seutter",
        "name": "Matthäus Seutter",
        "active": "1707-1757",
        "role": "engraver / publisher (Augsburg)",
        "key_works": ["Atlas Novus (c.1730)"],
        "plate_history": "Trained with Homann; acquired/re-cut many plates.",
        "state_edition_notes": "Augsburg imprint + Seutter cartouche = c.1707-1757; heirs continued briefly.",
        "attribution_keywords": ["seutter", "augsburg", "atlas novus"],
    },
    {
        "id": "coronelli",
        "name": "Vincenzo Coronelli",
        "active": "1678-1718",
        "role": "cosmographer (Venice)",
        "key_works": ["Atlante Veneto (1690-1701)", "Corso geografico"],
        "plate_history": "Founder of the Accademia degli Argonauti; large globes for Louis XIV.",
        "state_edition_notes": "Venice imprint + Atlante Veneto = 1690-1701 window.",
        "attribution_keywords": ["coronelli", "atlante veneto", "argonauti"],
    },
]


class CartobibliographicLookupTool(Tool):
    name = "cartobibliographic_lookup"
    description = (
        "Look up a map publisher/engraver or atlas by name (e.g. 'Blaeu', 'Ortelius', "
        "'Mercator-Hondius'). Returns active period, key works, plate-acquisition history, "
        "and state/edition identification notes for cartobibliographic attribution."
    )

    def schema(self) -> ToolSchema:
        params = _object_schema(
            "Arguments for cartobibliographic lookup.",
            {
                "maker": _string_schema("Publisher/engraver surname or name fragment to match."),
                "atlas": _string_schema("Atlas title fragment to match (e.g. 'Theatrum', 'Atlas Maior')."),
            },
        )
        output = _object_schema(
            "Cartobibliographic lookup result.",
            {
                "query": _object_schema("Echo of the query.", {}),
                "matches": _array_schema(_object_schema("A matched maker record.", {})),
                "match_count": _string_schema("Number of matches."),
            },
        )
        return ToolSchema(self.name, self.description, params, output)

    def run(self, arguments: Mapping[str, Any], *, ctx: SkillContext) -> dict[str, Any]:
        maker = str(arguments.get("maker") or "").strip().lower()
        atlas = str(arguments.get("atlas") or "").strip().lower()

        matches: list[dict[str, Any]] = []
        for record in MAKERS:
            haystacks = [
                str(record.get("name", "")).lower(),
                str(record.get("id", "")).lower(),
                *record.get("attribution_keywords", []),
                *record.get("key_works", []),
            ]
            blob = " ".join(haystacks)
            if maker and maker not in blob:
                continue
            if atlas and atlas not in blob:
                continue
            if not maker and not atlas:
                continue
            matches.append(dict(record))

        ctx.state.setdefault("cartobibliographic_queries", []).append(
            {"maker": maker, "atlas": atlas}
        )
        return {
            "query": {"maker": maker, "atlas": atlas},
            "matches": matches,
            "match_count": len(matches),
        }
