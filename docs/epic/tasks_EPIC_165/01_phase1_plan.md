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

# EPIC 165 - Phase 1: Pre-Implementation Cleanups, Fail-Fast Hydrator & Exception Translation Gate, Studio IDOR & 4-Phase In-Place Upsert Hardening, Single-UoW Transactionality & `StorageDriver` / V1 Ghost Repository Eradication

**Overview:** Establish the single sovereign `EntityPersistencePort` (`QuorumUnitOfWork`) persistence pipeline across Quorum V2 by implementing unified Fail-Fast row hydration (`validate_hydrated_row`) and PostgreSQL `SQLSTATE` exception translation (`translate_postgres_exception` via `@runtime_checkable class _SqlStateCarrier(Protocol)`) in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L344-L351]`, closing cross-tenant `PUT` IDOR and multi-autocommit transactional tears across all Studio services (`@[backend_v2/services/studio/prompt_block_service.py#L31-L320]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, `@[backend_v2/services/studio/system_config_service.py#L44-L817]`), introducing append-only PostgreSQL 19 `audit_logs` (`aud_`, `AuditLogRecord`) and `usage_records` (`usg_`, full FinOps telemetry parity) ledgers with SQL `SUM(...)` / `COUNT(*)` FinOps rollups (`UsageRollupSummaryDTO`), migrating all 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade (`@[backend_v2/database/repository.py#L19-L35]`) onto `EntityPersistencePort`, synchronizing `@[scripts/audit_zero_orm_strictness.py#L432-L452]` and `@[scripts/_ast_guardrails.py]` ratchets, and permanently deleting the legacy Firestore-era `StorageDriver` / `PostgresStorageDriver` dictionary layer along with all 11 legacy driver / dead V1 ghost modules and their 12 companion test files.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

> [!IMPORTANT]
> **Pre-Flight Technical Debt & DAG Orchestrator Permission Gate (`orchestrator_god_object_fragility`):**
> * Pre-flight baseline via `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --plan docs/epic/tasks_EPIC_165/01_phase1_plan.md --include-one-hop` identified `0` production technical debt findings and `1` test-suite finding (`TD_ISTQB_NEGATIVE` on `@[backend_v2/tests/unit/test_repositories_v2.py]`, which lacks `test_*_failure` / `test_*_invalid` / `test_*_error` functions and blocks `--strict`). Step 1.4 explicitly resolves `TD_ISTQB_NEGATIVE` by adding ISTQB negative and failure test partitions to `@[backend_v2/tests/unit/test_repositories_v2.py]`.
> * Removing dead `comp_repo: IComponentRepository | None` constructor parameters from `@[backend_v2/services/orchestrator/dag_executor/__init__.py#L77-L174]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`, `@[backend_v2/services/orchestrator/strategies/base.py#L106-L129]`, `@[backend_v2/services/orchestrator/strategies/logic.py]`, and `@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` requires explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` prior to `/tier2-execute` (or invocation under `--full-auto` with explicit orchestrator permission), followed by the full `backend_audit_loop.py` gate.

## Phase 1 Forensic Context & Invariants (Verbatim from EPIC 165)

### First Principles & Current-to-Target Persistence Cutover Context
* Audited schema and driver sources: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `@[backend_v2/database/postgres/pool.py#L422-L652]`, `@[backend_v2/database/postgres/uow.py#L185-L435]`, and `@[scripts/audit_zero_orm_strictness.py#L432-L452]`.
* **Finding 1 [P0 CRITICAL] — Firestore-Era Generic `StorageDriver`, Silent Volatile RAM Fallback & Dead V1 Ghost Layer:**
  * Forensic anchors: `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]` (`type StorageDocument = dict[str, StorageValue]`, `backend_v2/database/driver.py#L1-L143`), `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L47-L76]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L218-L247]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L291-L324]` (`_CANONICAL_COLLECTION_ALIASES` and `self._collections` RAM fallback, `backend_v2/database/postgres/storage_driver.py#L1-L195`), `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]` (`upsert_collection_document_row` swallowing `AppException`, `ValueError`, `KeyError`, `TypeError` and returning `False` with zero logging), `@[backend_v2/models/enums.py#L274-L277]` (`FIRESTORE` and `LOCAL` enum remnants alongside `POSTGRES`), and `@[backend_v2/api/dependencies.py#L317-L330]` (wiring V1 ghost repositories `KnowledgeRepositoryImpl`, `AgentRepositoryImpl`, `ComponentRepositoryImpl`, `TaskBlueprintRepositoryImpl`).
  * Active runtime failures eradicated in Phase 1: (1) cross-process loss of MCP grounding audit trails in `@[backend_v2/database/repositories/execution.py#L44-L80]` and `@[backend_v2/database/repositories/execution.py#L120-L211]`, (2) volatile compliance `"audit_logs"` and `"usage"` plus mutable shadow `"usage_aggregates"` in `@[backend_v2/database/repositories/audit.py#L25-L263]` and `@[backend_v2/services/usage_service.py#L24-L418]`, and (3) unmounted V1 ghost repositories `[DELETE]` `@[backend_v2/database/repositories/knowledge.py#L30-L219]`, `[DELETE]` `@[backend_v2/database/repositories/component.py#L17-L242]`, `[DELETE]` `@[backend_v2/database/repositories/components/agent.py#L17-L163]`, `[DELETE]` `@[backend_v2/database/repositories/components/role.py#L17-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/task_blueprint.py#L18-L167]`, `[DELETE]` `@[backend_v2/database/repositories/components/matrix.py#L18-L168]`, `[DELETE]` `@[backend_v2/database/repositories/components/execution_persona.py#L18-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/extraction_protocol.py#L18-L145]`, and `SystemRepositoryImpl.update_system_settings` (`doc_id="global_settings"` in `@[backend_v2/database/repositories/system.py#L20-L166]`, whereas `@[backend_v2/api/routers/system/configs.py#L71-L117]` serves static `StrictnessAnchor` enums only; `TokenService` is defined in `auth/` alongside `AuthService`).
* **Finding 2 [P0 CRITICAL] — Full-Table `SELECT *` Scans, Broken Repository Filter Keys & Legacy Disk Fallbacks:**
  * Forensic anchors: `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L424-L477]`, `@[backend_v2/database/repositories/execution.py#L424-L440]` (`user_id` vs `created_by`, lowercase `"completed"` vs `"COMPLETED"`, dead `matrix_id`), `@[backend_v2/services/execution/assignment_service.py#L762-L778]` and `@[backend_v2/services/execution/assignment_service.py#L1706-L1722]`, `@[backend_v2/database/repositories/workflow.py#L52-L71]`, and `@[backend_v2/main.py#L70-L115]` (legacy `data/workflows` and `execution_trace_storage_path` disk checks).
* **Finding 7 [P0 CRITICAL] — Complete Forensic Catalog of Silent Error Swallows (Sites 1–6, 9–12):**
  1. `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L82-L140]`: Drop `get_collection_document_row` (which caught `except AppException: return None`, disguising DB timeouts and corrupt rows as HTTP 404).
  2. `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`: Drop `list_collection_document_rows`, `upsert_collection_document_row`, `delete_collection_document_row`, and `clear_collection_document_rows`.
  3. `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`: Drop `PostgresStorageDriver` and `StorageDriver` completely.
  4. `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L219-L269]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L259-L319]`, `@[backend_v2/database/postgres/graph_adapter.py#L468-L761]`, and `@[backend_v2/database/repositories/identity.py#L31-L388]`: Enforce single SSOT `validate_hydrated_row(model_cls_or_adapter, payload, *, table_name: str, entity_id: str) -> T` catching `ValidationError` -> `logger.error` + `AppException(ErrorCodes.VALIDATION_FAILED, status_code=500)`.
  5. `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]`: Dispatch `hydrate_prompt_block_row` strictly through `PromptBlockAdapter.validate_python(payload, strict=False)` inside `validate_hydrated_row(...)` instead of falling through `else: SystemRulePromptBlock`.
  6. `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L413-L528]`: Centralize `translate_postgres_exception(exc, *, operation: str, table_name: str, entity_id: str) -> AppException` mapping `SQLSTATE 23503` on `DELETE` to HTTP 400 `ErrorCodes.DELETE_BLOCKED_BY_USAGE`, `SQLSTATE 23503` on `INSERT`/`UPDATE` to HTTP 422 `ErrorCodes.VALIDATION_FAILED`, `SQLSTATE 23505` to HTTP 409 `ErrorCodes.CONFLICT`, and transport/I/O errors to HTTP 500 `ErrorCodes.STORAGE_ACCESS_FAILED` (preceded by structured `logger.error`).
  9. `@[backend_v2/database/repositories/workflow.py#L296-L306]`: Drop `data/workflows/{id}.json` disk fallback, dead embedded-step scan in `get_step_by_id`, and `setdefault` dictionary hacks.
  10. `@[backend_v2/database/repositories/system.py#L20-L166]`: Drop `update_system_settings` and `get_system_settings` (along with `SystemSettingsDTO`) and `f"cfg_{config_data.type}"` non-UUIDv7 ID fallback.
  11. `@[backend_v2/database/postgres/graph_adapter.py#L468-L761]` (`_MATERIALIZE_WAVE_SQL`): Replace `ON CONFLICT (run_id, source_id, target_id, relation_type) DO NOTHING RETURNING edge_id` with `ON CONFLICT (run_id, source_id, target_id, relation_type) DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`.
  12. `@[backend_v2/services/usage_service.py#L310-L418]` & `@[backend_v2/database/repositories/identity.py#L67-L77]`: Compute `get_usage_report` and `check_quota` directly from `usage_records` via parameterized SQL `SUM(...)` / `COUNT(*)`; raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)` when `get_organization(org_id)` is `None`.
* **Finding 8 [P0 CRITICAL] — Studio Cross-Tenant IDOR Closure, 4-Phase In-Place Upsert, Single-UoW FK Ordering & Clone Hygiene:**
  * Enforce 4-Phase In-Place Upsert across `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, and `save_task_brief`: fetch `existing` first (`ResourceNotFoundError` 404 if missing), verify `enforce_modification_rights(initiator, existing.organization_id)` before reading payload, preserve `existing.organization_id` for non-`ROOT` callers, and route `create_*_draft` / `clone_*` through private `_insert_validated_*` helpers.
  * Fix `clone_workflow` in `@[backend_v2/services/studio/workflow_service.py#L657-L720]` inside one `async with uow:` transaction with parent-before-child ordering (`Workflow` with `default_profile_id=None` -> cloned `OutputProfile` rows -> update `Workflow.default_profile_id`), execute multi-table mutations inside single `async with uow:` blocks, drop `AppendOnlyRepositoryBase` (`@[backend_v2/database/repositories/base.py#L46-L66]`), preserve `original.slug` on Studio clones and `{original.slug}_copy` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones, replace `"New Työnkulku"` -> `"New Workflow"` and `"New Askel"` -> `"New Step"`, and enforce symmetric `ROOT`/`ADMIN` read RBAC on `@[backend_v2/services/studio/system_config_service.py#L44-L817]`.

### Append-Only `audit_logs` & `usage_records` SQL DDL (from Section 1.4.1)

```sql
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    actor_id UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_org_created ON audit_logs(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_execution_id ON audit_logs(execution_id);

CREATE TABLE IF NOT EXISTS usage_records (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    model_name TEXT NOT NULL,
    prompt_tokens BIGINT NOT NULL DEFAULT 0 CHECK (prompt_tokens >= 0),
    completion_tokens BIGINT NOT NULL DEFAULT 0 CHECK (completion_tokens >= 0),
    cached_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cached_tokens >= 0),
    reasoning_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reasoning_tokens >= 0),
    cache_creation_input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cache_creation_input_tokens >= 0),
    latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),
    finish_reason TEXT,
    system_fingerprint TEXT,
    cost_usd NUMERIC(14, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
    estimated_savings_usd NUMERIC(14, 6) NOT NULL DEFAULT 0 CHECK (estimated_savings_usd >= 0),
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
CREATE INDEX IF NOT EXISTS idx_usage_records_org_created ON usage_records(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_usage_records_execution_id ON usage_records(execution_id);
```

### Target Files
- `[DELETE] @[backend_v2/database/driver.py]`
- `[DELETE] @[backend_v2/database/postgres/storage_driver.py]`
- `[DELETE] @[backend_v2/models/domain/knowledge.py]`
- `[DELETE] @[backend_v2/database/repositories/knowledge.py]`
- `[DELETE] @[backend_v2/database/repositories/component.py]`
- `[DELETE] @[backend_v2/database/repositories/components/agent.py]`
- `[DELETE] @[backend_v2/database/repositories/components/role.py]`
- `[DELETE] @[backend_v2/database/repositories/components/task_blueprint.py]`
- `[DELETE] @[backend_v2/database/repositories/components/matrix.py]`
- `[DELETE] @[backend_v2/database/repositories/components/execution_persona.py]`
- `[DELETE] @[backend_v2/database/repositories/components/extraction_protocol.py]`
- `[DELETE] @[backend_v2/tests/unit/models/domain/test_knowledge_dtos.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/test_knowledge.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/test_component.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_agent.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_role.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_matrix.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_execution_persona.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_extraction_protocol.py]`
- `[DELETE] @[backend_v2/tests/unit/database/repositories/test_base.py]`
- `[DELETE] @[backend_v2/tests/unit/test_driver.py]`
- `[DELETE] @[backend_v2/tests/unit/test_storage_audit.py]`
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/database/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L302-L316]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L219-L269]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L259-L319]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L239-L250]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L253-L297]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L360-L465]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L468-L761]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L413-L426]`
- `[MODIFY] @[backend_v2/database/factory.py#L77-L112]`
- `[MODIFY] @[backend_v2/database/repository.py#L19-L35]`
- `[MODIFY] @[backend_v2/database/repositories/__init__.py]`
- `[MODIFY] @[backend_v2/database/repositories/components/__init__.py]`
- `[MODIFY] @[backend_v2/database/repositories/base.py#L46-L66]`
- `[MODIFY] @[backend_v2/database/repositories/audit.py#L25-L263]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L31-L388]`
- `[MODIFY] @[backend_v2/database/repositories/workflow.py#L26-L512]`
- `[MODIFY] @[backend_v2/database/repositories/system.py#L20-L166]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L41-L440]`
- `[MODIFY] @[backend_v2/database/repositories/report_artifact.py#L23-L148]`
- `[MODIFY] @[backend_v2/database/repositories/components/prompt_block.py#L16-L200]`
- `[MODIFY] @[backend_v2/database/repositories/components/output_profile.py#L11-L98]`
- `[MODIFY] @[backend_v2/database/repositories/components/task_brief.py#L11-L90]`
- `[MODIFY] @[backend_v2/models/domain/base.py#L394-L476]`
- `[MODIFY] @[backend_v2/models/dtos/system.py]`
- `[MODIFY] @[backend_v2/models/enums.py#L274-L277]`
- `[MODIFY] @[backend_v2/services/auth/secret_service.py#L140-L1170]`
- `[MODIFY] @[backend_v2/services/usage_service.py#L24-L418]`
- `[MODIFY] @[backend_v2/services/studio/prompt_block_service.py#L31-L320]`
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L49-L990]`
- `[MODIFY] @[backend_v2/services/studio/output_profile_service.py#L26-L369]`
- `[MODIFY] @[backend_v2/services/studio/task_brief_service.py#L29-L279]`
- `[MODIFY] @[backend_v2/services/studio/system_config_service.py#L44-L817]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L89-L1076]`
- `[MODIFY] @[backend_v2/services/execution/facade.py#L69-L714]`
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L35-L482]`
- `[MODIFY] @[backend_v2/services/report/__init__.py#L42-L297]`
- `[MODIFY] @[backend_v2/services/report/compilation_service.py#L33-L299]`
- `[MODIFY] @[backend_v2/services/report/format_reader_service.py#L22-L229]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/__init__.py#L77-L174]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/base.py#L106-L129]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/logic.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`
- `[MODIFY] @[backend_v2/core/hook_registry.py]`
- `[MODIFY] @[backend_v2/llm/handler.py]`
- `[MODIFY] @[backend_v2/worker.py]`
- `[MODIFY] @[backend_v2/workers/report_worker.py]`
- `[MODIFY] @[backend_v2/workers/synthesis_reducers.py#L58-L79]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#L155-L183]`
- `[MODIFY] @[backend_v2/api/dependencies.py#L317-L330]`
- `[MODIFY] @[backend_v2/main.py#L70-L115]`
- `[MODIFY] @[scripts/ablation_live_executor.py]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L432-L452]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/conftest.py]`
- `[MODIFY] @[backend_v2/tests/fakes/__init__.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py#L1545-L1552]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L2001-L2012]`
- `[MODIFY] @[backend_v2/tests/factories/__init__.py]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/factories/test_model_factories.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test___init__.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_repository.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_task_brief.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_audit.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_identity.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_report_artifact.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_workflow.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_base.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_system_config_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_compilation_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_format_reader_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_override_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution_resumability.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_atom_flattening.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_dlq_guard.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_input_processing.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_interaction_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_linguistics.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_matrix_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_metadata.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_passivity_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_references.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_validation.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_google_providers_separation.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_report_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`
- `[MODIFY] @[backend_v2/tests/unit/core/test_hook_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_concurrency_fuzzer.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dependencies.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_factory.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_finops_telemetry.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_handler.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_input_processing.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_interfaces.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_llm_context_bounds.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_llm_dependency.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_logic.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_main.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_metadata.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_metrics.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_references.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_repo_deletion.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_repositories_v2.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_usage_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker_dlq_fallback.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_epic_chain_e2e.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`

## Phase 1 Deprecations & Sunset Symbols

<demolish>
- `StorageDriver`
- `PostgresStorageDriver`
- `AppendOnlyRepositoryBase`
- `KnowledgeRepositoryImpl`
- `ComponentRepositoryImpl`
- `AgentRepositoryImpl`
- `RoleRepositoryImpl`
- `TaskBlueprintRepositoryImpl`
- `MatrixRepositoryImpl`
- `ExecutionPersonaRepositoryImpl`
- `ExtractionProtocolRepositoryImpl`
- `IKnowledgeRepository`
- `IComponentRepository`
- `IAgentRepository`
- `IRoleRepository`
- `ITaskBlueprintRepository`
- `IMatrixRepository`
- `IExecutionPersonaRepository`
- `IExtractionProtocolRepository`
- `InMemoryKnowledgeRepository`
- `InMemoryComponentRepository`
- `InMemoryAgentRepository`
- `InMemoryRoleRepository`
- `InMemoryTaskBlueprintRepository`
- `InMemoryMatrixRepository`
- `InMemoryExecutionPersonaRepository`
- `InMemoryExtractionProtocolRepository`
- `SystemSettingsDTO`
- `UsageAggregateDTO`
- `UsageAggregateUpdateDTO`
- `get_collection_document_row`
- `upsert_collection_document_row`
- `delete_collection_document_row`
- `list_collection_document_rows`
- `list_collection_documents_rows`
- `clear_collection_document_rows`
- `clear_collection_documents_rows`
- `get_collection_document`
- `upsert_collection_document`
- `delete_collection_document`
- `list_collection_documents`
- `clear_collection_documents`
- `_upsert_usage_aggregates`
- `upsert_usage_aggregate`
- `get_usage_aggregate`
- `get_system_settings`
- `update_system_settings`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L344-L351]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L219-L269]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L259-L319]`, `@[backend_v2/database/postgres/graph_adapter.py#L360-L465]`, `@[backend_v2/database/postgres/graph_adapter.py#L239-L250]`, `@[backend_v2/database/postgres/graph_adapter.py#L253-L297]` & `@[backend_v2/database/postgres/graph_adapter.py#L468-L761]` | Unwrapped `.model_validate()` calls across 12 entity hydrators, `else: SystemRulePromptBlock` fallthrough in `hydrate_prompt_block_row`, generic `Exception -> STORAGE_ACCESS_FAILED` masking of PostgreSQL `SQLSTATE 23503` / `23505`, `getattr`/`hasattr` SQLSTATE probing (`QGR001`), and `ON CONFLICT DO NOTHING` in `_MATERIALIZE_WAVE_SQL`. | Implement SSOT `validate_hydrated_row[M](validator: type[M] | TypeAdapter[M], payload, *, table_name: str, entity_id: str) -> M` (catching `ValidationError` -> RFC 7807 `logger.error` + `AppException(..., ErrorCodes.VALIDATION_FAILED.value, status_code=500)`), preserve `PromptBlockCategory` column projection for `extra="forbid"` before `PromptBlockAdapter` validation, implement `translate_postgres_exception` via `@runtime_checkable class _SqlStateCarrier(Protocol)` (`23503` on `DELETE` -> HTTP 400 `DELETE_BLOCKED_BY_USAGE`, `23503` on `INSERT`/`UPDATE` -> HTTP 422 `VALIDATION_FAILED`, `23505` -> HTTP 409 `CONFLICT`), and use `DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`. | Centralize hydration and exception translation in `coercion_and_constants.py` with zero per-table try/except copy-paste and zero top-level `asyncpg` exception coupling (`ZORM001`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/ backend_v2/tests/unit/database/postgres/entity_adapter/ backend_v2/tests/unit/database/test_postgres.py --test --ast-strict` |
| `@[backend_v2/services/studio/prompt_block_service.py#L31-L320]`, `@[backend_v2/services/studio/workflow_service.py#L657-L720]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, `@[backend_v2/services/studio/system_config_service.py#L44-L817]`, `@[backend_v2/api/dependencies.py#L317-L330]` & `@[backend_v2/tests/conftest.py]` | Payload-only RBAC checks enabling cross-tenant `PUT` IDOR hijack, client-defined ID creation via `PUT /{id}`, inverted FK insertion order in `clone_workflow`, missing `uow_factory` in `StudioWorkflowService` causing multi-autocommit tears, hyphenated `-copy` slugs, mixed Finnish `"New Työnkulku"`/`"New Askel"` strings, and `list`/`get` RBAC asymmetry. | Enforce 4-Phase In-Place Upsert across all Studio services including `StudioSystemConfigService` (`existing is None -> ResourceNotFoundError`, `enforce_modification_rights(initiator, existing.organization_id)`, preserve `existing.organization_id` for non-`ROOT`, private `_insert_validated_*` for draft/clone), inject `uow_factory: UnitOfWorkFactory | None = None` into `StudioWorkflowService` for single `async with uow:` parent-before-child `clone_workflow` / `save_workflow` / `delete_workflow`, preserve informational `original.slug` (`{original.slug}_copy` on `MCPGateway`), use pure English literals, and enforce symmetric `ROOT`/`ADMIN` read RBAC rejecting `MANAGER`, `MEMBER`, and `VIEWER` (`403`). | No separate revision history tables for Studio drafts; preserve single-row `JSONB` canvas saves inside one `QuorumUnitOfWork` transaction. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/tests/conftest.py backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/api/routers/studio/ --test --ast-strict` |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/interfaces.py#L360-L360]`, `@[backend_v2/models/domain/base.py#L394-L476]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/database/repositories/audit.py#L166-L187]`, `@[backend_v2/services/usage_service.py#L24-L418]`, `@[backend_v2/services/auth/secret_service.py#L140-L1170]` & `@[scripts/audit_zero_orm_strictness.py#L432-L452]` | Volatile process-RAM `"audit_logs"`, `"usage"`, and mutable shadow `"usage_aggregates"` counters (`UsageAggregateDTO`, `UsageAggregateUpdateDTO`, `get_usage_aggregate`), `SystemConfigUpdateDTO.system_settings` (`SystemSettingsDTO`), silent `if org:` skip in `UsageService.get_usage_report`, `SecretService` calling `delete_collection_document`, and `verify_seed_table_counts_rows` calling `list_collection_documents_rows`. | Create append-only UUIDv7 PostgreSQL 19 tables `audit_logs` (`aud_`, `AuditLogRecord` preserving `AuditLogEntry` on `Metadata`) and `usage_records` (`usg_`, preserving full FinOps columns `cache_creation_input_tokens`, `latency_ms`, `finish_reason`, `system_fingerprint`, `estimated_savings_usd`, and system-safe nullable FK bindings) with `VIRTUAL` `created_at`, add typed `insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `list_usage_records`, `aggregate_organization_usage` (`UsageRollupSummaryDTO`), and `delete_tenant_secret` on `EntityPersistencePort`, register the 18-table topology in `audit_zero_orm_strictness.py`, and raise `ResourceNotFoundError` (`404`) when `get_organization(org_id)` is `None`. | Compute FinOps usage totals directly via indexed SQL `SUM(...)` / `COUNT(*)` over `usage_records` without secondary counter tables. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/base.py backend_v2/models/dtos/system.py backend_v2/models/enums.py backend_v2/database/repositories/audit.py backend_v2/services/usage_service.py backend_v2/services/auth/secret_service.py scripts/audit_zero_orm_strictness.py backend_v2/tests/factories/ backend_v2/tests/unit/models/domain/test_base.py backend_v2/tests/unit/models/dtos/test_system.py backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py backend_v2/tests/unit/services/auth/test_secret_service.py backend_v2/tests/unit/test_usage_service.py backend_v2/tests/unit/test_finops_telemetry.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict` |
| `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `@[backend_v2/database/repository.py#L19-L35]`, `@[backend_v2/database/factory.py#L77-L112]`, `@[backend_v2/services/report/compilation_service.py#L33-L299]`, `@[backend_v2/api/dependencies.py#L317-L330]`, `@[backend_v2/models/enums.py#L274-L277]` & `@[scripts/_ast_guardrails.py]` | Generic `StorageDriver` / `PostgresStorageDriver` (`self._collections` RAM fallback), `AppendOnlyRepositoryBase` (`_v2` ID corruption), `StorageBackend.FIRESTORE`/`LOCAL`, `data/workflows/*.json` disk fallbacks, 8 dead V1 ghost repositories/protocols, dead `comp_repo` pass-throughs (including 7-arg `BlueprintTransformer` call in `compilation_service.py`), stale `storage_driver.py` entry in `BOUNDARY_EXEMPTION_FILES`, and `TD_ISTQB_NEGATIVE` in `test_repositories_v2.py`. | Route all 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade directly through the complete typed `EntityPersistencePort` surface, lock `StorageBackend` exclusively to `POSTGRES`, remove dead `comp_repo` parameters across services/orchestrator/tests, synchronize `_ast_guardrails.py` (`BOUNDARY_EXEMPTION_FILES`, `_QGR030_ENTITY_PREFIXES`), add ISTQB negative tests to `test_repositories_v2.py`, and delete all 11 legacy driver / V1 ghost production files and 12 companion test files. | Do NOT build a generic filter/ORM DSL and do NOT force ~95 worker/report/test callers to unpack 9 repository arguments; keep `UnifiedWorkflowRepository(uow_factory)` as a zero-storage-logic V2 composite facade. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ablation_live_executor.py scripts/audit_zero_orm_strictness.py scripts/_ast_guardrails.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L302-L316]`, `@[backend_v2/database/interfaces.py#L413-L426]`, `@[backend_v2/database/repository.py#L19-L35]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, and `@[backend_v2/services/usage_service.py#L24-L418]`.</action>
    <action>Look forward: Verify Step 1.1 establishes `validate_hydrated_row` and `translate_postgres_exception` across all entity hydrators, Step 1.2 hardens Studio 4-Phase In-Place Upserts, IDOR checks, and single-UoW `clone_workflow`, Step 1.3 adds `audit_logs` and `usage_records` on `EntityPersistencePort` and drops `usage_aggregates`, and Step 1.4 cuts over all 9 active repositories and `UnifiedWorkflowRepository(uow_factory)` onto `EntityPersistencePort` while deleting `StorageDriver`, `PostgresStorageDriver`, and all dead V1 ghost modules/tests.</action>
    <constraint invariant="orchestrator_god_object_fragility">Verify explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` authorization before editing `backend_v2/services/orchestrator/` files to strip dead `comp_repo: IComponentRepository | None` pass-throughs, and run the full `backend_audit_loop.py` gate.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/01_phase1_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>[DELETE] @[backend_v2/database/driver.py#L86-L207]</backend>
    <backend>[DELETE] @[backend_v2/database/postgres/storage_driver.py#L186-L556]</backend>
    <backend>[DELETE] @[backend_v2/models/domain/knowledge.py]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/knowledge.py#L30-L219]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/component.py#L17-L242]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/agent.py#L17-L163]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/role.py#L17-L145]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/task_blueprint.py#L18-L167]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/matrix.py#L18-L168]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/execution_persona.py#L18-L145]</backend>
    <backend>[DELETE] @[backend_v2/database/repositories/components/extraction_protocol.py#L18-L145]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/models/domain/test_knowledge_dtos.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/test_knowledge.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/test_component.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_agent.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_role.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_matrix.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_execution_persona.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/components/test_extraction_protocol.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/database/repositories/test_base.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/test_driver.py]</backend>
    <backend>[DELETE] @[backend_v2/tests/unit/test_storage_audit.py]</backend>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/database/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L302-L316]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L219-L269]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L259-L319]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py#L239-L250]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py#L253-L297]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py#L360-L465]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py#L468-L761]</backend>
    <backend>@[backend_v2/database/interfaces.py#L413-L426]</backend>
    <backend>@[backend_v2/database/factory.py#L77-L112]</backend>
    <backend>@[backend_v2/database/repository.py#L19-L35]</backend>
    <backend>@[backend_v2/database/repositories/__init__.py]</backend>
    <backend>@[backend_v2/database/repositories/components/__init__.py]</backend>
    <backend>@[backend_v2/database/repositories/base.py#L46-L66]</backend>
    <backend>@[backend_v2/database/repositories/audit.py#L25-L263]</backend>
    <backend>@[backend_v2/database/repositories/identity.py#L31-L388]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py#L26-L512]</backend>
    <backend>@[backend_v2/database/repositories/system.py#L20-L166]</backend>
    <backend>@[backend_v2/database/repositories/execution.py#L41-L440]</backend>
    <backend>@[backend_v2/database/repositories/report_artifact.py#L23-L148]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py#L16-L200]</backend>
    <backend>@[backend_v2/database/repositories/components/output_profile.py#L11-L98]</backend>
    <backend>@[backend_v2/database/repositories/components/task_brief.py#L11-L90]</backend>
    <backend>@[backend_v2/models/domain/base.py#L394-L476]</backend>
    <backend>@[backend_v2/models/dtos/system.py]</backend>
    <backend>@[backend_v2/models/enums.py#L274-L277]</backend>
    <backend>@[backend_v2/services/auth/secret_service.py#L140-L1170]</backend>
    <backend>@[backend_v2/services/usage_service.py#L24-L418]</backend>
    <backend>@[backend_v2/services/studio/prompt_block_service.py#L31-L320]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L49-L990]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py#L26-L369]</backend>
    <backend>@[backend_v2/services/studio/task_brief_service.py#L29-L279]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py#L44-L817]</backend>
    <backend>@[backend_v2/services/blueprint.py#L89-L1076]</backend>
    <backend>@[backend_v2/services/execution/facade.py#L69-L714]</backend>
    <backend>@[backend_v2/services/execution/override_service.py#L35-L482]</backend>
    <backend>@[backend_v2/services/report/__init__.py#L42-L297]</backend>
    <backend>@[backend_v2/services/report/compilation_service.py#L33-L299]</backend>
    <backend>@[backend_v2/services/report/format_reader_service.py#L22-L229]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/__init__.py#L77-L174]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py#L106-L129]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>@[backend_v2/worker.py]</backend>
    <backend>@[backend_v2/workers/report_worker.py]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py#L58-L79]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py#L155-L183]</backend>
    <backend>@[backend_v2/api/dependencies.py#L317-L330]</backend>
    <backend>@[backend_v2/main.py#L70-L115]</backend>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py#L432-L452]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/conftest.py]</backend>
    <backend>@[backend_v2/tests/fakes/__init__.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py#L1545-L1552]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L2001-L2012]</backend>
    <backend>@[backend_v2/tests/factories/__init__.py]</backend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/factories/test_model_factories.py]</backend>
    <backend>@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test___init__.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_postgres.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_repository.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/components/test_task_brief.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_audit.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_identity.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_report_artifact.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_workflow.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_base.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/services/auth/test_secret_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_workflow_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_system_config_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_compilation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_format_reader_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_override_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution_resumability.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_atom_flattening.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_dlq_guard.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_input_processing.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_interaction_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_linguistics.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_matrix_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_metadata.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_passivity_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_references.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_scoring.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_validation.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_google_providers_separation.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_report_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]</backend>
    <backend>@[backend_v2/tests/unit/core/test_hook_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/test_concurrency_fuzzer.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_taskgroup.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dependencies.py]</backend>
    <backend>@[backend_v2/tests/unit/test_factory.py]</backend>
    <backend>@[backend_v2/tests/unit/test_finops_telemetry.py]</backend>
    <backend>@[backend_v2/tests/unit/test_handler.py]</backend>
    <backend>@[backend_v2/tests/unit/test_input_processing.py]</backend>
    <backend>@[backend_v2/tests/unit/test_interfaces.py]</backend>
    <backend>@[backend_v2/tests/unit/test_llm_context_bounds.py]</backend>
    <backend>@[backend_v2/tests/unit/test_llm_dependency.py]</backend>
    <backend>@[backend_v2/tests/unit/test_logic.py]</backend>
    <backend>@[backend_v2/tests/unit/test_main.py]</backend>
    <backend>@[backend_v2/tests/unit/test_metadata.py]</backend>
    <backend>@[backend_v2/tests/unit/test_metrics.py]</backend>
    <backend>@[backend_v2/tests/unit/test_references.py]</backend>
    <backend>@[backend_v2/tests/unit/test_repo_deletion.py]</backend>
    <backend>@[backend_v2/tests/unit/test_repositories_v2.py]</backend>
    <backend>@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/test_usage_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_dlq_fallback.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]</backend>
    <backend>@[backend_v2/tests/integration/test_epic_chain_e2e.py]</backend>
    <backend>@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`validate_hydrated_row` and `translate_postgres_exception` (using `@runtime_checkable class _SqlStateCarrier(Protocol)`) in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L344-L351]` wrap 100% of entity hydrators and SQL mutation/delete helpers, mapping `ValidationError` -> HTTP 500 `ErrorCodes.VALIDATION_FAILED`, `SQLSTATE 23503` on `DELETE` -> HTTP 400 `ErrorCodes.DELETE_BLOCKED_BY_USAGE`, `SQLSTATE 23503` on `INSERT`/`UPDATE` -> HTTP 422 `ErrorCodes.VALIDATION_FAILED`, and `SQLSTATE 23505` -> HTTP 409 `ErrorCodes.CONFLICT` with structured RFC 7807 `logger.error`.</item>
    <item>All Studio `save_*` methods across `@[backend_v2/services/studio/prompt_block_service.py#L31-L320]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, and `@[backend_v2/services/studio/system_config_service.py#L44-L817]` enforce the 4-Phase In-Place Upsert Protocol (`existing is None -> raise ResourceNotFoundError`, `enforce_modification_rights(initiator, existing.organization_id)` before payload inspection, `existing.organization_id` preservation for non-`ROOT`), `StudioWorkflowService` injects `uow_factory: UnitOfWorkFactory | None = None` so `clone_workflow`, `save_workflow`, and `delete_workflow` execute atomically inside one `async with uow:` transaction, Studio clones preserve informational `original.slug` (`{original.slug}_copy` on `MCPGateway`), mixed Finnish code literals are replaced with English, and `StudioSystemConfigService` enforces symmetric `ROOT`/`ADMIN` read RBAC rejecting `MANAGER`, `MEMBER`, and `VIEWER` (`403`).</item>
    <item>Append-only `audit_logs` (`aud_`, `AuditLogRecord` preserving `AuditLogEntry` on `Metadata`) and `usage_records` (`usg_`, preserving full FinOps columns) tables and `EntityPersistencePort` methods (`insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `list_usage_records`, `aggregate_organization_usage` returning `UsageRollupSummaryDTO`, `delete_tenant_secret`) are live, `audit_zero_orm_strictness.py` registers the 18-table topology and adapter columns, and `usage_aggregates`, `UsageAggregateDTO`, `UsageAggregateUpdateDTO`, `get_usage_aggregate`, and `SystemSettingsDTO` are deleted.</item>
    <item>All 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade operate 100% on `EntityPersistencePort`, `StorageBackend` is locked exclusively to `POSTGRES`, dead `comp_repo` pass-throughs (including `ReportCompilationService`'s `BlueprintTransformer` call) are removed, `_ast_guardrails.py` ratchets (`BOUNDARY_EXEMPTION_FILES`, `_QGR030_ENTITY_PREFIXES`) and `TD_ISTQB_NEGATIVE` in `test_repositories_v2.py` are resolved, and all 11 legacy driver / V1 ghost production modules plus 12 companion test files are physically deleted.</item>
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
    <anti_target>Do NOT build a generic dynamic filter or ORM query DSL (`Filter`, `QueryCondition`, `FilterOperator`, `SortOrder`); expose explicit domain-typed query methods on `EntityPersistencePort`.</anti_target>
    <anti_target>Do NOT delete `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` in `@[backend_v2/database/repository.py#L19-L35]`; retain it strictly as a zero-storage-logic V2 composite protocol facade over the 9 active `EntityPersistencePort`-backed repositories.</anti_target>
    <anti_target>Do NOT overwrite `slug = new_id` on Studio entity clones (`Workflow`, `Step`, `PromptBlock`, `OutputProfile`, `TaskBrief`, `ModelRegistry`); preserve `original.slug` as non-unique informational metadata and `{original.slug}_copy` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones.</anti_target>
    <anti_target>Do NOT mutate or delete `AuditLogEntry` in `@[backend_v2/models/domain/base.py#L35-L50]` (`Metadata.audit_logs` embeds `AuditLogEntry` step-level records); introduce a dedicated frozen `AuditLogRecord(V2CoreBase)` model for the `audit_logs` PostgreSQL 19 ledger table and preserve all FinOps telemetry columns on `UsageRecord` (`feature_sovereignty_mandate`).</anti_target>
  </anti_targets>

  <step id="1.1" name="Unified Fail-Fast Hydrator (validate_hydrated_row) &amp; SQLSTATE Exception Translation Gate (translate_postgres_exception)">
    <action>1. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L344-L351]`: Implement PEP 695 `validate_hydrated_row[M](validator: type[M] | TypeAdapter[M], payload: object, *, table_name: str, entity_id: str) -> M` invoking `validator.validate_python(payload, strict=False)` when `isinstance(validator, TypeAdapter)` or `validator.model_validate(payload, strict=False)` otherwise, catching Pydantic `ValidationError`, logging `logger.error` with `ErrorCodes.VALIDATION_FAILED.value`, `table_name`, and `entity_id`, and raising `AppException(message=..., status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "table_name": table_name, "entity_id": entity_id})` (`QGR009`). Define `@runtime_checkable class _SqlStateCarrier(Protocol)` (`sqlstate: str`) to extract PostgreSQL `SQLSTATE` codes via `isinstance(exc, _SqlStateCarrier)` without `getattr`/`hasattr` (`QGR001`) or top-level `asyncpg` imports (`ZORM001`), and implement `translate_postgres_exception(exc: Exception, *, operation: str, table_name: str, entity_id: str) -> AppException` mapping `SQLSTATE 23503` on `DELETE` to `AppException(..., status_code=400, details={"error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value, ...})`, `SQLSTATE 23503` on `INSERT`/`UPDATE` to `AppException(..., status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value, ...})`, `SQLSTATE 23505` to `AppException(..., status_code=409, details={"error_code": ErrorCodes.CONFLICT.value, ...})`, and all other database I/O exceptions to `AppException(..., status_code=500, details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, ...})`, always preceded by structured `logger.error` (`QGR033`).</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L148-L266]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L219-L269]`, and `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L218-L256]`: Enforce `validate_hydrated_row` and `translate_postgres_exception` (preceded by `except AppException: raise` per `ZORM003`) across all entity hydrators (`organization`, `user`, `invitation`, `tenant_secret`, `system_config`, `execution_assignment`, `prompt_block`, `step`, `workflow`, `output_profile`, `task_brief`, `execution`, `report_artifact`), `get_report_binary_row`, and SQL write/delete helpers. In `hydrate_prompt_block_row`, preserve variant-specific column projection keyed by `PromptBlockCategory` enum members (`MATRIX`, `EXECUTION_PERSONA`/`AGENT_ROLE`, `PROTOCOL`, `SYSTEM_RULE`/`RUNTIME_VARIABLES`, passing the unprojected base payload when `category_id` is unrecognized so `PromptBlockAdapter` rejects unknown categories with `ValidationError`) so `ConfigDict(strict=True, extra="forbid", frozen=True)` never receives sibling-variant `NULL` columns, then validate via `validate_hydrated_row(PromptBlockAdapter, projected_payload, table_name="prompt_blocks", entity_id=blk_id)` with zero `else: SystemRulePromptBlock` fallback. Validate `Workflow.steps` (`list[StepRule]`) via a module-level `_STEP_RULE_LIST_ADAPTER: TypeAdapter[list[StepRule]] = TypeAdapter(list[StepRule])` passed into `validate_hydrated_row`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/database/postgres/graph_adapter.py#L253-L297]`, `@[backend_v2/database/postgres/graph_adapter.py#L253-L297]`, `@[backend_v2/database/postgres/graph_adapter.py#L253-L297]`, and `@[backend_v2/database/postgres/graph_adapter.py#L253-L297]`: Route `_hydrate_payload_dto`, `_hydrate_proposition_node`, and `CteReasoningStrategy.find_falsified_claims` (`FalsifiedClaimMatch`) through `validate_hydrated_row`, route graph SQL mutation error handlers through `translate_postgres_exception`, and replace `ON CONFLICT (run_id, source_id, target_id, relation_type) DO NOTHING RETURNING edge_id` in `_MATERIALIZE_WAVE_SQL` with `ON CONFLICT (run_id, source_id, target_id, relation_type) DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, and `@[backend_v2/tests/unit/database/test_postgres.py]`: Add positive, negative, and boundary unit tests verifying `validate_hydrated_row` (`ValidationError` -> `ErrorCodes.VALIDATION_FAILED` HTTP 500), `PromptBlockAdapter` rejection of unknown `category_id` while projecting valid `MatrixPromptBlock` / `SystemRulePromptBlock` rows cleanly under `extra="forbid"`, `translate_postgres_exception` (`23503` on `DELETE` -> `DELETE_BLOCKED_BY_USAGE` 400, `23503` on `INSERT`/`UPDATE` -> `VALIDATION_FAILED` 422, `23505` -> `CONFLICT` 409, transport error -> `STORAGE_ACCESS_FAILED` 500), and idempotent `_MATERIALIZE_WAVE_SQL` edge weight updates.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every `AppException` produced by `validate_hydrated_row` and `translate_postgres_exception` MUST log `logger.error` with `error_code`, `table_name`, and `entity_id` before raising, using inline `ErrorCodes.&lt;MEMBER&gt;.value` literals (`QGR009`).</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/ backend_v2/tests/unit/database/postgres/entity_adapter/ backend_v2/tests/unit/database/test_postgres.py --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="Studio Multi-Tenant IDOR Closure, 4-Phase In-Place Upsert, Single-UoW clone_workflow &amp; RBAC Symmetry">
    <action>1. `[MODIFY]` `@[backend_v2/services/studio/prompt_block_service.py#L171-L196]`, `@[backend_v2/services/studio/workflow_service.py#L386-L412]`, `@[backend_v2/services/studio/output_profile_service.py#L227-L252]`, `@[backend_v2/services/studio/task_brief_service.py#L182-L207]`, and `@[backend_v2/services/studio/system_config_service.py#L350-L368]`: Refactor `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, `save_task_brief`, `save_system_config`, and `save_mcp_gateways` to enforce the 4-Phase In-Place Upsert Protocol: (a) fetch `existing` by `id` first and raise `ResourceNotFoundError` (`404`) if `existing is None`, (b) verify `enforce_modification_rights(initiator, existing.organization_id)` (or `self._require_root` / tenant gateway ownership in `StudioSystemConfigService`) on `existing` before inspecting the incoming payload, (c) preserve `existing.organization_id` for non-`ROOT` callers, and (d) extract private `_insert_validated_*` helpers invoked exclusively by `create_*_draft` and `clone_*`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/api/dependencies.py#L624-L652]`, and `@[backend_v2/tests/conftest.py]`: Inject `uow_factory: UnitOfWorkFactory | None = None` into `StudioWorkflowService` (wired via `get_studio_workflow_service` in `dependencies.py` and `conftest.py`) and propagate the active UoW session context across `workflow_repo` and `output_profile_repo` so `clone_workflow` executes inside a single `async with uow:` transaction with parent-before-child FK ordering: (a) insert cloned `Workflow` with `default_profile_id=None`, (b) insert cloned `OutputProfile` rows referencing `workflow_id=new_id`, and (c) update `Workflow.default_profile_id` to the cloned default profile UUID. Execute `save_workflow` + `_sync_output_profiles_for_workflow` and `delete_workflow` each inside a single atomic `async with uow:` transaction boundary. Preserve informational `original.slug` on Studio clones (`PromptBlock`, `Workflow`, `Step`, `OutputProfile`, `TaskBrief`) and replace mixed Finnish strings (`"New Työnkulku"` -> `"New Workflow"`, `"New Askel"` -> `"New Step"`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/services/studio/system_config_service.py#L370-L424]`: Preserve informational `original.slug` on `ModelRegistry` clones, keep `{original.slug}_copy` / `{original.slug}_copy_N` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones (banning hyphenated `-copy`), enforce `self._require_root(initiator)` on `create_system_config_draft`, and enforce symmetric `ROOT`/`ADMIN` read RBAC across `get_system_config`, `list_system_configs`, `get_mcp_gateways`, and `list_mcp_gateways` via `if initiator.role not in (UserRole.ROOT, UserRole.ADMIN):` raising `PermissionDeniedError` (`403`) for `UserRole.MANAGER`, `UserRole.MEMBER`, and `UserRole.VIEWER`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`, `@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`, `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`, `@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]`, and `@[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]`: Update pre-existing tests that called `save_*` without seeding `existing` first or asserted hyphenated `-copy` / mutated `slug = new_id` or `VIEWER` read access, and add unit tests using Polyfactory models (`TaskBriefFactory.build(...)`, `WorkflowFactory.build(...)`) verifying cross-tenant `PUT` IDOR rejection (`403`), unknown-ID `PUT` rejection (`404`), non-`ROOT` `organization_id` preservation, symmetric `MANAGER`/`MEMBER`/`VIEWER` `403` rejection, and single-UoW `clone_workflow` parent-before-child ordering.</action>
    <constraint invariant="in_place_upsert_standard_mandate">Public `save_*` methods MUST NEVER insert new rows when `existing is None` or evaluate RBAC solely against untrusted payload `organization_id`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/tests/conftest.py backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/api/routers/studio/ --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="Append-Only PostgreSQL 19 audit_logs &amp; usage_records Ledgers, SQL FinOps Rollups &amp; delete_tenant_secret">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/enums.py#L246-L271]`, and `@[scripts/audit_zero_orm_strictness.py#L432-L452]`: Add `audit_logs` (`EntityPrefix.AUDIT_LOG = "aud"`) and `usage_records` (`EntityPrefix.USAGE_RECORD = "usg"`) UUIDv7 tables (including full FinOps columns `cache_creation_input_tokens`, `latency_ms`, `finish_reason`, `system_fingerprint`, `estimated_savings_usd`, nullable `organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE`, and updated `DROP TABLE IF EXISTS` ordering) with `VIRTUAL` `created_at` and B-Tree indexes (`idx_audit_logs_org_created`, `idx_audit_logs_execution_id`, `idx_usage_records_org_created`, `idx_usage_records_execution_id`). Lock `StorageBackend` in `@[backend_v2/models/enums.py#L246-L271]` exclusively to `POSTGRES` (dropping `FIRESTORE` and `LOCAL`). Register `"audit_logs"` and `"usage_records"` in `CANONICAL_ENTITY_PK_TABLES` and `CLOSED_POSTGRES_TABLES` and register all `audit_logs`, `usage_records`, and SQL rollup column names in `APPROVED_ADAPTER_RECORD_COLUMNS` inside `@[scripts/audit_zero_orm_strictness.py#L432-L452]` so Macro Stage 10 (`ZORM004` and `ZORM006`) passes deterministically.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/interfaces.py#L296-L383]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L926-L948]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`, and `@[backend_v2/tests/fakes/in_memory_uow.py#L1215-L1250]`: Add typed `EntityPersistencePort` methods `insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `list_usage_records`, `aggregate_organization_usage` (returning `UsageRollupSummaryDTO`), and `delete_tenant_secret` (coercing sentinel non-UUID `"system"` `actor_id`/`user_id` values to `None` on UUID FK columns). Switch `verify_seed_table_counts_rows` in `seed_and_collection_stage.py` from `list_collection_documents_rows(conn, timeout, "system_configs")` to `list_system_configs_rows(conn, timeout)`, and delete all generic collection document functions (`get_collection_document_row`, `upsert_collection_document_row`, `delete_collection_document_row`, `list_collection_document_rows`, `list_collection_documents_rows`, `clear_collection_document_rows`, `clear_collection_documents_rows`, `get_collection_document`, `upsert_collection_document`, `delete_collection_document`, `list_collection_documents`, `clear_collection_documents`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/models/domain/base.py#L35-L50]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/database/repositories/audit.py#L25-L263]`, `@[backend_v2/services/usage_service.py#L24-L418]`, and `@[backend_v2/services/auth/secret_service.py#L140-L1170]`: Keep `AuditLogEntry` untouched for `Metadata.audit_logs` and introduce frozen `AuditLogRecord(V2CoreBase)`, updated `AuditLogCreateDTO`, and `UsageRollupSummaryDTO(BaseDTO)` in `models/domain/base.py` while updating `UsageRecord.id` to canonical `usg_<hex32>` UUIDv7 (`OPAQUE_STRIPE_ID_REGEX`). Drop `UsageAggregateDTO`, `UsageAggregateUpdateDTO`, `SystemSettingsDTO`, `SystemConfigUpdateDTO.system_settings` (in `models/dtos/system.py`), `get_usage_aggregate` (from `IAuditRepository` and `audit.py`), `upsert_usage_aggregate`, and `_upsert_usage_aggregates`. Route `AuditRepositoryImpl` and `UsageService` (`get_usage_report` and `check_quota`, resolving `Organization` via `identity_repo.get_organization(org_id)` and raising `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)` when `None`) directly through `EntityPersistencePort`, and route `SecretService.delete_tenant_secret` through `entity_adapter.delete_tenant_secret(secret_id)`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/factories/__init__.py]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/factories/test_model_factories.py]`, `@[backend_v2/tests/unit/models/domain/test_base.py]`, `@[backend_v2/tests/unit/models/dtos/test_system.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`, `@[backend_v2/tests/unit/database/test_postgres.py]`, `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/test_usage_service.py]`, `@[backend_v2/tests/unit/test_finops_telemetry.py]`, and `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`: Add `AuditLogRecordFactory` and `UsageRecordFactory` (registered in `factories/__init__.py` and `ALL_FACTORIES` in `test_model_factories.py`), update `test_schema_dto_naming_parity` in `test_postgres.py` and `test_audit_zero_orm_strictness.py` to the 18-table topology, remove obsolete generic collection document tests, and add positive/negative/boundary unit tests for `audit_logs`, `usage_records`, `aggregate_organization_usage`, `UsageService` 404 org verification, and `delete_tenant_secret`.</action>
    <constraint invariant="universal_ssot_and_normalization_mandate">FinOps usage totals MUST be computed exclusively via parameterized SQL `SUM(...)` / `COUNT(*)` over append-only `usage_records` with zero secondary shadow counter tables and 100% preservation of `UsageRecord` FinOps columns (`feature_sovereignty_mandate`).</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/base.py backend_v2/models/dtos/system.py backend_v2/models/enums.py backend_v2/database/repositories/audit.py backend_v2/services/usage_service.py backend_v2/services/auth/secret_service.py scripts/audit_zero_orm_strictness.py backend_v2/tests/factories/ backend_v2/tests/unit/models/domain/test_base.py backend_v2/tests/unit/models/dtos/test_system.py backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py backend_v2/tests/unit/database/test_postgres.py backend_v2/tests/unit/services/auth/test_secret_service.py backend_v2/tests/unit/test_usage_service.py backend_v2/tests/unit/test_finops_telemetry.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict</audit_command>
  </step>

  <step id="1.4" name="Direct EntityPersistencePort Repository Cutover, StorageDriver &amp; Dead V1 Ghost Repository Eradication">
    <action>1. `[MODIFY]` `@[backend_v2/database/interfaces.py#L296-L383]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L741-L1887]`, `@[backend_v2/database/repository.py#L19-L35]`, `@[backend_v2/database/factory.py#L77-L112]`, `@[backend_v2/database/__init__.py]`, `@[backend_v2/database/postgres/__init__.py]`, `@[backend_v2/database/repositories/__init__.py]`, `@[backend_v2/database/repositories/components/__init__.py]`, `@[backend_v2/database/repositories/base.py#L46-L66]`, `@[backend_v2/database/repositories/identity.py#L221-L231]`, `@[backend_v2/database/repositories/workflow.py#L266-L276]`, `@[backend_v2/database/repositories/system.py#L73-L83]`, `@[backend_v2/database/repositories/execution.py#L370-L380]`, `@[backend_v2/database/repositories/report_artifact.py#L61-L74]`, `@[backend_v2/database/repositories/components/prompt_block.py#L151-L200]`, `@[backend_v2/database/repositories/components/output_profile.py#L85-L98]`, and `@[backend_v2/database/repositories/components/task_brief.py#L77-L90]`: Expose the complete typed CRUD/list method surface on `EntityPersistencePort`, `PostgresEntityAdapter`, and `InMemoryEntityAdapter` (specifically and exhaustively: `get_user_by_email`, `delete_organization`, `delete_user`, `delete_invitation`, `delete_tenant_secret`, `list_system_configs`, `delete_system_config`, `list_prompt_blocks`, `delete_prompt_block`, `list_task_briefs`, `delete_task_brief`, `list_output_profiles`, `delete_output_profile`, `list_workflows`, `delete_workflow`, `list_steps`, `delete_step`, `list_executions`, `update_execution_occ`, `delete_execution`, `list_report_artifacts_by_execution`, `delete_report_artifact`, `insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `list_usage_records`, and `aggregate_organization_usage`). Migrate all 9 active V2 repositories (`Workflow`, `Execution`, `ReportArtifact`, `PromptBlock`, `TaskBrief`, `OutputProfile`, `Identity`, `Audit`, `System`) and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade from `StorageDriver` onto `UnitOfWorkFactory` / `EntityPersistencePort` (supporting active UoW session propagation for multi-repository transactions). Delete `AppendOnlyRepositoryBase` from `base.py`, drop `get_system_settings` and `update_system_settings` from `system.py`, drop `data/workflows/*.json` disk fallbacks and embedded-step fallback scans from `workflow.py`, execute `delete_org_data` (`DELETE FROM organizations WHERE id = $1`) in `identity.py` inside one atomic `async with uow:` block, fix `ExecutionRepositoryImpl` filter bindings (`created_by`, `ExecutionStatus.COMPLETED`), and stop stripping `mcp_tool_audit` into phantom `"executions/{id}/audit_trails"` subcollections.</action>
    <action>2. `[MODIFY]` `@[backend_v2/api/dependencies.py#L317-L330]`, `@[backend_v2/main.py#L70-L115]`, `@[backend_v2/services/blueprint.py#L89-L1076]`, `@[backend_v2/services/execution/facade.py#L69-L714]`, `@[backend_v2/services/execution/override_service.py#L35-L482]`, `@[backend_v2/services/report/__init__.py#L42-L297]`, `@[backend_v2/services/report/compilation_service.py#L33-L299]`, `@[backend_v2/services/report/format_reader_service.py#L22-L229]`, `@[backend_v2/services/orchestrator/dag_executor/__init__.py#L77-L174]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`, `@[backend_v2/services/orchestrator/strategies/base.py#L106-L129]`, `@[backend_v2/services/orchestrator/strategies/logic.py]`, `@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`, `@[backend_v2/core/hook_registry.py]`, `@[backend_v2/llm/handler.py]`, `@[backend_v2/worker.py]`, `@[backend_v2/workers/report_worker.py]`, `@[backend_v2/workers/synthesis_reducers.py#L58-L79]`, `@[backend_v2/workers/synthesis_worker.py#L155-L183]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/audit_zero_orm_strictness.py#L1153-L1180]`, and `@[scripts/_ast_guardrails.py]`: Remove all `get_driver`, `StorageDriver`, dead V1 ghost repository DI bindings (`IKnowledgeRepository`, `IComponentRepository`, `IAgentRepository`, `IRoleRepository`, `ITaskBlueprintRepository`, `IMatrixRepository`, `IExecutionPersonaRepository`, `IExtractionProtocolRepository`), dead `comp_repo` constructor pass-throughs (including updating `BlueprintTransformer(...)` in `compilation_service.py` from 7 positional arguments to 6), dead V1 `LLMHandler` model-lookup helpers, and legacy `data/workflows` / `execution_trace_storage_path` startup checks in `main.py`. Remove `"backend_v2/database/postgres/storage_driver.py"` from `BOUNDARY_EXEMPTION_FILES` in `_ast_guardrails.py` and from `_is_adapter_file` in `audit_zero_orm_strictness.py`, and add `"aud"` and `"usg"` to `_QGR030_ENTITY_PREFIXES` in `_ast_guardrails.py`.</action>
    <action>3. `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `[DELETE]` `@[backend_v2/models/domain/knowledge.py]`, `[DELETE]` `@[backend_v2/database/repositories/knowledge.py#L30-L219]`, `[DELETE]` `@[backend_v2/database/repositories/component.py#L17-L242]`, `[DELETE]` `@[backend_v2/database/repositories/components/agent.py#L17-L163]`, `[DELETE]` `@[backend_v2/database/repositories/components/role.py#L17-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/task_blueprint.py#L18-L167]`, `[DELETE]` `@[backend_v2/database/repositories/components/matrix.py#L18-L168]`, `[DELETE]` `@[backend_v2/database/repositories/components/execution_persona.py#L18-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/extraction_protocol.py#L18-L145]`, `[DELETE]` `@[backend_v2/tests/unit/models/domain/test_knowledge_dtos.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_knowledge.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_component.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_agent.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_role.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_matrix.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_execution_persona.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_extraction_protocol.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_base.py]`, `[DELETE]` `@[backend_v2/tests/unit/test_driver.py]`, and `[DELETE]` `@[backend_v2/tests/unit/test_storage_audit.py]`: Physically delete all 11 legacy driver / dead V1 ghost production modules and their 12 companion unit test files.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/fakes/__init__.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py#L1101-L1572]`, `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`, `@[backend_v2/tests/unit/database/test___init__.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_task_brief.py]`, `@[backend_v2/tests/unit/database/repositories/test_audit.py]`, `@[backend_v2/tests/unit/database/repositories/test_execution.py]`, `@[backend_v2/tests/unit/database/repositories/test_identity.py]`, `@[backend_v2/tests/unit/database/repositories/test_report_artifact.py]`, `@[backend_v2/tests/unit/database/repositories/test_system.py]`, `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`, `@[backend_v2/tests/unit/database/repositories/test_workflow.py]`, `@[backend_v2/tests/unit/services/report/test_compilation_service.py]`, `@[backend_v2/tests/unit/services/report/test_format_reader_service.py]`, `@[backend_v2/tests/unit/services/test_report_service_synthesis_args.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_trace_event_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_base.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_logic.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_init.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]`, `@[backend_v2/tests/unit/hooks/test_atom_flattening.py]`, `@[backend_v2/tests/unit/hooks/test_atom_sampling_determinism.py]`, `@[backend_v2/tests/unit/hooks/test_dlq_guard.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_metadata.py]`, `@[backend_v2/tests/unit/hooks/test_passivity_hook.py]`, `@[backend_v2/tests/unit/hooks/test_references.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/hooks/test_validation.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`, `@[backend_v2/tests/unit/workers/test_report_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dict_eradication.py]`, `@[backend_v2/tests/unit/core/test_hook_registry.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_dependencies.py]`, `@[backend_v2/tests/unit/test_factory.py]`, `@[backend_v2/tests/unit/test_handler.py]`, `@[backend_v2/tests/unit/test_input_processing.py]`, `@[backend_v2/tests/unit/test_interfaces.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]`, `@[backend_v2/tests/unit/test_llm_dependency.py]`, `@[backend_v2/tests/unit/test_logic.py]`, `@[backend_v2/tests/unit/test_main.py]`, `@[backend_v2/tests/unit/test_metadata.py]`, `@[backend_v2/tests/unit/test_metrics.py]`, `@[backend_v2/tests/unit/test_references.py]`, `@[backend_v2/tests/unit/test_repo_deletion.py]`, `@[backend_v2/tests/unit/test_repositories_v2.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_dlq_fallback.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`, and `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`: Delete all 8 V1 `InMemory*Repository` classes from `in_memory_repositories.py`, align `InMemoryUnifiedWorkflowRepository` with the 9 active V2 repository protocols, remove `comp_repo=` and `get_driver` references across all unit and integration tests, update `test_ast_guardrails.py` and `test_audit_dict_eradication.py` for removed `driver.py` and `storage_driver.py`, and add ISTQB negative/failure test partitions (`test_*_failure` / `test_*_invalid`) to `test_repositories_v2.py` to resolve `TD_ISTQB_NEGATIVE`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">100% of persistence operations MUST flow through `EntityPersistencePort` (`QuorumUnitOfWork`) with zero `StorageDriver`, `PostgresStorageDriver`, or volatile RAM dictionary fallbacks.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ablation_live_executor.py scripts/audit_zero_orm_strictness.py scripts/_ast_guardrails.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_validate_hydrated_row_valid_model_returns_frozen_domain_instance" category="positive">
      <input>Valid `Workflow` row dictionary generated from `WorkflowFactory.build()` passed to `validate_hydrated_row(Workflow, payload, table_name="workflows", entity_id=wf.id)`</input>
      <expected>Returns frozen `Workflow` instance passing `ConfigDict(strict=True, extra="forbid", frozen=True)`</expected>
    </test>
    <test name="test_validate_hydrated_row_corrupt_payload_logs_and_raises_validation_failed" category="negative">
      <input>Corrupt database row payload with extra unrecognized key or invalid UUIDv7 prefix passed to `validate_hydrated_row` or `hydrate_prompt_block_row` (`category_id="corrupt_unknown"`)</input>
      <expected>Logs structured `logger.error` with `ErrorCodes.VALIDATION_FAILED` and raises `AppException` (`status_code=500`, `ErrorCodes.VALIDATION_FAILED`) with zero fallback to `SystemRulePromptBlock`</expected>
    </test>
    <test name="test_translate_postgres_exception_maps_23503_delete_to_delete_blocked_by_usage" category="error_path">
      <input>Simulated `_SqlStateCarrier` exception (`sqlstate="23503"`) passed to `translate_postgres_exception(..., operation="DELETE", table_name="prompt_blocks", entity_id=blk.id)`</input>
      <expected>Logs `logger.error` and returns `AppException` with `status_code=400` and `ErrorCodes.DELETE_BLOCKED_BY_USAGE`</expected>
    </test>
    <test name="test_translate_postgres_exception_maps_23505_unique_to_conflict_and_23503_insert_to_422" category="boundary">
      <input>Simulated `_SqlStateCarrier` unique violation (`sqlstate="23505"`) on `INSERT` and foreign key violation (`sqlstate="23503"`) on `UPDATE` passed to `translate_postgres_exception`</input>
      <expected>`23505` maps to `AppException(ErrorCodes.CONFLICT, status_code=409)` and `23503` on `UPDATE` maps to `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`</expected>
    </test>
    <test name="test_studio_save_workflow_cross_tenant_put_idor_raises_permission_denied" category="negative">
      <input>Persisted `WorkflowFactory.build(organization_id=org_b_id)` in `InMemoryUnitOfWork`; Tenant A `ADMIN` calls `save_workflow(initiator_a, wf_b.id, forged_payload_with_org_a)`</input>
      <expected>Fetches persisted `existing` first, rejects cross-tenant overwrite with `PermissionDeniedError` (`403`), and leaves `wf_b` unmodified</expected>
    </test>
    <test name="test_studio_save_methods_reject_client_invented_id_when_missing_with_404" category="boundary">
      <input>Caller invokes `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, `save_task_brief`, `save_system_config`, or `save_mcp_gateways` with a valid-format UUIDv7 ID that does not exist in `InMemoryUnitOfWork`</input>
      <expected>Raises `ResourceNotFoundError` (`404`) without inserting a client-defined primary ID</expected>
    </test>
    <test name="test_clone_workflow_executes_parent_before_child_atomically_in_single_uow" category="positive">
      <input>`WorkflowFactory.build()` with attached `OutputProfileFactory.build(workflow_id=wf.id)` cloned via `StudioWorkflowService.clone_workflow`</input>
      <expected>Inserts cloned `Workflow` (`default_profile_id=None`) before cloned `OutputProfile` rows and binds `default_profile_id` inside one `async with uow:` transaction while preserving `original.slug`</expected>
    </test>
    <test name="test_usage_service_get_usage_report_unknown_org_raises_resource_not_found" category="negative">
      <input>`UsageService.get_usage_report` called for a nonexistent `org_<hex32>` UUIDv7</input>
      <expected>Logs structured `logger.error` and raises `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)`</expected>
    </test>
    <test name="test_repositories_v2_occ_conflict_and_invalid_payload_failure" category="negative">
      <input>Persisted `ExecutionRecord` updated via `UnifiedWorkflowRepository(uow_factory)` with stale `expected_state_version` or invalid domain identifier in `test_repositories_v2.py`</input>
      <expected>Raises `AppException` (`status_code=409`, `ErrorCodes.CONFLICT`) or `ValidationError` and satisfies `TD_ISTQB_NEGATIVE` under `audit_technical_debt.py --strict`</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 1 backend &amp; static guardrail quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ scripts/ablation_live_executor.py scripts/audit_zero_orm_strictness.py scripts/_ast_guardrails.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
