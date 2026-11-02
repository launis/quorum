<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
</required_context_rules>

# Tracker: EPIC 160 — B2B SaaS IAM, Token Exchange & Enterprise Hardening Architecture

**Epic:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]
**Task Directory:** @[docs/epic/tasks_EPIC_160/]

## Phase Execution Status

### Phase 1: Pre-Implementation Technical Debt Cleanups, Zero-ORM Identity Schema & `PrefixedUUID7` DTOs
**Plan:** @[docs/epic/tasks_EPIC_160/01_phase1_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/01_phase1_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 1.1: Obsolete Document Demolition & Touched-Scope Technical Debt Remediation
  - [x] Step 1.2: Taxonomies, ErrorCodes & Strict `PrefixedUUID7` Identity & Assignment Models
  - [x] Step 1.3: PostgreSQL 19 Zero-ORM Identity, Invitation, Task Assignment & Secrets Schema + Dual-Layer Tenant Isolation
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 2: Session Upgrade, Token Exchange Engine, Headless CLI Governance & Multi-Role Guard
**Plan:** @[docs/epic/tasks_EPIC_160/02_phase2_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/02_phase2_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]` (`f10dd15f6`)
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 2.1: `TokenService` Session Upgrade (`exchange_firebase_token`), Mandatory 2FA Enforcement & 0.1 ms RAM Verification
  - [x] Step 2.2: Token Exchange & Logout Router Endpoints, IAM Router SSOT Consolidation & Multi-Role Dependency Guard
  - [x] Step 2.3: Headless CLI, E2E Variance Runner (`run_e2e_variance_test.py`) & Background Worker Session Governance
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 3: Enterprise BYOK & Cloud Secrets Engine for LLM & MCP Services
**Plan:** @[docs/epic/tasks_EPIC_160/03_phase3_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/03_phase3_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]` (`792a2fe62`)
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 3.1: `SecretService` (Cloud Secret Manager & Envelope Encryption — Single-Pipeline Non-Nullable Resolution)
  - [x] Step 3.2: Request-Scoped Credential Injection in `LiteLLMProvider` & `GenericMCPClient`
  - [x] Step 3.3: Organization BYOK Management Endpoints & DLP AST Guardrail
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 4: Real-Time Dual-Key Redis Kill-Switch (`MGET`) & FinOps Rate Limiting
**Plan:** @[docs/epic/tasks_EPIC_160/04_phase4_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/04_phase4_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]` (`acb75b876`)
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 4.1: Fail-Closed Dual-Key Redis Kill-Switch (`RevocationCache`)
  - [x] Step 4.2: Per-Tenant Redis Sliding-Window Rate Limiter & FinOps Pre-Flight Gatekeeper
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 5: B2B Invitation Flow, Time-Bound Execution Assignments (`ExecutionAssignment`), 4-Tier RBAC Matrix, Self-Service Profile & GDPR Soft-Delete Webhook
**Plan:** @[docs/epic/tasks_EPIC_160/05_phase5_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/05_phase5_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]` (`4a17b7736`)
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 5.1: Cryptographic B2B Invitations & 1:1 Flat Identity Collision Guard
  - [x] Step 5.2: 4-Tier RBAC Governance (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`) & Self-Service Profile (`name`, `language`, `theme_mode`)
  - [x] Step 5.3: GDPR Soft-Delete Anonymization & Firebase Deletion Webhook
  - [x] Step 5.4: Time-Bound Execution Assignments (`ExecutionAssignmentService`), SafeLinks-Immune Activation & Combined JIT User Onboarding
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 6: Flutter Client `AuthInterceptor`, Silent Refresh, Cryptographic Logout Pipeline & Separated User/Organization Views
**Plan:** @[docs/epic/tasks_EPIC_160/06_phase6_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/06_phase6_plan.md]
- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]` (`21f866e09`)
  - [x] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [x] Step 6.1: Mandatory 2FA Enrollment/Challenge Flow, `AuthInterceptor`, Session Upgrade Handshake, 13-Minute Silent Refresh & 5-Step Logout Pipeline
  - [x] Step 6.2: Adaptive Navigation Logout Action, Separated User Profile View (`UserProfileSettingsView`), Organization IAM Studio UI (`OrganizationIamSettingsView`), Direct Task Assignment Builder in `NewExecutionView` & Task Assignment Portal (`TaskAssignmentPortalView`)
- [x] **[OK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [x] **[OK] Backend & Frontend Full-Stack Integration Gate**

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [x] **[OK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_160_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` across existing and `[NEW]` backend targets.
  - [x] @[backend_v2/settings.py]
  - [x] @[backend_v2/models/enums.py]
  - [x] @[backend_v2/exceptions.py]
  - [x] @[backend_v2/models/auth.py]
  - [x] @[backend_v2/models/domain/execution.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/__init__.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]
  - [x] @[backend_v2/database/postgres/uow.py]
  - [x] @[backend_v2/database/repositories/identity.py]
  - [x] @[backend_v2/services/auth/repositories.py]
  - [x] @[backend_v2/services/auth/token_service.py]
  - [x] @[backend_v2/services/auth/user_service.py]
  - [x] @[backend_v2/services/auth/organization_service.py]
  - [x] [NEW] @[backend_v2/services/auth/secret_service.py]
  - [x] [NEW] @[backend_v2/services/auth/email_service.py]
  - [x] @[backend_v2/services/auth/__init__.py]
  - [x] [NEW] @[backend_v2/services/execution/assignment_service.py]
  - [x] @[backend_v2/services/execution/lifecycle_service.py]
  - [x] @[backend_v2/services/execution/ingress_service.py]
  - [x] [NEW] @[backend_v2/core/redis_security.py]
  - [x] @[backend_v2/services/usage_service.py]
  - [x] @[backend_v2/llm/provider/litellm_provider.py]
  - [x] @[backend_v2/llm/provider/provider_factory.py]
  - [x] @[backend_v2/services/mcp/generic_mcp_client.py]
  - [x] @[backend_v2/services/mcp/dispatcher.py]
  - [x] @[backend_v2/api/dependencies.py]
  - [x] @[backend_v2/api/routers/iam/auth.py]
  - [x] @[backend_v2/api/routers/iam/users.py]
  - [x] @[backend_v2/api/routers/iam/organizations.py]
  - [x] @[backend_v2/api/routers/execution/executions.py]
  - [x] @[scripts/sanitize_seed_vault.py]
  - [x] @[scripts/audit_zero_orm_strictness.py]
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/run_e2e_variance_test.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_160_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` across existing and `[NEW]` frontend targets.
  - [x] @[client_app_v2/lib/core/models/enums.dart]
  - [x] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]
  - [x] @[client_app_v2/lib/features/auth/domain/models/user.dart]
  - [x] @[client_app_v2/lib/features/auth/data/auth_repository.dart]
  - [x] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart]
  - [x] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]
  - [x] @[client_app_v2/lib/router/router.dart]
  - [x] @[client_app_v2/lib/router/scaffold_with_nav.dart]
  - [x] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [x] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]
  - [x] [NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]
  - [x] [NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]
  - [x] [NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
  - [x] [NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/epic/EPIC_160_tracker.md] @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md] @[ki_god_code_prevention.md] @[ki_zero_permissive_typing.md] @[ki_router_ssot_and_crud_clone_lifecycle.md] @[ki_frontend_iam_role_segregation.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`, `@[ki_zero_permissive_typing.md]`, `@[ki_router_ssot_and_crud_clone_lifecycle.md]`, and `@[ki_frontend_iam_role_segregation.md]`: Document the 15-table PostgreSQL 19 Zero-ORM IAM schema (`invitations`, `tenant_secrets`, `execution_assignments`), `POST /api/v2/iam/auth/exchange` Hybrid Session Upgrade with mandatory 2FA, Dual-Key Fail-Closed Redis Kill-Switch (`MGET`), `SecretService` Dual-Tier BYOK engine, `ExecutionAssignmentService` SafeLinks-immune Two-Phase Task Activation, and the 3 separated role-aware Flutter views (`UserProfileSettingsView`, `OrganizationIamSettingsView`, `TaskAssignmentPortalView`).
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `backend_v2/services/auth/secret_service.py`, `backend_v2/services/auth/email_service.py`, `backend_v2/services/execution/assignment_service.py`, `backend_v2/core/redis_security.py`, `client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart`, `client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart`, `client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart`, and `client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart`, and remove `backend_v2/services/auth/constants.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing newly established IAM, BYOK, Redis Kill-Switch, and Time-Bound Execution Assignment invariants in present tense without historical language or Epic IDs.

### Final Epic Audit

- [x] **[OK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: Commit each verified logical step with explicit relative paths in English.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan -> Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-160-001 | Delete four obsolete IAM draft documents and `backend_v2/services/auth/constants.py`, remediate touched-scope technical debt in `identity.py` and IAM test suites, and centralize JWT/MFA/BYOK/email settings in `settings.py` | Phase 1, Step 1.1 | [x] Completed |
| REQ-160-002 | Migrate `UserRole` and `SubscriptionStatus` to `enums.py`, add IAM/BYOK/Assignment enums and error codes, and create/define strict `PrefixedUUID7` DTOs (`TokenExchangeRequestDTO`, `TokenExchangeResponseDTO`, `LogoutRequestDTO`, `LogoutResponseDTO`, `CliSessionStateDTO`, `Invitation*`, `ExecutionAssignment*`, `TenantSecret*`, `ResolvedCredentialDTO`) | Phase 1, Step 1.2 | [x] Completed |
| REQ-160-003 | Extend PostgreSQL 19 Zero-ORM schema (`001_pg19_uuidv7_schema.sql`), `PostgresEntityAdapter`, `PostgresUnitOfWork` (`RESET quorum.current_org`), `audit_zero_orm_strictness.py` (15 tables), and hermetic `in_memory_uow.py` with `invitations`, `tenant_secrets`, and `execution_assignments` | Phase 1, Step 1.3 | [x] Completed |
| REQ-160-004 | Implement `TokenService.exchange_firebase_token` (enforcing mandatory 2FA `firebase.sign_in_second_factor` and headless CLI `target_user_id` exchange) and refactor `TokenService.verify_token` to 0.1 ms RAM-only decode with zero DB queries and zero `mock-token:` branches | Phase 2, Step 2.1 | [x] Completed |
| REQ-160-005 | Expose `POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/logout`, and RFC 8693 `POST /api/v2/iam/auth/impersonate`, remove `verify_user_token` and duplicate `/auth/users*` shadow routes, and upgrade `require_role` to `Sequence[UserRole] \| UserRole` | Phase 2, Step 2.2 | [x] Completed |
| REQ-160-006 | Migrate `scripts/run_e2e_variance_test.py` and `test_integration_real_llm.py` to `_get_or_refresh_cli_session` (`CliSessionStateDTO` created in Phase 1) with 13-minute auto-refresh and remediate all `TD_DICT_GET` and `TD_MODEL_FACTORY` warnings | Phase 2, Step 2.3 | [x] Completed |
| REQ-160-007 | Create `SecretService` in `[NEW] backend_v2/services/auth/secret_service.py` supporting `CLOUD_SECRET_MANAGER` and `ENVELOPE_KMS` (AES-256-GCM DEK + Cloud KMS KEK with `kek_version`) with a Single-Pipeline Non-Nullable `ResolvedCredentialDTO` contract | Phase 3, Step 3.1 | [x] Completed |
| REQ-160-008 | Inject request-scoped `pydantic.SecretStr` credentials dynamically per `organization_id` into `LLMFactory`, `LiteLLMProvider`, `ToolDispatcher`, and `GenericMCPClient` with zero cross-tenant bleed | Phase 3, Step 3.2 | [x] Completed |
| REQ-160-009 | Expose organization BYOK endpoints (`GET`, `PUT`, `DELETE` under `/api/v2/iam/organizations/{org_id}/secrets`) and add AST guardrail in `scripts/_ast_guardrails.py` preventing `SecretStr.get_secret_value()` leakage | Phase 3, Step 3.3 | [x] Completed |
| REQ-160-010 | Create `RevocationCache` in `[NEW] backend_v2/core/redis_security.py` executing atomic O(1) Dual-Key Redis `MGET revoked:usr:{id} revoked:jti:{jti}` with strict Fail-Closed `503 Service Unavailable` semantics and wire into `get_current_user_from_header` | Phase 4, Step 4.1 | [x] Completed |
| REQ-160-011 | Create `TenantRateLimitService` in `[NEW] backend_v2/core/redis_security.py` (per-org `rpm_limit`/`tpm_limit` and edge IP rate limiting) and monthly USD `quota_limit` / `SubscriptionStatus` check in `UsageService.check_quota` | Phase 4, Step 4.2 | [x] Completed |
| REQ-160-012 | Create `EmailService` in `[NEW] backend_v2/services/auth/email_service.py` and cryptographic single/batch B2B invitations (`create_invitation`, `create_invitation_batch`, `accept_invitation`) with `allowed_email_domains` and 1:1 Flat Identity Collision Guard | Phase 5, Step 5.1 | [x] Completed |
| REQ-160-013 | Enforce the 4-Tier RBAC Governance Matrix (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`), self-service profile updates (`name`, `language`, `theme_mode`), soft-delete aware `LAST_ADMIN_PROTECTION`, and immediate Redis Kill-Switch on privilege mutations | Phase 5, Step 5.2 | [x] Completed |
| REQ-160-014 | Implement in-place GDPR Soft-Delete anonymization in `UserService.delete_user` and `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` preserving `executions` foreign keys | Phase 5, Step 5.3 | [x] Completed |
| REQ-160-015 | Create `ExecutionAssignmentService` in `[NEW] backend_v2/services/execution/assignment_service.py` and `/api/v2/execution/executions/assignments` endpoints with SafeLinks-immune `GET .../preview`, JIT user onboarding + 2FA, explicit `POST .../activate`, Dual-Clock expiration, and single-shot submission | Phase 5, Step 5.4 | [x] Completed |
| REQ-160-016 | Implement mandatory 2FA challenge/enrollment in Flutter `LoginScreen` and `AuthController`, `@Riverpod(keepAlive: true)` `AuthRepository` with Freezed DTOs, `AuthInterceptor` token exchange, 13-minute silent refresh, and the 5-step `signOut` pipeline | Phase 6, Step 6.1 | [x] Completed |
| REQ-160-017 | Repurpose `ScaffoldWithNav` to **Profiili / Profile** with trailing Sign Out action, and build `UserProfileSettingsView`, `OrganizationIamSettingsView`, Direct Task Assignment Builder in `NewExecutionView`, and `TaskAssignmentPortalView` (`/task/:token`) | Phase 6, Step 6.2 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Phase 1 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 1.1**: Physically deleted the 4 obsolete IAM draft documents and `backend_v2/services/auth/constants.py`, relocated `SYSTEM_ROOT_USER_ID = "usr_0195f3a00000700a83fd6b3d77c748f4"` to `@[backend_v2/models/auth.py]`, centralized all 16 IAM/JWT/MFA/BYOK/Email/KMS settings on `Settings` in `@[backend_v2/settings.py]`, eradicated the `TD_DICT_GET` warnings in `@[backend_v2/database/repositories/identity.py]` by delegating through `EntityPersistencePort`, and remediated all touched-scope `TD_ISTQB_NEGATIVE` and `TD_MODEL_FACTORY` warnings across IAM test suites (`0` findings on `audit_technical_debt.py`).
  - **Step 1.2**: Migrated `UserRole` and `SubscriptionStatus` to `@[backend_v2/models/enums.py]`, added `InvitationStatus`, `AssignmentStatus`, `AssignmentResultVisibility`, `EmailTransportMode`, `EmailDeliveryStatus`, `SecretScope`, `SecretStorageMode`, and `EntityPrefix` (`INVITATION = "inv"`, `TENANT_SECRET = "sec"`, `ASSIGNMENT = "tsk"`), added the 7 IAM/BYOK/Assignment error codes to `@[backend_v2/exceptions.py]`, demolished `LEGACY_SYSTEM`, `TokenPayload`, and `LoginResponse`, set `SystemOrganizations.ROOT_SYSTEM = "org_0195f3a0000070008000000000000001"`, and created all strict `PrefixedUUID7` IAM, Invitation, Task Assignment, and BYOK DTOs in `@[backend_v2/models/auth.py]` and `@[backend_v2/models/domain/execution.py]`.
  - **Step 1.3**: Extended `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[scripts/audit_zero_orm_strictness.py]` (15 tables), `@[backend_v2/database/postgres/uow.py]` (`RESET quorum.current_org;`), and `@[backend_v2/tests/fakes/in_memory_uow.py]` with `invitations`, `tenant_secrets`, and `execution_assignments` and implemented all 6 `<test_contracts>`.
- Completed Phase 2 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 2.1**: Implemented `TokenService.exchange_firebase_token(payload: TokenExchangeRequestDTO) -> TokenExchangeResponseDTO` (enforcing mandatory `firebase.sign_in_second_factor` 2FA, 1:1 `firebase_uid` binding with `ConflictError` on collision, and headless CLI `target_user_id` exchange) and refactored `TokenService.verify_token(token: str) -> TokenData` in `@[backend_v2/services/auth/token_service.py]` to perform 0.1 ms RAM-only `Quorum Local JWT` decode with zero database queries and zero `mock-token:` string prefix branches.
  - **Step 2.2**: Exposed `POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/logout`, and RFC 8693 `POST /api/v2/iam/auth/impersonate` in `@[backend_v2/api/routers/iam/auth.py]` and `@[backend_v2/services/auth/__init__.py]`, deleted the 4 duplicate `/auth/users*` routes from `@[backend_v2/api/routers/iam/auth.py]`, exposed `POST /api/v2/iam/users` in `@[backend_v2/api/routers/iam/users.py]`, removed catch-all `try ... except Exception` blocks in `@[backend_v2/api/routers/iam/users.py]` and `@[backend_v2/api/routers/iam/organizations.py]`, and upgraded `require_role` in `@[backend_v2/api/dependencies.py]` to accept `Sequence[UserRole] | UserRole`.
  - **Step 2.3**: Implemented `_get_or_refresh_cli_session` with 13-minute auto-refresh (`expires_in_seconds - 120.0`) in `@[scripts/run_e2e_variance_test.py]`, migrated all `"Bearer mock-token:..."` headers in `@[scripts/run_e2e_variance_test.py]` and `@[backend_v2/tests/integration/test_integration_real_llm.py]`, and remediated all 132 `TD_DICT_GET` warnings and 2 `TD_MODEL_FACTORY` warnings (`0` findings across all 80 Epic 160 targets).
- Completed Phase 3 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 3.1**: Created `SecretService` in `@[backend_v2/services/auth/secret_service.py]` implementing Dual-Tier BYOK Secret Governance (`CLOUD_SECRET_MANAGER` and `ENVELOPE_KMS` with AES-256-GCM DEK + Cloud KMS KEK and `kek_version`) returning a non-nullable `ResolvedCredentialDTO` with zero fallback to platform keys on decryption/lookup failure (`3b27084c8`).
  - **Step 3.2**: Updated `LLMFactory._resolve_provider_api_key`, `LLMFactory.create_provider`, `LiteLLMProvider`, `ToolDispatcher`, and `GenericMCPClient` to inject request-scoped `pydantic.SecretStr` credentials dynamically per `organization_id` with tenant-isolated router cache keys (`f"{model_id}:{organization_id}"`) and zero secret leakage in `MCPAuditTrace` (`7f759a9f4`).
  - **Step 3.3**: Added `GET /api/v2/iam/organizations/{org_id}/secrets`, `PUT /api/v2/iam/organizations/{org_id}/secrets`, and `DELETE /api/v2/iam/organizations/{org_id}/secrets/{secret_id}` in `@[backend_v2/api/routers/iam/organizations.py]` guarded by `require_role([UserRole.ROOT, UserRole.ADMIN])`, added `QGR033` DLP AST guardrail check in `@[scripts/_ast_guardrails.py]` preventing `SecretStr.get_secret_value()` serialization inside logger calls or `MCPAuditTrace` instantiations (`3c051f263`), and updated subpackage test discovery in `@[scripts/backend_audit_loop.py]` (`792a2fe62`).
- Completed Phase 4 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 4.1**: Created `RevocationCache` in `@[backend_v2/core/redis_security.py]` implementing atomic O(1) Dual-Key Redis `MGET revoked:usr:{user_id} revoked:jti:{jti}` with strict Fail-Closed `503 Service Unavailable` (`ErrorCodes.SERVICE_UNAVAILABLE`) semantics when Redis is unreachable and `401 AuthenticationError` (`ErrorCodes.AUTH_TOKEN_EXPIRED`) when revoked, and wired `await revocation_cache.assert_not_revoked(token_data)` into `get_current_user_from_header` in `@[backend_v2/api/dependencies.py]` (`6b51bcd55`).
  - **Step 4.2**: Created `TenantRateLimitService` and `TenantRateLimitStatusDTO` in `@[backend_v2/core/redis_security.py]` enforcing per-organization `rpm_limit` / `tpm_limit` sliding-window counters and public auth-edge IP rate limiting (`PUBLIC_AUTH_EDGE_SCOPES`) raising `429 TokenLimitExceededError` (`ErrorCodes.RATE_LIMIT_EXCEEDED`), and updated `UsageService.check_quota` in `@[backend_v2/services/usage_service.py]` to enforce `SubscriptionStatus` (`ACTIVE`, `TRIAL`) and monthly USD `quota_limit` (`ErrorCodes.QUOTA_EXCEEDED`, HTTP 402) (`6b51bcd55`).
- Completed Phase 5 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 5.1**: Created `EmailService` in `@[backend_v2/services/auth/email_service.py]` and implemented single and cohort batch B2B invitations (`create_invitation`, `create_invitation_batch`, `accept_invitation`, `revoke_invitation`, `list_invitations`) in `@[backend_v2/services/auth/organization_service.py]` with `allowed_email_domains` and 1:1 Flat Identity Collision Guard (`9e8612164`).
  - **Step 5.2**: Enforced the 4-Tier RBAC Governance Matrix (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`), self-service profile updates (`name`, `language`, `theme_mode`), soft-delete aware `LAST_ADMIN_PROTECTION`, `OrganizationUpdateDTO`-only `update_organization`, immediate Redis Kill-Switch revocation on privilege mutations, and peer execution isolation in `@[backend_v2/services/auth/user_service.py]`, `@[backend_v2/services/auth/organization_service.py]`, and `@[backend_v2/services/execution/lifecycle_service.py]` (`9d9a42cca`).
  - **Step 5.3**: Implemented in-place GDPR Soft-Delete anonymization in `UserService.delete_user` (`@[backend_v2/services/auth/user_service.py]`) and exposed `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` in `@[backend_v2/api/routers/iam/auth.py]` preserving `executions` foreign keys (`2416a7416`).
  - **Step 5.4**: Created `ExecutionAssignmentService` in `@[backend_v2/services/execution/assignment_service.py]` and exposed `/api/v2/execution/executions/assignments` endpoints in `@[backend_v2/api/routers/execution/executions.py]` implementing single/batch task assignments, SafeLinks-immune `GET .../preview`, JIT user onboarding + 2FA, explicit `POST .../activate`, Dual-Clock expiration, draft checkpointing, single-shot submission via `ExecutionIngressService.start_execution`, and `AssignmentResultVisibility` (`4a17b7736`).
- Completed Phase 6 (`/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`):
  - **Step 6.1**: Implemented `@Riverpod(keepAlive: true)` `AuthRepository` with Freezed `TokenExchangeRequestDto`, `TokenExchangeResponseDto`, `LogoutRequestDto`, `LogoutResponseDto`, and `MfaAuthProgressDto` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart]`), mandatory TOTP 2FA enrollment/challenge state machine in `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]` and `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, `AuthInterceptor` session upgrade handshake with single-flight `Completer<String>` lock (`@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]`), 13-minute silent refresh timer, and the 5-step `signOut` pipeline with multi-tenant provider invalidation (`75fc4db25`).
  - **Step 6.2**: Created `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`, `@[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`, `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, and `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`, updated `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]` with `assign_as_task_btn` and `_TaskAssignmentConfigDialog`, updated `@[client_app_v2/lib/router/router.dart]` (`/settings`, `/organization`, `/task/:token`) and `@[client_app_v2/lib/router/scaffold_with_nav.dart]` (**Profiili / Profile** + trailing Sign Out + role-aware `/organization` destination), and verified all 4 Phase 6 `<test_contracts>`.
- Completed Post-EPIC 160 Tier 4 Bug-Fix Hardening (`45c9cacda`, `02d2248f7`, `3402d327b`, `71b5247c6`):
  - Enforced idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` column evolutions in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` (`ZORM007` in `@[scripts/audit_zero_orm_strictness.py]`), `await uow.pool_manager.apply_migrations()` preflight in `@[backend_v2/seed/run_seed.py]`, and $O(1)$ `await self.driver.get(collection, id)` PK lookup in `@[backend_v2/database/repositories/identity.py]`.
  - Enforced `useContext()` + post-`await` `if (!context.mounted) return res;` unmount guard in `@[client_app_v2/lib/core/state/mutation.dart]` (`DGR011` in `@[scripts/_dart_guardrails.py]`, banning `useIsMounted()`) and `GoRouter.refreshListenable` + `ValueNotifier<AsyncValue<User?>>` + `ref.listen` bridge in `@[client_app_v2/lib/router/router.dart]` (`DGR012` in `@[scripts/_dart_guardrails.py]`, banning `ref.watch(authControllerProvider)` inside `router(Ref ref)` and preserving `/login` during `AsyncLoading()`).
- Completed `/tier7-describe-architecture` and `/tier8-audit-epic`:
  - Synchronized Knowledge Items (`@[ki_zero_permissive_typing.md]`, `@[ki_god_code_prevention.md]`, `@[ki_router_ssot_and_crud_clone_lifecycle.md]`, `@[ki_frontend_iam_role_segregation.md]`), `@[.agents/rules/04_directory_reference.md]`, timeless architecture pillars (`01_`, `02_`, `04_`, `05_`), and `@[docs/epic/EPIC_160_audit_report.md]`.

## Learned
- `pydantic.mypy` requires `allowed_email_domains=[]` to be explicitly passed when instantiating `Organization(...)` directly in service/fake constructors (`@[backend_v2/services/auth/user_service.py]`, `@[backend_v2/services/auth/organization_service.py]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`).
- `@[backend_v2/tests/unit/database/test_postgres.py]` enforces 1:1 column-to-DTO-field naming parity across all 15 tables in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` (`tenant_secrets` includes a `VIRTUAL` generated `created_at` column), and `ZORM007` enforces idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` column evolutions for existing developer databases.
- `audit_dict_eradication.py` bans `dict[str, JsonValue]` return type annotations on test helper methods (`unauthorized_open_json_annotations`); fixture helpers in unit tests must return concrete validated Pydantic V2 DTOs (`TokenExchangeResponseDTO`) and call `.model_dump(mode="json")` at the mock boundary.
- When benchmarking sub-millisecond in-memory `RevocationCache.assert_not_revoked` execution in unit tests, warm up `get_settings()` once before `time.perf_counter_ns()` so cold `.env` disk loading on Windows does not skew the `MGET` latency measurement.
- In Flutter, `GoRouter` must be bound to `authControllerProvider` via `refreshListenable` + `ValueNotifier<AsyncValue<User?>>` (`DGR012`) rather than `ref.watch(authControllerProvider)` so `AsyncLoading()` transitions during TOTP 2FA challenges do not destroy `LoginScreen` state, and `useMutation` must guard post-`await` `state.value` assignments with `if (!context.mounted)` via `useContext()` (`DGR011`).

## Remaining
- None. All phases (Phases 1–6), post-implementation hardening gates, Tier 4 bug-fix guardrails (`ZORM007`, `DGR011`, `DGR012`), `/tier7-describe-architecture`, and `/tier8-audit-epic` are 100% complete and verified.

## Resume Command
```powershell
/tier8-audit-epic @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]
```
