# Tracker: EPIC 165 — Zero-Compromise PostgreSQL 19 Schema Sovereignty, Pragmatic Normalization & Fail-Fast Persistence

**Epic:** @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]
**Task Directory:** @[docs/epic/tasks_EPIC_165/]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_gateway_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Phase Execution Status

### Phase 1: Pre-Implementation Cleanups, Fail-Fast Hydrator & Exception Translation Gate, Studio IDOR & 4-Phase In-Place Upsert Hardening, Single-UoW Transactionality & `StorageDriver` / V1 Ghost Repository Eradication
**Plan:** @[docs/epic/tasks_EPIC_165/01_phase1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_165/01_phase1_plan.md] @[docs/epic/EPIC_165_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/01_phase1_plan.md] @[docs/epic/EPIC_165_tracker.md]`
  - [x] Step 1.1: Unified Fail-Fast Hydrator (validate_hydrated_row) & SQLSTATE Exception Translation Gate (translate_postgres_exception)
  - [x] Step 1.2: Studio Multi-Tenant IDOR Closure, 4-Phase In-Place Upsert, Single-UoW clone_workflow & RBAC Symmetry
  - [x] Step 1.3: Append-Only PostgreSQL 19 audit_logs & usage_records Ledgers, SQL FinOps Rollups & delete_tenant_secret
  - [x] Step 1.4: Direct EntityPersistencePort Repository Cutover, StorageDriver & Dead V1 Ghost Repository Eradication

### Phase 2: 21-Table PostgreSQL 19 DDL Evolution, `system_configs` Split (`model_registries` & `mcp_gateways`), Junction Tables (`step_criteria_blocks` & `workflow_step_refs`), `Workflow.version` SQL OCC & Typed UUID Foreign Keys
**Plan:** @[docs/epic/tasks_EPIC_165/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md]`
  - [x] Step 2.1: system_configs Split into model_registries (mrg_) & mcp_gateways (mcp_), tenant_secrets.mcp_gateway_id FK, ModelProfile / LLMProviderConfig Cleanup & QGR030 Prefix Ratchet
  - [x] Step 2.2: Junction Tables (step_criteria_blocks & workflow_step_refs), Deferrable default_profile_id, Typed UUID FKs, VIRTUAL created_at, Single-UoW clone_workflow & Workflow.version SQL OCC
  - [x] Step 2.3: Source-Level seed_data.json Structural Split (model_registries & mcp_gateways), Operational Seed Scripts & DTO Parity Registry
  - [ ] Step 2.4: Flutter Studio EntityPrefix, ModelConfig / LlmModelConfig, ModelRegistryView, McpGateway & OrganizationIamSettingsView Freezed Parity

