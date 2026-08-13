"""Tests for schema-based tool-argument validation."""
from __future__ import annotations

import unittest

from skill.errors import SchemaValidationError
from skill.tools import PrintTechniqueLookupTool, validate_arguments


class TestArgumentValidation(unittest.TestCase):
    def test_valid_args_pass(self) -> None:
        tool = PrintTechniqueLookupTool()
        # Must not raise.
        validate_arguments(tool, {"technique": "all"})

    def test_bad_enum_rejected(self) -> None:
        tool = PrintTechniqueLookupTool()
        with self.assertRaises(SchemaValidationError):
            validate_arguments(tool, {"technique": "bogus"})

    def test_missing_required_rejected(self) -> None:
        tool = PrintTechniqueLookupTool()
        with self.assertRaises(SchemaValidationError):
            validate_arguments(tool, {})

    def test_registry_invoke_validates(self) -> None:
        from skill.context import SkillContext
        from skill.registry import get_registry
        ctx = SkillContext.for_prompt("test")
        reg = get_registry()
        with self.assertRaises(SchemaValidationError):
            reg.invoke_tool("print_technique_lookup", {"technique": "bogus"}, ctx=ctx)


if __name__ == "__main__":
    unittest.main()
