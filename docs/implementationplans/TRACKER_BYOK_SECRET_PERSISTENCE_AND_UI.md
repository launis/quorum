# Tracker: BYOK Secret PostgreSQL 19 Persistence, Storage Mode Parity, Canonical MCP Gateway `name` Parity & Target Selector UI

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]`
  - [x] Step 1: Phase 1: Hexagonal EntityPersistencePort Delete Contract, UoW Factory Registration, InMemoryEntityAdapter Parity & Canonical MCP Gateway name Schema
  - [x] Step 2: Phase 2: Backend TenantSecretCreateDTO Storage Mode Contract, Zero-Fallback SecretService Persistence & Studio ADMIN Gateway Listing
  - [x] Step 3: Phase 3: Frontend McpGateway.name & TenantSecretCreateDto Parity, Studio Gateway Views & Scope-Aware BYOK Target Selector in OrganizationIamSettingsView
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/models/domain/system_config.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/factory.py]
  - [x] @[backend_v2/models/auth.py]
  - [x] @[backend_v2/services/auth/secret_service.py]
  - [x] @[backend_v2/services/studio/system_config_service.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]
  - [ ] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the protocol-level `UnitOfWorkFactory` registration in `backend_v2/database/interfaces.py`, the single-pipeline PostgreSQL 19 persistence and physical deletion contract in `SecretService` via `EntityPersistencePort.delete_collection_document`, the required `storage_mode` contract on `TenantSecretCreateDTO` / `TenantSecretCreateDto`, the required human-readable `name` field parity across `SystemConfigMCPGateways` and `McpGateway`, and the scope-aware `org_secret_target_dropdown` binding canonical `McpGateway.id` (`sys_<hex32>`) in `organization_iam_settings_view.dart`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect the `UnitOfWorkFactory` registration contract in `backend_v2/database/interfaces.py` and `backend_v2/database/factory.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the PostgreSQL 19 BYOK tenant secret persistence pipeline, canonical MCP gateway `name` + `id` contracts, and Studio/IAM target selector UI in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/target.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Change `name TEXT DEFAULT 'Default Model Registry'` on `system_configs` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L82-L98]` to `name TEXT NOT NULL` with zero SQL `DEFAULT` fallback. | Step 1 | [x] Completed |
| REQ-002 | Add required `name: Annotated[str, Field(min_length=1, description="Human-readable gateway title.")]` (without any default value) to `SystemConfigMCPGateways` in `@[backend_v2/models/domain/system_config.py#L376-L441]`. | Step 1 | [x] Completed |
| REQ-003 | Hydrate `"name": row["name"]` for `mcp_gateways` in `hydrate_system_config_row` and bind `name = cfg.name` for both `SystemConfigModelRegistry` and `SystemConfigMCPGateways` in `upsert_system_config_row` in `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L911-L956]`, updating `_build_mcp_gateway()` in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py#L239-L263]`. | Step 1 | [x] Completed |
| REQ-004 | Add `"name": "Tavily MCP Gateway"` to `sys_0195f3a00000700080008172bda70c86` in `@[backend_v2/seed/seed_data.json#L209-L219]`. | Step 1 | [x] Completed |
| REQ-005 | Add `delete_collection_document(self, collection_name: str, doc_id: str) -> bool` to `EntityPersistencePort` and expose `UnitOfWorkFactory`, `register_default_uow_factory`, and `get_registered_uow_factory` in `@[backend_v2/database/interfaces.py#L430-L473]`, registering `create_unit_of_work` in `@[backend_v2/database/factory.py#L136-L177]`. | Step 1 | [x] Completed |
| REQ-006 | Implement `delete_collection_document` on `InMemoryEntityAdapter` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1163-L1239]` and add the `isolate_default_uow_and_secret_service` autouse fixture in `@[backend_v2/tests/conftest.py#L157-L184]`. | Step 1 | [x] Completed |
| REQ-007 | Add required `storage_mode: Annotated[LaxSecretStorageMode, Field(description="Cryptographic storage mode (ENVELOPE_KMS or CLOUD_SECRET_MANAGER).")]` (without any default value) to `TenantSecretCreateDTO` in `@[backend_v2/models/auth.py#L1440-L1466]`. | Step 2 | [x] Completed |
| REQ-008 | Eradicate `_local_secrets` and `_deleted_secret_ids` from `SecretService` in `@[backend_v2/services/auth/secret_service.py#L106-L1139]`, route all persistence (`upsert_tenant_secret`, `delete_tenant_secret`, `_list_org_secret_records`, `_get_secret_record_by_id`) through `entity_adapter` or `uow_factory` (failing fast with `ConfigurationError` when unconfigured), read `payload.storage_mode` as the single SSOT, and validate `payload.target_identifier` against `LLMProvider` values or `EntityPrefix.SYSTEM_CONFIG` (`sys_<hex32>`). | Step 2 | [x] Completed |
| REQ-009 | Update `StudioSystemConfigService` in `@[backend_v2/services/studio/system_config_service.py#L43-L697]` to allow `[UserRole.ROOT, UserRole.ADMIN]` in `list_mcp_gateways`, pass `name="New MCP Gateway Draft"` in `create_mcp_gateway_draft`, and set `"name": f"{existing.name} (Copy)"` in `clone_mcp_gateways`. | Step 2 | [x] Completed |
| REQ-010 | Update unit tests in `@[backend_v2/tests/unit/services/auth/test_secret_service.py#L556-L705]` and `@[backend_v2/tests/unit/services/studio/test_system_config_service.py#L392-L425]` to cover `uow_factory` persistence roundtrip, physical deletion, `ConfigurationError` Fail-Fast, rejection of informational `slug` strings as `target_identifier`, and `UserRole.ADMIN` gateway listing. | Step 2 | [x] Completed |
| REQ-011 | Add `required String name` (without `@Default`) to `McpGateway` in `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart#L113-L134]`, update `@[client_app_v2/test/features/studio/models/mcp_gateway_test.dart#L9-L171]`, render `gateway.name` in `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L17-L228]`, and add the `gateway_name_field` `TextFormField` in `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart#L18-L341]`. | Step 3 | [x] Completed |
| REQ-012 | Add `@JsonKey(name: 'storage_mode') required SecretStorageMode storageMode` (without `@Default`) to `TenantSecretCreateDto` in `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart#L173-L189]`. | Step 3 | [x] Completed |
| REQ-013 | Add `availableMcpGatewaysProvider` and replace `org_secret_target_field` exclusively with `DropdownButtonFormField<String>` (`org_secret_target_dropdown`) in `_ByokSecretsCard` (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1291-L1566]`) displaying `'${gw.name} (${gw.id})'` and binding `value: gw.id` (`sys_<hex32>`), forwarding `storageMode: selectedStorageMode.value`, and verifying in `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L271-L850]`. | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Steps 1, 2, and 3 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md]` (`REQ-001` through `REQ-013`) in commits `dc68c0aa2`, `b5e44d57c`, and `0f975a9d7`.
- Implemented protocol-level `UnitOfWorkFactory` registration in `@[backend_v2/database/interfaces.py#L430-L473]` and `@[backend_v2/database/factory.py#L136-L177]`, eradicated `_local_secrets` and `_deleted_secret_ids` from `@[backend_v2/services/auth/secret_service.py#L106-L1139]`, enforced physical deletion via `delete_collection_document("tenant_secrets", secret_id)`, and validated `target_identifier` against `LLMProvider` values or `EntityPrefix.SYSTEM_CONFIG` (`sys_<hex32>`).
- Added required `storage_mode` (`SecretStorageMode`) to `TenantSecretCreateDTO` and `TenantSecretCreateDto`, required `name` (`min_length=1`) to `SystemConfigMCPGateways` and `McpGateway` (`name TEXT NOT NULL` in `001_pg19_uuidv7_schema.sql`), updated `StudioSystemConfigService.list_mcp_gateways` to allow `[UserRole.ROOT, UserRole.ADMIN]`, and replaced `org_secret_target_field` with `org_secret_target_dropdown` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1291-L1566]`.
- Completed `/tier7-describe-architecture` (`b8a9c617a`): synchronized `@[ki_god_code_prevention.md]`, `@[.agents/rules/04_directory_reference.md]`, `@[docs/architecture/01_SYSTEM_CONTEXT_AND_INVARIANTS.md]`, `@[docs/architecture/02_DATA_SEEDING_AND_ONTOLOGY.md]`, and `@[docs/architecture/04_SERVER_DRIVEN_UI_AND_PRESENTATION.md]`.

## Learned
- Wrapping `DropdownButtonFormField<String>` (`org_secret_target_dropdown`) in a scope-keyed `KeyedSubtree(key: ValueKey<SecretScope>(selectedScope.value))` in `_ByokSecretsCard` guarantees clean `FormField` state reset when switching between `SecretScope.llmProvider` and `SecretScope.mcpGateway`.
- Registering `create_unit_of_work` via `register_default_uow_factory` in `backend_v2/database/interfaces.py` and binding an isolated `InMemoryUnitOfWork` in `backend_v2/tests/conftest.py` keeps `SecretService` 100% compliant with `QGR017` while ensuring deterministic roundtrip persistence across both production and unit test suites.

## Remaining
- Run the Tier 2 Hardening pipelines (`scripts/auto_hardening_runner.py`) for the 7 Backend and 5 Frontend targets, followed by `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_BYOK_SECRET_PERSISTENCE_AND_UI.md] @[docs/implementationplans/TRACKER_BYOK_SECRET_PERSISTENCE_AND_UI.md]
```
