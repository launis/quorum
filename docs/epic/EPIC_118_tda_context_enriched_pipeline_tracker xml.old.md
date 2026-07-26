# EPIC 118: TDA Context-Enriched Decompose-Verify Pipeline Tracker

**Epic Reference**: `@[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]`
**Task Directory**: `@[c:\src\quorum\docs\epic\tasks_EPIC_118/]`

## Phase Execution Status

### Phase 1: Backend Domain Models & Service Engine Hardening
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_models_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_models_plan.md]`

### Phase 2 & 4: Orchestration, Registry & Prompt Compiler Updates
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_plan.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend and Frontend full-stack integration test gates.

### Phase 5: Dual-Axis Documentation Update (EPIC 115 Compliance)
- [ ] **[NOK]** `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\03_documentation_plan.md]`
- [ ] **[NOK]** `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\03_documentation_plan.md]`

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` backend files. NEVER specify whole directories.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` Flutter files. NEVER specify whole directories.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for new SSOTs in `<appDataDir>/knowledge/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent
- Atomic commit mandates MUST be strictly followed after EVERY successful quality gate pass.
- If seeding is required, use the command: `uv run python backend_v2/seed/run_seed.py local`.
- You MUST use explicit `@-reference` syntax for all target files.
- You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.

## Requirements Traceability Matrix

| Requirement | Epic Source | Handled In |
|-------------|-------------|------------|
| Move `FlattenedAtom` to DTO layer | Phase 1 | `01_backend_models_plan.md` |
| `EngineExecutionRequest` adds `shuffled_atoms` | Phase 1 | `01_backend_models_plan.md` |
| Unconditional fail-fast key access for `shuffled_atoms` | Phase 2 | `02_orchestration_plan.md` |
| Implement Context-Enriched Pipeline (Phase 0+1) | Phase 2 | `02_orchestration_plan.md` |
| Verification & E2E Integration Gate | Phase 4 | `02_orchestration_plan.md` |
| KI Creation & Architecture sync | Phase 5 | `03_documentation_plan.md` |

# Session Handover Context
## Achieved
- Broken down EPIC 118 into 3 micro-chunked implementation plans.
- Generated standard Epic Tracker with traceability matrix and execution phases.

## Learned
- None yet.

## Remaining
- Execute Phase 1: Backend Domain Models & Service Engine Hardening.

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_models_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md]"`
