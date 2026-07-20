# EPIC 105: Synthesis Engine Unification — Master Tracker

> **Epic Document**: [EPIC_105_synthesis_engine_unification.md](file:///c:/src/quorum/docs/epic/EPIC_105_synthesis_engine_unification.md)
> **Task Directory**: [tasks_epic_105_synthesis_engine_unification/](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification)
> **Created**: 2026-07-20

---

## Execution Phases

### Phase 0: `expected_sdui_type` Field Addition & Enum Rename (Backend)
- [ ] **[NOK] Red-Team**: Run `/tier0-research-plan` on [phase_0_sdui_type_and_enum_rename.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_0_sdui_type_and_enum_rename.md) in a fresh context window to validate architectural decisions before execution.
- [ ] **[NOK] Execute Phase 0**: Run `/tier2-execute` on [phase_0_sdui_type_and_enum_rename.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_0_sdui_type_and_enum_rename.md)
  - [ ] Milestone 0.1: Rename `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS` → `.SYNTHESIS` in `enums.py`
  - [ ] Milestone 0.2: Add `expected_sdui_type` field to `StepRule` in `v2_core.py`
  - [ ] Milestone 0.3: Update `seed_data.json` (13 engine_override renames + expected_sdui_type additions)
  - [ ] Milestone 0.4: Update all consumer references in `dag_executor.py` (lines 242, 667, 821)
  - [ ] Milestone 0.5: Update test fixtures in `test_dag_executor_preflight.py` and `test_dag_executor_atom_ceiling.py`
  - [ ] Run `uv run python backend_v2/seed/run_seed.py local` to validate seed data
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` — full backend audit pass

---

### Phase 1: SynthesisEngine Extraction (Backend — New SSOT Component)
- [ ] **[NOK] Red-Team**: Run `/tier0-research-plan` on [phase_1_synthesis_engine_extraction.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_1_synthesis_engine_extraction.md) in a fresh context window. This phase introduces a NEW SSOT component (`SynthesisEngine`) and modifies core `EngineExecutionResult` DTO — high-risk.
- [ ] **[NOK] Execute Phase 1**: Run `/tier2-execute` on [phase_1_synthesis_engine_extraction.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_1_synthesis_engine_extraction.md)
  - [ ] Milestone 1.1: Extend `EngineExecutionResult` with `synthesis_output` and `trace_events` fields
  - [ ] Milestone 1.2: Create `synthesis_engine.py` implementing `ExecutionEngine` Protocol
  - [ ] Milestone 1.3: Register in `engines/__init__.py`
  - [ ] Create unit tests in `tests/unit/services/orchestrator/engines/test_synthesis_engine.py`
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` — full backend audit pass

---

### Phase 2: DAG Executor Wiring & Synthesis Compilation Branch (Backend — God Object Mutation)
- [ ] **[NOK] Red-Team**: Run `/tier0-research-plan` on [phase_2_dag_wiring_and_synthesis_branch.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_2_dag_wiring_and_synthesis_branch.md) in a fresh context window. This phase mutates `dag_executor.py` (God Object ecosystem) — high-risk.
- [ ] **[NOK] Execute Phase 2**: Run `/tier2-execute` on [phase_2_dag_wiring_and_synthesis_branch.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_2_dag_wiring_and_synthesis_branch.md)
  - [ ] Milestone 2.1: Replace if/elif/else routing with Factory-Based Strategy Registry in `dag_executor.py`
  - [ ] Milestone 2.2: Add synthesis-specific pre-compilation branch to `LLMNodeStrategy.execute()` in `llm.py`
  - [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` — full backend audit pass

---

### Phase 2.5: Re-Plan Remaining Phases
- [ ] **[NOK] Invoke Tier 1 Planner**: Invoke the Tier 1 Planner again (`/tier1-planner`) to generate detailed plans for the remaining phases (3, 4) based on the updated codebase state after Phases 0-2.

---

### Phase 3: Integration Checkpoint — End-to-End UI Validation
- [ ] **[NOK] Execute Phase 3**: [phase_3_integration_checkpoint.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_3_integration_checkpoint.md) — PLACEHOLDER. Full plan generated after Phase 2.5.

---

### Phase 4: Legacy Deletion & Test Migration
- [ ] **[NOK] Execute Phase 4**: [phase_4_legacy_deletion_and_tests.md](file:///c:/src/quorum/docs/epic/tasks_epic_105_synthesis_engine_unification/phase_4_legacy_deletion_and_tests.md) — PLACEHOLDER. Full plan generated after Phase 2.5.

---

### Post-Extraction Pipeline

- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search for any remaining imports of `PreHydratedSynthesisStrategy` or `PRE_HYDRATED_SYNTHESIS`. Replace all old import paths with the new `SynthesisEngine` + `EngineOverrideStrategy.SYNTHESIS` references. Remove any proxy re-exports.

- [ ] **[NOK] Tier 2 Hardening**: Run `/tier2-hardening-backend` targeted at:
  - `backend_v2/services/orchestrator/engines/` — Modernize to Pydantic V2 strict models and push architecture.
  - `backend_v2/services/orchestrator/strategies/llm.py` — Verify synthesis branch complies with all Phase 9 standards.

- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain pointing to deleted files. Completely DELETE:
  - `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
  - Remove any `PreHydratedSynthesisStrategy` from `strategies/__init__.py` (already not exported, but verify no residual references).

- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify:
  1. Line coverage of surviving business logic remains >90%.
  2. All old fallback tests have been cleanly replaced by strict Pydantic V2 boundary tests.
  3. The `SynthesisEngine` test file covers: blackboard validation, happy path, immutable messages, exception wrapping.

- [ ] **[NOK] Documentation & Knowledge Item Update**:
  - Update `docs/architecture/` with Synthesis Engine Unification changes.
  - Update `.agents/rules/04_directory_reference.md` to add `engines/synthesis_engine.py` to the orchestrator module.
  - Create Knowledge Item (KI): `synthesis_engine_ssot` in `<appDataDir>/knowledge/` documenting the new SSOT `SynthesisEngine` usage rules.

---

## Instructions for the Execution Agent

> **CRITICAL**: Before handing over the session, you MUST update the `/tier5-resume` command at the bottom of this tracker file with current Achieved/Learned/Remaining status.

---

## Requirements Traceability Matrix

| Epic Requirement | Source | Phase |
|---|---|---|
| Add `expected_sdui_type` to `StepRule` | Phase 0, Step 1 | Phase 0 |
| Rename `PRE_HYDRATED_SYNTHESIS` → `SYNTHESIS` | Phase 0, Step 2 | Phase 0 |
| Update `seed_data.json` engine_overrides | Phase 0, Step 3 | Phase 0 |
| Create `SynthesisEngine` implementing `ExecutionEngine` | Phase 1, Step 1 | Phase 1 |
| Preserve `GlobalAtomBlackboard` Fail-Fast validation | Phase 1, Step 2 (Epic 101 Rule 1) | Phase 1 |
| Engine statelessness (no `self` state) | Phase 1, Step 2 | Phase 1 |
| Idempotent message handling (local copy + XML isolation) | Phase 1, Step 3 (Anti-Format-Crash) | Phase 1 |
| Real-time observability (debug log before LLM call) | Phase 1, Step 4 | Phase 1 |
| Anti-Corruption Layer (AppException wrapping) | Phase 1, Step 7 (RFC 7807) | Phase 1 |
| Telemetry mapping to `EngineExecutionResult.trace_events` | Phase 1, Step 5 | Phase 1 |
| Factory-Based Strategy Registry (replace if/elif) | Phase 2, Step 1 | Phase 2 |
| Synthesis pre-compilation branch in `LLMNodeStrategy` | Phase 2, Step 2 | Phase 2 |
| Schema compilation via `StepRule.expected_sdui_type` | Phase 2, Step 2 | Phase 2 |
| Delete `PreHydratedSynthesisStrategy` | Phase 3 | Phase 4 |
| Remove `strategies/__init__.py` references | Phase 3 | Phase 4 |
| New unit tests for `SynthesisEngine` | Phase 5 | Phase 1 + Phase 4 |
| Delete legacy test files | Phase 5 | Phase 4 |
| Phase 4 (Observability Logger) — DEFERRED to Epic 107 | Phase 4 | N/A (DEFERRED) |
| `LLMClient.from_strategy()` uses `context.model_strategy` (not hardcoded) | Phase 2, Registry | Phase 2 |

---

# Session Handover Context

## Achieved
- Generated detailed implementation plans for Phase 0, Phase 1, and Phase 2.
- Generated placeholder plans for Phase 3 (integration) and Phase 4 (deletion + tests).
- Created master tracker with full requirements traceability matrix.
- Performed dynamic context acquisition on all target files and verified codebase state.

## Learned
- `PreHydratedSynthesisStrategy` is only imported in `dag_executor.py` (lazy import) and its own file. No test file exists for it.
- `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS` has 13 occurrences in `seed_data.json` and is referenced in `dag_executor.py` at lines 242, 667, 821.
- `expected_sdui_type` does NOT exist anywhere in the codebase yet — clean slate for Phase 0.
- `EngineExecutionResult` currently has TDA-specific fields only (`AtomResultDTO`, `HydratedAtomDTO`). Synthesis returns different shapes — DTO must be extended.
- The `model_strategy` values in seed data include: `"fast"`, `"reasoning"`, `"synthesis"`.
- `strategies/__init__.py` does NOT export `PreHydratedSynthesisStrategy` (it uses a lazy inline import in `dag_executor.py`).

## Remaining
- Execute Phase 0 → Phase 1 → Phase 2 (detailed plans ready).
- After Phase 2, invoke Tier 1 Planner again for remaining phases.
- Phases 3-4 + Post-Extraction Pipeline + Documentation.

---

```
/tier5-resume --workflow=/tier2-execute --target="docs\epic\EPIC_105_synthesis_engine_unification_tracker.md, docs\epic\EPIC_105_synthesis_engine_unification.md" --rules="00-antigravity-core.md, 01-python-backend.md, 03_seed_vault.md"
```
