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

# EPIC 165 - Phase 4: `executions` + `execution_payloads` (`COMPRESSION lz4`) 1:1 Sidecar Split, Atomic Single-Statement `state_version` SQL OCC, Full-Duplex `ExecutionRecord.step_states` Eradication, Constraint-Enforcing `InMemoryUnitOfWork` & `audit_zero_orm_strictness.py` 22-Table Gate

**Overview:** Split `executions` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, and `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` into the lean 30-column hot `executions` table and the transactional 1:1 cold `lz4`-compressed `execution_payloads` sidecar table (retaining `ExecutionRecord.profile_syntheses` and `frozen_context.mcp_tool_audit` while dropping `_offload_record_blobs`, `_hydrate_record_blobs`, `_save_blob_payload`, `_updates_exceed_blob_threshold`, and `_BLOB_OFFLOAD_THRESHOLD_BYTES` local filesystem offload), replace the two-step `SELECT state_version`-then-`UPSERT` TOCTOU check in `save_execution_row` and `update_execution_occ_row` with a deterministic two-branch persistence contract (`INSERT ... ON CONFLICT` when `expected_state_version is None` for initial record creation vs. atomic single-statement SQL Optimistic Concurrency Control `UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1::uuid AND state_version = $2 RETURNING state_version` when `expected_state_version is not None`), split hydration into primary-key `hydrate_execution_row` (`INNER JOIN execution_payloads`) and payload-free `hydrate_execution_summary_row` (`frozen_context=None`) while hydrating matched records by primary key in `@[backend_v2/services/orchestrator/synthesis_distiller.py]` and `ExecutionRepositoryImpl.get_recent_completed_executions` (removing legacy `get_storage_driver()` disk trace fallbacks in `@[backend_v2/hooks/archival.py]` and `@[backend_v2/workers/synthesis_reducers.py]`), bind `effective_org_id` onto new records in `@[backend_v2/services/execution/ingress_service.py]`, eradicate `ExecutionRecord.step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` full-duplex across Python (`@[backend_v2/models/domain/execution.py#L252-L545]`, `ExecutionCoreFields`, services, DAG Orchestrator stages, workers, CLI scripts) and Flutter (`@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`, `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `dashboard_view.dart`, `result_dashboard.dart`, and 5 Dart test suites) with zero `@computed_field` shims, upgrade `@[backend_v2/tests/fakes/in_memory_uow.py#L1996-L2007]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`) to enforce all 22-table FK/UNIQUE/OCC constraints in unit tests, and lock single-pipeline governance permanently across `@[scripts/audit_zero_orm_strictness.py#L439-L459]` (`ZORM004`–`ZORM008`), `@[scripts/audit_technical_debt.py#L253-L579]` (`TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, `TD_UNWRAPPED_HYDRATION`), `@[scripts/_ast_guardrails.py#L110-L129]`, `@[scripts/audit_dict_eradication.py#L169-L628]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `.agents/rules/`, and `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`.

**DAG Orchestrator Permission Gate (`orchestrator_god_object_fragility`):** Mutating `@[backend_v2/services/orchestrator/synthesis_distiller.py]`, `backend_v2/services/orchestrator/dag_executor/` (`execution_committer.py`, `workflow_bootstrap_stage.py`, `step_execution_stage.py`, `wave_orchestrator_stage.py`), and `backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py` to remove `step_states` and `active_profile_id` references and hydrate historical `profile_syntheses` by primary key requires explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` prior to `/tier2-execute`, followed by the full `backend_audit_loop.py` gate.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 4 Forensic Context, Retained SSOT Invariants & Sidecar SQL DDL (Verbatim from EPIC 165 + Tier 0 Hardening)

### Forensic Finding 4 [P1 HIGH]: `executions` Intra-Row Duplication, Non-Transactional File Offload & Non-Atomic OCC
* **Forensic Anchors:**
  * `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
  * `@[backend_v2/models/domain/execution.py#L252-L545]`
  * `@[backend_v2/services/execution/ingress_service.py]`
  * `@[backend_v2/services/execution/override_service.py#L35-L482]`
  * `@[backend_v2/services/orchestrator/synthesis_distiller.py]`
  * `@[backend_v2/hooks/archival.py]`
  * `@[backend_v2/services/report/compilation_service.py#L33-L299]`
  * `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`
* **Root Cause (5 Coupled Defects + Tier 0 Red-Team Boundary Hardening):**
  1. **Intra-Row State Duplication (`steps` vs. `step_states`):** Every step's `scorecard_atoms` and token metrics are duplicated in both `steps` (`JSONB` list) and `step_states` (`JSONB` map). `ExecutionOverrideService.override_atom` mutates `step_states` without updating `steps`, causing immediate post-override split-brain, while `ReportCompilationService` and `ExecutionRecord.with_updated_profile_synthesis` inject synthetic `"sys_render_{profile_id}"` keys into `step_states` in violation of `ban_heuristic_identifier_matching`.
  2. **Duplicate Profile Foreign Keys (`active_profile_id` vs. `output_profile_id`):** Two overlapping nullable Foreign Keys to `output_profiles(id)` exist on the same `executions` row.
  3. **Shadow `pdf_report_path` Cache, Misplaced Hot-Row `profile_syntheses` Payload & Summary List Callers:** `pdf_report_path` duplicates binary report location owned authoritatively by `report_artifacts` + `report_binaries` (`universal_ssot_and_normalization_mandate`), whereas `profile_syntheses` (`dict[str, RenderedSynthesisCache]`, populated by Stage 2 `synthesis_worker.py` and consumed by `BlueprintTransformer`, `DistributionFormatter`, `SynthesisDistiller`, `ExecutionOverrideService.clear_profile_synthesis`, `ReportCompilationService`, and Flutter `ProfileSynthesisEntryDto`) has no column in `report_artifacts` (`@[backend_v2/models/domain/report_artifact.py#L22-L79]`) and bloats the hot `executions` tuple instead of residing in the 1:1 cold `lz4` `execution_payloads` sidecar (`feature_sovereignty_mandate`). When `list_executions_filtered` omits cold `execution_payloads` joins via `hydrate_execution_summary_row` (`frozen_context=None`), `SynthesisDistiller._fetch_historical_summary` and `ExecutionRepositoryImpl.get_recent_completed_executions` MUST hydrate matched candidates via `get_execution` so historical `profile_syntheses` and precedent `execution_trace` remain populated.
  4. **Non-Transactional Filesystem Offload (`*_storage_path`), Legacy `get_storage_driver()` Disk Fallbacks & Silent Empty-Blob Coalescing (Finding 7 Site 8):** Offloading `>100KB` `frozen_context`, `execution_trace`, and `context_variables` blobs via `_offload_record_blobs`, `_hydrate_record_blobs`, `_save_blob_payload`, and `_updates_exceed_blob_threshold` in `@[backend_v2/database/repositories/execution.py#L82-L118]` splits one logical record across PostgreSQL and local disk without ACID rollback guarantees, while `hooks/archival.py` (`retrieve_precedent_hook`) and `workers/synthesis_reducers.py` (`recover_trace_telemetry`) still contain legacy `get_storage_driver()` disk reads for `executions/{id}/execution_trace.json`, and `update_execution` defaults missing `state_version` to `1` and returns `False` on missing `existing_doc`.
  5. **TOCTOU Race in Optimistic Concurrency Control (`save_execution_row` & `update_execution_occ_row`), Cutover `DO $$` Guard, `executions.organization_id NOT NULL` Binding & Permissive `InMemoryUnitOfWork` (Finding 8 Item 6):** `save_execution_row` executes a separate `SELECT state_version` before `INSERT ... ON CONFLICT (id) DO UPDATE`, allowing two concurrent writers reading the same `state_version` to clobber each other; initial record creation (`expected_state_version is None`) requires `INSERT` while OCC updates (`expected_state_version is not None`) require single-statement `UPDATE ... WHERE id = $1::uuid AND state_version = $2 RETURNING state_version` unified with `update_execution_occ_row`. On post-Phase 3 databases, the `DO $$` cutover guard in `001_pg19_uuidv7_schema.sql` must also check `executions.step_states` / missing `execution_payloads` so `CREATE TABLE IF NOT EXISTS executions` is not a silent no-op; `ExecutionIngressService` must bind `effective_org_id` (`initiator.organization_id` or `SystemOrganizations.ROOT_SYSTEM.value`) while keeping `ExecutionRecord.organization_id: str | None = None` untouched (`ban_drive_by_schema_mutations`); and `@[backend_v2/tests/fakes/in_memory_uow.py#L3753-L3827]` lacks 22-table FK `ON DELETE RESTRICT` / `NO ACTION DEFERRABLE` / `CASCADE` (including `_StoreSnapshot` rollback of `seed_tables` and `execution_payloads`), `UNIQUE`, and `state_version`/`version` OCC enforcement.

### Retained SSOT Invariants & Producer-Consumer Contracts (Sections 1.5, 2.3 & 2.5)
* **Retained Stage 2 `ExecutionRecord.profile_syntheses` (`dict[str, RenderedSynthesisCache]` & Flutter `ProfileSynthesisEntryDto`):** Preserved on `ExecutionRecord` (`feature_sovereignty_mandate`) alongside `with_updated_profile_synthesis` and `with_cleared_profile_syntheses`, relocated off the hot `executions` tuple into `execution_payloads.profile_syntheses` (`JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb`).
* **Retained Domain `ExecutionRecord.organization_id: str | None = None` Schema Contract:** Preserved on Python and Flutter `ExecutionRecord` (`ban_drive_by_schema_mutations`), while `ExecutionIngressService` binds `effective_org_id` (`initiator.organization_id` when present, else `SystemOrganizations.ROOT_SYSTEM.value`), `ExecutionRecordFactory.organization_id` defaults to `Use(generate_opaque_id, EntityPrefix.ORGANIZATION)`, and `save_execution_row` / `InMemoryEntityAdapter.save_execution` enforce non-null `parse_prefixed_uuid7(record.organization_id, EntityPrefix.ORGANIZATION)` at the persistence boundary.
* **Retained Native `asyncpg` Binary `0x01` JSONB Codec & `QuorumUnitOfWork` Transaction Boundary:** Retained in `@[backend_v2/database/postgres/pool.py#L422-L652]` and `@[backend_v2/database/postgres/uow.py#L185-L435]`, and audited alongside `@[scripts/audit_database_atoms.py#L329-L787]` across the closed 22-table topology.
* **Producer 3 (`PostgresEntityAdapter.save_execution_row` in `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, DAG Orchestrator, `ExecutionOverrideService`, & `synthesis_worker.py`):** Persists hot lifecycle state and canonical `steps: list[ExecutionStep]` into `executions` (`INSERT` when `expected_state_version is None`; single-statement `UPDATE ... WHERE id = $1::uuid AND state_version = $2 RETURNING state_version` SQL OCC when `expected_state_version is not None`) and cold `lz4`-compressed payloads (`raw_inputs`, `frozen_context` retaining `mcp_tool_audit`, `context_variables`, `execution_trace`, and `profile_syntheses`) into `execution_payloads` within one atomic transaction.
* **Consumer 3 (SDUI/PDF Report Services, `SynthesisDistiller`, `retrieve_precedent_hook`, & Flutter Freezed `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]` / `@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L45]`):** Consumes `ExecutionRecord.steps` and `ExecutionRecord.profile_syntheses` across Backend Python, Jinja PDF, and Flutter Desktop with zero `step_states`, `active_profile_id`, `pdf_report_path`, or `*_storage_path` shadow fields.

### Canonical `executions` + `execution_payloads` PostgreSQL 19 DDL Specification (Section 1.4.1 Item 5 + `ZORM004`/`ZORM007` Parity)

```sql
-- Pre-Production Cutover Gate Predicate Extension in 001_pg19_uuidv7_schema.sql:
-- Extend the DO $$ IF predicate with:
--   OR EXISTS (
--       SELECT 1 FROM information_schema.columns
--       WHERE table_schema = 'public' AND table_name = 'executions' AND column_name = 'step_states'
--   )
--   OR NOT EXISTS (
--       SELECT 1 FROM information_schema.tables
--       WHERE table_schema = 'public' AND table_name = 'execution_payloads'
--   )
-- and include execution_payloads in DROP TABLE IF EXISTS ... CASCADE.

-- 5. Lean 30-Column executions Table + 1:1 lz4 execution_payloads Sidecar Table (retaining profile_syntheses)
CREATE TABLE IF NOT EXISTS executions (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    workflow_version INTEGER NOT NULL DEFAULT 1 CHECK (workflow_version >= 1),
    state_version INTEGER NOT NULL DEFAULT 1 CHECK (state_version >= 1),
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE SET NULL,
    status TEXT NOT NULL,
    target_locale TEXT NOT NULL,
    progress INTEGER CHECK (progress IS NULL OR (progress >= 0 AND progress <= 100)),
    status_message TEXT,
    steps JSONB NOT NULL DEFAULT '[]'::jsonb,
    source_identity_manifest JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_resumable BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_tokens BIGINT NOT NULL DEFAULT 0 CHECK (prompt_tokens >= 0),
    completion_tokens BIGINT NOT NULL DEFAULT 0 CHECK (completion_tokens >= 0),
    cached_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cached_tokens >= 0),
    reasoning_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reasoning_tokens >= 0),
    cumulative_synthesis_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cumulative_synthesis_tokens >= 0),
    dag_cost_usd NUMERIC(14, 6) NOT NULL DEFAULT 0,
    cumulative_synthesis_cost NUMERIC(14, 6) NOT NULL DEFAULT 0,
    cost_estimate NUMERIC(14, 6) NOT NULL DEFAULT 0,
    models_used JSONB NOT NULL DEFAULT '{}'::jsonb,
    execution_summary JSONB,
    metadata JSONB,
    duration_ms BIGINT NOT NULL DEFAULT 0 CHECK (duration_ms >= 0),
    error TEXT,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    CONSTRAINT enforce_execution_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_execution_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_execution_output_profile_uuidv7 CHECK (
        output_profile_id IS NULL OR uuid_extract_version(output_profile_id) = 7
    ),
    CONSTRAINT enforce_execution_created_by_uuidv7 CHECK (
        created_by IS NULL OR uuid_extract_version(created_by) = 7
    )
);
ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version INTEGER NOT NULL DEFAULT 1;
CREATE INDEX IF NOT EXISTS idx_executions_org_id_created ON executions(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_output_profile_id ON executions(output_profile_id);
CREATE INDEX IF NOT EXISTS idx_executions_created_by ON executions(created_by);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);

