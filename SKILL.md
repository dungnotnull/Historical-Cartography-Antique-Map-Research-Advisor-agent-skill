# SKILL.md — Historical Cartography & Antique Map Research Advisor

> A modular, registry-driven Claude Skill for analyzing, dating, and researching historical maps, grounded in established cartographic-history methodology.

**Version:** 1.0.0
**Domain:** Historical Cartography (disclaimer required)
**Registry entry schema:** `assets/schemas/skill.schema.json`

---

## 1. Skill identity

| Field | Value |
|---|---|
| `name` | historical-cartography-research-advisor |
| `version` | 1.0.0 |
| `domain` | Historical Cartography |
| `disclaimer_required` | `true` |
| `requires_python` | >=3.10 |
| `runtime_deps` | none (stdlib); optional `PyYAML`, `jsonschema` |

The skill supports map collectors, historians, and researchers in analyzing and researching historical maps using five core methodologies. It **explicitly disclaims** that formal authentication/valuation of a significant antique map must be verified by an **accredited map appraiser or cartographic-history specialist**.

---

## 2. How the skill is registered, resolved, executed, and validated

This skill uses a **modular skill-registry pattern** with a **chain-of-thought router** and **specialized sub-advisors**. The registry (`skill/registry.py`) is the single source of truth; the router (`skill/router.py`) is the entry point.

### 2.1 Registration
At first access, `get_registry()` calls `_register_defaults()` which registers, in order:
1. **Tools** (6) — each a `Tool` subclass with a `ToolSchema` (JSON-schema `parameters` + `output`) and a pure-Python `run()` handler.
2. **Sub-advisors** (6) — each a `SubAdvisor` subclass declaring `id`, `methodologies`, `keywords`, `references`, `tools`, and an `advise()` method.
3. **Hooks** (2) — each a `Hook` subclass subscribing to named events.

Registration is validated against the base-class contracts (`isinstance` checks) and uniqueness of `id`/`name`. Re-registering a name replaces the component (useful for hot-reloading references in dev).

### 2.2 Resolution
- `registry.advisor(id)` / `registry.tool(name)` — raise `RoutingError` / `ToolNotFoundError` with the list of available components on miss.
- `registry.hooks_for(event)` — returns hooks whose `events` is empty (subscribe-to-all) or contains `event`.
- `registry.invoke_tool(name, args, ctx)` — audited execution; emits `tool.invoke.start` / `tool.invoke.end` / `tool.invoke.error` events.

### 2.3 Execution (per request)
1. `SkillContext.for_prompt(prompt)` builds a per-request context: `request_id`, loaded `Settings`, structured logger, `TokenBudget`, hook bus, mutable `state`.
2. `Router.route(prompt)` scores each non-guard advisor by keyword overlap (`match_score` in `[0,100]`), selects every advisor with score > 0 (or the highest-scoring as best-effort fallback), and **always appends** the `AuthenticationReferralAdvisor` guard. It emits an explicit `RouterDecision` with a human-readable `rationale` and `reasoning_steps` (the chain of thought), so routing is auditable, not a black box.
3. `Router.execute(prompt)` runs each selected advisor's `advise()`, which may invoke tools through the registry. Per-advisor failures are caught and recorded as low-confidence fallback notes — a single advisor failure never aborts the request.
4. The router aggregates all `AdvisorResult`s, merges `authentication_triggers` across advisors, and attaches the **standing disclaimer**. In `strict_disclaimer_mode`, a user request to drop the disclaimer is refused and recorded as a `DisclaimerViolation`; the disclaimer is still attached.
5. Hooks emit lifecycle/state events; `StateSnapshotHook` writes a JSONL audit trail to `.skill_state/<request_id>.jsonl`.
6. If an LLM provider is configured (`config/llm_params.provider != "fallback"`) and a backend is registered via `register_provider()`, advisors may call `LLMClient.complete()`; on any failure (or when no backend is configured), `FallbackEngine` synthesises a structured result deterministically — **the pipeline never dead-ends**.

### 2.4 Validation
- `scripts/validate_schemas.py` parses every `assets/schemas/*.json`, builds the live registry manifest, and validates it against `skill.schema.json` + `tool.schema.json` + `hook.schema.json` (uses `jsonschema` if installed, else a built-in fallback validator).
- `scripts/run_tests.py` runs the `unittest` suite (43 tests).
- Every `ToolSchema` is JSON-serialisable (`registry.describe()` → `json.dumps` must not raise).

---