### Phase 3: `task_briefs` <-> `execution_assignments` Publication Snapshot (`task_brief_snapshot JSONB`), `ON DELETE RESTRICT`, `organization_id NOT NULL ON DELETE CASCADE` & $O(1)$ Indexed SQL Query Pushdown
**Plan:** @[docs/epic/tasks_EPIC_165/03_phase3_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_165/03_phase3_plan.md] @[docs/epic/EPIC_165_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/03_phase3_plan.md] @[docs/epic/EPIC_165_tracker.md]`
  - [ ] Step 3.1: Immutable task_brief_snapshot JSONB Parity & Fail-Fast TaskBrief Resolution on execution_assignments
  - [ ] Step 3.2: Kernel-Level ON DELETE RESTRICT & ROOT_SYSTEM organization_id NOT NULL ON DELETE CASCADE Across 123 Seed Rows
  - [ ] Step 3.3: O(1) Indexed SQL Query Pushdown for Execution Assignments & Executions
  - [ ] Step 3.4: Flutter Studio Freezed organizationId Non-Null Parity (TaskBrief, Workflow, PromptBlock, OutputProfile)

### Phase 4: `executions` + `execution_payloads` (`COMPRESSION lz4`) 1:1 Sidecar Split, Atomic Single-Statement `state_version` SQL OCC, Full-Duplex `ExecutionRecord.step_states` Eradication, Constraint-Enforcing `InMemoryUnitOfWork` & `audit_zero_orm_strictness.py` 22-Table Gate
**Plan:** @[docs/epic/tasks_EPIC_165/04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_165/04_phase4_plan.md] @[docs/epic/EPIC_165_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/04_phase4_plan.md] @[docs/epic/EPIC_165_tracker.md]`
  - [ ] Step 4.1: executions + execution_payloads (COMPRESSION lz4) 1:1 Sidecar Split & Atomic Single-Statement state_version SQL OCC
  - [ ] Step 4.2: Full-Duplex Backend Eradication of ExecutionRecord.step_states, active_profile_id, pdf_report_path & *_storage_path (Preserving profile_syntheses)
  - [ ] Step 4.3: Constraint-Enforcing InMemoryUnitOfWork & 22-Table audit_zero_orm_strictness.py (ZORM004-ZORM008)
  - [ ] Step 4.4: Flutter ExecutionRecord, ExecutionStep & Dashboard View Full-Duplex Parity
  - [ ] Step 4.5: Single-Pipeline Governance Lock Across audit_technical_debt.py, _ast_guardrails.py, audit_dict_eradication.py, Rules & Knowledge Items

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Seed Vault & Pre-Flight Integrity Gate:** Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- [ ] **[NOK] Backend, Frontend & Structural Parity Gate:** Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- [ ] **[NOK] Live E2E REST API Verification Gate:** Run `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_165_tracker.md]" --gate all --model gemini-4-carbon-medium --timeout 86400 --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[backend_v2/api/dependencies.py]
  - [ ] @[backend_v2/core/hook_registry.py]
  - [ ] @[backend_v2/database/__init__.py]
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/__init__.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/__init__.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]
  - [ ] @[backend_v2/database/postgres/graph_adapter.py]
  - [ ] @[backend_v2/database/repositories/__init__.py]
  - [ ] @[backend_v2/database/repositories/audit.py]
  - [ ] @[backend_v2/database/repositories/base.py]
  - [ ] @[backend_v2/database/repositories/components/__init__.py]
  - [ ] @[backend_v2/database/repositories/components/output_profile.py]
  - [ ] @[backend_v2/database/repositories/components/prompt_block.py]
  - [ ] @[backend_v2/database/repositories/components/task_brief.py]
  - [ ] @[backend_v2/database/repositories/execution.py]
  - [ ] @[backend_v2/database/repositories/identity.py]
  - [ ] @[backend_v2/database/repositories/report_artifact.py]
  - [ ] @[backend_v2/database/repositories/system.py]
  - [ ] @[backend_v2/database/repositories/workflow.py]
  - [ ] @[backend_v2/database/repository.py]
  - [ ] @[backend_v2/hooks/llm.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/llm/handler.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/auth.py]
  - [ ] @[backend_v2/models/domain/__init__.py]
  - [ ] @[backend_v2/models/domain/base.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/models/domain/output_profile.py]
  - [ ] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/domain/step.py]
  - [ ] @[backend_v2/models/domain/system_config.py]
  - [ ] @[backend_v2/models/domain/task_brief.py]
  - [ ] @[backend_v2/models/domain/workflow.py]
  - [ ] @[backend_v2/models/dtos/node_execution.py]
  - [ ] @[backend_v2/models/dtos/output_profile.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/models/dtos/system.py]
  - [ ] @[backend_v2/models/dtos/trace.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/models/execution_core.py]
  - [ ] @[backend_v2/models/llm.py]
  - [ ] @[backend_v2/models/state.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/seed/seed_registry.py]
  - [ ] @[backend_v2/services/auth/secret_service.py]
  - [ ] @[backend_v2/services/blueprint.py]
  - [ ] @[backend_v2/services/cache/typed_cache.py]
  - [ ] @[backend_v2/services/execution/assignment_service.py]
  - [ ] @[backend_v2/services/execution/context_service.py]
  - [ ] @[backend_v2/services/execution/facade.py]
  - [ ] @[backend_v2/services/execution/ingress_service.py]
  - [ ] @[backend_v2/services/execution/lifecycle_service.py]
  - [ ] @[backend_v2/services/execution/override_service.py]
  - [ ] @[backend_v2/services/execution/resumption_service.py]
  - [ ] @[backend_v2/services/export/metadata_resolver.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/__init__.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/base.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/logic.py]
  - [ ] @[backend_v2/services/report/__init__.py]
  - [ ] @[backend_v2/services/report/compilation_service.py]
  - [ ] @[backend_v2/services/report/format_reader_service.py]
  - [ ] @[backend_v2/services/report/lifecycle_service.py]
  - [ ] @[backend_v2/services/sdui/sdui_mapper_service.py]
  - [ ] @[backend_v2/services/studio/auth_validator.py]
  - [ ] @[backend_v2/services/studio/output_profile_service.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[backend_v2/services/studio/system_config_service.py]
  - [ ] @[backend_v2/services/studio/task_brief_service.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[backend_v2/services/usage_service.py]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[backend_v2/workers/execution_worker.py]
  - [ ] @[backend_v2/workers/report_worker.py]
  - [ ] @[backend_v2/workers/synthesis_reducers.py]
  - [ ] @[backend_v2/workers/synthesis_worker.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/ablation_live_executor.py]
  - [ ] @[scripts/audit_database_atoms.py]
  - [ ] @[scripts/audit_dict_eradication.py]
  - [ ] @[scripts/audit_dto_parity.py]
  - [ ] @[scripts/audit_skills_architecture.py]
  - [ ] @[scripts/audit_technical_debt.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/diff_executions.py]
  - [ ] @[scripts/reconcile_storage.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
  - [ ] @[scripts/sanitize_seed_vault.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_165_tracker.md]" --gate all --model gemini-4-carbon-medium --timeout 86400 --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_record.dart]
  - [ ] @[client_app_v2/lib/features/execution/models/execution_step.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/execution_view.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/output_profile.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/prompt_block.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/task_brief.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [ ] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_165_tracker.md] @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] @[ki_zero_orm_postgres_enforcement.md] @[ki_api_router_ssot_governance.md] @[ki_deterministic_hardening_state.md] @[ki_frontend_iam_role_segregation.md] @[ki_global_config_sovereignty.md] @[ki_god_code_prevention.md] @[ki_mcp_gateway_architecture.md] @[ki_router_ssot_and_crud_clone_lifecycle.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_zero_orm_postgres_enforcement.md]` (`[NEW]`): Document the closed 22-table PostgreSQL 19 UUIDv7 topology, single-pipeline `EntityPersistencePort` persistence (zero `StorageDriver`), `validate_hydrated_row` and `translate_postgres_exception` SSOT gates, `ON DELETE RESTRICT` / `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` / `ON DELETE CASCADE` rules, `executions` + `execution_payloads` (`COMPRESSION lz4`) sidecar split, single-statement SQL OCC (`WHERE state_version = $2` and `WHERE version = $2`), `task_brief_snapshot JSONB`, and `ZORM001`–`ZORM008`.
     - `@[ki_god_code_prevention.md]`, `@[ki_router_ssot_and_crud_clone_lifecycle.md]`, `@[ki_global_config_sovereignty.md]`, `@[ki_mcp_gateway_architecture.md]`, and `@[ki_zero_permissive_typing.md]`: Synchronize `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`) split, `tenant_secrets.mcp_gateway_id ON DELETE CASCADE`, 4-Phase In-Place Upsert IDOR guards, `ROOT_SYSTEM` `organization_id NOT NULL ON DELETE CASCADE`, and `TD_EXCEPT_SWALLOW_RETURN` / `TD_LEGACY_STORAGE_DRIVER` / `TD_UNWRAPPED_HYDRATION` AST guardrails.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect the removal of the 11 legacy driver and V1 ghost modules, the 22-table `001_pg19_uuidv7_schema.sql` topology, 9-collection `seed_data.json`, and `ZORM008`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the 22-table PostgreSQL 19 Zero-ORM persistence topology, single-pipeline `EntityPersistencePort` invariants, and `execution_payloads` (`COMPRESSION lz4`) sidecar architecture in present tense without historical language or Epic IDs.

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **DAG Orchestrator Permission Gate (`orchestrator_god_object_fragility`)**: Confirm explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` prior to executing Phase 1 Step 1.4 (`comp_repo` removal in `backend_v2/services/orchestrator/`) and Phase 4 Step 4.2 (`step_states` / `active_profile_id` removal in `backend_v2/services/orchestrator/`), and run the full `backend_audit_loop.py` gate.
- **Seed Vault Preservation (`prompt_preservation_mandate` & `03_seed_vault.md`)**: Create timestamped backups in `backend_v2/seed/backups/` prior to structural `seed_data.json` edits in Phase 2 Step 2.3 and Phase 3 Step 3.2, verify via `run_seed.py local --dry-run` and `audit_database_atoms.py --strict`, and touch ZERO `system_prompt`, `ai_description`, `instruction_text`, or matrix rubric natural-language coaching texts.
- **Atomic Commit Mandate**: Commit each verified logical step with explicit relative paths in English, keeping Backend and Frontend steps in separate atomic commits with regenerated `.freezed.dart` and `.g.dart` siblings staged cleanly.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `/tier0-research-plan -> /tier2-execute --full-auto -> Integration Checkpoint & Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.
- **Unattended Full-Lifecycle Batch Pipeline**: Commit newly generated plans and tracker first, then run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_165_tracker.md --full-lifecycle --timeout 86400` (append `--with-live-e2e` to include live LLM E2E tests).

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-165-001 | Implement `validate_hydrated_row`, `PromptBlockAdapter` discriminated union dispatch, `translate_postgres_exception` (`SQLSTATE 23503`/`23505`), and `_MATERIALIZE_WAVE_SQL` `DO UPDATE` idempotency across all entity hydrators. | Phase 1, Step 1.1 | [x] Completed |
| REQ-165-002 | Close cross-tenant Studio `PUT` IDOR vulnerabilities via 4-Phase In-Place Upsert, enforce atomic parent-before-child `clone_workflow` inside a single `async with uow:`, fix mixed Finnish strings, and align `StudioSystemConfigService` RBAC. | Phase 1, Step 1.2 | [x] Completed |
| REQ-165-003 | Add append-only UUIDv7 PostgreSQL 19 `audit_logs` (`aud_`) and `usage_records` (`usg_`) ledgers with SQL `SUM`/`COUNT` FinOps rollups, `delete_tenant_secret`, and `UsageAggregateDTO` shadow collection removal. | Phase 1, Step 1.3 | [x] Completed |
| REQ-165-004 | Cut over all 9 active V2 repositories and the zero-storage-logic `UnifiedWorkflowRepository(uow_factory)` facade directly onto `EntityPersistencePort`, deleting `driver.py`, `storage_driver.py`, 9 V1 ghost modules, and 12 companion test files. | Phase 1, Step 1.4 | [x] Completed |
| REQ-165-005 | Evolve `001_pg19_uuidv7_schema.sql` with the pre-production `DO $$` cutover gate, split `system_configs` into `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`), bind `tenant_secrets.mcp_gateway_id ON DELETE CASCADE`, and drop `ModelProfile.api_key` and `parsing_mode`. | Phase 2, Step 2.1 | [x] Completed |
| REQ-165-006 | Add `step_criteria_blocks` and `workflow_step_refs` (`ON DELETE RESTRICT`), deferrable `workflows.default_profile_id`, typed UUID FKs on `*_target_block` and `*.created_by`, `VIRTUAL` `created_at`, FK/tenant B-Tree indexes, and `Workflow.version` SQL OCC. | Phase 2, Step 2.2 | [x] Completed |
| REQ-165-007 | Split `"system_config"` in `seed_data.json`, `seed_registry.py`, `run_seed.py`, and operational CLI scripts into `"model_registries"` and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`) with 100% coaching prompt preservation. | Phase 2, Step 2.3 | [x] Completed |
| REQ-165-008 | Synchronize Flutter `EntityPrefix` (`enums.dart`), remove `apiKey` and `parsingMode` from `LlmModelConfig` and `ModelRegistryView`, and enforce required `McpGateway.organizationId`. | Phase 2, Step 2.4 | [ ] Pending |
| REQ-165-009 | Add immutable `task_brief_snapshot JSONB` (`enforce_assignment_task_brief_snapshot_parity`) to `ExecutionAssignment` and `execution_assignments`, freeze at cohort publication time, and drop `strict: bool = False` in `_validate_and_resolve_task_brief`. | Phase 3, Step 3.1 | [ ] Pending |
| REQ-165-010 | Enforce kernel `ON DELETE RESTRICT` on `execution_assignments` FKs (dropping `_check_active_assignment_usage`) and `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across all 123 `ROOT_SYSTEM` seed rows and Studio models/DTOs. | Phase 3, Step 3.2 | [ ] Pending |
| REQ-165-011 | Expose and wire $O(1)$ indexed SQL query methods (`get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization`, `list_executions_filtered`) on `EntityPersistencePort`, dropping `count_executions_by_matrix`. | Phase 3, Step 3.3 | [ ] Pending |
| REQ-165-012 | Synchronize non-nullable `required String organizationId` across Flutter Studio Freezed models (`TaskBrief`, `Workflow`, `PromptBlock`, `OutputProfile`). | Phase 3, Step 3.4 | [ ] Pending |
| REQ-165-013 | Split `executions` into the lean 30-column hot table and 1:1 `execution_payloads` (`COMPRESSION lz4`) sidecar table, delete `_offload_payloads`/`_hydrate_payloads`, and enforce atomic single-statement `WHERE state_version = $2` SQL OCC. | Phase 4, Step 4.1 | [ ] Pending |
| REQ-165-014 | Eradicate `ExecutionRecord.step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` across all Python models, DTOs, services, DAG Orchestrator stages, workers, and CLI scripts while preserving Stage 2 `profile_syntheses`. | Phase 4, Step 4.2 | [ ] Pending |
| REQ-165-015 | Upgrade `InMemoryUnitOfWork` and `InMemoryEntityAdapter` to enforce 22-table FK/UNIQUE/OCC constraints in unit tests, and update `audit_zero_orm_strictness.py` to the 22-table topology, 16-table `CANONICAL_ENTITY_PK_TABLES`, and `ZORM008`. | Phase 4, Step 4.3 | [ ] Pending |
| REQ-165-016 | Synchronize Flutter `ExecutionRecord`, `ExecutionStep`, `ExecutionView`, `DashboardView`, and `ResultDashboard` by removing `stepStates`, `activeProfileId`, `pdfReportPath`, and `*_StoragePath` while retaining `profileSyntheses`. | Phase 4, Step 4.4 | [ ] Pending |
| REQ-165-017 | Lock single-pipeline persistence governance in `audit_technical_debt.py` (`TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, `TD_UNWRAPPED_HYDRATION`), `_ast_guardrails.py`, `audit_dict_eradication.py`, `.agents/rules/`, and `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`. | Phase 4, Step 4.5 | [ ] Pending |

