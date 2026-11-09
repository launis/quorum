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

# EPIC 164 Audit Report: Unified Local Secret Seeding, ROOT-Scoped Telemetry & Authentic Email/Password IAM Parity

## 1. Executive Summary & Audit Verdict

- **Target Epic**: `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`
- **Audit Tier**: Tier 0 (`tier0-research-epic`) — Principal Enterprise Architect & System Red Team
- **Boundary Audit Status**: `PASSED` (`0` violations via `scripts/audit_markdown_boundaries.py`)
- **Touched-Scope Technical Debt Audit**: `PASSED` (`0` findings across 10 Python target modules and 196 1-hop callers via `scripts/audit_technical_debt.py --include-one-hop`)
- **Flutter Theme Sovereignty Audit**: `PASSED` (`0` findings across 197 Dart files via `scripts/audit_flutter_theme_sovereignty.py`)
- **Surgical Epic Hardening Applied**:
  1. **Canonical Knowledge Item Registry Alignment**: Removed three non-existent Knowledge Item references (`ki_opentelemetry_logfire_observability.md`, `ki_seed_vault_verification_and_sanitization.md`, and `ki_shared_storage_driver_architecture.md`) from `<required_context_rules>` so 100% of referenced Knowledge Items resolve against `CANONICAL_KI_ARTIFACTS`.
  2. **Explicit `InMemoryEntityAdapter.verify_seed_table_counts` Parity**: Clarified Phase 1 Mandate 3 so `"tenant_secrets": len(self._store.seed_tables["tenant_secrets"])` is explicitly added in `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` alongside `"tenant_secrets"` in `CANONICAL_SEED_TABLES` (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`).
  3. **Exact Call-Site Bounds in `@[scripts/run_e2e_variance_test.py]`**: Expanded Phase 2 Mandate 4 to explicitly bind the three functions referencing `settings.mock_admin_user_id` (`trigger_execution` at `@[scripts/run_e2e_variance_test.py#L940-L1054]`, `poll_execution_completion` at `@[scripts/run_e2e_variance_test.py#L940-L1054]`, and `run_variance_test` at `@[scripts/run_e2e_variance_test.py#L940-L1054]`).

---

## 2. Panel of Architects & Modernity Gate Invariants Audit

| Domain Persona | Evaluation Scope | Verdict & Architectural Assessment |
| :--- | :--- | :--- |
| **Security & Multi-Tenant IAM Architect** | `SecretScope.TELEMETRY`, `SecretService`, `TokenService`, `MockLoginPanel` eradication, `SERVICE_AUTH_SECRET` headless CLI auth | **APPROVED**: `SecretScope.TELEMETRY` is strictly locked to `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"`, raising `AuthorizationError(ErrorCodes.PERMISSION_DENIED)` with RFC 7807 `logger.error` dual-reporting on any non-`ROOT` or tenant-scoped attempt. Deleting `MockLoginPanel`, `allow_mock_tokens`, and `MOCK_*_USER_ID` enforces `single_pipeline_invariant_mandate` so interactive logins execute exclusively via Firebase Authentication + `POST /api/v2/iam/auth/exchange`, while headless CLI scripts (`@[scripts/run_e2e_variance_test.py]`) authenticate exclusively via constant-time `secrets.compare_digest` verification of `SERVICE_AUTH_SECRET`. |
| **PostgreSQL 19 Zero-ORM & Seed Vault Architect** | `CANONICAL_SEED_TABLES`, `run_seed.py`, `.env.secrets.local`, `LocalSeedSecretsSettings` | **APPROVED**: Adding `"tenant_secrets"` to `CANONICAL_SEED_TABLES` in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` ensures `reset_seed_tables_rows` and `verify_seed_table_counts_rows` in `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L220-L260]` include `tenant_secrets` (11 canonical seed tables). `backend_v2/seed/seed_data.json` remains 100% free of credentials (`credential_hardcoding_ban`), while git-ignored `.env.secrets.local` hydrates AES-256-GCM encrypted rows into `tenant_secrets` via `SecretService.upsert_tenant_secret`. |
| **Observability & Runtime Lifecycle Architect** | `telemetry.py`, `main.py`, `worker.py`, `initialize_firebase_admin_from_secrets` | **APPROVED**: Both FastAPI (`@[backend_v2/main.py#L178-L242]`) and the Arq worker daemon (`@[backend_v2/worker.py#L49-L108]`) resolve the Logfire write token at startup from `tenant_secrets` (`SecretScope.TELEMETRY`, `target_identifier="logfire"`) via `resolve_startup_logfire_token` after `_validate_database_preflight`, and initialize `firebase_admin` in-memory via `credentials.Certificate(sa_dict)` decrypted from the Root System Organization `vertex_ai` secret, eliminating `@[service-account.json]` on disk. |
| **Flutter Desktop & Riverpod 3.0 Architect** | `enums.dart`, `organization_iam_settings_view.dart`, `login_screen.dart`, `env.dart`, `auth_controller.dart`, `auth_repository.dart` | **APPROVED**: `SecretScope.telemetry` is added in `@[client_app_v2/lib/core/models/enums.dart#L711-L722]` for 1:1 parity with Python `SecretScope.TELEMETRY` (`test_enum_parity.py`). In `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]`, `signInWithEmailAndPassword` delegates MFA policy evaluation to `exchangeToken(idToken)` (`POST /api/v2/iam/auth/exchange`) so `REQUIRE_MFA=false` permits single-factor Email + Password login on Windows Desktop while `REQUIRE_MFA=true` returns `MFA_REQUIRED` and triggers `_prepareEnrollmentForUser`. |

---

## 3. Five-Axis System 2 Deconstruction & 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L1395-L1399]`, `@[client_app_v2/lib/core/models/enums.dart#L711-L722]` & `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]` | Storing telemetry credentials in plaintext `.env` without a typed `SecretScope` variant. | Add `TELEMETRY = "telemetry"` to Python `SecretScope`, add `telemetry('telemetry')` to Dart `SecretScope`, and expose `SecretScope.telemetry` in `_ByokSecretsCard` exclusively to `UserRole.root` on `"org_0195f3a0000070008000000000000001"`. | No separate database table for telemetry secrets; reuse `tenant_secrets` with `SecretScope.TELEMETRY`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |
| `@[backend_v2/services/auth/secret_service.py#L108-L1009]` | Allowing non-`ROOT` roles or tenant organizations to read/write `SecretScope.TELEMETRY`. | Enforce `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` on `SecretScope.TELEMETRY` and add `resolve_telemetry_secret`. | Reuse existing AES-256-GCM envelope encryption and `ResolvedCredentialDTO` in `SecretService`. | `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict` |
| `@[backend_v2/seed/run_seed.py#L257-L273]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` & `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` | Wiping `tenant_secrets` without re-seeding local credentials or leaving `ROOT` unprovisioned in Firebase Auth. | Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` and `InMemoryEntityAdapter.verify_seed_table_counts`, hydrate `.env.secrets.local` via `LocalSeedSecretsSettings` into `tenant_secrets`, and provision/sync the `ROOT` user (`SECRET_ROOT_USER_EMAIL` + `SECRET_ROOT_USER_PASSWORD`) in Firebase Auth during `run_seed.py`. | Provision only the `ROOT` user in `run_seed.py`; all other users are provisioned via UI Onboarding (`UserService.create_user`). | `uv run python scripts/backend_audit_loop.py backend_v2/seed/run_seed.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict` |
| `@[backend_v2/core/telemetry.py#L300-L414]`, `@[backend_v2/main.py#L178-L242]`, `@[backend_v2/worker.py#L49-L108]` & `@[backend_v2/services/auth/token_service.py#L41-L580]` | Reading `LOGFIRE_TOKEN` from `.env`, relying on `service-account.json` on disk, and leaving `firebase_admin` uninitialized. | Resolve `logfire` token via `resolve_startup_logfire_token` and initialize `firebase_admin` via `initialize_firebase_admin_from_secrets` using the decrypted `vertex_ai` Service Account JSON from `tenant_secrets`. | Single startup initialization in `main.py` and `worker.py` without background polling loops. | `uv run python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/services/auth/token_service.py --test --ast-strict` |
| `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `@[client_app_v2/lib/core/environment/env.dart]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]` & `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` | Rendering `MockLoginPanel` in development, reading `MOCK_*_USER_ID` from `.env`, and blocking Desktop Email/Password login via client-side `getEnrolledFactors()` when `REQUIRE_MFA=false`. | Delete `MockLoginPanel`, `debugMockLogin`, `debugSignInWithMockToken`, and `MOCK_*_USER_ID`; delegate MFA enforcement in `signInWithEmailAndPassword` to backend `exchangeToken(idToken)` response (`MFA_REQUIRED`). | Zero client-side `REQUIRE_MFA` environment duplication; backend `POST /api/v2/iam/auth/exchange` is the sole MFA policy authority. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/auth/presentation/login_screen_test.dart --build` |

---

## 4. Falsification & Red-Teaming Verification Matrix

1. **Fail-Fast Boundary & DLP Verification (`QGR033`)**:
   - All decrypted credentials returned by `SecretService.resolve_telemetry_secret` and `SecretService.resolve_llm_key` are wrapped in `ResolvedCredentialDTO` (`api_key: SecretStr`). Unwrapping via `.get_secret_value()` occurs strictly at the point of consumption (`logfire.configure(token=...)` and `json.loads(cred.api_key.get_secret_value())` for `credentials.Certificate`), never inside `logger.*`, `logfire.*`, or `print(...)` calls (`QGR033`).
2. **Atomic Data & Test Migration Verification**:
   - Updating `CANONICAL_SEED_TABLES` from 10 to 11 tables in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` is paired with updating `InMemoryEntityAdapter.verify_seed_table_counts` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` and `assert len(CANONICAL_SEED_TABLES) == 11` in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`.
3. **Sunset & Destructive Operation Parity (`SUNSET_PHASE_PARITY_GATE`)**:
   - Every symbol and file in the Epic's `Deprecations & Sunset List` (`@[service-account.json]`, `allow_mock_tokens`, `mock_admin_user_id`, `mock_root_user_id`, `mock_analyst_user_id`, `MockLoginPanel`, `allowMockTokens`, `_requireMockUserId`, `mockAdminUserId`, `mockRootUserId`, `mockAnalystUserId`, `mockMemberUserId`, `mockViewerUserId`, `debugMockLogin`, `_activeDebugUserId`, `debugSignInWithMockToken`) has an explicit deletion mandate in Phases 2 and 3 and companion test updates in Phase 4.
4. **Dry-Run Side-Effect Isolation in `run_seed.py`**:
   - When `uv run python backend_v2/seed/run_seed.py local --dry-run` is executed, `LocalSeedSecretsSettings` validates the structure of `.env.secrets.local` in-memory without writing to PostgreSQL 19 `tenant_secrets` or making network calls to Firebase Authentication.
