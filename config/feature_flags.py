"""Re-export module for feature-flag access ergonomics.

The canonical definition lives in :mod:`config.settings`; this module exists
so callers can write ``from config.feature_flags import FeatureFlags`` without
importing the whole settings graph, and provides a small helper to read the
effective flag set at runtime.
"""
from __future__ import annotations

from .settings import FeatureFlags, Settings, load_settings

__all__ = ["FeatureFlags", "current_feature_flags"]


def current_feature_flags() -> FeatureFlags:
    """Return the feature-flag block of the currently-loaded :class:`Settings`."""
    return load_settings().flags