# Session Handover Context

## Achieved
- Executed Tier 1 Epic Planning (`/tier1-planner`), Tier 0 Red-Teaming, and Tier 2 Full-Auto Execution across Phase 1 (`@[docs/epic/tasks_EPIC_165/01_phase1_plan.md]`): implemented `validate_hydrated_row` and `translate_postgres_exception`, closed Studio multi-tenant `PUT` IDOR vulnerabilities via 4-Phase In-Place Upsert and single-UoW `clone_workflow`, migrated `audit_logs` (`aud_`) and `usage_records` (`usg_`) onto PostgreSQL 19 ledgers, and eradicated `StorageDriver`, `PostgresStorageDriver`, and all dead V1 ghost repositories across 9 active `EntityPersistencePort`-backed repositories.
- Completed Tier 0 System 2 Red-Teaming (`/tier0-research-plan`) on `@[docs/epic/tasks_EPIC_165/02_phase2_plan.md]` with 100% 4-way bidirectional parity across `Target Files`, `touched_artifacts`, the 5-Column Architectural Directives Table, and `execution_protocol` Steps `2.1`–`2.4` (`49` production `[MODIFY]` targets and `156` test/factory/fake `[MODIFY]` targets):
  - **Step 2.1 (`system_configs` Split, `tenant_secrets.mcp_gateway_id`, `ModelProfile` / `LLMProviderConfig` Cleanup & `QGR030` Prefix Ratchet)**: Removed STI `type` discriminator fields from `SystemConfigModelRegistry` and `SystemConfigMCPGateways`, added required `organization_id` (`EntityPrefix.ORGANIZATION`) to `SystemConfigMCPGateways`, removed `LLMProviderConfig.parsing_mode` in `@[backend_v2/models/llm.py]`, preserved `StudioSystemConfigService` public method names so `model_registry.py` and `mcp_gateways.py` routers (`OPAQUE_STRIPE_ID_REGEX`) remain untouched, expanded `<demolish>` to all 15 retired `system_config` union/DTO/adapter/repo symbols, and ratcheted `_QGR030_ENTITY_PREFIXES` (`mrg`, `mcp`, retiring `^sys_[0-9a-fA-F]{32}$`) in `@[scripts/_ast_guardrails.py]`.
  - **Step 2.2 (21-Table DDL, `step_criteria_blocks` & `workflow_step_refs`, Typed UUID FKs, Single-UoW `clone_workflow` & `Workflow.version` SQL OCC)**: Dropped redundant `steps.criteria_block_ids JSONB` (projecting ordered `criteria_block_ids` from `step_criteria_blocks` via `ORDER BY scb.position ASC` and syncing via `UNNEST`), eliminated all 4 Python full-table delete loops (`PromptBlockRepositoryImpl`, `StudioWorkflowService`, `WorkflowRepositoryImpl`, `StudioOutputProfileService`), added `parse_prefixed_uuid7` validators across `Workflow`, `OutputProfile`, `Organization`, `User`, and `ExecutionRecord` (`IdentityRepositoryImpl`), pre-generated `profile_mapping` in `StudioWorkflowService.clone_workflow` for single-save (`version=1`) deferred-FK persistence, enforced `WHERE workflows.version = $6 RETURNING version` SQL OCC with `WorkflowRepositoryImpl.update_workflow` version re-fetch, and locked the 21-table Phase 2 topology in `@[scripts/audit_zero_orm_strictness.py]`.
  - **Step 2.3 & Step 2.4 (`seed_data.json` Split, `audit_dto_parity.py` Alias Parity & Flutter Freezed Sync)**: Mapped exact `seed_data.json` bounds (`#L2-L554` and `#L20805-L21600`), registered `"systemconfigmodelregistry": "modelconfig"` and `"modelprofile": "llmmodelconfig"` in `EXPLICIT_MODEL_ALIASES` inside `@[scripts/audit_dto_parity.py]`, removed redundant `llm/handler.py` from Phase 2 targets (already completed in Phase 1), synchronized `OrganizationIamSettingsView` (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`) and all 14 Flutter test suites, and structured `--micro` intermediate step gates so Backend (`Steps 2.1–2.3`) and Frontend (`Step 2.4`) commit cleanly without cross-language parity deadlocks.

## Learned
- Keeping `StudioSystemConfigService` method names (`get_all_system_configs`, `get_system_config`, `create_system_config_draft`, `save_system_config`, `delete_system_config`, `clone_system_config`) unchanged avoids touching `model_registry.py` and `mcp_gateways.py` while keeping `delete_system_config` and `get_system_config` out of `<demolish>` so `audit_epic_coverage.py` passes at Epic completion.
- `steps.criteria_block_ids JSONB` must be dropped in Step 2.2 once `step_criteria_blocks` is introduced so Step criteria order has a single normalized SSOT (`ORDER BY scb.position ASC`).
- Intermediate Backend step gates (`Steps 2.1–2.3`) must pass `--micro` to `backend_audit_loop.py` prior to Step 2.4's Flutter Freezed and `enums.dart` commit, followed by full Macro `backend_audit_loop.py` (including Stage 8 `audit_dto_parity.py --fail-on-mismatch`, Stage 10 `audit_zero_orm_strictness.py`, and `test_enum_parity.py`) and `flutter_audit_loop.py` in Step 2.4 and `<validation_gate>`.

## Remaining
- Execute Tier 2 Implementation for Phase 2 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md]`), followed by Phases 3–4 Tier 0 Red-Teaming and Tier 2 Execution, the Full-Stack Integration Checkpoint, Tier 2 Hardening (Backend & Frontend), `/tier7-describe-architecture`, and `/tier8-audit-epic`.

## Resume Command
```powershell
# Interactive Next Action (Start a fresh chat session for Phase 2 Execution):
/tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md]

# Unattended Start-to-Finish Full-Lifecycle Batch Pipeline (Phases 2-4 Tier 0 -> Tier 2 -> Hardening -> Seed/Parity/Audits -> Tier 7 -> Tier 8):
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_phase_runner.py --tracker docs/epic/EPIC_165_tracker.md --full-lifecycle --timeout 86400 --max-retries 6
```

