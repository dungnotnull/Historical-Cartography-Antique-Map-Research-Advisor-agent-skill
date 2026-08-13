# Architecture Diagram

```mermaid
flowchart TD
    User[User prompt] --> Router[HistoricalCartographyRouter<br/>chain-of-thought routing]
    Router -->|score & select| Reg[(SkillRegistry)]
    Reg --> Adv1[PrintTechniqueDatingAdvisor]
    Reg --> Adv2[CartobibliographyAdvisor]
    Reg --> Adv3[ProjectionHistoryAdvisor]
    Reg --> Adv4[ToponymyBoundaryAdvisor]
    Reg --> Adv5[ProvenanceMaterialsAdvisor]
    Reg --> AdvG[AuthenticationReferralAdvisor<br/>always-on guard]

    Adv1 -->|invoke| Tool1[print_technique_lookup]
    Adv2 -->|invoke| Tool2[cartobibliographic_lookup]
    Adv3 -->|invoke| Tool3[projection_timeline]
    Adv4 -->|invoke| Tool4[toponym_lookup]
    Adv5 -->|invoke| Tool5[watermark_lookup]
    Adv5 -->|invoke| Tool6[material_analysis_lookup]

    Tools[/skill/tools/] --> Refs[(/references/<br/>7 domain docs + prompts)]
    Adv1 & Adv2 & Adv3 & Adv4 & Adv5 & AdvG --> Refs

    Router --> Hooks[HookBus]
    Hooks --> H1[LifecycleLoggerHook]
    Hooks --> H2[StateSnapshotHook .jsonl]

    Adv1 & Adv2 & Adv3 & Adv4 & Adv5 & AdvG -->|AdvisorResult| Router
    Router -->|aggregate| Report[AggregatedReport<br/>disclaimer + referral + findings]
    Report --> LLM[/skill/llm<br/>client + fallback engine]

    Config[/config settings + flags + llm params/] --> Router
    Config --> Adv1 & Adv2 & Adv3 & Adv4 & Adv5 & AdvG
    Config --> Tools
```

## Layer responsibilities

| Layer | Module | Role |
|---|---|---|
| Entry | `skill.router` | Classify intent, select advisors, aggregate report |
| Registry | `skill.registry` | Register/resolve/validate/invoke advisors, tools, hooks |
| Advisors | `skill/agents/` | 5 methodology sub-advisors + 1 always-on guard |
| Tools | `skill/tools/` | 6 deterministic lookup tools (JSON-schema + handlers) |
| Hooks | `skill/hooks/` | Lifecycle logging + state-snapshot audit trail |
| Config | `config/` | Env vars, LLM params, feature flags (immutable, validated) |
| LLM | `skill/llm/` | Provider-agnostic client + deterministic fallback engine |
| References | `references/` | 7 domain docs + 4 report prompt templates |
| Assets | `assets/` | JSON schemas + this diagram |

## Data flow (per request)
1. `SkillContext` built (request_id, settings, token budget, hook bus).
2. `Router.route()` scores advisors by keyword overlap → emits `RouterDecision` (auditable).
3. Each selected advisor runs `advise()`, invoking tools through the registry (audited).
4. The guard advisor runs unconditionally, enforcing the disclaimer/referral policy.
5. `Router.execute()` aggregates results, merges referral triggers, attaches disclaimer.
6. Hooks emit lifecycle/state events; `StateSnapshotHook` writes a JSONL audit trail.
7. On any LLM/provider failure, `FallbackEngine` returns a structured result — pipeline never dead-ends.
