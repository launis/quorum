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

# Tracker: EPIC 164 — Unified Local Secret Seeding, ROOT-Scoped Telemetry & Authentic Email/Password IAM Parity

**Epic:** @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]
**Audit Report:** @[docs/epic/EPIC_164_audit_report.md]
**Task Directory:** @[docs/epic/tasks_EPIC_164/]

## Phase Execution Status

### Phase 1: Backend `SecretScope.TELEMETRY`, `.env.secrets.local` Seeding Pipeline & Root Firebase User Provisioning
**Plan:** @[docs/epic/tasks_EPIC_164/01_phase1_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/01_phase1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]` (`e31d46648`)
  - [x] Step 1.1: SecretScope.TELEMETRY Cross-Language Enum Parity & Root-Only UI Selector Filtering
  - [x] Step 1.2: SecretService Root-Only SecretScope.TELEMETRY RBAC Enforcement & resolve_telemetry_secret
  - [x] Step 1.3: CANONICAL_SEED_TABLES tenant_secrets Registration, .env.secrets.local Hydration & ROOT Firebase User Provisioning in run_seed.py
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 2: Database-Driven Telemetry & Firebase Admin Startup Initialization, `.env` Sanitation & `service-account.json` Deletion
**Plan:** @[docs/epic/tasks_EPIC_164/02_phase2_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]` (`d2f9a87fb`)
  - [x] Step 2.1: Startup Logfire Token Resolution & firebase_admin Initialization from tenant_secrets
  - [x] Step 2.2: Eradicate service-account.json Checks, allow_mock_tokens & mock_*_user_id Across Backend & .env
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 3: Frontend `MockLoginPanel` & `MOCK_*_USER_ID` Eradication and Authentic Email/Password Login Parity
**Plan:** @[docs/epic/tasks_EPIC_164/03_phase3_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/03_phase3_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]` (`1012f18b9`)
  - [x] Step 3.1: Eradicate MockLoginPanel, allowMockTokens & mock*UserId from LoginScreen, Env & client_app_v2/.env
  - [x] Step 3.2: Eradicate debugMockLogin & debugSignInWithMockToken and Delegate MFA Enforcement in signInWithEmailAndPassword to Backend
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 4: Comprehensive Unit, Integration, Seed & E2E Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_164/04_phase4_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/04_phase4_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]` (`7df1c8daf`)
  - [x] Step 4.1: Backend Unit Test Suite Verification & ISTQB Boundary Coverage
  - [x] Step 4.2: Frontend Unit & Widget Test Suite Verification
  - [x] Step 4.3: Local Secret Seeding, Full-Stack Audit Loops & Live E2E Verification
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend & Frontend Full-Stack Integration Gate**

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide verification that `@[service-account.json]`, `allow_mock_tokens`, `mock_*_user_id`, `MockLoginPanel`, `debugMockLogin`, and `debugSignInWithMockToken` are completely removed.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_164_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/core/telemetry.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [x] @[backend_v2/logging_config.py]
  - [x] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/auth/secret_service.py]
  - [ ] @[backend_v2/services/auth/token_service.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_164_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/core/environment/env.dart]
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/features/auth/data/auth_repository.dart]
  - [ ] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart]
  - [ ] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_164_tracker.md] @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] @[ki_frontend_iam_role_segregation.md] @[ki_global_config_sovereignty.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_frontend_iam_role_segregation.md]`: Document `SecretScope.TELEMETRY` (`"telemetry"`) Root-only RBAC isolation (`UserRole.ROOT` on `"org_0195f3a0000070008000000000000001"`), `.env.secrets.local` seeding and Firebase `ROOT` user provisioning in `run_seed.py`, `initialize_firebase_admin_from_secrets`, removal of `MockLoginPanel` / `allow_mock_tokens` / `MOCK_*_USER_ID`, and backend-driven MFA evaluation in `AuthRepository.signInWithEmailAndPassword`.
     - `@[ki_global_config_sovereignty.md]`: Document removal of `service-account.json` file checks, `allow_mock_tokens`, and `mock_*_user_id` from `Settings` (`backend_v2/settings.py`) and Flutter `Env` (`client_app_v2/lib/core/environment/env.dart`), and database-driven `resolve_startup_logfire_token`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any module descriptions change.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing unified database secret seeding, `SecretScope.TELEMETRY`, and authentic Email + Password IAM parity in present tense without historical language or Epic IDs.

### Final Epic Audit

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] @[docs/epic/EPIC_164_tracker.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: Commit each verified logical step with explicit relative paths in English.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `/tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan -> Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-164-001 | Add `SecretScope.TELEMETRY` (`"telemetry"`) to Python `enums.py` and Dart `enums.dart`, and filter `_ByokSecretsCard` so `SecretScope.telemetry` is selectable only by `UserRole.root` on `"org_0195f3a0000070008000000000000001"` | Phase 1, Step 1.1 | [x] Completed |
| REQ-164-002 | Enforce `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` for `SecretScope.TELEMETRY` in `SecretService` and add `resolve_telemetry_secret` | Phase 1, Step 1.2 | [x] Completed |
| REQ-164-003 | Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` and `InMemoryEntityAdapter.verify_seed_table_counts`, create `.env.secrets.example` and `.env.secrets.local`, and implement `LocalSeedSecretsSettings`, `_seed_local_secrets`, and `_provision_root_firebase_user` in `run_seed.py` | Phase 1, Step 1.3 | [x] Completed |
| REQ-164-004 | Add `resolve_startup_logfire_token` in `telemetry.py` and `initialize_firebase_admin_from_secrets` in `token_service.py`, and wire both into `main.py` and `worker.py` startup | Phase 2, Step 2.1 | [x] Completed |
| REQ-164-005 | Remove `service-account.json` checks, `allow_mock_tokens`, and `mock_*_user_id` from `settings.py`, `logging_config.py`, `token_service.py`, and `run_e2e_variance_test.py`, sanitize `.env`, and delete `service-account.json` | Phase 2, Step 2.2 | [x] Completed |
| REQ-164-006 | Delete `MockLoginPanel`, `allowMockTokens`, `_requireMockUserId`, and `mock*UserId` from `login_screen.dart`, `env.dart`, and `client_app_v2/.env` | Phase 3, Step 3.1 | [x] Completed |
| REQ-164-007 | Delete `_activeDebugUserId`, `debugMockLogin`, and `debugSignInWithMockToken`, and refactor `AuthRepository.signInWithEmailAndPassword` to delegate MFA enforcement to backend `exchangeToken(idToken)` | Phase 3, Step 3.2 | [x] Completed |
| REQ-164-008 | Verify and expand ISTQB positive, negative, and boundary unit tests across all 8 backend unit test suites | Phase 4, Step 4.1 | [x] Completed |
| REQ-164-009 | Verify and expand unit and widget tests across all 7 Flutter test suites | Phase 4, Step 4.2 | [x] Completed |
| REQ-164-010 | Execute `run_seed.py local --dry-run`, `run_seed.py local`, global backend and Flutter audit loops, and live E2E verification | Phase 4, Step 4.3 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Phase 1 (`e31d46648`), Phase 2 (`d2f9a87fb`), Phase 3 (`1012f18b9`), and Phase 4 (`/tier2-execute --full-auto` of `@[docs/epic/tasks_EPIC_164/04_phase4_plan.md]`):
  - **Step 4.1 (`4dce6abac`)**: Added `test_run_seed_dry_run_validates_local_secrets_without_db_mutation` and `test_live_e2e_real_llm_execution_with_seeded_tenant_secrets` to `@[backend_v2/tests/unit/seed/test_run_seed.py]`, added `test_epic_164_deprecated_symbols_and_files_absent_across_codebase` to `@[backend_v2/tests/unit/test_settings.py]`, and verified all 8 backend unit test suites (`test_secret_service.py`, `test_enum_parity.py`, `test_coercion_and_constants.py`, `test_run_seed.py`, `test_telemetry.py`, `test_settings.py`, `test_google_providers_separation.py`, `test_token_service.py`) pass with >90% coverage and 0 AST guardrail violations.
  - **Step 4.2**: Verified all 7 Flutter unit and widget test suites (`enums_test.dart`, `organization_iam_settings_view_test.dart`, `login_screen_test.dart`, `env_test.dart`, `auth_repository_test.dart`, `auth_controller_test.dart`, `auth_interceptor_test.dart`) and the full Flutter test suite (`1,383` passed, `0` failures) via `scripts/flutter_audit_loop.py client_app_v2/ --build`.
  - **Step 4.3**: Executed `run_seed.py local --dry-run` and `run_seed.py local` (upserting 6 encrypted secrets into `tenant_secrets`, provisioning the `ROOT` user in Firebase Authentication `cognitive-quorum`, and verifying all 11 PostgreSQL 19 tables), verified global `backend_audit_loop.py backend_v2/ --test --ast-strict` (`7,041` passed, `97.48%` coverage), verified `audit_epic_coverage.py --epic docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md` (`100% PASS` across 37 files and 7 deprecated symbols), and verified live E2E execution (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`, `7 passed`).

## Learned
- Because `TokenExchangeRequestDTO.service_auth_secret` is typed as `SecretStr | None`, calling `exchange_req.model_dump(mode="json", exclude_none=True)` redacts the secret to `'**********'`. Unwrapping `exchange_req.service_auth_secret.get_secret_value()` at the outbound HTTP JSON request boundary in `_get_or_refresh_cli_session` (`@[scripts/run_e2e_variance_test.py#L199-L216]`) and synchronizing an ephemeral `SERVICE_AUTH_SECRET` via `secrets.token_urlsafe(32)` in `_prepare_clean_subprocess_env` (`@[backend_v2/tests/integration/test_integration_real_llm.py#L340-L374]`) ensures headless M2M CLI token exchange succeeds deterministically without hardcoding static credentials.

## Remaining
- Run `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]` to audit Phase 4 before executing Post-Implementation Gates, `/tier7-describe-architecture`, and `/tier8-audit-epic`.

## Resume Command
```powershell
/tier8-audit-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]
```

