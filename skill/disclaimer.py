"""Standing-disclaimer policy for the Historical Cartography skill.

This domain REQUIRES a standing disclaimer on every substantive response
(see CLAUDE.md and PROJECT-detail.md §4). The disclaimer is non-negotiable
in ``strict_disclaimer_mode``: even an explicit user request to drop it is
refused and an :class:`DisclaimerViolation` is recorded instead.
"""
from __future__ import annotations

from dataclasses import dataclass

from .errors import DisclaimerViolation


DISCLAIMER_TEXT = (
    "This analysis is general, educational, and analytical information about "
    "historical cartography; it is NOT a certified authentication, appraisal, "
    "or valuation. Formal authentication or valuation of a significant antique "
    "map must be verified by an accredited map appraiser or cartographic-history "
    "specialist. Do not make financial or collecting decisions solely on this output."
)

REFERRAL_TEXT = (
    "Action required: consult an accredited map appraiser or cartographic-history "
    "specialist before treating this map as authenticated or valued. Indicators "
    "triggering this referral are listed under 'authentication_triggers' in the report."
)


@dataclass(frozen=True)
class DisclaimerPolicy:
    strict: bool = True

    def require_disclaimer(self, user_request: str | None) -> str:
        """Return the mandatory disclaimer block.

        If the user explicitly asked to drop the disclaimer and ``strict`` is
        on, raise :class:`DisclaimerViolation` so the caller can record the
        refusal and still attach the disclaimer to the final output.
        """
        if user_request and self._asks_to_skip_disclaimer(user_request):
            if self.strict:
                raise DisclaimerViolation(
                    "User requested removal of the standing disclaimer; refused in strict mode.",
                    details={"user_request_fingerprint": "redacted"},
                )
        return DISCLAIMER_TEXT

    @staticmethod
    def _asks_to_skip_disclaimer(text: str) -> bool:
        import re
        lowered = text.lower()
        # Match a skip-verb optionally separated from "disclaimer" by filler words
        # like "the/this/that/your", so "drop the disclaimer" is caught as well
        # as "drop disclaimer".
        verbs = r"(?:skip|drop|remove|omit|exclude|leave out|don'?t include|do not include)"
        pattern = verbs + r"(?:\s+(?:the|this|that|your|any))?\s+disclaimer"
        if re.search(pattern, lowered):
            return True
        return "no disclaimer" in lowered or "without disclaimer" in lowered

    def referral_block(self) -> str:
        return REFERRAL_TEXT

