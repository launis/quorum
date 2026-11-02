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

# Phase 6: Flutter Client `AuthInterceptor`, Silent Refresh, Cryptographic Logout Pipeline & Separated User/Organization Views

**Overview:** Synchronize Dart `@JsonEnum()` taxonomies in `@[client_app_v2/lib/core/models/enums.dart]` and Freezed IAM/BYOK/Assignment DTOs in `@[client_app_v2/lib/features/auth/domain/models/user.dart]` and `[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`, enforce mandatory TOTP 2FA enrollment (`TotpMultiFactorGenerator`) and 2FA challenge resolution (`MultiFactorResolver`) in `@[client_app_v2/lib/features/auth/presentation/login_screen.dart]` and `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart]`, implement `POST /api/v2/iam/auth/exchange` token handshake, 13-minute silent background refresh, and the deterministic 5-step `signOut` pipeline in `@[client_app_v2/lib/features/auth/data/auth_repository.dart]` and `@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]`, repurpose "Settings" to **Profiili / Profile** with a trailing **Sign Out** button in `@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]` and `@[client_app_v2/lib/router/router.dart#L55-L227]`, and build `UserProfileSettingsView`, `OrganizationIamSettingsView`, the Direct Task Assignment Builder in `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`, and `TaskAssignmentPortalView` (`/task/:token`).
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]`
- `[MODIFY] @[client_app_v2/lib/features/auth/domain/models/user.dart]`
- `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L11-L16]`
- `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L56-L61]`
- `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L73-L85]`
- `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L102-L123]`
- `[MODIFY] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`
- `[MODIFY] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]`
- `[MODIFY] @[client_app_v2/lib/router/router.dart#L55-L116]`
- `[MODIFY] @[client_app_v2/lib/router/router.dart#L55-L227]`
- `[MODIFY] @[client_app_v2/lib/router/router.dart#L66-L105]`
- `[MODIFY] @[client_app_v2/lib/router/router.dart#L72-L107]`
- `[MODIFY] @[client_app_v2/lib/router/router.dart#L219-L226]`
- `[MODIFY] @[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`
- `[MODIFY] @[client_app_v2/lib/router/scaffold_with_nav.dart#L101-L151]`
- `[MODIFY] @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`
- `[MODIFY] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`
- `[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`
- `[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`
- `[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`
- `[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]`
- `[NEW] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`
- `[NEW] @[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart]`
- `[NEW] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`
- `[NEW] @[client_app_v2/test/features/execution/views/task_assignment_portal_view_test.dart]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **6. Flutter Client `AuthInterceptor`, Silent Refresh, 5-Step Logout Pipeline & Separated User/Organization/Task Views**<br>`[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`<br>`[MODIFY] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/domain/models/user.dart]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L11-L16]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L56-L61]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L73-L85]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L102-L123]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`<br>`[MODIFY] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]`<br>`[MODIFY] @[client_app_v2/lib/router/router.dart#L55-L227]`<br>`[MODIFY] @[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`<br>`[MODIFY] @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`<br>`[MODIFY] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`<br>`[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`<br>`[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`<br>`[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`<br>`[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`<br>`[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]`<br>`[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]`<br>`[NEW] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`<br>`[NEW] @[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart]`<br>`[NEW] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`<br>`[NEW] @[client_app_v2/test/features/execution/views/task_assignment_portal_view_test.dart]` | Manual `Provider<AuthRepository>` in `auth_repository.dart`; `token ?? ''` and raw `response.data['user']` map indexing; sending raw `mock-token:` strings in `AuthInterceptor`; placeholder `SettingsRoute` in `router.dart`; missing Logout buttons in `ScaffoldWithNav` and settings; uncancelled refresh timer on `signOut`; local-only language state in `SharedPreferencesAsync` unsynced with `User.language`. | `@Riverpod(keepAlive: true)` `authRepository`; strict Freezed DTOs (`TokenExchangeRequestDto`, `TokenExchangeResponseDto`, `LogoutRequestDto`, `LogoutResponseDto`, and models in `[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`); mandatory 2FA challenge/enrollment in `LoginScreen`; 13-minute silent refresh + 5-step `AuthController.signOut` pipeline + 3 Logout UI surfaces (`ScaffoldWithNav` `NavigationRail.trailing`, `UserProfileSettingsView` Session & Security card, and `TaskAssignmentPortalView` account switch); separated `UserProfileSettingsView` (`/settings`), `OrganizationIamSettingsView` (`/organization`), direct task assignment builder in `NewExecutionView`, and `TaskAssignmentPortalView` (`/task/:token`). | Pruned client-side countdown state persistence in favor of server-authoritative `remaining_seconds` / `server_now_utc` synchronization on `ExecutionAssignmentPreviewDto`. | `flutter_audit_loop.py client_app_v2/ --build`, `audit_flutter_theme_sovereignty.py`, `audit_dto_parity.py`, and widget/unit tests in `[NEW] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`, `[NEW] @[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart]`, `[NEW] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, and `[NEW] @[client_app_v2/test/features/execution/views/task_assignment_portal_view_test.dart]`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, and `02_flutter_desktop.md` before modifying any Dart or ARB files.</action>
    <constraint>Enforce `manual_riverpod_providers`, `silent_json_fallbacks`, `freezed_when_ban`, `tenant_data_isolation`, `no_magic_strings_l10n`, `design_token_absolute_rule`, and `studio_unified_visual_design_system` across all Flutter models, controllers, and views.</constraint>
  </step>

  <demolish>
  - `LEGACY_SYSTEM`
  - `JWT_SECRET`
  - `JWT_ALGORITHM`
  - `LEGACY_SYSTEM_ROOT_USER_ID`
  - `LEGACY_SYSTEM_ORG_ID`
  - `LEGACY_ROOT_MASTER_ID`
  - `TokenPayload`
  - `LoginResponse`
  - `verify_user_token`
  </demolish>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/domain/models/user.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/data/auth_repository.dart#L11-L16]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/data/auth_repository.dart#L56-L61]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/data/auth_repository.dart#L73-L85]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/data/auth_repository.dart#L102-L123]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/presentation/login_screen.dart]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart#L55-L116]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart#L55-L227]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart#L66-L105]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart#L72-L107]</frontend>
    <frontend>@[client_app_v2/lib/router/router.dart#L219-L226]</frontend>
    <frontend>@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]</frontend>
    <frontend>@[client_app_v2/lib/router/scaffold_with_nav.dart#L101-L151]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]</frontend>
    <frontend>@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>[NEW] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/execution/views/task_assignment_portal_view_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`AuthController`, `LoginScreen`, `AuthRepository`, and `AuthInterceptor` enforce mandatory TOTP 2FA enrollment/challenge, `POST /api/v2/iam/auth/exchange` handshake (`TokenExchangeRequestDto` -> `TokenExchangeResponseDto`), 13-minute silent background token refresh, and the deterministic 5-step `signOut` pipeline with multi-tenant Riverpod provider invalidation (`tenant_data_isolation`).</item>
    <item>`ScaffoldWithNav` (`@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`) and `@[client_app_v2/lib/router/router.dart#L55-L227]` repurpose "Settings" to **Profiili / Profile** (`UserProfileSettingsView`), mount a persistent trailing **Sign Out** button in `NavigationRail.trailing` (`@[client_app_v2/lib/router/scaffold_with_nav.dart#L101-L151]`), add role-gated `/organization` (`OrganizationIamSettingsView` for `MANAGER`, `ADMIN`, `ROOT`), and allow unauthenticated access to `/task/:token` (`TaskAssignmentPortalView`).</item>
    <item>`[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`, `[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`, and `[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]` pass `flutter_audit_loop.py client_app_v2/ --build` and `audit_flutter_theme_sovereignty.py` with `0` violations.</item>
  </dod_checklist>

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

  <anti_targets>
    <file>@[backend_v2/services/orchestrator/dag_executor/__init__.py] (Do not modify Python backend files during Phase 6 Flutter client implementation)</file>
  </anti_targets>

  <step id="6.1" name="Mandatory 2FA Enrollment/Challenge Flow, `AuthInterceptor`, Session Upgrade Handshake, 13-Minute Silent Refresh &amp; 5-Step Logout Pipeline">
    <action>
      - **`[MODIFY] @[client_app_v2/lib/core/models/enums.dart]`, `[MODIFY] @[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]`, `[MODIFY] @[client_app_v2/lib/features/auth/domain/models/user.dart]`, `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L11-L16]`, `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L56-L61]`, `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L73-L85]`, `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L102-L123]`, `[MODIFY] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`, `[MODIFY] @[client_app_v2/lib/features/auth/presentation/login_screen.dart]`, & `[NEW] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`**:
        - Synchronize `@JsonEnum()` definitions in `@[client_app_v2/lib/core/models/enums.dart]` for `UserRole`, `SubscriptionStatus`, `InvitationStatus`, `AssignmentStatus`, `AssignmentResultVisibility`, `EmailTransportMode`, `EmailDeliveryStatus`, `SecretScope`, and `SecretStorageMode` (note: backend demolished `LoginResponse` was removed in Phase 1).
        - Direct all user accounts to use Two-Factor Authentication (2FA) in `AuthController` (`@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`) and `LoginScreen` (`@[client_app_v2/lib/features/auth/presentation/login_screen.dart]`):
          1. **Enrolled 2FA Challenge**: When `FirebaseAuth.instance.signInWithEmailAndPassword` throws `FirebaseAuthMultiFactorException`, capture the `MultiFactorResolver` in `AuthController` and display the 6-digit TOTP verification view in `LoginScreen` to complete second-factor authentication before calling `POST /api/v2/iam/auth/exchange`.
          2. **Mandatory First-Time 2FA Enrollment**: When a user signs in with a first factor but `user.multiFactor.enrolledFactors.isEmpty` (or when `POST /api/v2/iam/auth/exchange` returns `ErrorCodes.MFA_REQUIRED`), block workspace entry in `AuthController` and guide the user through mandatory TOTP 2FA enrollment (`user.multiFactor.getSession()` -> `TotpMultiFactorGenerator.generateSecret` -> provisioning URI / secret display + 6-digit TOTP confirmation) before executing `AuthRepository.exchangeToken(firebaseIdToken)`.
        - **Strict Freezed DTO Hydration & `@Riverpod(keepAlive: true)` Codegen in `AuthRepository`**:
          1. Replace the manual `final authRepositoryProvider = Provider<AuthRepository>(...)` declaration (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L11-L16]`) with `@Riverpod(keepAlive: true) AuthRepository authRepository(Ref ref)` (`manual_riverpod_providers`).
          2. Define Freezed `TokenExchangeRequestDto`, `TokenExchangeResponseDto`, `LogoutRequestDto`, and `LogoutResponseDto` in `@[client_app_v2/lib/features/auth/domain/models/user.dart]` with `@JsonSerializable(explicitToJson: true, disallowUnrecognizedKeys: true)` and explicit `@JsonKey(name: 'snake_case')` annotations (`freezed_explicit_to_json` & `silent_json_fallbacks`).
          3. Eliminate `token ?? ''` (`silent_json_fallbacks`), raw `response.data['user']` map indexing (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L56-L61]`), and raw `'HTTP_401'` string comparisons (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L73-L85]`); hydrate responses strictly via `TokenExchangeResponseDto.fromJson(response.data as Map<String, dynamic>)` and `LogoutResponseDto.fromJson(response.data as Map<String, dynamic>)`.
        - Update `AuthInterceptor` (`@[client_app_v2/lib/core/network/interceptors/auth_interceptor.dart#L11-L52]`), `AuthRepository.exchangeToken(String firebaseIdToken)`, `AuthRepository.debugSignInWithMockToken` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L102-L123]`), and `AuthController.debugMockLogin` (`@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`) so both interactive 2FA login (`firebase_token`) and local developer debug login (`target_user_id`) call `POST /api/v2/iam/auth/exchange` via `TokenExchangeRequestDto` to obtain and cache a cryptographically signed 15-minute `Quorum Local JWT` instead of sending raw `mock-token:` strings, and synchronize the authenticated user's persisted `user.language` and `user.themeMode` with `SettingsController` (`@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`).
        - Configure a periodic Riverpod background refresh timer in `AuthController` (`@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L64-L89]`) that fetches a fresh MFA-verified Firebase ID Token (or re-exchanges `target_user_id` in local debug mode) and calls `/api/v2/iam/auth/exchange` at minute 13 (2 minutes before JWT expiry).
        - **Deterministic 5-Step Logout Pipeline (`AuthController.signOut({bool revokeAllSessions = false})` & `AuthRepository.signOut({bool revokeAllSessions = false})`)**:
          1. **Cancel Background Refresh Timer First**: Immediately cancel `_refreshTimer?.cancel(); _refreshTimer = null;` so no in-flight silent refresh races with session termination.
          2. **Bounded Server-Side Token Revocation (`POST /api/v2/iam/auth/logout`)**: When a `Quorum Local JWT` is present, invoke `POST /api/v2/iam/auth/logout` with `LogoutRequestDto(revokeAllSessions: revokeAllSessions)`. Adhering to `graceful_network_degradation` and NIST SP 800-63B session termination guarantees, if the network is unreachable or the token is already expired (`DioException`), log the warning via `loggerServiceProvider` and always proceed with local credential destruction inside a `finally` block so the user is never trapped in an authenticated UI state.
          3. **IdP & Local Credential Destruction**: Execute `_firebaseAuth?.signOut()` and clear the cached `Quorum Local JWT` (`mockTokenProvider` / `AuthInterceptor` token state) and `mockUserProvider`.
          4. **Multi-Tenant Memory Cache Purge (`tenant_data_isolation`)**: Whenever `organizationId` changes or the user signs out, invalidate all tenant-cached Riverpod providers (`ref.invalidate(masterDataProvider)`, `ref.invalidate(executionListProvider)`, `ref.invalidate(availableWorkflowsProvider)`, `ref.invalidate(workflowsControllerProvider)`, and `ref.invalidate(promptBlocksControllerProvider)`).
          5. **Atomic Auth State Reset & GoRouter Redirect**: Set `state = const AsyncData(null)`, triggering `resolveAuthRedirect` in `@[client_app_v2/lib/router/router.dart#L72-L107]` to route the client deterministically to `/login`.
    </action>
  </step>

  <step id="6.2" name="Adaptive Navigation Logout Action, Separated User Profile View (`UserProfileSettingsView`), Organization IAM Studio UI (`OrganizationIamSettingsView`), Direct Task Assignment Builder in `NewExecutionView` &amp; Task Assignment Portal (`TaskAssignmentPortalView`)">
    <action>
      - **`[MODIFY] @[client_app_v2/lib/router/router.dart#L55-L116]`, `[MODIFY] @[client_app_v2/lib/router/router.dart#L55-L227]`, `[MODIFY] @[client_app_v2/lib/router/router.dart#L66-L105]`, `[MODIFY] @[client_app_v2/lib/router/router.dart#L72-L107]`, `[MODIFY] @[client_app_v2/lib/router/router.dart#L219-L226]`, `[MODIFY] @[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`, `[MODIFY] @[client_app_v2/lib/router/scaffold_with_nav.dart#L101-L151]`, `[MODIFY] @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`, `[MODIFY] @[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`, `[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`, `[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]`, `[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, `[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`, `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]`, `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]`, `[NEW] @[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart]`, `[NEW] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`, & `[NEW] @[client_app_v2/test/features/execution/views/task_assignment_portal_view_test.dart]`**:
        - Create Freezed models `TenantSecretResponseDto`, `TenantSecretCreateDto`, `InvitationResponseDto`, `InvitationBatchCreateDto`, `InvitationBatchResponseDto`, `ExecutionAssignmentPreviewDto`, `ExecutionAssignmentCreateDto`, `ExecutionAssignmentRecipientDto`, `ExecutionAssignmentBatchCreateDto`, `ExecutionAssignmentBatchResponseDto`, and `ExecutionAssignmentResponseDto` in `[NEW] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]` synchronized 1:1 with backend `InvitationCreateDTO`, `InvitationResponseDTO`, `InvitationBatchCreateDTO`, `InvitationBatchResponseDTO`, `ExecutionAssignmentCreateDTO`, domain models, and `TenantSecretDTO` created in `@[backend_v2/models/auth.py]` and `@[backend_v2/models/domain/execution.py#L85-L129]`.
        - **Adaptive Navigation Shell, Trailing Sign-Out Action & Route Guard Wiring (`@[client_app_v2/lib/router/router.dart#L55-L116]`, `@[client_app_v2/lib/router/router.dart#L55-L227]`, & `@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`)**:
          1. Replace the unused placeholder `Scaffold(body: Center(child: Text(l10n.settings)))` in `SettingsRoute` (`@[client_app_v2/lib/router/router.dart#L219-L226]`) with `UserProfileSettingsView`, and repurpose the 3rd navigation destination in `ScaffoldWithNav` (`@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`) from "Asetukset / Settings" (`l10n.navSettings`, `Icons.settings_outlined` / `Icons.settings`) to **Profiili / Profile** (`l10n.navProfile`: `"Profiili"` in `@[client_app_v2/lib/l10n/app_fi.arb]` and `"Profile"` in `@[client_app_v2/lib/l10n/app_en.arb]`, using `Icons.person_outline` and `Icons.person`), visible in both `NavigationRail` and `NavigationBar` for all authenticated roles (`VIEWER`, `MEMBER`, `MANAGER`, `ADMIN`, `ROOT`).
          2. Add `TypedStatefulShellBranch<OrganizationBranch>` (`OrganizationSettingsRoute` at `/organization`) rendering `OrganizationIamSettingsView`, and expose an **Organization & IAM** navigation destination in `ScaffoldWithNav` (`@[client_app_v2/lib/router/scaffold_with_nav.dart#L19-L147]`) exclusively when `user.role` is `MANAGER`, `ADMIN`, or `ROOT` (enforcing route redirect to `/dashboard` if a `MEMBER` or `VIEWER` navigates to `/organization`).
          3. Mount a persistent **Sign Out** action button (`IconButton` with `Icons.logout`, `tooltip: l10n.signOutBtn`, `FocusNode`, and `SystemMouseCursors.click` per `desktop_pro_tool_interaction`) inside `NavigationRail.trailing` in `_WideScreenLayout` (`@[client_app_v2/lib/router/scaffold_with_nav.dart#L101-L151]`) invoking `ref.read(authControllerProvider.notifier).signOut()`.
          4. Register `@TypedGoRoute<TaskAssignmentRoute>(path: '/task/:token')` rendering `TaskAssignmentPortalView` and update the `redirect` guard in `@[client_app_v2/lib/router/router.dart#L66-L105]` so unauthenticated users opening `/task/:token` are permitted directly onto `TaskAssignmentPortalView` without being redirected to `/login` (enabling inline JIT user registration + 2FA enrollment on the same route).
        - Build **View 1 — `UserProfileSettingsView`** in `[NEW] @[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart]` wrapped in `AppErrorBoundary` (`DGR009`) and `Center -> ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200))`:
          - Accessible to **all authenticated roles (`VIEWER`, `MEMBER`, `MANAGER`, `ADMIN`, `ROOT`)** for managing their personal profile and active session across both desktop (`>= 800dp`) and compact/mobile (`< 800dp`) layouts.
          - Displays read-only identity attributes (`email`, `role` pill badge, `organizationId`, and 2FA verification status) and editable controls for the user's own **display name (`name`)**, **preferred UI language (`language`: `fi` / `en`)**, and **theme (`themeMode`)**.
          - Updating `name`, `language`, or `themeMode` executes an optimistic update via `SettingsController` (`@[client_app_v2/lib/features/settings/presentation/settings_controller.dart]`) and `AuthController`, persisting the change both to `SharedPreferencesAsync` and to PostgreSQL via `PUT /api/v2/iam/users/{id}`.
          - Renders a **Session & Security** card (`studio_unified_visual_design_system`) containing a primary **"Sign Out"** button (`OutlinedButton.icon` with `Icons.logout` invoking `ref.read(authControllerProvider.notifier).signOut(revokeAllSessions: false)`) and a secondary **"Sign Out From All Devices"** action (`TextButton.icon` with `Icons.phonelink_erase` invoking `ref.read(authControllerProvider.notifier).signOut(revokeAllSessions: true)`).
        - Build **View 2 — `OrganizationIamSettingsView`** in `[NEW] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` wrapped in `AppErrorBoundary` (`DGR009`) and `Center -> ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200))` + **Direct Assignment Action in `NewExecutionView` (`@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`)**:
          - Accessible exclusively to **`MANAGER`, `ADMIN`, and `ROOT` roles** (hidden and blocked for `MEMBER` and `VIEWER`).
          - **Organization Profile & Time-Bound Task Assignments Section (`MANAGER`, `ADMIN`, and `ROOT`)**:
            1. Displays FinOps quota telemetry (`quota_limit`, `tpm_limit`, `rpm_limit`) as read-only indicators and provides editable fields for organization metadata (`name` and `contact_email`) persisted via `PUT /api/v2/iam/organizations/{id}`.
            2. **Task Assignment Creation & Management UI (in `NewExecutionView` and `OrganizationIamSettingsView`)**:
               - In `NewExecutionView` (`@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L319-L756]`), alongside the primary `Start AI Execution` button, render an `OutlinedButton.icon` (**"Assign as Time-Bound Task"**) for `MANAGER`, `ADMIN`, and `ROOT` roles. Clicking it opens the Task Assignment Configuration Dialog pre-populated with the currently selected `workflowId`, `profileId`, and filled background inputs (`locked_inputs`), allowing the sender to select `locked_inputs` vs. `assignee_input_keys` using interactive `FilterChip` widgets (`studio_unified_visual_design_system`), enter a single `assigned_email` OR add a cohort of recipients (1–500) via **Multi-Email Copy-Paste (`InputChip` parser)** or **RFC 4180 `.csv` File Upload (`email,name,language`)**, select `hard_deadline_at` and optional `relative_duration_seconds`, select `result_visibility` (`confirmationOnly` vs. `fullReportAccess` on `AssignmentResultVisibility`), submit `POST /api/v2/execution/executions/assignments` or `POST /api/v2/execution/executions/assignments/batch`, and display a copyable Magic Task Link card (`/task/<token>`) or **"Download Cohort Magic Links (.csv)"** export action.
               - In `OrganizationIamSettingsView`, render the **Task Assignments Management Panel** displaying all organization assignments (with optional cohort grouping by `batch_id`) with pill-shaped status badges and `emailDeliveryStatus` badges, live deadline/activation telemetry, actions to create single or batch assignments, resend task emails (`POST .../assignments/{id}/resend`), extend `hard_deadline_at`, or revoke `PENDING`/`ACTIVATED` links, and a direct button to open the generated execution report (`ExecutionReportRoute`) once `SUBMITTED`/`COMPLETED`.
          - **User Invitations, Role Governance & BYOK Secrets Section (`ADMIN` and `ROOT` only; read-only/hidden for `MANAGER`)**:
            1. Create and revoke single (`InvitationCreateDto`) or batch (`InvitationBatchCreateDto`) general B2B organization invitations into the admin's own organization, update member roles, and trigger instant user session revocation / GDPR soft-deletion.
            2. Configure LLM Provider and MCP Gateway BYOK credentials (using `obscureText: true` input fields, `SecretStorageMode` dropdowns with `isExpanded: true`, and pill badges displaying `configured: true` and `maskedHint: "****abcd"`).
        - Build **View 3 — `TaskAssignmentPortalView`** in `[NEW] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]` mounted at `@TypedGoRoute<TaskAssignmentRoute>(path: '/task/:token')` in `@[client_app_v2/lib/router/router.dart#L55-L227]` wrapped in `AppErrorBoundary` (`DGR009`):
          - Fetches read-only preview metadata via `GET /api/v2/execution/executions/assignments/preview?token=...` without starting the timer.
          - If `requiresAccountCreation` is `true`, renders an inline **Just-In-Time (JIT) User Onboarding + 2FA Enrollment** flow (`name`, `language`, password, and TOTP 2FA setup) calling `POST /api/v2/execution/executions/assignments/onboard`. If the user already exists, prompts login + 2FA challenge (or detects `IDENTITY_MISMATCH` if signed in as a different email and offers a one-click account switch).
          - Displays the task briefing, deadline window, and an explicit **"Start Task"** button calling `POST /api/v2/execution/executions/assignments/{id}/activate`.
          - Once activated, renders a tamper-proof countdown timer synchronized with `server_now_utc` / `remaining_seconds`, displays only the `assignee_input_keys` slots, auto-saves drafts via `PUT .../draft`, and submits the task via `POST .../submit`.
    </action>
  </step>

  <test_contracts>
    <contract name="test_auth_interceptor_token_exchange_and_5_step_logout_positive" category="positive">
      <input>`AuthController.debugMockLogin` or 2FA login followed by `AuthController.signOut(revokeAllSessions: true)`</input>
      <expected>Exchanges credential at `/api/v2/iam/auth/exchange`, schedules 13-minute refresh timer, and on `signOut` cancels timer, posts `/api/v2/iam/auth/logout`, clears token state, invalidates tenant providers, and redirects to `/login`</expected>
    </contract>
    <contract name="test_auth_controller_sign_out_offline_graceful_degradation_error_path" category="error_path">
      <input>`AuthController.signOut()` called when `/api/v2/iam/auth/logout` throws `DioException` (network unreachable or expired JWT)</input>
      <expected>Logs warning via `loggerServiceProvider` and completes local token destruction, provider invalidation, and `/login` redirect inside `finally` without trapping user</expected>
    </contract>
    <contract name="test_user_profile_and_organization_iam_role_segregation_boundary" category="boundary">
      <input>Rendering `ScaffoldWithNav`, `UserProfileSettingsView`, and `OrganizationIamSettingsView` for `VIEWER`, `MEMBER`, `MANAGER`, `ADMIN`, and `ROOT`</input>
      <expected>`VIEWER`/`MEMBER` see Profile and Sign Out but not `/organization`; `MANAGER` edits org `name`/`contact_email` and manages task assignments while BYOK and general user role controls are restricted to `ADMIN` and `ROOT`</expected>
    </contract>
    <contract name="test_task_assignment_portal_view_identity_mismatch_negative" category="negative">
      <input>Authenticated user with `alice@org.com` opens `/task/:token` assigned to `bob@org.com`</input>
      <expected>Displays `IDENTITY_MISMATCH` state with one-click **Sign Out & Switch Account** action without starting task timer</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_flutter_theme_sovereignty.py client_app_v2/lib/features/auth/presentation/login_screen.dart client_app_v2/lib/features/execution/views/new_execution_view.dart client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart
  </validation_gate>
</execution_protocol>
```

