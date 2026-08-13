"""Re-export module for LLM-parameter access ergonomics."""
from __future__ import annotations

from .settings import LLMParams, Settings, load_settings

__all__ = ["LLMParams", "current_llm_params"]


def current_llm_params() -> LLMParams:
    """Return the LLM-parameter block of the currently-loaded :class:`Settings`."""
    return load_settings().llm
