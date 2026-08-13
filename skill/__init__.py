"""Historical Cartography & Antique Map Research Advisor — skill package.

A modular, registry-driven skill implementation providing:

* a **chain-of-thought router** (:mod:`skill.router`) that classifies user
  intent and dispatches to the right specialised **sub-advisor**;
* a **skill registry** (:mod:`skill.registry`) so sub-advisors, tools and
  hooks are registered, resolved and validated uniformly;
* a set of **tools** (:mod:`skill.tools`) with JSON-schema definitions and
  executable handlers that sub-advisors can invoke dynamically;
* a set of **hooks** (:mod:`skill.hooks`) for lifecycle / state events;
* a graceful **LLM client** (:mod:`skill.llm`) with a deterministic fallback
  engine so the skill always produces structured, auditable output even when
  no model is reachable.

The package is deliberately dependency-light: the only optional runtime
dependency is ``PyYAML`` (for ``defaults.yaml``); everything else runs on the
Python standard library.
"""
from __future__ import annotations

from .context import SkillContext
from .registry import SkillRegistry, get_registry
from .router import RouterDecision, HistoricalCartographyRouter

__all__ = [
    "SkillContext",
    "SkillRegistry",
    "get_registry",
    "RouterDecision",
    "HistoricalCartographyRouter",
]

__version__ = "1.0.0"
