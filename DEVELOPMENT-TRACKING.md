# DEVELOPMENT-TRACKING.md — Agent memory / build log

Working memory for the agent that built this skill. Mirrors `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` at a higher resolution for future maintenance.

## Decisions made
- **Architecture:** chose a modular **skill-registry pattern** with a **chain-of-thought router** and **specialized sub-advisors** over a single monolithic agent — auditable routing, per-methodology isolation, and uniform tool/hook lifecycle.
- **Always-on guard:** `AuthenticationReferralAdvisor` is appended to every request so the standing disclaimer + referral language can never be missing.
- **Resilience:** provider-agnostic `LLMClient` + deterministic `FallbackEngine` — the pipeline always returns a structured `AdvisorResult`, even with no model reachable.
- **Dependency policy:** stdlib-only runtime; `PyYAML` and `jsonschema` are optional extras. Tools encode compact verified reference tables so output is reproducible without external calls.

## Bugs found & fixed during the build
- `print_technique_lookup` feature matching: `"platemark"` substring-matched `"No platemark"` for woodcut/lithography. Fixed with negation-aware matching (`_feature_present`).
- `disclaimer._asks_to_skip_disclaimer`: only matched adjacent words, so `"drop the disclaimer"` was missed. Rewrote with a regex allowing filler words.
- JSON schema files written with a UTF-8 BOM by Windows `Set-Content -Encoding utf8`, breaking JSON parsing. Stripped BOMs via `System.Text.UTF8Encoding($false)`.
- `demo_cli.py` typo `args.compompact` → `args.compact`.
- `tool.schema.json` odd `{"const":"object"}` for the type field → cleaned to `"type":"string"`.

## Final verification
- `python scripts/validate_schemas.py` → all schemas OK (jsonschema=yes)
- `python scripts/run_tests.py` → Ran 43 tests — OK
- `python scripts/demo_cli.py` → structured report with disclaimer + referral triggers

## Future maintenance notes
- To add a new sub-advisor: subclass `SubAdvisor`, set `id/methodologies/keywords/references/tools`, implement `advise()`, and register in `skill/registry.py::_register_defaults`.
- To add a tool: subclass `Tool`, implement `schema()` + `run()`, register in `_register_defaults`.
- To add a hook: subclass `Hook`, set `events`, implement `handle()`, register in `_register_defaults`.
- Reference data lives in tool modules as compact tables; update there and in the matching `references/*.md` together to keep them consistent.
