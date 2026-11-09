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

# EPIC 164: Unified Local Secret Seeding, ROOT-Scoped Telemetry & Authentic Email/Password IAM Parity

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> Modern multi-tenant AI SaaS platforms enforce three architectural invariants across local development and cloud production:
> 1. **Zero-Drift Secret Hydration & Envelope Encryption Parity**: Maintaining divergent credential resolution paths between local developer workstations (plaintext `.env` keys or root `service-account.json` files) and cloud production (database-backed AES-256-GCM envelope encryption in `tenant_secrets`) introduces configuration drift and masks serialization regressions. Ingesting git-ignored local bootstrap secrets (`.env.secrets.local`) through the deterministic database seed pipeline (`run_seed.py`) into PostgreSQL 19 `tenant_secrets` guarantees that 100% of runtime LLM, MCP, Firebase Admin, and Telemetry credential resolutions execute through `SecretService` in both local and cloud environments.
> 2. **Principle of Least Privilege for Platform Observability (`SecretScope.TELEMETRY`)**: In multi-tenant SaaS architectures, OpenTelemetry / Logfire ingestion tokens capture system-wide traces and span metrics. Isolating telemetry tokens under a dedicated `SecretScope.TELEMETRY` enumeration bound exclusively to the Root System Organization (`"org_0195f3a0000070008000000000000001"`) and `UserRole.ROOT` prevents tenant administrators (`UserRole.ADMIN`) from reading or mutating platform observability pipelines.
> 3. **Eradication of UI Authentication Bypass Shortcuts (`MockLoginPanel`) & IdP-Backed Seed Provisioning**: Development-only login bypass panels (`MockLoginPanel`, `allowMockTokens`, `MOCK_*_USER_ID`) create a bifurcated authentication pipeline where UI state transitions, Firebase ID token verification, and backend `TokenService.exchange_firebase_token` paths remain untested during daily development. Provisioning the `ROOT` administrator account into Firebase Authentication during `run_seed.py` from `.env.secrets.local` and initializing `firebase_admin` from the encrypted GCP Service Account stored in `tenant_secrets` enables 100% authentic Email + Password login across local Windows Desktop and cloud deployments while restricting headless CLI token exchange strictly to cryptographic `SERVICE_AUTH_SECRET` verification.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### 1.1 Problem Statement
While runtime LLM (`SecretScope.LLM_PROVIDER`) and MCP (`SecretScope.MCP_GATEWAY`) credential resolution operate from the PostgreSQL 19 `tenant_secrets` table via `@[backend_v2/services/auth/secret_service.py#L108-L1009]`, four structural gaps prevent 1:1 parity between local development and cloud production:

1. **Full Database Reset (`run_seed.py`) Wipes `tenant_secrets` Without Re-Seeding Local Secrets**:
   - `"tenant_secrets"` is absent from `CANONICAL_SEED_TABLES` in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, and `@[backend_v2/seed/run_seed.py#L257-L273]` does not load local secrets into PostgreSQL 19 `tenant_secrets`. Executing a clean database reset wipes all stored provider keys unless manually re-entered through the UI.
2. **Lingering `service-account.json` File & Synchronous Settings File Checks**:
   - The workspace root still contains `@[service-account.json]` (`project_id: "cognitive-quorum"`), and `@[backend_v2/settings.py#L1172-L1211]` plus `@[backend_v2/settings.py#L1320-L1351]` retain synchronous file-existence checks for `service-account.json`.
   - Furthermore, `@[backend_v2/services/auth/token_service.py#L89-L97]` assigns `self.firebase_auth = self._firebase_module` without initializing `firebase_admin.initialize_app(...)` from the encrypted GCP Service Account stored in `tenant_secrets`.
3. **Plaintext Logfire Telemetry Tokens in `.env` Instead of `ROOT`-Scoped `tenant_secrets`**:
   - `@[.env#L4-L5]` stores `LOGFIRE_TOKEN` and `LOGFIRE_Read_Token`, and `@[backend_v2/core/telemetry.py#L300-L414]` reads `settings.logfire_token` from `.env` rather than resolving a `UserRole.ROOT`-restricted `SecretScope.TELEMETRY` secret from the Root System Organization (`"org_0195f3a0000070008000000000000001"`).