CREATE TABLE IF NOT EXISTS execution_payloads (
    execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE,
    raw_inputs JSONB COMPRESSION lz4 NOT NULL,
    frozen_context JSONB COMPRESSION lz4,
    context_variables JSONB COMPRESSION lz4 NOT NULL,
    execution_trace JSONB COMPRESSION lz4 NOT NULL,
    profile_syntheses JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT enforce_execution_payload_uuidv7 CHECK (uuid_extract_version(execution_id) = 7)
);
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L252-L545]`
- `[MODIFY] @[backend_v2/models/execution_core.py#L70-L123]`
- `[MODIFY] @[backend_v2/models/state.py]`
- `[MODIFY] @[backend_v2/models/dtos/trace.py#L66-L86]`
- `[MODIFY] @[backend_v2/models/dtos/node_execution.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L41-L420]`
- `[MODIFY] @[backend_v2/hooks/archival.py]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L89-L1076]`
- `[MODIFY] @[backend_v2/services/execution/assignment_service.py#L150-L1929]`
- `[MODIFY] @[backend_v2/services/execution/context_service.py]`
- `[MODIFY] @[backend_v2/services/execution/ingress_service.py]`
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L35-L482]`
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L25-L324]`
- `[MODIFY] @[backend_v2/services/execution/resumption_service.py#L30-L242]`
- `[MODIFY] @[backend_v2/services/orchestrator/synthesis_distiller.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`
- `[MODIFY] @[backend_v2/services/report/compilation_service.py#L33-L299]`
- `[MODIFY] @[backend_v2/services/report/lifecycle_service.py#L36-L464]`
- `[MODIFY] @[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]`
- `[MODIFY] @[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]`
- `[MODIFY] @[backend_v2/workers/execution_worker.py#_mark_execution_failed]`
- `[MODIFY] @[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`
- `[MODIFY] @[scripts/reconcile_storage.py#L59-L71]`
- `[MODIFY] @[scripts/diff_executions.py]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L439-L459]`
- `[MODIFY] @[scripts/audit_technical_debt.py#L253-L579]`
- `[MODIFY] @[scripts/_ast_guardrails.py#L110-L129]`
- `[MODIFY] @[scripts/audit_dict_eradication.py#L169-L628]`
- `[MODIFY] @[scripts/audit_skills_architecture.py#L160-L175]`
- `[MODIFY] @[.agents/rules/01-python-backend.md]`
- `[MODIFY] @[.agents/rules/03_seed_vault.md]`
- `[MODIFY] @[.agents/rules/04_directory_reference.md]`
- `[MODIFY] @[.agents/skills/tier2-hardening-backend/SKILL.md]`
- `[NEW] @[ki_zero_orm_postgres_enforcement.md]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L1996-L2007]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/execution_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/dashboard_view.dart]`
- `[MODIFY] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test___init__.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_repository.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_archival.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_node_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_trace.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_execution_core.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_state.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_context_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_ingress_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_override_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/export/test_csv_exporter.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/export/test_excel_exporter.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/export/test_export_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/export/test_metadata_resolver.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_compilation_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_lifecycle_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_report_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution_resumability.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_interfaces.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_report_headers_l10n_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_repositories_v2.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_v2_core_models.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_execution_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_variance_synthesis.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py]`
- `[MODIFY] @[client_app_v2/test/core/api/sse_client_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/execution/models/execution_models_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/execution/views/execution_view_test.dart]`

