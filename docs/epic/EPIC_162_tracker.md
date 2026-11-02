<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# Tracker: EPIC 162 — Studio Target Block Synchronization, CognitiveTier SSOT Enforcement & DAG Optimistic Concurrency Resilience

- **Epic:** @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]
- **Task Directory:** @[docs/epic/tasks_EPIC_162/]

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups, 100% `CognitiveTier` Enum Enforcement & `LLMClient.from_strategy` Eradication
**Plan:** @[docs/epic/tasks_EPIC_162/01_phase1_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/01_phase1_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [x] Step 1.1: Pre-Implementation Technical Debt Cleanups in `ablation_live_executor.py` and `in_memory_uow.py`
  - [x] Step 1.2: `PipelineConfig.default_strategy` `CognitiveTier` Enum Enforcement & Production Call-Site Migration
  - [x] Step 1.3: Eradication of `LLMClient.from_strategy`, Static AST Guardrail Enforcement & Unit Test Suite Migration
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI
**Plan:** @[docs/epic/tasks_EPIC_162/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/02_phase2_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]` (`c3c6ae39b`)
  - [x] Step 2.1: Backend `StudioWorkflowService.save_workflow` Auto-Pruning & `StudioOutputProfileService.save_output_profile` Target Block Validation
  - [x] Step 2.2: Localization `.arb` Strings & Flutter `MatrixGraphItemEditor` Error `FilterChip` Rendering
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 3: DAG Execution Resilience — Semantic Oscillation Detector, Per-Run `ExecutionBudget` Cap, Node-Level `input_merkle_hash` & MCP XML Control-Tag Sanitization
**Plan:** @[docs/epic/tasks_EPIC_162/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/03_phase3_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [x] Step 3.1: Cumulative `usage_agg` Accounting & Canonical SHA-256 Semantic Oscillation Short-Circuit in `execute_engine_retry_stage`
  - [x] Step 3.2: Per-Run `ExecutionBudget` Ceiling in `Settings` & `execute_topological_waves_stage`
  - [x] Step 3.3: Node-Level `ExecutionStep.input_merkle_hash` Computation, Resumption Verification, Flutter DTO Parity & MCP XML Control-Tag Sanitization
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_162/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/04_phase4_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]` (`c8fe8abd5`, `2c0fa20de`, `a5b60d555`)
  - [x] Step 4.1: `ExecutionRecord.state_version` Schema, PostgreSQL 19 DDL, Zero-ORM Strictness & Entity Adapter OCC Enforcement
  - [x] Step 4.2: Cross-Process OCC Wiring in `ExecutionOverrideService`, `ExecutionCommitter`, In-Memory Fakes & Flutter `ExecutionRecord` Parity
  - [x] Step 4.3: Global Backend & Frontend Quality Gates, DTO/SDUI Parity & Mandatory Live E2E REST API Verification Gate
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend & Frontend Full-Stack Integration Gate**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`, `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`, and `uv run python scripts/audit_dto_parity.py --fail-on-mismatch`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide verification of zero `from_strategy` calls across `backend_v2/` and `scripts/`, zero unsynchronized `OutputProfile` target block references, and 100% `state_version` OCC enforcement (`scripts/audit_epic_coverage.py --epic docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md`).
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_162_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"`.
  - [ ] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]
  - [ ] @[backend_v2/database/postgres/storage_driver.py]
  - [ ] @[backend_v2/database/repositories/execution.py]
  - [ ] @[backend_v2/hooks/interaction_hook.py]
  - [ ] @[backend_v2/hooks/linguistics.py]
  - [ ] @[backend_v2/hooks/source_verification_hook.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/models/dtos/node_execution.py]
  - [ ] @[backend_v2/models/dtos/trace.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/services/chat_parser.py]
  - [ ] @[backend_v2/services/execution/override_service.py]
  - [ ] @[backend_v2/services/execution/resumption_service.py]
  - [ ] @[backend_v2/services/mcp/mcp_tool_loop.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]
  - [ ] @[backend_v2/services/studio/output_profile_service.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/ablation_live_executor.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/run_ablation_benchmark.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_162_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend {target}'"`.
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_step.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies or deprecated parameters remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic across all modified modules.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_162_tracker.md] @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_router_ssot_and_crud_clone_lifecycle.md] @[ki_deterministic_hardening_state.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document 100% `CognitiveTier` Enum enforcement on `PipelineConfig.default_strategy`, complete removal of `LLMClient.from_strategy`, and static AST guardrail enforcement in `scripts/_ast_guardrails.py`.
     - `@[ki_router_ssot_and_crud_clone_lifecycle.md]`: Document automatic pruning of stale `target_blocks`, `variance_target_block`, and `user_role_target_block` references on `StudioWorkflowService.save_workflow`, `StudioOutputProfileService.save_output_profile` validation, and removable error-styled `FilterChip` rendering in `MatrixGraphItemEditor`.
     - `@[ki_zero_permissive_typing.md]`: Document `ExecutionStep.input_merkle_hash` and `ExecutionRecord.state_version` full-duplex serialization parity across Python Pydantic V2, PostgreSQL 19 (`001_pg19_uuidv7_schema.sql`), and Flutter Freezed models.
     - `@[ki_deterministic_hardening_state.md]`: Document cumulative `usage_agg` accounting and canonical SHA-256 semantic oscillation short-circuiting in `execute_engine_retry_stage`, per-run execution budget enforcement (`max_tokens_per_run`, `max_cost_usd_per_run`, `max_total_steps_per_run`) in `execute_topological_waves_stage`, MCP XML control-tag sanitization in `_assemble_evidence_payload`, and PostgreSQL 19 `state_version` OCC enforcement.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` reflects updated orchestrator, studio, and persistence responsibilities.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing Studio target block synchronization, `CognitiveTier` SSOT routing, semantic oscillation detection, per-run execution budgets, node-level Merkle input hashing, MCP XML boundary sanitization, and `state_version` OCC in present tense without historical language or Epic IDs.

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: Commit each verified logical step with explicit relative paths in English.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `/tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan -> Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-162-001** | Resolve pre-existing `TD_DICT_GET` and `TD_MODEL_FACTORY` technical debt items in `scripts/ablation_live_executor.py#L153-L179`, `scripts/ablation_live_executor.py#L649-L687`, `backend_v2/tests/fakes/in_memory_uow.py#L951-L1123`, and `backend_v2/tests/fakes/in_memory_uow.py#L1125-L1200`. | Phase 1, Step 1.1 | [x] Complete |
| **REQ-162-002** | Type `PipelineConfig.default_strategy` as `CognitiveTier \| None = None` in `backend_v2/models/enums.py#L1051-L1061`, update `PIPELINE_REGISTRY` entries to `CognitiveTier.FAST`, and migrate `chat_parser.py#L72-L346`, `interaction_hook.py#L43-L184`, `linguistics.py#L77-L229`, and `source_verification_hook.py#L155-L281` to `LLMClient.from_tier`. | Phase 1, Step 1.2 | [x] Complete |
| **REQ-162-003** | Delete `LLMClient.from_strategy` from `backend_v2/llm/client.py#L44-L911`, enforce static AST guardrail bans in `scripts/_ast_guardrails.py#L781-L3490`, and migrate all 16 unit test suites to `LLMClient.from_tier`. | Phase 1, Step 1.3 | [x] Complete |
| **REQ-162-004** | Implement `_sync_output_profiles_for_workflow` in `StudioWorkflowService.save_workflow` (`workflow_service.py#L283-321`) to prune stale `target_blocks`, `variance_target_block`, and `user_role_target_block` references and coerce `view_type`, and validate `variance_target_block` and `user_role_target_block` against `allowed_prompt_blocks` in `StudioOutputProfileService.save_output_profile` (`output_profile_service.py#L96-155`). | Phase 2, Step 2.1 | [x] Complete |
| **REQ-162-005** | Add `staleTargetBlockChipLabel` to `app_en.arb#L2963-2983` and `app_fi.arb#L2213-2233` and render removable error-styled `FilterChip` widgets for stale block IDs in `matrix_graph_item_editor.dart#L260-305` and `profile_section_config_tab.dart#L41-72`. | Phase 2, Step 2.2 | [x] Complete |
| **REQ-162-006** | Accumulate `usage_agg` across all anomaly retries and abort immediately on duplicate canonical SHA-256 output digests (`seen_anomaly_digests`) in `execute_engine_retry_stage` (`engine_retry_stage.py#L411-L588`). | Phase 3, Step 3.1 | [x] Complete |
| **REQ-162-007** | Add `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` to `Settings` (`settings.py#L47-L1199`) and enforce per-run budget ceilings via `ErrorCodes.QUOTA_EXCEEDED` in `execute_topological_waves_stage` (`wave_orchestrator_stage.py#L280-L369`). | Phase 3, Step 3.2 | [x] Complete |
| **REQ-162-008** | Add `input_merkle_hash` to `ExecutionStep` (`execution.py#L135-L170` and `execution_step.dart#L8-39`), wire Merkle drift invalidation across `step_execution_stage.py#L238-L403`, `workflow_bootstrap_stage.py#L148-L326`, and `resumption_service.py#L128-L192`, and strip reserved XML boundary tags in `_assemble_evidence_payload` (`mcp_tool_loop.py#L412-L448`). | Phase 3, Step 3.3 | [x] Complete |
| **REQ-162-009** | Add `state_version` to `ExecutionRecord` (`execution.py#L189-L356`), `ExecutionUpdateDTO` (`trace.py#L65-L118`), `NodeExecutionUpdateDTO` (`node_execution.py#L30-L72`), `001_pg19_uuidv7_schema.sql#L233-281`, and `audit_zero_orm_strictness.py`, and enforce conditional `expected_state_version` OCC conflict detection (`ErrorCodes.CONFLICT`, HTTP 409) in `execution_and_report_stage.py#L299-L366`, `storage_driver.py#L326-353`, and `execution.py#L28-L442`. | Phase 4, Step 4.1 | [x] Complete |
| **REQ-162-010** | Wire `expected_state_version` OCC across `InMemoryUnitOfWork` (`in_memory_uow.py#L1336-1391`), `InMemoryExecutionRepository` (`in_memory_repositories.py#L206-226`), `ExecutionOverrideService` (`override_service.py#L35-L425`), `ExecutionCommitter` (`execution_committer.py#L41-L107`), and Flutter `ExecutionRecord` (`execution_record.dart#L17-84`). | Phase 4, Step 4.2 | [x] Complete |
| **REQ-162-011** | Execute Cross-Language DTO Parity (`audit_dto_parity.py`), Zero-ORM Strictness (`audit_zero_orm_strictness.py`), SDUI Semantic Parity (`test_sdui_semantic_parity.py`), Global Backend and Flutter Audit Loops, and the Mandatory Live E2E REST API Verification Gate (`test_integration_real_llm.py`). | Phase 4, Step 4.3 | [x] Complete |

# Session Handover Context

## Achieved
- Completed `/tier0-research-epic` on `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` and generated `@[docs/epic/EPIC_162_audit_report.md]` with 100% coverage and zero AST boundary errors.
- Completed `/tier1-planner @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` generating `@[docs/epic/tasks_EPIC_162/01_phase1_plan.md]` through `@[docs/epic/tasks_EPIC_162/04_phase4_plan.md]`.
- Completed `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]` across all 3 steps:
  - **Step 1.1 (`af3dafc5b`)**: Resolved all 4 touched-scope technical debt items in `@[scripts/ablation_live_executor.py]` (`compare_strategies` typed as `tuple[LaxCognitiveTier, LaxCognitiveTier] | None = None`, `"system_config" in data` and `strat in telemetry` membership checks, `LLMClient.from_tier`) and `@[backend_v2/tests/fakes/in_memory_uow.py]` (`_hydrate_in_memory_execution_record` and `_hydrate_in_memory_proposition_node`), and migrated `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`.
  - **Step 1.2 (`71ba73f8e`)**: Enforced `CognitiveTier | None = None` on `PipelineConfig.default_strategy` in `@[backend_v2/models/enums.py]`, updated `PIPELINE_REGISTRY` (`"chat_parser"`, `"studio_generation"`, `"interaction_hook"`) to `default_strategy=CognitiveTier.FAST`, migrated all 4 production backend call sites (`@[backend_v2/services/chat_parser.py]`, `@[backend_v2/hooks/interaction_hook.py]`, `@[backend_v2/hooks/linguistics.py]`, `@[backend_v2/hooks/source_verification_hook.py]`) to `LLMClient.from_tier(CognitiveTier.FAST, ...)`, and updated all 5 unit test suites (`@[backend_v2/tests/unit/models/test_enums.py]`, `@[backend_v2/tests/unit/services/test_chat_parser.py]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`).
  - **Step 1.3 (`cc28095bc`)**: Deleted `LLMClient.from_strategy` from `@[backend_v2/llm/client.py]`, enforced `QGR030` (`GuardrailSeverity.FATAL`) in `@[scripts/_ast_guardrails.py]` banning `.from_strategy(...)` and string-literal `LLMClient.from_tier("...")` calls, and migrated all remaining 10 unit test suites (`@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py]`, `@[backend_v2/tests/unit/guardrails/test_cdata_hardening_comprehensive.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_rag_preflight_chat_inflation.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]`, `@[backend_v2/tests/unit/test_ast_domain_security_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`).
- Completed `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]` across both steps:
  - **Step 2.1 (`9f32c34c6`)**: Implemented `_sync_output_profiles_for_workflow` in `@[backend_v2/services/studio/workflow_service.py]` to automatically prune stale `target_blocks`, `variance_target_block`, and `user_role_target_block` references and coerce `view_type` (`MATRIX_3D -> COMPARE_2D -> METRICS_1D` and empty-group removal) on `StudioWorkflowService.save_workflow`, enforced `allowed_prompt_blocks` validation on `variance_target_block` and `user_role_target_block` in `StudioOutputProfileService.save_output_profile` (`@[backend_v2/services/studio/output_profile_service.py]`), and verified positive, boundary, and negative unit tests in `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]` and `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`.
  - **Step 2.2 (`c3c6ae39b`)**: Added `staleTargetBlockChipLabel` to `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`, synchronized `allowedBlockIds` with `executionPersonaBlockId` in `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_section_config_tab.dart]`, rendered removable error-styled `FilterChip` widgets for stale block IDs in `@[client_app_v2/lib/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor.dart]`, and verified widget unit tests in `@[client_app_v2/test/unit/features/studio/views/widgets/profile/blocks/matrix_graph_item_editor_test.dart]`.
- Completed `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]` across all 3 steps:
  - **Step 3.1 (`b0591fc62`)**: Fixed cumulative `usage_agg` token accounting across anomaly retries and implemented canonical SHA-256 semantic oscillation short-circuiting (`_compute_retry_output_digest`, `seen_anomaly_digests`) in `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, with unit tests in `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`.
  - **Step 3.2 (`47846b2d9`)**: Added `ErrorCodes.QUOTA_EXCEEDED` in `@[backend_v2/exceptions.py]`, added `max_tokens_per_run`, `max_cost_usd_per_run` (validated via `@field_validator`), and `max_total_steps_per_run` in `@[backend_v2/settings.py]`, and enforced per-run execution budget ceilings between topological waves via `_enforce_execution_budget` in `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, with unit tests in `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`.
  - **Step 3.3 (`f9ae9d221`)**: Added `input_merkle_hash: str | None = None` to `ExecutionStep` (`@[backend_v2/models/domain/execution.py]` and `@[client_app_v2/lib/features/execution/models/execution_step.dart]`), implemented `compute_step_input_merkle_hash`, `_fetch_referenced_prompt_blocks`, and `invalidate_drifted_passed_steps` across `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`, and `@[backend_v2/services/execution/resumption_service.py]`, implemented `_sanitize_mcp_xml_control_tags` in `@[backend_v2/services/mcp/mcp_tool_loop.py]`, and verified unit tests in `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`, and `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`.
- Completed `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]` across all 3 steps:
  - **Step 4.1 (`c8fe8abd5`)**: Added `state_version: Annotated[int, Field(ge=1, default=1, ...)] = 1` to `ExecutionRecord` (`@[backend_v2/models/domain/execution.py]`), `expected_state_version` and `state_version` to `ExecutionUpdateDTO` (`@[backend_v2/models/dtos/trace.py]`) and `NodeExecutionUpdateDTO` (`@[backend_v2/models/dtos/node_execution.py]`), `ErrorCodes.CONFLICT` to `@[backend_v2/exceptions.py]`, `state_version INTEGER NOT NULL DEFAULT 1` to `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, and `"state_version"` to `APPROVED_ADAPTER_RECORD_COLUMNS` in `@[scripts/audit_zero_orm_strictness.py]`, and enforced `expected_state_version` OCC conflict detection (`ErrorCodes.CONFLICT`, HTTP 409) and atomic increment across `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`, `@[backend_v2/database/postgres/storage_driver.py]`, and `@[backend_v2/database/repositories/execution.py]`, with unit tests in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`.
  - **Step 4.2 (`2c0fa20de`)**: Synchronized `state_version` OCC and atomic increments in `@[backend_v2/tests/fakes/in_memory_uow.py]` and `@[backend_v2/tests/fakes/in_memory_repositories.py]`, wired `expected_state_version=record.state_version` in `ExecutionOverrideService` (`@[backend_v2/services/execution/override_service.py]`), preserved concurrent human overrides and incremented `state_version` in `ExecutionCommitter.commit_trace` (`@[backend_v2/services/orchestrator/dag_executor/execution_committer.py]`), added `@JsonKey(name: 'state_version') @Default(1) int stateVersion` to Flutter `ExecutionRecord` (`@[client_app_v2/lib/features/execution/models/execution_record.dart]`), and verified unit tests in `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]`, and `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`.
  - **Step 4.3 (`a5b60d555`)**: Verified 100% pass across `scripts/audit_zero_orm_strictness.py`, `scripts/audit_dto_parity.py`, `backend_v2/tests/integration/test_sdui_semantic_parity.py`, `scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` (`6,764 passed`, `97.32%` coverage), `scripts/flutter_audit_loop.py client_app_v2/ --build`, and live E2E integration suite `backend_v2/tests/integration/test_integration_real_llm.py` (`6 passed`).

## Learned
- `ExecutionStep` (`#L135-L170`) and `ExecutionRecord` (`#L196-L375`) in `@[backend_v2/models/domain/execution.py]` must be referenced as distinct single-class AST spans to satisfy `MBD004` in `scripts/audit_markdown_boundaries.py`.
- Pre-existing technical debt in `@[scripts/ablation_live_executor.py]` and `@[backend_v2/tests/fakes/in_memory_uow.py]` is resolved in Phase 1 Step `1.1` (`0` findings in `scripts/audit_technical_debt.py`).
- Static AST guardrail `QGR030` in `QuorumGuardrailVisitor.visit_Call` (`@[scripts/_ast_guardrails.py]`) enforces zero `.from_strategy(...)` calls and zero raw string literal `tier` arguments to `.from_tier(...)` across all 407 `backend_v2` modules and 32 `scripts` modules.
- When `StudioWorkflowService._sync_output_profiles_for_workflow` prunes stale `target_blocks` or `variance_target_block`, it must also coerce `MatrixSynthesisGroup.view_type` and prune `TargetBlockType.MATRIX_GRAPHS_BLOCK` / `TargetBlockType.VARIANCE_VALIDATION_BLOCK` and `XaiExtensionType.VARIANCE_VALIDATION` so `OutputProfile.model_validate` passes all coherence validators.
- On `Step` (`@[backend_v2/models/domain/step.py]`), referenced prompt blocks are resolved from `criteria_block_ids`, `role_block_id`, `execution_persona_block_id`, and `extraction_protocol_block_id` when computing `compute_step_input_merkle_hash`.
- Adding `ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version INTEGER NOT NULL DEFAULT 1;` to `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` ensures `PostgresPoolManager.apply_migrations()` idempotently upgrades existing local PostgreSQL 19 `executions` tables prior to live E2E execution.

## Remaining
- Execute `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]` to audit Phase 4, then complete the Post-Implementation Gates (`auto_hardening_runner.py`, `audit_epic_coverage.py`), `/tier7-describe-architecture`, and `/tier8-audit-epic`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]
```