4. **Legacy Mock Login Shortcuts (`MockLoginPanel` & `MOCK_*_USER_ID`) Bypassing Real Email/Password Authentication**:
   - `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L158-L161]` and `#L367-L474` render `MockLoginPanel` in development mode, backed by `MOCK_*_USER_ID` variables in `@[.env#L14-L17]`, `@[client_app_v2/.env#L3-L7]`, `@[client_app_v2/lib/core/environment/env.dart#L29-L79]`, and `@[backend_v2/settings.py#L1367-L1387]`.
   - In `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L128-L141]`, `signInWithEmailAndPassword` unconditionally invokes `firebaseUser.multiFactor.getEnrolledFactors()` on the client before calling `exchangeToken(idToken)`, blocking single-factor Email + Password login on Windows Desktop even when backend `REQUIRE_MFA=false`.

### 1.2 Quantitative Scope Summary

| Metric / Category | Count | Details |
| :--- | :--- | :--- |
| **New Files (`[NEW]`)** | **2** | `[NEW] @[.env.secrets.example]`, `[NEW] @[.env.secrets.local]` (git-ignored) |
| **Deleted Files (`[DELETE]`)** | **1** | `[DELETE] @[service-account.json]` |
| **Backend Production Files (`[MODIFY]`)** | **12** | `@[backend_v2/models/enums.py]`, `@[backend_v2/services/auth/secret_service.py]`, `@[backend_v2/services/auth/token_service.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `@[backend_v2/seed/run_seed.py]`, `@[backend_v2/core/telemetry.py]`, `@[backend_v2/main.py]`, `@[backend_v2/worker.py]`, `@[backend_v2/settings.py]`, `@[backend_v2/logging_config.py]`, `@[.env]`, `@[.gitignore]` |
| **Frontend Production Files (`[MODIFY]`)** | **7** | `@[client_app_v2/lib/core/models/enums.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `@[client_app_v2/lib/core/environment/env.dart]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart]`, `@[client_app_v2/.env]` |
| **Scripts, Fakes & Test Files (`[MODIFY]`)** | **17** | `@[scripts/run_e2e_variance_test.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py]`, `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`, `@[backend_v2/tests/unit/test_enum_parity.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/seed/test_run_seed.py]`, `@[backend_v2/tests/unit/core/test_telemetry.py]`, `@[backend_v2/tests/unit/test_settings.py]`, `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`, `@[backend_v2/tests/unit/test_token_service.py]`, `@[client_app_v2/test/core/models/enums_test.dart]`, `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`, `@[client_app_v2/test/unit/core/environment/env_test.dart]`, `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`, `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`, `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]` |

---

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)

