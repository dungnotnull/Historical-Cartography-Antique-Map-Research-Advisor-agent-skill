"""LLM client abstraction with a deterministic fallback engine.

The skill is designed to *always* produce structured, auditable output. When
no model is reachable (or ``LLMParams.fallback_on_error`` is set), the
:class:`FallbackEngine` synthesises an :class:`AdvisorResult` deterministically
from the sub-advisor's own keyword/tool logic — so the registry pipeline
never dead-ends on a provider outage.
"""
from __future__ import annotations

from .client import LLMClient, get_llm_client
from .fallback import FallbackEngine

__all__ = ["LLMClient", "get_llm_client", "FallbackEngine"]
