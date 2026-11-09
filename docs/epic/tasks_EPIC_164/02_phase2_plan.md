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

# EPIC 164 - Phase 2: Database-Driven Telemetry & Firebase Admin Startup Initialization, `.env` Sanitation & `service-account.json` Deletion

**Overview:** Migrate Logfire telemetry initialization (`@[backend_v2/core/telemetry.py#L300-L414]`) and `firebase_admin` initialization (`@[backend_v2/services/auth/token_service.py#L41-L580]`, `@[backend_v2/services/auth/token_service.py#L89-L97]`, `@[backend_v2/services/auth/token_service.py#L99-L166]`) in `@[backend_v2/main.py#L178-L242]` and `@[backend_v2/worker.py#L49-L108]` to resolve encrypted credentials directly from PostgreSQL 19 `tenant_secrets` (`SecretScope.TELEMETRY` `"logfire"` and `SecretScope.LLM_PROVIDER` `"vertex_ai"` under `"org_0195f3a0000070008000000000000001"`). Remove synchronous `service-account.json` file checks (`@[backend_v2/settings.py#L1172-L1211]`, `@[backend_v2/settings.py#L1320-L1351]`), `allow_mock_tokens` (`@[backend_v2/settings.py#L1367-L1387]`), and `mock_admin_user_id` / `mock_root_user_id` / `mock_analyst_user_id` (`#L1410-L1417`, `#L1418-L1425`, `#L1426-L1433`) from `@[backend_v2/settings.py#L68-L1492]` and `@[backend_v2/logging_config.py#L446-L479]`. Require `SERVICE_AUTH_SECRET` (`secrets.compare_digest`) unconditionally in `TokenService._resolve_headless_cli_user` (`@[backend_v2/services/auth/token_service.py#L304-L339]`), update `@[scripts/run_e2e_variance_test.py#L940-L1054]` to authenticate using `"usr_0195f3a00000700a83fd6b3d77c748f4"` + `settings.service_auth_secret`, sanitize `@[.env]` (`@[.env#L4-L5]`, `@[.env#L14-L17]`), and delete `[DELETE] @[service-account.json]`.