## 3. Sub-advisor registry

Each sub-advisor owns one methodology. The guard is appended to every request.

| `id` | Sub-advisor | Methodology | Tools | Key references |
|---|---|---|---|---|
| `print_technique_dating` | PrintTechniqueDatingAdvisor | Print-technique dating (woodcut→copper→steel→lithography chronology) | `print_technique_lookup` | Woodward 1975; Verner 1965; Woodward 1996 |
| `cartobibliography` | CartobibliographyAdvisor | Cartobibliography (state/edition/issue identification + attribution) | `cartobibliographic_lookup` | Tooley 1978; Koeman/van der Krogt; Karrow 1993; Goss 1990 |
| `projection_history` | ProjectionHistoryAdvisor | History of map projections (terminus post quem) | `projection_timeline` | Snyder 1993; History of Cartography |
| `toponymy_boundary` | ToponymyBoundaryAdvisor | Historical toponymy / place-name change + boundary history | `toponym_lookup` | Edney 1997; Barber & Harper 2010; Barber 2005 |
| `provenance_materials` | ProvenanceMaterialsAdvisor | Provenance research + paper/ink material analysis | `watermark_lookup`, `material_analysis_lookup` | Heawood 1932; Briquet 1907; Hunter 1978; Gettens & Stout 1966; IMCoS 2020 |
| `authentication_referral` | AuthenticationReferralAdvisor | Authentication/referral guard policy (always-on) | — | IMCoS 2020 |

---

## 4. Tool registry (input/output JSON schemas)

Each tool exposes a `ToolSchema` (`parameters` + `output`, JSON-Schema object shape) and a deterministic handler. Full schemas are emitted by `registry.describe()` and validated against `assets/schemas/tool.schema.json`.

### 4.1 `print_technique_lookup`
**Parameters**
```json
{
  "type": "object",
  "required": ["technique"],
  "properties": {
    "technique": { "type": "string", "enum": ["woodcut","copper_engraving","etching","steel_engraving","lithography","all"] },
    "observed_features": { "type": "array", "items": { "type": "string" } }
  }
}
```
**Output**
```json
{
  "type": "object",
  "properties": {
    "query": { "type": "object" },
    "techniques": { "type": "array", "items": { "type": "object" } },
    "matched_by_feature": { "type": "array", "items": { "type": "string" } }
  }
}
```

### 4.2 `projection_timeline`
**Parameters:** `projection` (enum: `ptolelemaic_conic`...`robinson`,`all`), `map_year?` (string).
**Output:** `projections[]` (id, invented, inventor, use_period, dating_implication) + `consistency` (`compatible`: `yes|no|unknown`, `reason`).

### 4.3 `toponym_lookup`
**Parameters:** `query` (string), `match_mode?` (`auto|place|region`).
**Output:** `matches[]` (place, region, variants[], dating_rule) + `match_count`.

### 4.4 `watermark_lookup`
**Parameters:** `motif?`, `mill?`, `year?` (strings).
**Output:** `matches[]` (motif, mills, date_range, dating_note, provenance_note) + `match_count`.

### 4.5 `cartobibliographic_lookup`
**Parameters:** `maker?`, `atlas?` (strings).
**Output:** `matches[]` (name, active, role, key_works, plate_history, state_edition_notes) + `match_count`.

### 4.6 `material_analysis_lookup`
**Parameters:** `table` (enum: `paper_fibre` | `paper_type` | `pigment` | `all`), `id?` (string).
**Output:** `records[]` (table, id, label, date_range/introduced, principle, dating_implication) + `match_count`.
Grounded in Hunter (1978), Whatman (wove c.1757), Gettens & Stout (1966): paper fibre (rag pre-c.1850 / wood-pulp post-c.1850), paper type (laid pre-c.1800 / wove c.1757+), pigment chronology (Prussian blue c.1704, chrome yellow c.1797, synthetic ultramarine 1828). Each is a terminus post quem for the paper or the colouring.

---

## 5. Hook registry

| `name` | events | effect |
|---|---|---|
| `lifecycle_logger` | `[]` (all) | structured-log every lifecycle event |
| `state_snapshot` | `advisor.end`, `router.decision`, `request.end` | append JSONL snapshot to `.skill_state/<request_id>.jsonl` |

Emitted events: `request.start`, `router.decision`, `advisor.start`, `advisor.end`, `advisor.error`, `tool.invoke.start`, `tool.invoke.end`, `tool.invoke.error`, `request.end`.

---

