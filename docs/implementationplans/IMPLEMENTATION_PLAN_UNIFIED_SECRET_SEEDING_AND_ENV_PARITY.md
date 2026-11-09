<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: Unified Secret Seeding (`.env.secrets.local` -> PostgreSQL 19 `tenant_secrets`), `.env` Cleanup, `service-account.json` Removal & ROOT-Scoped Logfire Telemetry

## 1. Objective & Architectural Background

### Technical Objective
Establish 1:1 local-to-cloud secret and bootstrap parity by:
1. Separating **Tier 1 Process Bootstrap configuration** (`@[.env#L1-L18]`: `JWT_SECRET_KEY`, `STORAGE_BACKEND`, `OTEL_ENABLED`, `ENVIRONMENT`, `DEV_EXECUTION_MODE`, `DUMP_PROMPTS_FILE`, `LITELLM_LOG`, `POSTGRES_PASSWORD`) from **Tier 2 Seeded Capability & Platform Secrets** (`[NEW] @[.env.secrets.local]` and committed template `[NEW] @[.env.secrets.example]`).
2. Extending `@[backend_v2/seed/run_seed.py#L257-L273]` so that after seeding the 8 public collections from `@[backend_v2/seed/seed_data.json#L1-L100]` (which guarantees the Root System Organization `org_0195f3a0000070008000000000000001` and Root User `usr_0195f3a00000700a83fd6b3d77c748f4` exist even after a complete database wipe), it validates `.env.secrets.local` via `LocalSeedSecretsSettings` and encrypts/upserts all `ROOT_SYSTEM` secrets (`ai_studio`, `openai`, `anthropic`, `vertex_ai` GCP Service Account JSON, `sys_0195f3a00000700080008172bda70c86` Tavily MCP, `logfire`, and `logfire_read`) into PostgreSQL 19 `tenant_secrets` via `SecretService.upsert_tenant_secret`, verifying the `tenant_secrets` row count in `verify_seed_table_counts`.
3. Adding `TELEMETRY = "telemetry"` to `SecretScope` in `@[backend_v2/models/enums.py#L1395-L1399]` and `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`, enforcing strict `UserRole.ROOT` and `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) access control in `@[backend_v2/services/auth/secret_service.py#L108-L1009]` and `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`, and resolving the Logfire write token from `tenant_secrets` during async startup in `@[backend_v2/core/telemetry.py#L300-L414]`, `@[backend_v2/main.py#L178-L242]`, and `@[backend_v2/worker.py#L49-L108]`.
4. Removing `LOGFIRE_TOKEN`, `LOGFIRE_READ_TOKEN`, and `MOCK_*_USER_ID` from `@[.env#L1-L18]`, deleting the physical `@[service-account.json]` file from the workspace root, and removing the obsolete synchronous `service-account.json` / `google_api_key` startup check from `@[backend_v2/settings.py#L1172-L1211]` and `@[backend_v2/settings.py#L1320-L1351]`.

### Root Cause Analysis
1. **Unseeded `tenant_secrets` Table on Full Database Wipe (`@[backend_v2/seed/run_seed.py#L257-L273]`)**:
   - `run_seed.py` currently seeds 8 collections (`organizations`, `users`, `system_config`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`) from `seed_data.json` and verifies 10 tables in `CANONICAL_SEED_TABLES` (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`), leaving `tenant_secrets` unverified and empty (`0` rows) whenever PostgreSQL 19 is recreated from scratch.
2. **Residual Local Secret Fragmentation (`@[.env#L4-L17]` & `@[service-account.json]`)**:
   - `LOGFIRE_TOKEN` and `LOGFIRE_READ_TOKEN` remain in `@[.env#L4-L5]` without `SecretScope` governance or `UserRole.ROOT` isolation, `MOCK_*_USER_ID` variables remain in `@[.env#L14-L17]`, and `@[service-account.json]` remains in the workspace root only because `Settings.model_post_init` (`@[backend_v2/settings.py#L1172-L1211]`) synchronously checks for `service-account.json` or `google_api_key` at import/startup time.

---

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[backend_v2/models/auth.py#L107-L126]`
- `@[backend_v2/models/auth.py#L1359-L1435]`
- `@[backend_v2/api/routers/iam/organizations.py#L197-L224]`
- `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L165-L217]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY] @[backend_v2/models/enums.py#L1395-L1399]` | Limiting `SecretScope` to `LLM_PROVIDER` and `MCP_GATEWAY` while leaving platform telemetry tokens unmanaged in `.env`. | Add `TELEMETRY = "telemetry"` to `SecretScope` in `@[backend_v2/models/enums.py#L1395-L1399]`. | Reuse existing `SecretScope` and `LaxSecretScope` without creating parallel secret models. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/services/auth/secret_service.py#L108-L1009]` | Allowing only `LLM_PROVIDER` and `MCP_GATEWAY` target validation and lacking `UserRole.ROOT`-only enforcement for `SecretScope.TELEMETRY`. | Define `_VALID_TELEMETRY_TARGET_IDS = frozenset({"logfire", "logfire_read"})`, enforce `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` for `SecretScope.TELEMETRY` across `list_tenant_secrets`, `upsert_tenant_secret`, and `delete_tenant_secret`, validate `SecretScope.TELEMETRY` in `_validate_target_identifier`, and expose `resolve_telemetry_secret`. | Reuse `_resolve_scoped_secret` and `tenant_secrets` table with zero additional database tables. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/tests/unit/services/auth/test_secret_service.py#L681-L811]` | Testing `SecretService` only for `LLM_PROVIDER` and `MCP_GATEWAY` scopes. | Add positive and negative unit tests for `SecretScope.TELEMETRY` (`resolve_telemetry_secret`, `UserRole.ROOT` upsert/list/delete, `UserRole.ADMIN` HTTP 403 `ErrorCodes.PERMISSION_DENIED` rejection, non-`ROOT_SYSTEM` org rejection, and invalid telemetry target rejection). | Extend existing hermetic `InMemoryUnitOfWork` fixtures in `test_secret_service.py`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py#L290-L305]` | Hardcoding `{"llm_provider", "mcp_gateway"}` in `test_extract_python_enum_values_ast`. | Update `SecretScope` expected set in `@[backend_v2/tests/unit/test_enum_parity.py#L290-L305]` to `{"llm_provider", "mcp_gateway", "telemetry"}`. | Keep existing AST parity harness unchanged. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |
| `[MODIFY] @[client_app_v2/lib/core/models/enums.dart#L711-L722]` | Missing `telemetry` member on Dart `SecretScope` enum. | Add `@JsonValue('telemetry') telemetry('telemetry')` to `SecretScope` in `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`. | Direct 1:1 `@JsonEnum()` value mapping. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/core/models/enums.dart --build --micro` |
| `[MODIFY] @[client_app_v2/test/core/models/enums_test.dart#L85-L115]` | Asserting only 2 values on `SecretScope.values`. | Assert `SecretScope.telemetry.backendValue == 'telemetry'` in `@[client_app_v2/test/core/models/enums_test.dart#L85-L115]`. | Single enum parity assertion update. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/core/models/enums.dart --build --micro` |
| `[MODIFY] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]` | Non-exhaustive `switch (scope)` when `SecretScope.telemetry` is added and exposing all `SecretScope.values` to non-ROOT users. | Filter `SecretScope.values` in `_ByokSecretsCard` so `SecretScope.telemetry` is selectable only when `currentUser?.role == UserRole.root && orgId == 'org_0195f3a0000070008000000000000001'`, and handle `SecretScope.telemetry` in `_formatSecretTarget`, `effectiveTarget`, and the target dropdown (`'logfire'`, `'logfire_read'`). | Reuse existing `DropdownButtonFormField<String>` (`org_secret_target_dropdown`) in `_ByokSecretsCard`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart --micro` |
| `[MODIFY] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L846-L1025]` | Missing widget test coverage for `SecretScope.telemetry` ROOT-only visibility in `_ByokSecretsCard`. | Add widget test assertions verifying `SecretScope.telemetry` is available to `UserRole.root` on `org_0195f3a0000070008000000000000001` and hidden from tenant `UserRole.admin`. | Reuse existing `createSubject` harness in `organization_iam_settings_view_test.dart`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart --micro` |
| `[NEW] @[.env.secrets.example]`, `[NEW] @[.env.secrets.local]`, `[MODIFY] @[.gitignore#L124-L201]`, `[MODIFY] @[.env#L1-L18]`, `[DELETE] @[service-account.json]` | Keeping `LOGFIRE_TOKEN`, `LOGFIRE_READ_TOKEN`, and `MOCK_*_USER_ID` in `@[.env#L4-L17]` and keeping `@[service-account.json]` in the repository root. | Create committed `[NEW] @[.env.secrets.example]` and git-ignored `[NEW] @[.env.secrets.local]`, add `.env.secrets.local` and `.env.*.local` (with `!.env.secrets.example`) to `@[.gitignore#L124-L201]`, strip `LOGFIRE_*` and `MOCK_*_USER_ID` from `@[.env#L1-L18]`, and delete `@[service-account.json]`. | Single flat `.env.secrets.local` file parsed by Pydantic `BaseSettings` (`extra="forbid"`). | `git status --ignored` verifies `.env.secrets.local` is ignored and `service-account.json` is deleted. |
| `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`, `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py#L37-L90]` | Omitting `"tenant_secrets"` from `CANONICAL_SEED_TABLES` and `InMemoryEntityAdapter.verify_seed_table_counts`. | Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` (`11` tables) in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` and to `counts` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`, and update `len(CANONICAL_SEED_TABLES) == 11` in `test_coercion_and_constants.py`. | Zero changes to SQL queries in `seed_and_collection_stage.py`, which already dynamically iterates `CANONICAL_SEED_TABLES`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/seed/run_seed.py#L257-L273]`, `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py#L264-L291]` | Seeding only the 8 public collections from `seed_data.json` and leaving `tenant_secrets` empty (`0` rows) after a full database wipe. | Add `LocalSeedSecretsSettings`, `load_and_validate_local_seed_secrets`, and `_seed_local_secrets` in `@[backend_v2/seed/run_seed.py#L257-L273]` to encrypt and upsert all secrets from `.env.secrets.local` into `tenant_secrets` under `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001`) via `SecretService.upsert_tenant_secret` right after `TOPOLOGICAL_SEED_ORDER`, and verify `"tenant_secrets"` count in `verify_seed_table_counts`. | Reuse `SecretService.upsert_tenant_secret` directly over `active_uow.entities` within `_seed_postgres`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/seed/run_seed.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/core/telemetry.py#L300-L414]`, `[MODIFY] @[backend_v2/main.py#L178-L242]`, `[MODIFY] @[backend_v2/worker.py#L49-L108]`, `[MODIFY] @[backend_v2/tests/unit/core/test_telemetry.py#L259-L288]` | Reading `settings.logfire_token` exclusively from `.env` instead of resolving `SecretScope.TELEMETRY` (`"logfire"`) from PostgreSQL 19 `tenant_secrets`. | Add `logfire_token: str | None = None` parameter and `resolve_startup_logfire_token(settings, secret_service)` to `@[backend_v2/core/telemetry.py#L300-L414]`, and wire `@[backend_v2/main.py#L178-L242]` (`lifespan`) and `@[backend_v2/worker.py#L49-L108]` (`startup`) to resolve the token from `SecretService.resolve_telemetry_secret("logfire")` before calling `configure_telemetry`. | Keep telemetry initialization inside the existing async `lifespan` and `startup` hooks. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/tests/unit/core/test_telemetry.py --test --ast-strict` |
| `[MODIFY] @[backend_v2/settings.py#L1172-L1211]`, `[MODIFY] @[backend_v2/settings.py#L1320-L1351]`, `[MODIFY] @[backend_v2/tests/unit/test_settings.py#L146-L179]`, `[MODIFY] @[backend_v2/tests/unit/llm/test_google_providers_separation.py#L138-L180]` | Auto-detecting `service-account.json` on disk and crashing synchronously in `Settings.model_post_init` when `google_api_key` and `service-account.json` are absent from `.env`/root. | Remove the obsolete `service-account.json` disk auto-detection and synchronous `google_api_key`/`has_vertex` crash from `Settings.model_post_init` (`@[backend_v2/settings.py#L1172-L1211]`) and remove `Path("service-account.json").exists()` from `Settings.enabled_providers` (`@[backend_v2/settings.py#L1320-L1351]`), updating unit tests in `test_settings.py` and `test_google_providers_separation.py`. | Keep `Settings` pure for Tier 1 bootstrap configuration while `SecretService` governs runtime provider credentials in PostgreSQL 19. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/settings.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py --test --ast-strict` |

---

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

Pre-flight execution of `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/seed/run_seed.py backend_v2/settings.py backend_v2/core/telemetry.py backend_v2/services/auth/secret_service.py backend_v2/main.py backend_v2/worker.py --include-one-hop` scanned all 6 primary targets and 87 1-hop callers:
- **Result:** **`0` technical debt findings (`✅ PASSED`)**.
- **Scoped Boy Scout Cleanup in Touched Files:** Eradicate the legacy synchronous `service-account.json` disk probe in `Settings.model_post_init` (`@[backend_v2/settings.py#L1172-L1211]`) and `Settings.enabled_providers` (`@[backend_v2/settings.py#L1320-L1351]`).

---

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1, Step 1: Add SecretScope.TELEMETRY, Enforce ROOT-Only SecretService Guardrails &amp; Sync Flutter Enum Parity">
    <constraint invariant="cross_language_enum_parity">Maintain 1:1 enum parity between SecretScope in backend_v2/models/enums.py and SecretScope in client_app_v2/lib/core/models/enums.dart, verified by test_enum_parity.py and enums_test.dart.</constraint>
    <constraint invariant="universal_fail_fast">Reject any SecretScope.TELEMETRY operation when initiator.role != UserRole.ROOT or organization_id != SystemOrganizations.ROOT_SYSTEM.value ("org_0195f3a0000070008000000000000001") by logging RFC 7807 logger.error and raising PermissionDeniedError (ErrorCodes.PERMISSION_DENIED, HTTP 403).</constraint>
    <constraint invariant="anti_happy_path_mandate">Write positive tests for ROOT telemetry secret provisioning/resolution and at least 2 negative tests (tenant ADMIN attempting to upsert/delete SecretScope.TELEMETRY raising PermissionDeniedError, and invalid telemetry target_identifier raising AppException with ErrorCodes.VALIDATION_FAILED).</constraint>
    <touched_artifacts>
      <artifact action="MODIFY" path="@[backend_v2/models/enums.py#L1395-L1399]" />
      <artifact action="MODIFY" path="@[backend_v2/services/auth/secret_service.py#L108-L1009]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/services/auth/test_secret_service.py#L681-L811]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/test_enum_parity.py#L290-L305]" />
      <artifact action="MODIFY" path="@[client_app_v2/lib/core/models/enums.dart#L711-L722]" />
      <artifact action="MODIFY" path="@[client_app_v2/test/core/models/enums_test.dart#L85-L115]" />
      <artifact action="MODIFY" path="@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]" />
      <artifact action="MODIFY" path="@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L846-L1025]" />
    </touched_artifacts>
    <action>1. In `@[backend_v2/models/enums.py#L1395-L1399]`, add `TELEMETRY = "telemetry"` to `SecretScope`.
2. In `@[backend_v2/services/auth/secret_service.py#L108-L1009]`:
   - Define `_VALID_TELEMETRY_TARGET_IDS: frozenset[str] = frozenset({"logfire", "logfire_read"})` alongside `_VALID_LLM_PROVIDER_IDS`.
   - Add a helper `_verify_telemetry_root_access(*, initiator: TokenData, organization_id: str) -> None` that checks `if initiator.role != UserRole.ROOT or organization_id != SystemOrganizations.ROOT_SYSTEM.value:` and logs `logger.error` + raises `PermissionDeniedError(message="Telemetry secrets are restricted exclusively to the ROOT user on the System Root organization.", details={"error_code": ErrorCodes.PERMISSION_DENIED.value, "organization_id": organization_id, "role": initiator.role.value})`.
   - Call `self._verify_telemetry_root_access(initiator=initiator, organization_id=organization_id)` in `upsert_tenant_secret` (`#L165-L249`) when `payload.scope == SecretScope.TELEMETRY` and in `delete_tenant_secret` (`#L251-L300`) when `record.scope == SecretScope.TELEMETRY`.
   - In `list_tenant_secrets` (`#L143-L163`), filter out records where `record.scope == SecretScope.TELEMETRY` if `initiator.role != UserRole.ROOT`.
   - In `_validate_target_identifier` (`#L759-L820`), add `if scope == SecretScope.TELEMETRY:`: verify `target_identifier in _VALID_TELEMETRY_TARGET_IDS` (raising `AppException(status_code=status.HTTP_400_BAD_REQUEST, message=..., details={"error_code": ErrorCodes.VALIDATION_FAILED.value, ...})` if invalid) and `return`.
   - Add `async def resolve_telemetry_secret(self, target_identifier: str = "logfire") -> ResolvedCredentialDTO:` delegating to `await self._resolve_scoped_secret(organization_id=SystemOrganizations.ROOT_SYSTEM.value, scope=SecretScope.TELEMETRY, target_identifier=target_identifier, target_kind_label="telemetry sink", detail_key="telemetry_target")`.
   - In `_record_audit_event` (`#L972-L1009`), add `elif record.scope == SecretScope.TELEMETRY: metadata["telemetry_target"] = record.target_identifier`.
3. In `@[backend_v2/tests/unit/test_enum_parity.py#L290-L305]`, update the expected `SecretScope` set at `#L280-L283` to `{"llm_provider", "mcp_gateway", "telemetry"}`.
4. In `@[backend_v2/tests/unit/services/auth/test_secret_service.py#L681-L811]`, add unit tests covering:
   - `ROOT` user provisioning and resolving `SecretScope.TELEMETRY` (`"logfire"` and `"logfire_read"`) on `SystemOrganizations.ROOT_SYSTEM.value` via `upsert_tenant_secret` and `resolve_telemetry_secret`.
   - Negative Path 1: `UserRole.ADMIN` attempting `upsert_tenant_secret` or `delete_tenant_secret` with `SecretScope.TELEMETRY` raises `PermissionDeniedError` (`ErrorCodes.PERMISSION_DENIED`), and `list_tenant_secrets` hides `SecretScope.TELEMETRY` from non-ROOT users.
   - Negative Path 2: `UserRole.ROOT` attempting `upsert_tenant_secret` with `SecretScope.TELEMETRY` on a non-`ROOT_SYSTEM` organization (`org_0195f3a0000070008000000000000777`) raises `PermissionDeniedError`, and passing an unknown `target_identifier="datadog"` raises `AppException` (`ErrorCodes.VALIDATION_FAILED`).
5. In `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`, add `@JsonValue('telemetry') telemetry('telemetry')` to `SecretScope`, and update `@[client_app_v2/test/core/models/enums_test.dart#L85-L115]`.
6. In `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`:
   - Add `final selectedTelemetryTarget = useState<String>('logfire');` in `_ByokSecretsCard.build`.
   - Update `_formatSecretTarget` (`#L1315-L1331`) and `effectiveTarget` (`#L1348-L1362`) exhaustive `switch` expressions to handle `SecretScope.telemetry`.
   - Filter the scope dropdown items (`#L1421`) so `SecretScope.telemetry` is included only when `currentUser?.role == UserRole.root && orgId == 'org_0195f3a0000070008000000000000001'`.
   - In the target selector `switch (selectedScope.value)` (`#L1476-L1525`), add the `SecretScope.telemetry => DropdownButtonFormField<String>(...)` branch offering `'logfire'` and `'logfire_read'`.
7. In `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L846-L1025]`, add widget tests verifying `SecretScope.telemetry` is selectable for `UserRole.root` on `org_0195f3a0000070008000000000000001` and hidden for tenant `UserRole.admin`.</action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/core/models/enums.dart --build --micro; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart --micro</validation_gate>
  </step>

  <step id="2" name="Phase 1, Step 2: Create .env.secrets.local &amp; .env.secrets.example, Clean Up .env, Delete service-account.json &amp; Wire Unified Secret Seeding into run_seed.py">
    <constraint invariant="credential_hardcoding_ban">Never commit plaintext secrets to Git. Ensure .env.secrets.local is listed in .gitignore before writing local secrets, and only commit redacted placeholders in .env.secrets.example.</constraint>
    <constraint invariant="strict_pydantic_v2_rust">Validate .env.secrets.local via LocalSeedSecretsSettings (SettingsConfigDict(extra='forbid', frozen=True)) and pre-validate SECRET_LLM_VERTEX_AI_SA_JSON structure before touching PostgreSQL 19.</constraint>
    <constraint invariant="anti_happy_path_mandate">Test positive end-to-end secret seeding and table count verification in test_run_seed.py alongside at least 2 negative tests (malformed SECRET_LLM_VERTEX_AI_SA_JSON raising AppException with ErrorCodes.VALIDATION_FAILED, and missing .env.secrets.local when require_file=True raising AppException with ErrorCodes.CONFIGURATION_ERROR).</constraint>
    <touched_artifacts>
      <artifact action="MODIFY" path="@[.gitignore#L124-L201]" />
      <artifact action="NEW" path="[NEW] @[.env.secrets.example]" />
      <artifact action="NEW" path="[NEW] @[.env.secrets.local]" />
      <artifact action="MODIFY" path="@[.env#L1-L18]" />
      <artifact action="DELETE" path="@[service-account.json]" />
      <artifact action="MODIFY" path="@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py#L37-L90]" />
      <artifact action="MODIFY" path="@[backend_v2/seed/run_seed.py#L84-L198]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/seed/test_run_seed.py#L264-L291]" />
    </touched_artifacts>
    <action>1. In `@[.gitignore#L124-L201]`, add `.env.secrets.local`, `.env.*.local`, and `!.env.secrets.example` under `# Environments`.
2. Create `[NEW] @[.env.secrets.example]` containing documented placeholder keys (`SECRET_LLM_AI_STUDIO`, `SECRET_LLM_OPENAI`, `SECRET_LLM_ANTHROPIC`, `SECRET_LLM_VERTEX_AI_SA_JSON`, `SECRET_MCP_TAVILY`, `SECRET_TELEMETRY_LOGFIRE_TOKEN`, `SECRET_TELEMETRY_LOGFIRE_READ_TOKEN`).
3. Create git-ignored `[NEW] @[.env.secrets.local]` by extracting the active decrypted `ROOT_SYSTEM` secrets from PostgreSQL 19 `tenant_secrets` (`ai_studio`, `openai`, `vertex_ai` JSON, `sys_0195f3a00000700080008172bda70c86` Tavily) and the Logfire tokens from `@[.env#L4-L5]` (`LOGFIRE_TOKEN`, `LOGFIRE_READ_TOKEN`).
4. Update `@[.env#L1-L18]` to remove `LOGFIRE_TOKEN`, `LOGFIRE_READ_TOKEN` (`#L4-L5`), and `MOCK_ADMIN_USER_ID`, `MOCK_ROOT_USER_ID`, `MOCK_ANALYST_USER_ID` (`#L14-L17`), retaining only Tier 1 Bootstrap variables (`JWT_SECRET_KEY`, `STORAGE_BACKEND`, `OTEL_ENABLED`, `ENVIRONMENT`, `DEV_EXECUTION_MODE`, `DUMP_PROMPTS_FILE`, `LITELLM_LOG`, `POSTGRES_PASSWORD`). Delete `[DELETE] @[service-account.json]` from the workspace root.
5. In `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, append `"tenant_secrets"` to `CANONICAL_SEED_TABLES` (making 11 canonical seed tables). In `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`, add `"tenant_secrets": len(self._store.seed_tables["tenant_secrets"])` to `counts` in `InMemoryEntityAdapter.verify_seed_table_counts`. Update `assert len(CANONICAL_SEED_TABLES) == 11` in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py#L37-L90]`.
6. In `@[backend_v2/seed/run_seed.py#L84-L198]`:
   - Define `SECRETS_LOCAL_PATH = PROJECT_ROOT / ".env.secrets.local"` and `TAVILY_MCP_GATEWAY_ID = "sys_0195f3a00000700080008172bda70c86"`.
   - Define `class LocalSeedSecretsSettings(BaseSettings):` with `model_config = SettingsConfigDict(extra="forbid", frozen=True, populate_by_name=True)` and PEP 593 `Annotated[SecretStr | None, Field(default=None, ...)]` fields for `secret_llm_ai_studio`, `secret_llm_openai`, `secret_llm_anthropic`, `secret_llm_vertex_ai_sa_json`, `secret_mcp_tavily`, `secret_telemetry_logfire_token`, and `secret_telemetry_logfire_read_token`, plus `@field_validator("secret_llm_vertex_ai_sa_json")` verifying that non-empty JSON contains `"type"`, `"project_id"`, `"private_key_id"`, `"private_key"`, and `"client_email"`.
   - Add `load_and_validate_local_seed_secrets(secrets_path: Path | None = None, *, require_file: bool = False) -> list[TenantSecretCreateDTO]` which loads `LocalSeedSecretsSettings(_env_file=resolved_path, _env_file_encoding="utf-8")` when `resolved_path.exists()` (or raises `_fail_fast` with `ErrorCodes.CONFIGURATION_ERROR` if `not resolved_path.exists() and require_file`) and builds the ordered list of `TenantSecretCreateDTO` payloads (`storage_mode=SecretStorageMode.ENVELOPE_KMS`).
   - Add `async def _seed_local_secrets(active_uow: QuorumUnitOfWork, secret_payloads: Sequence[TenantSecretCreateDTO]) -> int:` which instantiates `SecretService(entity_adapter=active_uow.entities)` and `root_initiator = TokenData(uid=SYSTEM_ROOT_USER_ID, email="root@system.local", role=UserRole.ROOT, organization_id=SystemOrganizations.ROOT_SYSTEM.value)` and awaits `secret_service.upsert_tenant_secret(initiator=root_initiator, organization_id=SystemOrganizations.ROOT_SYSTEM.value, payload=payload)` for each payload in `secret_payloads`.
   - In `_seed_postgres` (`@[backend_v2/seed/run_seed.py#L276-L338]`), accept `secrets_path: Path | None = None` and `require_secrets_file: bool = False`, call `secret_payloads = load_and_validate_local_seed_secrets(secrets_path, require_file=require_secrets_file)` during Stage 1 pre-flight validation, include `"tenant_secrets": len(secret_payloads)` in `expected_counts`, and inside `async with resolved_uow as active_uow:` (after `TOPOLOGICAL_SEED_ORDER` upserts `organizations` and `users`), call `await _seed_local_secrets(active_uow, secret_payloads)` before `verify_seed_table_counts(active_uow, expected_counts)`.
   - In `seed_database` (`@[backend_v2/seed/run_seed.py#L341-L379]`), pass `secrets_path=SECRETS_LOCAL_PATH` and `require_secrets_file=not dry_run` when `uow is None`.
7. In `@[backend_v2/tests/unit/seed/test_run_seed.py#L264-L291]`, add unit tests verifying:
   - `load_and_validate_local_seed_secrets` parses a valid `.env.secrets.local` file (including valid Vertex AI Service Account JSON and Logfire tokens) into `TenantSecretCreateDTO` instances and `_seed_postgres` persists them into `InMemoryUnitOfWork` `tenant_secrets` under `org_0195f3a0000070008000000000000001` with verified `tenant_secrets` table count.
   - Negative Path 1: Malformed or incomplete `SECRET_LLM_VERTEX_AI_SA_JSON` in `.env.secrets.local` fails fast in Stage 1 with `AppException` (`ErrorCodes.VALIDATION_FAILED`) before any database table is touched.
   - Negative Path 2: Missing `.env.secrets.local` when `require_file=True` raises `AppException` (`ErrorCodes.CONFIGURATION_ERROR` / `ErrorCodes.VALIDATION_FAILED`).</action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py backend_v2/seed/run_seed.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict</validation_gate>
  </step>

  <step id="3" name="Phase 1, Step 3: Wire Async Telemetry Logfire Secret Resolution &amp; Remove Legacy service-account.json Checks from Settings">
    <constraint invariant="single_pipeline_invariant_mandate">Resolve the Logfire write token from PostgreSQL 19 tenant_secrets (SecretScope.TELEMETRY, target_identifier='logfire') via SecretService during async startup in main.py and worker.py, and remove the synchronous service-account.json disk probe and startup crash from Settings.model_post_init.</constraint>
    <constraint invariant="security_logging_ban">Never pass unwrapped SecretStr values into logger.* or print() calls (QGR033); unwrap credential_value.get_secret_value() only when passing token=... to configure_telemetry / logfire.configure.</constraint>
    <constraint invariant="anti_happy_path_mandate">Test positive Logfire initialization from SecretService.resolve_telemetry_secret alongside at least 2 negative/boundary tests (missing telemetry secret in tenant_secrets degrading cleanly to native TracerProvider with a structured warning, and empty whitespace logfire_token override raising AppException with ErrorCodes.CONFIGURATION_ERROR).</constraint>
    <touched_artifacts>
      <artifact action="MODIFY" path="@[backend_v2/core/telemetry.py#L300-L414]" />
      <artifact action="MODIFY" path="@[backend_v2/main.py#L178-L242]" />
      <artifact action="MODIFY" path="@[backend_v2/worker.py#L49-L108]" />
      <artifact action="MODIFY" path="@[backend_v2/settings.py#L1172-L1211]" />
      <artifact action="MODIFY" path="@[backend_v2/settings.py#L1320-L1351]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/core/test_telemetry.py#L259-L288]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/test_settings.py#L146-L179]" />
      <artifact action="MODIFY" path="@[backend_v2/tests/unit/llm/test_google_providers_separation.py#L138-L180]" />
    </touched_artifacts>
    <action>1. In `@[backend_v2/core/telemetry.py#L300-L414]`:
   - Update `configure_telemetry(settings: Settings, service_name_override: str | None = None, app: Any | None = None, logfire_token: str | None = None) -> None` so that if `logfire_token is not None and not logfire_token.strip()`, it logs `logger.error` and raises `AppException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Telemetry logfire_token override cannot be empty or whitespace.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})`.
   - Resolve `effective_logfire_token: str | None = logfire_token if logfire_token is not None else settings.logfire_token` and use `effective_logfire_token` in place of `settings.logfire_token` at `#L337`, `#L371`, and `#L379`.
   - Add `async def resolve_startup_logfire_token(settings: Settings, secret_service: SecretService | None = None) -> str | None:` which returns `None` immediately if `not settings.otel_enabled`, returns `settings.logfire_token` if explicitly set on `settings`, and otherwise awaits `active_service.resolve_telemetry_secret("logfire")` (catching `AppException` to log a structured `logger.warning` and return `None` when no `logfire` secret is provisioned in `tenant_secrets`). Export `"resolve_startup_logfire_token"` in `__all__`.
2. In `@[backend_v2/main.py#L178-L242]` (`lifespan`):
   - Import `resolve_startup_logfire_token` from `backend_v2.core.telemetry`.
   - After `register_default_uow_factory(lambda: create_unit_of_work(settings))` and `_validate_database_preflight(settings)` (or right after registering the UoW factory), resolve `resolved_logfire_token = await resolve_startup_logfire_token(settings)` and pass `logfire_token=resolved_logfire_token` to `configure_telemetry(settings, app=app, logfire_token=resolved_logfire_token)`.
3. In `@[backend_v2/worker.py#L49-L108]` (`startup`):
   - Import `resolve_startup_logfire_token` from `backend_v2.core.telemetry`.
   - After `register_default_uow_factory(lambda: create_unit_of_work(settings))`, resolve `resolved_logfire_token = await resolve_startup_logfire_token(settings)` and pass `logfire_token=resolved_logfire_token` to `configure_telemetry(settings, service_name_override="quorum-worker", logfire_token=resolved_logfire_token)`.
4. In `@[backend_v2/settings.py#L1172-L1211]` (`model_post_init`) and `@[backend_v2/settings.py#L1320-L1351]` (`enabled_providers`):
   - Remove the synchronous `service-account.json` file auto-detection and synchronous `if not self.google_api_key and not has_vertex:` crash from `model_post_init` (`#L1181-L1211`), because LLM provider credentials now reside in PostgreSQL 19 `tenant_secrets` and `service-account.json` is deleted from the repository root.
   - Remove `or Path("service-account.json").exists()` from `enabled_providers` (`#L1335`).
5. Update `@[backend_v2/tests/unit/core/test_telemetry.py#L259-L288]`, `@[backend_v2/tests/unit/test_settings.py#L146-L179]`, and `@[backend_v2/tests/unit/llm/test_google_providers_separation.py#L138-L180]`:
   - In `test_telemetry.py`, add tests for `resolve_startup_logfire_token` (resolving from `SecretService`, degrading cleanly to `None` when unconfigured, and `configure_telemetry` rejecting whitespace `logfire_token=""` with `AppException`).
   - In `test_settings.py` and `test_google_providers_separation.py`, replace the legacy `service-account.json` disk-existence tests with tests asserting that `Settings(use_mock_llm=False)` initializes cleanly without `service-account.json` on disk or `google_api_key` in `.env`.
6. Execute `uv run python backend_v2/seed/run_seed.py` against local PostgreSQL 19 to verify that all 8 public collections and all 6 secrets from `.env.secrets.local` (`ai_studio`, `openai`, `vertex_ai`, `sys_0195f3a00000700080008172bda70c86`, `logfire`, `logfire_read`) are transactionally seeded and verified in PostgreSQL 19 `tenant_secrets`.</action>
    <validation_gate>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/settings.py backend_v2/tests/unit/core/test_telemetry.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py --test --ast-strict</validation_gate>
  </step>
</execution_protocol>
```

---

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path — Full Database Wipe & Unified Seeding via `run_seed.py`):**
  - **Input:** `.env.secrets.local` contains `SECRET_LLM_AI_STUDIO`, `SECRET_LLM_OPENAI`, `SECRET_LLM_VERTEX_AI_SA_JSON`, `SECRET_MCP_TAVILY`, `SECRET_TELEMETRY_LOGFIRE_TOKEN`, and `SECRET_TELEMETRY_LOGFIRE_READ_TOKEN`. `uv run python backend_v2/seed/run_seed.py` is executed.
  - **Expected Output:** All 8 public collections from `seed_data.json` (`organizations` including `org_0195f3a0000070008000000000000001`, `users` including `usr_0195f3a00000700a83fd6b3d77c748f4`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`) AND `tenant_secrets` (`6` encrypted `ENVELOPE_KMS` records under `org_0195f3a0000070008000000000000001`) are upserted and verified via `verify_seed_table_counts`.
- **Scenario 2 (Happy Path — ROOT-Scoped Telemetry Secret Resolution at Startup):**
  - **Input:** `settings.otel_enabled = True`, `settings.logfire_token = None`, and `tenant_secrets` contains `(org_0195f3a0000070008000000000000001, SecretScope.TELEMETRY, "logfire")`. `resolve_startup_logfire_token` and `configure_telemetry` execute during `main.py` / `worker.py` startup.
  - **Expected Output:** `SecretService.resolve_telemetry_secret("logfire")` decrypts the token and `configure_telemetry` initializes `logfire.configure(token=...)` without any `LOGFIRE_TOKEN` in `.env`.
- **Scenario 3 (Negative Path 1 — Tenant Admin Forbidden from `SecretScope.TELEMETRY`):**
  - **Input:** A user with `UserRole.ADMIN` attempts `upsert_tenant_secret` or `delete_tenant_secret` with `scope=SecretScope.TELEMETRY`, or a `UserRole.ROOT` user attempts to provision `SecretScope.TELEMETRY` under a customer organization `org_0195f3a0000070008000000000000777`.
  - **Expected Output:** Raises `PermissionDeniedError` (HTTP 403) with `details["error_code"] == ErrorCodes.PERMISSION_DENIED.value`.
- **Scenario 4 (Negative Path 2 — Malformed Vertex AI Service Account JSON in `.env.secrets.local`):**
  - **Input:** `.env.secrets.local` contains `SECRET_LLM_VERTEX_AI_SA_JSON='{"project_id": "missing-keys"}'` (missing `private_key` and `client_email`). `load_and_validate_local_seed_secrets` is called.
  - **Expected Output:** Fails fast in Stage 1 pre-flight validation with `AppException` (`ErrorCodes.VALIDATION_FAILED`) before any PostgreSQL 19 transaction is opened.
- **Scenario 5 (Negative Path 3 — Invalid Telemetry Target Identifier or Whitespace Override):**
  - **Input:** `upsert_tenant_secret` is called with `scope=SecretScope.TELEMETRY, target_identifier="invalid_sink"`, or `configure_telemetry` is called with `logfire_token="   "`.
  - **Expected Output:** Raises `AppException` (`ErrorCodes.VALIDATION_FAILED` / `ErrorCodes.CONFIGURATION_ERROR`).

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