## Phase 4 Deprecations & Sunset Symbols

<demolish>
- `_offload_payloads`
- `_hydrate_payloads`
- `_offload_record_blobs`
- `_hydrate_record_blobs`
- `_save_blob_payload`
- `_updates_exceed_blob_threshold`
- `_BLOB_OFFLOAD_THRESHOLD_BYTES`
- `frozen_context_storage_path`
- `execution_trace_storage_path`
- `context_variables_storage_path`
- `pdf_report_path`
- `active_profile_id`
- `step_states`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, `@[backend_v2/database/repositories/execution.py#L82-L118]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L760-L2425]` & `@[scripts/audit_zero_orm_strictness.py#L439-L459]` | Local disk JSON offload (`_offload_record_blobs`, `_hydrate_record_blobs`, `_save_blob_payload`, `_updates_exceed_blob_threshold`, `_BLOB_OFFLOAD_THRESHOLD_BYTES`, `*_storage_path`), silent `[]` coalescing on corrupt trace files, missing-`state_version` defaults (`actual_version = 1`), silent `False` return on missing `update_execution`, post-Phase 3 `DO $$` cutover no-op on `executions`, and two-step `SELECT`-before-`UPSERT` TOCTOU OCC in `save_execution_row` / `update_execution_occ_row`. | Extend `001_pg19_uuidv7_schema.sql` `DO $$` guard (`executions.step_states` / missing `execution_payloads`) and `seed_and_collection_stage.py` `TRUNCATE TABLE`, retaining `ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version`, `idx_executions_output_profile_id`, and UUIDv7 `CHECK` constraints (`ZORM004`/`ZORM007`); split into lean 30-column `executions` + transactional 1:1 `execution_payloads` (`COMPRESSION lz4` for `raw_inputs`, `frozen_context` retaining `mcp_tool_audit`, `context_variables`, `execution_trace`, and `profile_syntheses`); implement two-branch `save_execution_row` (`INSERT ... ON CONFLICT` when `expected_state_version is None` vs. single-statement `UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1::uuid AND state_version = $2 RETURNING state_version` + post-miss `404` vs `409` probe when `expected_state_version is not None`), unified with `update_execution_occ_row` and `InMemoryEntityAdapter.save_execution`; enforce non-null `organization_id` at persistence boundary (defaulting `ExecutionRecordFactory.organization_id`); split `hydrate_execution_row` (`INNER JOIN execution_payloads`) from `hydrate_execution_summary_row` (`frozen_context=None`) while hydrating matched records in `get_recent_completed_executions`; and bootstrap `InMemoryAsyncPgPool` + `CLOSED_POSTGRES_TABLES` (`execution_payloads`). | Do NOT shatter `ScorecardAtomDTO` or `TraceEvent` arrays into millions of EAV rows, and do NOT mutate domain `ExecutionRecord.organization_id: str | None = None`; store cold JSONB in 1:1 `lz4` TOAST `execution_payloads` alongside normalized `quorum_nodes` and `quorum_edges`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/database/ --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L252-L545]`, `@[backend_v2/models/execution_core.py#L70-L123]`, `@[backend_v2/models/state.py]`, `@[backend_v2/models/dtos/trace.py#L47-L86]`, `@[backend_v2/models/dtos/node_execution.py]`, `@[backend_v2/hooks/archival.py]`, `@[backend_v2/services/execution/ingress_service.py]`, `@[backend_v2/services/execution/override_service.py#L35-L482]`, `@[backend_v2/services/orchestrator/synthesis_distiller.py]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]`, `@[backend_v2/services/report/compilation_service.py#L33-L299]`, `@[backend_v2/services/blueprint.py#L89-L1076]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]` & CLI scripts | Duplicate `ExecutionRecord.step_states` map, `active_profile_id`, synthetic `"sys_render_{profile_id}"` keys in `ReportCompilationService` and `with_updated_profile_synthesis`, `pdf_report_path` shadow cache, `*_storage_path` attributes, legacy `get_storage_driver()` disk trace fallbacks in `hooks/archival.py` and `workers/synthesis_reducers.py`, unhydrated summary reads in `SynthesisDistiller._fetch_historical_summary`, and missing `organization_id` binding in `ExecutionIngressService`. | Drop `step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` across `ExecutionRecord`, `ExecutionCoreFields`, `state.py`, `ExecutionCreateDTO`, `ExecutionUpdateDTO`, `NodeExecutionUpdateDTO`, `InMemoryUnifiedWorkflowRepository`, services, DAG Orchestrator stages, workers, CLI scripts, and 50 unit/integration test suites with zero `@computed_field` shims; bind `effective_org_id` (`initiator.organization_id` or `SystemOrganizations.ROOT_SYSTEM.value`) in `ExecutionIngressService`; hydrate passed historical candidates via `deps.exec_repo.get_execution` in `SynthesisDistiller._fetch_historical_summary`; delete `get_storage_driver()` disk trace fallbacks in `archival.py` and `synthesis_reducers.py`; and read/mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) and `output_profile_id` exclusively while retaining `ExecutionRecord.profile_syntheses`. | Preserve `profile_syntheses` and its immutable transition helpers (`with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) and `ExecutionStepState = ExecutionStep` alias (`feature_sovereignty_mandate`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/hooks/archival.py backend_v2/services/ backend_v2/workers/ scripts/reconcile_storage.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/ backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict` |
| `@[backend_v2/tests/fakes/in_memory_uow.py#L3753-L3827]`, `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`, `@[scripts/audit_zero_orm_strictness.py#L439-L459]` & `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` | Permissive `InMemoryUnitOfWork` ignoring FK/UNIQUE/OCC violations, incomplete `_StoreSnapshot` rollback omitting `seed_tables` and `execution_payloads`, `DELETE FROM EXECUTIONS` omitting child cascades, and outdated 16-table `audit_zero_orm_strictness.py` constants / `APPROVED_ADAPTER_RECORD_COLUMNS`. | Upgrade `InMemoryUnitOfWork`, `_InMemoryPostgresStore` (`_StoreSnapshot` / `restore_snapshot` deep-copying `seed_tables` and `execution_payloads`), and `InMemoryEntityAdapter` to enforce `ON DELETE RESTRICT` (`DELETE_BLOCKED_BY_USAGE` 400), `ON DELETE NO ACTION DEFERRABLE` (`workflows.default_profile_id` commit-time check + rollback), `ON DELETE CASCADE` (including `DELETE FROM EXECUTIONS` child tables, `organization_id`, and `tenant_secrets.mcp_gateway_id`), `UNIQUE` (`CONFLICT` 409), populated-parent child `INSERT` validation, and `state_version`/`version` OCC across all 22 tables; finalize `CLOSED_POSTGRES_TABLES` (22 tables), `CANONICAL_ENTITY_PK_TABLES` (16 UUIDv7-PK tables), `APPROVED_ADAPTER_RECORD_COLUMNS` (`ZORM006` dropping the 6 demolished columns), and `ZORM008` in `audit_zero_orm_strictness.py`. | Exclude composite/sidecar tables (`step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`) from `CANONICAL_ENTITY_PK_TABLES` (`ZORM004`), and gate child `INSERT` parent checks on `if parent_table_non_empty` so isolated single-table unit tests remain hermetic. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py backend_v2/tests/fakes/ backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict` |
| `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`, `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]` & 5 Flutter test suites | Stale `stepStates`, `activeProfileId`, `pdfReportPath`, and `*_StoragePath` fields on Flutter `ExecutionRecord`, view bindings, and SSE/execution test fixtures. | Drop `stepStates`, `activeProfileId`, `pdfReportPath`, and `*_StoragePath` from `ExecutionRecord` and `ExecutionStep`, bind `record.outputProfileId` in `execution_view.dart`, `dashboard_view.dart`, and `result_dashboard.dart`, retain `profileSyntheses` (`ProfileSynthesisEntryDto`) under `disallowUnrecognizedKeys: true`, regenerate `.freezed.dart` / `.g.dart` siblings, and update `execution_record_test.dart`, `execution_step_test.dart`, `sse_client_test.dart`, `execution_models_test.dart`, and `execution_view_test.dart`. | Maintain 1:1 Backend-PDF-Flutter semantic and DTO parity. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch` |
| `@[scripts/audit_technical_debt.py#L253-L579]`, `@[scripts/_ast_guardrails.py#L110-L129]`, `@[scripts/audit_dict_eradication.py#L874-L964]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]` & `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` | `BOUNDARY_EXEMPTION_FILES` entry for `seed_and_collection_stage.py`, stale `test_postgres.py` `_QGR031` exemption, unguarded swallow-return/hydration/driver debt patterns, and stale 15/16-table or 8-collection rule/KI docs. | Add `TD_EXCEPT_SWALLOW_RETURN` (skipping `_is_test_file` and `_is_boundary_exempt`), `TD_LEGACY_STORAGE_DRIVER` (excluding stdlib `logging.Filter`), and `TD_UNWRAPPED_HYDRATION` to `audit_technical_debt.py`; remove `seed_and_collection_stage.py` from `BOUNDARY_EXEMPTION_FILES` (`12 -> 11` in `test_ast_guardrails.py` and `test_audit_dict_eradication.py`), drop `test_postgres.py` from `_check_qgr031_filter_call`, lock `storage_driver.py` and `driver.py` into `QGR017` retired monoliths, and keep `QGR030` retired `^sys_[0-9a-fA-F]{32}$` active; synchronize `.agents/rules/`, create `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` registered in `DEFAULT_CANONICAL_KI_ARTIFACTS`, and verify pairwise orthogonality via `audit_skills_architecture.py`. | Consolidate static checks directly inside existing `audit_technical_debt.py`, `_ast_guardrails.py`, `audit_dict_eradication.py`, and `audit_zero_orm_strictness.py` visitors without new standalone linter scripts. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[backend_v2/models/domain/execution.py#L252-L545]`, `@[backend_v2/models/domain/report_artifact.py#L22-L79]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, `@[backend_v2/database/repositories/execution.py#L41-L420]`, `@[backend_v2/database/postgres/pool.py#L422-L652]`, `@[backend_v2/database/postgres/uow.py#L185-L435]`, and `@[scripts/audit_database_atoms.py#L329-L787]`.</action>
    <action>Look forward: Confirm explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` is active before executing Step 4.2 (`orchestrator_god_object_fragility`). Verify Step 4.1 implements the 30-column `executions` + `execution_payloads` (`COMPRESSION lz4`) split, two-branch `save_execution_row` (`INSERT` vs. single-statement `state_version` SQL OCC), summary vs. primary-key hydration, and `InMemoryAsyncPgPool` / `CLOSED_POSTGRES_TABLES` bootstrap; Step 4.2 eradicates `step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` across all backend callers and unit tests while binding `ExecutionIngressService` `organization_id`, hydrating `SynthesisDistiller` historical records, deleting `get_storage_driver()` disk trace fallbacks, and preserving `profile_syntheses`; Step 4.3 completes 22-table `InMemoryUnitOfWork` constraint enforcement and `audit_zero_orm_strictness.py` (`ZORM004`–`ZORM008`); Step 4.4 synchronizes Flutter Execution Freezed models, views, and 5 Dart test suites; and Step 4.5 locks static AST/technical-debt guardrails, rules, and Knowledge Items.</action>
    <constraint invariant="feature_sovereignty_mandate">NEVER remove `ExecutionRecord.profile_syntheses` (`dict[str, RenderedSynthesisCache]`), `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`, `frozen_context.mcp_tool_audit`, or Flutter `ProfileSynthesisEntryDto`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/04_phase4_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L252-L545]</backend>
    <backend>@[backend_v2/models/execution_core.py#L70-L123]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py#L66-L86]</backend>
    <backend>@[backend_v2/models/dtos/node_execution.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/database/repositories/execution.py#L41-L420]</backend>
    <backend>@[backend_v2/hooks/archival.py]</backend>
    <backend>@[backend_v2/services/blueprint.py#L89-L1076]</backend>
    <backend>@[backend_v2/services/execution/assignment_service.py#L150-L1929]</backend>
    <backend>@[backend_v2/services/execution/context_service.py]</backend>
    <backend>@[backend_v2/services/execution/ingress_service.py]</backend>
    <backend>@[backend_v2/services/execution/override_service.py#L35-L482]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py#L25-L324]</backend>
    <backend>@[backend_v2/services/execution/resumption_service.py#L30-L242]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]</backend>
    <backend>@[backend_v2/services/report/compilation_service.py#L33-L299]</backend>
    <backend>@[backend_v2/services/report/lifecycle_service.py#L36-L464]</backend>
    <backend>@[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]</backend>
    <backend>@[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]</backend>
    <backend>@[backend_v2/workers/execution_worker.py#_mark_execution_failed]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]</backend>
    <backend>@[scripts/reconcile_storage.py#L59-L71]</backend>
    <backend>@[scripts/diff_executions.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py#L439-L459]</backend>
    <backend>@[scripts/audit_technical_debt.py#L253-L579]</backend>
    <backend>@[scripts/_ast_guardrails.py#L110-L129]</backend>
    <backend>@[scripts/audit_dict_eradication.py#L169-L628]</backend>
    <backend>@[scripts/audit_skills_architecture.py#L160-L175]</backend>
    <backend>@[.agents/rules/01-python-backend.md]</backend>
    <backend>@[.agents/rules/03_seed_vault.md]</backend>
    <backend>@[.agents/rules/04_directory_reference.md]</backend>
    <backend>@[.agents/skills/tier2-hardening-backend/SKILL.md]</backend>
    <backend>[NEW] @[ki_zero_orm_postgres_enforcement.md]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L1996-L2007]</backend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/execution_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/dashboard_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/shared/widgets/result_dashboard.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test___init__.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_postgres.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_repository.py]</backend>
    <backend>@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_archival.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_scoring.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_node_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_trace.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_execution_core.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_state.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_reconcile_storage.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_context_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_ingress_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_override_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/export/test_csv_exporter.py]</backend>
    <backend>@[backend_v2/tests/unit/services/export/test_excel_exporter.py]</backend>
    <backend>@[backend_v2/tests/unit/services/export/test_export_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/export/test_metadata_resolver.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_compilation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_lifecycle_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_report_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution_resumability.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_taskgroup.py]</backend>
    <backend>@[backend_v2/tests/unit/test_interfaces.py]</backend>
    <backend>@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/test_repositories_v2.py]</backend>
    <backend>@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]</backend>
    <backend>@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/test_v2_core_models.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_execution_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_variance_synthesis.py]</backend>
    <backend>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</backend>
    <frontend>@[client_app_v2/test/core/api/sse_client_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/execution/models/execution_models_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/execution/views/execution_view_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`executions` (30 hot columns, `idx_executions_output_profile_id`, UUIDv7 FK `CHECK` constraints, and `ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version`) and `execution_payloads` (1:1 `COMPRESSION lz4` sidecar storing `raw_inputs`, `frozen_context`, `context_variables`, `execution_trace`, and `profile_syntheses`) are live in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, and `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, `_offload_record_blobs`/`_hydrate_record_blobs`/`_save_blob_payload`/`_updates_exceed_blob_threshold` are deleted, and `save_execution_row` + `update_execution_occ_row` enforce two-branch `INSERT` (`expected_state_version is None`) vs. single-statement SQL OCC (`WHERE id = $1::uuid AND state_version = $2 RETURNING state_version`).</item>
    <item>`ExecutionRecord.step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` are eradicated full-duplex across Python models (`ExecutionRecord`, `ExecutionCoreFields`), DTOs, hooks (`archival.py`), services (`ExecutionIngressService` `organization_id` binding, `SynthesisDistiller._fetch_historical_summary` primary-key hydration), DAG Orchestrator stages, workers, CLI scripts, and Flutter (`execution_record.dart`, `execution_step.dart`, `execution_view.dart`, `dashboard_view.dart`, `result_dashboard.dart`, and 5 Dart test suites) with zero `@computed_field` transition shims while retaining Stage 2 `profile_syntheses`.</item>
    <item>`@[backend_v2/tests/fakes/in_memory_uow.py#L139-L172]` enforces all 22-table FK `ON DELETE RESTRICT` / `NO ACTION DEFERRABLE` (with `_StoreSnapshot` rollback of `seed_tables` and `execution_payloads`) / `CASCADE` (including `DELETE FROM EXECUTIONS`), `UNIQUE`, and `state_version`/`version` OCC constraints, and `@[scripts/audit_zero_orm_strictness.py#L439-L459]` enforces the closed 22-table topology, 16-table `CANONICAL_ENTITY_PK_TABLES`, `ZORM006` column parity, and `ZORM008`.</item>
    <item>`@[scripts/audit_technical_debt.py#L253-L579]` enforces `TD_EXCEPT_SWALLOW_RETURN` (exempting `_is_test_file` and `_is_boundary_exempt`), `TD_LEGACY_STORAGE_DRIVER` (excluding `logging.Filter`), and `TD_UNWRAPPED_HYDRATION`; `@[scripts/_ast_guardrails.py#L110-L129]` and `@[scripts/audit_dict_eradication.py#L169-L628]` remove `seed_and_collection_stage.py` from `BOUNDARY_EXEMPTION_FILES` and `test_postgres.py` from `_check_qgr031_filter_call` while locking `storage_driver.py` and `driver.py` into `QGR017`; and `.agents/rules/` plus `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` pass `scripts/audit_skills_architecture.py`.</item>
  </dod_checklist>

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

  <anti_targets>
    <anti_target>Do NOT add any `@computed_field` or `@property def step_states` transition shim on `ExecutionRecord` (`zero_backward_compatibility_planning_ban`).</anti_target>
    <anti_target>Do NOT mutate `ExecutionRecord.organization_id: str | None = None` on the Python or Flutter domain model (`ban_drive_by_schema_mutations`); enforce non-null `organization_id` at `ExecutionIngressService` and the `save_execution_row` / `InMemoryEntityAdapter.save_execution` persistence boundary.</anti_target>
    <anti_target>Do NOT include composite/sidecar tables (`step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`) in `CANONICAL_ENTITY_PK_TABLES` in `scripts/audit_zero_orm_strictness.py`.</anti_target>
    <anti_target>Do NOT match legitimate `sys_rag_*` step keys, `_sys_initiator_id` metadata keys, stdlib `logging.Filter`, or `_is_boundary_exempt` startup telemetry probes (`backend_v2/core/telemetry.py`) when enforcing `QGR030`, `TD_LEGACY_STORAGE_DRIVER`, and `TD_EXCEPT_SWALLOW_RETURN`.</anti_target>
  </anti_targets>

  <step id="4.1" name="executions + execution_payloads (COMPRESSION lz4) 1:1 Sidecar Split &amp; Atomic Single-Statement state_version SQL OCC">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L333-L452]`, and `@[backend_v2/database/repositories/execution.py#L82-L118]`: Extend the `DO $$` cutover guard in `001_pg19_uuidv7_schema.sql` to check `executions.step_states` existence or missing `execution_payloads` table, include `execution_payloads` in both `DROP TABLE IF EXISTS ... CASCADE` and `seed_and_collection_stage.py` (`TRUNCATE TABLE ... RESTART IDENTITY CASCADE`), split `executions` into the lean 30-column `executions` table (`models_used DEFAULT '{}'::jsonb`, `duration_ms BIGINT NOT NULL DEFAULT 0`, `VIRTUAL` `created_at`, UUIDv7 FK `CHECK` constraints, `ALTER TABLE executions ADD COLUMN IF NOT EXISTS state_version INTEGER NOT NULL DEFAULT 1;`, and `idx_executions_output_profile_id`) and the 1:1 `execution_payloads` sidecar table (`execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE`, `raw_inputs JSONB COMPRESSION lz4 NOT NULL`, `frozen_context JSONB COMPRESSION lz4` retaining `mcp_tool_audit`, `context_variables JSONB COMPRESSION lz4 NOT NULL`, `execution_trace JSONB COMPRESSION lz4 NOT NULL`, `profile_syntheses JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb`, and `enforce_execution_payload_uuidv7`). Delete `_offload_record_blobs`, `_hydrate_record_blobs`, `_save_blob_payload`, `_updates_exceed_blob_threshold`, and `_BLOB_OFFLOAD_THRESHOLD_BYTES` from `ExecutionRepositoryImpl`. Implement two-branch `save_execution_row` (enforcing non-null `parse_prefixed_uuid7(record.organization_id, EntityPrefix.ORGANIZATION)`): when `expected_state_version is None` (`create_execution`, initial `append_trace_event`, `seed_collection_batch_rows`), execute `INSERT INTO executions (...) VALUES (...) ON CONFLICT (id) DO UPDATE SET ...` + `INSERT INTO execution_payloads (...) VALUES (...) ON CONFLICT (execution_id) DO UPDATE SET ...` in one transaction; when `expected_state_version is not None`, execute single-statement `UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1::uuid AND state_version = $2 RETURNING state_version` paired with `execution_payloads` upsert in the same transaction, probing `SELECT state_version FROM executions WHERE id = $1::uuid` on miss to distinguish missing `id` (`ResourceNotFoundError` 404) from stale `state_version` (`AppException(ErrorCodes.CONFLICT, status_code=409)`), and unify `update_execution_occ_row` and `ExecutionRepositoryImpl.update_execution` onto the same contract. Split hydration into `hydrate_execution_row` (`get_execution_row` with `INNER JOIN execution_payloads ep ON ep.execution_id = e.id`) and `hydrate_execution_summary_row` (`list_execution_rows` and `list_executions_filtered_rows` omitting cold sidecar joins and explicitly passing `raw_inputs={"dynamic_inputs": {}}`, `frozen_context=None`, `context_variables={}`, `execution_trace=[]`, `profile_syntheses={}`), and hydrate matched records via `get_execution` in `ExecutionRepositoryImpl.get_recent_completed_executions`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_uow.py#L3690-L3750]`, `@[scripts/audit_zero_orm_strictness.py#L439-L459]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, `@[backend_v2/tests/unit/database/repositories/test_execution.py]`, `@[backend_v2/tests/unit/database/test___init__.py]`, `@[backend_v2/tests/unit/database/test_postgres.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, `@[backend_v2/tests/unit/test_interfaces.py]`, and `@[backend_v2/tests/unit/test_repositories_v2.py]`: Synchronously update `InMemoryAsyncPgPool`, `_InMemoryPostgresStore`, and `InMemoryEntityAdapter` (`save_execution`, `get_execution`, `list_executions`, `list_executions_filtered`) for the 30-column `executions` + 7-column `execution_payloads` split, single-statement `UPDATE executions ... RETURNING state_version` OCC, `404` vs `409` miss semantics, non-null `organization_id` validation, and `hydrate_execution_summary_row` (`frozen_context=None`); add `"execution_payloads"` to `CLOSED_POSTGRES_TABLES` in `audit_zero_orm_strictness.py`; default `ExecutionRecordFactory.organization_id` to `Use(generate_opaque_id, EntityPrefix.ORGANIZATION)` in `model_factories.py`; and update all database/repository unit tests with canonical `org_<hex32>` fixtures and sidecar roundtrip/OCC assertions.</action>
    <constraint invariant="uow_transactional_concurrency_mandate">Hot `executions` row updates and cold `execution_payloads` upserts MUST commit or roll back atomically inside a single PostgreSQL 19 transaction under `WHERE id = $1::uuid AND state_version = $2` OCC.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/database/ backend_v2/tests/unit/test_interfaces.py backend_v2/tests/unit/test_repositories_v2.py --test --ast-strict</audit_command>
  </step>

  <step id="4.2" name="Full-Duplex Backend Eradication of ExecutionRecord.step_states, active_profile_id, pdf_report_path &amp; *_storage_path (Preserving profile_syntheses)">
    <action>1. `[MODIFY]` `@[backend_v2/models/domain/execution.py#L252-L545]`, `@[backend_v2/models/execution_core.py#L70-L123]`, `@[backend_v2/models/state.py]`, `@[backend_v2/models/dtos/trace.py#L47-L86]`, `@[backend_v2/models/dtos/node_execution.py]`, `@[backend_v2/tests/factories/model_factories.py]`, and `@[backend_v2/tests/fakes/in_memory_repositories.py]`: Drop `step_states`, `active_profile_id`, `pdf_report_path`, `frozen_context_storage_path`, `execution_trace_storage_path`, and `context_variables_storage_path` from `ExecutionRecord`, `ExecutionCoreFields`, `state.py`, `ExecutionCreateDTO`, `ExecutionUpdateDTO`, `NodeExecutionUpdateDTO`, `ExecutionRecordFactory`, and `InMemoryUnifiedWorkflowRepository` with zero `@computed_field` transition shims, while retaining `ExecutionStepState = ExecutionStep`, `ExecutionRecord.profile_syntheses: dict[str, RenderedSynthesisCache]`, `with_updated_profile_synthesis` (dropping optional `step_id`/`step_state` `sys_render_` arguments), and `with_cleared_profile_syntheses`, and updating `with_updated_step_state` and `transition_step` to mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) immutably.</action>
    <action>2. `[MODIFY]` `@[backend_v2/hooks/archival.py]`, `@[backend_v2/services/blueprint.py#L89-L1076]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1929]`, `@[backend_v2/services/execution/context_service.py]`, `@[backend_v2/services/execution/ingress_service.py]`, `@[backend_v2/services/execution/override_service.py#L35-L482]`, `@[backend_v2/services/execution/lifecycle_service.py#L25-L324]`, `@[backend_v2/services/execution/resumption_service.py#L30-L242]`, `@[backend_v2/services/orchestrator/synthesis_distiller.py]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]`, `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, `@[backend_v2/services/report/compilation_service.py#L33-L299]`, `@[backend_v2/services/report/lifecycle_service.py#L36-L464]`, `@[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]`, `@[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]`, `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`, `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`, `@[scripts/reconcile_storage.py#L59-L71]`, `@[scripts/diff_executions.py]`, and `@[scripts/run_e2e_variance_test.py]`: Bind `effective_org_id` (`initiator.organization_id` when present, else `SystemOrganizations.ROOT_SYSTEM.value`) onto `create_execution_record` in `ExecutionIngressService`; hydrate passed historical candidates via `await deps.exec_repo.get_execution(e.id)` in `SynthesisDistiller._fetch_historical_summary` before reading `e.profile_syntheses`; delete legacy `get_storage_driver()` local disk `executions/{id}/execution_trace.json` fallback blocks in `hooks/archival.py` (`retrieve_precedent_hook`) and `workers/synthesis_reducers.py` (`recover_trace_telemetry`); and update all execution, DAG Orchestrator, blueprint, SDUI, export, report compilation (dropping synthetic `"sys_render_{profile_id}"` keys), worker, and CLI callers to read and mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) and `output_profile_id` exclusively.</action>
    <action>3. `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_archival.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/models/domain/test_execution.py]`, `@[backend_v2/tests/unit/models/dtos/test_node_execution.py]`, `@[backend_v2/tests/unit/models/dtos/test_trace.py]`, `@[backend_v2/tests/unit/models/test_execution_core.py]`, `@[backend_v2/tests/unit/models/test_state.py]`, `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`, `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`, `@[backend_v2/tests/unit/services/execution/test_context_service.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/export/test_csv_exporter.py]`, `@[backend_v2/tests/unit/services/export/test_excel_exporter.py]`, `@[backend_v2/tests/unit/services/export/test_export_facade.py]`, `@[backend_v2/tests/unit/services/export/test_metadata_resolver.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_concurrency_stress.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_matrix_reducer.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`, `@[backend_v2/tests/unit/services/report/test_compilation_service.py]`, `@[backend_v2/tests/unit/services/report/test_lifecycle_service.py]`, `@[backend_v2/tests/unit/services/report/test_report_facade.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/test_v2_core_models.py]`, `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]`, and `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`: Migrate all unit and integration test suites off `step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` onto `ExecutionRecord.steps` and `output_profile_id`, replace raw dictionary `.model_validate({...})` fixtures (`TD_MODEL_FACTORY`) with `ModelFactory.build(...)` builders from `model_factories.py` (retaining raw dicts strictly in negative schema-rejection tests), and add ISTQB negative `test_*_invalid` / `test_*_failure` partitions (`TD_ISTQB_NEGATIVE`) plus `SynthesisDistiller` and `retrieve_precedent_hook` hydration assertions.</action>
    <constraint invariant="ban_heuristic_identifier_matching">Zero synthetic `"sys_render_{profile_id}"` step keys may be injected into `ExecutionRecord.steps`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/hooks/archival.py backend_v2/services/ backend_v2/workers/ scripts/reconcile_storage.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/ backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict</audit_command>
  </step>

  <step id="4.3" name="Constraint-Enforcing InMemoryUnitOfWork &amp; 22-Table audit_zero_orm_strictness.py (ZORM004-ZORM008)">
    <action>1. `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_uow.py#L3753-L3827]` and `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`: Upgrade `InMemoryUnitOfWork`, `_InMemoryPostgresStore`, and `InMemoryEntityAdapter` to enforce `ON DELETE RESTRICT` (`ErrorCodes.DELETE_BLOCKED_BY_USAGE` 400), `ON DELETE NO ACTION DEFERRABLE` (`workflows.default_profile_id` evaluated at transaction commit, with `_StoreSnapshot` / `restore_snapshot` deep-copying and restoring `seed_tables` and `execution_payloads` on rollback), `ON DELETE CASCADE` (including `organization_id` across all tenant-scoped tables, `DELETE FROM EXECUTIONS` cascading to `execution_payloads`, `quorum_nodes`, `quorum_edges`, `report_artifacts`, `report_binaries`, and `usage_records`, and `tenant_secrets.mcp_gateway_id`), `UNIQUE` constraints (`ErrorCodes.CONFLICT` 409), populated-parent child `INSERT` validation (`if parent_table_non_empty`), and `state_version` / `version` OCC across all 22 tables.</action>
    <action>2. `[MODIFY]` `@[scripts/audit_zero_orm_strictness.py#L439-L459]` and `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`: Update `CLOSED_POSTGRES_TABLES` to the exact 22 tables (`organizations`, `users`, `invitations`, `tenant_secrets`, `model_registries`, `mcp_gateways`, `prompt_blocks`, `task_briefs`, `steps`, `step_criteria_blocks`, `workflows`, `workflow_step_refs`, `output_profiles`, `executions`, `execution_payloads`, `execution_assignments`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`, `audit_logs`, `usage_records`), update `CANONICAL_ENTITY_PK_TABLES` strictly to the 16 UUIDv7-PK tables (adding `model_registries`, `mcp_gateways`, `audit_logs`, `usage_records` and dropping `system_configs`, excluding `step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`), synchronize `CANONICAL_NAMED_ENTITY_TABLES`, remove the 6 demolished columns (`active_profile_id`, `frozen_context_storage_path`, `pdf_report_path`, `step_states`, `execution_trace_storage_path`, `context_variables_storage_path`) from `APPROVED_ADAPTER_RECORD_COLUMNS` (`ZORM006`), retain `REQUIRED_IDEMPOTENT_ALTER_COLUMNS` (`ZORM007`), and add `ZORM008` banning `StorageDriver` imports, unwrapped `.model_validate(` calls in `entity_adapter/` stage modules, and unparameterized `SELECT *` list scans.</action>
    <constraint invariant="hermetic_test_fixtures_mandate">Every FK `RESTRICT`/`DEFERRABLE`/`CASCADE`, `UNIQUE`, and OCC invariant enforced by PostgreSQL 19 MUST behave identically in `InMemoryUnitOfWork` unit tests.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict</audit_command>
  </step>

  <step id="4.4" name="Flutter ExecutionRecord, ExecutionStep &amp; Dashboard View Full-Duplex Parity">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`, `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`, `@[client_app_v2/test/core/api/sse_client_test.dart]`, `@[client_app_v2/test/features/execution/models/execution_models_test.dart]`, `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`, `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`, and `@[client_app_v2/test/unit/features/execution/views/execution_view_test.dart]`: Drop `stepStates`, `activeProfileId`, `pdfReportPath`, `frozenContextStoragePath`, `executionTraceStoragePath`, and `contextVariablesStoragePath` from `ExecutionRecord` and `ExecutionStep`, replace `record.activeProfileId` with `record.outputProfileId` in `execution_view.dart`, `dashboard_view.dart`, and `result_dashboard.dart`, preserve `profileSyntheses` (`ProfileSynthesisEntryDto`) and `@JsonSerializable(disallowUnrecognizedKeys: true)`, regenerate `.freezed.dart` / `.g.dart` siblings, and update all 5 Dart test suites (`sse_client_test.dart`, `execution_models_test.dart`, `execution_record_test.dart`, `execution_step_test.dart`, `execution_view_test.dart`) to assert strict rejection of removed keys.</action>
    <constraint invariant="full_duplex_serialization_parity_mandate">`ExecutionRecord` wire JSON keys MUST match 1:1 between Python Pydantic and Flutter Freezed under `uv run python scripts/audit_dto_parity.py --fail-on-mismatch`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</audit_command>
  </step>

  <step id="4.5" name="Single-Pipeline Governance Lock Across audit_technical_debt.py, _ast_guardrails.py, audit_dict_eradication.py, Rules &amp; Knowledge Items">
    <action>1. `[MODIFY]` `@[scripts/audit_technical_debt.py#L253-L579]`, `@[scripts/_ast_guardrails.py#L110-L129]`, `@[scripts/audit_dict_eradication.py#L169-L628]`, `@[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`, and `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`: Add `TD_EXCEPT_SWALLOW_RETURN` (flagging `except (Exception, AppException, ValidationError)` blocks returning `None`, `False`, `[]`, or `{}` without `logger.error` and `raise AppException`, while skipping `self._is_test_file` and `self._is_boundary_exempt` so `backend_v2/core/telemetry.py` passes `--include-one-hop`), `TD_LEGACY_STORAGE_DRIVER` (flagging imports/references to `StorageDriver`, `PostgresStorageDriver`, `QueryCondition`, `AppendOnlyRepositoryBase`, `KnowledgeRepositoryImpl`, `ComponentRepositoryImpl`, `AgentRepositoryImpl`, `RoleRepositoryImpl`, `TaskBlueprintRepositoryImpl`, and `backend_v2.database` `Filter` while excluding stdlib `logging.Filter`), and `TD_UNWRAPPED_HYDRATION` (flagging direct `.model_validate(` or `.validate_python(` calls inside `backend_v2/database/postgres/` outside `validate_hydrated_row`) in `audit_technical_debt.py`. Drop `"backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py"` from `BOUNDARY_EXEMPTION_FILES` (`12 -> 11` entries in `test_ast_guardrails.py`, updating `test_audit_dict_eradication.py` fixture path to `entity_adapter/__init__.py`), add `"backend_v2/database/postgres/storage_driver.py"` and `"backend_v2/database/driver.py"` to `QGR017` retired monoliths, drop the obsolete `test_postgres.py` exemption in `_check_qgr031_filter_call`, and retain `_QGR030_ENTITY_PREFIXES` (`^sys_[0-9a-fA-F]{32}$` and `EntityPrefix.SYSTEM_CONFIG`).</action>
    <action>2. `[MODIFY]` `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`, and `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`: Update `01-python-backend.md` (`primary_key_lookup_o1_mandate`, `in_place_upsert_standard_mandate`, `crud_and_clone_lifecycle_standard_mandate`, `zero_orm_ddl_column_evolution_and_preflight_mandate`, `service_layer_hydration_firewall`), `03_seed_vault.md`, and `04_directory_reference.md` to codify the single `EntityPersistencePort` pipeline, 22-table PostgreSQL 19 topology, `validate_hydrated_row`, `translate_postgres_exception`, `ON DELETE RESTRICT`, `ROOT_SYSTEM` `organization_id NOT NULL ON DELETE CASCADE`, and 9-collection `seed_data.json`. Create `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` (and synchronize `ki_router_ssot_and_crud_clone_lifecycle.md`, `ki_global_config_sovereignty.md`, `ki_mcp_gateway_architecture.md`, and `ki_zero_permissive_typing.md` plus `metadata.json` in `<appDataDir>/knowledge/`), register `ki_zero_orm_postgres_enforcement.md` in `DEFAULT_CANONICAL_KI_ARTIFACTS` (`audit_skills_architecture.py`) and `tier2-hardening-backend/SKILL.md`, and execute pairwise rule and static checker orthogonality verification via `uv run python scripts/audit_skills_architecture.py`.</action>
    <constraint invariant="pairwise_rule_and_guardrail_orthogonality_mandate">Every added or modified `<rule_block>` and static AST checker MUST pass pairwise conflict and syntax probe verification via `scripts/audit_skills_architecture.py`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/audit_zero_orm_strictness.py scripts/audit_technical_debt.py scripts/_ast_guardrails.py scripts/audit_dict_eradication.py scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/ --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_execution_and_lz4_payloads_sidecar_roundtrip_preserves_profile_syntheses_and_mcp_audit" category="positive">
      <input>`ExecutionRecordFactory.build(...)` containing `steps`, `raw_inputs`, `frozen_context` (`mcp_tool_audit`), `context_variables`, `execution_trace`, and `profile_syntheses` (`RenderedSynthesisCache`) persisted (`expected_state_version=None`) and hydrated by primary key</input>
      <expected>Persists hot columns in `executions` and cold JSONB in `execution_payloads` (`COMPRESSION lz4`), roundtripping 100% of fields without local disk `*_storage_path` files while `list_executions_filtered` hydrates via `hydrate_execution_summary_row` (`frozen_context=None`) and `SynthesisDistiller` / `get_recent_completed_executions` hydrate full sidecars via `get_execution`</expected>
    </test>
    <test name="test_save_execution_row_concurrent_taskgroup_occ_race_raises_conflict_409" category="boundary">
      <input>Two concurrent `asyncio.TaskGroup` tasks updating the same `ExecutionRecord` from `state_version=1` (`expected_state_version=1`)</input>
      <expected>Exactly one task commits `state_version=2`; the competing task fails fast with `AppException(ErrorCodes.CONFLICT, status_code=409)` with zero lost updates</expected>
    </test>
    <test name="test_save_execution_row_missing_execution_id_raises_resource_not_found_404" category="negative">
      <input>OCC update attempted via `save_execution_row` and `update_execution_occ_row` on a non-existent `ExecutionRecord.id` expecting `state_version=2`</input>
      <expected>Raises `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)` instead of returning `False` or masking as `CONFLICT`</expected>
    </test>
    <test name="test_override_atom_mutates_canonical_steps_and_clears_profile_syntheses_atomically" category="positive">
      <input>`ExecutionOverrideService.override_atom` invoked on a completed `ExecutionRecord` with populated `steps` and `profile_syntheses`</input>
      <expected>Updates the target atom inside `ExecutionRecord.steps` (`list[ExecutionStep]`), clears stale `profile_syntheses`, and renders 1:1 matching scores across Backend SDUI, PDF, and Flutter (`test_sdui_semantic_parity.py`)</expected>
    </test>
    <test name="test_execution_record_python_and_flutter_reject_removed_step_states_and_storage_path_keys" category="negative">
      <input>`ExecutionRecord.model_validate` (Python) and `ExecutionRecord.fromJson` (Dart) called with `"step_states"`, `"active_profile_id"`, `"pdf_report_path"`, or `"execution_trace_storage_path"`</input>
      <expected>Crashes immediately under `ConfigDict(extra="forbid", strict=True)` and `@JsonSerializable(disallowUnrecognizedKeys: true)`</expected>
    </test>
    <test name="test_in_memory_uow_enforces_22_table_restrict_deferrable_cascade_unique_and_occ" category="negative">
      <input>`InMemoryUnitOfWork` delete of referenced `Workflow`/`PromptBlock`/`TaskBrief`, delete of `workflows.default_profile_id` at commit (verifying `_StoreSnapshot` rollback of `seed_tables` and `execution_payloads`), duplicate `token_hash` insert, `DELETE FROM EXECUTIONS` cascade, and stale `state_version` update</input>
      <expected>Raises `ErrorCodes.DELETE_BLOCKED_BY_USAGE` (400) on `RESTRICT` and deferred `NO ACTION` violations with full rollback, `ErrorCodes.CONFLICT` (409) on `UNIQUE` and stale `state_version`/`version` updates, and cascades `organization_id`, `execution_payloads`, and `mcp_gateway_id` deletes</expected>
    </test>
    <test name="test_zorm008_and_technical_debt_visitors_reject_storage_driver_swallow_and_unwrapped_hydration" category="negative">
      <input>Synthetic AST snippets importing `StorageDriver`, catching `except AppException: return None` in domain services while keeping `_is_boundary_exempt` `telemetry.py` and stdlib `logging.Filter` in `logging_config.py`, calling unwrapped `.model_validate(` in `entity_adapter/`, or embedding `sys_0195f3a00000700080008172bda70c86` while keeping `sys_rag_preflight`</input>
      <expected>`ZORM008`, `TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, `TD_UNWRAPPED_HYDRATION`, and `QGR030` flag all banned constructs while passing `telemetry.py`, `logging.Filter`, `sys_rag_preflight`, and `_sys_initiator_id` cleanly</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/audit_zero_orm_strictness.py scripts/audit_technical_debt.py scripts/_ast_guardrails.py scripts/audit_dict_eradication.py scripts/audit_skills_architecture.py scripts/reconcile_storage.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/ backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</command>
  </validation_gate>
</execution_protocol>
```