**Source:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`

**Target Files:**
- `[MODIFY] @[backend_v2/core/telemetry.py#L300-L414]`
- `[MODIFY] @[backend_v2/services/auth/token_service.py#L41-L580]`
- `[MODIFY] @[backend_v2/main.py#L178-L242]`
- `[MODIFY] @[backend_v2/worker.py#L49-L108]`
- `[MODIFY] @[backend_v2/settings.py#L68-L1492]`
- `[MODIFY] @[backend_v2/logging_config.py#L446-L479]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py#L940-L1054]`
- `[MODIFY] @[.env]`
- `[DELETE] @[service-account.json]`
- `[MODIFY] @[backend_v2/tests/unit/core/test_telemetry.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_settings.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_google_providers_separation.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_token_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/core/telemetry.py#L300-L414]`, `@[backend_v2/main.py#L178-L242]`, `@[backend_v2/worker.py#L49-L108]` & `@[backend_v2/services/auth/token_service.py#L41-L580]` | Reading `LOGFIRE_TOKEN` from `.env`, relying on `service-account.json` on disk, and leaving `firebase_admin` uninitialized. | Resolve `logfire` token via `resolve_startup_logfire_token` and initialize `firebase_admin` via `initialize_firebase_admin_from_secrets` using the decrypted `vertex_ai` Service Account JSON from `tenant_secrets`. | Single startup initialization in `main.py` and `worker.py` without background polling loops. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/services/auth/token_service.py backend_v2/tests/unit/core/test_telemetry.py backend_v2/tests/unit/test_token_service.py --test --ast-strict` |
| `@[backend_v2/settings.py#L68-L1492]`, `@[backend_v2/logging_config.py#L446-L479]`, `@[scripts/run_e2e_variance_test.py#L940-L1054]`, `@[.env]` & `[DELETE] @[service-account.json]` | Checking `Path("service-account.json").exists()` in `Settings.model_post_init` and `enabled_providers`, permitting unauthenticated headless token exchange via `allow_mock_tokens`, and storing `MOCK_*_USER_ID` and `LOGFIRE_*` in `.env`. | Delete `@[service-account.json]`, remove `allow_mock_tokens` and `mock_*_user_id` from `Settings` and `.env`, and authenticate headless CLI tools (`run_e2e_variance_test.py`) using `"usr_0195f3a00000700a83fd6b3d77c748f4"` + `SERVICE_AUTH_SECRET`. | One deterministic headless authentication gate (`secrets.compare_digest` against `settings.service_auth_secret`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/settings.py backend_v2/logging_config.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py --test --ast-strict` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_audit_report.md]`, `@[backend_v2/core/telemetry.py#L300-L414]`, `@[backend_v2/services/auth/token_service.py#L41-L580]`, `@[backend_v2/main.py#L178-L242]`, `@[backend_v2/worker.py#L49-L108]`, `@[backend_v2/settings.py#L68-L1492]`, `@[backend_v2/logging_config.py#L446-L479]`, and `@[scripts/run_e2e_variance_test.py#L940-L1054]`.</action>
    <action>Look forward: Verify Step 2.1 wires database-driven Logfire and Firebase Admin initialization in `telemetry.py`, `token_service.py`, `main.py`, and `worker.py`, and Step 2.2 eradicates `service-account.json`, `allow_mock_tokens`, and `mock_*_user_id` across `settings.py`, `logging_config.py`, `token_service.py`, `run_e2e_variance_test.py`, and `.env`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">Headless CLI token exchange in `TokenService._resolve_headless_cli_user` MUST require cryptographic `SERVICE_AUTH_SECRET` verification (`secrets.compare_digest`) unconditionally with zero `allow_mock_tokens` bypass.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] and @[docs/epic/EPIC_164_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/core/telemetry.py#L300-L414]</backend>
    <backend>@[backend_v2/services/auth/token_service.py#L41-L580]</backend>
    <backend>@[backend_v2/main.py#L178-L242]</backend>
    <backend>@[backend_v2/worker.py#L49-L108]</backend>
    <backend>@[backend_v2/settings.py#L68-L1492]</backend>
    <backend>@[backend_v2/logging_config.py#L446-L479]</backend>
    <backend>@[scripts/run_e2e_variance_test.py#L940-L1054]</backend>
    <backend>@[.env]</backend>
    <backend>@[service-account.json]</backend>
    <backend>@[backend_v2/tests/unit/core/test_telemetry.py]</backend>
    <backend>@[backend_v2/tests/unit/test_settings.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_google_providers_separation.py]</backend>
    <backend>@[backend_v2/tests/unit/test_token_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`resolve_startup_logfire_token` in `@[backend_v2/core/telemetry.py#L300-L414]` and `initialize_firebase_admin_from_secrets` in `@[backend_v2/services/auth/token_service.py#L41-L580]` initialize Logfire and `firebase_admin` from PostgreSQL 19 `tenant_secrets` during `@[backend_v2/main.py#L178-L242]` and `@[backend_v2/worker.py#L49-L108]` startup.</item>
    <item>`allow_mock_tokens`, `mock_admin_user_id`, `mock_root_user_id`, `mock_analyst_user_id`, and `service-account.json` file checks are removed from `@[backend_v2/settings.py#L68-L1492]`, `@[backend_v2/logging_config.py#L446-L479]`, and `@[backend_v2/services/auth/token_service.py#L304-L339]`.</item>
    <item>`@[scripts/run_e2e_variance_test.py#L940-L1054]` authenticates using `"usr_0195f3a00000700a83fd6b3d77c748f4"` and `settings.service_auth_secret`, `@[.env]` is sanitized (`USE_FIREBASE_AUTH=true`, `REQUIRE_MFA=false`, zero `LOGFIRE_*` or `MOCK_*_USER_ID` variables), and `[DELETE] @[service-account.json]` is deleted from disk.</item>
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
    <anti_target>Do NOT log unwrapped `SecretStr` values (`get_secret_value()`) inside `logger.*`, `logfire.*`, or `print(...)` calls (`security_logging_ban` and `QGR033`).</anti_target>
    <anti_target>Do NOT retain `service-account.json` on disk or in `Settings` (`zero_compromise_cutover_mandate`).</anti_target>
  </anti_targets>

  <step id="2.1" name="Startup Logfire Token Resolution &amp; firebase_admin Initialization from tenant_secrets">
    <action>1. `[MODIFY]` `@[backend_v2/core/telemetry.py#L300-L414]`: Add `logfire_token: str | None = None` parameter to `configure_telemetry(settings: Settings, service_name_override: str | None = None, app: Any | None = None, logfire_token: str | None = None) -> None` (preferring `logfire_token` over `settings.logfire_token`), and add `async def resolve_startup_logfire_token(settings: Settings, secret_service: SecretService) -> str | None` which resolves the `SecretScope.TELEMETRY` (`"logfire"`) secret from `SecretService.resolve_telemetry_secret("logfire")` when `settings.otel_enabled` is `True`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/services/auth/token_service.py#L41-L580]`: Update `TokenService._init_firebase` (`@[backend_v2/services/auth/token_service.py#L89-L97]`) and `TokenService.exchange_firebase_token` (`@[backend_v2/services/auth/token_service.py#L99-L166]`) and add `async def initialize_firebase_admin_from_secrets(secret_service: SecretService, settings: Settings) -> None` so that when `settings.use_firebase_auth` is `True` and `not firebase_admin._apps`, it resolves the Root System Organization (`"org_0195f3a0000070008000000000000001"`) `LLMProvider.VERTEX_AI` secret via `secret_service.resolve_llm_key`, parses the Service Account JSON, and calls `firebase_admin.initialize_app(credentials.Certificate(sa_dict))`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/main.py#L178-L242]` and `@[backend_v2/worker.py#L49-L108]`: In `lifespan` (`@[backend_v2/main.py#L178-L242]`), after `await _validate_database_preflight(logger)`, instantiate `SecretService(uow_factory=get_registered_uow_factory())`, resolve `startup_logfire_token = await resolve_startup_logfire_token(settings, secret_service)`, call `configure_telemetry(settings, app=app, logfire_token=startup_logfire_token)`, and call `await initialize_firebase_admin_from_secrets(secret_service, settings)`. In `startup` (`@[backend_v2/worker.py#L49-L108]`), resolve `startup_logfire_token = await resolve_startup_logfire_token(settings, secret_service)` and pass `logfire_token=startup_logfire_token` to `configure_telemetry`.</action>
    <action>4. `[MODIFY]` `@[backend_v2/tests/unit/core/test_telemetry.py]`: Add unit tests for `resolve_startup_logfire_token` and `configure_telemetry(..., logfire_token=...)`.</action>
    <constraint invariant="security_logging_ban">Unwrapping `.get_secret_value()` on `ResolvedCredentialDTO.api_key` MUST occur strictly at `logfire.configure(token=...)` and `credentials.Certificate(...)` call sites without logging secret contents.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/services/auth/token_service.py backend_v2/tests/unit/core/test_telemetry.py --test --ast-strict</audit_command>
  </step>

  <step id="2.2" name="Eradicate service-account.json Checks, allow_mock_tokens &amp; mock_*_user_id Across Backend &amp; .env">
    <demolish>
      Delete `[DELETE] @[service-account.json]`, and remove `allow_mock_tokens` (`@[backend_v2/settings.py#L1367-L1387]`), `mock_admin_user_id` (`#L1410-L1417`), `mock_root_user_id` (`#L1418-L1425`), and `mock_analyst_user_id` (`#L1426-L1433`) from `@[backend_v2/settings.py#L68-L1492]`.
    </demolish>
    <action>1. `[MODIFY]` `@[backend_v2/settings.py#L68-L1492]`: Remove `model_post_init` (`@[backend_v2/settings.py#L1172-L1211]`), remove `Path("service-account.json").exists()` from `enabled_providers` (`@[backend_v2/settings.py#L1320-L1351]`), and delete `allow_mock_tokens` (`@[backend_v2/settings.py#L1367-L1387]`), `mock_admin_user_id` (`#L1410-L1417`), `mock_root_user_id` (`#L1418-L1425`), and `mock_analyst_user_id` (`#L1426-L1433`).</action>
    <action>2. `[MODIFY]` `@[backend_v2/logging_config.py#L446-L479]`: Remove `mock_tokens_desc` and the `Mock Tokens Allowed:` log line from `log_startup_system_parameters`.</action>
    <action>3. `[MODIFY]` `@[backend_v2/services/auth/token_service.py#L304-L339]` and `@[scripts/run_e2e_variance_test.py#L940-L1054]`: Update `TokenService._resolve_headless_cli_user` (`@[backend_v2/services/auth/token_service.py#L304-L339]`) to check `if not secret_matches:` unconditionally (without the removed `allow_mock_tokens` bypass), and update `@[scripts/run_e2e_variance_test.py#L940-L1054]` (`_get_or_refresh_cli_session`, `trigger_execution`, and `run_variance_test`) to pass canonical Root user ID `"usr_0195f3a00000700a83fd6b3d77c748f4"` and `service_auth_secret` from `settings.service_auth_secret`.</action>
    <action>4. `[MODIFY]` `@[.env]` and `[DELETE]` `@[service-account.json]`: Remove `LOGFIRE_TOKEN` and `LOGFIRE_Read_Token` (`@[.env#L4-L5]`) and `MOCK_ADMIN_USER_ID`, `MOCK_ROOT_USER_ID`, `MOCK_ANALYST_USER_ID` (`@[.env#L14-L17]`) from `@[.env]`, set `USE_FIREBASE_AUTH=true` and `REQUIRE_MFA=false` in `@[.env]`, and delete `[DELETE] @[service-account.json]` from the workspace root.</action>
    <action>5. `[MODIFY]` `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`, and `@[backend_v2/tests/unit/test_token_service.py]`: Update unit tests to remove obsolete `allow_mock_tokens`, `mock_*_user_id`, and `service-account.json` assertions and verify `initialize_firebase_admin_from_secrets` and headless CLI `service_auth_secret` enforcement.</action>
    <constraint invariant="the_no_legacy_mandate">Zero references to `service-account.json`, `allow_mock_tokens`, `mock_admin_user_id`, `mock_root_user_id`, or `mock_analyst_user_id` may remain in `backend_v2/` or `scripts/`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/settings.py backend_v2/logging_config.py backend_v2/services/auth/token_service.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py backend_v2/tests/unit/test_token_service.py --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_resolve_startup_logfire_token_returns_decrypted_secret" category="positive">
      <input>`resolve_startup_logfire_token` called with `settings.otel_enabled=True` and `SecretService` containing `"logfire"` under `SecretScope.TELEMETRY` in `"org_0195f3a0000070008000000000000001"`</input>
      <expected>Returns the decrypted Logfire token string and `configure_telemetry` configures Logfire with that token</expected>
    </test>
    <test name="test_resolve_startup_logfire_token_returns_none_when_secret_missing_in_dev" category="boundary">
      <input>`resolve_startup_logfire_token` called when `tenant_secrets` has no `"logfire"` row</input>
      <expected>Returns `None` gracefully and `configure_telemetry` falls back to native `TracerProvider` with `LocalTraceSnapshotExporter`</expected>
    </test>
    <test name="test_initialize_firebase_admin_from_secrets_initializes_app_from_vertex_sa" category="positive">
      <input>`initialize_firebase_admin_from_secrets` invoked when `settings.use_firebase_auth=True` and `SecretService` holds valid `vertex_ai` Service Account JSON in `tenant_secrets`</input>
      <expected>Calls `credentials.Certificate` with parsed Service Account dictionary and initializes `firebase_admin`</expected>
    </test>
    <test name="test_initialize_firebase_admin_from_secrets_fails_fast_on_invalid_json" category="negative">
      <input>`initialize_firebase_admin_from_secrets` invoked when `vertex_ai` secret contains malformed non-JSON text</input>
      <expected>Logs structured `logger.error` with `ErrorCodes.CONFIGURATION_ERROR.name` and raises `ConfigurationError`</expected>
    </test>
    <test name="test_headless_cli_exchange_requires_service_auth_secret_even_in_development" category="negative">
      <input>`TokenService.exchange_firebase_token` called with `TokenExchangeRequestDTO(target_user_id="usr_0195f3a00000700a83fd6b3d77c748f4", service_auth_secret=None)` in `environment="development"`</input>
      <expected>Logs `ErrorCodes.PERMISSION_DENIED.name` and raises `AuthenticationError` (HTTP 403)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 2 backend quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/services/auth/token_service.py backend_v2/main.py backend_v2/worker.py backend_v2/settings.py backend_v2/logging_config.py scripts/run_e2e_variance_test.py backend_v2/tests/unit/core/test_telemetry.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py backend_v2/tests/unit/test_token_service.py --test --ast-strict`.</action>
  </validation_gate>
</execution_protocol>
```
