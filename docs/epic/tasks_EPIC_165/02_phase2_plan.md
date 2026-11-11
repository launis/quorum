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

# EPIC 165 - Phase 2: 22-Table PostgreSQL 19 DDL Evolution, `system_configs` Split (`model_registries` & `mcp_gateways`), Junction Tables (`step_criteria_blocks` & `workflow_step_refs`), `Workflow.version` SQL OCC & Typed UUID Foreign Keys

**Overview:** Evolve `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` to the closed 22-table PostgreSQL 19 UUIDv7 topology with an idempotent pre-production cutover `DO $$` block, split the Single-Table Inheritance `system_configs` table and `"system_config"` seed collection (`@[backend_v2/seed/seed_data.json#L1-L50]`, `@[backend_v2/seed/seed_data.json#L1-L260]`) into dedicated `model_registries` (`EntityPrefix.MODEL_REGISTRY = "mrg"`) and `mcp_gateways` (`EntityPrefix.MCP_GATEWAY = "mcp"`), bind `tenant_secrets.mcp_gateway_id` (`ON DELETE CASCADE`), drop banned `ModelProfile.api_key` and `ModelProfile.parsing_mode` fields across Python, Seed Vault, and Flutter Studio (`@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`), add normalized `step_criteria_blocks` and `workflow_step_refs` junction/projection tables (`ON DELETE RESTRICT`) plus deferrable `workflows.default_profile_id` (`ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`), convert `output_profiles.*_target_block` and `*.created_by` to typed `UUID` Foreign Keys, convert `created_at` to `VIRTUAL` UUIDv7 extraction across all 16 UUIDv7-PK tables, and enforce single-statement SQL Optimistic Concurrency Control (`WHERE version = $2`) on `workflows`.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 2 Forensic Context, Complexity Slayer & Evolved 22-Table SQL DDL (Verbatim from EPIC 165)

