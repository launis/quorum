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

# EPIC 164 - Phase 4: Comprehensive Unit, Integration, Seed & E2E Verification Gate

**Overview:** Execute comprehensive ISTQB positive, negative, and boundary value verification across all 8 backend unit test suites (`@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/core/test_telemetry.py]`, `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`, `@[backend_v2/tests/unit/test_token_service.py]`) and all 7 Flutter unit/widget test suites (`@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`, `@[client_app_v2/test/unit/core/environment/env_test.dart]`, `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`, `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`, `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`), run `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python backend_v2/seed/run_seed.py local` (`@[backend_v2/seed/run_seed.py#L257-L273]`), and execute the global backend, Flutter, and live E2E verification gates.

**Source:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`

**Target Files:**
- `[MODIFY] @[backend_v2/tests/unit/services/auth/test_secret_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_enum_parity.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py]`
- `[MODIFY] @[backend_v2/tests/unit/core/test_telemetry.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_settings.py]`
- `[MODIFY] @[backend_v2/tests/unit/llm/test_google_providers_separation.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_token_service.py]`
- `[MODIFY] @[client_app_v2/test/core/models/enums_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/core/environment/env_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/core/test_telemetry.py]`, `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]` & `@[backend_v2/tests/unit/test_token_service.py]` | Legacy unit test assertions relying on `allow_mock_tokens`, `mock_*_user_id`, or `service-account.json` file existence. | Assert >90% coverage and ISTQB positive/negative/boundary test contracts across all 8 backend unit test suites using `InMemoryUnitOfWork` and `ModelFactory`. | Zero live network calls in unit tests (`hermetic_test_fixtures_mandate`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` |
| `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`, `@[client_app_v2/test/unit/core/environment/env_test.dart]`, `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`, `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]` & `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]` | Legacy widget and unit tests referencing `MockLoginPanel`, `debugMockLogin`, or `mock*UserId`. | Verify `SecretScope.telemetry` UI visibility and `signInWithEmailAndPassword` behavior across `200 OK` and `403 MFA_REQUIRED` responses, followed by `run_seed.py local` and live E2E verification. | Single unified full-stack verification pipeline. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_audit_report.md]`, and verify Phases 1, 2, and 3 are marked `[x]` in `@[docs/epic/EPIC_164_tracker.md]`.</action>
    <action>Look forward: Verify Step 4.1 audits all 8 backend test suites, Step 4.2 audits all 7 Flutter test suites, and Step 4.3 executes `run_seed.py local --dry-run`, `run_seed.py local`, global audit loops, and live E2E verification.</action>
    <constraint invariant="anti_happy_path_mandate">Every positive test case across the 8 backend and 7 Flutter test suites MUST be paired with at least 2 negative or boundary test cases.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] and @[docs/epic/EPIC_164_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/tests/unit/services/auth/test_secret_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_enum_parity.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/seed/test_run_seed.py]</backend>
    <backend>@[backend_v2/tests/unit/core/test_telemetry.py]</backend>
    <backend>@[backend_v2/tests/unit/test_settings.py]</backend>
    <backend>@[backend_v2/tests/unit/llm/test_google_providers_separation.py]</backend>
    <backend>@[backend_v2/tests/unit/test_token_service.py]</backend>
    <frontend>@[client_app_v2/test/core/models/enums_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/core/environment/env_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>All 8 backend unit test suites (`test_secret_service.py`, `test_enum_parity.py`, `test_coercion_and_constants.py`, `test_run_seed.py`, `test_telemetry.py`, `test_settings.py`, `test_google_providers_separation.py`, `test_token_service.py`) pass with >90% coverage and zero AST guardrail violations.</item>
    <item>All 7 Flutter test suites (`enums_test.dart`, `organization_iam_settings_view_test.dart`, `login_screen_test.dart`, `env_test.dart`, `auth_repository_test.dart`, `auth_controller_test.dart`, `auth_interceptor_test.dart`) pass with zero analyzer or Dart guardrail violations.</item>
    <item>`uv run python backend_v2/seed/run_seed.py local --dry-run`, `uv run python backend_v2/seed/run_seed.py local`, global `backend_audit_loop.py backend_v2/ --test`, global `flutter_audit_loop.py client_app_v2/ --build`, and `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` pass 100%.</item>
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
    <anti_target>Do NOT use `@pytest.mark.skip` or comment out failing tests (`anti_test_skipping_mandate`).</anti_target>
    <anti_target>Do NOT write tautological mocks that assert mocked return values without exercising real domain logic (`tautological_mocking_ban`).</anti_target>
  </anti_targets>

  <step id="4.1" name="Backend Unit Test Suite Verification &amp; ISTQB Boundary Coverage">
    <action>1. `[MODIFY]` `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/core/test_telemetry.py]`, `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`, and `@[backend_v2/tests/unit/test_token_service.py]`: Verify and expand positive, negative, and boundary unit test coverage across all 8 backend unit test suites using `ModelFactory.build(...)` and `InMemoryUnitOfWork`.</action>
    <constraint invariant="backend_quality_gate_delegation">Pass all 8 modified backend test file paths explicitly to `scripts/backend_audit_loop.py` so `mypy --strict` and `pytest` validate every test fixture and assertion.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/unit/services/auth/test_secret_service.py backend_v2/tests/unit/test_enum_parity.py backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py backend_v2/tests/unit/seed/test_run_seed.py backend_v2/tests/unit/core/test_telemetry.py backend_v2/tests/unit/test_settings.py backend_v2/tests/unit/llm/test_google_providers_separation.py backend_v2/tests/unit/test_token_service.py --test --ast-strict</audit_command>
  </step>

  <step id="4.2" name="Frontend Unit &amp; Widget Test Suite Verification">
    <action>1. `[MODIFY]` `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`, `@[client_app_v2/test/unit/core/environment/env_test.dart]`, `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`, `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`, and `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`: Verify and expand positive, negative, and boundary test coverage across all 7 Flutter unit and widget test suites.</action>
    <constraint invariant="frontend_quality_gate_delegation">Execute `scripts/flutter_audit_loop.py` across all modified Flutter test suites.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
  </step>

  <step id="4.3" name="Local Secret Seeding, Full-Stack Audit Loops &amp; Live E2E Verification">
    <action>1. Execute `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python backend_v2/seed/run_seed.py local` (`@[backend_v2/seed/run_seed.py#L257-L273]`) to verify all 11 canonical seed tables (including `tenant_secrets`) and `ROOT` user provisioning in Firebase Authentication (`cognitive-quorum`) and PostgreSQL 19 `users`.</action>
    <action>2. Execute global `backend_audit_loop.py backend_v2/ --test`, global `flutter_audit_loop.py client_app_v2/ --build`, `audit_epic_coverage.py --epic docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md`, and live E2E verification `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
    <constraint invariant="fragmented_quality_gates_prevention">Both global completion gates (`backend_audit_loop.py backend_v2/ --test` and `flutter_audit_loop.py client_app_v2/ --build`) and live E2E verification MUST pass 100% before closing Phase 4.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict</audit_command>
  </step>

  <test_contracts>
    <test name="test_run_seed_dry_run_validates_local_secrets_without_db_mutation" category="positive">
      <input>`uv run python backend_v2/seed/run_seed.py local --dry-run` executed with valid `.env.secrets.local`</input>
      <expected>Validates `seed_data.json` and `LocalSeedSecretsSettings` in-memory and exits 0 without mutating PostgreSQL 19 `tenant_secrets` or calling Firebase Auth</expected>
    </test>
    <test name="test_epic_164_deprecated_symbols_and_files_absent_across_codebase" category="negative">
      <input>Run `scripts/audit_epic_coverage.py --epic docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md`</input>
      <expected>Verifies 0 occurrences of `service-account.json`, `allow_mock_tokens`, `mock_admin_user_id`, `MockLoginPanel`, `debugMockLogin`, and `debugSignInWithMockToken` across target files</expected>
    </test>
    <test name="test_live_e2e_real_llm_execution_with_seeded_tenant_secrets" category="boundary">
      <input>`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</input>
      <expected>Seeds PostgreSQL 19 `tenant_secrets` from `.env.secrets.local`, authenticates via `SERVICE_AUTH_SECRET`, and completes full E2E workflow and PDF generation</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run global Backend, Flutter, and E2E quality gates: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </validation_gate>
</execution_protocol>
```

