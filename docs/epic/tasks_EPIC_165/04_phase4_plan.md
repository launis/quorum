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

**Overview:** Split `executions` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` and `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]` into the lean 30-column hot `executions` table and the transactional 1:1 cold `lz4`-compressed `execution_payloads` sidecar table (retaining `ExecutionRecord.profile_syntheses` and `frozen_context.mcp_tool_audit` while dropping `_offload_payloads` and `_hydrate_payloads` local filesystem offload), replace the two-step `SELECT state_version`-then-`UPSERT` TOCTOU check in `save_execution_row` with atomic single-statement SQL Optimistic Concurrency Control (`UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1 AND state_version = $2 RETURNING state_version`), eradicate `ExecutionRecord.step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` full-duplex across Python (`@[backend_v2/models/domain/execution.py#L249-L520]`, services, DAG Orchestrator stages, workers, CLI scripts) and Flutter (`@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`, `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `dashboard_view.dart`, `result_dashboard.dart`) with zero `@computed_field` shims, upgrade `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`) to enforce all 22-table FK/UNIQUE/OCC constraints in unit tests, and lock single-pipeline governance permanently across `@[scripts/audit_zero_orm_strictness.py#L407-L427]` (`ZORM004`–`ZORM008`), `@[scripts/audit_technical_debt.py#L253-L579]` (`TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, `TD_UNWRAPPED_HYDRATION`), `@[scripts/_ast_guardrails.py#L111-L130]`, `@[scripts/audit_dict_eradication.py#L169-L628]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `.agents/rules/`, and `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`.

**DAG Orchestrator Permission Gate (`orchestrator_god_object_fragility`):** Mutating `backend_v2/services/orchestrator/dag_executor/` (`execution_committer.py`, `workflow_bootstrap_stage.py`, `step_execution_stage.py`, `wave_orchestrator_stage.py`) and `backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py` to remove `step_states` and `active_profile_id` references requires explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` prior to `/tier2-execute`, followed by the full `backend_audit_loop.py` gate.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 4 Forensic Context, Retained SSOT Invariants & Sidecar SQL DDL (Verbatim from EPIC 165)

### Forensic Finding 4 [P1 HIGH]: `executions` Intra-Row Duplication, Non-Transactional File Offload & Non-Atomic OCC
* **Forensic Anchors:**
  * `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` (lines 249–330)
  * `@[backend_v2/models/domain/execution.py#L249-L520]` (`backend_v2/models/domain/execution.py#L221-L320`)
  * `@[backend_v2/services/execution/override_service.py#L36-L488]`
  * `@[backend_v2/services/report/compilation_service.py#L33-L301]`
  * `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`
* **Root Cause (5 Coupled Defects + Finding 7 Site 8 & Finding 8 Item 6):**
  1. **Intra-Row State Duplication (`steps` vs. `step_states`):** Every step's `scorecard_atoms` and token metrics are duplicated in both `steps` (`JSONB` list) and `step_states` (`JSONB` map). `ExecutionOverrideService.override_atom` mutates `step_states` without updating `steps`, causing immediate post-override split-brain, while `ReportCompilationService` injects synthetic `"sys_render_{profile_id}"` keys into `step_states` in violation of `ban_heuristic_identifier_matching`.
  2. **Duplicate Profile Foreign Keys (`active_profile_id` vs. `output_profile_id`):** Two overlapping nullable Foreign Keys to `output_profiles(id)` exist on the same `executions` row.
  3. **Shadow `pdf_report_path` Cache & Misplaced Hot-Row `profile_syntheses` Payload:** `pdf_report_path` duplicates binary report location owned authoritatively by `report_artifacts` + `report_binaries` (`universal_ssot_and_normalization_mandate`), whereas `profile_syntheses` (`dict[str, RenderedSynthesisCache]`, populated by Stage 2 `synthesis_worker.py` and consumed by `BlueprintTransformer`, `DistributionFormatter`, `SynthesisDistiller`, `ExecutionOverrideService.clear_profile_synthesis`, `ReportCompilationService`, and Flutter `ProfileSynthesisEntryDto`) has no column in `report_artifacts` (`@[backend_v2/models/domain/report_artifact.py#L22-L79]`) and bloats the hot `executions` tuple instead of residing in the 1:1 cold `lz4` `execution_payloads` sidecar (`feature_sovereignty_mandate`).
  4. **Non-Transactional Filesystem Offload (`*_storage_path`) & Silent Empty-Blob Coalescing (Finding 7 Site 8):** Offloading `>100KB` `frozen_context`, `execution_trace`, and `context_variables` blobs to `data/files/executions/{id}/*.json` splits one logical record across PostgreSQL and local disk without ACID rollback guarantees, while `_hydrate_payloads` in `@[backend_v2/database/repositories/execution.py#L30-L481]` silently replaces an empty/corrupt offloaded `execution_trace` file with `[]` and `update_execution` defaults missing `state_version` to `1` and returns `False` on missing `existing_doc`.
  5. **TOCTOU Race in Optimistic Concurrency Control (`save_execution_row`) & Permissive `InMemoryUnitOfWork` (Finding 8 Item 6):** `save_execution_row` executes a separate `SELECT state_version` before `INSERT ... ON CONFLICT (id) DO UPDATE`, allowing two concurrent writers reading the same `state_version` to clobber each other, while `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`) lacks 22-table FK `ON DELETE RESTRICT` / `CASCADE`, `UNIQUE`, and `state_version`/`version` OCC enforcement.

### Retained SSOT Invariants & Producer-Consumer Contracts (Sections 1.5, 2.3 & 2.5)
* **Retained Stage 2 `ExecutionRecord.profile_syntheses` (`dict[str, RenderedSynthesisCache]` & Flutter `ProfileSynthesisEntryDto`):** Preserved on `ExecutionRecord` (`feature_sovereignty_mandate`) alongside `with_updated_profile_synthesis` and `with_cleared_profile_syntheses`, relocated off the hot `executions` tuple into `execution_payloads.profile_syntheses` (`JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb`).
* **Retained Native `asyncpg` Binary `0x01` JSONB Codec & `QuorumUnitOfWork` Transaction Boundary:** Retained in `@[backend_v2/database/postgres/pool.py#L422-L652]` and `@[backend_v2/database/postgres/uow.py#L185-L435]`, and audited alongside `@[scripts/audit_database_atoms.py#L328-L786]` across the closed 22-table topology.
* **Producer 3 (`PostgresEntityAdapter.save_execution_row` in `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`, DAG Orchestrator, `ExecutionOverrideService`, & `synthesis_worker.py`):** Persists hot lifecycle state and canonical `steps: list[ExecutionStep]` into `executions` with single-statement `WHERE state_version = $2` SQL OCC and cold `lz4`-compressed payloads (`raw_inputs`, `frozen_context` retaining `mcp_tool_audit`, `context_variables`, `execution_trace`, and `profile_syntheses`) into `execution_payloads` within one atomic transaction.
* **Consumer 3 (SDUI/PDF Report Services & Flutter Freezed `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]` / `@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L45]`):** Consumes `ExecutionRecord.steps` and `ExecutionRecord.profile_syntheses` across Backend Python, Jinja PDF, and Flutter Desktop with zero `step_states`, `active_profile_id`, `pdf_report_path`, or `*_storage_path` shadow fields.

### Canonical `executions` + `execution_payloads` PostgreSQL 19 DDL Specification (Section 1.4.1 Item 5 Verbatim)

```sql
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
    completed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_executions_org_id_created ON executions(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_executions_workflow_id ON executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_executions_created_by ON executions(created_by);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);

CREATE TABLE IF NOT EXISTS execution_payloads (
    execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE,
    raw_inputs JSONB COMPRESSION lz4 NOT NULL,
    frozen_context JSONB COMPRESSION lz4,
    context_variables JSONB COMPRESSION lz4 NOT NULL,
    execution_trace JSONB COMPRESSION lz4 NOT NULL,
    profile_syntheses JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L249-L520]` (`backend_v2/models/domain/execution.py#L221-L320`)
- `[MODIFY] @[backend_v2/models/execution_core.py#L70-L123]`
- `[MODIFY] @[backend_v2/models/state.py]`
- `[MODIFY] @[backend_v2/models/dtos/trace.py#L66-L128]`
- `[MODIFY] @[backend_v2/models/dtos/node_execution.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L30-L481]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L90-L1081]`
- `[MODIFY] @[backend_v2/services/execution/assignment_service.py#L150-L1959]`
- `[MODIFY] @[backend_v2/services/execution/context_service.py]`
- `[MODIFY] @[backend_v2/services/execution/ingress_service.py]`
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L36-L488]`
- `[MODIFY] @[backend_v2/services/execution/lifecycle_service.py#L25-L324]`
- `[MODIFY] @[backend_v2/services/execution/resumption_service.py#L30-L242]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`
- `[MODIFY] @[backend_v2/services/report/compilation_service.py#L33-L301]`
- `[MODIFY] @[backend_v2/services/report/lifecycle_service.py#L36-L464]`
- `[MODIFY] @[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]`
- `[MODIFY] @[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]`
- `[MODIFY] @[backend_v2/workers/execution_worker.py#_mark_execution_failed]`
- `[MODIFY] @[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`
- `[MODIFY] @[scripts/reconcile_storage.py#L59-L71]`
- `[MODIFY] @[scripts/diff_executions.py]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L407-L427]` (`@[scripts/audit_zero_orm_strictness.py#L834-L1028]`)
- `[MODIFY] @[scripts/audit_technical_debt.py#L253-L579]`
- `[MODIFY] @[scripts/_ast_guardrails.py#L111-L130]`
- `[MODIFY] @[scripts/audit_dict_eradication.py#L169-L628]` (`@[scripts/audit_dict_eradication.py#L874-L964]`)
- `[MODIFY] @[scripts/audit_skills_architecture.py#L160-L175]`
- `[MODIFY] @[.agents/rules/01-python-backend.md]`
- `[MODIFY] @[.agents/rules/03_seed_vault.md]`
- `[MODIFY] @[.agents/rules/04_directory_reference.md]`
- `[MODIFY] @[.agents/skills/tier2-hardening-backend/SKILL.md]`
- `[NEW] @[ki_zero_orm_postgres_enforcement.md]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`)
- `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]` (`@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L45]`)
- `[MODIFY] @[client_app_v2/lib/features/execution/views/execution_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/dashboard_view.dart]`
- `[MODIFY] @[client_app_v2/lib/shared/widgets/result_dashboard.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_reconcile_storage.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py]`
- `[MODIFY] @[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`