| Symbol / File / Field | Current Location | Target Destination / Disposition |
| :--- | :--- | :--- |
| `@[service-account.json]` | `@[service-account.json]` | `INTENTIONALLY DROPPED` — Migrated to `SECRET_VERTEX_AI_SA_JSON` in `.env.secrets.local` and seeded into PostgreSQL 19 `tenant_secrets`. |
| `allow_mock_tokens` | `@[backend_v2/settings.py#L1367-L1387]` | `INTENTIONALLY DROPPED` — Bifurcated mock token mode eradicated under `single_pipeline_invariant_mandate`. |
| `mock_admin_user_id` | `@[backend_v2/settings.py#L68-L1492]` | `INTENTIONALLY DROPPED` — Mock user IDs eradicated; headless CLI scripts use `"usr_0195f3a00000700a83fd6b3d77c748f4"` with `SERVICE_AUTH_SECRET`. |
| `mock_root_user_id` | `@[backend_v2/settings.py#L68-L1492]` | `INTENTIONALLY DROPPED` — Replaced by canonical Root user ID `"usr_0195f3a00000700a83fd6b3d77c748f4"`. |
| `mock_analyst_user_id` | `@[backend_v2/settings.py#L68-L1492]` | `INTENTIONALLY DROPPED` — Mock user IDs eradicated. |
| `MockLoginPanel` | `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L367-L474]` | `INTENTIONALLY DROPPED` — UI login shortcut panel removed; all interactive logins use Email + Password on `LoginScreen`. |
| `allowMockTokens` | `@[client_app_v2/lib/core/environment/env.dart#L62-L65]` | `INTENTIONALLY DROPPED` — Mock token bypass flag removed from Flutter `Env`. |
| `_requireMockUserId` | `@[client_app_v2/lib/core/environment/env.dart#L45-L54]` | `INTENTIONALLY DROPPED` — Mock user ID validator removed from Flutter `Env`. |
| `mockAdminUserId` | `@[client_app_v2/lib/core/environment/env.dart#L68]` | `INTENTIONALLY DROPPED` — Removed from Flutter `Env` and `client_app_v2/.env`. |
| `mockRootUserId` | `@[client_app_v2/lib/core/environment/env.dart#L70]` | `INTENTIONALLY DROPPED` — Removed from Flutter `Env` and `client_app_v2/.env`. |
| `mockAnalystUserId` | `@[client_app_v2/lib/core/environment/env.dart#L72-L73]` | `INTENTIONALLY DROPPED` — Removed from Flutter `Env` and `client_app_v2/.env`. |
| `mockMemberUserId` | `@[client_app_v2/lib/core/environment/env.dart#L75-L76]` | `INTENTIONALLY DROPPED` — Removed from Flutter `Env` and `client_app_v2/.env`. |
| `mockViewerUserId` | `@[client_app_v2/lib/core/environment/env.dart#L78-L79]` | `INTENTIONALLY DROPPED` — Removed from Flutter `Env` and `client_app_v2/.env`. |
| `debugMockLogin` | `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L154-L170]` | `INTENTIONALLY DROPPED` — Debug mock login controller method eradicated. |
| `_activeDebugUserId` | `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L48]` | `INTENTIONALLY DROPPED` — Debug session refresh override field eradicated. |
| `debugSignInWithMockToken` | `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L291]` | `INTENTIONALLY DROPPED` — Debug mock token exchange repository method eradicated. |

### Retained SSOT Invariants (`What We Will RETAIN`)