### Forensic Findings 3 & 6 (Verbatim)
* **Finding 3 [P1 HIGH] — `system_configs` Single-Table Inheritance Kitchen Sink & `seed_data.json` Schema Drift:**
  * Forensic anchors: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` (lines 82–105 and 179–180), `@[backend_v2/models/domain/system_config.py#L151-L208]` and `@[backend_v2/models/domain/system_config.py#L383-L443]`, `@[backend_v2/seed/seed_registry.py#L23-L34]`, and `@[backend_v2/seed/seed_data.json#L1-L50]` (`@[backend_v2/seed/seed_data.json#L1-L260]`).
  * Root cause: Persistence and seeding cram `SystemConfigModelRegistry` and `SystemConfigMCPGateways` into one `system_configs` table under shared `sys_` prefix with zero shared domain columns, cross-type FK ambiguity on `workflows.model_registry_id` and `workflows.mcp_gateway_id`, unlinked string-only `target_identifier` for `scope = 'mcp_gateway'` in `tenant_secrets`, and banned `ModelProfile.api_key` and `ModelProfile.parsing_mode` fields (including 12 `"parsing_mode": "STRUCTURED_JSON"` occurrences in `@[backend_v2/seed/seed_data.json#L17-L205]`).
* **Finding 6 [P2 MEDIUM] — Permissive `SET NULL` Blueprint FKs, Untyped `TEXT` IDs, Non-Virtual `created_at` & Missing Indexes:**
  * Forensic anchors: `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/repositories/components/prompt_block.py#L18-L268]`, and `@[scripts/audit_database_atoms.py#L328-L786]`.
  * Concrete gaps closed in Phase 2: (1) upgrade permissive `ON DELETE SET NULL` on `steps.*_block_id` and `workflows.*_id` to `ON DELETE RESTRICT`, (2) bind circular `workflows.default_profile_id` as `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` and convert `output_profiles.variance_target_block`, `output_profiles.user_role_target_block`, `users.created_by`, and `executions.created_by` from `TEXT` to typed `UUID` Foreign Keys, (3) convert physical `created_at` on `executions` and `report_artifacts` to `GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL` and remove dirty-DB `UPDATE`/`DELETE` SQL scrubbing blocks, (4) add complete B-Tree indexes across all FK and `organization_id` columns, and (5) replace Python full-table delete loops on `criteria_block_ids` and `workflows.steps[*].task_blueprint` with `step_criteria_blocks` and `workflow_step_refs` (`ON DELETE RESTRICT`).

### Seven Aggregate Leaf Structures That MUST NOT Be Over-Normalized (Section 2.1.1)
1. Cohort assignments (`execution_assignments.batch_id` + `task_brief_snapshot JSONB`).
2. `I18nText` localized maps (`dict[SystemLocale, str]`).
3. `MatrixPromptBlock` rubric hierarchy (`scales`, `rows`, `columns`, `TDAAssertion`, `ContrastiveExample`).
4. `OutputProfile.content_blocks` (`AnySduiBlock`) and `Workflow.expected_inputs` (`ExpectedInput`).
5. `Workflow.steps` (`list[StepRule]` DAG canvas topology backed by `workflow_step_refs`).
6. 1:1 cold `lz4` TOAST sidecars (`report_binaries` and `execution_payloads`).
7. Flat FinOps scalar columns on `executions`.

### Canonical PostgreSQL 19 22-Table DDL Specification (Section 1.4.1 Verbatim)

```sql
-- 0. Idempotent Pre-Production Schema Cutover Gate (when legacy STI system_configs exists on local Docker volumes)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'system_configs'
    ) THEN
        DROP TABLE IF EXISTS
            report_binaries, report_artifacts, quorum_edges, quorum_nodes,
            execution_assignments, execution_payloads, executions,
            workflow_step_refs, step_criteria_blocks, output_profiles,
            workflows, steps, task_briefs, prompt_blocks,
            tenant_secrets, mcp_gateways, model_registries, system_configs,
            audit_logs, usage_records, invitations, users, organizations
        CASCADE;
    END IF;
END $$;

-- 1. model_registries (mrg_<hex32>) & mcp_gateways (mcp_<hex32>) replacing system_configs
-- Note: Zero UNIQUE constraint on slug (enforced by ZORM007); name is TEXT NOT NULL matching SystemConfigModelRegistry / SystemConfigMCPGateways.
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

-- 2. tenant_secrets with cascading mcp_gateway_id Foreign Key (declared in CREATE TABLE + ALTER TABLE for ZORM007 parity)
ALTER TABLE tenant_secrets
    ADD COLUMN IF NOT EXISTS mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_org_id ON tenant_secrets(organization_id);
CREATE INDEX IF NOT EXISTS idx_tenant_secrets_mcp_gateway_id ON tenant_secrets(mcp_gateway_id);

-- 3. step_criteria_blocks, workflow_step_refs & Deferrable Circular workflows.default_profile_id FK
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

-- Circular FK workflows.default_profile_id -> output_profiles(id) uses ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED
-- (PostgreSQL 19 never defers ON DELETE RESTRICT; NO ACTION DEFERRABLE defers intra-transaction checks to COMMIT while raising SQLSTATE 23503 on orphan deletes).
ALTER TABLE workflows
    DROP CONSTRAINT IF EXISTS workflows_default_profile_id_fkey,
    ADD CONSTRAINT workflows_default_profile_id_fkey
        FOREIGN KEY (default_profile_id) REFERENCES output_profiles(id)
        ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/models/enums.py#L246-L269]`
- `[MODIFY] @[backend_v2/models/domain/__init__.py]`
- `[MODIFY] @[backend_v2/models/domain/system_config.py#L151-L208]`
- `[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L232]`
- `[MODIFY] @[backend_v2/models/domain/output_profile.py#L44-L435]`
- `[MODIFY] @[backend_v2/models/dtos/system.py]`
- `[MODIFY] @[backend_v2/models/auth.py#L1421-L1497]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L414-L447]`
- `[MODIFY] @[backend_v2/database/repositories/system.py#L25-L213]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L373-L418]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L253-L297]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L169-L223]`
- `[MODIFY] @[backend_v2/services/studio/system_config_service.py#L44-L746]`
- `[MODIFY] @[backend_v2/services/auth/secret_service.py#L140-L1170]`
- `[MODIFY] @[backend_v2/services/cache/typed_cache.py#L340-L418]`
- `[MODIFY] @[backend_v2/llm/client.py#L51-L947]`
- `[MODIFY] @[backend_v2/llm/handler.py]`
- `[MODIFY] @[backend_v2/hooks/llm.py]`
- `[MODIFY] @[backend_v2/main.py#L72-L130]`
- `[MODIFY] @[backend_v2/seed/seed_registry.py#L23-L34]`
- `[MODIFY] @[backend_v2/seed/run_seed.py#L671-L749]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L1-L50]`
- `[MODIFY] @[scripts/audit_database_atoms.py#L328-L786]`
- `[MODIFY] @[scripts/sanitize_seed_vault.py]`
- `[MODIFY] @[scripts/ablation_live_executor.py]`
- `[MODIFY] @[scripts/diff_executions.py]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/model_config.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]`
- `[MODIFY] @[backend_v2/tests/unit/models/dtos/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_diff_executions.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[client_app_v2/test/core/models/enums_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`
- `[MODIFY] @[client_app_v2/test/models/domain_parity_test.dart]`

## Phase 2 Deprecations & Sunset Symbols

<demolish>
- `SystemConfigUnion`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/enums.py#L246-L269]`, `@[backend_v2/models/domain/system_config.py#L151-L208]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/services/auth/secret_service.py#L140-L1170]`, `@[backend_v2/services/cache/typed_cache.py#L340-L418]` & `@[backend_v2/llm/client.py#L51-L947]` | `system_configs` STI table, `SystemConfigUnion`, `EntityPrefix.SYSTEM_CONFIG` (`sys_`), `SystemConfigID.MCP_GATEWAYS`, duplicate `EntityPrefix.ORG`, unlinked MCP secret `target_identifier`, and banned `ModelProfile.api_key` / `ModelProfile.parsing_mode`. | Create `model_registries` (`mrg_`, `slug TEXT`, `name TEXT NOT NULL`, `default_provider TEXT NOT NULL`, `tier_definitions JSONB NOT NULL`, `VIRTUAL` `created_at`) and `mcp_gateways` (`mcp_`, `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE`, `slug TEXT NOT NULL`, `name TEXT NOT NULL`, `auth_header_name TEXT`, `tools JSONB NOT NULL`, `VIRTUAL` `created_at`) with zero `UNIQUE` on `slug`; add `tenant_secrets.mcp_gateway_id ON DELETE CASCADE` derived via `parse_prefixed_uuid7`. | Preserve `tier_definitions` and `tools` (`list[AllowedMCPTool]`) as strict Pydantic-validated `JSONB` Aggregate Leaves without child EAV tables. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/ backend_v2/llm/ backend_v2/hooks/llm.py backend_v2/services/studio/system_config_service.py backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py --test --ast-strict` |
| `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L373-L418]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L253-L297]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`, `@[backend_v2/models/domain/workflow.py#L25-L232]` & `@[backend_v2/models/domain/output_profile.py#L44-L435]` | Python $O(N)$ full-table delete loops on `criteria_block_ids` and `workflows.steps[*].task_blueprint`, permissive `ON DELETE SET NULL` on blueprint FKs, untyped `TEXT` on `*_target_block` and `*.created_by`, physical `created_at` on `executions`/`report_artifacts`, and blind `workflows.version` overwrites. | Sync `step_criteria_blocks` and `workflow_step_refs` (`ON DELETE RESTRICT`) via `UNNEST` inside `upsert_step_row` and `upsert_workflow_row`; bind `workflows.default_profile_id` as `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`; convert `variance_target_block`, `user_role_target_block`, `users.created_by`, and `executions.created_by` to `UUID` FKs; enforce `WHERE version = $2` SQL OCC on `workflows` raising `ErrorCodes.CONFLICT` (409). | Keep `Workflow.steps` (`list[StepRule]`), `MatrixPromptBlock`, `I18nText`, and `OutputProfile.content_blocks` as typed `JSONB` Aggregate Leaves. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/ backend_v2/tests/unit/database/postgres/entity_adapter/ --test --ast-strict` |
| `@[backend_v2/seed/seed_data.json#L1-L50]`, `@[backend_v2/seed/seed_registry.py#L23-L34]`, `@[backend_v2/seed/run_seed.py#L671-L749]`, `@[scripts/audit_database_atoms.py#L328-L786]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/diff_executions.py]` & `@[scripts/run_e2e_variance_test.py]` | Monolithic `"system_config"` seed collection (`sys_`), 12 banned `"parsing_mode": "STRUCTURED_JSON"` entries in `seed_data.json`, and stale `EntityPrefix.STEP_REFERENCE` in `prompt_blocks` atom rules. | Create timestamped backup in `backend_v2/seed/backups/`, split `"system_config"` into `"model_registries"` (`mrg_`) and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`), seed `mcp_gateways` before `_seed_local_secrets`, and drop `EntityPrefix.STEP_REFERENCE` from `prompt_blocks` rules in `audit_database_atoms.py`. | Touch ZERO `system_prompt`, `ai_description`, `instruction_text`, or matrix rubric natural-language coaching texts (`prompt_preservation_mandate`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict` |
| `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]` & `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` | Stale `apiKey` and `parsingMode` fields on Flutter `LlmModelConfig` / `ModelRegistryView`, missing `organizationId` on `McpGateway`, and outdated `EntityPrefix` Dart enum values. | Synchronize `EntityPrefix` in `enums.dart`, drop `apiKey` and `parsingMode` from `model_config.dart` and `model_registry_view.dart`, and add `@JsonKey(name: 'organization_id') required String organizationId` to `McpGateway` (`disallowUnrecognizedKeys: true`). | Maintain 1:1 DTO parity verified automatically by `audit_dto_parity.py --fail-on-mismatch` and `domain_parity_test.dart`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[.agents/rules/03_seed_vault.md]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/domain/system_config.py#L151-L208]`, `@[backend_v2/seed/seed_registry.py#L23-L34]`, and `@[backend_v2/seed/run_seed.py#L671-L749]`.</action>
    <action>Look forward: Verify Step 2.1 evolves the 22-table PostgreSQL 19 DDL and splits `system_configs` into `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`) with `tenant_secrets.mcp_gateway_id ON DELETE CASCADE`, Step 2.2 adds `step_criteria_blocks`, `workflow_step_refs`, deferrable `workflows.default_profile_id`, typed UUID FKs, `VIRTUAL` `created_at`, and `Workflow.version` SQL OCC, Step 2.3 executes the `seed_data.json` structural split with backup and `--dry-run` gates, and Step 2.4 synchronizes Flutter Studio models and enums in a separate frontend step.</action>
    <constraint invariant="prompt_preservation_mandate">Zero qualitative coaching prompts (`system_prompt`, `ai_description`, `instruction_text`, matrix `scales`/`rows`/`columns`) in `backend_v2/seed/seed_data.json` may be altered; create a timestamped backup in `backend_v2/seed/backups/` before editing `seed_data.json`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/02_phase2_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/models/enums.py#L246-L269]</backend>
    <backend>@[backend_v2/models/domain/__init__.py]</backend>
    <backend>@[backend_v2/models/domain/system_config.py#L151-L208]</backend>
    <backend>@[backend_v2/models/domain/workflow.py#L25-L232]</backend>
    <backend>@[backend_v2/models/domain/output_profile.py#L44-L435]</backend>
    <backend>@[backend_v2/models/dtos/system.py]</backend>
    <backend>@[backend_v2/models/auth.py#L1421-L1497]</backend>
    <backend>@[backend_v2/database/interfaces.py#L414-L447]</backend>
    <backend>@[backend_v2/database/repositories/system.py#L25-L213]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L373-L418]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L253-L297]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L169-L223]</backend>
    <backend>@[backend_v2/services/studio/system_config_service.py#L44-L746]</backend>
    <backend>@[backend_v2/services/auth/secret_service.py#L140-L1170]</backend>
    <backend>@[backend_v2/services/cache/typed_cache.py#L340-L418]</backend>
    <backend>@[backend_v2/llm/client.py#L51-L947]</backend>
    <backend>@[backend_v2/llm/handler.py]</backend>
    <backend>@[backend_v2/hooks/llm.py]</backend>
    <backend>@[backend_v2/main.py#L72-L130]</backend>
    <backend>@[backend_v2/seed/seed_registry.py#L23-L34]</backend>
    <backend>@[backend_v2/seed/run_seed.py#L671-L749]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L1-L50]</backend>
    <backend>@[scripts/audit_database_atoms.py#L328-L786]</backend>
    <backend>@[scripts/sanitize_seed_vault.py]</backend>
    <backend>@[scripts/ablation_live_executor.py]</backend>
    <backend>@[scripts/diff_executions.py]</backend>
    <backend>@[scripts/run_e2e_variance_test.py]</backend>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/model_config.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/model_registry_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]</backend>
    <backend>@[backend_v2/tests/unit/models/dtos/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]</backend>
    <backend>@[backend_v2/tests/unit/seed/test_run_seed.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_diff_executions.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]</backend>
    <backend>@[backend_v2/tests/unit/test_enum_parity.py]</backend>
    <frontend>@[client_app_v2/test/core/models/enums_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]</frontend>
    <frontend>@[client_app_v2/test/models/domain_parity_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` includes the idempotent `DO $$` pre-production cutover gate, replaces `system_configs` with `model_registries` (`mrg_`) and `mcp_gateways` (`mcp_`) without `UNIQUE` on `slug`, binds `tenant_secrets.mcp_gateway_id ON DELETE CASCADE` (in both `CREATE TABLE` and `ALTER TABLE`), adds `step_criteria_blocks` and `workflow_step_refs` (`ON DELETE RESTRICT`), sets `workflows.default_profile_id` to `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`, converts `variance_target_block`, `user_role_target_block`, `users.created_by`, and `executions.created_by` to `UUID` FKs, converts `created_at` to `VIRTUAL` across all 16 UUIDv7-PK tables, adds complete FK/tenant B-Tree indexes, and removes dirty-DB scrubbing blocks.</item>
    <item>`EntityPrefix.MODEL_REGISTRY = "mrg"` and `EntityPrefix.MCP_GATEWAY = "mcp"` replace `EntityPrefix.SYSTEM_CONFIG` (`sys_`), `SystemConfigUnion`, `SystemConfigID.MCP_GATEWAYS`, and duplicate `EntityPrefix.ORG`; `ModelProfile.api_key` and `ModelProfile.parsing_mode` are removed across Python, Seed Vault, and Flutter Studio; and `workflows` enforces single-statement SQL `WHERE version = $2` OCC (`ErrorCodes.CONFLICT` 409).</item>
    <item>`@[backend_v2/seed/seed_data.json#L1-L50]` (`@[backend_v2/seed/seed_data.json#L1-L260]`), `seed_registry.py`, `run_seed.py`, and the 4 operational CLI scripts split `"system_config"` into `"model_registries"` and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`, seeded prior to `_seed_local_secrets`) with zero qualitative prompt mutations, passing `run_seed.py local --dry-run` and `audit_database_atoms.py --strict`.</item>
    <item>Flutter `enums.dart`, `model_config.dart`, `model_registry_view.dart`, and `mcp_gateway.dart` (`organizationId`) are 100% synchronized and pass `audit_dto_parity.py --fail-on-mismatch` and `flutter_audit_loop.py`.</item>
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
    <anti_target>Do NOT add a `UNIQUE` constraint on `model_registries.slug` or `mcp_gateways.slug` (`ZORM007` fatal violation), and do NOT declare `ON DELETE RESTRICT DEFERRABLE` on `workflows.default_profile_id` (use `ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED`).</anti_target>
    <anti_target>Do NOT normalize `ModelRegistry.tier_definitions`, `MCPGateway.tools`, `MatrixPromptBlock`, `I18nText`, `OutputProfile.content_blocks`, or `Workflow.steps` (`list[StepRule]`) into child EAV tables.</anti_target>
    <anti_target>Do NOT modify any `system_prompt`, `ai_description`, `instruction_text`, or matrix rubric text in `backend_v2/seed/seed_data.json` (`prompt_preservation_mandate`).</anti_target>
  </anti_targets>

  <step id="2.1" name="system_configs Split into model_registries (mrg_) &amp; mcp_gateways (mcp_), tenant_secrets.mcp_gateway_id FK &amp; ModelProfile Cleanup">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/enums.py#L246-L269]`, `@[backend_v2/models/domain/__init__.py]`, `@[backend_v2/models/domain/system_config.py#L151-L208]`, `@[backend_v2/models/dtos/system.py]`, and `@[backend_v2/models/auth.py#L1421-L1497]`: Prepend the idempotent pre-production cutover `DO $$` block when `information_schema.tables` contains `'system_configs'`; replace `system_configs` with `model_registries` (`EntityPrefix.MODEL_REGISTRY = "mrg"`, `slug TEXT`, `name TEXT NOT NULL`, `default_provider TEXT NOT NULL`, `tier_definitions JSONB NOT NULL`, `VIRTUAL` `created_at`) and `mcp_gateways` (`EntityPrefix.MCP_GATEWAY = "mcp"`, `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE`, `slug TEXT NOT NULL`, `name TEXT NOT NULL`, `endpoint_url TEXT NOT NULL`, `transport_type TEXT NOT NULL`, `auth_type TEXT NOT NULL`, `auth_env_var TEXT`, `auth_header_name TEXT`, `timeout_seconds INTEGER NOT NULL`, `tools JSONB NOT NULL`, `VIRTUAL` `created_at`) with zero `UNIQUE` constraint on `slug`. Drop `EntityPrefix.SYSTEM_CONFIG` (`sys_`), `SystemConfigUnion`, `SystemConfigID.MCP_GATEWAYS`, and duplicate `EntityPrefix.ORG`. Drop `ModelProfile.api_key` and `ModelProfile.parsing_mode`. Add `mcp_gateway_id UUID REFERENCES mcp_gateways(id) ON DELETE CASCADE` to `tenant_secrets` (in both `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE tenant_secrets ADD COLUMN IF NOT EXISTS`) with a SQL `CHECK` constraint enforcing `(scope = 'mcp_gateway' AND mcp_gateway_id IS NOT NULL) OR (scope IN ('llm_provider', 'telemetry') AND mcp_gateway_id IS NULL)` plus `idx_tenant_secrets_org_id` and `idx_tenant_secrets_mcp_gateway_id`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/interfaces.py#L414-L447]`, `@[backend_v2/database/repositories/system.py#L25-L213]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L289-L334]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L915-L971]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L169-L223]`, `@[backend_v2/services/studio/system_config_service.py#L44-L746]`, `@[backend_v2/services/auth/secret_service.py#L140-L1170]`, `@[backend_v2/services/cache/typed_cache.py#L340-L418]`, `@[backend_v2/llm/client.py#L51-L947]`, `@[backend_v2/llm/handler.py]`, `@[backend_v2/hooks/llm.py]`, and `@[backend_v2/main.py#L72-L130]`: Split `hydrate_system_config_row` into dedicated `hydrate_model_registry_row` and `hydrate_mcp_gateway_row`, split `ISystemRepository.delete_system_config` into `delete_model_registry` and `delete_mcp_gateways`, derive SQL `mcp_gateway_id` in `upsert_tenant_secret_row` via `parse_prefixed_uuid7(secret.target_identifier, EntityPrefix.MCP_GATEWAY)` when `scope == SecretScope.MCP_GATEWAY` (else `None`), validate `EntityPrefix.MCP_GATEWAY` (`mcp_<hex32>`) in `SecretService`, update `MCPGatewayCache` (`typed_cache.py`), `CANONICAL_SEED_TABLES`, and `main.py` (`verify_seed_table_counts`), and remove all `api_key` / `parsing_mode` references in `llm/client.py`, `llm/handler.py`, and `hooks/llm.py`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py#L1515-L2185]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L2010-L2084]`, `@[backend_v2/tests/unit/models/dtos/test_system.py]`, `@[backend_v2/tests/unit/database/repositories/test_system.py]`, `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]`, and `@[backend_v2/tests/unit/test_enum_parity.py]`: Update `WorkflowFactory.model_registry_id` (`EntityPrefix.MODEL_REGISTRY`) and `WorkflowFactory.mcp_gateway_id` (`EntityPrefix.MCP_GATEWAY`), update in-memory fakes for `model_registries` and `mcp_gateways`, and add positive, negative, and boundary unit tests for `mrg_`/`mcp_` prefix enforcement and `tenant_secrets.mcp_gateway_id` cascading cleanup.</action>
    <constraint invariant="canonical_id_relational_sovereignty_and_zero_default_guardrails">`workflows.model_registry_id` MUST validate `mrg_<hex32>` and `workflows.mcp_gateway_id` MUST validate `mcp_<hex32>` with `ON DELETE RESTRICT` in PostgreSQL 19.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/ backend_v2/llm/ backend_v2/hooks/llm.py backend_v2/services/studio/system_config_service.py backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py backend_v2/main.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/models/dtos/test_system.py backend_v2/tests/unit/database/repositories/test_system.py backend_v2/tests/unit/database/repositories/test_system_model_registry.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Junction Tables (step_criteria_blocks &amp; workflow_step_refs), Deferrable default_profile_id, Typed UUID FKs, VIRTUAL created_at &amp; Workflow.version SQL OCC">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/domain/workflow.py#L25-L232]`, and `@[backend_v2/models/domain/output_profile.py#L44-L435]`: Add `step_criteria_blocks` (`step_id UUID REFERENCES steps(id) ON DELETE CASCADE`, `prompt_block_id UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT`, `position INTEGER NOT NULL CHECK (position >= 0)`, `PRIMARY KEY (step_id, prompt_block_id)`) and `workflow_step_refs` (`workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE`, `step_id UUID REFERENCES steps(id) ON DELETE RESTRICT`, `PRIMARY KEY (workflow_id, step_id)`). Upgrade `steps.role_block_id`, `steps.extraction_protocol_block_id`, `steps.execution_persona_block_id`, `workflows.model_registry_id`, and `workflows.mcp_gateway_id` to `ON DELETE RESTRICT`; add `FOREIGN KEY (default_profile_id) REFERENCES output_profiles(id) ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED` on `workflows`; convert `output_profiles.variance_target_block` and `output_profiles.user_role_target_block` from `TEXT` to `UUID REFERENCES prompt_blocks(id) ON DELETE RESTRICT`; convert `users.created_by` and `executions.created_by` from `TEXT` to `UUID REFERENCES users(id) ON DELETE SET NULL`; convert `executions.created_at` and `report_artifacts.created_at` to `TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL`; add SQL `CHECK` discriminator constraints on `prompt_blocks.category_id` and `users.role`; add complete B-Tree indexes across all Foreign Key and `organization_id` columns; and remove dirty-DB `UPDATE`/`DELETE` scrubbing blocks.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L373-L418]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L253-L297]`, and `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L241-L298]`: Synchronize `step_criteria_blocks` and `workflow_step_refs` atomically via `UNNEST` inside `upsert_step_row` and `upsert_workflow_row`; drop full-table Python delete loops in `PromptBlockRepositoryImpl.delete_prompt_block` and `StudioWorkflowService.delete_step`; parse/format `users.created_by` and `executions.created_by` via `_parse_optional_uuid7(..., EntityPrefix.USER)` and `_format_optional_uuid7(..., EntityPrefix.USER)` and `variance_target_block` / `user_role_target_block` via `EntityPrefix.PROMPT_BLOCK`; and enforce single-statement SQL Optimistic Concurrency Control (`WHERE version = $2`) on `workflows` in `upsert_workflow_row`, raising `AppException(ErrorCodes.CONFLICT, status_code=409)` when `version` mismatches.</action>
    <constraint invariant="uow_transactional_concurrency_mandate">Concurrent `save_workflow` updates with a stale `version` MUST fail fast with `AppException(ErrorCodes.CONFLICT, status_code=409)` via atomic SQL `WHERE version = $2`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/ backend_v2/models/domain/workflow.py backend_v2/models/domain/output_profile.py --test --ast-strict</audit_command>
  </step>

  <step id="2.3" name="Source-Level seed_data.json Structural Split (model_registries &amp; mcp_gateways) &amp; Operational Seed Script Synchronization">
    <action>1. `[MODIFY]` `@[backend_v2/seed/seed_data.json#L1-L50]`, `@[backend_v2/seed/seed_registry.py#L23-L34]`, `@[backend_v2/seed/run_seed.py#L671-L749]`, `@[scripts/audit_database_atoms.py#L328-L786]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/ablation_live_executor.py]`, `@[scripts/diff_executions.py]`, and `@[scripts/run_e2e_variance_test.py]`: Store a timestamped backup copy in `backend_v2/seed/backups/` (`03_seed_vault.md` Step `2_backup`), split `"system_config"` in `@[backend_v2/seed/seed_data.json#L1-L50]` (`@[backend_v2/seed/seed_data.json#L1-L260]`), `seed_registry.py`, `run_seed.py`, and the 4 operational CLI scripts into `"model_registries"` (`mrg_<hex32>`, removing all 12 banned `"parsing_mode": "STRUCTURED_JSON"` entries) and `"mcp_gateways"` (`mcp_0195f3a00000700080008172bda70c86`, with `"organization_id": "org_0195f3a0000070008000000000000001"`), update `workflows[*].model_registry_id` and `workflows[*].mcp_gateway_id` references accordingly, ensure `run_seed.py` seeds `mcp_gateways` prior to `_seed_local_secrets`, and drop stale `EntityPrefix.STEP_REFERENCE` from `prompt_blocks` validation in `audit_database_atoms.py`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`, `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`, `@[backend_v2/tests/unit/scripts/test_ablation_live_executor.py]`, `@[backend_v2/tests/unit/scripts/test_diff_executions.py]`, and `@[backend_v2/tests/unit/scripts/test_run_e2e_variance_test.py]`: Update unit tests for the 9-collection `SeedCollectionName` registry (`model_registries` + `mcp_gateways`), pre-secret `mcp_gateways` seeding order, and `prompt_blocks` prefix strictness.</action>
    <constraint invariant="live_database_mutation">Validate `seed_data.json` 100% in-memory via `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python scripts/audit_database_atoms.py --strict` before any database sync; restore backup immediately if any check fails.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/seed/ scripts/audit_database_atoms.py scripts/sanitize_seed_vault.py scripts/ablation_live_executor.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/seed/ backend_v2/tests/unit/scripts/ --test --ast-strict</audit_command>
  </step>

  <step id="2.4" name="Flutter Studio Enum, LlmModelConfig, ModelRegistryView &amp; McpGateway Freezed Parity">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, and `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`: Synchronize `EntityPrefix` in `enums.dart` (`modelRegistry('mrg')`, `mcpGateway('mcp')`, `auditLog('aud')`, `usageRecord('usg')`, dropping `systemConfig` and duplicate `org`), remove `apiKey` and `parsingMode` from `LlmModelConfig` (`model_config.dart`) and `ModelRegistryView` (`model_registry_view.dart`), and add `@JsonKey(name: 'organization_id') required String organizationId` to `McpGateway` (`mcp_gateway.dart`).</action>
    <action>2. `[MODIFY]` `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart]`, and `@[client_app_v2/test/models/domain_parity_test.dart]`: Regenerate Freezed/JSON artifacts and update unit and domain parity tests to assert `McpGateway.organizationId` requirement, strict rejection of legacy `parsing_mode`/`api_key` under `disallowUnrecognizedKeys: true`, and 1:1 `test_enum_parity.py` alignment.</action>
    <constraint invariant="anti_semantic_drift_renaming">Stage and commit Backend (`Step 2.1`–`Step 2.3`) and Frontend (`Step 2.4`) changes cleanly with regenerated `.freezed.dart`/`.g.dart` siblings so `audit_dto_parity.py --fail-on-mismatch` and `flutter_audit_loop.py` pass 100%.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_model_registry_and_mcp_gateway_roundtrip_and_fk_restrict" category="positive">
      <input>Valid `SystemConfigModelRegistry` (`mrg_<hex32>`) and `SystemConfigMCPGateways` (`mcp_<hex32>`, `organization_id="org_0195f3a0000070008000000000000001"`) persisted and referenced by `WorkflowFactory.build()`</input>
      <expected>Roundtrips both models without loss; attempting to delete a referenced `model_registry` or `mcp_gateway` raises `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)`</expected>
    </test>
    <test name="test_model_profile_rejects_banned_api_key_and_parsing_mode_fields" category="negative">
      <input>`ModelProfile.model_validate` called with `"api_key": "sk-..."` or `"parsing_mode": "STRUCTURED_JSON"`</input>
      <expected>Fails fast with Pydantic `ValidationError` under `ConfigDict(extra="forbid", strict=True)`</expected>
    </test>
    <test name="test_workflow_model_registry_id_rejects_mcp_prefix_and_vice_versa" category="negative">
      <input>`WorkflowFactory.build` / `Workflow.model_validate` called with `model_registry_id="mcp_..."` or `mcp_gateway_id="mrg_..."`</input>
      <expected>Raises `ValidationError` on cross-entity prefix mismatch</expected>
    </test>
    <test name="test_tenant_secret_mcp_gateway_cascade_delete_cleans_up_encrypted_secret" category="positive">
      <input>Unreferenced custom `SystemConfigMCPGateways` (`mcp_<hex32>`) with bound `TenantSecretDTO` (`scope=SecretScope.MCP_GATEWAY`, `mcp_gateway_id`) deleted</input>
      <expected>Cascades deletion of the associated `tenant_secrets` row while leaving `llm_provider` and `telemetry` secrets intact</expected>
    </test>
    <test name="test_upsert_workflow_stale_version_raises_conflict_409" category="boundary">
      <input>Persisted `Workflow` at `version=1` updated concurrently twice expecting `version=1`</input>
      <expected>First update increments `version` to `2`; second stale update fails fast with `AppException(ErrorCodes.CONFLICT, status_code=409)`</expected>
    </test>
    <test name="test_step_criteria_blocks_and_workflow_step_refs_block_referenced_deletes" category="negative">
      <input>Attempt to delete a `PromptBlock` referenced in `Step.criteria_block_ids` or a `Step` referenced in `Workflow.steps[*].task_blueprint`, or delete `Workflow.default_profile_id`</input>
      <expected>Raises `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)` via `SQLSTATE 23503` without Python full-table scans</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 2 seed pre-flight &amp; backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/ backend_v2/llm/ backend_v2/hooks/llm.py backend_v2/services/studio/system_config_service.py backend_v2/services/auth/secret_service.py backend_v2/services/cache/typed_cache.py backend_v2/seed/ scripts/audit_database_atoms.py scripts/sanitize_seed_vault.py scripts/ablation_live_executor.py scripts/diff_executions.py scripts/run_e2e_variance_test.py backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/models/ backend_v2/tests/unit/database/repositories/test_system.py backend_v2/tests/unit/database/repositories/test_system_model_registry.py backend_v2/tests/unit/seed/ backend_v2/tests/unit/scripts/ backend_v2/tests/unit/test_enum_parity.py --test --ast-strict`.</action>
    <action>Run Phase 2 Flutter Studio quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build`.</action>
  </validation_gate>
</execution_protocol>
