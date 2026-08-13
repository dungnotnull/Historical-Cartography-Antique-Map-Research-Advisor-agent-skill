"""Tests for the type-safe configuration layer."""
from __future__ import annotations

import os
import unittest

from config import FeatureFlags, LLMParams, Settings, load_settings
from config.settings import ConfigError


class TestLLMParams(unittest.TestCase):
    def test_defaults_valid(self) -> None:
        p = LLMParams()
        self.assertEqual(p.provider, "fallback")
        self.assertGreater(p.max_tokens, 0)

    def test_invalid_temperature_rejected(self) -> None:
        with self.assertRaises(ConfigError):
            LLMParams(temperature=5.0)

    def test_negative_retries_rejected(self) -> None:
        with self.assertRaises(ConfigError):
            LLMParams(max_retries=-1)


class TestFeatureFlags(unittest.TestCase):
    def test_defaults_strict_disclaimer(self) -> None:
        f = FeatureFlags()
        self.assertTrue(f.strict_disclaimer_mode)
        self.assertTrue(f.enable_authentication_referral_guard)

    def test_invalid_concurrency_rejected(self) -> None:
        with self.assertRaises(ConfigError):
            FeatureFlags(max_concurrent_sub_advisors=0)


class TestSettings(unittest.TestCase):
    def test_environment_validation(self) -> None:
        with self.assertRaises(ConfigError):
            Settings(environment="mars")

    def test_log_level_normalised(self) -> None:
        s = Settings(log_level="info")
        self.assertEqual(s.log_level, "INFO")

    def test_with_overrides_immutable(self) -> None:
        s = load_settings()
        s2 = s.with_overrides(environment="test")
        self.assertEqual(s2.environment, "test")
        self.assertNotEqual(s.environment, s2.environment)

    def test_env_override(self) -> None:
        old = os.environ.get("HCRA_ENV")
        os.environ["HCRA_ENV"] = "test"
        try:
            self.assertEqual(load_settings().environment, "test")
        finally:
            if old is None:
                os.environ.pop("HCRA_ENV", None)
            else:
                os.environ["HCRA_ENV"] = old


if __name__ == "__main__":
    unittest.main()
