# EPIC 106 Tracker: OutputProfile Simplification & SDUI Unification

> **Epic**: [EPIC_106_output_profile_simplification.md](file:///c:/src/quorum/docs/epic/EPIC_106_output_profile_simplification.md)
> **Task Directory**: [tasks_epic_106/](file:///c:/src/quorum/docs/epic/tasks_epic_106/)

---

## Phase Execution Status

### Phase 1: Workflow Prerequisite & OutputProfile Data Model Pruning (Backend)
- [x] **[OK] Red-Team**: Run `/tier0-research-plan` on [phase_1_backend_model_pruning.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_1_backend_model_pruning.md) in a fresh context window to Red-Team the architecture before execution.
- [x] **[OK] Execute**: Run `/tier2-execute` on [phase_1_backend_model_pruning.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_1_backend_model_pruning.md)

---

### Phase 2: SchemaFactory Registry Pattern & PromptCompiler SDUI Enforcement (Backend)
- [x] **[OK] Red-Team**: Run `/tier0-research-plan` on [phase_2_schema_factory_registry.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_2_schema_factory_registry.md) in a fresh context window — HIGH-RISK: introduces new SSOT component (`SchemaBuilderRegistry`), modifies protected `prompt_compiler.py`.
- [x] **[OK] Execute**: Run `/tier2-execute` on [phase_2_schema_factory_registry.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_2_schema_factory_registry.md)

---

### Phase 2 → Phase 2.5/3 Lazy Planning Gate
- [x] **[OK] Re-Plan**: Invoke the Tier 1 Planner again (`/tier1-planner`) to generate detailed plans for Phase 2.5 and Phase 3 based on the updated codebase state after Phase 2 is complete.

---

### Phase 2.5: Worker Rendering Pipeline Migration (Backend)
- [x] **[OK] Red-Team**: Run `/tier0-research-plan` on [phase_2_5_worker_migration.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_2_5_worker_migration.md)
- [ ] **[NOK] Execute**: Run `/tier2-execute` on [phase_2_5_worker_migration.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_2_5_worker_migration.md)

---

### Integration Checkpoint: Backend Full-Stack Validation
- [ ] **[NOK] Integration Test**: Run full backend audit `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and verify existing UI features work through the API layer.

---

### Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization (Frontend)
- [x] **[OK] Red-Team**: Run `/tier0-research-plan` on [phase_3_flutter_cleanup.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_3_flutter_cleanup.md)
- [ ] **[NOK] Execute**: Run `/tier2-execute` on [phase_3_flutter_cleanup.md](file:///c:/src/quorum/docs/epic/tasks_epic_106/phase_3_flutter_cleanup.md)

---

### Integration Checkpoint: Full-Stack UI Validation
- [ ] **[NOK] UI Validation**: Deploy locally and verify existing report generation flows (report creation, PDF export, Studio Admin UI) work end-to-end through the User Interface. Both backend and Flutter must pass their respective quality gates.

---

### Post-Implementation Gates

- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide `grep_search` for any remaining references to `OutputProfile.synthesis`, `OutputProfile.formatting_directives`, or `OutputProfile.matrix_column_labels`. Replace old import paths. Delete any deprecated proxy methods.

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` targeted at:
  - `backend_v2/core/registry.py` (new SSOT component)
  - `backend_v2/services/orchestrator/schema_factory.py` (refactored)
  - `backend_v2/models/v2_core.py` (pruned models)
  After the structural extraction (Zero Behavioral Change), modernize the new code's architecture to strict Pydantic V2 and Push models via Tier 2 Hardening.

- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` targeted at:
  - `client_app_v2/lib/features/studio/models/output_profile.dart` (pruned Freezed models)
  - `client_app_v2/lib/features/studio/views/` (cleaned UI)

- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain. Confirm no file still imports or references the deleted fields. Run comprehensive `grep_search` across the entire codebase for `formatting_directives`, `matrix_column_labels`, and profile-level `synthesis` patterns.

- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify that line coverage of the surviving business logic remains >90%. Verify all old fallback tests have been cleanly replaced by strict Pydantic V2 boundary tests. Do NOT match raw test counts (which will drop as legacy tests are deleted per the Anti-TDD trap).

- [ ] **[NOK] Documentation Update**: Update `docs/architecture/` and `.agents/rules/04_directory_reference.md` with the new SchemaBuilder Registry, pruned OutputProfile schema, and Workflow-level configuration fields. Create a Knowledge Item (KI) for the SDUI Schema Builder Registry Pattern.

---

## Instructions for the Execution Agent

1. Execute phases strictly in order. Each `[NOK]` task must be completed before the next begins.
2. After completing each session, you MUST update the `/tier5-resume` command at the bottom of this tracker file.
3. **Atomic Commit Mandate**: Phase 1 Milestones 1.2-1.5 MUST be committed atomically. Phase 2 Milestone 2.4 (llm.py) MUST be committed atomically with Phase 2.5 (worker.py).
4. Run `uv run python backend_v2/seed/run_seed.py local` after any seed data modifications.

---

## Requirements Traceability Matrix

| Epic Requirement | Phase/Plan |
|---|---|
| Remove `formatting_directives` from OutputProfile | Phase 1 (Milestone 1.2, 1.3), Phase 2 (Milestone 2.4), Phase 2.5, Phase 3 |
| Remove profile-level `synthesis` (SynthesisConfigDTO) from OutputProfile | Phase 1 (Milestone 1.2, 1.3), Phase 3 |
| Relocate `SynthesisConfigDTO.allowed_exports` → Workflow | Phase 1 (Milestone 1.1, 1.4) |
| Relocate `SynthesisConfigDTO.historical_context_mode` → Workflow | Phase 1 (Milestone 1.1, 1.4) |
| Relocate `SynthesisConfigDTO.allowed_mcp_tools` → StepRule | Already exists on StepRule (line 717 of v2_core.py). No action needed. |
| Relocate `SynthesisConfigDTO.length_constraint` → OutputLayoutBlock.synthesis | Already exists on OutputLayoutBlock.synthesis (retained). No action needed. |
| Relocate `SynthesisConfigDTO.matrix_visible_columns` → StepRule | Phase 2.5 (worker migration) |
| Remove `matrix_column_labels` from OutputProfile | Phase 1 (Milestone 1.2, 1.3), Phase 3 |
| SchemaFactory Registry Pattern (Open-Closed Principle) | Phase 2 (Milestone 2.1, 2.2) |
| `expected_sdui_type` threading: StepRule → SchemaFactory | Phase 2 (Milestone 2.2, 2.3) |
| PromptCompiler uses `expected_sdui_type` as formatting SSOT | Phase 2 (Milestone 2.3) |
| Remove `formatting_directives` from `llm.py` | Phase 2 (Milestone 2.4) |
| Worker rendering pipeline migration | Phase 2.5 |
| Flutter Freezed model synchronization | Phase 3 |
| Flutter Admin UI cleanup | Phase 3 |
| Seed data pruning | Phase 1 (Milestone 1.4) |
| Test mock migration (Anti-TDD trap) | Phase 1 (Milestone 1.5) |
| Retain `layouts`, `content_blocks`, `visible_block_extensions`, `visible_workflow_extensions`, `display_scale`, `max_extension_items` | Phase 1 (explicitly retained — Section A.1 validated) |
| Retain `OutputLayoutBlock.synthesis` and `ReportLayoutDTO.synthesis` | Untouched (Phase 1 only removes profile-level synthesis) |
| Deterministic Schema Binding via `expected_sdui_type` | Phase 2 (Milestones 2.1-2.3) |
| Database reset after seed changes | Phase 1 (Milestone 1.4) |

---

# Session Handover Context

## Achieved
- Tier 1 Planning session complete. Epic 106 broken down into 4 phases (Phase 1, 2, 2.5, 3) plus integration checkpoints and hardening gates.
- Detailed plans generated for Phase 1 and Phase 2.
- Placeholder plans generated for Phase 2.5 and Phase 3 (to be detailed after Phase 2 completion).
- Dynamic context acquisition performed: all target files read, current state of `OutputProfile`, `SynthesisConfigDTO`, `SchemaFactory`, `worker.py`, `llm.py`, and Flutter models verified.
- **Phase 1 Execution Complete**: Successfully pruned all `synthesis`, `formatting_directives`, and `matrix_column_labels` attributes from `OutputProfile` DTOs and database models.
- **Workflow Configurations Migrated**: Migrated the global fallback `allowed_exports` and `historical_context_mode` directly to the `Workflow` domain boundary and updated all consumers (`dag_executor`, `workflow_service`, `blueprint`, `worker`).
- **Test Suite Rescued**: Stripped obsolete proxy fields across 1,100+ tests and updated mock injections.
- **Global Audit Passed**: Executed the `backend_audit_loop.py` verifying Python strictness, MyPy types, Ruff formatting, and test suite passage (1120 passed).
- **Phase 2 Complete**: Successfully refactored `SchemaFactory` into a registry pattern, threaded `expected_sdui_type`, passed all tests, and created the `sdui_schema_registry` Knowledge Item.

## Learned
- `SynthesisConfigDTO` is still needed for `OutputLayoutBlock.synthesis` and `ReportLayoutDTO.synthesis` — only the profile-level `synthesis` field is removed.
- `allowed_mcp_tools` already exists on `StepRule` (v2_core.py line 717). No migration needed.
- `length_constraint` already exists on `OutputLayoutBlock.synthesis`. No migration needed.
- `OutputProfileConfig` in `lightweight_matrix.py` only has extension fields — no changes needed.
- `expected_sdui_type` already exists on `StepRule` (v2_core.py line 784, added by Epic 105). Seed data already has `"expected_sdui_type": "markdown"` values.
- The `Workflow` model does NOT yet have `allowed_exports` or `historical_context_mode` — Phase 0/1 adds them.
- Flutter `output_profile.dart` has `SynthesisConfigDTO` imported from `synthesis_config_dto.dart` in `execution/models/`. This is also used by `OutputLayoutBlock.synthesis` in the same file, so it CANNOT be deleted — only the profile-level field is removed.

## Remaining
- Phase 1 (Backend model pruning) — Executed and verified.
- Phase 2 (SchemaFactory + PromptCompiler) — Executed and verified.
- **Phase 2.5 (Worker migration)** — RED-TEAMED & PLAN READY (`/tier2-execute`)
- **Phase 3 (Flutter cleanup)** — RED-TEAMED & PLAN READY (`/tier2-execute`)
- All post-implementation gates (hardening, proxy sunset, coverage audit, documentation).

---

```bash
/tier5-resume --workflow=/tier2-execute --target="docs/epic/tasks_epic_106/phase_2_5_worker_migration.md, docs/epic/EPIC_106_output_profile_simplification_tracker.md"
```
