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

# EPIC 164 - Phase 3: Frontend `MockLoginPanel` & `MOCK_*_USER_ID` Eradication and Authentic Email/Password Login Parity

**Overview:** Eradicate `MockLoginPanel` (`@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L158-L161]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L367-L474]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`), `allowMockTokens` (`@[client_app_v2/lib/core/environment/env.dart#L62-L65]`), `_requireMockUserId` (`@[client_app_v2/lib/core/environment/env.dart#L45-L54]`), and `mockAdminUserId` / `mockRootUserId` / `mockAnalystUserId` / `mockMemberUserId` / `mockViewerUserId` (`#L68`, `#L70`, `@[client_app_v2/lib/core/environment/env.dart#L72-L73]`, `@[client_app_v2/lib/core/environment/env.dart#L75-L76]`, `@[client_app_v2/lib/core/environment/env.dart#L78-L79]`, `@[client_app_v2/lib/core/environment/env.dart#L29-L79]`, `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`, and `@[client_app_v2/.env#L3-L7]`). Eradicate `_activeDebugUserId` (`#L48`), `debugMockLogin` (`@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L154-L170]`), and `debugUserId` from `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`, and eradicate `debugSignInWithMockToken` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L291]`) and `debugTargetUserId` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L315]`) from `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]`. Refactor `AuthRepository.signInWithEmailAndPassword` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L128-L141]`) so MFA enforcement is delegated strictly to the backend `POST /api/v2/iam/auth/exchange` response (`MFA_REQUIRED`), enabling authentic Email + Password login on Windows Desktop when `REQUIRE_MFA=false` while preserving TOTP enrollment when `REQUIRE_MFA=true`.

**Source:** `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`

**Target Files:**
- `[MODIFY] @[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`
- `[MODIFY] @[client_app_v2/lib/core/environment/env.dart#L25-L80]`
- `[MODIFY] @[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`
- `[MODIFY] @[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]`
- `[MODIFY] @[client_app_v2/.env]`
- `[MODIFY] @[client_app_v2/test/features/auth/presentation/login_screen_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/core/environment/env_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`
- `[MODIFY] @[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`, `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]` & `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]` | Rendering `MockLoginPanel` in development, reading `MOCK_*_USER_ID` from `.env`, and blocking Desktop Email/Password login via client-side `getEnrolledFactors()` when `REQUIRE_MFA=false`. | Delete `MockLoginPanel`, `debugMockLogin`, `debugSignInWithMockToken`, and `MOCK_*_USER_ID`; delegate MFA enforcement in `signInWithEmailAndPassword` to backend `exchangeToken(idToken)` response (`MFA_REQUIRED`). | Zero client-side `REQUIRE_MFA` environment duplication; backend `POST /api/v2/iam/auth/exchange` is the sole MFA policy authority. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/features/auth/presentation/login_screen_test.dart --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md]`, `@[docs/epic/EPIC_164_audit_report.md]`, `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`, `@[client_app_v2/lib/core/environment/env.dart#L25-L80]`, `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`, and `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]`.</action>
    <action>Look forward: Verify Step 3.1 deletes `MockLoginPanel` and all `MOCK_*_USER_ID` / `allowMockTokens` getters from `LoginScreen`, `Env`, and `client_app_v2/.env`, and Step 3.2 removes `debugMockLogin` and `debugSignInWithMockToken` and delegates MFA enforcement in `AuthRepository.signInWithEmailAndPassword` to `exchangeToken(idToken)`.</action>
    <constraint invariant="single_pipeline_invariant_mandate">All interactive UI authentication MUST flow through Email + Password (`signInWithEmailAndPassword`) and backend `POST /api/v2/iam/auth/exchange` with zero debug mock login bypass paths.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_164_unified_secret_seeding_and_authentic_iam_parity.md] and @[docs/epic/EPIC_164_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_164/03_phase3_plan.md] @[docs/epic/EPIC_164_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]</frontend>
    <frontend>@[client_app_v2/lib/core/environment/env.dart#L25-L80]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]</frontend>
    <frontend>@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]</frontend>
    <frontend>@[client_app_v2/.env]</frontend>
    <frontend>@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/core/environment/env_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]</frontend>
    <frontend>@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`MockLoginPanel` is deleted from `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`, and `_requireMockUserId`, `allowMockTokens`, `mockAdminUserId`, `mockRootUserId`, `mockAnalystUserId`, `mockMemberUserId`, and `mockViewerUserId` are deleted from `@[client_app_v2/lib/core/environment/env.dart#L25-L80]` and `@[client_app_v2/.env]`.</item>
    <item>`_activeDebugUserId`, `debugMockLogin`, and `debugUserId` are deleted from `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`, and `debugSignInWithMockToken` and `debugTargetUserId` are deleted from `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L315]`.</item>
    <item>`AuthRepository.signInWithEmailAndPassword` in `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]` calls `exchangeToken(idToken)` directly after Firebase sign-in and invokes `_prepareEnrollmentForUser(firebaseUser, fallbackEmail: email)` when `exchangeToken` returns `Left(error)` with `error.errorCode == 'MFA_REQUIRED'`.</item>
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
    <anti_target>Do NOT duplicate `REQUIRE_MFA` in `client_app_v2/.env` or `Env`; backend `POST /api/v2/iam/auth/exchange` is the sole authority for MFA enforcement (`universal_ssot_and_normalization_mandate`).</anti_target>
    <anti_target>Do NOT use `SizedBox.shrink()` to hide `MockLoginPanel` (`sized_box_shrink_ban`); physically delete `MockLoginPanel`.</anti_target>
  </anti_targets>

  <step id="3.1" name="Eradicate MockLoginPanel, allowMockTokens &amp; mock*UserId from LoginScreen, Env &amp; client_app_v2/.env">
    <demolish>
      Delete `class MockLoginPanel` (`@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L367-L474]`), `if (Env.allowMockTokens) ...` (`@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L158-L161]`), `_requireMockUserId` (`@[client_app_v2/lib/core/environment/env.dart#L45-L54]`), `allowMockTokens` (`@[client_app_v2/lib/core/environment/env.dart#L62-L65]`), and `mockAdminUserId`, `mockRootUserId`, `mockAnalystUserId`, `mockMemberUserId`, `mockViewerUserId` (`#L68`, `#L70`, `@[client_app_v2/lib/core/environment/env.dart#L72-L73]`, `@[client_app_v2/lib/core/environment/env.dart#L75-L76]`, `@[client_app_v2/lib/core/environment/env.dart#L78-L79]`, `@[client_app_v2/lib/core/environment/env.dart#L29-L79]`).
    </demolish>
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/auth/presentation/login_screen.dart#L155-L474]`: Remove `if (Env.allowMockTokens) ...[ AppSpacing.h24, const MockLoginPanel() ]`, delete `class MockLoginPanel`, and remove unused imports.</action>
    <action>2. `[MODIFY]` `@[client_app_v2/lib/core/environment/env.dart#L25-L80]` and `@[client_app_v2/.env]`: Delete `_idValidator`, `_requireMockUserId`, `allowMockTokens`, `mockAdminUserId`, `mockRootUserId`, `mockAnalystUserId`, `mockMemberUserId`, and `mockViewerUserId` from `Env`, and remove `MOCK_ADMIN_USER_ID`, `MOCK_ROOT_USER_ID`, `MOCK_ANALYST_USER_ID`, `MOCK_MEMBER_USER_ID`, and `MOCK_VIEWER_USER_ID` (`@[client_app_v2/.env#L3-L7]`) from `@[client_app_v2/.env]`.</action>
    <action>3. `[MODIFY]` `@[client_app_v2/test/features/auth/presentation/login_screen_test.dart]` and `@[client_app_v2/test/unit/core/environment/env_test.dart]`: Remove obsolete `MockLoginPanel` and `mock*UserId` test cases and verify `Env.apiUrl` and `Env.environment` Fail-Fast validation and `LoginScreen` Email + Password sign-in rendering.</action>
    <constraint invariant="the_no_legacy_mandate">Zero `MockLoginPanel` or `mock*UserId` symbols may remain in `client_app_v2/lib/` or `client_app_v2/test/`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/unit/core/environment/env_test.dart</audit_command>
  </step>

  <step id="3.2" name="Eradicate debugMockLogin &amp; debugSignInWithMockToken and Delegate MFA Enforcement in signInWithEmailAndPassword to Backend">
    <demolish>
      Delete `_activeDebugUserId` (`#L48`), `debugMockLogin` (`@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L154-L170]`), `debugSignInWithMockToken` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L291]`), and the unconditional pre-exchange `firebaseUser.multiFactor.getEnrolledFactors()` block (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L128-L141]`).
    </demolish>
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/auth/presentation/auth_controller.dart#L45-L305]`: Delete `_activeDebugUserId`, delete `debugMockLogin`, and remove the `debugUserId` parameter from `applyTokenExchangeResponse` (defined on `AuthController`), `_applyAuthenticatedSession`, `_scheduleSilentRefresh`, and `performSilentRefresh`.</action>
    <action>2. `[MODIFY]` `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L315]`: Delete `debugSignInWithMockToken` and remove `debugTargetUserId` from `refreshSession` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L279-L315]`). In `signInWithEmailAndPassword` (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L110-L176]`), replace the unconditional client-side `getEnrolledFactors()` block (`@[client_app_v2/lib/features/auth/data/auth_repository.dart#L128-L141]`) so that after `_firebaseAuth.signInWithEmailAndPassword(email: email, password: password)` succeeds, it obtains `final idToken = await firebaseUser.getIdToken()`, invokes `final exchangeResult = await exchangeToken(idToken)`, and if `exchangeResult` returns `Left(error)` with `error.errorCode == 'MFA_REQUIRED'`, calls `await _prepareEnrollmentForUser(firebaseUser, fallbackEmail: email)` before returning `Left(error)`.</action>
    <action>3. `[MODIFY]` `@[client_app_v2/test/unit/features/auth/data/auth_repository_test.dart]`, `@[client_app_v2/test/unit/features/auth/presentation/auth_controller_test.dart]`, and `@[client_app_v2/test/unit/core/network/auth_interceptor_test.dart]`: Update unit tests to remove `debugMockLogin` / `debugSignInWithMockToken` tests and verify `signInWithEmailAndPassword` both when `exchangeToken` succeeds (`200 OK` when backend `REQUIRE_MFA=false` or 2FA claim present) and when `exchangeToken` returns `403 MFA_REQUIRED` (triggering `_prepareEnrollmentForUser`).</action>
    <constraint invariant="universal_ssot_and_normalization_mandate">`AuthRepository.signInWithEmailAndPassword` MUST delegate MFA policy evaluation to `exchangeToken(idToken)` rather than hardcoding client-side factor checks before contacting the backend.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/unit/features/auth/ --build</audit_command>
  </step>

  <test_contracts>
    <test name="test_sign_in_with_email_and_password_succeeds_when_backend_require_mfa_false" category="positive">
      <input>`AuthRepository.signInWithEmailAndPassword` called with valid email and password when Firebase returns a valid `idToken` and backend `/iam/auth/exchange` returns `200 OK` with `TokenExchangeResponseDto`</input>
      <expected>Returns `Right(TokenExchangeResponseDto)` without calling `multiFactor.getSession()` or blocking on `getEnrolledFactors()`</expected>
    </test>
    <test name="test_sign_in_with_email_and_password_prepares_totp_enrollment_on_backend_mfa_required" category="negative">
      <input>`AuthRepository.signInWithEmailAndPassword` called when backend `/iam/auth/exchange` returns `403 Forbidden` with `error_code: 'MFA_REQUIRED'`</input>
      <expected>Invokes `_prepareEnrollmentForUser`, populates `pendingMfaState` with `MfaRequirementType.enrollment`, and returns `Left(AppException)` with `errorCode == 'MFA_REQUIRED'`</expected>
    </test>
    <test name="test_env_throws_app_exception_when_required_api_url_or_environment_missing" category="boundary">
      <input>`Env.apiUrl` or `Env.environment` accessed when `.env` is missing `API_URL` or `ENVIRONMENT`</input>
      <expected>Throws `AppException` validation error immediately (Fail-Fast)</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Phase 3 Flutter quality gate: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/features/auth/presentation/login_screen_test.dart --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/unit/features/auth/`.</action>
  </validation_gate>
</execution_protocol>
```
