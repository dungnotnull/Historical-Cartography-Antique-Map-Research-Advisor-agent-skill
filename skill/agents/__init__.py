"""Specialized sub-advisors for the Historical Cartography skill.

Each sub-advisor owns one of the five core cartographic-research
methodologies (plus the always-on :class:`AuthenticationReferralAdvisor`
guard). Advisors are registered in :mod:`skill.registry` and dispatched by
the chain-of-thought router (:mod:`skill.router`).

Every advisor:

* declares ``methodologies``, ``keywords``, ``references`` and ``tools`` so
  the router can score relevance and the registry can validate the contract;
* implements :meth:`advise` returning a structured :class:`AdvisorResult`;
* invokes its declared tools through the registry (via the shared
  :func:`invoke_tool` helper) so tool usage is logged and audited;
* records evidence/findings with explicit references to the knowledge base;
* sets ``requires_professional_referral`` / ``authentication_triggers``
  whenever formal authentication or valuation signals appear.
"""
from __future__ import annotations

from .authentication_referral import AuthenticationReferralAdvisor
from .cartobibliography import CartobibliographyAdvisor
from .print_technique_dating import PrintTechniqueDatingAdvisor
from .projection_history import ProjectionHistoryAdvisor
from .provenance_materials import ProvenanceMaterialsAdvisor
from .toponymy_boundary import ToponymyBoundaryAdvisor
from .util import invoke_tool, mentions

__all__ = [
    "AuthenticationReferralAdvisor",
    "CartobibliographyAdvisor",
    "PrintTechniqueDatingAdvisor",
    "ProjectionHistoryAdvisor",
    "ProvenanceMaterialsAdvisor",
    "ToponymyBoundaryAdvisor",
    "invoke_tool",
    "mentions",
]
