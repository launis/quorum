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

**Overview:** Establish the single sovereign `EntityPersistencePort` (`QuorumUnitOfWork`) persistence pipeline across Quorum V2 by implementing unified Fail-Fast row hydration (`validate_hydrated_row`) and PostgreSQL `SQLSTATE` exception translation (`translate_postgres_exception`) in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`, closing cross-tenant `PUT` IDOR and multi-autocommit transactional tears across all Studio services (`@[backend_v2/services/studio/prompt_block_service.py#L31-L279]`, `@[backend_v2/services/studio/workflow_service.py#L47-L929]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L322]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L255]`, `@[backend_v2/services/studio/system_config_service.py#L44-L746]`), introducing append-only PostgreSQL 19 `audit_logs` (`aud_`) and `usage_records` (`usg_`) ledgers with SQL `SUM(...)` / `COUNT(*)` FinOps rollups, migrating all 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade (`@[backend_v2/database/repository.py#L25-L52]`) onto `EntityPersistencePort`, and permanently deleting the legacy Firestore-era `StorageDriver` / `PostgresStorageDriver` dictionary layer along with all 11 legacy driver / dead V1 ghost modules and their 10 companion test files.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

> [!IMPORTANT]
> **Pre-Flight Technical Debt & DAG Orchestrator Permission Gate (`orchestrator_god_object_fragility`):**
> * Pre-flight baseline verified `0` technical debt findings across target database/service modules and their 1-hop callers via `scripts/audit_technical_debt.py --include-one-hop` (`@[docs/epic/EPIC_165_audit_report.md]`).
> * Removing dead `comp_repo: IComponentRepository | None` constructor parameters from `@[backend_v2/services/orchestrator/dag_executor/__init__.py#L78-L177]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`, `@[backend_v2/services/orchestrator/strategies/base.py#L106-L132]`, `@[backend_v2/services/orchestrator/strategies/logic.py]`, and `@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]` requires explicit `"PERMISSION GRANTED to mutate DAG Orchestrator ecosystem"` prior to `/tier2-execute` (or invocation under `--full-auto` with explicit orchestrator permission), followed by the full `backend_audit_loop.py` gate.

## Phase 1 Forensic Context & Invariants (Verbatim from EPIC 165)

### First Principles & Current-to-Target Persistence Cutover Context
* Audited schema and driver sources: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `@[backend_v2/database/postgres/pool.py#L422-L652]`, `@[backend_v2/database/postgres/uow.py#L185-L435]`, and `@[scripts/audit_zero_orm_strictness.py#L407-L427]`.
* **Finding 1 [P0 CRITICAL] — Firestore-Era Generic `StorageDriver`, Silent Volatile RAM Fallback & Dead V1 Ghost Layer:**
  * Forensic anchors: `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]` (`type StorageDocument = dict[str, StorageValue]`, `backend_v2/database/driver.py#L1-L143`), `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L47-L76]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L218-L247]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L291-L324]` (`_CANONICAL_COLLECTION_ALIASES` and `self._collections` RAM fallback, `backend_v2/database/postgres/storage_driver.py#L1-L195`), `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L321-L362]` (`upsert_collection_document_row` swallowing `AppException`, `ValueError`, `KeyError`, `TypeError` and returning `False` with zero logging), `@[backend_v2/models/enums.py#L272-L277]` (`FIRESTORE` and `LOCAL` enum remnants alongside `POSTGRES`), and `@[backend_v2/api/dependencies.py#L327-L336]` (wiring V1 ghost repositories `KnowledgeRepositoryImpl`, `AgentRepositoryImpl`, `ComponentRepositoryImpl`, `TaskBlueprintRepositoryImpl`).
  * Active runtime failures eradicated in Phase 1: (1) cross-process loss of MCP grounding audit trails in `@[backend_v2/database/repositories/execution.py#L33-L110]` and `@[backend_v2/database/repositories/execution.py#L112-L218]`, (2) volatile compliance `"audit_logs"` and `"usage"` plus mutable shadow `"usage_aggregates"` in `@[backend_v2/database/repositories/audit.py#L26-L325]` and `@[backend_v2/services/usage_service.py#L25-L406]`, and (3) unmounted V1 ghost repositories `[DELETE]` `@[backend_v2/database/repositories/knowledge.py#L30-L219]`, `[DELETE]` `@[backend_v2/database/repositories/component.py#L17-L242]`, `[DELETE]` `@[backend_v2/database/repositories/components/agent.py#L17-L163]`, `[DELETE]` `@[backend_v2/database/repositories/components/role.py#L17-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/task_blueprint.py#L18-L167]`, `[DELETE]` `@[backend_v2/database/repositories/components/matrix.py#L18-L168]`, `[DELETE]` `@[backend_v2/database/repositories/components/execution_persona.py#L18-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/extraction_protocol.py#L18-L145]`, and `SystemRepositoryImpl.update_system_settings` (`doc_id="global_settings"` in `@[backend_v2/database/repositories/system.py#L198-L213]`, whereas `@[backend_v2/api/routers/system/configs.py#L71-L117]` serves static `StrictnessAnchor` enums only; `TokenService` is defined in `auth/` alongside `AuthService`).
* **Finding 2 [P0 CRITICAL] — Full-Table `SELECT *` Scans, Broken Repository Filter Keys & Legacy Disk Fallbacks:**
  * Forensic anchors: `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L424-L477]`, `@[backend_v2/database/repositories/execution.py#L428-L451]` (`user_id` vs `created_by`, lowercase `"completed"` vs `"COMPLETED"`, dead `matrix_id`), `@[backend_v2/services/execution/assignment_service.py#L762-L778]` and `@[backend_v2/services/execution/assignment_service.py#L1706-L1722]`, `@[backend_v2/database/repositories/workflow.py#L33-L67]`, and `@[backend_v2/main.py#L72-L130]` (legacy `data/workflows` and `execution_trace_storage_path` disk checks).
* **Finding 7 [P0 CRITICAL] — Complete Forensic Catalog of Silent Error Swallows (Sites 1–6, 9–12):**
  1. `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L293-L318]`: Drop `get_collection_document_row` (which caught `except AppException: return None`, disguising DB timeouts and corrupt rows as HTTP 404).
  2. `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L321-L362]`: Drop `list_collection_document_rows`, `upsert_collection_document_row`, `delete_collection_document_row`, and `clear_collection_document_rows`.
  3. `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`: Drop `PostgresStorageDriver` and `StorageDriver` completely.
  4. `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L209-L250]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`, `@[backend_v2/database/postgres/graph_adapter.py#L433-L754]`, and `@[backend_v2/database/repositories/identity.py#L28-L310]`: Enforce single SSOT `validate_hydrated_row(model_cls_or_adapter, payload, *, table_name: str, entity_id: str) -> T` catching `ValidationError` -> `logger.error` + `AppException(ErrorCodes.VALIDATION_FAILED, status_code=500)`.
  5. `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]`: Dispatch `hydrate_prompt_block_row` strictly through `PromptBlockAdapter.validate_python(payload, strict=False)` inside `validate_hydrated_row(...)` instead of falling through `else: SystemRulePromptBlock`.
  6. `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`: Centralize `translate_postgres_exception(exc, *, operation: str, table_name: str, entity_id: str) -> AppException` mapping `SQLSTATE 23503` on `DELETE` to HTTP 400 `ErrorCodes.DELETE_BLOCKED_BY_USAGE`, `SQLSTATE 23503` on `INSERT`/`UPDATE` to HTTP 422 `ErrorCodes.VALIDATION_FAILED`, `SQLSTATE 23505` to HTTP 409 `ErrorCodes.CONFLICT`, and transport/I/O errors to HTTP 500 `ErrorCodes.STORAGE_ACCESS_FAILED` (preceded by structured `logger.error`).
  9. `@[backend_v2/database/repositories/workflow.py#L30-L394]`: Drop `data/workflows/{id}.json` disk fallback, dead embedded-step scan in `get_step_by_id`, and `setdefault` dictionary hacks.
  10. `@[backend_v2/database/repositories/system.py#L25-L213]`: Drop `update_system_settings` and `get_system_settings` (along with `SystemSettingsDTO`) and `f"cfg_{config_data.type}"` non-UUIDv7 ID fallback.
  11. `@[backend_v2/database/postgres/graph_adapter.py#L433-L754]` (`_MATERIALIZE_WAVE_SQL`): Replace `ON CONFLICT (run_id, source_id, target_id, relation_type) DO NOTHING RETURNING edge_id` with `ON CONFLICT (run_id, source_id, target_id, relation_type) DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`.
  12. `@[backend_v2/services/usage_service.py#L25-L406]` & `@[backend_v2/database/repositories/identity.py#L28-L310]`: Compute `get_usage_report` and `check_quota` directly from `usage_records` via parameterized SQL `SUM(...)` / `COUNT(*)`; raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)` when `get_organization(org_id)` is `None`.
* **Finding 8 [P0 CRITICAL] — Studio Cross-Tenant IDOR Closure, 4-Phase In-Place Upsert, Single-UoW FK Ordering & Clone Hygiene:**
  * Enforce 4-Phase In-Place Upsert across `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, and `save_task_brief`: fetch `existing` first (`ResourceNotFoundError` 404 if missing), verify `enforce_modification_rights(initiator, existing.organization_id)` before reading payload, preserve `existing.organization_id` for non-`ROOT` callers, and route `create_*_draft` / `clone_*` through private `_insert_validated_*` helpers.
  * Fix `clone_workflow` in `@[backend_v2/services/studio/workflow_service.py#L47-L929]` inside one `async with uow:` transaction with parent-before-child ordering (`Workflow` with `default_profile_id=None` -> cloned `OutputProfile` rows -> update `Workflow.default_profile_id`), execute multi-table mutations inside single `async with uow:` blocks, drop `AppendOnlyRepositoryBase` (`@[backend_v2/database/repositories/base.py#L39-L62]`), preserve `original.slug` on Studio clones and `{original.slug}_copy` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones, replace `"New Työnkulku"` -> `"New Workflow"` and `"New Askel"` -> `"New Step"`, and enforce symmetric `ROOT`/`ADMIN` read RBAC on `@[backend_v2/services/studio/system_config_service.py#L44-L746]`.

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
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    model_name TEXT NOT NULL,
    prompt_tokens BIGINT NOT NULL DEFAULT 0 CHECK (prompt_tokens >= 0),
    completion_tokens BIGINT NOT NULL DEFAULT 0 CHECK (completion_tokens >= 0),
    cached_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cached_tokens >= 0),
    reasoning_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reasoning_tokens >= 0),
    cost_usd NUMERIC(14, 6) NOT NULL DEFAULT 0 CHECK (cost_usd >= 0),
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
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/database/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L209-L250]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L321-L362]`
- `[MODIFY] @[backend_v2/database/postgres/graph_adapter.py#L433-L754]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L414-L447]`
- `[MODIFY] @[backend_v2/database/factory.py#L132-L167]`
- `[MODIFY] @[backend_v2/database/repository.py#L25-L52]`
- `[MODIFY] @[backend_v2/database/repositories/__init__.py]`
- `[MODIFY] @[backend_v2/database/repositories/components/__init__.py]`
- `[MODIFY] @[backend_v2/database/repositories/base.py#L39-L62]`
- `[MODIFY] @[backend_v2/database/repositories/audit.py#L26-L325]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L28-L310]`
- `[MODIFY] @[backend_v2/database/repositories/workflow.py#L30-L394]`
- `[MODIFY] @[backend_v2/database/repositories/system.py#L25-L213]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L30-L481]`
- `[MODIFY] @[backend_v2/database/repositories/report_artifact.py#L26-L192]`
- `[MODIFY] @[backend_v2/database/repositories/components/prompt_block.py#L18-L268]`
- `[MODIFY] @[backend_v2/database/repositories/components/output_profile.py#L17-L162]`
- `[MODIFY] @[backend_v2/database/repositories/components/task_brief.py#L17-L147]`
- `[MODIFY] @[backend_v2/models/domain/base.py#L414-L435]`
- `[MODIFY] @[backend_v2/models/dtos/system.py]`
- `[MODIFY] @[backend_v2/models/enums.py#L272-L277]`
- `[MODIFY] @[backend_v2/services/auth/secret_service.py#L140-L1170]`
- `[MODIFY] @[backend_v2/services/usage_service.py#L25-L406]`
- `[MODIFY] @[backend_v2/services/studio/prompt_block_service.py#L31-L279]`
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L47-L929]`
- `[MODIFY] @[backend_v2/services/studio/output_profile_service.py#L26-L322]`
- `[MODIFY] @[backend_v2/services/studio/task_brief_service.py#L29-L255]`
- `[MODIFY] @[backend_v2/services/studio/system_config_service.py#L44-L746]`
- `[MODIFY] @[backend_v2/services/blueprint.py#L90-L1081]`
- `[MODIFY] @[backend_v2/services/execution/facade.py#L70-L719]`
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L36-L488]`
- `[MODIFY] @[backend_v2/services/report/__init__.py#L42-L297]`
- `[MODIFY] @[backend_v2/services/report/format_reader_service.py#L22-L229]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/__init__.py#L78-L177]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/base.py#L106-L132]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/logic.py]`
- `[MODIFY] @[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`
- `[MODIFY] @[backend_v2/core/hook_registry.py]`
- `[MODIFY] @[backend_v2/llm/handler.py]`
- `[MODIFY] @[backend_v2/worker.py]`
- `[MODIFY] @[backend_v2/workers/report_worker.py]`
- `[MODIFY] @[backend_v2/workers/synthesis_reducers.py#L60-L81]`
- `[MODIFY] @[backend_v2/workers/synthesis_worker.py#L157-L185]`
- `[MODIFY] @[backend_v2/api/dependencies.py#L327-L336]`
- `[MODIFY] @[backend_v2/main.py#L72-L130]`
- `[MODIFY] @[scripts/ablation_live_executor.py]`
- `[MODIFY] @[backend_v2/tests/fakes/__init__.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test___init__.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_repository.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/core/test_hook_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dependencies.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_interfaces.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_repositories_v2.py]`

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
- `clear_collection_document_rows`
- `get_collection_document`
- `upsert_collection_document`
- `delete_collection_document`
- `list_collection_documents`
- `clear_collection_documents`
- `_upsert_usage_aggregates`
- `upsert_usage_aggregate`
- `get_system_settings`
- `update_system_settings`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L209-L250]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]` & `@[backend_v2/database/postgres/graph_adapter.py#L433-L754]` | Unwrapped `.model_validate()` calls across 12 entity hydrators, `else: SystemRulePromptBlock` fallthrough in `hydrate_prompt_block_row`, generic `Exception -> STORAGE_ACCESS_FAILED` masking of PostgreSQL `SQLSTATE 23503` / `23505`, and `ON CONFLICT DO NOTHING` in `_MATERIALIZE_WAVE_SQL`. | Implement SSOT `validate_hydrated_row` (catching `ValidationError` -> RFC 7807 `logger.error` + `AppException(ErrorCodes.VALIDATION_FAILED, status_code=500)`), `PromptBlockAdapter` discriminated union dispatch, `translate_postgres_exception` (`23503` on `DELETE` -> HTTP 400 `DELETE_BLOCKED_BY_USAGE`, `23503` on `INSERT`/`UPDATE` -> HTTP 422 `VALIDATION_FAILED`, `23505` -> HTTP 409 `CONFLICT`), and `DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`. | Centralize hydration and exception translation in `coercion_and_constants.py` with zero per-table try/except copy-paste. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/ backend_v2/tests/unit/database/postgres/entity_adapter/ --test --ast-strict` |
| `@[backend_v2/services/studio/prompt_block_service.py#L31-L279]`, `@[backend_v2/services/studio/workflow_service.py#L47-L929]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L322]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L255]` & `@[backend_v2/services/studio/system_config_service.py#L44-L746]` | Payload-only RBAC checks enabling cross-tenant `PUT` IDOR hijack, client-defined ID creation via `PUT /{id}`, inverted FK insertion order in `clone_workflow`, multi-autocommit tears, hyphenated `-copy` slugs, mixed Finnish `"New Työnkulku"`/`"New Askel"` strings, and `list`/`get` RBAC asymmetry. | Enforce 4-Phase In-Place Upsert (`existing is None -> ResourceNotFoundError`, `enforce_modification_rights(initiator, existing.organization_id)`, preserve `existing.organization_id` for non-`ROOT`, private `_insert_validated_*` for draft/clone), single `async with uow:` parent-before-child `clone_workflow`, informational `original.slug` preservation (`{original.slug}_copy` on `MCPGateway`), pure English literals, and symmetric `ROOT`/`ADMIN` read RBAC. | No separate revision history tables for Studio drafts; preserve single-row `JSONB` canvas saves inside one `QuorumUnitOfWork` transaction. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/tests/unit/services/studio/ --test --ast-strict` |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/interfaces.py#L414-L447]`, `@[backend_v2/database/repositories/audit.py#L26-L325]`, `@[backend_v2/services/usage_service.py#L25-L406]` & `@[backend_v2/services/auth/secret_service.py#L140-L1170]` | Volatile process-RAM `"audit_logs"`, `"usage"`, and mutable shadow `"usage_aggregates"` counters (`UsageAggregateDTO`, `UsageAggregateUpdateDTO`), silent `if org:` skip in `UsageService.get_usage_report`, and `SecretService` calling `delete_collection_document`. | Create append-only UUIDv7 PostgreSQL 19 tables `audit_logs` (`aud_`) and `usage_records` (`usg_`) with `VIRTUAL` `created_at`, add typed `insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `aggregate_organization_usage`, and `delete_tenant_secret` methods on `EntityPersistencePort`, and raise `ResourceNotFoundError` (`404`) when `get_organization(org_id)` is `None`. | Compute FinOps usage totals directly via indexed SQL `SUM(...)` / `COUNT(*)` over `usage_records` without secondary counter tables. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/repositories/audit.py backend_v2/services/usage_service.py backend_v2/services/auth/secret_service.py --test --ast-strict` |
| `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `@[backend_v2/database/repository.py#L25-L52]`, `@[backend_v2/database/factory.py#L132-L167]`, `@[backend_v2/api/dependencies.py#L327-L336]` & `@[backend_v2/models/enums.py#L272-L277]` | Generic `StorageDriver` / `PostgresStorageDriver` (`self._collections` RAM fallback), `AppendOnlyRepositoryBase` (`_v2` ID corruption), `StorageBackend.FIRESTORE`/`LOCAL`, `data/workflows/*.json` disk fallbacks, 8 dead V1 ghost repositories/protocols, and dead `comp_repo` pass-throughs. | Route all 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade directly through `EntityPersistencePort`, lock `StorageBackend` exclusively to `POSTGRES`, remove dead `comp_repo` parameters, and delete all 11 legacy driver / V1 ghost production files and 10 companion test files. | Do NOT build a generic filter/ORM DSL and do NOT force ~95 worker/report/test callers to unpack 9 repository arguments; keep `UnifiedWorkflowRepository(uow_factory)` as a zero-storage-logic V2 composite facade. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/api/dependencies.py backend_v2/tests/unit/test_dependencies.py backend_v2/tests/unit/test_interfaces.py backend_v2/tests/unit/test_repositories_v2.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`, `@[backend_v2/database/interfaces.py#L414-L447]`, `@[backend_v2/database/repository.py#L25-L52]`, `@[backend_v2/services/studio/workflow_service.py#L47-L929]`, and `@[backend_v2/services/usage_service.py#L25-L406]`.</action>
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
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/database/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L209-L250]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L321-L362]</backend>
    <backend>@[backend_v2/database/postgres/graph_adapter.py#L433-L754]</backend>
    <backend>@[backend_v2/database/interfaces.py#L414-L447]</backend>
    <backend>@[backend_v2/database/factory.py#L132-L167]</backend>
    <backend>@[backend_v2/database/repository.py#L25-L52]</backend>
    <backend>@[backend_v2/database/repositories/__init__.py]</backend>
    <backend>@[backend_v2/database/repositories/components/__init__.py]</backend>
    <backend>@[backend_v2/database/repositories/base.py#L39-L62]</backend>
    <backend>@[backend_v2/database/repositories/audit.py#L26-L325]</backend>
    <backend>@[backend_v2/database/repositories/identity.py#L28-L310]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py#L30-L394]</backend>
    <backend>@[backend_v2/database/repositories/system.py#L25-L213]</backend>
    <backend>@[backend_v2/database/repositories/execution.py#L30-L481]</backend>
    <backend>@[backend_v2/database/repositories/report_artifact.py#L26-L192]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py#L18-L268]</backend>
    <backend>@[backend_v2/database/repositories/components/output_profile.py#L17-L162]</backend>
    <backend>@[backend_v2/database/repositories/components/task_brief.py#L17-L147]</backend>
    <backend>@[backend_v2/models/domain/base.py#L414-L435]</backend>
    <backend>@[backend_v2/models/dtos/system.py]</backend>
    <backend>@[backend_v2/models/enums.py#L272-L277]</backend>
    <backend>@[backend_v2/services/auth/secret_service.py#L140-L1170]</backend>
    <backend>@[backend_v2/services/usage_service.py#L25-L406]</backend>
    <backend>@[backend_v2/services/studio/prompt_block_service.py#L31-L279]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L47-L929]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py#L26-L322]</backend>
    <backend>@[backend_v2/services/studio/task_brief_service.py#L29-L255]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py#L44-L746]</backend>
    <backend>@[backend_v2/services/blueprint.py#L90-L1081]</backend>
    <backend>@[backend_v2/services/execution/facade.py#L70-L719]</backend>
    <backend>@[backend_v2/services/execution/override_service.py#L36-L488]</backend>
    <backend>@[backend_v2/services/report/__init__.py#L42-L297]</backend>
    <backend>@[backend_v2/services/report/format_reader_service.py#L22-L229]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/__init__.py#L78-L177]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py#L106-L132]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>@[backend_v2/worker.py]</backend>
    <backend>@[backend_v2/workers/report_worker.py]</backend>
    <backend>@[backend_v2/workers/synthesis_reducers.py#L60-L81]</backend>
    <backend>@[backend_v2/workers/synthesis_worker.py#L157-L185]</backend>
    <backend>@[backend_v2/api/dependencies.py#L327-L336]</backend>
    <backend>@[backend_v2/main.py#L72-L130]</backend>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[backend_v2/tests/fakes/__init__.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]</backend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test___init__.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_repository.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]</backend>
    <backend>@[backend_v2/tests/unit/core/test_hook_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dependencies.py]</backend>
    <backend>@[backend_v2/tests/unit/test_interfaces.py]</backend>
    <backend>@[backend_v2/tests/unit/test_repositories_v2.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`validate_hydrated_row` and `translate_postgres_exception` in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]` wrap 100% of entity hydrators and SQL mutation/delete helpers, mapping `ValidationError` -> HTTP 500 `ErrorCodes.VALIDATION_FAILED`, `SQLSTATE 23503` on `DELETE` -> HTTP 400 `ErrorCodes.DELETE_BLOCKED_BY_USAGE`, `SQLSTATE 23503` on `INSERT`/`UPDATE` -> HTTP 422 `ErrorCodes.VALIDATION_FAILED`, and `SQLSTATE 23505` -> HTTP 409 `ErrorCodes.CONFLICT` with structured RFC 7807 `logger.error`.</item>
    <item>All 5 Studio `save_*` methods enforce the 4-Phase In-Place Upsert Protocol (`existing is None -> raise ResourceNotFoundError`, `enforce_modification_rights(initiator, existing.organization_id)` before payload inspection, `existing.organization_id` preservation for non-`ROOT`), `clone_workflow` executes parent-before-child inside one `async with uow:` transaction, Studio clones preserve informational `original.slug` (`{original.slug}_copy` on `MCPGateway`), mixed Finnish code literals are replaced with English, and `StudioSystemConfigService` enforces symmetric `ROOT`/`ADMIN` read RBAC.</item>
    <item>Append-only `audit_logs` (`aud_`) and `usage_records` (`usg_`) tables and `EntityPersistencePort` methods (`insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `aggregate_organization_usage`, `delete_tenant_secret`) are live, and `usage_aggregates`, `UsageAggregateDTO`, `UsageAggregateUpdateDTO`, and `SystemSettingsDTO` are deleted.</item>
    <item>All 9 active V2 repositories and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade operate 100% on `EntityPersistencePort`, `StorageBackend` is locked exclusively to `POSTGRES`, dead `comp_repo` pass-throughs are removed, and all 11 legacy driver / V1 ghost production modules plus 10 companion test files are physically deleted.</item>
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
    <anti_target>Do NOT delete `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` in `@[backend_v2/database/repository.py#L25-L52]`; retain it strictly as a zero-storage-logic V2 composite protocol facade over the 9 active `EntityPersistencePort`-backed repositories.</anti_target>
    <anti_target>Do NOT overwrite `slug = new_id` on Studio entity clones (`Workflow`, `Step`, `PromptBlock`, `OutputProfile`, `TaskBrief`, `ModelRegistry`); preserve `original.slug` as non-unique informational metadata and `{original.slug}_copy` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones.</anti_target>
  </anti_targets>

  <step id="1.1" name="Unified Fail-Fast Hydrator (validate_hydrated_row) &amp; SQLSTATE Exception Translation Gate (translate_postgres_exception)">
    <action>1. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`: Implement `validate_hydrated_row(model_cls_or_adapter, payload, *, table_name: str, entity_id: str) -> T` catching Pydantic `ValidationError`, logging `logger.error` with `ErrorCodes.VALIDATION_FAILED`, `table_name`, and `entity_id`, and raising `AppException(ErrorCodes.VALIDATION_FAILED, status_code=500)`. Implement `translate_postgres_exception(exc: Exception, *, operation: str, table_name: str, entity_id: str) -> AppException` mapping PostgreSQL `SQLSTATE 23503` (`ForeignKeyViolationError`) on `DELETE` to `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)`, `SQLSTATE 23503` on `INSERT`/`UPDATE` to `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`, `SQLSTATE 23505` (`UniqueViolationError`) to `AppException(ErrorCodes.CONFLICT, status_code=409)`, and all other database I/O exceptions to `AppException(ErrorCodes.STORAGE_ACCESS_FAILED, status_code=500)`, always preceded by structured `logger.error`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L143-L240]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L209-L250]`, and `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`: Enforce `validate_hydrated_row` and `translate_postgres_exception` across all entity hydrators (`organization`, `user`, `invitation`, `tenant_secret`, `execution_assignment`, `prompt_block`, `step`, `workflow`, `output_profile`, `task_brief`, `execution`, `report_artifact`) and `get_report_binary_row`. Replace the `if/elif/else: SystemRulePromptBlock` fallthrough in `hydrate_prompt_block_row` with `PromptBlockAdapter.validate_python(payload, strict=False)` wrapped in `validate_hydrated_row`, and validate `Workflow.steps` (`list[StepRule]`) via `TypeAdapter(list[StepRule])` inside `validate_hydrated_row`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/database/postgres/graph_adapter.py#L433-L754]`: Wrap `_hydrate_proposition_node` in `validate_hydrated_row` and replace `ON CONFLICT (run_id, source_id, target_id, relation_type) DO NOTHING RETURNING edge_id` in `_MATERIALIZE_WAVE_SQL` with `ON CONFLICT (run_id, source_id, target_id, relation_type) DO UPDATE SET causal_weight = EXCLUDED.causal_weight RETURNING edge_id`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, and `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`: Add positive, negative, and boundary unit tests verifying `validate_hydrated_row` (`ValidationError` -> `ErrorCodes.VALIDATION_FAILED`), `PromptBlockAdapter` rejection of unknown `category_id`, `translate_postgres_exception` (`23503` on `DELETE` -> `DELETE_BLOCKED_BY_USAGE` 400, `23503` on `INSERT`/`UPDATE` -> `VALIDATION_FAILED` 422, `23505` -> `CONFLICT` 409, transport error -> `STORAGE_ACCESS_FAILED` 500), and idempotent `_MATERIALIZE_WAVE_SQL` edge weight updates.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every `AppException` produced by `validate_hydrated_row` and `translate_postgres_exception` MUST log `logger.error` with `error_code`, `table_name`, and `entity_id` before raising.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/ backend_v2/tests/unit/database/postgres/entity_adapter/ --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="Studio Multi-Tenant IDOR Closure, 4-Phase In-Place Upsert, Single-UoW clone_workflow &amp; RBAC Symmetry">
    <action>1. `[MODIFY]` `@[backend_v2/services/studio/prompt_block_service.py#L31-L279]`, `@[backend_v2/services/studio/workflow_service.py#L47-L929]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L322]`, and `@[backend_v2/services/studio/task_brief_service.py#L29-L255]`: Refactor `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, and `save_task_brief` to enforce the 4-Phase In-Place Upsert Protocol: (a) fetch `existing` by `id` first and raise `ResourceNotFoundError` (`404`) if `existing is None`, (b) verify `enforce_modification_rights(initiator, existing.organization_id)` on `existing` before inspecting the incoming payload, (c) preserve `existing.organization_id` for non-`ROOT` callers, and (d) extract private `_insert_validated_*` helpers invoked exclusively by `create_*_draft` and `clone_*`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py#L47-L929]`: Execute `clone_workflow` inside a single `async with uow:` transaction with parent-before-child FK ordering: (a) insert cloned `Workflow` with `default_profile_id=None`, (b) insert cloned `OutputProfile` rows referencing `workflow_id=new_id`, and (c) update `Workflow.default_profile_id` to the cloned default profile UUID. Execute `save_workflow` + `_sync_output_profiles_for_workflow` and `delete_workflow` each inside a single atomic `async with uow:` transaction boundary. Replace mixed Finnish strings (`"New Työnkulku"` -> `"New Workflow"`, `"New Askel"` -> `"New Step"`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/services/studio/system_config_service.py#L44-L746]`: Preserve informational `original.slug` on `ModelRegistry` clones, keep `{original.slug}_copy` / `{original.slug}_copy_N` (`_SINGLE_UNDERSCORE_SLUG_PATTERN`) on `MCPGateway` clones (banning hyphenated `-copy`), and enforce symmetric `ROOT`/`ADMIN` read RBAC across `get`/`list` methods while raising `PermissionDeniedError` (`403`) for unauthorized roles (`VIEWER`/`USER`).</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`: Add unit tests using `TaskBriefFactory.build(...)` and `WorkflowFactory.build(...)` verifying cross-tenant `PUT` IDOR rejection (`403`), unknown-ID `PUT` rejection (`404`), non-`ROOT` `organization_id` preservation, and single-UoW `clone_workflow` parent-before-child ordering.</action>
    <constraint invariant="in_place_upsert_standard_mandate">Public `save_*` methods MUST NEVER insert new rows when `existing is None` or evaluate RBAC solely against untrusted payload `organization_id`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/tests/unit/services/studio/ --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="Append-Only PostgreSQL 19 audit_logs &amp; usage_records Ledgers, SQL FinOps Rollups &amp; delete_tenant_secret">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` and `@[backend_v2/models/enums.py#L272-L277]`: Add `audit_logs` (`EntityPrefix.AUDIT_LOG = "aud"`) and `usage_records` (`EntityPrefix.USAGE_RECORD = "usg"`) UUIDv7 tables with `VIRTUAL` `created_at` and B-Tree indexes (`idx_audit_logs_org_created`, `idx_audit_logs_execution_id`, `idx_usage_records_org_created`, `idx_usage_records_execution_id`), and lock `StorageBackend` in `@[backend_v2/models/enums.py#L272-L277]` exclusively to `POSTGRES` (dropping `FIRESTORE` and `LOCAL`).</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/interfaces.py#L414-L447]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L321-L362]`, and `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]`: Add typed `EntityPersistencePort` methods `insert_audit_log`, `list_audit_logs`, `insert_usage_record`, `aggregate_organization_usage`, and `delete_tenant_secret`, and delete all 5 generic `*_collection_document_row` / `*_collection_document` functions (`get_collection_document_row`, `upsert_collection_document_row`, `delete_collection_document_row`, `list_collection_document_rows`, `clear_collection_document_rows`, `get_collection_document`, `upsert_collection_document`, `delete_collection_document`, `list_collection_documents`, `clear_collection_documents`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/models/domain/base.py#L414-L435]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/database/repositories/audit.py#L26-L325]`, `@[backend_v2/services/usage_service.py#L25-L406]`, and `@[backend_v2/services/auth/secret_service.py#L140-L1170]`: Route `AuditRepositoryImpl` and `UsageService` directly through `EntityPersistencePort` (`audit_logs` and `usage_records`), route `SecretService.delete_tenant_secret` through `entity_adapter.delete_tenant_secret(secret_id)`, delete `UsageAggregateDTO`, `UsageAggregateUpdateDTO`, `SystemSettingsDTO`, `upsert_usage_aggregate`, and `_upsert_usage_aggregates`, and raise `AppException(ErrorCodes.RESOURCE_NOT_FOUND, status_code=404)` in `UsageService.get_usage_report` when `get_organization(org_id)` is `None`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]` and `@[backend_v2/tests/factories/model_factories.py]`: Remove obsolete generic collection document tests, update factories in `model_factories.py` for removed `UsageAggregateDTO`/`SystemSettingsDTO`, and add unit tests for `audit_logs`, `usage_records`, `aggregate_organization_usage`, and `delete_tenant_secret`.</action>
    <constraint invariant="universal_ssot_and_normalization_mandate">FinOps usage totals MUST be computed exclusively via parameterized SQL `SUM(...)` / `COUNT(*)` over append-only `usage_records` with zero secondary shadow counter tables.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/base.py backend_v2/models/dtos/system.py backend_v2/models/enums.py backend_v2/database/repositories/audit.py backend_v2/services/usage_service.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py --test --ast-strict</audit_command>
  </step>

  <step id="1.4" name="Direct EntityPersistencePort Repository Cutover, StorageDriver &amp; Dead V1 Ghost Repository Eradication">
    <action>1. `[MODIFY]` `@[backend_v2/database/repository.py#L25-L52]`, `@[backend_v2/database/factory.py#L132-L167]`, `@[backend_v2/database/__init__.py]`, `@[backend_v2/database/postgres/__init__.py]`, `@[backend_v2/database/repositories/__init__.py]`, `@[backend_v2/database/repositories/components/__init__.py]`, `@[backend_v2/database/repositories/base.py#L39-L62]`, `@[backend_v2/database/repositories/identity.py#L28-L310]`, `@[backend_v2/database/repositories/workflow.py#L30-L394]`, `@[backend_v2/database/repositories/system.py#L25-L213]`, `@[backend_v2/database/repositories/execution.py#L30-L481]`, `@[backend_v2/database/repositories/report_artifact.py#L26-L192]`, `@[backend_v2/database/repositories/components/prompt_block.py#L18-L268]`, `@[backend_v2/database/repositories/components/output_profile.py#L17-L162]`, and `@[backend_v2/database/repositories/components/task_brief.py#L17-L147]`: Migrate all 9 active V2 repositories (`Workflow`, `Execution`, `ReportArtifact`, `PromptBlock`, `TaskBrief`, `OutputProfile`, `Identity`, `Audit`, `System`) and the retained zero-storage-logic `UnifiedWorkflowRepository(uow_factory: UnitOfWorkFactory)` composite protocol facade from `StorageDriver` onto `UnitOfWorkFactory` / `EntityPersistencePort`. Delete `AppendOnlyRepositoryBase` from `base.py`, drop `get_system_settings` and `update_system_settings` from `system.py`, drop `data/workflows/*.json` disk fallbacks and embedded-step fallback scans from `workflow.py`, execute `delete_org_data` (`DELETE FROM organizations WHERE id = $1`) in `identity.py` inside one atomic `async with uow:` block, fix `ExecutionRepositoryImpl` filter bindings (`created_by`, `ExecutionStatus.COMPLETED`), and stop stripping `mcp_tool_audit` into phantom `"executions/{id}/audit_trails"` subcollections.</action>
    <action>2. `[MODIFY]` `@[backend_v2/api/dependencies.py#L327-L336]`, `@[backend_v2/main.py#L72-L130]`, `@[backend_v2/services/blueprint.py#L90-L1081]`, `@[backend_v2/services/execution/facade.py#L70-L719]`, `@[backend_v2/services/execution/override_service.py#L36-L488]`, `@[backend_v2/services/report/__init__.py#L42-L297]`, `@[backend_v2/services/report/format_reader_service.py#L22-L229]`, `@[backend_v2/services/orchestrator/dag_executor/__init__.py#L78-L177]`, `@[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py#L70-L109]`, `@[backend_v2/services/orchestrator/strategies/base.py#L106-L132]`, `@[backend_v2/services/orchestrator/strategies/logic.py]`, `@[backend_v2/services/orchestrator/strategies/llm_strategy/blueprint_and_metadata_stage.py]`, `@[backend_v2/core/hook_registry.py]`, `@[backend_v2/llm/handler.py]`, `@[backend_v2/worker.py]`, `@[backend_v2/workers/report_worker.py]`, `@[backend_v2/workers/synthesis_reducers.py#L60-L81]`, `@[backend_v2/workers/synthesis_worker.py#L157-L185]`, and `@[scripts/ablation_live_executor.py]`: Remove all `get_driver`, `StorageDriver`, dead V1 ghost repository DI bindings (`IKnowledgeRepository`, `IComponentRepository`, `IAgentRepository`, `IRoleRepository`, `ITaskBlueprintRepository`, `IMatrixRepository`, `IExecutionPersonaRepository`, `IExtractionProtocolRepository`), dead `comp_repo` constructor pass-throughs, dead V1 `LLMHandler` model-lookup helpers, and legacy `data/workflows` / `execution_trace_storage_path` startup checks in `main.py`.</action>
    <action>3. `[DELETE]` `@[backend_v2/database/driver.py#L86-L207]`, `[DELETE]` `@[backend_v2/database/postgres/storage_driver.py#L186-L556]`, `[DELETE]` `@[backend_v2/models/domain/knowledge.py]`, `[DELETE]` `@[backend_v2/database/repositories/knowledge.py#L30-L219]`, `[DELETE]` `@[backend_v2/database/repositories/component.py#L17-L242]`, `[DELETE]` `@[backend_v2/database/repositories/components/agent.py#L17-L163]`, `[DELETE]` `@[backend_v2/database/repositories/components/role.py#L17-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/task_blueprint.py#L18-L167]`, `[DELETE]` `@[backend_v2/database/repositories/components/matrix.py#L18-L168]`, `[DELETE]` `@[backend_v2/database/repositories/components/execution_persona.py#L18-L145]`, `[DELETE]` `@[backend_v2/database/repositories/components/extraction_protocol.py#L18-L145]`, `[DELETE]` `@[backend_v2/tests/unit/models/domain/test_knowledge_dtos.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_knowledge.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_component.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_agent.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_role.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_task_blueprint.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_matrix.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_execution_persona.py]`, `[DELETE]` `@[backend_v2/tests/unit/database/repositories/components/test_extraction_protocol.py]`, and `[DELETE]` `@[backend_v2/tests/unit/database/repositories/test_base.py]`: Physically delete all 11 legacy driver / dead V1 ghost production modules and their 10 companion unit test files.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/fakes/__init__.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]`, `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`, `@[backend_v2/tests/unit/database/test___init__.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, `@[backend_v2/tests/unit/core/test_hook_registry.py]`, `@[backend_v2/tests/unit/test_dependencies.py]`, `@[backend_v2/tests/unit/test_interfaces.py]`, and `@[backend_v2/tests/unit/test_repositories_v2.py]`: Delete `InMemoryKnowledgeRepository`, `InMemoryComponentRepository`, `InMemoryAgentRepository`, `InMemoryRoleRepository`, `InMemoryTaskBlueprintRepository`, `InMemoryMatrixRepository`, `InMemoryExecutionPersonaRepository`, and `InMemoryExtractionProtocolRepository` from `in_memory_repositories.py`, align `InMemoryUnifiedWorkflowRepository` with the 9 active V2 repository protocols, and update unit test suites to verify `UnifiedWorkflowRepository(uow_factory)` roundtrip persistence via `InMemoryUnitOfWork`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">100% of persistence operations MUST flow through `EntityPersistencePort` (`QuorumUnitOfWork`) with zero `StorageDriver`, `PostgresStorageDriver`, or volatile RAM dictionary fallbacks.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/services/ backend_v2/workers/ backend_v2/worker.py backend_v2/core/hook_registry.py backend_v2/llm/handler.py backend_v2/api/dependencies.py backend_v2/main.py scripts/ablation_live_executor.py backend_v2/tests/fakes/ backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/database/ backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/core/test_hook_registry.py backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/test_dependencies.py backend_v2/tests/unit/test_interfaces.py backend_v2/tests/unit/test_repositories_v2.py --test --ast-strict</audit_command>
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
      <input>Simulated `asyncpg.ForeignKeyViolationError` (`sqlstate="23503"`) passed to `translate_postgres_exception(..., operation="DELETE", table_name="prompt_blocks", entity_id=blk.id)`</input>
      <expected>Logs `logger.error` and returns `AppException` with `status_code=400` and `ErrorCodes.DELETE_BLOCKED_BY_USAGE`</expected>
    </test>
    <test name="test_translate_postgres_exception_maps_23505_unique_to_conflict_and_23503_insert_to_422" category="boundary">
      <input>Simulated `UniqueViolationError` (`sqlstate="23505"`) on `INSERT` and `ForeignKeyViolationError` (`sqlstate="23503"`) on `UPDATE` passed to `translate_postgres_exception`</input>
      <expected>`23505` maps to `AppException(ErrorCodes.CONFLICT, status_code=409)` and `23503` on `UPDATE` maps to `AppException(ErrorCodes.VALIDATION_FAILED, status_code=422)`</expected>
    </test>
    <test name="test_studio_save_workflow_cross_tenant_put_idor_raises_permission_denied" category="negative">
      <input>Persisted `WorkflowFactory.build(organization_id=org_b_id)` in `InMemoryUnitOfWork`; Tenant A `ADMIN` calls `save_workflow(initiator_a, wf_b.id, forged_payload_with_org_a)`</input>
      <expected>Fetches persisted `existing` first, rejects cross-tenant overwrite with `PermissionDeniedError` (`403`), and leaves `wf_b` unmodified</expected>
    </test>
    <test name="test_studio_save_methods_reject_client_invented_id_when_missing_with_404" category="boundary">
      <input>Caller invokes `save_prompt_block`, `save_workflow`, `save_step`, `save_output_profile`, or `save_task_brief` with a valid-format UUIDv7 ID that does not exist in `InMemoryUnitOfWork`</input>
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
  </test_contracts>

  <validation_gate>
    <action>Run Phase 1 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/services/ backend_v2/workers/ backend_v2/worker.py backend_v2/core/hook_registry.py backend_v2/llm/handler.py backend_v2/api/dependencies.py backend_v2/main.py scripts/ablation_live_executor.py backend_v2/tests/fakes/ backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/database/ backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/core/test_hook_registry.py backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/test_dependencies.py backend_v2/tests/unit/test_interfaces.py backend_v2/tests/unit/test_repositories_v2.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