- **Master Key Encryption Environment Variable (`SECRET_ENCRYPTION_KEY`)**: Retained in `@[.env]` as the KEK (Key Encryption Key) required to decrypt AES-256-GCM rows in PostgreSQL 19 `tenant_secrets`.
- **Headless CLI / E2E Shared Secret (`SERVICE_AUTH_SECRET` / `settings.service_auth_secret`)**: Retained in `@[backend_v2/settings.py#L68-L1492]` and `@[backend_v2/services/auth/token_service.py#L304-L339]` as the sole cryptographic authorization mechanism (`secrets.compare_digest`) for non-interactive CLI scripts (`@[scripts/run_e2e_variance_test.py]`).
- **Dual-Tier Secret Fallback (`Tenant BYOK -> Root System Organization`)**: Retained in `@[backend_v2/services/auth/secret_service.py#L108-L1009]` for `SecretScope.LLM_PROVIDER` and `SecretScope.MCP_GATEWAY`, while `SecretScope.TELEMETRY` is restricted exclusively to `"org_0195f3a0000070008000000000000001"` and `UserRole.ROOT`.
- **Static Seed Vault Purity (`backend_v2/seed/seed_data.json`)**: Retained 100% secret-free (`credential_hardcoding_ban`).

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/models/enums.py#L1395-L1399]`, `@[client_app_v2/lib/core/models/enums.dart#L711-L722]` & `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]` | Storing telemetry credentials in plaintext `.env` without a typed `SecretScope` variant. | Add `TELEMETRY = "telemetry"` to Python `SecretScope`, add `telemetry('telemetry')` to Dart `SecretScope`, and expose `SecretScope.telemetry` in `_ByokSecretsCard` exclusively to `UserRole.root` on `"org_0195f3a0000070008000000000000001"`. | No separate database table for telemetry secrets; reuse `tenant_secrets` with `SecretScope.TELEMETRY`. | `uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py backend_v2/tests/unit/test_enum_parity.py --test --ast-strict` |
| `@[backend_v2/services/auth/secret_service.py#L108-L1009]` | Allowing non-`ROOT` roles or tenant organizations to read/write `SecretScope.TELEMETRY`. | Enforce `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"` on `SecretScope.TELEMETRY` and add `resolve_telemetry_secret`. | Reuse existing AES-256-GCM envelope encryption and `ResolvedCredentialDTO` in `SecretService`. | `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/secret_service.py backend_v2/tests/unit/services/auth/test_secret_service.py --test --ast-strict` |
| `@[backend_v2/seed/run_seed.py#L257-L273]` & `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Wiping `tenant_secrets` without re-seeding local credentials or leaving `ROOT` unprovisioned in Firebase Auth. | Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES`, hydrate `.env.secrets.local` via `LocalSeedSecretsSettings` into `tenant_secrets`, and provision/sync the `ROOT` user (`SECRET_ROOT_USER_EMAIL` + `SECRET_ROOT_USER_PASSWORD`) in Firebase Auth during `run_seed.py`. | Provision only the `ROOT` user in `run_seed.py`; all other users are provisioned via UI Onboarding (`UserService.create_user`). | `uv run python scripts/backend_audit_loop.py backend_v2/seed/run_seed.py backend_v2/tests/unit/seed/test_run_seed.py --test --ast-strict` |
| `@[backend_v2/core/telemetry.py#L300-L414]`, `@[backend_v2/main.py#L178-L242]`, `@[backend_v2/worker.py#L49-L108]` & `@[backend_v2/services/auth/token_service.py#L41-L580]` | Reading `LOGFIRE_TOKEN` from `.env`, relying on `service-account.json` on disk, and leaving `firebase_admin` uninitialized. | Resolve `logfire` token via `resolve_startup_logfire_token` and initialize `firebase_admin` via `initialize_firebase_admin_from_secrets` using the decrypted `vertex_ai` Service Account JSON from `tenant_secrets`. | Single startup initialization in `main.py` and `worker.py` without background polling loops. | `uv run python scripts/backend_audit_loop.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/services/auth/token_service.py --test --ast-strict` |
| `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `@[client_app_v2/lib/core/environment/env.dart]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]` & `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` | Rendering `MockLoginPanel` in development, reading `MOCK_*_USER_ID` from `.env`, and blocking Desktop Email/Password login via client-side `getEnrolledFactors()` when `REQUIRE_MFA=false`. | Delete `MockLoginPanel`, `debugMockLogin`, `debugSignInWithMockToken`, and `MOCK_*_USER_ID`; delegate MFA enforcement in `signInWithEmailAndPassword` to backend `exchangeToken(idToken)` response (`MFA_REQUIRED`). | Zero client-side `REQUIRE_MFA` environment duplication; backend `POST /api/v2/iam/auth/exchange` is the sole MFA policy authority. | `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/auth/presentation/login_screen_test.dart --build` |

### Producer-Consumer Integration Check

- **Producer 1 (`LocalSeedSecretsSettings`, `_seed_local_secrets`, and `_provision_root_firebase_user` in `@[backend_v2/seed/run_seed.py#L257-L273]`)**: Reads git-ignored `.env.secrets.local`, encrypts and upserts Root System Organization (`"org_0195f3a0000070008000000000000001"`) secrets (`ai_studio`, `vertex_ai`, `openai`, `anthropic`, `sys_0195f3a00000700080008172bda70c86`, `logfire`, `logfire_read`) into PostgreSQL 19 `tenant_secrets`, provisions/updates the `ROOT` user (`SECRET_ROOT_USER_EMAIL`, `SECRET_ROOT_USER_PASSWORD`) in Firebase Authentication, and binds `firebase_uid` onto `usr_0195f3a00000700a83fd6b3d77c748f4` in PostgreSQL 19 `users`.
- **Consumer 1 (`SecretService`, `resolve_startup_logfire_token`, `initialize_firebase_admin_from_secrets`)**: Consumes encrypted rows from PostgreSQL 19 `tenant_secrets` to configure Logfire telemetry (`@[backend_v2/core/telemetry.py#L300-L414]`), initialize `firebase_admin` (`@[backend_v2/services/auth/token_service.py#L41-L580]`), and serve LLM/MCP credentials at runtime.
- **Producer 2 (`LoginScreen` & `AuthRepository.signInWithEmailAndPassword` in `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]`)**: Authenticates the user against Firebase Authentication with Email + Password, obtains a Firebase ID Token (`firebaseUser.getIdToken()`), and sends `TokenExchangeRequestDTO(firebase_token=idToken)` to `POST /api/v2/iam/auth/exchange`.
- **Consumer 2 (`TokenService.exchange_firebase_token` in `@[backend_v2/services/auth/token_service.py#L99-L166]`)**: Verifies the Firebase ID Token via the `tenant_secrets`-initialized `firebase_admin` app, evaluates `settings.require_mfa` (`REQUIRE_MFA=false` locally, `REQUIRE_MFA=true` in cloud), and returns a signed 15-minute `TokenExchangeResponseDTO` (`Quorum Local JWT`).

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Backend `SecretScope.TELEMETRY`, `.env.secrets.local` Seeding Pipeline & Root Firebase User Provisioning

- **Pre-Flight Technical Debt Audit Verification**:
  - Verified clean (`0` findings across 12 target files and 195 1-hop callers via `scripts/audit_technical_debt.py`).
- **Target Files**:
  - `[MODIFY]` `@[backend_v2/models/enums.py#L1395-L1399]`
  - `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`
  - `[MODIFY]` `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`
  - `[MODIFY]` `@[backend_v2/services/auth/secret_service.py#L108-L1009]`
  - `[MODIFY]` `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`
  - `[MODIFY]` `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]`
  - `[MODIFY]` `@[backend_v2/seed/run_seed.py#L257-L273]`
  - `[NEW]` `@[.env.secrets.example]`
  - `[NEW]` `@[.env.secrets.local]`
  - `[MODIFY]` `@[.gitignore]`
- **Implementation Mandates**:
  1. Add `TELEMETRY = "telemetry"` to `SecretScope` in `@[backend_v2/models/enums.py#L1395-L1399]`, add `telemetry('telemetry')` to `SecretScope` in `@[client_app_v2/lib/core/models/enums.dart#L711-L722]`, and filter `SecretScope.values` in `_ByokSecretsCard` (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L1315-L1525]`) so `SecretScope.telemetry` is selectable only when `currentUser?.role == UserRole.root && orgId == 'org_0195f3a0000070008000000000000001'`.
  2. Update `SecretService` in `@[backend_v2/services/auth/secret_service.py#L108-L1009]` so any operation where `scope == SecretScope.TELEMETRY` requires `initiator.role == UserRole.ROOT` and `organization_id == "org_0195f3a0000070008000000000000001"`, logging `logger.error` and raising `AuthorizationError(ErrorCodes.PERMISSION_DENIED)` otherwise, and add `async def resolve_telemetry_secret(self, target_identifier: str = "logfire") -> ResolvedCredentialDTO`.
  3. Add `"tenant_secrets"` to `CANONICAL_SEED_TABLES` in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` and add `"tenant_secrets": len(self._store.seed_tables["tenant_secrets"])` to `InMemoryEntityAdapter.verify_seed_table_counts` in `@[backend_v2/tests/fakes/in_memory_uow.py#L1231-L1289]` so `reset_seed_tables()` and `verify_seed_table_counts()` include `tenant_secrets`.
  4. Create `[NEW] @[.env.secrets.example]` (committed template) and `[NEW] @[.env.secrets.local]` (git-ignored via `@[.gitignore]`) with strict fields: `SECRET_AI_STUDIO_API_KEY`, `SECRET_VERTEX_AI_SA_JSON`, `SECRET_OPENAI_API_KEY`, `SECRET_ANTHROPIC_API_KEY`, `SECRET_TAVILY_API_KEY`, `SECRET_LOGFIRE_TOKEN`, `SECRET_LOGFIRE_READ_TOKEN`, `SECRET_ROOT_USER_EMAIL`, and `SECRET_ROOT_USER_PASSWORD`.
  5. Define `LocalSeedSecretsSettings(BaseSettings)` (`extra="forbid"`) in `@[backend_v2/seed/run_seed.py#L257-L273]` and implement `_seed_local_secrets` and `_provision_root_firebase_user` so `uv run python backend_v2/seed/run_seed.py local` seeds all configured Root System Organization (`"org_0195f3a0000070008000000000000001"`) secrets into PostgreSQL 19 `tenant_secrets` and provisions/synchronizes ONLY the `ROOT` user (`"usr_0195f3a00000700a83fd6b3d77c748f4"`) in Firebase Authentication (`email_verified=True`) and PostgreSQL 19 `users`.

### Phase 2: Database-Driven Telemetry & Firebase Admin Startup Initialization, `.env` Sanitation & `service-account.json` Deletion

- **Target Files**:
  - `[MODIFY]` `@[backend_v2/core/telemetry.py#L300-L414]`
  - `[MODIFY]` `@[backend_v2/services/auth/token_service.py#L41-L580]`
  - `[MODIFY]` `@[backend_v2/main.py#L178-L242]`
  - `[MODIFY]` `@[backend_v2/worker.py#L49-L108]`
  - `[MODIFY]` `@[backend_v2/settings.py#L68-L1492]`
  - `[MODIFY]` `@[backend_v2/logging_config.py#L446-L479]`
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py]`
  - `[MODIFY]` `@[.env]`
  - `[DELETE]` `@[service-account.json]`
- **Implementation Mandates**:
  1. Add `async def resolve_startup_logfire_token(settings: Settings, secret_service: SecretService) -> str | None` in `@[backend_v2/core/telemetry.py#L300-L414]` and pass `logfire_token: str | None = None` into `configure_telemetry(settings, logfire_token=...)` from `@[backend_v2/main.py#L178-L242]` and `@[backend_v2/worker.py#L49-L108]`.
  2. Add `async def initialize_firebase_admin_from_secrets(secret_service: SecretService, settings: Settings) -> None` in `@[backend_v2/services/auth/token_service.py#L41-L580]` to initialize `firebase_admin.initialize_app(credentials.Certificate(sa_dict))` from the Root System Organization (`"org_0195f3a0000070008000000000000001"`) `vertex_ai` secret in PostgreSQL 19 `tenant_secrets` during FastAPI startup (`@[backend_v2/main.py#L178-L242]`) when `settings.use_firebase_auth` is `True`.
  3. Remove synchronous `service-account.json` file checks (`#L1172-L1211`, `#L1320-L1351`), `allow_mock_tokens` (`#L1367-L1387`), `mock_admin_user_id` (`#L1410-L1417`), `mock_root_user_id` (`#L1418-L1425`), and `mock_analyst_user_id` (`#L1426-L1433`) from `@[backend_v2/settings.py#L68-L1492]`, and remove `allow_mock_tokens` logging from `@[backend_v2/logging_config.py#L446-L479]`.
  4. Update `TokenService._resolve_headless_cli_user` (`@[backend_v2/services/auth/token_service.py#L304-L339]`) to require `secret_matches` (`SERVICE_AUTH_SECRET` verified via `secrets.compare_digest`) unconditionally without `allow_mock_tokens`, and update `trigger_execution` (`@[scripts/run_e2e_variance_test.py#L940-L1054]`), `poll_execution_completion` (`@[scripts/run_e2e_variance_test.py#L940-L1054]`), and `run_variance_test` (`@[scripts/run_e2e_variance_test.py#L940-L1054]`) in `@[scripts/run_e2e_variance_test.py]` to authenticate using `"usr_0195f3a00000700a83fd6b3d77c748f4"` and `settings.service_auth_secret`.
  5. Remove `LOGFIRE_TOKEN`, `LOGFIRE_Read_Token`, `MOCK_ADMIN_USER_ID`, `MOCK_ROOT_USER_ID`, and `MOCK_ANALYST_USER_ID` from `@[.env]`, set `USE_FIREBASE_AUTH=true` and `REQUIRE_MFA=false` in `@[.env]`, and delete `[DELETE] @[service-account.json]`.

### Phase 3: Frontend `MockLoginPanel` & `MOCK_*_USER_ID` Eradication and Authentic Email/Password Login Parity

- **Target Files**:
  - `[MODIFY]` `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`
  - `[MODIFY]` `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`
  - `[MODIFY]` `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`
  - `[MODIFY]` `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]`
  - `[MODIFY]` `@[client_app_v2/.env]`
- **Implementation Mandates**:
  1. Delete `class MockLoginPanel` (`#L367-L474`) and remove `if (Env.allowMockTokens) ...[ AppSpacing.h24, const MockLoginPanel() ]` (`#L158-L161`) from `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`.
  2. Delete `_requireMockUserId`, `allowMockTokens`, `mockAdminUserId`, `mockRootUserId`, `mockAnalystUserId`, `mockMemberUserId`, and `mockViewerUserId` from `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`, and remove `MOCK_ADMIN_USER_ID`, `MOCK_ROOT_USER_ID`, `MOCK_ANALYST_USER_ID`, `MOCK_MEMBER_USER_ID`, and `MOCK_VIEWER_USER_ID` from `@[client_app_v2/.env]`.
  3. Delete `_activeDebugUserId`, `debugMockLogin`, and `debugUserId` parameters from `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`, and delete `debugSignInWithMockToken` and `debugTargetUserId` from `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L315]`.
  4. Refactor `AuthRepository.signInWithEmailAndPassword` in `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]` so that after `_firebaseAuth.signInWithEmailAndPassword(email: email, password: password)` succeeds, it obtains `final idToken = await firebaseUser.getIdToken()` and calls `final exchangeResult = await exchangeToken(idToken)` directly. If `exchangeResult` returns `Left(error)` with `error.errorCode == 'MFA_REQUIRED'`, invoke `await _prepareEnrollmentForUser(firebaseUser, fallbackEmail: email)` and return `Left(error)`.

### Phase 4: Comprehensive Unit, Integration, Seed & E2E Verification Gate

- **Target Files**:
  - `[MODIFY]` `@[backend_v2/tests/unit/services/auth/test_secret_service.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/seed/test_run_seed.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/core/test_telemetry.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/test_settings.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/llm/test_google_providers_separation.py]`
  - `[MODIFY]` `@[backend_v2/tests/unit/test_token_service.py]`
  - `[MODIFY]` `@[client_app_v2/test/core/models/enums_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/unit/core/environment/env_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`
  - `[MODIFY]` `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`
- **Implementation Mandates**:
  1. Add positive and negative ISTQB boundary tests across all 8 backend unit test suites covering `SecretScope.TELEMETRY` RBAC isolation, `.env.secrets.local` seeding, Firebase `ROOT` user provisioning, startup Logfire token resolution, startup `firebase_admin` initialization, and headless CLI `service_auth_secret` enforcement.
  2. Update all 7 Flutter test suites to remove obsolete `MockLoginPanel` / `debugMockLogin` / `mock*UserId` assertions and verify `SecretScope.telemetry` parity and `signInWithEmailAndPassword` token exchange behavior under both `200 OK` (`REQUIRE_MFA=false` or 2FA-verified token) and `403 MFA_REQUIRED` (`REQUIRE_MFA=true` triggering `_prepareEnrollmentForUser`).
  3. Execute `uv run python backend_v2/seed/run_seed.py local --dry-run` and `uv run python backend_v2/seed/run_seed.py local`, followed by global backend and Flutter audit loops.

---

## 4. Definition of Done (DoD) & Verification Plan

- **Definition of Done (DoD):**
  1. `SecretScope.TELEMETRY` (`"telemetry"`) is synchronized across Python (`@[backend_v2/models/enums.py#L1395-L1399]`) and Flutter (`@[client_app_v2/lib/core/models/enums.dart#L711-L722]`) and strictly restricted to `UserRole.ROOT` and `"org_0195f3a0000070008000000000000001"`.
  2. Running `uv run python backend_v2/seed/run_seed.py local` populates PostgreSQL 19 `tenant_secrets` from `.env.secrets.local` and provisions/synchronizes ONLY the `ROOT` user (`SECRET_ROOT_USER_EMAIL` + `SECRET_ROOT_USER_PASSWORD`) in Firebase Authentication (`cognitive-quorum`) and PostgreSQL 19 `users`.
  3. `@[service-account.json]` is deleted from the workspace root, `@[.env]` and `@[client_app_v2/.env]` contain zero `LOGFIRE_*` or `MOCK_*_USER_ID` variables, and `MockLoginPanel` is completely removed from `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`.
  4. Primary Email + Password login on `LoginScreen` works end-to-end against Firebase Authentication and `POST /api/v2/iam/auth/exchange` (`TokenService.exchange_firebase_token`) initialized from the encrypted GCP Service Account in PostgreSQL 19 `tenant_secrets`.
- **Automated Unit Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **AST Guardrails & Structural Tests:**
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md --fix`
  - `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --targets backend_v2/models/enums.py backend_v2/services/auth/secret_service.py backend_v2/services/auth/token_service.py backend_v2/seed/run_seed.py backend_v2/core/telemetry.py backend_v2/main.py backend_v2/worker.py backend_v2/settings.py backend_v2/logging_config.py --include-one-hop`
- **MANDATORY Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
