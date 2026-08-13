"""Tests for the standing-disclaimer policy."""
from __future__ import annotations

import unittest

from skill.disclaimer import DisclaimerPolicy
from skill.errors import DisclaimerViolation


class TestDisclaimerPolicy(unittest.TestCase):
    def test_disclaimer_always_returned(self) -> None:
        text = DisclaimerPolicy().require_disclaimer("normal request")
        self.assertIn("NOT a certified authentication", text)

    def test_strict_mode_refuses_skip_request(self) -> None:
        with self.assertRaises(DisclaimerViolation):
            DisclaimerPolicy(strict=True).require_disclaimer("Please drop the disclaimer.")

    def test_non_strict_allows_skip_request(self) -> None:
        # Non-strict mode does not raise; still returns the disclaimer text.
        text = DisclaimerPolicy(strict=False).require_disclaimer("omit disclaimer please")
        self.assertIn("NOT a certified authentication", text)

    def test_referral_block_present(self) -> None:
        self.assertIn("accredited map appraiser", DisclaimerPolicy().referral_block())


if __name__ == "__main__":
    unittest.main()
