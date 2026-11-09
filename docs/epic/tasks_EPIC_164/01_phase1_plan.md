<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# EPIC 164 - Phase 1: Backend `SecretScope.TELEMETRY`, `.env.secrets.local` Seeding Pipeline & Root Firebase User Provisioning

**Overview:** Introduce `SecretScope.TELEMETRY` (`"telemetry"`) across Python (`@[backend_v2/models/enums.py#L1395-L1399]`) and Flutter (`@[client_app_v2/lib/core/models/enums.dart#L711-L722]`), restrict `SecretScope.TELEMETRY` in `@[backend_v2/services/auth/secret_service.py#L108-L1009]` and `_ByokSecretsCard` (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`) exclusively to `UserRole.ROOT` and the Root System Organization (`"org_0195f3a0000070008000000000000001"`), register `"tenant_secrets"` in `CANONICAL_SEED_TABLES` (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`) and `InMemoryEntityAdapter.verify_seed_table_counts` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`), create `[NEW] @[.env.secrets.example]` and git-ignored `[NEW] @[.env.secrets.local]`, and extend `@[backend_v2/seed/run_seed.py#L257-L273]` (`LocalSeedSecretsSettings`, `_seed_local_secrets`, `_provision_root_firebase_user`) so `uv run python backend_v2/seed/run_seed.py local` seeds all configured Root System Organization secrets into PostgreSQL 19 `tenant_secrets` and provisions/synchronizes ONLY the `ROOT` user (`"usr_0195f3a00000700a83fd6b3d77c748f4"`) in Firebase Authentication (`email_verified=True`) and PostgreSQL 19 `users`.

**Source:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`

**Target Files:**
- `[MODIFY] @[backend_v2/models/enums.py#L1395-L1399]`
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart#L711-L722]`
- `[MODIFY] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`
- `[MODIFY] @[backend_v2/services/auth/secret_service.py#L108-L1009]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`
- `[MODIFY] @[backend_v2/seed/run_seed.py#L257-L273]`
- `[NEW] @[.env.secrets.example]`
- `[NEW] @[.env.secrets.local]`
- `[MODIFY] @[.gitignore]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py]`
- `[MODIFY] @[client_app_v2/test/core/models/enums_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L1395-L1399]`, `@[client_app_v2/lib/core/models/enums.dart#L711-L722]` & `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]` | Storing telemetry credentials in plaintext `.env` without a typed `SecretScope` variant. | Add `TELEMETRY = "telemetry"` to Python `SecretScope`, add `telemetry('telemetry')` to Dart `SecretScope`, and expose `SecretScope.telemetry` in `_ByokSecretsCard` exclusively to `UserRole.root` on `"org_0195f3a0000070008000000000000001"`. | No separate database table for telemetry secrets; reuse `tenant_secrets` with `SecretScope.TELEMETRY`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |
| `@[backend_v2/services/auth/secret_service.py#L108-L1009]` | Allowing non-`ROOT` roles or tenant organizations to read/write `SecretScope.TELEMETRY`. | Enforce `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` on `SecretScope.TELEMETRY` and add `resolve_telemetry_secret`. | Reuse existing AES-256-GCM envelope encryption and `ResolvedCredentialDTO` in `SecretService`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict` |
| `@[backend_v2/seed/run_seed.py#L257-L273]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` & `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` | Wiping `tenant_secrets` without re-seeding local credentials or leaving `ROOT` unprovisioned in Firebase Auth. | Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` and `InMemoryEntityAdapter.verify_seed_table_counts`, hydrate `.env.secrets.local` via `LocalSeedSecretsSettings` into `tenant_secrets`, and provision/sync the `ROOT` user (`SECRET_ROOT_USER_EMAIL` + `SECRET_ROOT_USER_PASSWORD`) in Firebase Auth during `run_seed.py`. | Provision only the `ROOT` user in `run_seed.py`; all other users are provisioned via UI Onboarding (`UserService.create_user`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py backend_v2/seed/run_seed.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_audit_report.md]`, `@[backend_v2/models/enums.py#L1395-L1399]`, `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`, `@[backend_v2/services/auth/secret_service.py#L108-L1009]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`, and `@[backend_v2/seed/run_seed.py#L257-L273]`.</action>
    <action>Look forward: Verify Step 1.1 synchronizes `SecretScope.TELEMETRY` across Python and Dart with Root-only UI visibility, Step 1.2 enforces `UserRole.ROOT` and `"org_0195f3a0000070008000000000000001"` on `SecretScope.TELEMETRY` in `SecretService`, and Step 1.3 adds `"tenant_secrets"` to `CANONICAL_SEED_TABLES` and implements `.env.secrets.local` seeding and Firebase `ROOT` user provisioning in `run_seed.py`.</action>
    <constraint invariant="credential_hardcoding_ban">Never commit plaintext secrets to `backend_v2/seed/seed_data.json` or `.env.secrets.example`; real local secrets reside exclusively in git-ignored `.env.secrets.local` and are encrypted into PostgreSQL 19 `tenant_secrets` via `SecretService`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] and @[docs/epic/EPIC_164_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/enums.py#L1395-L1399]</backend>
    <frontend>@[client_app_v2/lib/core/models/enums.dart#L711-L722]</frontend>
    <frontend>@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]</frontend>
    <backend>@[backend_v2/services/auth/secret_service.py#L108-L1009]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]</backend>
    <backend>@[backend_v2/seed/run_seed.py#L257-L273]</backend>
    <backend>[NEW] @[.env.secrets.example]</backend>
    <backend>[NEW] @[.env.secrets.local]</backend>
    <backend>@[.gitignore]</backend>
    <backend>@[backend_v2/tests/unit/test_enum_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/services/auth/test_secret_service.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/seed/test_run_seed.py]</backend>
    <frontend>@[client_app_v2/test/core/models/enums_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`SecretScope.TELEMETRY` (`"telemetry"`) is defined in `@[backend_v2/models/enums.py#L1395-L1399]` and `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`, and `_ByokSecretsCard` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]` exposes `SecretScope.telemetry` exclusively when `currentUser?.role == UserRole.root &amp;&amp; orgId == 'org_0195f3a0000070008000000000000001'`.</item>
    <item>`SecretService` in `@[backend_v2/services/auth/secret_service.py#L108-L1009]` enforces `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` on all `SecretScope.TELEMETRY` operations and provides `resolve_telemetry_secret(self, target_identifier: str = "logfire") -> ResolvedCredentialDTO`.</item>
    <item>`"tenant_secrets"` is added to `CANONICAL_SEED_TABLES` (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`) and `InMemoryEntityAdapter.verify_seed_table_counts` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`), `[NEW] @[.env.secrets.example]` and git-ignored `[NEW] @[.env.secrets.local]` are created, and `run_seed.py` (`@[backend_v2/seed/run_seed.py#L257-L273]`) seeds `.env.secrets.local` into `tenant_secrets` and provisions/synchronizes ONLY the `ROOT` user in Firebase Authentication and PostgreSQL 19 `users`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT add secrets or credentials to `backend_v2/seed/seed_data.json` (`credential_hardcoding_ban`).</anti_target>
    <anti_target>Do NOT allow `UserRole.ADMIN` or non-Root tenant organizations to create, list, or delete `SecretScope.TELEMETRY` secrets.</anti_target>
    <anti_target>Do NOT provision non-`ROOT` users in `run_seed.py`; only the `ROOT` user (`"usr_0195f3a00000700a83fd6b3d77c748f4"`) is provisioned during seed execution.</anti_target>
  </anti_targets>

  <step id="1.1" name="SecretScope.TELEMETRY Cross-Language Enum Parity &amp; Root-Only UI Selector Filtering">
    <action>1. `[MODIFY]` `@[backend_v2/models/enums.py#L1395-L1399]`: Add `TELEMETRY = "telemetry"` to `SecretScope`.</action>
    <action>2. `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`: Add `@JsonValue('telemetry') telemetry('telemetry')` to `SecretScope`.</action>
    <action>3. `[MODIFY]` `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`: Update exhaustive Dart 3 `switch (secret.scope)` and `switch (selectedScope.value)` expressions in `_ByokSecretsCard` to handle `SecretScope.telemetry` (with target choices `'logfire'` and `'logfire_read'`), and filter the scope dropdown items so `SecretScope.telemetry` is selectable ONLY when `currentUser?.role == UserRole.root &amp;&amp; orgId == 'org_0195f3a0000070008000000000000001'`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[client_app_v2/test/core/models/enums_test.dart]`, and `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`: Update `SecretScope` expected enum values to include `"telemetry"` / `SecretScope.telemetry` and verify `_ByokSecretsCard` role/organization filtering.</action>
    <constraint invariant="cross_language_enum_parity">`SecretScope` in Python and Dart MUST maintain 1:1 member and `@JsonValue` parity verified by `test_enum_parity.py`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict</audit_command>
  </step>

  <step id="1.2" name="SecretService Root-Only SecretScope.TELEMETRY RBAC Enforcement &amp; resolve_telemetry_secret">
    <action>1. `[MODIFY]` `@[backend_v2/services/auth/secret_service.py#L108-L1009]`: Update `SecretService` so that:
      - `list_tenant_secrets` filters out `record.scope == SecretScope.TELEMETRY` whenever `initiator.role != UserRole.ROOT` or `organization_id != ROOT_SYSTEM_ORGANIZATION_ID` (`"org_0195f3a0000070008000000000000001"`).
      - `upsert_tenant_secret` and `delete_tenant_secret` enforce that any operation targeting `scope == SecretScope.TELEMETRY` requires `initiator.role == UserRole.ROOT` and `organization_id == ROOT_SYSTEM_ORGANIZATION_ID`, logging `logger.error` and raising `AuthorizationError(ErrorCodes.PERMISSION_DENIED)` otherwise.
      - `_validate_target_identifier` validates `SecretScope.TELEMETRY` target identifiers against `frozenset({"logfire", "logfire_read"})`, raising `AppException` (`ErrorCodes.VALIDATION_FAILED`, `status_code=400`) on unknown telemetry target identifiers.
      - Add `async def resolve_telemetry_secret(self, target_identifier: str = "logfire") -> ResolvedCredentialDTO` resolving the `SecretScope.TELEMETRY` secret strictly from `ROOT_SYSTEM_ORGANIZATION_ID` (`"org_0195f3a0000070008000000000000001"`).</action>
    <action>2. `[MODIFY]` `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`: Add positive, negative, and boundary unit tests using `UserFactory.build(...)` / `TokenData` verifying `SecretScope.TELEMETRY` RBAC isolation (`UserRole.ROOT` allowed on Root System Organization; `UserRole.ADMIN` and tenant organizations rejected with `AuthorizationError`), target identifier validation, and `resolve_telemetry_secret`.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every `AuthorizationError` or `AppException` raised for `SecretScope.TELEMETRY` violations MUST be preceded by a structured `logger.error` call.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict</audit_command>
  </step>

  <step id="1.3" name="CANONICAL_SEED_TABLES tenant_secrets Registration, .env.secrets.local Hydration &amp; ROOT Firebase User Provisioning in run_seed.py">
    <action>1. `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` and `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`: Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` (11 canonical seed tables) in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` and add `"tenant_secrets": len(self._store.seed_tables["tenant_secrets"])` to `InMemoryEntityAdapter.verify_seed_table_counts` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` so `reset_seed_tables()` and `verify_seed_table_counts()` include `tenant_secrets`.</action>
    <action>2. `[NEW]` `@[.env.secrets.example]`, `[NEW]` `@[.env.secrets.local]`, and `[MODIFY]` `@[.gitignore]`: Create committed template `@[.env.secrets.example]` with placeholder keys (`SECRET_AI_STUDIO_API_KEY`, `SECRET_VERTEX_AI_SA_JSON`, `SECRET_OPENAI_API_KEY`, `SECRET_ANTHROPIC_API_KEY`, `SECRET_TAVILY_API_KEY`, `SECRET_LOGFIRE_TOKEN`, `SECRET_LOGFIRE_READ_TOKEN`, `SECRET_ROOT_USER_EMAIL`, `SECRET_ROOT_USER_PASSWORD`), add `.env.secrets.local` to `@[.gitignore]`, and populate git-ignored `@[.env.secrets.local]` on disk from existing local workspace credentials (`@[.env#L4-L5]` and `@[service-account.json]`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/seed/run_seed.py#L257-L273]`: Define `LocalSeedSecretsSettings(BaseSettings)` (`model_config = SettingsConfigDict(env_file=".env.secrets.local", env_file_encoding="utf-8", extra="forbid", case_sensitive=False)`) with `Annotated[SecretStr | None, Field(default=None, ...)]` fields for the 7 secret keys plus `secret_root_user_email` and `secret_root_user_password`. Implement `_seed_local_secrets(uow: QuorumUnitOfWork, secrets_settings: LocalSeedSecretsSettings)` to encrypt and upsert all non-empty secrets into PostgreSQL 19 `tenant_secrets` under `"org_0195f3a0000070008000000000000001"` via `SecretService(entity_adapter=uow.entities)` (and include `"tenant_secrets": seeded_secrets_count` in `expected_counts`), and implement `_provision_root_firebase_user(uow: QuorumUnitOfWork, secrets_settings: LocalSeedSecretsSettings)` to initialize `firebase_admin` from `secret_vertex_ai_sa_json`, create or update ONLY the `ROOT` user (`"usr_0195f3a00000700a83fd6b3d77c748f4"`) in Firebase Authentication with `email_verified=True`, and update `usr_0195f3a00000700a83fd6b3d77c748f4` in PostgreSQL 19 `users` with the resolved `firebase_uid` and `email`. Ensure `dry_run=True` validates `LocalSeedSecretsSettings` in-memory without writing to PostgreSQL 19 or calling Firebase Authentication.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` and `@[backend_v2/tests/unit/seed/test_run_seed.py]`: Update `CANONICAL_SEED_TABLES` count assertion from 10 to 11 and add unit tests for `LocalSeedSecretsSettings`, `_seed_local_secrets`, and `_provision_root_firebase_user` (including `--dry-run` isolation, create-on-missing, update-on-existing, and Fail-Fast validation).</action>
    <constraint invariant="duck_typing_token_shield_ban">`LocalSeedSecretsSettings` MUST enforce `extra="forbid"` so unknown or misspelled variables in `.env.secrets.local` trigger immediate Fail-Fast validation errors.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py backend_v2/seed/run_seed.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_secret_scope_telemetry_python_and_dart_parity" category="positive">
      <input>Inspect `SecretScope` in `backend_v2/models/enums.py` and `client_app_v2/lib/core/models/enums.dart` via `test_enum_parity.py`</input>
      <expected>Both Python and Dart `SecretScope` contain `{"llm_provider", "mcp_gateway", "telemetry"}` in 1:1 parity</expected>
    </test>
    <test name="test_secret_service_telemetry_scope_allows_root_on_root_org" category="positive">
      <input>`UserFactory.build(role=UserRole.ROOT, organization_id="org_0195f3a0000070008000000000000001")` upserts `TenantSecretCreateDTO(scope=SecretScope.TELEMETRY, target_identifier="logfire", plaintext_secret=SecretStr("lf_tok_12345678"))` and calls `resolve_telemetry_secret("logfire")`</input>
      <expected>Persists encrypted secret in `InMemoryUnitOfWork` and `resolve_telemetry_secret("logfire")` returns `ResolvedCredentialDTO` with decrypted `"lf_tok_12345678"`</expected>
    </test>
    <test name="test_secret_service_telemetry_scope_rejects_tenant_admin_and_non_root_org" category="negative">
      <input>`UserRole.ADMIN` or `UserRole.ROOT` targeting a non-Root organization ID attempts `upsert_tenant_secret` or `delete_tenant_secret` with `scope=SecretScope.TELEMETRY`</input>
      <expected>Logs structured `logger.error` with `ErrorCodes.PERMISSION_DENIED.name` and raises `AuthorizationError` (HTTP 403)</expected>
    </test>
    <test name="test_secret_service_telemetry_scope_rejects_unknown_target_identifier" category="boundary">
      <input>`UserRole.ROOT` on `"org_0195f3a0000070008000000000000001"` attempts `upsert_tenant_secret` with `scope=SecretScope.TELEMETRY` and `target_identifier="invalid_target"`</input>
      <expected>Logs `ErrorCodes.VALIDATION_FAILED.name` and raises `AppException` with `status_code=400`</expected>
    </test>
    <test name="test_run_seed_seeds_local_secrets_and_provisions_root_firebase_user" category="positive">
      <input>`_seed_postgres` executed with `InMemoryUnitOfWork`, mocked Firebase Admin auth client, and `LocalSeedSecretsSettings` containing `SECRET_AI_STUDIO_API_KEY`, `SECRET_VERTEX_AI_SA_JSON`, `SECRET_LOGFIRE_TOKEN`, `SECRET_ROOT_USER_EMAIL`, and `SECRET_ROOT_USER_PASSWORD`</input>
      <expected>Populates encrypted rows in `uow.entities` (`tenant_secrets`), provisions/updates ONLY `usr_0195f3a00000700a83fd6b3d77c748f4` in Firebase Auth with `email_verified=True`, binds `firebase_uid` on `usr_0195f3a00000700a83fd6b3d77c748f4`, and verifies all 11 canonical seed tables</expected>
    </test>
    <test name="test_local_seed_secrets_settings_rejects_extra_unknown_keys" category="negative">
      <input>`LocalSeedSecretsSettings` instantiated with an unrecognized key (`UNKNOWN_SECRET_KEY="xyz"`)</input>
      <expected>Raises Pydantic `ValidationError` due to `extra="forbid"`</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 1 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/services/auth/secret_service.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py backend_v2/seed/run_seed.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/unit/test_enum_parity.py backend_v2/tests/unit/services/auth/test_secret_service.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict`.</action>
    <action>Run Phase 1 Flutter quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/core/models/enums_test.dart --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart`.</action>
  </validation_gate>
</execution_protocol>
```