## 6. Output format (structured report)

The router returns an `AggregatedReport` (validated by `assets/schemas/map-dating-report.schema.json`):

```json
{
  "request_id": "...",
  "user_prompt_fingerprint": "14841541ebb6",
  "disclaimer": "This analysis is general... NOT a certified authentication...",
  "referral_block": "Action required: consult an accredited map appraiser...",
  "requires_professional_referral": true,
  "authentication_triggers": ["..."],
  "routing": { "request_id": "...", "rationale": "...", "selected_advisors": [...], "reasoning_steps": [...], "fallback_used": false },
  "advisor_results": [
    { "advisor": "print_technique_dating", "methodology": "...", "summary": "...",
      "evidence": [...], "findings": [...], "confidence": "medium",
      "requires_professional_referral": false, "authentication_triggers": [],
      "references_used": [...], "tools_invoked": ["print_technique_lookup"], "notes": [...] }
  ],
  "elapsed_ms": 4,
  "notes": []
}
```

Report templates for human-readable rendering live in `references/prompts/` (`map-dating-report.md`, `cartobibliographic-report.md`, `provenance-report.md`, `authentication-referral-memo.md`).

---

## 7. Mandatory disclaimer & guardrails

- Every substantive response carries the standing disclaimer (see `skill/disclaimer.py`).
- `strict_disclaimer_mode` (default `true`) refuses requests to drop the disclaimer.
- The `AuthenticationReferralAdvisor` is appended to **every** request and sets `requires_professional_referral` on any authentication/valuation/certification intent or significance marker.
- Never present output as a certified/professional determination; never issue a definitive judgment about a named individual; always flag when an accredited professional must be consulted.

---

## 8. Configuration

`config/settings.py` builds an immutable, validated `Settings` from `config/defaults.yaml` + `HCRA_*` environment variables. Key knobs:

| Setting | Env var | Default |
|---|---|---|
| `environment` | `HCRA_ENV` | `production` |
| `log_level` | `HCRA_LOG_LEVEL` | `INFO` |
| `llm.provider` | `HCRA_LLM_PROVIDER` | `fallback` (`anthropic`/`openai` optional via stdlib adapters) |
| `llm.model` | `HCRA_LLM_MODEL` | `claude-sonnet-4-5` |
| `flags.strict_disclaimer_mode` | `HCRA_FLAG_STRICT_DISCLAIMER` | `true` |
| `flags.enable_chain_of_thought_routing` | `HCRA_FLAG_COT_ROUTING` | `true` |
| `flags.enable_tool_invocation` | `HCRA_FLAG_TOOLS` | `true` |

Feature flags enable/disable: auth guard, CoT routing, tools, hooks, provenance, materials, structured logging, and the concurrency cap.

---

## 9. Getting started

```bash
# 1. Verify setup + imports
python scripts/setup_env.py

# 2. Run the demo CLI
python scripts/demo_cli.py "A copper-engraved Blaeu map with a platemark, labelled Constantinople."

# 3. Validate schemas + registry manifest
python scripts/validate_schemas.py

# 4. Run the test suite (43 tests)
python scripts/run_tests.py

# 5. (Re)index the references knowledge base
python scripts/seed_knowledge_base.py
```

---

## 10. Project layout

```
historical-cartography-research-advisor/
├── SKILL.md                  # this registry documentation
├── CLAUDE.md                 # operating instructions for Claude
├── README.md                 # project overview
├── PROJECT-detail.md         # functional specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md  # phase tracker
├── SECOND-BRAIN-KNOWLEDGE-PAPER.md        # source knowledge base
├── pyproject.toml / requirements.txt
├── config/                   # type-safe settings, feature flags, llm params
├── references/               # 7 domain docs + prompts/ (4 templates)
├── assets/                   # schemas/ (7 JSON schemas) + diagrams/
├── scripts/                  # setup, seed, ingest, validate, run_tests, demo_cli
├── skill/                    # registry, router, agents/, hooks/, tools/, llm/
└── tests/                    # unittest suite (43 tests)
```

---

## 11. Knowledge grounding

Reference files in `references/` distill the operational principles from `SECOND-BRAIN-KNOWLEDGE-PAPER.md` into concrete checklists and tables. Advisors cite their reference basis in every `AdvisorResult.references_used`, and tools encode compact verified tables (e.g. the projection-invention timeline, the watermark motif→date map, the toponym change table). Claims beyond the knowledge base are flagged as unsourced, per `CLAUDE.md`.
