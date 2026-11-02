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
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 1.1: Obsolete Document Demolition & Touched-Scope Technical Debt Remediation
  - [ ] Step 1.2: Taxonomies, ErrorCodes & Strict `PrefixedUUID7` Identity & Assignment Models
  - [ ] Step 1.3: PostgreSQL 19 Zero-ORM Identity, Invitation, Task Assignment & Secrets Schema + Dual-Layer Tenant Isolation
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 2: Session Upgrade, Token Exchange Engine, Headless CLI Governance & Multi-Role Guard
**Plan:** @[docs/epic/tasks_EPIC_160/02_phase2_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/02_phase2_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 2.1: `TokenService` Session Upgrade (`exchange_firebase_token`), Mandatory 2FA Enforcement & 0.1 ms RAM Verification
  - [ ] Step 2.2: Token Exchange & Logout Router Endpoints, IAM Router SSOT Consolidation & Multi-Role Dependency Guard
  - [ ] Step 2.3: Headless CLI, E2E Variance Runner (`run_e2e_variance_test.py`) & Background Worker Session Governance
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/02_phase2_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 3: Enterprise BYOK & Cloud Secrets Engine for LLM & MCP Services
**Plan:** @[docs/epic/tasks_EPIC_160/03_phase3_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/03_phase3_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 3.1: `SecretService` (Cloud Secret Manager & Envelope Encryption — Single-Pipeline Non-Nullable Resolution)
  - [ ] Step 3.2: Request-Scoped Credential Injection in `LiteLLMProvider` & `GenericMCPClient`
  - [ ] Step 3.3: Organization BYOK Management Endpoints & DLP AST Guardrail
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/03_phase3_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 4: Real-Time Dual-Key Redis Kill-Switch (`MGET`) & FinOps Rate Limiting
**Plan:** @[docs/epic/tasks_EPIC_160/04_phase4_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/04_phase4_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 4.1: Fail-Closed Dual-Key Redis Kill-Switch (`RevocationCache`)
  - [ ] Step 4.2: Per-Tenant Redis Sliding-Window Rate Limiter & FinOps Pre-Flight Gatekeeper
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/04_phase4_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 5: B2B Invitation Flow, Time-Bound Execution Assignments (`ExecutionAssignment`), 4-Tier RBAC Matrix, Self-Service Profile & GDPR Soft-Delete Webhook
**Plan:** @[docs/epic/tasks_EPIC_160/05_phase5_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/05_phase5_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 5.1: Cryptographic B2B Invitations & 1:1 Flat Identity Collision Guard
  - [ ] Step 5.2: 4-Tier RBAC Governance (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`) & Self-Service Profile (`name`, `language`, `theme_mode`)
  - [ ] Step 5.3: GDPR Soft-Delete Anonymization & Firebase Deletion Webhook
  - [ ] Step 5.4: Time-Bound Execution Assignments (`ExecutionAssignmentService`), SafeLinks-Immune Activation & Combined JIT User Onboarding
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/05_phase5_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Phase 6: Flutter Client `AuthInterceptor`, Silent Refresh, Cryptographic Logout Pipeline & Separated User/Organization Views
**Plan:** @[docs/epic/tasks_EPIC_160/06_phase6_plan.md]
- [x] **[OK] Create Plan:** Plan generated in @[docs/epic/tasks_EPIC_160/06_phase6_plan.md]
- [ ] **[NOK] Red-Teaming:** `/tier0-research-plan @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`
  - [ ] Step 0: PRE-FLIGHT & SELF-HYDRATION
  - [ ] Step 6.1: Mandatory 2FA Enrollment/Challenge Flow, `AuthInterceptor`, Session Upgrade Handshake, 13-Minute Silent Refresh & 5-Step Logout Pipeline
  - [ ] Step 6.2: Adaptive Navigation Logout Action, Separated User Profile View (`UserProfileSettingsView`), Organization IAM Studio UI (`OrganizationIamSettingsView`), Direct Task Assignment Builder in `NewExecutionView` & Task Assignment Portal (`TaskAssignmentPortalView`)
- [ ] **[NOK] Test Coverage Assertions:** The Tier 2 execution agent MUST explicitly execute the test coverage assertions for this phase before passing it to the audit.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_EPIC_160/06_phase6_plan.md] @[docs/epic/EPIC_160_tracker.md]`

### Integration Checkpoint: Full-Stack Validation
- [ ] **[NOK] Backend & Frontend Full-Stack Integration Gate**

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests were left behind in the modified domains.
- [ ] **[NOK] Proxy Sunset & Consumer Migration**: Codebase-wide search/replace of old import paths & delete deprecated proxies.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_160_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` across existing and `[NEW]` backend targets.
  - [ ] @[backend_v2/settings.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/exceptions.py]
  - [ ] @[backend_v2/models/auth.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/__init__.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]
  - [ ] @[backend_v2/database/postgres/uow.py]
  - [ ] @[backend_v2/database/repositories/identity.py]
  - [ ] @[backend_v2/services/auth/repositories.py]
  - [ ] @[backend_v2/services/auth/token_service.py]
  - [ ] @[backend_v2/services/auth/user_service.py]
  - [ ] @[backend_v2/services/auth/organization_service.py]
  - [ ] [NEW] @[backend_v2/services/auth/secret_service.py]
  - [ ] [NEW] @[backend_v2/services/auth/email_service.py]
  - [ ] @[backend_v2/services/auth/__init__.py]
  - [ ] [NEW] @[backend_v2/services/execution/assignment_service.py]
  - [ ] @[backend_v2/services/execution/lifecycle_service.py]
  - [ ] @[backend_v2/services/execution/ingress_service.py]
  - [ ] [NEW] @[backend_v2/core/redis_security.py]
  - [ ] @[backend_v2/services/usage_service.py]
  - [ ] @[backend_v2/llm/provider/litellm_provider.py]
  - [ ] @[backend_v2/llm/provider/provider_factory.py]
  - [ ] @[backend_v2/services/mcp/generic_mcp_client.py]
  - [ ] @[backend_v2/services/mcp/dispatcher.py]
  - [ ] @[backend_v2/api/dependencies.py]
  - [ ] @[backend_v2/api/routers/iam/auth.py]
  - [ ] @[backend_v2/api/routers/iam/users.py]
  - [ ] @[backend_v2/api/routers/iam/organizations.py]
  - [ ] @[backend_v2/api/routers/execution/executions.py]
  - [ ] @[scripts/sanitize_seed_vault.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/EPIC_160_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"` across existing and `[NEW]` frontend targets.
  - [ ] @[client_app_v2/lib/core/models/enums.dart]
  - [ ] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart]
  - [ ] @[client_app_v2/lib/features/auth/domain/models/user.dart]
  - [ ] @[client_app_v2/lib/features/auth/data/auth_repository.dart]
  - [ ] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart]
  - [ ] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]
  - [ ] @[client_app_v2/lib/router/router.dart]
  - [ ] @[client_app_v2/lib/router/scaffold_with_nav.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]
  - [ ] [NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]
  - [ ] [NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]
  - [ ] [NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
  - [ ] [NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for surviving business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
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

- [ ] **[NOK]** System 2 Reverse Epic Analysis: Run `/tier8-audit-epic @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: Commit each verified logical step with explicit relative paths in English.
- **Database Seeding**: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local`
- **Workflow Loop**: `[/tier0-create-plan if deferred] -> /tier0-research-plan -> /tier2-execute --full-auto -> /tier8-audit-plan -> Post-Implementation Gates -> parameterized /tier7-describe-architecture -> /tier8-audit-epic`. Always pass BOTH the plan and the tracker file in all commands.

## Requirements Traceability Matrix

| Requirement | Description | Phase / Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-160-001 | Delete four obsolete IAM draft documents and `backend_v2/services/auth/constants.py`, remediate touched-scope technical debt in `identity.py` and IAM test suites, and centralize JWT/MFA/BYOK/email settings in `settings.py` | Phase 1, Step 1.1 | [ ] Pending |
| REQ-160-002 | Migrate `UserRole` and `SubscriptionStatus` to `enums.py`, add IAM/BYOK/Assignment enums and error codes, and create/define strict `PrefixedUUID7` DTOs (`TokenExchangeRequestDTO`, `TokenExchangeResponseDTO`, `LogoutRequestDTO`, `LogoutResponseDTO`, `CliSessionStateDTO`, `Invitation*`, `ExecutionAssignment*`, `TenantSecret*`, `ResolvedCredentialDTO`) | Phase 1, Step 1.2 | [ ] Pending |
| REQ-160-003 | Extend PostgreSQL 19 Zero-ORM schema (`001_pg19_uuidv7_schema.sql`), `PostgresEntityAdapter`, `PostgresUnitOfWork` (`RESET quorum.current_org`), `audit_zero_orm_strictness.py` (15 tables), and hermetic `in_memory_uow.py` with `invitations`, `tenant_secrets`, and `execution_assignments` | Phase 1, Step 1.3 | [ ] Pending |
| REQ-160-004 | Implement `TokenService.exchange_firebase_token` (enforcing mandatory 2FA `firebase.sign_in_second_factor` and headless CLI `target_user_id` exchange) and refactor `TokenService.verify_token` to 0.1 ms RAM-only decode with zero DB queries and zero `mock-token:` branches | Phase 2, Step 2.1 | [ ] Pending |
| REQ-160-005 | Expose `POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/logout`, and RFC 8693 `POST /api/v2/iam/auth/impersonate`, remove `verify_user_token` and duplicate `/auth/users*` shadow routes, and upgrade `require_role` to `Sequence[UserRole] \| UserRole` | Phase 2, Step 2.2 | [ ] Pending |
| REQ-160-006 | Migrate `scripts/run_e2e_variance_test.py` and `test_integration_real_llm.py` to `_get_or_refresh_cli_session` (`CliSessionStateDTO` created in Phase 1) with 13-minute auto-refresh and remediate all `TD_DICT_GET` and `TD_MODEL_FACTORY` warnings | Phase 2, Step 2.3 | [ ] Pending |
| REQ-160-007 | Create `SecretService` in `[NEW] backend_v2/services/auth/secret_service.py` supporting `CLOUD_SECRET_MANAGER` and `ENVELOPE_KMS` (AES-256-GCM DEK + Cloud KMS KEK with `kek_version`) with a Single-Pipeline Non-Nullable `ResolvedCredentialDTO` contract | Phase 3, Step 3.1 | [ ] Pending |
| REQ-160-008 | Inject request-scoped `pydantic.SecretStr` credentials dynamically per `organization_id` into `LLMFactory`, `LiteLLMProvider`, `ToolDispatcher`, and `GenericMCPClient` with zero cross-tenant bleed | Phase 3, Step 3.2 | [ ] Pending |
| REQ-160-009 | Expose organization BYOK endpoints (`GET`, `PUT`, `DELETE` under `/api/v2/iam/organizations/{org_id}/secrets`) and add AST guardrail in `scripts/_ast_guardrails.py` preventing `SecretStr.get_secret_value()` leakage | Phase 3, Step 3.3 | [ ] Pending |
| REQ-160-010 | Create `RevocationCache` in `[NEW] backend_v2/core/redis_security.py` executing atomic O(1) Dual-Key Redis `MGET revoked:usr:{id} revoked:jti:{jti}` with strict Fail-Closed `503 Service Unavailable` semantics and wire into `get_current_user_from_header` | Phase 4, Step 4.1 | [ ] Pending |
| REQ-160-011 | Create `TenantRateLimitService` in `[NEW] backend_v2/core/redis_security.py` (per-org `rpm_limit`/`tpm_limit` and edge IP rate limiting) and monthly USD `quota_limit` / `SubscriptionStatus` check in `UsageService.check_quota` | Phase 4, Step 4.2 | [ ] Pending |
| REQ-160-012 | Create `EmailService` in `[NEW] backend_v2/services/auth/email_service.py` and cryptographic single/batch B2B invitations (`create_invitation`, `create_invitation_batch`, `accept_invitation`) with `allowed_email_domains` and 1:1 Flat Identity Collision Guard | Phase 5, Step 5.1 | [ ] Pending |
| REQ-160-013 | Enforce the 4-Tier RBAC Governance Matrix (`VIEWER`/`MEMBER` vs. `MANAGER` vs. `ADMIN` vs. `ROOT`), self-service profile updates (`name`, `language`, `theme_mode`), soft-delete aware `LAST_ADMIN_PROTECTION`, and immediate Redis Kill-Switch on privilege mutations | Phase 5, Step 5.2 | [ ] Pending |
| REQ-160-014 | Implement in-place GDPR Soft-Delete anonymization in `UserService.delete_user` and `POST /api/v2/iam/auth/webhooks/firebase-user-deleted` preserving `executions` foreign keys | Phase 5, Step 5.3 | [ ] Pending |
| REQ-160-015 | Create `ExecutionAssignmentService` in `[NEW] backend_v2/services/execution/assignment_service.py` and `/api/v2/execution/executions/assignments` endpoints with SafeLinks-immune `GET .../preview`, JIT user onboarding + 2FA, explicit `POST .../activate`, Dual-Clock expiration, and single-shot submission | Phase 5, Step 5.4 | [ ] Pending |
| REQ-160-016 | Implement mandatory 2FA challenge/enrollment in Flutter `LoginScreen` and `AuthController`, `@Riverpod(keepAlive: true)` `AuthRepository` with Freezed DTOs, `AuthInterceptor` token exchange, 13-minute silent refresh, and the 5-step `signOut` pipeline | Phase 6, Step 6.1 | [ ] Pending |
| REQ-160-017 | Repurpose `ScaffoldWithNav` to **Profiili / Profile** with trailing Sign Out action, and build `UserProfileSettingsView`, `OrganizationIamSettingsView`, Direct Task Assignment Builder in `NewExecutionView`, and `TaskAssignmentPortalView` (`/task/:token`) | Phase 6, Step 6.2 | [ ] Pending |

# Session Handover Context

## Achieved
- Executed Tier 1 Epic Planning (`/tier1-planner`) for `@[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]` and `@[docs/epic/EPIC_160_audit_report.md]`.
- Generated all 6 phased implementation plans in `@[docs/epic/tasks_EPIC_160/]`:
  - `@[docs/epic/tasks_EPIC_160/01_phase1_plan.md]` (Phase 1: Pre-Implementation Technical Debt Cleanups, Zero-ORM Identity Schema & `PrefixedUUID7` DTOs)
  - `@[docs/epic/tasks_EPIC_160/02_phase2_plan.md]` (Phase 2: Session Upgrade, Token Exchange Engine, Headless CLI Governance & Multi-Role Guard)
  - `@[docs/epic/tasks_EPIC_160/03_phase3_plan.md]` (Phase 3: Enterprise BYOK & Cloud Secrets Engine for LLM & MCP Services)
  - `@[docs/epic/tasks_EPIC_160/04_phase4_plan.md]` (Phase 4: Real-Time Dual-Key Redis Kill-Switch (`MGET`) & FinOps Rate Limiting)
  - `@[docs/epic/tasks_EPIC_160/05_phase5_plan.md]` (Phase 5: B2B Invitation Flow, Time-Bound Execution Assignments (`ExecutionAssignment`), 4-Tier RBAC Matrix, Self-Service Profile & GDPR Soft-Delete Webhook)
  - `@[docs/epic/tasks_EPIC_160/06_phase6_plan.md]` (Phase 6: Flutter Client `AuthInterceptor`, Silent Refresh, Cryptographic Logout Pipeline & Separated User/Organization Views)
- Created and synchronized `@[docs/epic/EPIC_160_tracker.md]` with 100% requirements traceability (`REQ-160-001` through `REQ-160-017`).

## Learned
- All 9 `<demolish>` symbols (`LEGACY_SYSTEM`, `JWT_SECRET`, `JWT_ALGORITHM`, `LEGACY_SYSTEM_ROOT_USER_ID`, `LEGACY_SYSTEM_ORG_ID`, `LEGACY_ROOT_MASTER_ID`, `TokenPayload`, `LoginResponse`, `verify_user_token` replaced by newly created/defined DTOs), all `141` touched-scope technical debt warnings from `@[docs/epic/EPIC_160_audit_report.md]`, and all `#Lnn-Lmm` AST line boundaries are mapped deterministically across Phases 1–6.
- Hermetic unit tests for `PostgresEntityAdapter` require extending `_InMemoryPostgresStore.seed_tables` and `InMemoryAsyncPgConnection` in `@[backend_v2/tests/fakes/in_memory_uow.py]` in Phase 1, Step 1.3 alongside the 15-table PostgreSQL 19 DDL in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` and `@[scripts/audit_zero_orm_strictness.py]`.

## Remaining
- The next agent must run `/tier0-research-plan` to analyze and red-team Phase 1 (`@[docs/epic/tasks_EPIC_160/01_phase1_plan.md]`) before executing Phase 1.

## Resume Command
```powershell
/tier0-research-plan @[docs/epic/tasks_EPIC_160/01_phase1_plan.md] @[docs/epic/EPIC_160_tracker.md]
```

