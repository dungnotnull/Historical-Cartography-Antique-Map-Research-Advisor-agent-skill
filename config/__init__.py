"""Type-safe configuration management for the Historical Cartography Research Advisor.

Public surface:
    - :class:`Settings`  -- top-level, immutable configuration object
    - :class:`FeatureFlags`
    - :class:`LLMParams`
    - :func:`load_settings` -- builds a :class:`Settings` from env + defaults.yaml
"""
from __future__ import annotations

from .settings import FeatureFlags, LLMParams, Settings, load_settings

__all__ = ["Settings", "FeatureFlags", "LLMParams", "load_settings"]
