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

# EPIC 165 - Phase 2: 21-Table PostgreSQL 19 DDL Evolution, `system_configs` Split (`model_registries` & `mcp_gateways`), Junction Tables (`step_criteria_blocks` & `workflow_step_refs`), `Workflow.version` SQL OCC & Typed UUID Foreign Keys

**Overview:** Evolve `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]` from the 18-table Phase 1 schema to the 21-table Phase 2 PostgreSQL 19 UUIDv7 topology (prior to Phase 4's 22nd `execution_payloads` sidecar table) with an idempotent pre-production cutover `DO $$` block, split the Single-Table Inheritance `system_configs` table and `"system_config"` seed collection (`@[backend_v2/seed/seed_data.json#L2-L554]` and `@[backend_v2/seed/seed_data.json#L20805-L21600]`) into dedicated `model_registries` (`EntityPrefix.MODEL_REGISTRY = "mrg"`, zero `type` discriminator) and `mcp_gateways` (`EntityPrefix.MCP_GATEWAY = "mcp"`, required `organization_id`, zero `type` discriminator), bind `tenant_secrets.mcp_gateway_id` (`ON DELETE CASCADE`), drop banned `ModelProfile.api_key`, `ModelProfile.parsing_mode`, and `LLMProviderConfig.parsing_mode` fields across Python (`@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/models/llm.py#L185-L444]`), Seed Vault, and Flutter Studio (`@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`), add normalized `step_criteria_blocks` (dropping redundant `steps.criteria_block_ids JSONB`) and `workflow_step_refs` junction/projection tables (`ON DELETE RESTRICT`) plus deferrable `workflows.default_profile_id` (`ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`), convert `output_profiles.*_target_block`, `users.created_by`, and `executions.created_by` to typed `UUID` Foreign Keys with `parse_prefixed_uuid7` domain validators, convert `created_at` to `VIRTUAL` UUIDv7 extraction across all 16 UUIDv7-PK tables plus `report_binaries` (`uuid_extract_timestamp(report_id)`), and enforce single-statement SQL Optimistic Concurrency Control (`WHERE workflows.version = $6 RETURNING version`) on `workflows`.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 2 Forensic Context, Complexity Slayer & Evolved PostgreSQL 19 SQL DDL

### Forensic Findings 3 & 6
* **Finding 3 [P1 HIGH] — `system_configs` Single-Table Inheritance Kitchen Sink & `seed_data.json` Schema Drift:**
  * Forensic anchors: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/models/llm.py#L185-L444]`, `@[backend_v2/seed/seed_registry.py]`, and `@[backend_v2/seed/seed_data.json#L2-L554]`.
  * Root cause: Persistence and seeding cram `SystemConfigModelRegistry` and `SystemConfigMCPGateways` into one `system_configs` table under shared `sys_` prefix with STI `type` discriminator literals and zero shared domain columns, cross-type FK ambiguity on `workflows.model_registry_id` and `workflows.mcp_gateway_id`, unlinked string-only `target_identifier` for `scope = 'mcp_gateway'` in `tenant_secrets`, missing `organization_id` on `SystemConfigMCPGateways` / Flutter `McpGateway`, and banned `ModelProfile.api_key`, `ModelProfile.parsing_mode`, and `LLMProviderConfig.parsing_mode` fields (including 12 `"parsing_mode": "STRUCTURED_JSON"` occurrences in `@[backend_v2/seed/seed_data.json#L2-L554]`).
* **Finding 6 [P2 MEDIUM] — Permissive `SET NULL` Blueprint FKs, Untyped `TEXT` IDs, Non-Virtual `created_at`, Python Full-Table Delete Scans & Missing Indexes:**
  * Forensic anchors: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/database/repositories/components/prompt_block.py#L16-L200]`, `@[backend_v2/database/repositories/workflow.py#L26-L512]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, and `@[scripts/audit_database_atoms.py#audit_collection]`.
  * Concrete gaps closed in Phase 2: (1) upgrade permissive `ON DELETE SET NULL` on `steps.*_block_id` and `workflows.*_id` to `ON DELETE RESTRICT`, (2) bind circular `workflows.default_profile_id` as `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` and convert `output_profiles.variance_target_block`, `output_profiles.user_role_target_block`, `users.created_by`, and `executions.created_by` from `TEXT` to typed `UUID` Foreign Keys with `parse_prefixed_uuid7` Pydantic validators, (3) convert physical `created_at` on `executions`, `report_artifacts`, and `report_binaries` (`uuid_extract_timestamp(report_id)`) to `VIRTUAL` generated columns and remove dirty-DB `UPDATE`/`DELETE` SQL scrubbing blocks while preserving the idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements mandated by `ZORM007`, (4) add complete B-Tree indexes across all FK and `organization_id` columns plus `CHECK` discriminator constraints on `prompt_blocks.category_id` and `users.role`, and (5) eliminate all 4 Python full-table delete loops (`PromptBlockRepositoryImpl.delete_prompt_block`, `StudioWorkflowService.delete_step`, `WorkflowRepositoryImpl.delete_step`, and `StudioOutputProfileService.delete_output_profile`) in favor of `step_criteria_blocks` (dropping `steps.criteria_block_ids JSONB`), `workflow_step_refs`, and deferrable `workflows.default_profile_id`.

### Seven Aggregate Leaf Structures That MUST NOT Be Over-Normalized (Section 2.1.1)
1. Cohort assignments (`execution_assignments.batch_id` + `task_brief_snapshot JSONB`).
2. `I18nText` localized maps (`dict[SystemLocale, str]`).
3. `MatrixPromptBlock` rubric hierarchy (`scales`, `rows`, `columns`, `TDAAssertion`, `ContrastiveExample`).
4. `OutputProfile.content_blocks` (`AnySduiBlock`) and `Workflow.expected_inputs` (`ExpectedInput`).
5. `Workflow.steps` (`list[StepRule]` DAG canvas topology backed by `workflow_step_refs`).
6. 1:1 cold `lz4` TOAST sidecars (`report_binaries` and `execution_payloads`).
7. Flat FinOps scalar columns on `executions`.

### Canonical PostgreSQL 19 DDL Specification (Zero `QGR033` Breadcrumb Comments)

```sql
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'system_configs'
    ) THEN
        DROP TABLE IF EXISTS
            report_binaries, report_artifacts, quorum_edges, quorum_nodes,
            execution_assignments, executions,
            workflow_step_refs, step_criteria_blocks, output_profiles,
            workflows, steps, task_briefs, prompt_blocks,
            tenant_secrets, mcp_gateways, model_registries, system_configs,
            audit_logs, usage_records, invitations, users, organizations
        CASCADE;
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS model_registries (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    slug TEXT,
    name TEXT NOT NULL,
    default_provider TEXT NOT NULL,
    tier_definitions JSONB NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);

CREATE TABLE IF NOT EXISTS mcp_gateways (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    endpoint_url TEXT NOT NULL,
    transport_type TEXT NOT NULL,
    auth_type TEXT NOT NULL,
    auth_env_var TEXT,
    auth_header_name TEXT,
    timeout_seconds INTEGER NOT NULL CHECK (timeout_seconds >= 1 AND timeout_seconds <= 300),
    tools JSONB NOT NULL,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL
);
CREATE INDEX IF NOT EXISTS idx_mcp_gateways_org_id ON mcp_gateways(organization_id);

ALTER TABLE tenant_secrets
    ADD COLUMN IF NOT EXISTS mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_org_id ON tenant_secrets(organization_id);
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_mcp_gateway_id ON tenant_secrets(mcp_gateway_id);

CREATE TABLE IF NOT EXISTS step_criteria_blocks (
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE,
    prompt_block_id UUID NOT NULL REFERENCES prompt_blocks(id) ON DELETE RESTRICT,
    position INTEGER NOT NULL CHECK (position >= 0),
    PRIMARY KEY (step_id, prompt_block_id)
);
CREATE INDEX IF NOT EXISTS idx_step_criteria_blocks_block_id ON step_criteria_blocks(prompt_block_id);

CREATE TABLE IF NOT EXISTS workflow_step_refs (
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_id UUID NOT NULL REFERENCES steps(id) ON DELETE RESTRICT,
    PRIMARY KEY (workflow_id, step_id)
);
CREATE INDEX IF NOT EXISTS idx_workflow_step_refs_step_id ON workflow_step_refs(step_id);

ALTER TABLE workflows
    DROP CONSTRAINT IF EXISTS workflows_default_profile_id_fkey,
    ADD CONSTRAINT workflows_default_profile_id_fkey
        FOREIGN KEY (default_profile_id) REFERENCES output_profiles(id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`
- `[MODIFY] @[backend_v2/models/enums.py#L246-L271]`
- `[MODIFY] @[backend_v2/models/auth.py]`
- `[MODIFY] @[backend_v2/models/llm.py#L185-L444]`
- `[MODIFY] @[backend_v2/models/domain/__init__.py]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py]`
- `[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L232]`
- `[MODIFY] @[backend_v2/models/domain/output_profile.py#L44-L435]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L249-L520]`
- `[MODIFY] @[backend_v2/models/dtos/system.py]`
- `[MODIFY] @[backend_v2/models/dtos/studio.py]`
- `[MODIFY] @[backend_v2/models/dtos/output_profile.py]`
- `[MODIFY] @[backend_v2/models/dtos/trace.py#L46-L63]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L296-L383]`
- `[MODIFY] @[backend_v2/database/repositories/identity.py#L31-L388]`
- `[MODIFY] @[backend_v2/database/repositories/system.py#L20-L166]`
- `[MODIFY] @[backend_v2/database/repositories/workflow.py#L26-L512]`
- `[MODIFY] @[backend_v2/database/repositories/components/prompt_block.py#L16-L200]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L402-L447]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L272-L316]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L322-L441]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`
- `[MODIFY] @[backend_v2/services/studio/system_config_service.py#L44-L817]`
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L49-L990]`
- `[MODIFY] @[backend_v2/services/studio/output_profile_service.py#L26-L369]`
- `[MODIFY] @[backend_v2/services/auth/secret_service.py#L140-L1170]`
- `[MODIFY] @[backend_v2/services/cache/typed_cache.py#L340-L418]`
- `[MODIFY] @[backend_v2/llm/client.py#L51-L947]`
- `[MODIFY] @[backend_v2/hooks/llm.py]`
- `[MODIFY] @[backend_v2/main.py#L70-L115]`
- `[MODIFY] @[backend_v2/seed/seed_registry.py]`
- `[MODIFY] @[backend_v2/seed/run_seed.py]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L2-L554]`
- `[MODIFY] @[scripts/_ast_guardrails.py]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py]`
- `[MODIFY] @[scripts/audit_dto_parity.py]`
- `[MODIFY] @[scripts/audit_database_atoms.py#audit_collection]`
- `[MODIFY] @[scripts/sanitize_seed_vault.py]`
- `[MODIFY] @[scripts/ablation_live_executor.py]`
- `[MODIFY] @[scripts/diff_executions.py]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/model_config.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
- `[MODIFY] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py]`
- `[MODIFY] @[backend_v2/tests/conftest.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_epic_chain_e2e.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`
- `[MODIFY] @[backend_v2/tests/test_caching_schema_scrub_bug.py]`
- `[MODIFY] @[backend_v2/tests/test_fastdev_frozen.py]`
- `[MODIFY] @[backend_v2/tests/test_worker_models_used.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_tier4_workflow_leak_bug.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/studio/test_workflows.py]`
- `[MODIFY] @[backend_v2/tests/unit/api/routers/test_server_id_authority.py]`
- `[MODIFY] @[backend_v2/tests/unit/core/test_redis_security.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_identity.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_report_artifact.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_workflow.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test___init__.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_repository.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_input_processing.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_interaction_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_linguistics.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_llm.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_matrix_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_scoring.py]`
- `[MODIFY] @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_client.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_provider_retry_after.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_source_verification.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_system_config.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_workflow.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_mcp.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_studio.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_enums.py]`
- `[MODIFY] @[backend_v2/tests/unit/models/test_v2_core.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_dto_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_diff_executions.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_seed_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/cache/test_cache_init.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/cache/test_typed_cache.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_ingress_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_override_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/mcp/test_dispatcher.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_schema_factory.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/test_unmapped_generic_inputs_bug.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_compilation_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_lifecycle_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/report/test_report_facade.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_auth_validator.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_simulation_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_system_config_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_execution_resumability.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/test_source_verification_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_api_clone_endpoints.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_api_seed_mutations.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_api_workflow_fail_fast.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_auth.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_concurrency_fuzzer.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_dag_taskgroup.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_input_processing.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_litellm_redis_timeout.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_llm_context_bounds.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_main.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_phase8_documentation_contracts.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_repositories_v2.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_schema_builder.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_execution_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_tasks.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_synthesis_worker.py]`
- `[MODIFY] @[backend_v2/tests/unit/workers/test_variance_synthesis.py]`
- `[MODIFY] @[client_app_v2/test/core/models/enums_test.dart]`
- `[MODIFY] @[client_app_v2/test/core/api/studio_client_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/core/api/studio_client_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/model_config_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/model_registry_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/studio/views/widgets/workflow/workflow_general_tab_test.dart]`
- `[MODIFY] @[client_app_v2/test/models/domain_parity_test.dart]`

## Phase 2 Deprecations & Sunset Symbols

<demolish>
- `SystemConfigUnion`
- `SystemConfigID`
- `AnySystemConfig`
- `AnySystemConfigAdapter`
- `SystemConfigCreateDTO`
- `SystemConfigUpdateDTO`
- `SystemConfigUpsertDTO`
- `hydrate_system_config_row`
- `upsert_system_config_row`
- `delete_system_config_row`
- `get_system_config_row`
- `list_system_configs_rows`
- `upsert_system_config`
- `list_system_configs`
- `create_system_config`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Step 2.1 (`system_configs` Split, `tenant_secrets.mcp_gateway_id`, `ModelProfile` / `LLMProviderConfig` Cleanup & `QGR030` Prefix Ratchet):** `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/enums.py#L246-L271]`, `@[backend_v2/models/auth.py]`, `@[backend_v2/models/llm.py#L185-L444]`, `@[backend_v2/models/domain/__init__.py]`, `@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/models/dtos/system.py]`, `@[backend_v2/database/interfaces.py#L296-L383]`, `@[backend_v2/database/repositories/system.py#L20-L166]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`, `@[backend_v2/services/studio/system_config_service.py#L44-L817]`, `@[backend_v2/services/auth/secret_service.py#L140-L1170]`, `@[backend_v2/services/cache/typed_cache.py#L340-L418]`, `@[backend_v2/llm/client.py#L51-L947]`, `@[backend_v2/hooks/llm.py]`, `@[backend_v2/main.py#L70-L115]`, `@[scripts/_ast_guardrails.py]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py]`, `@[backend_v2/tests/conftest.py]`, `@[backend_v2/tests/test_caching_schema_scrub_bug.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]`, `@[backend_v2/tests/test_worker_models_used.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_tier4_workflow_leak_bug.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_workflows.py]`, `@[backend_v2/tests/unit/api/routers/test_server_id_authority.py]`, `@[backend_v2/tests/unit/core/test_redis_security.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, `@[backend_v2/tests/unit/database/repositories/test_system.py]`, `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`, `@[backend_v2/tests/unit/database/test___init__.py]`, `@[backend_v2/tests/unit/database/test_postgres.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/hooks/test_llm.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/llm/test_client.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py]`, `@[backend_v2/tests/unit/models/domain/test_source_verification.py]`, `@[backend_v2/tests/unit/models/domain/test_system_config.py]`, `@[backend_v2/tests/unit/models/dtos/test_mcp.py]`, `@[backend_v2/tests/unit/models/dtos/test_system.py]`, `@[backend_v2/tests/unit/models/test_enums.py]`, `@[backend_v2/tests/unit/models/test_v2_core.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/services/cache/test_cache_init.py]`, `@[backend_v2/tests/unit/services/cache/test_typed_cache.py]`, `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/mcp/test_dispatcher.py]`, `@[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]`, `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_schema_factory.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_unmapped_generic_inputs_bug.py]`, `@[backend_v2/tests/unit/services/report/test_compilation_service.py]`, `@[backend_v2/tests/unit/services/report/test_lifecycle_service.py]`, `@[backend_v2/tests/unit/services/report/test_report_facade.py]`, `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, `@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`, `@[backend_v2/tests/unit/services/studio/test_simulation_service.py]`, `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]`, `@[backend_v2/tests/unit/test_api_clone_endpoints.py]`, `@[backend_v2/tests/unit/test_api_workflow_fail_fast.py]`, `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_input_processing.py]`, `@[backend_v2/tests/unit/test_litellm_redis_timeout.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]`, `@[backend_v2/tests/unit/test_main.py]`, `@[backend_v2/tests/unit/test_organization_service.py]`, `@[backend_v2/tests/unit/test_phase8_documentation_contracts.py]`, `@[backend_v2/tests/unit/test_repositories_v2.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/unit/test_schema_builder.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_tasks.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]` & `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]` | `system_configs` STI table, `SystemConfigUnion`, `SystemConfigID`, `AnySystemConfig`, `AnySystemConfigAdapter`, `SystemConfigCreateDTO`, `SystemConfigUpdateDTO`, `SystemConfigUpsertDTO`, STI `type` discriminator fields on `SystemConfigModelRegistry` and `SystemConfigMCPGateways`, `EntityPrefix.SYSTEM_CONFIG` (`sys_`), duplicate `EntityPrefix.ORG`, unlinked MCP secret `target_identifier`, missing `organization_id` on `SystemConfigMCPGateways`, and banned `ModelProfile.api_key`, `ModelProfile.parsing_mode`, and `LLMProviderConfig.parsing_mode`. | Create `model_registries` (`mrg_`, `slug TEXT`, `name TEXT NOT NULL`, `default_provider TEXT NOT NULL`, `tier_definitions JSONB NOT NULL`, `VIRTUAL` `created_at`) and `mcp_gateways` (`mcp_`, `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE`, `slug TEXT NOT NULL`, `name TEXT NOT NULL`, `auth_header_name TEXT`, `tools JSONB NOT NULL`, `VIRTUAL` `created_at`) with zero `UNIQUE` on `slug`; enforce `parse_prefixed_uuid7` on `SystemConfigModelRegistry.id` (`MODEL_REGISTRY`), `SystemConfigMCPGateways.id` & `MCPAuditTrace.gateway_id` (`MCP_GATEWAY`), and `SystemConfigMCPGateways.organization_id` (`ORGANIZATION`); split `EntityPersistencePort` and `ISystemRepository` while preserving `StudioSystemConfigService` public method names for `model_registry.py` and `mcp_gateways.py` routers; add `tenant_secrets.mcp_gateway_id ON DELETE CASCADE` derived via `parse_prefixed_uuid7`; and ratchet `_QGR030_ENTITY_PREFIXES` (`mrg`, `mcp`, banning `^sys_[0-9a-fA-F]{32}$`). | Preserve `tier_definitions` and `tools` (`list[AllowedMCPTool]`) as strict Pydantic-validated `JSONB` Aggregate Leaves without child EAV tables, and keep `OPAQUE_STRIPE_ID_REGEX` router `Path` bindings untouched in `model_registry.py` and `mcp_gateways.py`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/models/auth.py backend_v2/models/llm.py backend_v2/models/domain/__init__.py backend_v2/models/domain/system_config.py backend_v2/models/dtos/system.py backend_v2/database/interfaces.py backend_v2/database/repositories/system.py backend_v2/database/postgres/entity_adapter/ backend_v2/services/studio/system_config_service.py backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py backend_v2/llm/client.py backend_v2/hooks/llm.py backend_v2/main.py scripts/_ast_guardrails.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ --test --ast-strict --micro` |
| **Step 2.2 (`step_criteria_blocks` & `workflow_step_refs`, Deferrable `default_profile_id`, Typed UUID FKs, `VIRTUAL` `created_at`, Single-UoW `clone_workflow` & `Workflow.version` SQL OCC):** `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/domain/workflow.py#L25-L232]`, `@[backend_v2/models/domain/output_profile.py#L44-L435]`, `@[backend_v2/models/domain/execution.py#L249-L520]`, `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/dtos/output_profile.py]`, `@[backend_v2/models/dtos/trace.py#L46-L63]`, `@[backend_v2/database/repositories/identity.py#L31-L388]`, `@[backend_v2/database/repositories/workflow.py#L26-L512]`, `@[backend_v2/database/repositories/components/prompt_block.py#L16-L200]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L402-L447]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L272-L316]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L322-L441]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/database/repositories/test_identity.py]`, `@[backend_v2/tests/unit/database/repositories/test_report_artifact.py]`, `@[backend_v2/tests/unit/database/repositories/test_workflow.py]`, `@[backend_v2/tests/unit/models/domain/test_workflow.py]`, `@[backend_v2/tests/unit/models/dtos/test_studio.py]`, `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]` & `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]` | Redundant `steps.criteria_block_ids JSONB` column, all 4 Python $O(N)$ full-table delete loops (`PromptBlockRepositoryImpl.delete_prompt_block`, `StudioWorkflowService.delete_step`, `WorkflowRepositoryImpl.delete_step`, `StudioOutputProfileService.delete_output_profile`), permissive `ON DELETE SET NULL` on blueprint FKs, untyped `TEXT` on `*_target_block` and `*.created_by`, physical `created_at` on `executions`/`report_artifacts`/`report_binaries`, dirty-DB SQL `UPDATE`/`DELETE` patches, blind `workflows.version` overwrites, and stale 18-table `CLOSED_POSTGRES_TABLES`. | Drop `steps.criteria_block_ids JSONB` and project ordered `criteria_block_ids` from `step_criteria_blocks` (`ORDER BY scb.position ASC`), syncing `step_criteria_blocks` and deduplicated `workflow_step_refs` (`ON DELETE RESTRICT`) via `UNNEST`; bind `workflows.default_profile_id` as `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` and pre-bind `profile_mapping` (`version=1`) in a single save inside `open_uow_session(self._uow_factory)` in `StudioWorkflowService.clone_workflow`; enforce `parse_prefixed_uuid7` and `UUID` FKs on `variance_target_block`, `user_role_target_block`, `users.created_by`, and `executions.created_by`; enforce `WHERE workflows.version = $6 RETURNING version` SQL OCC (`ErrorCodes.CONFLICT` 409) and re-fetch incremented `version` in `WorkflowRepositoryImpl.update_workflow`; and lock 21-table `CLOSED_POSTGRES_TABLES` in `audit_zero_orm_strictness.py`. | Keep `Workflow.steps` (`list[StepRule]`), `MatrixPromptBlock`, `I18nText`, and `OutputProfile.content_blocks` as typed `JSONB` Aggregate Leaves. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/workflow.py backend_v2/models/domain/output_profile.py backend_v2/models/domain/execution.py backend_v2/models/dtos/studio.py backend_v2/models/dtos/output_profile.py backend_v2/models/dtos/trace.py backend_v2/database/repositories/identity.py backend_v2/database/repositories/workflow.py backend_v2/database/repositories/components/prompt_block.py backend_v2/database/postgres/entity_adapter/ backend_v2/services/studio/workflow_service.py backend_v2/services/studio/output_profile_service.py scripts/audit_zero_orm_strictness.py --test --ast-strict --micro` |
| **Step 2.3 (Source-Level `seed_data.json` Split, Operational Seed/CLI Scripts & Cross-Language Alias Registry):** `@[backend_v2/seed/seed_data.json#L2-L554]`, `@[backend_v2/seed/seed_registry.py]`, `@[backend_v2/seed/run_seed.py]`, `@[scripts/audit_database_atoms.py#audit_collection]`, `@[scripts/audit_dto_parity.py]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/diff_executions.py]`, `@[scripts/run_e2e_variance_test.py]`, `@[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]`, `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`, `@[backend_v2/tests/integration/test_integration_real_llm.py]`, `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/seed/test_seed_registry.py]`, `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dto_parity.py]`, `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`, `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`, `@[backend_v2/tests/unit/scripts/test_diff_executions.py]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`, `@[backend_v2/tests/unit/test_api_seed_mutations.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]` & `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]` | Monolithic `"system_config"` seed collection (`sys_`), STI `"type"` discriminator keys and 12 banned `"parsing_mode": "STRUCTURED_JSON"` entries in `seed_data.json`, stale `EntityPrefix.STEP_REFERENCE` in `prompt_blocks` atom rules, and unmapped `SystemConfigModelRegistry` / `ModelProfile` aliases in `audit_dto_parity.py`. | Create timestamped backup in `backend_v2/seed/backups/`, split `"system_config"` into `"model_registries"` (`mrg_0195f3a0000070008000bf23c2670ad5`, zero `"type"`, zero `"parsing_mode"`) and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`, `"organization_id": "org_0195f3a0000070008000000000000001"`, zero `"type"`), update `workflows[*].model_registry_id` and `workflows[*].mcp_gateway_id` in `@[backend_v2/seed/seed_data.json#L20805-L21600]`, seed `mcp_gateways` before `_seed_local_secrets` (12-table `CANONICAL_SEED_TABLES`), drop `EntityPrefix.STEP_REFERENCE` from `prompt_blocks` rules in `audit_database_atoms.py`, and register `"systemconfigmodelregistry": "modelconfig"` and `"modelprofile": "llmmodelconfig"` in `EXPLICIT_MODEL_ALIASES` inside `audit_dto_parity.py`. | Touch ZERO `system_prompt`, `ai_description`, `instruction_text`, or matrix rubric natural-language coaching texts (`prompt_preservation_mandate`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/seed/ scripts/audit_database_atoms.py scripts/audit_dto_parity.py scripts/sanitize_seed_vault.py scripts/ablation_live_executor.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/seed/ backend_v2/tests/unit/scripts/ backend_v2/tests/unit/test_api_seed_mutations.py backend_v2/tests/unit/test_seed_architectural_guardrails.py --test --ast-strict --micro` |
| **Step 2.4 (Flutter Studio `EntityPrefix`, `ModelConfig` / `LlmModelConfig`, `ModelRegistryView`, `McpGateway` & `OrganizationIamSettingsView` Freezed Parity):** `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/core/api/studio_client_test.dart]`, `@[client_app_v2/test/unit/core/api/studio_client_test.dart]`, `@[client_app_v2/test/features/studio/models/model_config_test.dart]`, `@[client_app_v2/test/features/studio/views/model_registry_view_test.dart]`, `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]`, `@[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`, `@[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]`, `@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart]`, `@[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]`, `@[client_app_v2/test/unit/features/studio/views/widgets/workflow/workflow_general_tab_test.dart]` & `@[client_app_v2/test/models/domain_parity_test.dart]` | Stale `type` discriminator, `apiKey`, and `parsingMode` fields on Flutter `ModelConfig` / `LlmModelConfig` / `ModelRegistryView`, stale `type` discriminator and missing `organizationId` on `McpGateway`, outdated `EntityPrefix` Dart enum values, and legacy `sys_` fixture IDs in Studio and IAM tests. | Synchronize `EntityPrefix` in `enums.dart` (`'mrg'`, `'mcp'`, `'aud'`, `'usg'`, dropping `systemConfig` and duplicate `org`), drop `type` from `ModelConfig` and `McpGateway`, drop `apiKey` and `parsingMode` from `LlmModelConfig` and `ModelRegistryView`, add `@JsonKey(name: 'organization_id') required String organizationId` to `McpGateway` (`disallowUnrecognizedKeys: true`), and synchronize `OrganizationIamSettingsView` and all 14 Flutter Studio/IAM test suites. | Maintain 1:1 DTO parity verified automatically by `audit_dto_parity.py --fail-on-mismatch`, `test_enum_parity.py`, and `domain_parity_test.dart`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/domain/system_config.py]`, `@[backend_v2/models/llm.py#L185-L444]`, `@[backend_v2/seed/seed_registry.py]`, and `@[backend_v2/seed/run_seed.py]`.</action>
    <action>Look forward: Verify Step 2.1 evolves the PostgreSQL 19 DDL and splits `system_configs` into `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`) with zero STI `type` discriminators, `tenant_secrets.mcp_gateway_id ON DELETE CASCADE`, and `QGR030` prefix ratcheting; Step 2.2 adds `step_criteria_blocks` (dropping `steps.criteria_block_ids JSONB`), `workflow_step_refs`, deferrable `workflows.default_profile_id`, typed UUID FKs with `parse_prefixed_uuid7`, `VIRTUAL` `created_at`, single-UoW `clone_workflow` profile binding, `Workflow.version` SQL OCC, and 21-table `audit_zero_orm_strictness.py` enforcement; Step 2.3 executes the `seed_data.json` structural split with timestamped backup, `--dry-run`, `audit_database_atoms.py --strict`, and `audit_dto_parity.py` alias synchronization; and Step 2.4 synchronizes Flutter Studio and IAM Freezed models, views, enums, and tests in a dedicated frontend commit.</action>
    <constraint invariant="prompt_preservation_mandate">Zero qualitative coaching prompts (`system_prompt`, `ai_description`, `instruction_text`, matrix `scales`/`rows`/`columns`) in `backend_v2/seed/seed_data.json` may be altered; create a timestamped backup in `backend_v2/seed/backups/` before editing `seed_data.json`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]</backend>
    <backend>@[backend_v2/models/enums.py#L246-L271]</backend>
    <backend>@[backend_v2/models/auth.py]</backend>
    <backend>@[backend_v2/models/llm.py#L185-L444]</backend>
    <backend>@[backend_v2/models/domain/__init__.py]</backend>
    <backend>@[backend_v2/models/domain/system_config.py]</backend>
    <backend>@[backend_v2/models/domain/workflow.py#L25-L232]</backend>
    <backend>@[backend_v2/models/domain/output_profile.py#L44-L435]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L249-L520]</backend>
    <backend>@[backend_v2/models/dtos/system.py]</backend>
    <backend>@[backend_v2/models/dtos/studio.py]</backend>
    <backend>@[backend_v2/models/dtos/output_profile.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py#L46-L63]</backend>
    <backend>@[backend_v2/database/interfaces.py#L296-L383]</backend>
    <backend>@[backend_v2/database/repositories/identity.py#L31-L388]</backend>
    <backend>@[backend_v2/database/repositories/system.py#L20-L166]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py#L26-L512]</backend>
    <backend>@[backend_v2/database/repositories/components/prompt_block.py#L16-L200]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L402-L447]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L272-L316]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L322-L441]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py#L44-L817]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L49-L990]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py#L26-L369]</backend>
    <backend>@[backend_v2/services/auth/secret_service.py#L140-L1170]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py#L340-L418]</backend>
    <backend>@[backend_v2/llm/client.py#L51-L947]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/main.py#L70-L115]</backend>
    <backend>@[backend_v2/seed/seed_registry.py]</backend>
    <backend>@[backend_v2/seed/run_seed.py]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L2-L554]</backend>
    <backend>@[scripts/_ast_guardrails.py]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py]</backend>
    <backend>@[scripts/audit_dto_parity.py]</backend>
    <backend>@[scripts/audit_database_atoms.py#audit_collection]</backend>
    <backend>@[scripts/sanitize_seed_vault.py]</backend>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[scripts/diff_executions.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/model_config.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/model_registry_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py]</backend>
    <backend>@[backend_v2/tests/conftest.py]</backend>
    <backend>@[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]</backend>
    <backend>@[backend_v2/tests/integration/test_epic_chain_e2e.py]</backend>
    <backend>@[backend_v2/tests/integration/test_integration_real_llm.py]</backend>
    <backend>@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]</backend>
    <backend>@[backend_v2/tests/test_caching_schema_scrub_bug.py]</backend>
    <backend>@[backend_v2/tests/test_fastdev_frozen.py]</backend>
    <backend>@[backend_v2/tests/test_worker_models_used.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_tier4_workflow_leak_bug.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/studio/test_workflows.py]</backend>
    <backend>@[backend_v2/tests/unit/api/routers/test_server_id_authority.py]</backend>
    <backend>@[backend_v2/tests/unit/core/test_redis_security.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_identity.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_report_artifact.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_workflow.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test___init__.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_postgres.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_repository.py]</backend>
    <backend>@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_input_processing.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_interaction_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_linguistics.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_llm.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_matrix_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_scoring.py]</backend>
    <backend>@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_client.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_provider_retry_after.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_source_verification.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_system_config.py]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_workflow.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_mcp.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_studio.py]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_enums.py]</backend>
    <backend>@[backend_v2/tests/unit/models/test_v2_core.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_dto_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_diff_executions.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]</backend>
    <backend>@[backend_v2/tests/unit/seed/test_run_seed.py]</backend>
    <backend>@[backend_v2/tests/unit/seed/test_seed_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/services/auth/test_secret_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/cache/test_cache_init.py]</backend>
    <backend>@[backend_v2/tests/unit/services/cache/test_typed_cache.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_ingress_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_override_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/mcp/test_dispatcher.py]</backend>
    <backend>@[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]</backend>
    <backend>@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_schema_factory.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/test_unmapped_generic_inputs_bug.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_compilation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_lifecycle_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/report/test_report_facade.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_auth_validator.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_simulation_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_system_config_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_workflow_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_execution_resumability.py]</backend>
    <backend>@[backend_v2/tests/unit/services/test_source_verification_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_api_clone_endpoints.py]</backend>
    <backend>@[backend_v2/tests/unit/test_api_seed_mutations.py]</backend>
    <backend>@[backend_v2/tests/unit/test_api_workflow_fail_fast.py]</backend>
    <backend>@[backend_v2/tests/unit/test_auth.py]</backend>
    <backend>@[backend_v2/tests/unit/test_concurrency_fuzzer.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]</backend>
    <backend>@[backend_v2/tests/unit/test_dag_taskgroup.py]</backend>
    <backend>@[backend_v2/tests/unit/test_enum_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/test_input_processing.py]</backend>
    <backend>@[backend_v2/tests/unit/test_litellm_redis_timeout.py]</backend>
    <backend>@[backend_v2/tests/unit/test_llm_context_bounds.py]</backend>
    <backend>@[backend_v2/tests/unit/test_main.py]</backend>
    <backend>@[backend_v2/tests/unit/test_organization_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_phase8_documentation_contracts.py]</backend>
    <backend>@[backend_v2/tests/unit/test_repositories_v2.py]</backend>
    <backend>@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]</backend>
    <backend>@[backend_v2/tests/unit/test_schema_builder.py]</backend>
    <backend>@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]</backend>
    <backend>@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis.py]</backend>
    <backend>@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_execution_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_tasks.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_synthesis_worker.py]</backend>
    <backend>@[backend_v2/tests/unit/workers/test_variance_synthesis.py]</backend>
    <frontend>@[client_app_v2/test/core/models/enums_test.dart]</frontend>
    <frontend>@[client_app_v2/test/core/api/studio_client_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/core/api/studio_client_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/models/model_config_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/model_registry_view_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/studio/views/widgets/workflow/workflow_general_tab_test.dart]</frontend>
    <frontend>@[client_app_v2/test/models/domain_parity_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]` includes the idempotent `DO $$` pre-production cutover gate with zero `-- Phase` or `-- Step` comments (`QGR033`), replaces `system_configs` with `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`) without `UNIQUE` on `slug`, binds `tenant_secrets.mcp_gateway_id ON DELETE CASCADE` (in both `CREATE TABLE` and `ALTER TABLE`), adds `step_criteria_blocks` (dropping `steps.criteria_block_ids JSONB`) and `workflow_step_refs` (`ON DELETE RESTRICT`), sets `workflows.default_profile_id` to `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`, converts `variance_target_block`, `user_role_target_block`, `users.created_by`, and `executions.created_by` to `UUID` FKs, converts `created_at` to `VIRTUAL` across all 16 UUIDv7-PK tables plus `report_binaries` (`uuid_extract_timestamp(report_id)`), adds `CHECK` discriminator constraints on `prompt_blocks.category_id` and `users.role`, adds complete FK/tenant B-Tree indexes, and removes dirty-DB scrubbing blocks while preserving required `ZORM007` `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements.</item>
    <item>`EntityPrefix` defines `MODEL_REGISTRY = "mrg"` and `MCP_GATEWAY = "mcp"` while dropping `SYSTEM_CONFIG` (`sys_`), `SystemConfigUnion`, `SystemConfigID`, `AnySystemConfig`, `AnySystemConfigAdapter`, `SystemConfigCreateDTO`, `SystemConfigUpdateDTO`, `SystemConfigUpsertDTO`, STI `type` discriminator fields, and duplicate `EntityPrefix.ORG`; `ModelProfile.api_key`, `ModelProfile.parsing_mode`, and `LLMProviderConfig.parsing_mode` are removed across Python, Seed Vault, and Flutter Studio; `parse_prefixed_uuid7` enforces exact entity prefixes on all split/FK models and DTOs; `scripts/_ast_guardrails.py` and `scripts/audit_zero_orm_strictness.py` enforce the 21-table Phase 2 topology and `mrg`/`mcp` prefixes; and `workflows` enforces single-statement SQL `WHERE workflows.version = $6 RETURNING version` OCC (`ErrorCodes.CONFLICT` 409).</item>
    <item>`@[backend_v2/seed/seed_data.json#L2-L554]` (`@[backend_v2/seed/seed_data.json#L20805-L21600]`), `seed_registry.py`, `run_seed.py`, and the 4 operational CLI scripts split `"system_config"` into `"model_registries"` (`mrg_0195f3a0000070008000bf23c2670ad5`) and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`, seeded prior to `_seed_local_secrets`) with zero qualitative prompt mutations, passing `run_seed.py local --dry-run` and `audit_database_atoms.py --strict`.</item>
    <item>Flutter `enums.dart`, `model_config.dart`, `model_registry_view.dart`, `mcp_gateway.dart` (`organizationId`, zero `type`), `organization_iam_settings_view.dart`, and `scripts/audit_dto_parity.py` (`EXPLICIT_MODEL_ALIASES`) are 100% synchronized and pass `audit_dto_parity.py --fail-on-mismatch`, `test_enum_parity.py`, and `flutter_audit_loop.py`.</item>
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
    <anti_target>Do NOT add a `UNIQUE` constraint on `model_registries.slug` or `mcp_gateways.slug` (`ZORM007` fatal violation), do NOT declare `ON DELETE RESTRICT DEFERRABLE` on `workflows.default_profile_id` (use `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`), and do NOT add `-- Phase X` or `-- Step Y` comments to `001_pg19_uuidv7_schema.sql` (`QGR033`).</anti_target>
    <anti_target>Do NOT modify `backend_v2/api/routers/studio/model_registry.py` or `backend_v2/api/routers/studio/mcp_gateways.py` (`Path(pattern=OPAQUE_STRIPE_ID_REGEX)` is enforced by `test_router_ssot_guardrails.py`; preserve `StudioSystemConfigService` method names so routers stay untouched).</anti_target>
    <anti_target>Do NOT normalize `ModelRegistry.tier_definitions`, `MCPGateway.tools`, `MatrixPromptBlock`, `I18nText`, `OutputProfile.content_blocks`, or `Workflow.steps` (`list[StepRule]`) into child EAV tables.</anti_target>
    <anti_target>Do NOT modify any `system_prompt`, `ai_description`, `instruction_text`, or matrix rubric text in `backend_v2/seed/seed_data.json` (`prompt_preservation_mandate`).</anti_target>
  </anti_targets>

  <step id="2.1" name="system_configs Split into model_registries (mrg_) &amp; mcp_gateways (mcp_), tenant_secrets.mcp_gateway_id FK, ModelProfile / LLMProviderConfig Cleanup &amp; QGR030 Prefix Ratchet">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/enums.py#L246-L271]`, `@[backend_v2/models/auth.py]`, `@[backend_v2/models/llm.py#L185-L444]`, `@[backend_v2/models/domain/__init__.py]`, `@[backend_v2/models/domain/system_config.py]`, and `@[backend_v2/models/dtos/system.py]`: Prepend the idempotent pre-production cutover `DO $$` block when `information_schema.tables` contains `'system_configs'` (with zero `-- Phase` or `-- Step` comments per `QGR033`); replace `system_configs` with `model_registries` (`MODEL_REGISTRY = "mrg"`, `slug TEXT`, `name TEXT NOT NULL`, `default_provider TEXT NOT NULL`, `tier_definitions JSONB NOT NULL`, `VIRTUAL` `created_at`) and `mcp_gateways` (`MCP_GATEWAY = "mcp"`, `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE`, `slug TEXT NOT NULL`, `name TEXT NOT NULL`, `endpoint_url TEXT NOT NULL`, `transport_type TEXT NOT NULL`, `auth_type TEXT NOT NULL`, `auth_env_var TEXT`, `auth_header_name TEXT`, `timeout_seconds INTEGER NOT NULL CHECK (timeout_seconds >= 1 AND timeout_seconds <= 300)`, `tools JSONB NOT NULL`, `VIRTUAL` `created_at`) with zero `UNIQUE` constraint on `slug` plus `idx_mcp_gateways_org_id`. Drop `SYSTEM_CONFIG` (`sys_`), `SystemConfigUnion`, `SystemConfigID`, `AnySystemConfig`, `AnySystemConfigAdapter`, `SystemConfigCreateDTO`, `SystemConfigUpdateDTO`, `SystemConfigUpsertDTO`, STI `type` discriminator fields (and `title=` in `ConfigDict`) from `SystemConfigModelRegistry` and `SystemConfigMCPGateways`, and duplicate `ORG` from `EntityPrefix`. Add dedicated `ModelRegistryCreateDTO`, `ModelRegistryUpdateDTO`, `ModelRegistryUpsertDTO`, `MCPGatewayCreateDTO`, `MCPGatewayUpdateDTO`, and `MCPGatewayUpsertDTO` in `models/dtos/system.py`. Add required `organization_id` (`OPAQUE_STRIPE_ID_REGEX` + `parse_prefixed_uuid7(v, EntityPrefix.ORGANIZATION)`) to `SystemConfigMCPGateways`, enforce `parse_prefixed_uuid7` on `SystemConfigModelRegistry.id` (`MODEL_REGISTRY`), `SystemConfigMCPGateways.id` (`MCP_GATEWAY`), `MCPAuditTrace.gateway_id` (`MCP_GATEWAY`), and `Organization.created_by` / `User.created_by` / `UserCreate.created_by` (`USER` in `models/auth.py`). Drop `ModelProfile.api_key`, `ModelProfile.parsing_mode`, and `LLMProviderConfig.parsing_mode`. Add `mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE` to `tenant_secrets` (in both `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE tenant_secrets ADD COLUMN IF NOT EXISTS`) with a SQL `CHECK` constraint enforcing `(scope = 'mcp_gateway' AND mcp_gateway_id IS NOT NULL) OR (scope IN ('llm_provider', 'telemetry') AND mcp_gateway_id IS NULL)` plus `idx_tenant_secrets_org_id` and `idx_tenant_secrets_mcp_gateway_id`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/interfaces.py#L296-L383]`, `@[backend_v2/database/repositories/system.py#L20-L166]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L143-L183]`, `@[backend_v2/services/studio/system_config_service.py#L44-L817]`, `@[backend_v2/services/auth/secret_service.py#L140-L1170]`, `@[backend_v2/services/cache/typed_cache.py#L340-L418]`, `@[backend_v2/llm/client.py#L51-L947]`, `@[backend_v2/hooks/llm.py]`, `@[backend_v2/main.py#L70-L115]`, and `@[scripts/_ast_guardrails.py]`: Replace `hydrate_system_config_row`, `upsert_system_config_row`, `delete_system_config_row`, `get_system_config_row`, `list_system_configs_rows`, `upsert_system_config`, `list_system_configs`, and `create_system_config` with dedicated `model_registry` and `mcp_gateway` functions/methods across `iam_and_system_stage.py`, `PostgresEntityAdapter`, `EntityPersistencePort`, and `ISystemRepository` (`delete_model_registry` and `delete_mcp_gateways`), while preserving `StudioSystemConfigService` method names (`get_all_system_configs`, `get_system_config`, `create_system_config_draft`, `save_system_config`, `delete_system_config`, `clone_system_config` for model registries and `list_mcp_gateways`, `get_mcp_gateways`, `create_mcp_gateway_draft` populating `organization_id=SystemOrganizations.ROOT_SYSTEM.value`, `save_mcp_gateways`, `delete_mcp_gateway`, `clone_mcp_gateways` preserving `organization_id`) so `model_registry.py` and `mcp_gateways.py` routers remain untouched. Derive SQL `mcp_gateway_id` in `upsert_tenant_secret_row` via `parse_prefixed_uuid7(secret.target_identifier, EntityPrefix.MCP_GATEWAY)` when `scope == SecretScope.MCP_GATEWAY` (else `None`), validate `MCP_GATEWAY` (`mcp_<hex32>`) in `SecretService`, update `MCPGatewayCache` (`typed_cache.py`), update `CANONICAL_SEED_TABLES` (12 tables replacing `"system_configs"` with `"model_registries"` and `"mcp_gateways"`), `verify_seed_table_counts_rows`, and `main.py`, remove `api_key` and `parsing_mode` references in `llm/client.py` and `hooks/llm.py`, and update `_QGR030_ENTITY_PREFIXES` in `scripts/_ast_guardrails.py` to add `"mrg"`, `"mcp"`, `"tbr"`, `"inv"`, `"sec"`, and `"tsk"` while banning retired `^sys_[0-9a-fA-F]{32}$` literals and `SYSTEM_CONFIG` references.</action>
    <action>3. `[MODIFY]` `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py]`, `@[backend_v2/tests/conftest.py]`, `@[backend_v2/tests/test_caching_schema_scrub_bug.py]`, `@[backend_v2/tests/test_fastdev_frozen.py]`, `@[backend_v2/tests/test_worker_models_used.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_mcp_gateways.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_model_registry.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_tier4_workflow_leak_bug.py]`, `@[backend_v2/tests/unit/api/routers/studio/test_workflows.py]`, `@[backend_v2/tests/unit/api/routers/test_server_id_authority.py]`, `@[backend_v2/tests/unit/core/test_redis_security.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, `@[backend_v2/tests/unit/database/repositories/test_system.py]`, `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`, `@[backend_v2/tests/unit/database/test___init__.py]`, `@[backend_v2/tests/unit/database/test_postgres.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`, `@[backend_v2/tests/unit/hooks/test_input_processing.py]`, `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`, `@[backend_v2/tests/unit/hooks/test_linguistics.py]`, `@[backend_v2/tests/unit/hooks/test_llm.py]`, `@[backend_v2/tests/unit/hooks/test_matrix_hook.py]`, `@[backend_v2/tests/unit/hooks/test_scoring.py]`, `@[backend_v2/tests/unit/hooks/test_source_verification_hook.py]`, `@[backend_v2/tests/unit/llm/test_client.py]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py]`, `@[backend_v2/tests/unit/models/domain/test_source_verification.py]`, `@[backend_v2/tests/unit/models/domain/test_system_config.py]`, `@[backend_v2/tests/unit/models/dtos/test_mcp.py]`, `@[backend_v2/tests/unit/models/dtos/test_system.py]`, `@[backend_v2/tests/unit/models/test_enums.py]`, `@[backend_v2/tests/unit/models/test_v2_core.py]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/services/cache/test_cache_init.py]`, `@[backend_v2/tests/unit/services/cache/test_typed_cache.py]`, `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`, `@[backend_v2/tests/unit/services/execution/test_facade.py]`, `@[backend_v2/tests/unit/services/execution/test_ingress_service.py]`, `@[backend_v2/tests/unit/services/execution/test_override_service.py]`, `@[backend_v2/tests/unit/services/mcp/test_dispatcher.py]`, `@[backend_v2/tests/unit/services/mcp/test_generic_mcp_client.py]`, `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`, `@[backend_v2/tests/unit/services/orchestrator/anchor_validation/test_lexical_matcher.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_blueprint_and_metadata_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_engine_retry_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_prompt_and_schema_stage.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_strategies_facade.py]`, `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_compiler.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_orchestrator_init.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_schema_factory.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_state_reducer.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller_wiring.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_tier4_matrix_distribution_regression.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_unmapped_generic_inputs_bug.py]`, `@[backend_v2/tests/unit/services/report/test_compilation_service.py]`, `@[backend_v2/tests/unit/services/report/test_lifecycle_service.py]`, `@[backend_v2/tests/unit/services/report/test_report_facade.py]`, `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, `@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`, `@[backend_v2/tests/unit/services/studio/test_simulation_service.py]`, `@[backend_v2/tests/unit/services/studio/test_system_config_service.py]`, `@[backend_v2/tests/unit/services/test_blueprint.py]`, `@[backend_v2/tests/unit/services/test_blueprint_combined_costs.py]`, `@[backend_v2/tests/unit/services/test_blueprint_sdui_crash.py]`, `@[backend_v2/tests/unit/services/test_execution.py]`, `@[backend_v2/tests/unit/services/test_execution_resumability.py]`, `@[backend_v2/tests/unit/services/test_source_verification_service.py]`, `@[backend_v2/tests/unit/test_api_clone_endpoints.py]`, `@[backend_v2/tests/unit/test_api_workflow_fail_fast.py]`, `@[backend_v2/tests/unit/test_auth.py]`, `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`, `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`, `@[backend_v2/tests/unit/test_dag_taskgroup.py]`, `@[backend_v2/tests/unit/test_input_processing.py]`, `@[backend_v2/tests/unit/test_litellm_redis_timeout.py]`, `@[backend_v2/tests/unit/test_llm_context_bounds.py]`, `@[backend_v2/tests/unit/test_main.py]`, `@[backend_v2/tests/unit/test_organization_service.py]`, `@[backend_v2/tests/unit/test_phase8_documentation_contracts.py]`, `@[backend_v2/tests/unit/test_repositories_v2.py]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]`, `@[backend_v2/tests/unit/test_schema_builder.py]`, `@[backend_v2/tests/unit/test_synthesis_distiller_hook.py]`, `@[backend_v2/tests/unit/test_worker.py]`, `@[backend_v2/tests/unit/test_worker_synthesis.py]`, `@[backend_v2/tests/unit/test_worker_synthesis_accumulation.py]`, `@[backend_v2/tests/unit/workers/test_execution_worker.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_reducers.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_tasks.py]`, `@[backend_v2/tests/unit/workers/test_synthesis_worker.py]`, and `@[backend_v2/tests/unit/workers/test_variance_synthesis.py]`: Migrate all factories (`SystemConfigModelRegistryFactory`, `SystemConfigMCPGatewaysFactory` with `organization_id`, `MCPAuditTraceFactory`, `WorkflowFactory`, `LLMProviderConfigFactory`), `InMemorySystemRepository`, `InMemoryEntityAdapter`, `conftest.py`, and hermetic unit tests from `sys_` / `SYSTEM_CONFIG` / `parsing_mode` / `api_key` to `mrg_` (`MODEL_REGISTRY`) and `mcp_` (`MCP_GATEWAY`), adding positive, negative, and boundary unit tests for `mrg_`/`mcp_` prefix enforcement and `tenant_secrets.mcp_gateway_id` cascading cleanup.</action>
    <constraint invariant="canonical_id_relational_sovereignty_and_zero_default_guardrails">`workflows.model_registry_id` MUST validate `mrg_<hex32>` and `workflows.mcp_gateway_id` MUST validate `mcp_<hex32>` with `ON DELETE RESTRICT` in PostgreSQL 19.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/models/auth.py backend_v2/models/llm.py backend_v2/models/domain/__init__.py backend_v2/models/domain/system_config.py backend_v2/models/dtos/system.py backend_v2/database/interfaces.py backend_v2/database/repositories/system.py backend_v2/database/postgres/entity_adapter/ backend_v2/services/studio/system_config_service.py backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py backend_v2/llm/client.py backend_v2/hooks/llm.py backend_v2/main.py scripts/_ast_guardrails.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/models/dtos/test_system.py backend_v2/tests/unit/models/domain/test_system_config.py backend_v2/tests/unit/models/test_enums.py backend_v2/tests/unit/database/repositories/test_system.py backend_v2/tests/unit/database/repositories/test_system_model_registry.py backend_v2/tests/unit/scripts/test_ast_guardrails.py --test --ast-strict --micro</audit_command>
  </step>

  <step id="2.2" name="Junction Tables (step_criteria_blocks &amp; workflow_step_refs), Deferrable default_profile_id, Typed UUID FKs, VIRTUAL created_at, Single-UoW clone_workflow &amp; Workflow.version SQL OCC">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L621]`, `@[backend_v2/models/domain/workflow.py#L25-L232]`, `@[backend_v2/models/domain/output_profile.py#L44-L435]`, `@[backend_v2/models/domain/execution.py#L249-L520]`, `@[backend_v2/models/dtos/studio.py]`, `@[backend_v2/models/dtos/output_profile.py]`, and `@[backend_v2/models/dtos/trace.py#L46-L63]`: Drop redundant `steps.criteria_block_ids JSONB` from `steps` and add `step_criteria_blocks` (`step_id UUID NOT NULL REFERENCES steps(id) ON DELETE CASCADE`, `prompt_block_id UUID NOT NULL REFERENCES prompt_blocks(id) ON DELETE RESTRICT`, `position INTEGER NOT NULL CHECK (position >= 0)`, `PRIMARY KEY (step_id, prompt_block_id)`) and `workflow_step_refs` (`workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE`, `step_id UUID NOT NULL REFERENCES steps(id) ON DELETE RESTRICT`, `PRIMARY KEY (workflow_id, step_id)`). Upgrade `steps.role_block_id`, `steps.extraction_protocol_block_id`, `steps.execution_persona_block_id`, `workflows.model_registry_id` (`REFERENCES model_registries(id)`), and `workflows.mcp_gateway_id` (`REFERENCES mcp_gateways(id)`) to `ON DELETE RESTRICT`; add `FOREIGN KEY (default_profile_id) REFERENCES output_profiles(id) ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` on `workflows`; convert `output_profiles.variance_target_block` and `output_profiles.user_role_target_block` from `TEXT` to `UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT`; convert `users.created_by` and `executions.created_by` from `TEXT` to `UUID REFERENCES users(id) ON DELETE SET NULL`; convert `executions.created_at`, `report_artifacts.created_at`, and `report_binaries.created_at` (`uuid_extract_timestamp(report_id)`) to `TIMESTAMPTZ GENERATED ALWAYS AS (...) VIRTUAL`; add SQL `CHECK` discriminator constraints on `prompt_blocks.category_id IN ('matrix', 'agent_role', 'system_rule', 'protocol', 'runtime_variables', 'execution_persona')` and `users.role IN ('ROOT', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER')`; add complete B-Tree indexes across all Foreign Key and `organization_id` columns; and remove dirty-DB `UPDATE`/`DELETE` scrubbing blocks while preserving the `ZORM007` idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` statements. Enforce `parse_prefixed_uuid7` validators on `Workflow` / `WorkflowCreateDTO` / `WorkflowUpdateDTO` (`model_registry_id` -> `MODEL_REGISTRY`, `mcp_gateway_id` -> `MCP_GATEWAY`), `OutputProfile` / `OutputProfileCreateDTO` / `OutputProfileUpdateDTO` (`variance_target_block` and `user_role_target_block` -> `PROMPT_BLOCK`), and `ExecutionRecord.created_by` / `ExecutionCreateDTO.created_by` (`USER`).</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/repositories/identity.py#L31-L388]`, `@[backend_v2/database/repositories/workflow.py#L26-L512]`, `@[backend_v2/database/repositories/components/prompt_block.py#L16-L200]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L402-L447]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L272-L316]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L322-L441]`, `@[backend_v2/services/studio/workflow_service.py#L49-L990]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L369]`, and `@[scripts/audit_zero_orm_strictness.py]`: Project ordered `criteria_block_ids` from `step_criteria_blocks` (`ORDER BY scb.position ASC`) in `_GET_STEP_SQL` and `_LIST_STEPS_SQL` and synchronize `step_criteria_blocks` and deduplicated `workflow_step_refs` atomically via `UNNEST` inside `upsert_step_row` and `upsert_workflow_row`; drop all 4 full-table Python delete loops across `PromptBlockRepositoryImpl.delete_prompt_block`, `StudioWorkflowService.delete_step`, `WorkflowRepositoryImpl.delete_step`, and `StudioOutputProfileService.delete_output_profile`; update `IdentityRepositoryImpl` for `usr_<hex32>` `created_by` validation and parse/format `users.created_by` and `executions.created_by` via `_parse_optional_uuid7(..., EntityPrefix.USER)` and `_format_optional_uuid7(..., EntityPrefix.USER)` plus `variance_target_block` / `user_role_target_block` via `EntityPrefix.PROMPT_BLOCK`; enforce single-statement SQL Optimistic Concurrency Control (`ON CONFLICT (id) DO UPDATE SET ..., version = workflows.version + 1 WHERE workflows.version = $6 RETURNING version`) on `workflows` in `upsert_workflow_row` (raising `AppException(ErrorCodes.CONFLICT, status_code=409)` when `None` is returned), re-fetch the persisted workflow in `WorkflowRepositoryImpl.update_workflow` so callers receive the SQL-incremented `version`, and pre-generate `profile_mapping` in `StudioWorkflowService.clone_workflow` so the cloned workflow is saved once (`version=1`) with its target `default_profile_id` inside `open_uow_session(self._uow_factory)` before deferred FK commit; and update `scripts/audit_zero_orm_strictness.py` to enforce the 21-table `CLOSED_POSTGRES_TABLES`, 16-table `CANONICAL_ENTITY_PK_TABLES` (excluding composite-PK `step_criteria_blocks` and `workflow_step_refs`), `CANONICAL_NAMED_ENTITY_TABLES` (`model_registries`, `mcp_gateways`), and `APPROVED_ADAPTER_RECORD_COLUMNS`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_output_profile.py]`, `@[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py]`, `@[backend_v2/tests/unit/database/repositories/test_identity.py]`, `@[backend_v2/tests/unit/database/repositories/test_report_artifact.py]`, `@[backend_v2/tests/unit/database/repositories/test_workflow.py]`, `@[backend_v2/tests/unit/models/domain/test_workflow.py]`, `@[backend_v2/tests/unit/models/dtos/test_studio.py]`, `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`, and `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`: Add positive, negative, and boundary unit tests for `UNNEST` junction synchronization, `ON DELETE RESTRICT` `SQLSTATE 23503 -> DELETE_BLOCKED_BY_USAGE` translation, single-save `clone_workflow` (`version=1`), stale `Workflow.version` `CONFLICT` (`409`), and 21-table `audit_zero_orm_strictness.py` checks.</action>
    <constraint invariant="uow_transactional_concurrency_mandate">Concurrent `save_workflow` updates with a stale `version` MUST fail fast with `AppException(ErrorCodes.CONFLICT, status_code=409)` via atomic SQL `WHERE workflows.version = $6 RETURNING version`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/workflow.py backend_v2/models/domain/output_profile.py backend_v2/models/domain/execution.py backend_v2/models/dtos/studio.py backend_v2/models/dtos/output_profile.py backend_v2/models/dtos/trace.py backend_v2/database/repositories/identity.py backend_v2/database/repositories/workflow.py backend_v2/database/repositories/components/prompt_block.py backend_v2/database/postgres/entity_adapter/ backend_v2/services/studio/workflow_service.py backend_v2/services/studio/output_profile_service.py scripts/audit_zero_orm_strictness.py backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py backend_v2/tests/unit/database/repositories/test_workflow.py backend_v2/tests/unit/services/studio/test_workflow_service.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py --test --ast-strict --micro</audit_command>
  </step>

  <step id="2.3" name="Source-Level seed_data.json Structural Split (model_registries &amp; mcp_gateways), Operational Seed Scripts &amp; DTO Parity Registry">
    <action>1. `[MODIFY]` `@[backend_v2/seed/seed_data.json#L2-L554]`, `@[backend_v2/seed/seed_registry.py]`, `@[backend_v2/seed/run_seed.py]`, `@[scripts/audit_database_atoms.py#audit_collection]`, `@[scripts/audit_dto_parity.py]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/diff_executions.py]`, and `@[scripts/run_e2e_variance_test.py]`: Store a timestamped backup copy in `backend_v2/seed/backups/` (`03_seed_vault.md` Step `2_backup`), split `"system_config"` in `@[backend_v2/seed/seed_data.json#L2-L554]`, `seed_registry.py`, `run_seed.py`, and the 4 operational CLI scripts into `"model_registries"` (`mrg_0195f3a0000070008000bf23c2670ad5`, removing `"type": "model_registry"` and all 12 banned `"parsing_mode": "STRUCTURED_JSON"` entries) and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`, removing `"type": "mcp_gateways"` and adding `"organization_id": "org_0195f3a0000070008000000000000001"`), update `workflows[*].model_registry_id` and `workflows[*].mcp_gateway_id` references in `@[backend_v2/seed/seed_data.json#L20805-L21600]` plus `default_mcp_gateway` target resolution in `run_seed.py` (`mcp_0195f3a00000700080008172bda70c86`), ensure `run_seed.py` seeds `mcp_gateways` prior to `_seed_local_secrets`, drop stale `EntityPrefix.STEP_REFERENCE` from `prompt_blocks` validation and update the 9-collection `SEED_COLLECTION_ALLOWED_PREFIXES` in `audit_database_atoms.py`, and register `"systemconfigmodelregistry": "modelconfig"` and `"modelprofile": "llmmodelconfig"` in `EXPLICIT_MODEL_ALIASES` inside `scripts/audit_dto_parity.py`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]`, `@[backend_v2/tests/integration/test_epic_chain_e2e.py]`, `@[backend_v2/tests/integration/test_integration_real_llm.py]`, `@[backend_v2/tests/integration/test_tavily_e2e_full_pipeline.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/seed/test_seed_registry.py]`, `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`, `@[backend_v2/tests/unit/scripts/test_audit_dto_parity.py]`, `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`, `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`, `@[backend_v2/tests/unit/scripts/test_diff_executions.py]`, `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`, `@[backend_v2/tests/unit/test_api_seed_mutations.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, and `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py]`: Update seed, script, enum-parity, and integration test suites for the 9-collection `SeedCollectionName` registry (`model_registries` + `mcp_gateways`), pre-secret `mcp_gateways` seeding order, `EXPLICIT_MODEL_ALIASES` DTO parity, and `prompt_blocks` prefix strictness.</action>
    <constraint invariant="live_database_mutation">Validate `seed_data.json` 100% in-memory via `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict` before any database sync; restore backup immediately if any check fails.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/seed/ scripts/audit_database_atoms.py scripts/audit_dto_parity.py scripts/sanitize_seed_vault.py scripts/ablation_live_executor.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/seed/ backend_v2/tests/unit/scripts/ backend_v2/tests/unit/test_api_seed_mutations.py backend_v2/tests/unit/test_seed_architectural_guardrails.py --test --ast-strict --micro</audit_command>
  </step>

  <step id="2.4" name="Flutter Studio EntityPrefix, ModelConfig / LlmModelConfig, ModelRegistryView, McpGateway &amp; OrganizationIamSettingsView Freezed Parity">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`, and `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`: Synchronize `EntityPrefix` in `enums.dart` (`'mrg'`, `'mcp'`, `'aud'`, `'usg'`, dropping `systemConfig` and duplicate `org`), remove the `type` discriminator field from `ModelConfig` (`model_config.dart`) and `McpGateway` (`mcp_gateway.dart`), remove `apiKey` and `parsingMode` from `LlmModelConfig` (`model_config.dart`) and `ModelRegistryView` (`model_registry_view.dart`), add `@JsonKey(name: 'organization_id') required String organizationId` to `McpGateway` (`mcp_gateway.dart`), and synchronize `OrganizationIamSettingsView` (`organization_iam_settings_view.dart`) with `McpGateway`.</action>
    <action>2. `[MODIFY]` `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/core/api/studio_client_test.dart]`, `@[client_app_v2/test/unit/core/api/studio_client_test.dart]`, `@[client_app_v2/test/features/studio/models/model_config_test.dart]`, `@[client_app_v2/test/features/studio/views/model_registry_view_test.dart]`, `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]`, `@[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`, `@[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]`, `@[client_app_v2/test/features/studio/views/widgets/mcp_tool_params_panel_test.dart]`, `@[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]`, `@[client_app_v2/test/unit/features/studio/views/widgets/workflow/workflow_general_tab_test.dart]`, and `@[client_app_v2/test/models/domain_parity_test.dart]`: Regenerate Freezed/JSON artifacts and update all 14 Flutter unit, widget, and domain parity test suites for `mrg_`/`mcp_` IDs, required `McpGateway.organizationId`, removal of `type`, `parsingMode`, and `apiKey` under `disallowUnrecognizedKeys: true`, and 1:1 `test_enum_parity.py` and `audit_dto_parity.py --fail-on-mismatch` alignment.</action>
    <constraint invariant="anti_semantic_drift_renaming">Stage and commit Backend (`Step 2.1`–`Step 2.3`) and Frontend (`Step 2.4`) changes in separate atomic commits with regenerated `.freezed.dart` and `.g.dart` siblings so `audit_dto_parity.py --fail-on-mismatch` and `flutter_audit_loop.py` pass 100%.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_model_registry_and_mcp_gateway_roundtrip_and_fk_restrict" category="positive">
      <input>Valid `SystemConfigModelRegistry` (`mrg_<hex32>`) and `SystemConfigMCPGateways` (`mcp_<hex32>`, `organization_id="org_0195f3a0000070008000000000000001"`) built via `ModelFactory` and referenced by `WorkflowFactory.build()`</input>
      <expected>Roundtrips both models without loss; attempting to delete a referenced `model_registry` or `mcp_gateway` raises `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)`</expected>
    </test>
    <test name="test_model_profile_and_system_configs_reject_banned_api_key_parsing_mode_and_type_fields" category="negative">
      <input>`ModelProfile.model_validate` called with `"api_key": "sk-..."` or `"parsing_mode": "STRUCTURED_JSON"`, or `SystemConfigModelRegistry.model_validate` / `SystemConfigMCPGateways.model_validate` called with legacy `"type"` discriminator</input>
      <expected>Fails fast with Pydantic `ValidationError` under `ConfigDict(extra="forbid", strict=True)`</expected>
    </test>
    <test name="test_workflow_model_registry_id_rejects_mcp_prefix_and_vice_versa" category="negative">
      <input>`WorkflowFactory.build` / `Workflow.model_validate` called with `model_registry_id="mcp_..."` or `mcp_gateway_id="mrg_..."`</input>
      <expected>Raises `ValidationError` via `parse_prefixed_uuid7` on cross-entity prefix mismatch</expected>
    </test>
    <test name="test_tenant_secret_mcp_gateway_cascade_delete_cleans_up_encrypted_secret" category="positive">
      <input>Unreferenced custom `SystemConfigMCPGateways` (`mcp_<hex32>`) with bound `TenantSecretDTO` (`scope=SecretScope.MCP_GATEWAY`, `mcp_gateway_id`) deleted</input>
      <expected>Cascades deletion of the associated `tenant_secrets` row while leaving `llm_provider` and `telemetry` secrets intact</expected>
    </test>
    <test name="test_upsert_workflow_stale_version_raises_conflict_409_and_increments_on_match" category="boundary">
      <input>Persisted `Workflow` at `version=1` updated twice expecting `version=1`</input>
      <expected>First update returns SQL-incremented `version=2`; second stale update fails fast with `AppException(ErrorCodes.CONFLICT, status_code=409)`</expected>
    </test>
    <test name="test_step_criteria_blocks_and_workflow_step_refs_block_referenced_deletes" category="negative">
      <input>Attempt to delete a `PromptBlock` referenced in `Step.criteria_block_ids` or a `Step` referenced in `Workflow.steps[*].task_blueprint`, or delete `Workflow.default_profile_id`</input>
      <expected>Raises `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)` via `SQLSTATE 23503` without Python full-table scans</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 2 seed pre-flight, Zero-ORM strictness, DTO parity &amp; Macro backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/ backend_v2/llm/ backend_v2/hooks/llm.py backend_v2/services/studio/ backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py backend_v2/main.py backend_v2/seed/ scripts/_ast_guardrails.py scripts/audit_zero_orm_strictness.py scripts/audit_dto_parity.py scripts/audit_database_atoms.py scripts/sanitize_seed_vault.py scripts/ablation_live_executor.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/conftest.py backend_v2/tests/unit/ backend_v2/tests/integration/ --test --ast-strict`.</action>
    <action>Run Phase 2 Macro Flutter quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </validation_gate>
</execution_protocol>
