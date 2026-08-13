"""Tests for the stdlib LLM provider adapter and fallback synthesis path."""
from __future__ import annotations

import unittest
from unittest import mock

from config import LLMParams


class TestAnthropicProvider(unittest.TestCase):
    def test_missing_api_key_raises(self) -> None:
        from skill.llm.providers import AnthropicProvider
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                AnthropicProvider()(system="s", user="u", params=LLMParams(provider="anthropic"))

    def test_register_default_providers(self) -> None:
        from skill.llm import client as client_mod
        client_mod._PROVIDERS.clear()
        from skill.llm.providers import register_default_providers
        register_default_providers()
        self.assertIn("anthropic", client_mod._PROVIDERS)
        self.assertIn("openai", client_mod._PROVIDERS)

    def test_openai_missing_api_key_raises(self) -> None:
        from skill.llm.providers import OpenAIProvider
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(RuntimeError):
                OpenAIProvider()(system="s", user="u", params=LLMParams(provider="openai"))


class TestRouterSynthesis(unittest.TestCase):
    def test_synthesis_empty_with_fallback(self) -> None:
        from skill.router import HistoricalCartographyRouter
        report = HistoricalCartographyRouter().execute("A Blaeu copper engraving map.")
        self.assertEqual(report.synthesis, "")
        self.assertIn("synthesis", report.to_dict())


if __name__ == "__main__":
    unittest.main()
