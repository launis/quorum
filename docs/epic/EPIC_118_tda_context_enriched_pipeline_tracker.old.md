# EPIC 118: TDA Context-Enriched Decompose-Verify Pipeline — Tracker

> **Source Epic:** @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]
> **Task Directory:** @[c:\src\quorum\docs\epic\tasks_EPIC_118\]

---

## Phase Execution Status

### Phase 1: Backend Domain Models & DTO Hardening
- [ ] **[NOK]** Red-Teaming: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_dto_hardening_plan.md]`
- [ ] **[NOK]** Execute: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_dto_hardening_plan.md]`

### Phase 2: Orchestration & TDA Engine Context-Enriched Pipeline
- [ ] **[NOK]** Red-Teaming: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_tda_pipeline_plan.md]`
- [ ] **[NOK]** Execute: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_orchestration_tda_pipeline_plan.md]`

### Phase 3: Frontend Flutter UI & Freezed DTO Synchronization
- N/A — No frontend changes required. Backend-only change with no DTO parity impact.

### Phase 4: Verification & E2E Integration Gate
- [ ] **[NOK]** Full backend audit loop for all modified files: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines --test`
- [ ] **[NOK]** Manual verification: Re-seed DB, execute Matrix workflow, verify non-empty results with correct `tda_id` correlations

### Phase 5: Documentation & Knowledge Item Update
- [ ] **[NOK]** Create KI: `ki_context_enriched_decompose_verify.md` in `<appDataDir>/knowledge/context_enriched_pipeline/artifacts/`
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to update physical implementation maps

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK]** Backend full-stack validation: All audit loops pass >90% coverage for modified files
- [ ] **[NOK]** MANDATORY Final E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Post-Implementation Gates
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Verify no orphaned `FlattenedAtom` imports remain in `atom_flattening.py` after migration to DTO layer. `grep_search` for old import paths.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying:
  - @[c:\src\quorum\backend_v2\models\dtos\engine.py]
  - @[c:\src\quorum\backend_v2\hooks\atom_flattening.py]
  - @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]
  - @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: N/A — No frontend changes.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain after `FlattenedAtom` move.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for all modified files.
- [ ] **[NOK] MANDATORY Final E2E REST API Verification Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create a Knowledge Item (KI) for the Context-Enriched Decompose-Verify SSOT in `<appDataDir>/knowledge/context_enriched_pipeline/artifacts/`.
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Instructions for the Execution Agent

1. **Atomic Commit Mandate**: After EVERY successful audit loop pass, execute an atomic `git commit` with exact file paths before proceeding to the next step.
2. **Seeding Command**: If database re-seeding is needed: `uv run python backend_v2/seed/run_seed.py local`
3. **@-reference Syntax**: All target files are provided as `@[absolute_path]` references. You MUST use `view_file` to read them before modification.
4. **PERMISSION GRANTED**: This Epic explicitly grants "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem" per `orchestrator_god_object_fragility`.
5. **Test-First**: Write failing tests BEFORE modifying domain code per `tdd_mandate`.
6. **You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.**

---

## Requirements Traceability Matrix

| # | Epic Requirement | Phase/Plan | Status |
|:--|:-----------------|:-----------|:-------|
| R1 | `FlattenedAtom` defined ONLY in DTO layer (`engine.py`) | Phase 1 / `01_backend_dto_hardening_plan.md` Step 1.1 | [ ] |
| R2 | `EngineExecutionRequest` includes `shuffled_atoms: list[FlattenedAtom] \| None` | Phase 1 / `01_backend_dto_hardening_plan.md` Step 1.2 | [ ] |
| R3 | `atom_flattening.py` imports `FlattenedAtom` from DTO layer | Phase 1 / `01_backend_dto_hardening_plan.md` Step 1.3 | [ ] |
| R4 | `llm.py` uses Fail-Fast `state_data["shuffled_atoms"]` key access | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.1 | [ ] |
| R5 | `llm.py` hydrates atoms via `TypeAdapter(list[FlattenedAtom]).validate_python()` | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.1 | [ ] |
| R6 | `llm.py` passes `shuffled_atoms` into BOTH `EngineExecutionRequest` constructors | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.1 | [ ] |
| R7 | `tda_engine.py` — Matrix path: Phase 0+1 → enriched context → predefined atoms → `EnrichedDagExecutor` | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R8 | `tda_engine.py` — Matrix path: `full_context` includes enriched facts AND original `hydrated_text` with `[B0]`/`[B1]` tags | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R9 | `tda_engine.py` — Matrix path: `SlidingWindowLinker` is SKIPPED | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R10 | `tda_engine.py` — Regular path: Preserves existing `SlidingWindowLinker` behavior | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R11 | `matrix_scoring_hook` receives original predefined `tda_id` values — zero UUID mismatches | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R12 | `_MATRIX_SOURCE_SENTINEL` module-level constant per `zero_db_hardcoding_mandate` | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Step 2.2 | [ ] |
| R13 | 4 TDD test cases (2 success + 2 failure) | Phase 2 / `02_orchestration_tda_pipeline_plan.md` Testing section | [ ] |
| R14 | Backend audit >90% coverage | Phase 4 | [ ] |
| R15 | KI `ki_context_enriched_decompose_verify.md` created | Phase 5 | [ ] |
| R16 | E2E REST API Verification Gate passes | Phase 4 | [ ] |

---

# Session Handover Context

## Achieved
- Tier 1 planning completed for EPIC 118.
- Created task directory `docs/epic/tasks_EPIC_118/`.
- Generated 2 detailed implementation plans:
  - `01_backend_dto_hardening_plan.md` (Phase 1: FlattenedAtom DTO migration + shuffled_atoms field)
  - `02_orchestration_tda_pipeline_plan.md` (Phase 2: LLM strategy wiring + TDA Engine dual-path)
- Created standardized tracker with full Requirements Traceability Matrix.

## Learned
- `FlattenedAtom` currently lives in `hooks/atom_flattening.py` (L21-38), needs migration to `models/dtos/engine.py`.
- `EngineExecutionRequest` (engine.py L21-56) does NOT have `shuffled_atoms` field yet — `extra="forbid"` is set.
- `llm.py` (L403-408) uses defensive `in` check for `shuffled_atoms` — must be replaced with Fail-Fast key access.
- `tda_engine.py` (149 lines) has NO matrix path branching — all paths go through `SlidingWindowLinker`.
- `ExtractedAtom.tda_id` has regex pattern `^tda_[a-fA-F0-9]{8,32}$` — predefined matrix atoms already have `tda_`-prefixed IDs from seed data.
- Existing test file: `tests/unit/services/orchestrator/engines/test_tda_engine.py` (197 lines) — needs new matrix path tests.
- Existing test file: `tests/unit/hooks/test_atom_flattening.py` — needs import path update.

## Remaining
- Execute Phase 1 (`01_backend_dto_hardening_plan.md`)
- Execute Phase 2 (`02_orchestration_tda_pipeline_plan.md`)
- Phase 4 verification and E2E gate
- Phase 5 KI creation and `/tier7-describe-architecture`
- Post-implementation hardening gates

## Resume Command
`/tier5-resume --workflow=/tier2-execute --target="@[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline_tracker.md] @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_backend_dto_hardening_plan.md]" --rules="@[c:\src\quorum\.agents\rules\00-antigravity-core.md] @[c:\src\quorum\.agents\rules\01-python-backend.md] @[c:\src\quorum\.agents\rules\05_llm_architecture.md]"`
