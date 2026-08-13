"""Tests for the lookup tools."""
from __future__ import annotations

import unittest

from skill.context import SkillContext
from skill.errors import ToolExecutionError
from skill.tools import (
    CartobibliographicLookupTool,
    PrintTechniqueLookupTool,
    ProjectionTimelineTool,
    ToponymLookupTool,
    WatermarkLookupTool,
)


def _ctx() -> SkillContext:
    return SkillContext.for_prompt("test prompt")


class TestPrintTechniqueLookup(unittest.TestCase):
    def test_all_returns_five(self) -> None:
        r = PrintTechniqueLookupTool().run({"technique": "all"}, ctx=_ctx())
        self.assertEqual(len(r["techniques"]), 5)

    def test_platemark_excludes_woodcut_litho(self) -> None:
        r = PrintTechniqueLookupTool().run(
            {"technique": "all", "observed_features": ["platemark"]}, ctx=_ctx()
        )
        self.assertIn("copper_engraving", r["matched_by_feature"])
        self.assertNotIn("woodcut", r["matched_by_feature"])
        self.assertNotIn("lithography", r["matched_by_feature"])

    def test_unknown_technique_raises(self) -> None:
        with self.assertRaises(ToolExecutionError):
            PrintTechniqueLookupTool().run({"technique": "xyz"}, ctx=_ctx())


class TestProjectionTimeline(unittest.TestCase):
    def test_mercator_terminus_post_quem(self) -> None:
        r = ProjectionTimelineTool().run(
            {"projection": "mercator", "map_year": "1500"}, ctx=_ctx()
        )
        self.assertEqual(r["consistency"]["compatible"], "no")

    def test_mercator_compatible(self) -> None:
        r = ProjectionTimelineTool().run(
            {"projection": "mercator", "map_year": "1600"}, ctx=_ctx()
        )
        self.assertEqual(r["consistency"]["compatible"], "yes")


class TestToponymLookup(unittest.TestCase):
    def test_bombay_match(self) -> None:
        r = ToponymLookupTool().run({"query": "bombay"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 1)
        self.assertEqual(r["matches"][0]["place"], "Mumbai (India)")

    def test_region_match(self) -> None:
        r = ToponymLookupTool().run({"query": "South Asia", "match_mode": "region"}, ctx=_ctx())
        self.assertGreaterEqual(r["match_count"], 1)


class TestWatermarkLookup(unittest.TestCase):
    def test_posthorn(self) -> None:
        r = WatermarkLookupTool().run({"motif": "posthorn"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 1)
        self.assertEqual(r["matches"][0]["motif"], "posthorn")

    def test_year_filter(self) -> None:
        r = WatermarkLookupTool().run({"mill": "Amsterdam", "year": "1700"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 1)


class TestCartobibliographicLookup(unittest.TestCase):
    def test_blaeu_match(self) -> None:
        r = CartobibliographicLookupTool().run({"maker": "blaeu"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 1)
        self.assertIn("Blaeu", r["matches"][0]["name"])

    def test_empty_query_no_match(self) -> None:
        r = CartobibliographicLookupTool().run({}, ctx=_ctx())
        self.assertEqual(r["match_count"], 0)


class TestMaterialAnalysisLookup(unittest.TestCase):
    def test_all_returns_seven_records(self) -> None:
        from skill.tools import MaterialAnalysisLookupTool
        r = MaterialAnalysisLookupTool().run({"table": "all"}, ctx=_ctx())
        # 2 fibre + 2 paper_type + 3 pigment = 7
        self.assertEqual(r["match_count"], 7)

    def test_pigment_table(self) -> None:
        from skill.tools import MaterialAnalysisLookupTool
        r = MaterialAnalysisLookupTool().run({"table": "pigment"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 3)

    def test_wood_pulp_tpq(self) -> None:
        from skill.tools import MaterialAnalysisLookupTool
        r = MaterialAnalysisLookupTool().run({"table": "paper_fibre", "id": "wood_pulp"}, ctx=_ctx())
        self.assertEqual(r["match_count"], 1)
        self.assertIn("1850", r["records"][0]["date_range"])

    def test_unknown_table_raises(self) -> None:
        from skill.tools import MaterialAnalysisLookupTool
        from skill.errors import ToolExecutionError
        with self.assertRaises(ToolExecutionError):
            MaterialAnalysisLookupTool().run({"table": "xyz"}, ctx=_ctx())


if __name__ == "__main__":
    unittest.main()

