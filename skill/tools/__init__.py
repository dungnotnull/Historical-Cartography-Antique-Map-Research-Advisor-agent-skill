"""Tools the sub-advisors can invoke dynamically.

Each tool exposes a JSON-Schema (``ToolSchema``) and a pure-Python handler.
The handlers encode compact, verified reference tables distilled from the
sources in ``SECOND-BRAIN-KNOWLEDGE-PAPER.md``; they return deterministic,
structured data so advisor output stays reproducible across runs.
"""
from __future__ import annotations

from .base import _object_schema, _string_schema
from .validation import validate_arguments
from .cartobibliographic_lookup import CartobibliographicLookupTool
from .print_technique_lookup import PrintTechniqueLookupTool
from .projection_timeline import ProjectionTimelineTool
from .toponym_lookup import ToponymLookupTool
from .watermark_lookup import WatermarkLookupTool
from .material_analysis_lookup import MaterialAnalysisLookupTool

__all__ = [
    "PrintTechniqueLookupTool",
    "ProjectionTimelineTool",
    "ToponymLookupTool",
    "WatermarkLookupTool",
    "CartobibliographicLookupTool",
]

