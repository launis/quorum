<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
</required_context_rules>

# EPIC 163: Complete Eradication of Residual Guardrail Exemption Ledgers, Open-JSON DTO Consumers & Worker Repository Mocks — Execution Tracker

**Epic Specification:** @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md]
**Audit Report:** @[docs/epic/EPIC_163_audit_report.md]
**Generated Plans Directory:** `docs/epic/tasks_EPIC_163/`

---

## Phase Execution Status

### Phase 1: Pre-Implementation Guardrail Hygiene (`QGR001`, `QGR002`), Audit Script `C901` Decomposition & `QGR030` Local Shadow-State Eradication
**Plan:** @[docs/epic/tasks_EPIC_163/01_phase1_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/01_phase1_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]` (`30aba5589`)
  - [x] Step 1.1: PEP 257 Docstring Remediation (`QGR001`) & Unlogged `AppException` Dual-Reporting (`QGR002`)
  - [x] Step 1.2: Audit Script `C901` McCabe Complexity Decomposition & Per-File-Ignore Removal
  - [x] Step 1.3: Eradicate Process-Local Shadow State Fallbacks (`QGR030`) in Organization, Assignment & Cache Services
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 2: Pydantic V2 Schema Strictness — Zero Silent Defaults (`QGR020` Check 20C) & 100% PEP 593 `Annotated` (`QGR020` Check 20B)
**Plan:** @[docs/epic/tasks_EPIC_163/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/02_phase2_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [x] Step 2.1: Eradicate Silent Identity, Relational & Display Field Defaults (`QGR020` Check 20C)
  - [x] Step 2.2: Convert Bare `Field(...)` Declarations in Core, Exceptions, Chunking & Domain Models (`QGR020` Check 20B — Batch 1)
  - [x] Step 2.3: Convert Bare `Field(...)` Declarations in DTOs, View, Packer & Scripts and Delete `QGR020` Exemption Sets (`QGR020` Check 20B — Batch 2)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 3: Immutable `ExecutionRecord` State Transitions & Zero Redundant Re-Validation (`QGR028`)
**Plan:** @[docs/epic/tasks_EPIC_163/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/03_phase3_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [x] Step 3.1: Immutable `ExecutionRecord` Transition Helpers & Worker State Updates
  - [x] Step 3.2: Eradicate Redundant `.model_validate()` Calls in Hooks & Services and Delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES`
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 4: Strongly Typed DAG Context, Matrix Evaluation & Synthesis DTOs (`QGR027` `JsonValue` Eradication)
**Plan:** @[docs/epic/tasks_EPIC_163/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/04_phase4_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]` (`3d4c0ed3b`)
  - [x] Step 4.1: Replace `JsonValue` Containers in Backend DTOs & State Envelopes
  - [x] Step 4.2: Migrate LLM Client, Ingress Pipeline, Task Executor & Matrix Hook Away from `JsonValue`
  - [x] Step 4.3: Migrate Orchestrator Stages, Compressor, Projector & Reducer and Delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 5: Frontend Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication
**Plan:** @[docs/epic/tasks_EPIC_163/05_phase5_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/05_phase5_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]` (`18cdee79a`)
  - [x] Step 5.1: Migrate Group 2 Execution & Studio Freezed DTO Models
  - [x] Step 5.2: Migrate Group 3 Execution & Studio Controllers, Utilities & Views
  - [x] Step 5.3: Migrate Group 3 Shared Widgets & Shrink `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` to 9 Transport Files
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 6: Stateful `InMemoryUnitOfWork` Migration for Worker Test Suites (`Census F = 0`) & Final E2E Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_163/06_phase6_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/06_phase6_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]` (`115e332ab`)
  - [x] Step 6.1: Migrate `test_worker.py`, `test_worker_synthesis.py` & `test_worker_synthesis_accumulation.py` to Stateful `InMemoryUnifiedWorkflowRepository`
  - [x] Step 6.2: Migrate `test_report_worker.py`, `test_synthesis_reducers.py` & `test_synthesis_worker.py` and Lock `Census F = 0`
  - [x] Step 6.3: Full-Stack Global Quality Gates & Live E2E Verification
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 7: Non-Residual Static Guardrail Modernization (`DGR013`, `DGR014`, `QGR013`, `QGR033` Check 33B) & Tier 2 Hardening Rules Synchronization
**Plan:** @[docs/epic/tasks_EPIC_163/07_phase7_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/07_phase7_plan.md`
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] @[docs/epic/EPIC_163_tracker.md]` (`fbe6e1b33`)
  - [x] Step 7.1: Pre-Implementation Docstring (`ValidationHookPayloadDTO.model_validate`) & Dart Test Fixture (`test_dgr010_guarded_async_value_allowed`) Cleanups
  - [x] Step 7.2: Dart 3.11+ Freezed Switch (`DGR013`) & Riverpod 3.1 (`DGR014`) Guardrails
  - [x] Step 7.3: Python 3.14 PEP 695 `TypeAlias` (`QGR013`) & Public Function / Module Docstring Ordering (`QGR033` Check 33B) Guardrails
  - [x] Step 7.4: Tier 2 Hardening Skills, Phase 1 Learnings & `auto_hardening_runner.py` `.agents/rules/` Enforcement
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Integration Checkpoint**: Run full-stack quality gates (`uv run python scripts/backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`) to verify cross-boundary contract parity before hardening.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide verification of zero `RESIDUAL_*` exemption sets in `@[scripts/_ast_guardrails.py]`, zero `per-file-ignores` in `@[pyproject.toml]`, 9 transport boundary files in `@[scripts/_dart_guardrails.py]`, and `CURRENT_RESIDUAL_CEILINGS["f"] = 0` in `@[scripts/audit_warning_baseline.py]`.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_163_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"` to audit all modified backend files:
  - [x] @[backend_v2/core/hook_registry.py]
  - [x] @[backend_v2/core/registry.py]
  - [x] @[backend_v2/exceptions.py]
  - [x] @[backend_v2/hooks/atom_flattening.py]
  - [x] @[backend_v2/hooks/scoring/falsifier_hook.py]
  - [x] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [x] @[backend_v2/hooks/scoring/normalization_hook.py]
  - [x] @[backend_v2/llm/client.py]
  - [x] @[backend_v2/llm/ingress_pipeline.py]
  - [x] @[backend_v2/llm/mock_data.py]
  - [x] @[backend_v2/logging_config.py]
  - [x] @[backend_v2/models/auth.py]
  - [x] @[backend_v2/models/chunking.py]
  - [x] @[backend_v2/models/domain/execution.py]
  - [x] @[backend_v2/models/domain/inputs.py]
  - [x] @[backend_v2/models/domain/matrix.py]
  - [x] @[backend_v2/models/domain/metadata.py]
  - [x] @[backend_v2/models/domain/output_profile.py]
  - [x] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/domain/step.py]
  - [ ] @[backend_v2/models/domain/system_config.py]
  - [ ] @[backend_v2/models/domain/validation.py]
  - [ ] @[backend_v2/models/domain/workflow.py]
  - [ ] @[backend_v2/models/dtos/atom_evaluation.py]
  - [ ] @[backend_v2/models/dtos/context_variables.py]
  - [ ] @[backend_v2/models/dtos/engine.py]
  - [ ] @[backend_v2/models/dtos/hook_delta.py]
  - [ ] @[backend_v2/models/dtos/hook_state.py]
  - [ ] @[backend_v2/models/dtos/lightweight_matrix.py]
  - [ ] @[backend_v2/models/dtos/mcp.py]
  - [ ] @[backend_v2/models/dtos/prompt_context.py]
  - [ ] @[backend_v2/models/dtos/quote_evidence.py]
  - [ ] @[backend_v2/models/dtos/schema_manifest.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/models/dtos/theory_manifest.py]
  - [ ] @[backend_v2/models/dtos/trace.py]
  - [ ] @[backend_v2/models/dtos/variance.py]
  - [ ] @[backend_v2/models/dtos/workflow_schema.py]
  - [ ] @[backend_v2/models/execution_core.py]
  - [ ] @[backend_v2/models/llm.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/models/view/sdui.py]
  - [ ] @[backend_v2/services/auth/organization_service.py]
  - [ ] @[backend_v2/services/auth/secret_service.py]
  - [ ] @[backend_v2/services/cache/typed_cache.py]
  - [ ] @[backend_v2/services/execution/assignment_service.py]
  - [ ] @[backend_v2/services/execution/ingress_service.py]
  - [ ] @[backend_v2/services/llm_task_executor.py]
  - [ ] @[backend_v2/services/orchestrator/context_router.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]
  - [ ] @[backend_v2/services/orchestrator/extraction_schema_factory.py]
  - [ ] @[backend_v2/services/orchestrator/matrix_reducer.py]
  - [ ] @[backend_v2/services/orchestrator/rag_preflight_service.py]
  - [ ] @[backend_v2/services/orchestrator/result_projector.py]
  - [ ] @[backend_v2/services/orchestrator/schema_factory.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/logic.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_distiller.py]
  - [ ] @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
  - [ ] @[backend_v2/utils/finops_trace_analyzer.py]
  - [ ] @[backend_v2/workers/execution_worker.py]
  - [ ] @[backend_v2/workers/synthesis_reducers.py]
  - [ ] @[backend_v2/workers/synthesis_worker.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/_dart_guardrails.py]
  - [ ] @[scripts/ablation_live_executor.py]
  - [ ] @[scripts/audit_dict_eradication.py]
  - [ ] @[scripts/audit_warning_baseline.py]
  - [ ] @[scripts/auto_hardening_runner.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[scripts/diff_executions.py]
  - [ ] @[scripts/flutter_audit_loop.py]
  - [ ] @[scripts/reconcile_storage.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_163_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"` to audit all modified frontend files:
  - [ ] @[client_app_v2/lib/features/execution/controllers/execution_controller.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/workflow_inputs.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/step_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]
  - [ ] @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/mcp_tool_params_panel.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/comparison_matrix.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/dynamic_form.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/generic_grid.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/schema_mapper.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/score_card_radar.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/specialist_section.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/workflow_selector.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies or deprecated parameters remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic across all modified modules.
- [ ] **[NOK] Test Coverage Expansion (`/tier8-test-coverage-expansion`)**: Run ISTQB negative and boundary value test expansion across modified DTOs, services, and worker suites.

### Documentation & Knowledge Item Update
- [ ] **[NOK] As-Built Architectural Sync**: Execute `/tier7-describe-architecture @[docs/epic/EPIC_163_tracker.md] @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_deterministic_hardening_state.md] @[ki_router_ssot_and_crud_clone_lifecycle.md]` to synchronize `docs/architecture/` and Knowledge Items with the zero-exemption guardrail state.

### Final Epic Audit
- [ ] **Reverse Verification Audit**: Execute `/tier8-audit-epic @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] @[docs/epic/EPIC_163_tracker.md]` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_epic_coverage.py --epic docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md --tracker docs/epic/EPIC_163_tracker.md`.

---

## Instructions for the Execution Agent

1. **Before Starting Any Phase:** Run `/tier0-research-plan` on the target phase plan (`01_phase1_plan.md` through `07_phase7_plan.md`) alongside `@[docs/epic/EPIC_163_tracker.md]` to perform System 2 validation before `/tier2-execute`.
2. **Double-Entry Bookkeeping:** Upon completing each step (`Step X.Y`), immediately mark `[x]` on both the step checkbox in `@[docs/epic/EPIC_163_tracker.md]` and the corresponding `<dod_checklist>` item in the phase plan before creating an atomic `git commit`.
3. **Zero Residual Exemptions:** Do not introduce any new `RESIDUAL_*` sets in `@[scripts/_ast_guardrails.py]` or `per-file-ignores` in `@[pyproject.toml]`.

---

## Requirements Traceability Matrix

| Requirement ID | Epic Requirement Summary | Target Phase & Step | Verification Gate | Status |
| :--- | :--- | :--- | :--- | :--- |
| `REQ-163-001` | Add PEP 257 docstrings to 4 files (`QGR001`), add `logger.error` before `AppException` in `logging_config.py` (`QGR002`), and delete `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` | Phase 1, Step 1.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-002` | Decompose C901 functions in `backend_audit_loop.py` and `flutter_audit_loop.py`, remove `[tool.ruff.lint.per-file-ignores]` from `pyproject.toml`, and empty `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` | Phase 1, Step 1.2 | `audit_dict_eradication.py` & `ruff check` | `[x]` |
| `REQ-163-003` | Eradicate `_local_invitations`, `_local_assignments`, and `_memory_entries` (`QGR030`) and delete `RESIDUAL_LOCAL_SHADOW_STATE_FILES` | Phase 1, Step 1.3 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-004` | Remove all 14 silent identity, relational, and display field defaults across 8 files (`QGR020` Check 20C) and delete `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` | Phase 2, Step 2.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-005` | Convert bare `Field(...)` declarations in core, exceptions, chunking, and domain models to PEP 593 `Annotated[T, Field(...)]` (`QGR020` Check 20B Batch 1) | Phase 2, Step 2.2 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-006` | Convert bare `Field(...)` declarations in DTOs, view, packer, and scripts to PEP 593 `Annotated[T, Field(...)]` and delete `RESIDUAL_BARE_FIELD_FILES` (`QGR020` Check 20B Batch 2) | Phase 2, Step 2.3 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-007` | Add immutable `ExecutionRecord` transition helpers (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) and refactor worker state transitions (`QGR028`) | Phase 3, Step 3.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-008` | Eliminate redundant `.model_validate()` calls on typed DTOs across 7 hook and service files and delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES` (`QGR028`) | Phase 3, Step 3.2 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-009` | Replace `dict[str, JsonValue]` and `list[JsonValue]` across 8 DTO and state files in `backend_v2/models/` with closed Pydantic V2 DTOs (`QGR027`) | Phase 4, Step 4.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-010` | Replace `dict[str, JsonValue]` in `LLMClient`, `LLMIngressPipeline`, `mock_data.py`, `LLMTaskExecutor`, and `matrix_hook.py` with generic `BaseModel` and typed DTOs (`QGR027`) | Phase 4, Step 4.2 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-011` | Replace `dict[str, JsonValue]` across 6 orchestrator files with typed DTOs and delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` (`QGR027`) | Phase 4, Step 4.3 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-012` | Replace `Map<String, Object?>` fields across all 13 Group 2 Execution and Studio Freezed DTO models (`DGR005`) | Phase 5, Step 5.1 | `flutter_audit_loop.py --build` | `[x]` |
| `REQ-163-013` | Refactor all 12 Group 3 Execution and Studio controllers, cloner utilities, and views to consume typed Freezed DTOs (`DGR005`) | Phase 5, Step 5.2 | `flutter_audit_loop.py --build` | `[x]` |
| `REQ-163-014` | Refactor all 11 Group 3 shared widgets to consume typed Freezed DTOs and shrink `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` to the 9 transport boundary files (`DGR005`) | Phase 5, Step 5.3 | `flutter_audit_loop.py --build` & `test_dart_guardrails.py` | `[x]` |
| `REQ-163-015` | Replace 35 `UnifiedWorkflowRepository` patches across `test_worker.py`, `test_worker_synthesis.py`, and `test_worker_synthesis_accumulation.py` with stateful `InMemoryUnifiedWorkflowRepository` fixtures | Phase 6, Step 6.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-016` | Replace 9 `UnifiedWorkflowRepository` patches across `tests/unit/workers/` with stateful `InMemoryUnifiedWorkflowRepository` fixtures and lock `CURRENT_RESIDUAL_CEILINGS["f"] = 0` | Phase 6, Step 6.2 | `audit_warning_baseline.py --verify-ceilings` | `[x]` |
| `REQ-163-017` | Execute global Backend, Frontend, Dict Eradication, Warning Baseline, DTO Parity, SDUI Semantic Parity, and Live E2E verification gates | Phase 6, Step 6.3 | Full-Stack & Live E2E Gates | `[x]` |
| `REQ-163-018` | Add PEP 257 docstring to `ValidationHookPayloadDTO.model_validate` (`validation.py`) and migrate `test_dgr010_guarded_async_value_allowed` (`test_dart_guardrails.py`) to Dart 3 `switch (state)` | Phase 7, Step 7.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-019` | Enforce `DGR013` (`freezed_when_ban`) and `DGR014` (`manual_riverpod_providers` & `riverpod_read_vs_watch_ban`) at `GuardrailSeverity.FATAL` in `scripts/_dart_guardrails.py` (`C901 <= 10`) | Phase 7, Step 7.2 | `backend_audit_loop.py --test --ast-strict` & `_dart_guardrails.py --strict` | `[x]` |
| `REQ-163-020` | Extend `QGR013` (`TypeAlias` ban) and `QGR033` Check 33B (public function/method docstrings and line-1 module docstring ordering before `from __future__ import annotations`) in `scripts/_ast_guardrails.py` (`C901 <= 10`) | Phase 7, Step 7.3 | `backend_audit_loop.py --test --ast-strict` & `_ast_guardrails.py --strict` | `[x]` |
| `REQ-163-021` | Synchronize Tier 2 hardening `SKILL.md` playbooks and `scripts/auto_hardening_runner.py` (`resolve_target_rule_files`, `execute_subagent_pass` `C901 <= 10`, and `compute_rules_sha256` hashing `AGENTS.md` + `SKILL.md`) | Phase 7, Step 7.4 | `audit_skills_architecture.py` & `backend_audit_loop.py --test --ast-strict` | `[x]` |

---

# Session Handover Context

## Achieved
- Decomposed @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] and @[docs/epic/EPIC_163_audit_report.md] into 7 phased implementation plans under `docs/epic/tasks_EPIC_163/`:
  - @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] (Phase 1: `QGR001`, `QGR002`, `C901`, `QGR030`)
  - @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] (Phase 2: `QGR020` Check 20C & Check 20B)
  - @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] (Phase 3: `QGR028` Immutable `ExecutionRecord` Transitions & Zero Redundant Re-Validation)
  - @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] (Phase 4: `QGR027` `JsonValue` Eradication)
  - @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] (Phase 5: Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication)
  - @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] (Phase 6: Worker Test Migration `Census F = 0` & Final E2E Verification Gate)
  - @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] (Phase 7: Non-Residual Static Guardrail Modernization `DGR013`, `DGR014`, `QGR013`, `QGR033` Check 33B & Tier 2 Hardening Rules Synchronization)
- Completed Tier 0 Red-Teaming (`/tier0-research-plan`) and Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 1 (@[docs/epic/tasks_EPIC_163/01_phase1_plan.md]):
  - **Step 1.1 (`0ca707436`):** Restored PEP 257 module, class, and function docstrings across @[backend_v2/models/dtos/variance.py#L17-L38], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168], @[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L325], and @[backend_v2/services/orchestrator/schema_factory.py#L39-L411]; added RFC 7807 `logger.error` calls with `ErrorCodes.CONFIGURATION_ERROR.name` before raising `AppException` in `setup_logging` (@[backend_v2/logging_config.py#L138-L282]); and deleted `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` from @[scripts/_ast_guardrails.py].
  - **Step 1.2 (`650c05504`):** Decomposed high-branching functions in @[scripts/backend_audit_loop.py] and @[scripts/flutter_audit_loop.py] so all functions achieve McCabe complexity $\le 10$ (well below $\le 15$), removed `[tool.ruff.lint.per-file-ignores]` from @[pyproject.toml], and set `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS = frozenset()` in @[scripts/audit_dict_eradication.py].
  - **Step 1.3 (`30aba5589`):** Eradicated process-local shadow state dictionaries (`self._local_invitations`, `self._local_assignments`, `self._memory_entries`) across @[backend_v2/services/auth/organization_service.py#L66-L1325], @[backend_v2/services/execution/assignment_service.py#L137-L1662], and @[backend_v2/services/cache/typed_cache.py#L109-L201]; routed all persistence through `entity_adapter` / `uow_factory` (`get_registered_uow_factory()`) and `TypedCacheService` (`RedisClientProtocol` / `InMemoryRedisClient`); deleted `RESIDUAL_LOCAL_SHADOW_STATE_FILES` from @[scripts/_ast_guardrails.py]; and verified all 6 Phase 1 test contracts and the full Phase 1 `<validation_gate>` with 0 errors and >90% test coverage.
- Completed Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 2 (@[docs/epic/tasks_EPIC_163/02_phase2_plan.md]):
  - **Step 2.1 (`6ab6c4b31`):** Removed all 14 silent identity, relational, and display field defaults (`= ""`, `= "unknown"`, `= "system"`) across all 8 files in `RESIDUAL_DEFAULT_VALUE_MODEL_FILES`, added `TenantSecretDTOFactory` and `ReportViewFactory` to @[backend_v2/tests/factories/model_factories.py], and updated callers and tests.
  - **Step 2.2 (`71f58275d`):** Converted all bare `Field(...)` declarations across @[backend_v2/core/hook_registry.py], @[backend_v2/core/registry.py], @[backend_v2/exceptions.py], @[backend_v2/models/chunking.py], and all 8 files in `backend_v2/models/domain/` to PEP 593 `Annotated[T, Field(...)]` syntax.
  - **Step 2.3 (`9a4a81f0b`):** Converted all bare `Field(...)` declarations across all 14 Batch 2 files in `backend_v2/models/dtos/`, `backend_v2/models/execution_core.py`, `backend_v2/models/llm.py`, `backend_v2/models/state.py`, `backend_v2/models/view/sdui.py`, `backend_v2/services/orchestrator/strategies/llm_execution/source_document_packer.py`, `scripts/diff_executions.py`, and `scripts/reconcile_storage.py` to PEP 593 `Annotated[T, Field(...)]` syntax; deleted `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` and `RESIDUAL_BARE_FIELD_FILES` from @[scripts/_ast_guardrails.py] and @[scripts/audit_technical_debt.py]; implemented all 4 Phase 2 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]; and passed the full Phase 2 `<validation_gate>` (`task-785`) and SDUI semantic parity suite with 0 violations and >90% coverage.
- Completed Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 3 (@[docs/epic/tasks_EPIC_163/03_phase3_plan.md]):
  - **Step 3.1 (`1d0649870`):** Added pure immutable transition helpers (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) returning `Self` on `ExecutionRecord` in @[backend_v2/models/domain/execution.py#L394-L411]; refactored @[backend_v2/workers/execution_worker.py#_mark_execution_failed], @[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic], and @[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase] to eliminate all `dict(record.step_states)` / `dict(record.profile_syntheses)` mutations and redundant `.model_validate()` calls; and implemented the 3 Step 3.1 `<test_contracts>` in @[backend_v2/tests/unit/workers/test_synthesis_reducers.py].
  - **Step 3.2 (`5b3413ef2`):** Eliminated all redundant `.model_validate()` calls on typed repository return models across @[backend_v2/hooks/atom_flattening.py#atom_flattening_hook], @[backend_v2/hooks/scoring/falsifier_hook.py#falsifier_adversarial_hook], @[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook], @[backend_v2/hooks/scoring/normalization_hook.py#score_normalization_hook], @[backend_v2/services/execution/ingress_service.py#L377-L783], @[backend_v2/services/orchestrator/strategies/logic.py#L38-L241], and @[backend_v2/services/orchestrator/synthesis_distiller.py#L173-L389]; deleted `RESIDUAL_FUTURE_PHASE_QGR028_FILES` from @[scripts/_ast_guardrails.py]; implemented the 3 Step 3.2 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]; and passed the full Step 3.2 `<validation_gate>` (`task-393`) with 0 violations and >90% test coverage.
- Completed Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 4 (@[docs/epic/tasks_EPIC_163/04_phase4_plan.md]):
  - **Step 4.1 (`6e1105aa1`):** Replaced all `dict[str, JsonValue]` and `list[JsonValue]` fields across @[backend_v2/models/dtos/atom_evaluation.py], @[backend_v2/models/dtos/hook_delta.py], @[backend_v2/models/dtos/lightweight_matrix.py], @[backend_v2/models/dtos/prompt_context.py], @[backend_v2/models/dtos/schema_manifest.py], @[backend_v2/models/dtos/system.py], @[backend_v2/models/dtos/trace.py], @[backend_v2/models/state.py], and @[backend_v2/models/dtos/node_execution.py] with closed Pydantic V2 DTOs and PEP 695 typed unions (`ScalarExtensionValue`, `ExtractedAtomScalar`, `GlobalMetricValue`, `HookDeltaPayloadValue`, `EngineDebugValue`, `XaiExtensionValue`, `PromptContextEntryValue`, `JsonSchemaNode`, `StepTraceValue`, `StepOutputContentValue`), and implemented the 3 Step 4.1 `<test_contracts>` in @[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py], @[backend_v2/tests/unit/models/dtos/test_system.py], and @[backend_v2/tests/unit/models/test_state.py].
  - **Step 4.2 (`d733b971b`):** Migrated @[backend_v2/hooks/scoring/matrix_hook.py#matrix_evaluation_hook], @[backend_v2/llm/client.py#L43-L880], @[backend_v2/llm/ingress_pipeline.py#LLMIngressPipeline], @[backend_v2/llm/mock_data.py#L482-L538], @[backend_v2/llm/mock.py], and @[backend_v2/services/llm_task_executor.py#L107-L526] away from `dict[str, JsonValue]` to generic `BaseModel` type parameters and typed `LightweightMatrixOutput` / `ScoringResultDTO` models, and implemented the 3 Step 4.2 `<test_contracts>` in @[backend_v2/tests/unit/services/test_llm_task_executor.py], @[backend_v2/tests/unit/hooks/test_matrix_hook.py], and @[backend_v2/tests/unit/test_mock_data.py].
  - **Step 4.3 (`3d4c0ed3b`):** Migrated @[backend_v2/services/orchestrator/context_router.py], @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py], @[backend_v2/services/orchestrator/matrix_reducer.py], @[backend_v2/services/orchestrator/result_projector.py], @[backend_v2/services/orchestrator/strategies/logic.py], and @[backend_v2/services/orchestrator/synthesis_payload_compressor.py] away from `dict[str, JsonValue]`; deleted `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` from @[scripts/_ast_guardrails.py] (leaving zero `RESIDUAL_*` exemption sets in @[scripts/_ast_guardrails.py]); implemented the 3 Step 4.3 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py] and @[backend_v2/tests/unit/services/orchestrator/test_synthesis_payload_compressor.py]; and passed the full Phase 4 `<validation_gate>`, SDUI semantic parity suite, and Flutter audit loop.
- Completed Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 5 (@[docs/epic/tasks_EPIC_163/05_phase5_plan.md]):
  - **Step 5.1 (`45ee21080`):** Replaced all `Map<String, Object?>` fields and casts across all 13 Group 2 Execution and Studio Freezed DTO models (`distilled_evaluation.dart`, `execution_create_request_dto.dart`, `execution_metadata.dart`, `execution_record.dart`, `frozen_context_snapshot.dart`, `report_data_v2_dto.dart`, `workflow_inputs.dart`, `model_config.dart`, `prompt_block.dart`, `prompt_block_simulation.dart`, `step_simulation.dart`, `workflow.dart`, `workflow_simulation.dart`) with closed Freezed classes enforcing `@JsonSerializable(disallowUnrecognizedKeys: true)` in 1:1 parity with backend Pydantic V2 DTOs, and implemented the 3 Step 5.1 `<test_contracts>` in @[client_app_v2/test/unit/features/execution/models/execution_record_test.dart].
  - **Step 5.2 (`e5529b455`):** Refactored all 12 Group 3 Execution and Studio controllers, cloner utilities, and views (`execution_controller.dart`, `dashboard_view.dart`, `dynamic_start_screen.dart`, `new_execution_view.dart`, `blueprint_editor_controller.dart`, `output_profile_controller.dart`, `prompt_blocks_controller.dart`, `workflow_cloner.dart`, `blueprint_editor_view.dart`, `model_registry_view.dart`, `step_builder_view.dart`, `mcp_tool_params_panel.dart`) to consume typed Freezed DTOs directly with zero `Map<String, Object?>`, and implemented the 3 Step 5.2 `<test_contracts>`.
  - **Step 5.3 (`18cdee79a`):** Refactored all 11 Group 3 shared widgets in `client_app_v2/lib/shared/widgets/` (`audit_trail_viewer.dart`, `comparison_matrix.dart`, `dynamic_form.dart`, `generic_grid.dart`, `pre_mortem_card.dart`, `result_dashboard.dart`, `schema_mapper.dart`, `score_card_radar.dart`, `specialist_section.dart`, `validation_timeline_widget.dart`, `workflow_selector.dart`) and their 11 unit test suites to strongly typed `@immutable` data models with zero `Map<String, Object?>`; shrank `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` in @[scripts/_dart_guardrails.py] from 45 files to exclusively the 9 Group 1 transport boundary files; implemented the 3 Step 5.3 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_dart_guardrails.py]; and passed the full Phase 5 `<validation_gate>`, `audit_dto_parity.py`, and `test_sdui_semantic_parity.py`.
- Completed Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 6 (@[docs/epic/tasks_EPIC_163/06_phase6_plan.md]):
  - **Step 6.1 (`2ae70c057`):** Replaced all 35 string-based `patch("...UnifiedWorkflowRepository")` calls across @[backend_v2/tests/unit/test_worker.py] (18), @[backend_v2/tests/unit/test_worker_synthesis.py] (16), and @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py] (1) with `patch.object(..., "UnifiedWorkflowRepository", return_value=mock_repo)` backed by stateful `InMemoryUnifiedWorkflowRepository` fixtures, and implemented all 3 Step 6.1 `<test_contracts>` (`test_worker_execution_persists_completed_record_in_memory_roundtrip`, `test_worker_handles_injected_repository_fault_and_clears_faults`, `test_worker_synthesis_accumulation_preserves_multi_profile_caches`).
  - **Step 6.2 (`2ae81e4f6`):** Replaced all 9 remaining string-based `patch("...UnifiedWorkflowRepository")` calls across @[backend_v2/tests/unit/workers/test_report_worker.py] (2), @[backend_v2/tests/unit/workers/test_synthesis_reducers.py] (3), and @[backend_v2/tests/unit/workers/test_synthesis_worker.py] (4) with `patch.object(..., "UnifiedWorkflowRepository", return_value=mock_repo)` backed by stateful `InMemoryUnifiedWorkflowRepository` fixtures; updated `CURRENT_RESIDUAL_CEILINGS.f` from `44` to `0` (`d=0, f=0, k=0, x=0, n=0, t=0, p=0, m=0, r=0, s=0`) and added `--verify-ceilings` in @[scripts/audit_warning_baseline.py]; added `_resolve_mypy_targets` in @[scripts/backend_audit_loop.py]; and implemented all 3 Step 6.2 `<test_contracts>` (`test_audit_warning_baseline_verify_ceilings_all_zero`, `test_report_worker_fails_fast_when_execution_record_missing_in_memory`, `test_synthesis_reducers_atomic_persistence_roundtrip`).
  - **Step 6.3 (`115e332ab`):** Implemented all 3 Step 6.3 `<test_contracts>` (`test_full_stack_epic_163_verification_gates_pass`, `test_guardrail_unit_suites_reject_regressed_exemptions`, `test_sdui_and_dto_parity_across_python_and_flutter`) in @[backend_v2/tests/unit/scripts/test_audit_warning_baseline.py]; updated `_resolve_stage_targets` in @[scripts/backend_audit_loop.py] to deduplicate `scripts/` when `is_macro_backend_gate` expands `discover_authoritative_scripts()`; passed 100% of full-stack quality gates (`backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict` with 93.55% coverage, `flutter_audit_loop.py client_app_v2/ --build`, `audit_dict_eradication.py`, `audit_warning_baseline.py --verify-ceilings`, `audit_dto_parity.py`, and `test_sdui_semantic_parity.py`); and verified 5/6 tests in `test_integration_real_llm.py`.
- Completed Tier 0 Red-Teaming (`/tier0-research-plan`) and Tier 2 Execution (`/tier2-execute --full-auto`) for Phase 7 (@[docs/epic/tasks_EPIC_163/07_phase7_plan.md]):
  - **Step 7.1 (`0944a276d`):** Added PEP 257 Google-style docstring (`Args:` and `Returns:`) to `ValidationHookPayloadDTO.model_validate` in @[backend_v2/models/domain/validation.py#L48-L85], migrated `test_dgr010_guarded_async_value_allowed` in @[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L737-L751] from `state.when(...)` to a Dart 3 `switch (state)` expression, and implemented the 3 Step 7.1 `<test_contracts>`.
  - **Step 7.2 (`e1858bfe2`):** Enforced `DGR013` (`freezed_when_ban`) and `DGR014` (`manual_riverpod_providers` Check 14A & `riverpod_read_vs_watch_ban` Check 14B) at `GuardrailSeverity.FATAL` in @[scripts/_dart_guardrails.py#L716-L858] (`C901 <= 10`), implemented Partition 13 unit tests and the 3 Step 7.2 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L1101-L1192], and verified 0 violations across `client_app_v2/lib --strict`.
  - **Step 7.3 (`0c25223d0`):** Extended `QGR013` in @[scripts/_ast_guardrails.py] (`_check_qgr013_import_from`, `_check_qgr013_ann_assign`, `_is_type_alias_annotation`) to reject legacy PEP 613 `from typing import TypeAlias` imports and `: TypeAlias = ...` annotations in favor of PEP 695 `type Alias = ...`; extended `QGR033` Check 33B (`_is_ellipsis_stub_body`, `_has_misplaced_docstring_after_future_import`) to require PEP 257 docstrings on top-level public functions and public class methods (`_function_depth == 0`, non-`Protocol` ellipsis stubs) and diagnose misplaced module docstrings appearing after `from __future__ import annotations`; implemented the 3 Step 7.3 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]; and verified 0 violations across `backend_v2 scripts --strict`.
  - **Step 7.4:** Synchronized @[.agents/skills/tier2-hardening-backend/SKILL.md#L72-L136], @[.agents/skills/tier2-hardening-frontend/SKILL.md#L66-L130], @[.agents/rules/04_directory_reference.md#L120], and @[scripts/auto_hardening_runner.py] (`resolve_target_rule_files`, `_inject_subagent_context_rules`, `_run_subagent_auto_fix_prepass`, `execute_subagent_pass` at `C901 <= 10`, and `compute_rules_sha256` hashing `AGENTS.md` + Tier 2 hardening `SKILL.md` playbooks); implemented the 3 Step 7.4 `<test_contracts>` in @[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1780-L1879]; and passed both the Step 7.4 `<validation_gate>` (`387 passed`) and the full-stack Integration Checkpoint (`backend_audit_loop.py backend_v2/ --test --ast-strict` with `6980 passed` / `97.48%` coverage / 0 violations; `flutter_audit_loop.py client_app_v2/ --build` with 0 violations).

## Learned
- In `RESIDUAL_MISSING_DOCSTRING_FILES`, @[backend_v2/models/dtos/variance.py#L17-L38], @[backend_v2/services/orchestrator/extraction_schema_factory.py#L83-L168], @[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L325], and @[backend_v2/services/orchestrator/schema_factory.py#L39-L411] placed `from __future__ import annotations` on line 1 before the module docstring on line 3, causing `ast.get_docstring(module_node)` to return `None`. Placing the module docstring at line 1 before `from __future__ import annotations` resolves the module-level `QGR001` violation, and `QGR033` Check 33B (`_has_misplaced_docstring_after_future_import`) now diagnoses this ordering explicitly.
- `QuorumUnitOfWork` (@[backend_v2/database/interfaces.py#L437-L477]) and `InMemoryUnitOfWork` (@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]) natively implement all persistence methods for `OrganizationInvitation` and `ExecutionTaskAssignment`, enabling deterministic UoW persistence and Fail-Fast `ConfigurationError` when neither `entity_adapter` nor `uow_factory` is configured.
- In @[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py], `test_cli_micro_lib_leaf_directory_positive_and_negative` must patch `scripts.flutter_audit_loop.os.chdir` so multi-file `scripts/` pytest runs do not mutate the process working directory.
- Under `pydantic.mypy` `--strict`, fields declared as `Annotated[list[T] | dict[K, V], Field(default_factory=...)]` without an RHS assignment (required because `= []`/`= {}` is banned as a mutable default and `= Field(...)` is banned as a duplicate `Field()`) are treated by MyPy as required keyword arguments on direct `Model(...)` construction, whereas `Model.model_validate(...)` and `Polyfactory` builders hydrate `default_factory` at runtime.
- When removing redundant `ExecutionRecord.model_validate` and `Step.model_validate` calls on repository return values (`QGR028`), test helpers (`_build_mock_deps` in @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]) must seed `InMemoryUnifiedWorkflowRepository` with validated `ExecutionRecord` instances rather than raw dicts so repository calls return typed domain models matching production `PostgresEntityAdapter` contracts.
- Replacing `dict[str, JsonValue]` on `LightweightMatrixOutput.extensions` with `dict[LaxXaiExtensionType, XaiExtensionValue]` (`str | int | float | bool | list[str] | None`) enforces strict scalar/string-list typing on XAI extension maps across `matrix_hook.py`, `result_projector.py`, and `synthesis_engine.py`, requiring unit tests (`test_synthesis_engine_with_lightweight_matrix_output` in @[backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py]) to pass typed `XaiExtensionValue` entries (`["high"]`) instead of raw nested dictionaries.
- Defining `@immutable` widget data classes with `const` constructors directly inside shared widget files in `client_app_v2/lib/shared/widgets/` eliminates `Map<String, Object?>` (`DGR005`) while keeping `requires_dart_codegen(target_path) == False` for fast `--micro` quality gate execution.
- In @[scripts/backend_audit_loop.py], passing both `backend_v2/` and `scripts/` in Macro Mode caused `mypy --strict` to receive both `scripts/` and expanded `scripts/__init__.py` (`Duplicate module named "scripts"`), and passing a directory under `backend_v2/tests/unit/<subpath>` hit `pyproject.toml` `exclude = ["^backend_v2/tests/"]`. Filtering bare `scripts` in `_resolve_stage_targets` when `is_macro_backend_gate` is `True` and mapping `backend_v2/tests/unit/<subpath>` to `backend_v2/<subpath>` in `_resolve_mypy_targets` resolves both cleanly.
- In @[scripts/auto_hardening_runner.py], decomposing `execute_subagent_pass` via `_run_subagent_auto_fix_prepass` and `_inject_subagent_context_rules` keeps McCabe complexity $\le 10$ while deterministically injecting domain-scoped `.agents/rules/` references (`resolve_target_rule_files`) into every headless subagent prompt and invalidating SHA-256 hardening cache entries whenever `AGENTS.md` or Tier 2 hardening `SKILL.md` playbooks mutate.

## Remaining
- Execute `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] @[docs/epic/EPIC_163_tracker.md]` to audit Phase 7 (and audit Phases 1–6), then proceed through the `Post-Implementation Gates` (`Tier 2 Hardening (Backend)`, `Tier 2 Hardening (Frontend)`, `/tier8-test-coverage-expansion`, `/tier7-describe-architecture`, and `/tier8-audit-epic`).

## Resume Command
```text
/tier8-audit-plan @[docs/epic/tasks_EPIC_163/07_phase7_plan.md] @[docs/epic/EPIC_163_tracker.md]
```

