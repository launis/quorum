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
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [x] Step 1.1: PEP 257 Docstring Remediation (`QGR001`) & Unlogged `AppException` Dual-Reporting (`QGR002`)
  - [x] Step 1.2: Audit Script `C901` McCabe Complexity Decomposition & Per-File-Ignore Removal
  - [ ] Step 1.3: Eradicate Process-Local Shadow State Fallbacks (`QGR030`) in Organization, Assignment & Cache Services
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 2: Pydantic V2 Schema Strictness — Zero Silent Defaults (`QGR020` Check 20C) & 100% PEP 593 `Annotated` (`QGR020` Check 20B)
**Plan:** @[docs/epic/tasks_EPIC_163/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/02_phase2_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [ ] Step 2.1: Eradicate Silent Identity, Relational & Display Field Defaults (`QGR020` Check 20C)
  - [ ] Step 2.2: Convert Bare `Field(...)` Declarations in Core, Exceptions, Chunking & Domain Models (`QGR020` Check 20B — Batch 1)
  - [ ] Step 2.3: Convert Bare `Field(...)` Declarations in DTOs, View, Packer & Scripts and Delete `QGR020` Exemption Sets (`QGR020` Check 20B — Batch 2)
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 3: Immutable `ExecutionRecord` State Transitions & Zero Redundant Re-Validation (`QGR028`)
**Plan:** @[docs/epic/tasks_EPIC_163/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/03_phase3_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [ ] Step 3.1: Immutable `ExecutionRecord` Transition Helpers & Worker State Updates
  - [ ] Step 3.2: Eradicate Redundant `.model_validate()` Calls in Hooks & Services and Delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 4: Strongly Typed DAG Context, Matrix Evaluation & Synthesis DTOs (`QGR027` `JsonValue` Eradication)
**Plan:** @[docs/epic/tasks_EPIC_163/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/04_phase4_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [ ] Step 4.1: Replace `JsonValue` Containers in Backend DTOs & State Envelopes
  - [ ] Step 4.2: Migrate LLM Client, Ingress Pipeline, Task Executor & Matrix Hook Away from `JsonValue`
  - [ ] Step 4.3: Migrate Orchestrator Stages, Compressor, Projector & Reducer and Delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES`
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 5: Frontend Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication
**Plan:** @[docs/epic/tasks_EPIC_163/05_phase5_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/05_phase5_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [ ] Step 5.1: Migrate Group 2 Execution & Studio Freezed DTO Models
  - [ ] Step 5.2: Migrate Group 3 Execution & Studio Controllers, Utilities & Views
  - [ ] Step 5.3: Migrate Group 3 Shared Widgets & Shrink `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` to 9 Transport Files
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Phase 6: Stateful `InMemoryUnitOfWork` Migration for Worker Test Suites (`Census F = 0`) & Final E2E Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_163/06_phase6_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_163/06_phase6_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]`
  - [ ] Step 6.1: Migrate `test_worker.py`, `test_worker_synthesis.py` & `test_worker_synthesis_accumulation.py` to Stateful `InMemoryUnifiedWorkflowRepository`
  - [ ] Step 6.2: Migrate `test_report_worker.py`, `test_synthesis_reducers.py` & `test_synthesis_worker.py` and Lock `Census F = 0`
  - [ ] Step 6.3: Full-Stack Global Quality Gates & Live E2E Verification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] @[docs/epic/EPIC_163_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Integration Checkpoint**: Run full-stack quality gates (`uv run python scripts/backend_audit_loop.py backend_v2/ scripts/ --test --ast-strict` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`) to verify cross-boundary contract parity before hardening.

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide verification of zero `RESIDUAL_*` exemption sets in `@[scripts/_ast_guardrails.py]`, zero `per-file-ignores` in `@[pyproject.toml]`, 9 transport boundary files in `@[scripts/_dart_guardrails.py]`, and `CURRENT_RESIDUAL_CEILINGS["f"] = 0` in `@[scripts/audit_warning_baseline.py]`.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Execute `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_163_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"` to audit all modified backend files:
  - [ ] @[backend_v2/core/hook_registry.py]
  - [ ] @[backend_v2/core/registry.py]
  - [ ] @[backend_v2/exceptions.py]
  - [ ] @[backend_v2/hooks/atom_flattening.py]
  - [ ] @[backend_v2/hooks/scoring/falsifier_hook.py]
  - [ ] @[backend_v2/hooks/scoring/matrix_hook.py]
  - [ ] @[backend_v2/hooks/scoring/normalization_hook.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/llm/ingress_pipeline.py]
  - [ ] @[backend_v2/llm/mock_data.py]
  - [ ] @[backend_v2/logging_config.py]
  - [ ] @[backend_v2/models/auth.py]
  - [ ] @[backend_v2/models/chunking.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/models/domain/inputs.py]
  - [ ] @[backend_v2/models/domain/matrix.py]
  - [ ] @[backend_v2/models/domain/metadata.py]
  - [ ] @[backend_v2/models/domain/output_profile.py]
  - [ ] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/domain/step.py]
  - [ ] @[backend_v2/models/domain/system_config.py]
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

1. **Before Starting Any Phase:** Run `/tier0-research-plan` on the target phase plan (`01_phase1_plan.md` through `06_phase6_plan.md`) alongside `@[docs/epic/EPIC_163_tracker.md]` to perform System 2 validation before `/tier2-execute`.
2. **Double-Entry Bookkeeping:** Upon completing each step (`Step X.Y`), immediately mark `[x]` on both the step checkbox in `@[docs/epic/EPIC_163_tracker.md]` and the corresponding `<dod_checklist>` item in the phase plan before creating an atomic `git commit`.
3. **Zero Residual Exemptions:** Do not introduce any new `RESIDUAL_*` sets in `@[scripts/_ast_guardrails.py]` or `per-file-ignores` in `@[pyproject.toml]`.

---

## Requirements Traceability Matrix

| Requirement ID | Epic Requirement Summary | Target Phase & Step | Verification Gate | Status |
| :--- | :--- | :--- | :--- | :--- |
| `REQ-163-001` | Add PEP 257 docstrings to 4 files (`QGR001`), add `logger.error` before `AppException` in `logging_config.py` (`QGR002`), and delete `RESIDUAL_MISSING_DOCSTRING_FILES` and `RESIDUAL_UNLOGGED_APP_EXCEPTION_FILES` | Phase 1, Step 1.1 | `backend_audit_loop.py --test --ast-strict` | `[x]` |
| `REQ-163-002` | Decompose C901 functions in `backend_audit_loop.py` and `flutter_audit_loop.py`, remove `[tool.ruff.lint.per-file-ignores]` from `pyproject.toml`, and empty `FROZEN_APPROVED_PER_FILE_IGNORE_PATHS` | Phase 1, Step 1.2 | `audit_dict_eradication.py` & `ruff check` | `[x]` |
| `REQ-163-003` | Eradicate `_local_invitations`, `_local_assignments`, and `_memory_entries` (`QGR030`) and delete `RESIDUAL_LOCAL_SHADOW_STATE_FILES` | Phase 1, Step 1.3 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-004` | Remove all 14 silent identity, relational, and display field defaults across 8 files (`QGR020` Check 20C) and delete `RESIDUAL_DEFAULT_VALUE_MODEL_FILES` | Phase 2, Step 2.1 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-005` | Convert bare `Field(...)` declarations in core, exceptions, chunking, and domain models to PEP 593 `Annotated[T, Field(...)]` (`QGR020` Check 20B Batch 1) | Phase 2, Step 2.2 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-006` | Convert bare `Field(...)` declarations in DTOs, view, packer, and scripts to PEP 593 `Annotated[T, Field(...)]` and delete `RESIDUAL_BARE_FIELD_FILES` (`QGR020` Check 20B Batch 2) | Phase 2, Step 2.3 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-007` | Add immutable `ExecutionRecord` transition helpers (`with_updated_step_state`, `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) and refactor worker state transitions (`QGR028`) | Phase 3, Step 3.1 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-008` | Eliminate redundant `.model_validate()` calls on typed DTOs across 7 hook and service files and delete `RESIDUAL_FUTURE_PHASE_QGR028_FILES` (`QGR028`) | Phase 3, Step 3.2 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-009` | Replace `dict[str, JsonValue]` and `list[JsonValue]` across 8 DTO and state files in `backend_v2/models/` with closed Pydantic V2 DTOs (`QGR027`) | Phase 4, Step 4.1 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-010` | Replace `dict[str, JsonValue]` in `LLMClient`, `LLMIngressPipeline`, `mock_data.py`, `LLMTaskExecutor`, and `matrix_hook.py` with generic `BaseModel` and typed DTOs (`QGR027`) | Phase 4, Step 4.2 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-011` | Replace `dict[str, JsonValue]` across 6 orchestrator files with typed DTOs and delete `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` (`QGR027`) | Phase 4, Step 4.3 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-012` | Replace `Map<String, Object?>` fields across all 13 Group 2 Execution and Studio Freezed DTO models (`DGR005`) | Phase 5, Step 5.1 | `flutter_audit_loop.py --build` | `[ ]` |
| `REQ-163-013` | Refactor all 12 Group 3 Execution and Studio controllers, cloner utilities, and views to consume typed Freezed DTOs (`DGR005`) | Phase 5, Step 5.2 | `flutter_audit_loop.py --build` | `[ ]` |
| `REQ-163-014` | Refactor all 11 Group 3 shared widgets to consume typed Freezed DTOs and shrink `DGR005_BOUNDARY_AND_OPEN_JSON_EXEMPT_FILES` to the 9 transport boundary files (`DGR005`) | Phase 5, Step 5.3 | `flutter_audit_loop.py --build` & `test_dart_guardrails.py` | `[ ]` |
| `REQ-163-015` | Replace 35 `UnifiedWorkflowRepository` patches across `test_worker.py`, `test_worker_synthesis.py`, and `test_worker_synthesis_accumulation.py` with stateful `InMemoryUnifiedWorkflowRepository` fixtures | Phase 6, Step 6.1 | `backend_audit_loop.py --test --ast-strict` | `[ ]` |
| `REQ-163-016` | Replace 9 `UnifiedWorkflowRepository` patches across `tests/unit/workers/` with stateful `InMemoryUnifiedWorkflowRepository` fixtures and lock `CURRENT_RESIDUAL_CEILINGS["f"] = 0` | Phase 6, Step 6.2 | `audit_warning_baseline.py --verify-ceilings` | `[ ]` |
| `REQ-163-017` | Execute global Backend, Frontend, Dict Eradication, Warning Baseline, DTO Parity, SDUI Semantic Parity, and Live E2E verification gates | Phase 6, Step 6.3 | Full-Stack & Live E2E Gates | `[ ]` |

---

# Session Handover Context

## Achieved
- Decomposed @[docs/epic/EPIC_163_residual_guardrail_and_tech_debt_eradication.md] and @[docs/epic/EPIC_163_audit_report.md] into 6 phased implementation plans under `docs/epic/tasks_EPIC_163/`:
  - @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] (Phase 1: `QGR001`, `QGR002`, `C901`, `QGR030`)
  - @[docs/epic/tasks_EPIC_163/02_phase2_plan.md] (Phase 2: `QGR020` Check 20C & Check 20B)
  - @[docs/epic/tasks_EPIC_163/03_phase3_plan.md] (Phase 3: `QGR028` Immutable `ExecutionRecord` Transitions & Zero Redundant Re-Validation)
  - @[docs/epic/tasks_EPIC_163/04_phase4_plan.md] (Phase 4: `QGR027` `JsonValue` Eradication)
  - @[docs/epic/tasks_EPIC_163/05_phase5_plan.md] (Phase 5: Flutter `DGR005` Open-JSON DTO & UI Consumer Eradication)
  - @[docs/epic/tasks_EPIC_163/06_phase6_plan.md] (Phase 6: Worker Test Migration `Census F = 0` & Final E2E Verification Gate)
- Completed Tier 0 Red-Teaming (`/tier0-research-plan`) on @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] with `CONVERGENCE ACHIEVED: 0 architectural defects found` (`audit_markdown_boundaries.py`, `audit_planner_output.py`, `audit_technical_debt.py --include-one-hop`, and `audit_tracker_output.py` all passed with `0` findings).

## Learned
- In `RESIDUAL_MISSING_DOCSTRING_FILES`, `@[backend_v2/models/dtos/variance.py#L17-L38]`, `@[backend_v2/services/orchestrator/extraction_schema_factory.py#L171-L238]`, `@[backend_v2/services/orchestrator/rag_preflight_service.py#L108-L305]`, and `@[backend_v2/services/orchestrator/schema_factory.py#L39-L411]` place `from __future__ import annotations` on line 1 before the module docstring on line 3, causing `ast.get_docstring(module_node)` to return `None`. Moving the module docstring to line 1 before `from __future__ import annotations` resolves the module-level `QGR001` violation.
- `QuorumUnitOfWork` (`@[backend_v2/database/interfaces.py#L437-L477]`) and `InMemoryUnitOfWork` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1960-L2034]`) already implement all persistence methods for `OrganizationInvitation` and `ExecutionTaskAssignment`, enabling clean removal of `_local_invitations` and `_local_assignments` in Phase 1 Step 1.3.

## Remaining
- Execute Phase 1 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]`), followed by `/tier8-audit-plan` on Phase 1, then sequentially execute Tier 0 Research and Tier 2 Execution across Phases 2 through 6, Post-Implementation Hardening, Architecture Documentation Sync, and Final Epic Audit.

## Resume Command
```text
/tier2-execute --full-auto @[docs/epic/tasks_EPIC_163/01_phase1_plan.md] @[docs/epic/EPIC_163_tracker.md]
```

