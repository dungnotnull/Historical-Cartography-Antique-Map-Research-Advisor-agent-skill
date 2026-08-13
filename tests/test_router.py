"""Tests for the registry and router."""
from __future__ import annotations

import unittest

from skill.registry import SkillRegistry, get_registry
from skill.router import HistoricalCartographyRouter
from skill.errors import RoutingError, ToolNotFoundError


class TestRegistry(unittest.TestCase):
    def test_default_registry_populated(self) -> None:
        r = get_registry()
        self.assertEqual(len(r.advisors()), 6)
        self.assertEqual(len(r.tools()), 6)
        self.assertGreaterEqual(len(r.hooks()), 2)

    def test_unknown_advisor_raises(self) -> None:
        r = get_registry()
        with self.assertRaises(RoutingError):
            r.advisor("does_not_exist")

    def test_unknown_tool_raises(self) -> None:
        r = get_registry()
        with self.assertRaises(ToolNotFoundError):
            r.tool("does_not_exist")

    def test_describe_serialisable(self) -> None:
        import json
        r = get_registry()
        json.dumps(r.describe())  # must not raise


class TestRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.router = HistoricalCartographyRouter()

    def test_execute_returns_report_with_disclaimer(self) -> None:
        report = self.router.execute("A woodcut map labelled Constantinople.")
        d = report.to_dict()
        self.assertTrue(d["disclaimer"])
        self.assertIn("authentication_referral", d["routing"]["selected_advisors"])

    def test_authentication_intent_triggers_referral(self) -> None:
        report = self.router.execute("Is my Blaeu map genuine and what is it worth?")
        d = report.to_dict()
        self.assertTrue(d["requires_professional_referral"])
        self.assertGreater(len(d["authentication_triggers"]), 0)

    def test_no_intent_still_has_guard(self) -> None:
        report = self.router.execute("Tell me about Mercator projection history.")
        d = report.to_dict()
        self.assertFalse(d["requires_professional_referral"])
        self.assertTrue(d["disclaimer"])
        self.assertIn("authentication_referral", d["routing"]["selected_advisors"])

    def test_relevant_advisors_selected(self) -> None:
        report = self.router.execute("Copper engraving with a platemark, by Blaeu.")
        ids = report.to_dict()["routing"]["selected_advisors"]
        self.assertIn("print_technique_dating", ids)
        self.assertIn("cartobibliography", ids)


if __name__ == "__main__":
    unittest.main()

