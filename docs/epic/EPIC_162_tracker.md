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
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [x] Step 1.1: Pre-Implementation Technical Debt Cleanups in `ablation_live_executor.py` and `in_memory_uow.py`
  - [ ] Step 1.2: `PipelineConfig.default_strategy` `CognitiveTier` Enum Enforcement & Production Call-Site Migration
  - [ ] Step 1.3: Eradication of `LLMClient.from_strategy`, Static AST Guardrail Enforcement & Unit Test Suite Migration
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI
**Plan:** @[docs/epic/tasks_EPIC_162/02_phase2_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/02_phase2_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [ ] Step 2.1: Backend `StudioWorkflowService.save_workflow` Auto-Pruning & `StudioOutputProfileService.save_output_profile` Target Block Validation
  - [ ] Step 2.2: Localization `.arb` Strings & Flutter `MatrixGraphItemEditor` Error `FilterChip` Rendering
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/02_phase2_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 3: DAG Execution Resilience — Semantic Oscillation Detector, Per-Run `ExecutionBudget` Cap, Node-Level `input_merkle_hash` & MCP XML Control-Tag Sanitization
**Plan:** @[docs/epic/tasks_EPIC_162/03_phase3_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/03_phase3_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [ ] Step 3.1: Cumulative `usage_agg` Accounting & Canonical SHA-256 Semantic Oscillation Short-Circuit in `execute_engine_retry_stage`
  - [ ] Step 3.2: Per-Run `ExecutionBudget` Ceiling in `Settings` & `execute_topological_waves_stage`
  - [ ] Step 3.3: Node-Level `ExecutionStep.input_merkle_hash` Computation, Resumption Verification, Flutter DTO Parity & MCP XML Control-Tag Sanitization
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/03_phase3_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_162/04_phase4_plan.md]
- [x] **[OK] Create Plan:** `docs/epic/tasks_EPIC_162/04_phase4_plan.md`
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]`
  - [ ] Step 4.1: `ExecutionRecord.state_version` Schema, PostgreSQL 19 DDL, Zero-ORM Strictness & Entity Adapter OCC Enforcement
  - [ ] Step 4.2: Cross-Process OCC Wiring in `ExecutionOverrideService`, `ExecutionCommitter`, In-Memory Fakes & Flutter `ExecutionRecord` Parity
  - [ ] Step 4.3: Global Backend & Frontend Quality Gates, DTO/SDUI Parity & Mandatory Live E2E REST API Verification Gate
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend & Frontend Full-Stack Integration Gate**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`, `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`, and `uv run python scripts/audit_dto_parity.py --fail-on-mismatch`

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
| **REQ-162-002** | Type `PipelineConfig.default_strategy` as `CognitiveTier \| None = None` in `backend_v2/models/enums.py#L1051-L1061`, update `PIPELINE_REGISTRY` entries to `CognitiveTier.FAST`, and migrate `chat_parser.py#L72-L346`, `interaction_hook.py#L43-L184`, `linguistics.py#L77-L229`, and `source_verification_hook.py#L155-L281` to `LLMClient.from_tier`. | Phase 1, Step 1.2 | [ ] Pending |
| **REQ-162-003** | Delete `LLMClient.from_strategy` from `backend_v2/llm/client.py#L44-L911`, enforce static AST guardrail bans in `scripts/_ast_guardrails.py#L781-L3490`, and migrate all 16 unit test suites to `LLMClient.from_tier`. | Phase 1, Step 1.3 | [ ] Pending |
| **REQ-162-004** | Implement `_sync_output_profiles_for_workflow` in `StudioWorkflowService.save_workflow` (`workflow_service.py#L283-321`) to prune stale `target_blocks`, `variance_target_block`, and `user_role_target_block` references and coerce `view_type`, and validate `variance_target_block` and `user_role_target_block` against `allowed_prompt_blocks` in `StudioOutputProfileService.save_output_profile` (`output_profile_service.py#L96-155`). | Phase 2, Step 2.1 | [ ] Pending |
| **REQ-162-005** | Add `staleTargetBlockChipLabel` to `app_en.arb#L2963-2983` and `app_fi.arb#L2213-2233` and render removable error-styled `FilterChip` widgets for stale block IDs in `matrix_graph_item_editor.dart#L260-305` and `profile_section_config_tab.dart#L41-72`. | Phase 2, Step 2.2 | [ ] Pending |
| **REQ-162-006** | Accumulate `usage_agg` across all anomaly retries and abort immediately on duplicate canonical SHA-256 output digests (`seen_anomaly_digests`) in `execute_engine_retry_stage` (`engine_retry_stage.py#L411-L588`). | Phase 3, Step 3.1 | [ ] Pending |
| **REQ-162-007** | Add `max_tokens_per_run`, `max_cost_usd_per_run`, and `max_total_steps_per_run` to `Settings` (`settings.py#L47-L1199`) and enforce per-run budget ceilings via `ErrorCodes.QUOTA_EXCEEDED` in `execute_topological_waves_stage` (`wave_orchestrator_stage.py#L280-L369`). | Phase 3, Step 3.2 | [ ] Pending |
| **REQ-162-008** | Add `input_merkle_hash` to `ExecutionStep` (`execution.py#L135-L170` and `execution_step.dart#L8-39`), wire Merkle drift invalidation across `step_execution_stage.py#L238-L403`, `workflow_bootstrap_stage.py#L148-L326`, and `resumption_service.py#L128-L192`, and strip reserved XML boundary tags in `_assemble_evidence_payload` (`mcp_tool_loop.py#L412-L448`). | Phase 3, Step 3.3 | [ ] Pending |
| **REQ-162-009** | Add `state_version` to `ExecutionRecord` (`execution.py#L189-L356`), `ExecutionUpdateDTO` (`trace.py#L65-L118`), `NodeExecutionUpdateDTO` (`node_execution.py#L30-L72`), `001_pg19_uuidv7_schema.sql#L233-279`, and `audit_zero_orm_strictness.py`, and enforce conditional `expected_state_version` OCC conflict detection (`ErrorCodes.CONFLICT`, HTTP 409) in `execution_and_report_stage.py#L299-L366`, `storage_driver.py#L326-353`, and `execution.py#L28-L442`. | Phase 4, Step 4.1 | [ ] Pending |
| **REQ-162-010** | Wire `expected_state_version` OCC across `InMemoryUnitOfWork` (`in_memory_uow.py#L1336-1391`), `InMemoryExecutionRepository` (`in_memory_repositories.py#L206-226`), `ExecutionOverrideService` (`override_service.py#L35-L425`), `ExecutionCommitter` (`execution_committer.py#L41-L107`), and Flutter `ExecutionRecord` (`execution_record.dart#L17-84`). | Phase 4, Step 4.2 | [ ] Pending |
| **REQ-162-011** | Execute Cross-Language DTO Parity (`audit_dto_parity.py`), Zero-ORM Strictness (`audit_zero_orm_strictness.py`), SDUI Semantic Parity (`test_sdui_semantic_parity.py`), Global Backend and Flutter Audit Loops, and the Mandatory Live E2E REST API Verification Gate (`test_integration_real_llm.py`). | Phase 4, Step 4.3 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed `/tier0-research-epic` on `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` and generated `@[docs/epic/EPIC_162_audit_report.md]` with 100% coverage and zero AST boundary errors.
- Completed `/tier1-planner @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]`:
  - Created task directory `@[docs/epic/tasks_EPIC_162/]` containing all 4 phased implementation plans:
    1. `@[docs/epic/tasks_EPIC_162/01_phase1_plan.md]` (Phase 1: Pre-Implementation Technical Debt Cleanups, 100% `CognitiveTier` Enum Enforcement & `LLMClient.from_strategy` Eradication — Steps `1.1`, `1.2`, `1.3`)
    2. `@[docs/epic/tasks_EPIC_162/02_phase2_plan.md]` (Phase 2: Studio `Workflow` & `OutputProfile` Stale `target_blocks` Synchronization & Error FilterChip UI — Steps `2.1`, `2.2`)
    3. `@[docs/epic/tasks_EPIC_162/03_phase3_plan.md]` (Phase 3: DAG Execution Resilience — Semantic Oscillation Detector, Per-Run `ExecutionBudget` Cap, Node-Level `input_merkle_hash` & MCP XML Control-Tag Sanitization — Steps `3.1`, `3.2`, `3.3`)
    4. `@[docs/epic/tasks_EPIC_162/04_phase4_plan.md]` (Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate — Steps `4.1`, `4.2`, `4.3`)
  - Created and synchronized `@[docs/epic/EPIC_162_tracker.md]` with bidirectional Requirements Traceability Matrix (`REQ-162-001` through `REQ-162-011`) and complete Backend (26 `.py` targets) and Frontend (4 `.dart` targets) hardening checklists.

## Learned
- `ExecutionStep` (`#L135-L170`) and `ExecutionRecord` (`#L189-L356`) in `@[backend_v2/models/domain/execution.py]` must be referenced as distinct single-class AST spans to satisfy `MBD004` in `scripts/audit_markdown_boundaries.py`.
- Pre-existing technical debt in `@[scripts/ablation_live_executor.py]` and `@[backend_v2/tests/fakes/in_memory_uow.py]` is isolated into Phase 1 Step `1.1` so all downstream phases execute on a zero-debt baseline.
- `Settings` float fields (`max_cost_usd_per_run`) must validate `>= 0.0` via a local `@field_validator` method rather than `Field(ge=0.0)` to comply with `vertex_serving_grammar_fix`.

## Remaining
- Execute Phase 1 starting with Tier 0 Research & Analysis (`/tier0-research-plan`) on `@[docs/epic/tasks_EPIC_162/01_phase1_plan.md]`, followed by Phases 2, 3, and 4, Post-Implementation Gates, `/tier7-describe-architecture`, and `/tier8-audit-epic`.

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_162/01_phase1_plan.md] @[docs/epic/EPIC_162_tracker.md]
```
