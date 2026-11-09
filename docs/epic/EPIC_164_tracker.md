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
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]`
  - [x] Step 1.1: SecretScope.TELEMETRY Cross-Language Enum Parity & Root-Only UI Selector Filtering
  - [x] Step 1.2: SecretService Root-Only SecretScope.TELEMETRY RBAC Enforcement & resolve_telemetry_secret
  - [x] Step 1.3: CANONICAL_SEED_TABLES tenant_secrets Registration, .env.secrets.local Hydration & ROOT Firebase User Provisioning in run_seed.py
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 2: Database-Driven Telemetry & Firebase Admin Startup Initialization, `.env` Sanitation & `service-account.json` Deletion
**Plan:** @[docs/epic/tasks_EPIC_164/02_phase2_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/02_phase2_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]`
  - [ ] Step 2.1: Startup Logfire Token Resolution & firebase_admin Initialization from tenant_secrets
  - [ ] Step 2.2: Eradicate service-account.json Checks, allow_mock_tokens & mock_*_user_id Across Backend & .env
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/02_phase2_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 3: Frontend `MockLoginPanel` & `MOCK_*_USER_ID` Eradication and Authentic Email/Password Login Parity
**Plan:** @[docs/epic/tasks_EPIC_164/03_phase3_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/03_phase3_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]`
  - [ ] Step 3.1: Eradicate MockLoginPanel, allowMockTokens & mock*UserId from LoginScreen, Env & client_app_v2/.env
  - [ ] Step 3.2: Eradicate debugMockLogin & debugSignInWithMockToken and Delegate MFA Enforcement in signInWithEmailAndPassword to Backend
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Phase 4: Comprehensive Unit, Integration, Seed & E2E Verification Gate
**Plan:** @[docs/epic/tasks_EPIC_164/04_phase4_plan.md]
- [x] **[OK] Create Plan:** @[docs/epic/tasks_EPIC_164/04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]`
  - [ ] Step 4.1: Backend Unit Test Suite Verification & ISTQB Boundary Coverage
  - [ ] Step 4.2: Frontend Unit & Widget Test Suite Verification
  - [ ] Step 4.3: Local Secret Seeding, Full-Stack Audit Loops & Live E2E Verification
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/04_phase4_plan.md] @[docs/epic/EPIC_164_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend & Frontend Full-Stack Integration Gate**

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide verification that `@[service-account.json]`, `allow_mock_tokens`, `mock_*_user_id`, `MockLoginPanel`, `debugMockLogin`, and `debugSignInWithMockToken` are completely removed.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_164_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[backend_v2/core/telemetry.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [ ] @[backend_v2/logging_config.py]
  - [ ] @[backend_v2/main.py]
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
| REQ-164-004 | Add `resolve_startup_logfire_token` in `telemetry.py` and `initialize_firebase_admin_from_secrets` in `token_service.py`, and wire both into `main.py` and `worker.py` startup | Phase 2, Step 2.1 | [ ] Pending |
| REQ-164-005 | Remove `service-account.json` checks, `allow_mock_tokens`, and `mock_*_user_id` from `settings.py`, `logging_config.py`, `token_service.py`, and `run_e2e_variance_test.py`, sanitize `.env`, and delete `service-account.json` | Phase 2, Step 2.2 | [ ] Pending |
| REQ-164-006 | Delete `MockLoginPanel`, `allowMockTokens`, `_requireMockUserId`, and `mock*UserId` from `login_screen.dart`, `env.dart`, and `client_app_v2/.env` | Phase 3, Step 3.1 | [ ] Pending |
| REQ-164-007 | Delete `_activeDebugUserId`, `debugMockLogin`, and `debugSignInWithMockToken`, and refactor `AuthRepository.signInWithEmailAndPassword` to delegate MFA enforcement to backend `exchangeToken(idToken)` | Phase 3, Step 3.2 | [ ] Pending |
| REQ-164-008 | Verify and expand ISTQB positive, negative, and boundary unit tests across all 8 backend unit test suites | Phase 4, Step 4.1 | [ ] Pending |
| REQ-164-009 | Verify and expand unit and widget tests across all 7 Flutter test suites | Phase 4, Step 4.2 | [ ] Pending |
| REQ-164-010 | Execute `run_seed.py local --dry-run`, `run_seed.py local`, global backend and Flutter audit loops, and live E2E verification | Phase 4, Step 4.3 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed Phase 1 (`/tier2-execute --full-auto`) of `@[docs/epic/tasks_EPIC_164/01_phase1_plan.md]` across 3 atomic commits:
  - **Step 1.1 (`cd25ecd0e`)**: Added `SecretScope.TELEMETRY = "telemetry"` to `@[backend_v2/models/enums.py#L1395-L1400]` and `SecretScope.telemetry('telemetry')` to `@[client_app_v2/lib/core/models/enums.dart#L711-L724]`, updated `_ByokSecretsCard` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1574]` to filter `SecretScope.telemetry` exclusively to `UserRole.root` on `"org_0195f3a0000070008000000000000001"`, and verified cross-language enum and widget tests (`@[backend_v2/tests/unit/test_enum_parity.py]`, `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`).
  - **Step 1.2 (`028ffc61b`)**: Enforced `UserRole.ROOT` and `"org_0195f3a0000070008000000000000001"` RBAC isolation for `SecretScope.TELEMETRY` (`_validate_telemetry_scope_rbac`, `_validate_target_identifier` against `frozenset({"logfire", "logfire_read"})`) and added `resolve_telemetry_secret` in `@[backend_v2/services/auth/secret_service.py#L841-L925]`, verified by positive, negative, and boundary unit tests in `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`.
  - **Step 1.3**: Registered `"tenant_secrets"` in `CANONICAL_SEED_TABLES` (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`) and `InMemoryEntityAdapter.verify_seed_table_counts` (`@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1290]`), created `@[.env.secrets.example]` and git-ignored `@[.env.secrets.local]` (registered in `@[.gitignore#L124-L128]`), implemented `LocalSeedSecretsSettings`, `_seed_local_secrets`, and `_provision_root_firebase_user` in `@[backend_v2/seed/run_seed.py]`, verified unit tests in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` and `@[backend_v2/tests/unit/seed/test_run_seed.py]`, and executed live `uv run python backend_v2/seed/run_seed.py local` to seed all 6 Root System Organization secrets into PostgreSQL 19 `tenant_secrets` and provision/synchronize `usr_0195f3a00000700a83fd6b3d77c748f4` (`root@example.com`, `email_verified=True`) in Firebase Authentication (`cognitive-quorum`).

## Learned
- Returning `list[TenantSecretCreateDTO]` directly from `LocalSeedSecretsSettings.iter_secret_entries()` in `@[backend_v2/seed/run_seed.py]` satisfies `QGR023` (`ban_anonymous_state_tuples`) with 100% typed Pydantic V2 DTO transit.
- Initializing Firebase Authentication (`identityPlatform:initializeAuth` and enabling `signIn.email`) on GCP project `cognitive-quorum` resolved `ConfigurationNotFoundError` and allowed `run_seed.py local` to idempotently create and update `usr_0195f3a00000700a83fd6b3d77c748f4` in live Firebase Authentication and PostgreSQL 19 `users`.

## Remaining
- Run `/tier8-audit-plan @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]` to audit Phase 1 before proceeding to Phase 2 (`@[docs/epic/tasks_EPIC_164/02_phase2_plan.md]`).

## Resume Command
```powershell
/tier8-audit-plan @[docs/epic/tasks_EPIC_164/01_phase1_plan.md] @[docs/epic/EPIC_164_tracker.md]
```