## Phase 4 Deprecations & Sunset Symbols

<demolish>
- `_offload_payloads`
- `_hydrate_payloads`
- `frozen_context_storage_path`
- `execution_trace_storage_path`
- `context_variables_storage_path`
- `pdf_report_path`
- `step_states`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]` & `@[backend_v2/database/repositories/execution.py#L30-L481]` | Local disk JSON offload (`_offload_payloads`, `_hydrate_payloads`, `*_storage_path`), silent `[]` coalescing on corrupt trace files, missing-`state_version` defaults, and two-step `SELECT`-before-`UPSERT` TOCTOU OCC in `save_execution_row`. | Split into lean 30-column `executions` (`VIRTUAL` `created_at`, `models_used DEFAULT '{}'::jsonb`, `duration_ms BIGINT NOT NULL DEFAULT 0`) + transactional 1:1 `execution_payloads` (`COMPRESSION lz4` for `raw_inputs`, `frozen_context` retaining `mcp_tool_audit`, `context_variables`, `execution_trace`, and `profile_syntheses`); enforce single-statement SQL OCC (`UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1 AND state_version = $2 RETURNING state_version`), distinguishing missing `id` (`ResourceNotFoundError` 404) from stale `state_version` (`ErrorCodes.CONFLICT` 409), and keep `list_executions_filtered` payload-free. | Do NOT shatter `ScorecardAtomDTO` or `TraceEvent` arrays into millions of EAV rows; store cold JSONB in 1:1 `lz4` TOAST `execution_payloads` alongside normalized `quorum_nodes` and `quorum_edges`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/unit/database/test_postgres.py backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py --test --ast-strict` |
| `@[backend_v2/models/domain/execution.py#L249-L520]`, `@[backend_v2/models/execution_core.py#L70-L123]`, `@[backend_v2/models/dtos/trace.py#L66-L128]`, `@[backend_v2/services/execution/override_service.py#L36-L488]`, `@[backend_v2/services/report/compilation_service.py#L33-L301]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]` & `@[backend_v2/services/blueprint.py#L90-L1081]` | Duplicate `ExecutionRecord.step_states` map, `active_profile_id`, synthetic `"sys_render_{profile_id}"` keys in `ReportCompilationService`, `pdf_report_path` shadow cache, and `*_storage_path` attributes. | Drop `step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` across all backend models, DTOs, services, DAG Orchestrator stages, workers, and CLI scripts with zero `@computed_field` shims; read and mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) and `output_profile_id` exclusively while retaining `ExecutionRecord.profile_syntheses` (`RenderedSynthesisCache`). | Preserve `profile_syntheses` and its immutable transition helpers (`with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) for Stage 2 synthesis (`feature_sovereignty_mandate`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/services/ backend_v2/workers/ backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict` |
| `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` & `@[scripts/audit_zero_orm_strictness.py#L407-L427]` | Permissive `InMemoryUnitOfWork` ignoring FK/UNIQUE/OCC violations, and outdated 16-table `audit_zero_orm_strictness.py` constants. | Upgrade `InMemoryUnitOfWork` and `InMemoryEntityAdapter` to enforce `ON DELETE RESTRICT` (`DELETE_BLOCKED_BY_USAGE` 400), `ON DELETE NO ACTION DEFERRABLE` (`workflows.default_profile_id`), `ON DELETE CASCADE`, `UNIQUE` (`CONFLICT` 409), and `state_version`/`version` OCC across all 22 tables; update `CLOSED_POSTGRES_TABLES` (22 tables) and `CANONICAL_ENTITY_PK_TABLES` (strictly the 16 UUIDv7-PK tables) and add `ZORM008` in `audit_zero_orm_strictness.py`. | Exclude composite/sidecar tables (`step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`) from `CANONICAL_ENTITY_PK_TABLES` so `ZORM004` stays exact. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py backend_v2/tests/fakes/ backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict` |
| `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]`, `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]` & `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]` | Stale `stepStates`, `activeProfileId`, `pdfReportPath`, and `*_StoragePath` fields on Flutter `ExecutionRecord` and view bindings. | Drop `stepStates`, `activeProfileId`, `pdfReportPath`, and `*_StoragePath` from `ExecutionRecord` and `ExecutionStep`, bind `record.outputProfileId` in `execution_view.dart`, `dashboard_view.dart`, and `result_dashboard.dart`, and retain `profileSyntheses` (`ProfileSynthesisEntryDto`) under `disallowUnrecognizedKeys: true`. | Maintain 1:1 Backend-PDF-Flutter semantic and DTO parity. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch` |
| `@[scripts/audit_technical_debt.py#L253-L579]`, `@[scripts/_ast_guardrails.py#L111-L130]`, `@[scripts/audit_dict_eradication.py#L874-L964]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/rules/04_directory_reference.md]` & `@[.agents/skills/tier2-hardening-backend/SKILL.md]` | `BOUNDARY_EXEMPTION_FILES` entries for `storage_driver.py` and `seed_and_collection_stage.py`, `EntityPrefix.SYSTEM_CONFIG`, `Filter`/`QueryCondition` exemptions, and stale 15/16-table or 8-collection rule/KI docs. | Add `TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, and `TD_UNWRAPPED_HYDRATION` to `audit_technical_debt.py`; lock `storage_driver.py` and `driver.py` into `QGR017` retired monoliths and scope retired `sys_` detection strictly to `^sys_[0-9a-fA-F]{32}$` (`QGR030`); synchronize `.agents/rules/`, create `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`, and verify pairwise orthogonality via `audit_skills_architecture.py`. | Consolidate static checks directly inside existing `audit_technical_debt.py`, `_ast_guardrails.py`, `audit_dict_eradication.py`, and `audit_zero_orm_strictness.py` visitors without new standalone linter scripts. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_skills_architecture.py` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[backend_v2/models/domain/execution.py#L249-L520]`, `@[backend_v2/models/domain/report_artifact.py#L22-L79]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`, `@[backend_v2/database/repositories/execution.py#L30-L481]`, `@[backend_v2/database/postgres/pool.py#L422-L652]`, `@[backend_v2/database/postgres/uow.py#L185-L435]`, and `@[scripts/audit_database_atoms.py#L328-L786]`.</action>
    <action>Look forward: Confirm explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` is active before executing Step 4.2 (`orchestrator_god_object_fragility`). Verify Step 4.1 implements the 30-column `executions` + `execution_payloads` (`COMPRESSION lz4`) split and single-statement `state_version` SQL OCC, Step 4.2 eradicates `step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` across all backend callers while preserving `profile_syntheses`, Step 4.3 upgrades `InMemoryUnitOfWork` and `audit_zero_orm_strictness.py` (22 tables + `ZORM008`), Step 4.4 synchronizes Flutter Execution Freezed models and views, and Step 4.5 locks static AST/technical-debt guardrails, rules, and Knowledge Items.</action>
    <constraint invariant="feature_sovereignty_mandate">NEVER remove `ExecutionRecord.profile_syntheses` (`dict[str, RenderedSynthesisCache]`), `with_updated_profile_synthesis`, `with_cleared_profile_syntheses`, `frozen_context.mcp_tool_audit`, or Flutter `ProfileSynthesisEntryDto`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/04_phase4_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L249-L520]</backend>
    <backend>@[backend_v2/models/execution_core.py#L70-L123]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py#L66-L128]</backend>
    <backend>@[backend_v2/models/dtos/node_execution.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]</backend>
    <backend>@[backend_v2/database/repositories/execution.py#L30-L481]</backend>
    <backend>@[backend_v2/services/blueprint.py#L90-L1081]</backend>
    <backend>@[backend_v2/services/execution/assignment_service.py#L150-L1959]</backend>
    <backend>@[backend_v2/services/execution/context_service.py]</backend>
    <backend>@[backend_v2/services/execution/ingress_service.py]</backend>
    <backend>@[backend_v2/services/execution/override_service.py#L36-L488]</backend>
    <backend>@[backend_v2/services/execution/lifecycle_service.py#L25-L324]</backend>
    <backend>@[backend_v2/services/execution/resumption_service.py#L30-L242]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]</backend>
    <backend>@[backend_v2/services/report/compilation_service.py#L33-L301]</backend>
    <backend>@[backend_v2/services/report/lifecycle_service.py#L36-L464]</backend>
    <backend>@[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]</backend>
    <backend>@[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]</backend>
    <backend>@[backend_v2/workers/execution_worker.py#_mark_execution_failed]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]</backend>
    <backend>@[scripts/reconcile_storage.py#L59-L71]</backend>
    <backend>@[scripts/diff_executions.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py#L407-L427]</backend>
    <backend>@[scripts/audit_technical_debt.py#L253-L579]</backend>
    <backend>@[scripts/_ast_guardrails.py#L111-L130]</backend>
    <backend>@[scripts/audit_dict_eradication.py#L169-L628]</backend>
    <backend>@[scripts/audit_skills_architecture.py#L160-L175]</backend>
    <backend>@[.agents/rules/01-python-backend.md]</backend>
    <backend>@[.agents/rules/03_seed_vault.md]</backend>
    <backend>@[.agents/rules/04_directory_reference.md]</backend>
    <backend>@[.agents/skills/tier2-hardening-backend/SKILL.md]</backend>
    <backend>[NEW] @[ki_zero_orm_postgres_enforcement.md]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]</backend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/execution_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/dashboard_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/shared/widgets/result_dashboard.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_postgres.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_reconcile_storage.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]</backend>
    <backend>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</backend>
    <frontend>@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`executions` (30 hot columns) and `execution_payloads` (1:1 `COMPRESSION lz4` sidecar storing `raw_inputs`, `frozen_context`, `context_variables`, `execution_trace`, and `profile_syntheses`) are live in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` and `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`, `_offload_payloads`/`_hydrate_payloads` are deleted, and `save_execution_row` enforces single-statement SQL OCC (`WHERE state_version = $2`).</item>
    <item>`ExecutionRecord.step_states`, `active_profile_id`, `pdf_report_path`, and `*_storage_path` are eradicated full-duplex across Python models, DTOs, services, DAG Orchestrator stages, workers, CLI scripts, and Flutter (`execution_record.dart`, `execution_step.dart`, `execution_view.dart`, `dashboard_view.dart`, `result_dashboard.dart`) with zero `@computed_field` transition shims while retaining Stage 2 `profile_syntheses`.</item>
    <item>`@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`) enforces all 22-table FK `ON DELETE RESTRICT` / `NO ACTION DEFERRABLE` / `CASCADE`, `UNIQUE`, and `state_version`/`version` OCC constraints, and `@[scripts/audit_zero_orm_strictness.py#L407-L427]` (`@[scripts/audit_zero_orm_strictness.py#L834-L1028]`) enforces the closed 22-table topology, 16-table `CANONICAL_ENTITY_PK_TABLES`, and `ZORM008`.</item>
    <item>`@[scripts/audit_technical_debt.py#L253-L579]` enforces `TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, and `TD_UNWRAPPED_HYDRATION`; `@[scripts/_ast_guardrails.py#L111-L130]` and `@[scripts/audit_dict_eradication.py#L169-L628]` (`@[scripts/audit_dict_eradication.py#L874-L964]`) remove `storage_driver.py` and `seed_and_collection_stage.py` exemptions and scope retired `sys_` detection to `^sys_[0-9a-fA-F]{32}$`; and `.agents/rules/` plus `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` pass `scripts/audit_skills_architecture.py`.</item>
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
    <anti_target>Do NOT include composite/sidecar tables (`step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`) in `CANONICAL_ENTITY_PK_TABLES` in `scripts/audit_zero_orm_strictness.py`.</anti_target>
    <anti_target>Do NOT match legitimate `sys_rag_*` step keys or `_sys_initiator_id` metadata keys when flagging retired `sys_<hex32>` entity IDs in `QGR030` (match strictly `^sys_[0-9a-fA-F]{32}$` and `EntityPrefix.SYSTEM_CONFIG`).</anti_target>
  </anti_targets>

  <step id="4.1" name="executions + execution_payloads (COMPRESSION lz4) 1:1 Sidecar Split &amp; Atomic Single-Statement state_version SQL OCC">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L301-L420]`, `@[backend_v2/database/repositories/execution.py#L30-L481]`, `@[backend_v2/tests/unit/database/test_postgres.py]`, and `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`: Split `executions` into the lean 30-column `executions` table (`models_used DEFAULT '{}'::jsonb`, `duration_ms BIGINT NOT NULL DEFAULT 0`, `VIRTUAL` `created_at`) and the 1:1 `execution_payloads` sidecar table (`execution_id UUID PRIMARY KEY REFERENCES executions(id) ON DELETE CASCADE`, `raw_inputs JSONB COMPRESSION lz4 NOT NULL`, `frozen_context JSONB COMPRESSION lz4` retaining `mcp_tool_audit`, `context_variables JSONB COMPRESSION lz4 NOT NULL`, `execution_trace JSONB COMPRESSION lz4 NOT NULL`, and `profile_syntheses JSONB COMPRESSION lz4 NOT NULL DEFAULT '{}'::jsonb`). Delete `_offload_payloads` and `_hydrate_payloads` from `ExecutionRepositoryImpl`. Replace the two-step `SELECT state_version`-then-`UPSERT` in `save_execution_row` with an atomic single-statement SQL OCC update (`UPDATE executions SET ..., state_version = state_version + 1 WHERE id = $1 AND state_version = $2 RETURNING state_version`) paired with `INSERT INTO execution_payloads ... ON CONFLICT (execution_id) DO UPDATE` inside the same transaction, distinguishing missing `id` (`ResourceNotFoundError` 404) from stale `state_version` (`AppException(ErrorCodes.CONFLICT, status_code=409)`). Keep `list_executions_filtered` lean by omitting cold `execution_payloads` joins while joining `execution_payloads` on primary-key hydration (`get_execution_row`).</action>
    <constraint invariant="uow_transactional_concurrency_mandate">Hot `executions` row updates and cold `execution_payloads` upserts MUST commit or roll back atomically inside a single PostgreSQL 19 transaction under `WHERE state_version = $2` OCC.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/unit/database/test_postgres.py backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py --test --ast-strict</audit_command>
  </step>

  <step id="4.2" name="Full-Duplex Backend Eradication of ExecutionRecord.step_states, active_profile_id, pdf_report_path &amp; *_storage_path (Preserving profile_syntheses)">
    <action>1. `[MODIFY]` `@[backend_v2/models/domain/execution.py#L249-L520]` (`backend_v2/models/domain/execution.py#L221-L320`), `@[backend_v2/models/execution_core.py#L70-L123]`, `@[backend_v2/models/state.py]`, `@[backend_v2/models/dtos/trace.py#L66-L128]`, `@[backend_v2/models/dtos/node_execution.py]`, `@[backend_v2/tests/factories/model_factories.py]`, and `@[backend_v2/tests/fakes/in_memory_repositories.py]`: Drop `step_states`, `active_profile_id`, `pdf_report_path`, `frozen_context_storage_path`, `execution_trace_storage_path`, and `context_variables_storage_path` from `ExecutionRecord`, `ExecutionCore`, `state.py`, `ExecutionCreateDTO`, `ExecutionUpdateDTO`, `NodeExecutionUpdateDTO`, `ExecutionRecordFactory`, and `InMemoryUnifiedWorkflowRepository` with zero `@computed_field` transition shims, while retaining `ExecutionRecord.profile_syntheses: dict[str, RenderedSynthesisCache]` and its helpers (`with_updated_profile_synthesis`, `with_cleared_profile_syntheses`) and updating `with_updated_step_state` to mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) immutably.</action>
    <action>2. `[MODIFY]` `@[backend_v2/services/blueprint.py#L90-L1081]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, `@[backend_v2/services/execution/context_service.py]`, `@[backend_v2/services/execution/ingress_service.py]`, `@[backend_v2/services/execution/override_service.py#L36-L488]`, `@[backend_v2/services/execution/lifecycle_service.py#L25-L324]`, `@[backend_v2/services/execution/resumption_service.py#L30-L242]`, `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L143]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#WorkflowBootstrapStage]`, `@[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]`, `@[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]`, `@[backend_v2/services/orchestrator/strategies/llm_strategy/engine_retry_stage.py]`, `@[backend_v2/services/report/compilation_service.py#L33-L301]`, `@[backend_v2/services/report/lifecycle_service.py#L36-L464]`, `@[backend_v2/services/export/metadata_resolver.py#ExportMetadataResolver]`, `@[backend_v2/services/sdui/sdui_mapper_service.py#L33-L194]`, `@[backend_v2/workers/execution_worker.py#_mark_execution_failed]`, `@[backend_v2/workers/synthesis_reducers.py#persist_profile_synthesis_atomic]`, `@[backend_v2/workers/synthesis_worker.py#execute_synthesis_phase]`, `@[scripts/reconcile_storage.py#L59-L71]`, `@[scripts/diff_executions.py]`, `@[scripts/run_e2e_variance_test.py]`, `@[backend_v2/tests/unit/scripts/test_reconcile_storage.py]`, and `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`: Update all execution, DAG Orchestrator, blueprint, SDUI, export, report compilation (dropping synthetic `"sys_render_{profile_id}"` keys), worker, and CLI callers to read and mutate `ExecutionRecord.steps` (`list[ExecutionStep]`) and `output_profile_id` exclusively.</action>
    <constraint invariant="ban_heuristic_identifier_matching">Zero synthetic `"sys_render_{profile_id}"` step keys may be injected into `ExecutionRecord.steps`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/services/ backend_v2/workers/ scripts/reconcile_storage.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/scripts/test_reconcile_storage.py backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict</audit_command>
  </step>

  <step id="4.3" name="Constraint-Enforcing InMemoryUnitOfWork &amp; 22-Table audit_zero_orm_strictness.py (ZORM004-ZORM008)">
    <action>1. `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]` (`backend_v2/tests/fakes/in_memory_uow.py#L1-L561`): Upgrade `InMemoryUnitOfWork` and `InMemoryEntityAdapter` to enforce `ON DELETE RESTRICT` (`ErrorCodes.DELETE_BLOCKED_BY_USAGE` 400), `ON DELETE NO ACTION DEFERRABLE` (`workflows.default_profile_id` evaluated at transaction commit), `ON DELETE CASCADE` (including `organization_id` across all tenant-scoped tables, `execution_payloads`, and `tenant_secrets.mcp_gateway_id`), `UNIQUE` constraints (`ErrorCodes.CONFLICT` 409), and `state_version` / `version` OCC across all 22 tables.</action>
    <action>2. `[MODIFY]` `@[scripts/audit_zero_orm_strictness.py#L407-L427]` (`@[scripts/audit_zero_orm_strictness.py#L834-L1028]`) and `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`: Update `CLOSED_POSTGRES_TABLES` to the exact 22 tables (`organizations`, `users`, `invitations`, `tenant_secrets`, `model_registries`, `mcp_gateways`, `prompt_blocks`, `task_briefs`, `steps`, `step_criteria_blocks`, `workflows`, `workflow_step_refs`, `output_profiles`, `executions`, `execution_payloads`, `execution_assignments`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`, `audit_logs`, `usage_records`), update `CANONICAL_ENTITY_PK_TABLES` strictly to the 16 UUIDv7-PK tables (adding `model_registries`, `mcp_gateways`, `audit_logs`, `usage_records` and dropping `system_configs`, excluding `step_criteria_blocks`, `workflow_step_refs`, `execution_payloads`, `report_binaries`, `quorum_nodes`, `quorum_edges`), synchronize `CANONICAL_NAMED_ENTITY_TABLES` and `APPROVED_ADAPTER_RECORD_COLUMNS`, and add `ZORM008` banning `StorageDriver` imports, unwrapped `.model_validate(` calls in `entity_adapter/` stage modules, and unparameterized `SELECT *` list scans.</action>
    <constraint invariant="hermetic_test_fixtures_mandate">Every FK `RESTRICT`/`CASCADE`, `UNIQUE`, and OCC invariant enforced by PostgreSQL 19 MUST behave identically in `InMemoryUnitOfWork` unit tests.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict</audit_command>
  </step>

  <step id="4.4" name="Flutter ExecutionRecord, ExecutionStep &amp; Dashboard View Full-Duplex Parity">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/execution/models/execution_record.dart#L15-L162]`, `@[client_app_v2/lib/features/execution/models/execution_step.dart#L15-L45]` (`@[client_app_v2/lib/features/execution/models/execution_step.dart#L1-L45]`), `@[client_app_v2/lib/features/execution/views/execution_view.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`, `@[client_app_v2/test/unit/features/execution/models/execution_record_test.dart]`, and `@[client_app_v2/test/unit/features/execution/models/execution_step_test.dart]`: Drop `stepStates`, `activeProfileId`, `pdfReportPath`, `frozenContextStoragePath`, `executionTraceStoragePath`, and `contextVariablesStoragePath` from `ExecutionRecord` and `ExecutionStep`, replace `record.activeProfileId` with `record.outputProfileId` in `execution_view.dart`, `dashboard_view.dart`, and `result_dashboard.dart`, preserve `profileSyntheses` (`ProfileSynthesisEntryDto`) and `@JsonSerializable(disallowUnrecognizedKeys: true)`, regenerate `.freezed.dart` / `.g.dart` siblings, and update unit tests (`execution_record_test.dart`, `execution_step_test.dart`) to assert strict rejection of removed keys.</action>
    <constraint invariant="full_duplex_serialization_parity_mandate">`ExecutionRecord` wire JSON keys MUST match 1:1 between Python Pydantic and Flutter Freezed under `uv run python scripts/audit_dto_parity.py --fail-on-mismatch`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</audit_command>
  </step>

  <step id="4.5" name="Single-Pipeline Governance Lock Across audit_technical_debt.py, _ast_guardrails.py, audit_dict_eradication.py, Rules &amp; Knowledge Items">
    <action>1. `[MODIFY]` `@[scripts/audit_technical_debt.py#L253-L579]`, `@[scripts/_ast_guardrails.py#L111-L130]`, `@[scripts/audit_dict_eradication.py#L169-L628]` (`@[scripts/audit_dict_eradication.py#L874-L964]`), `@[backend_v2/tests/unit/scripts/test_audit_technical_debt.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`, and `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`: Add `TD_EXCEPT_SWALLOW_RETURN` (flagging `except (Exception, AppException, ValidationError)` blocks returning `None`, `False`, `[]`, or `{}` without `logger.error` and `raise AppException`), `TD_LEGACY_STORAGE_DRIVER` (flagging imports/references to `StorageDriver`, `PostgresStorageDriver`, `Filter`, `QueryCondition`, `AppendOnlyRepositoryBase`, `KnowledgeRepositoryImpl`, `ComponentRepositoryImpl`, `AgentRepositoryImpl`, `RoleRepositoryImpl`, `TaskBlueprintRepositoryImpl`), and `TD_UNWRAPPED_HYDRATION` (flagging direct `.model_validate(` or `.validate_python(` calls inside `backend_v2/database/postgres/` outside `validate_hydrated_row`) in `audit_technical_debt.py`. Drop `"backend_v2/database/postgres/storage_driver.py"` and `"backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py"` from `BOUNDARY_EXEMPTION_FILES`, add `"backend_v2/database/postgres/storage_driver.py"` and `"backend_v2/database/driver.py"` to `QGR017` retired monoliths, update `_QGR030_ENTITY_PREFIXES` (`mrg`, `mcp`, `tbr`, `tsk`, `aud`, `usg`, `inv`, `sec`; scoping retired `sys_` detection strictly to `^sys_[0-9a-fA-F]{32}$` and `EntityPrefix.SYSTEM_CONFIG`), and drop obsolete `Filter`/`QueryCondition` (`_QGR031_*`) exemptions.</action>
    <action>2. `[MODIFY]` `@[.agents/rules/01-python-backend.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]`, `@[scripts/audit_skills_architecture.py#L160-L175]`, `@[backend_v2/tests/unit/scripts/test_audit_skills_architecture.py]`, and `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]`: Update `01-python-backend.md` (`primary_key_lookup_o1_mandate`, `in_place_upsert_standard_mandate`, `crud_and_clone_lifecycle_standard_mandate`, `zero_orm_ddl_column_evolution_and_preflight_mandate`, `service_layer_hydration_firewall`), `03_seed_vault.md`, and `04_directory_reference.md` to codify the single `EntityPersistencePort` pipeline, 22-table PostgreSQL 19 topology, `validate_hydrated_row`, `translate_postgres_exception`, `ON DELETE RESTRICT`, `ROOT_SYSTEM` `organization_id NOT NULL ON DELETE CASCADE`, and 9-collection `seed_data.json`. Create `[NEW]` `@[ki_zero_orm_postgres_enforcement.md]` (and synchronize `ki_router_ssot_and_crud_clone_lifecycle.md`, `ki_global_config_sovereignty.md`, `ki_mcp_gateway_architecture.md`, and `ki_zero_permissive_typing.md` plus `metadata.json`), register `ki_zero_orm_postgres_enforcement.md` in `DEFAULT_CANONICAL_KI_ARTIFACTS` (`audit_skills_architecture.py`) and `tier2-hardening-backend/SKILL.md`, and execute pairwise rule and static checker orthogonality verification via `uv run python scripts/audit_skills_architecture.py`.</action>
    <constraint invariant="pairwise_rule_and_guardrail_orthogonality_mandate">Every added or modified `<rule_block>` and static AST checker MUST pass pairwise conflict and syntax probe verification via `scripts/audit_skills_architecture.py`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/audit_zero_orm_strictness.py scripts/audit_technical_debt.py scripts/_ast_guardrails.py scripts/audit_dict_eradication.py scripts/audit_skills_architecture.py backend_v2/tests/unit/scripts/ --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_execution_and_lz4_payloads_sidecar_roundtrip_preserves_profile_syntheses_and_mcp_audit" category="positive">
      <input>`ExecutionRecordFactory.build(...)` containing `steps`, `raw_inputs`, `frozen_context` (`mcp_tool_audit`), `context_variables`, `execution_trace`, and `profile_syntheses` (`RenderedSynthesisCache`) persisted and hydrated by primary key</input>
      <expected>Persists hot columns in `executions` and cold JSONB in `execution_payloads` (`COMPRESSION lz4`), roundtripping 100% of fields without local disk `*_storage_path` files while `list_executions_filtered` executes without cold sidecar joins</expected>
    </test>
    <test name="test_save_execution_row_concurrent_taskgroup_occ_race_raises_conflict_409" category="boundary">
      <input>Two concurrent `asyncio.TaskGroup` tasks updating the same `ExecutionRecord` from `state_version=1`</input>
      <expected>Exactly one task commits `state_version=2`; the competing task fails fast with `AppException(ErrorCodes.CONFLICT, status_code=409)` with zero lost updates</expected>
    </test>
    <test name="test_save_execution_row_missing_execution_id_raises_resource_not_found_404" category="negative">
      <input>OCC update attempted on a non-existent `ExecutionRecord.id` expecting `state_version=2`</input>
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
      <input>`InMemoryUnitOfWork` delete of referenced `Workflow`/`PromptBlock`/`TaskBrief`, delete of `workflows.default_profile_id` at commit, duplicate `token_hash` insert, and stale `state_version` update</input>
      <expected>Raises `ErrorCodes.DELETE_BLOCKED_BY_USAGE` (400) on `RESTRICT` and deferred `NO ACTION` violations, `ErrorCodes.CONFLICT` (409) on `UNIQUE` and stale `state_version`/`version` updates, and cascades `organization_id` and `mcp_gateway_id` deletes</expected>
    </test>
    <test name="test_zorm008_and_technical_debt_visitors_reject_storage_driver_swallow_and_unwrapped_hydration" category="negative">
      <input>Synthetic AST snippets importing `StorageDriver`, catching `except AppException: return None`, calling unwrapped `.model_validate(` in `entity_adapter/`, or embedding `sys_0195f3a00000700080008172bda70c86` while keeping `sys_rag_preflight`</input>
      <expected>`ZORM008`, `TD_EXCEPT_SWALLOW_RETURN`, `TD_LEGACY_STORAGE_DRIVER`, `TD_UNWRAPPED_HYDRATION`, and `QGR030` flag all banned constructs while passing `sys_rag_preflight` and `_sys_initiator_id` cleanly</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/database backend_v2/services --include-one-hop; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/audit_skills_architecture.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/audit_zero_orm_strictness.py scripts/audit_technical_debt.py scripts/_ast_guardrails.py scripts/audit_dict_eradication.py scripts/audit_skills_architecture.py scripts/reconcile_storage.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/scripts/ --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</command>
  </validation_gate>
</execution_protocol>

