# Historical Cartography & Antique Map Research Advisor

> A modular, registry-driven Claude Skill for analyzing, dating, and researching historical maps — grounded in established cartographic-history methodology (print-technique dating, cartobibliography, map-projection history, historical toponymy, provenance/materials analysis).

**Category:** Historical Cartography (disclaimer required)
**Version:** 1.0.0
**Status:** Built and verified — 43 tests passing.

> **Disclaimer:** This skill provides general, educational, and analytical information only. It is **not** a certified authentication, appraisal, or valuation. Formal authentication or valuation of a significant antique map must be verified by an **accredited map appraiser or cartographic-history specialist**. Do not make financial or collecting decisions solely on its output.

---

## Overview

The skill supports map collectors, historians, and researchers in analyzing and researching historical maps using five core methodologies, with an always-on guard that flags when an accredited specialist must be consulted. It is implemented as a **chain-of-thought router** dispatching to **specialized sub-advisors** through a **skill registry**, with reusable **tools**, **hooks**, and a graceful **LLM fallback engine** so structured, auditable output is always produced — even with no model reachable.

## Architecture (chain-of-thought router + skill-registry pattern)

```
User prompt → HistoricalCartographyRouter (CoT routing)
                → SkillRegistry (resolve advisors/tools/hooks)
                  → 5 methodology sub-advisors + 1 always-on auth-referral guard
                    → 6 deterministic lookup tools (JSON-schema + handlers)
                  → HookBus (lifecycle logging + state-snapshot audit trail)
                → AggregatedReport (disclaimer + referral + findings)
                  → LLM client (provider-agnostic) + deterministic FallbackEngine
```

See `assets/diagrams/architecture.md` for the full Mermaid diagram, and `SKILL.md` for the complete registry documentation (registration, resolution, execution, validation, I/O schemas).

## Core capabilities

- **Print-technique dating** — woodcut → copper engraving → etching → steel engraving → lithography chronology (terminus post quem).
- **Cartobibliography** — state/edition/issue identification + publisher/engraver attribution (Ortelius, Mercator, Hondius, Blaeu, Janssonius, Sanson, Homann, Seutter, Coronelli).
- **Map-projection history** — projection as a terminus postquem (Mercator 1569, Bonne 1752, Lambert 1772, Robinson 1963, …) with year-consistency checks.
- **Historical toponymy & boundary history** — dated place-name changes as a dating aid (New Amsterdam→New York 1664, Petrograd 1914-24, etc.).
- **Provenance & materials** — watermark analysis, ownership-mark research, paper/ink material-analysis principles.
- **Authentication & referral guard** — always-on; flags accredited-specialist referral on any authentication/valuation intent.

## Project layout

| Path | Purpose |
|---|---|
| `SKILL.md` | Skill-registry documentation (centerpiece) |
| `CLAUDE.md` | Operating instructions for Claude |
| `PROJECT-detail.md` | Functional specification |
| `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` | Phase tracker (100% complete) |
| `SECOND-BRAIN-KNOWLEDGE-PAPER.md` | Curated source knowledge base |
| `config/` | Type-safe settings, feature flags, LLM params |
| `skill/` | Registry, router, `agents/`, `hooks/`, `tools/`, `llm/` |
| `references/` | 7 domain docs + `prompts/` (4 report templates) |
| `assets/` | `schemas/` (7 JSON schemas) + `diagrams/` |
| `scripts/` | setup, seed, ingest, validate, run_tests, demo_cli |
| `tests/` | unittest suite (43 tests) |

## Getting started

```bash
python scripts/setup_env.py            # verify setup + imports
python scripts/demo_cli.py "..."       # run the router on a question
python scripts/validate_schemas.py     # validate schemas + registry manifest
python scripts/run_tests.py            # run the 32-test suite
python scripts/seed_knowledge_base.py  # index references/ for RAG grounding
```

The skill runs on the Python standard library alone; `PyYAML` and `jsonschema` are optional extras for richer config parsing and strict schema validation.

## Configuration

Type-safe, immutable, validated configuration in `config/settings.py`, loaded from `config/defaults.yaml` + `HCRA_*` environment variables. See `SKILL.md` §8 for the full knob table.

## License

MIT (see `pyproject.toml`).
