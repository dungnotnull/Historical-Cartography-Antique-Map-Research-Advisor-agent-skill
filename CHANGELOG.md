# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] — 2026-08-11

### Added
- Modular skill-registry architecture with a chain-of-thought router
  (`skill/router.py`, `skill/registry.py`).
- Six specialized sub-advisors: print-technique dating, cartobibliography,
  projection history, toponymy/boundary, provenance/materials, and an
  always-on authentication-referral guard (`skill/agents/`).
- Six deterministic lookup tools with JSON schemas and pure-Python handlers:
  `print_technique_lookup`, `projection_timeline`, `toponym_lookup`,
  `watermark_lookup`, `cartobibliographic_lookup`, `material_analysis_lookup`
  (`skill/tools/`).
- Lifecycle + state-snapshot hooks with a JSONL audit trail (`skill/hooks/`).
- Provider-agnostic LLM client with a deterministic fallback engine
  (`skill/llm/`).
- Type-safe, immutable, validated configuration with env-var overrides
  (`config/`).
- Seven reference docs + four report prompt templates (`references/`).
- Seven JSON schemas + an architecture diagram (`assets/`).
- Six automation scripts: setup, seed, ingest, validate, run_tests, demo_cli
  (`scripts/`).
- `RESEARCH-PAPER-KNOWLEDGE-BRAIN.md` — 30 cited sources mapped to concrete
  project data points.
- Comprehensive `SKILL.md` registry documentation.
- 36-test unittest suite.

### Security / Safety
- Standing disclaimer enforced on every substantive response; strict mode
  refuses requests to drop the disclaimer.
- Always-on accredited-specialist referral guard for authentication/valuation
  intent.

### Fixed
- Negation-aware print-technique feature matching (`"platemark"` no longer
  matches `"No platemark"`).
- Regex-based disclaimer-skip detection (handles filler words).
- UTF-8 BOM stripping on JSON schemas.
- `material_analysis_lookup` tool import + advisor wiring.

## [Unreleased]
- Stdlib HTTP LLM provider adapter.
- Schema-based tool-argument validation.
