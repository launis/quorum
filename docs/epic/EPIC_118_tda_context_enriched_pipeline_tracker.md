# EPIC 118: TDA Context-Enriched Decompose-Verify Pipeline — Execution Tracker

> **Epic**: @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]
> **Task Directory**: @[c:\src\quorum\docs\epic\tasks_EPIC_118/]
> **Created**: 2026-07-25

---

## Instructions for the Execution Agent
- Atomic commit mandates must be respected.
- If seeding is required, use: `uv run python backend_v2/seed/run_seed.py local`
- You MUST use `@-reference` syntax for all target file paths.
- **You MUST update the `/tier5-resume` command at the bottom of this tracker before handing over the session.**

---

## Phase Execution Status

### Phase 1: DTO Model & Hook Migration
> Plan: @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_dto_model_and_hook_migration_plan.md]
> Target Files: @[c:\src\quorum\backend_v2\models\dtos\engine.py], @[c:\src\quorum\backend_v2\hooks\atom_flattening.py]

- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_dto_model_and_hook_migration_plan.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_dto_model_and_hook_migration_plan.md]`

---

### Phase 2: Context-Enriched Pipeline & Strategy Wiring
> Plan: @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_context_enriched_pipeline_and_strategy_wiring_plan.md]
> Target Files: @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py], @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]

- [ ] **[NOK] Red-Teaming**: `/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_context_enriched_pipeline_and_strategy_wiring_plan.md]`
- [ ] **[NOK] Execution**: `/tier2-execute @[c:\src\quorum\docs\epic\tasks_EPIC_118\02_context_enriched_pipeline_and_strategy_wiring_plan.md]`

---

### Integration Checkpoint: Full-Stack Validation

- [ ] **[NOK] Backend Integration Test**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to verify zero cross-module regressions.
- [ ] **[NOK] Manual Verification**: Re-seed (`uv run python backend_v2/seed/run_seed.py local`), execute a Matrix workflow, verify `matrix_scoring_hook` produces non-empty results with correct `tda_id` correlations.
- [ ] **[NOK] Inspect `llm_debug_prompts.md`**: Verify `full_context` contains both enriched facts and original `[B0]`/`[B1]` block tags.

---

### Post-Implementation Gates

- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Verify `FlattenedAtom` is no longer defined in `atom_flattening.py`. Run `grep_search` for any remaining direct imports from the old location.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` targeting:
  - @[c:\src\quorum\backend_v2\models\dtos\engine.py]
  - @[c:\src\quorum\backend_v2\hooks\atom_flattening.py]
  - @[c:\src\quorum\backend_v2\services\orchestrator\engines\tda_engine.py]
  - @[c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py]
  - @[c:\src\quorum\backend_v2\tests\unit\services\orchestrator\engines\test_tda_engine.py]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned imports or references to the old `FlattenedAtom` location remain in the codebase.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Backend audit loop confirms >90% coverage for all modified files.
- [ ] **[NOK] MANDATORY E2E Gate**: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Documentation & Knowledge Item Update
- [ ] **[NOK]** Create KI `ki_context_enriched_decompose_verify.md` (EPIC 115 compliance).
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to automatically scan the codebase, anchor the physical implementation map in `docs/architecture/`, and update `.agents/rules/04_directory_reference.md`.

### Final Epic Audit
- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[c:\src\quorum\docs\epic\EPIC_118_tda_context_enriched_pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

---

## Requirements Traceability Matrix

| # | Epic Requirement | Plan Phase | Status |
|:--|:-----------------|:-----------|:-------|
| R1 | `FlattenedAtom` defined ONLY in `engine.py` | Phase 1 | `[NOK]` |
| R2 | `FlattenedAtom` imported by `atom_flattening.py` from DTO layer | Phase 1 | `[NOK]` |
| R3 | `EngineExecutionRequest` includes `shuffled_atoms: list[FlattenedAtom] \| None` | Phase 1 | `[NOK]` |
| R4 | `llm.py` uses `state_data["shuffled_atoms"]` (Fail-Fast key access) when `is_matrix_step` | Phase 2 | `[NOK]` |
| R5 | `tda_engine.py` implements Context-Enriched pipeline: Phase 0+1 → enriched context → predefined matrix atoms → `EnrichedDagExecutor` | Phase 2 | `[NOK]` |
| R6 | `full_context` includes enriched facts AND original `hydrated_text` with `[B0]`, `[B1]` AliasEngine block tags | Phase 2 | `[NOK]` |
| R7 | `matrix_scoring_hook` receives results with original predefined `tda_id` values — zero UUID mismatches | Phase 2 (Integration) | `[NOK]` |
| R8 | 4 TDD test cases pass (2 success, 2 failure) per EPIC 114 | Phase 2 | `[NOK]` |
| R9 | Backend audit loop >90% coverage | Post-Gates | `[NOK]` |
| R10 | KI `ki_context_enriched_decompose_verify.md` created (EPIC 115 compliance) | Post-Gates | `[NOK]` |

---

# Session Handover Context

## Achieved
- Tier 1 planning complete. Two micro-chunked implementation plans generated for EPIC 118.
- No code changes made (Tier 1 is planning-only).
- Updated tracker to use the strict Phase Execution Status format.

## Learned
- **Architecture Snapshot**: `FlattenedAtom` currently lives in `atom_flattening.py` (to be moved to `engine.py`).
- `EngineExecutionRequest` currently lacks `shuffled_atoms` field.
- `TDAEngine.execute()` has a single code path (always runs linker + dag executor on extracted atoms).
- `llm.py` uses defensive `"shuffled_atoms" in state_data` checks instead of Fail-Fast.

## Remaining
- Execute `/tier0-research-plan` and `/tier2-execute` on the Phase 1 plan.
- Execute `/tier0-research-plan` and `/tier2-execute` on the Phase 2 plan.
- Run integration checkpoint.
- Complete post-implementation gates.

## Resume Command
`/tier0-research-plan @[c:\src\quorum\docs\epic\tasks_EPIC_118\01_dto_model_and_hook_migration_plan.md]`
