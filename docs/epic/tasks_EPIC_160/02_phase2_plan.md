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

# Phase 2: Session Upgrade, Token Exchange Engine, Headless CLI Governance & Multi-Role Guard

**Overview:** Implement `TokenService.exchange_firebase_token` (`POST /api/v2/iam/auth/exchange`) supporting both interactive MFA-verified Firebase ID Tokens (`firebase.sign_in_second_factor`) and headless CLI / E2E `target_user_id` token exchange, refactor `TokenService.verify_token` (`@[backend_v2/services/auth/token_service.py#L94-L232]`) to execute 0.1 ms RAM-only `Quorum Local JWT` verification with zero database queries and zero `mock-token:` prefix branches, implement server-side `POST /api/v2/iam/auth/logout` and RFC 8693 `POST /api/v2/iam/auth/impersonate`, consolidate duplicate `/auth/users*` routes into `@[backend_v2/api/routers/iam/users.py]`, upgrade `require_role` (`@[backend_v2/api/dependencies.py#L410-L454]`) to accept `Sequence[UserRole] | UserRole`, and migrate headless CLI / E2E runners (`@[scripts/run_e2e_variance_test.py]` and `@[backend_v2/tests/integration/test_integration_real_llm.py]`) to `_get_or_refresh_cli_session` with 13-minute auto-refresh and zero `TD_DICT_GET` warnings.
**Source:** @[docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md]

**Target Files:**
- `[MODIFY] @[backend_v2/services/auth/token_service.py#L32-L232]`
- `[MODIFY] @[backend_v2/services/auth/token_service.py#L94-L232]`
- `[MODIFY] @[backend_v2/services/auth/__init__.py#L59-L202]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L107-L148]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L163-L217]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L220-L234]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L237-L303]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L306-L371]`
- `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L374-L399]`
- `[MODIFY] @[backend_v2/api/routers/iam/users.py#L19-L47]`
- `[MODIFY] @[backend_v2/api/routers/iam/users.py#L71-L89]`
- `[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]`
- `[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]`
- `[MODIFY] @[backend_v2/api/dependencies.py#L410-L454]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py#L875-L986]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py#L1539-L1593]`
- `[MODIFY] @[scripts/run_e2e_variance_test.py#L1596-L2014]`
- `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]`
- `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]`
- `[MODIFY] @[backend_v2/tests/unit/test_token_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/test_user_service.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **2. Session Upgrade, Mandatory 2FA Gate, Headless CLI Exchange, Token Exchange & Logout Engine**<br>`[MODIFY] @[backend_v2/services/auth/token_service.py#L32-L232]`<br>`[MODIFY] @[backend_v2/services/auth/token_service.py#L94-L232]`<br>`[MODIFY] @[backend_v2/services/auth/__init__.py#L59-L202]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L107-L148]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L163-L217]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L220-L234]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L237-L303]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L306-L371]`<br>`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L374-L399]`<br>`[MODIFY] @[backend_v2/api/routers/iam/users.py#L19-L47]`<br>`[MODIFY] @[backend_v2/api/routers/iam/users.py#L71-L89]`<br>`[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]`<br>`[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]`<br>`[MODIFY] @[backend_v2/api/dependencies.py#L410-L454]`<br>`[MODIFY] @[scripts/run_e2e_variance_test.py#L875-L986]`<br>`[MODIFY] @[scripts/run_e2e_variance_test.py#L1539-L1593]`<br>`[MODIFY] @[scripts/run_e2e_variance_test.py#L1596-L2014]`<br>`[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]`<br>`[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]`<br>`[MODIFY] @[backend_v2/tests/unit/test_token_service.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`<br>`[MODIFY] @[backend_v2/tests/unit/test_user_service.py]` | Querying PostgreSQL on every HTTP request inside `verify_token`; `token.startswith("mock-token:")` string prefix branching; raw `Bearer mock-token:` headers and 132 `TD_DICT_GET` warnings in `run_e2e_variance_test.py` and 2 `TD_MODEL_FACTORY` warnings in `test_integration_real_llm.py`; allowing single-factor (password-only) sessions without 2FA; client-only sign-out leaving stateless JWTs valid on the wire for 15 minutes; duplicate `/auth/users*` shadow routes in `auth.py`; single-role `require_role(UserRole)`; raw `"AUTH_TOKEN_MISSING"` string error code; missing RFC 7807 `logger.error` in `require_role`. | `POST /api/v2/iam/auth/exchange` (using created `TokenExchangeRequestDTO` -> `TokenExchangeResponseDTO`): verifies Firebase ID Token with mandatory 2FA (`firebase.sign_in_second_factor` when `require_mfa` on `Settings` is `True`) OR exchanges `target_user_id` for headless CLI / E2E / local dev sessions when `allow_mock_tokens` is `True` or `service_auth_secret` matches, mints 15-minute `Quorum Local JWT` (`sub`, `org`, `role`, `mfa: True`, `jti`, `iat`, `exp`, `type: "access"`), validates all subsequent requests in RAM (< 0.1 ms), revokes logged-out tokens via `POST /api/v2/iam/auth/logout` (using created `LogoutRequestDTO` -> `LogoutResponseDTO`), enforces `require_role(Sequence[UserRole] | UserRole)`, and auto-refreshes CLI tokens via created `CliSessionStateDTO` before minute 13 during long-running E2E polling. | Pruned custom OAuth2 refresh token database tables and parallel M2M token verification pipelines; unified all UI and CLI callers onto `Quorum Local JWT`. | Unit tests asserting 0 DB queries during `verify_token`, Fail-Fast `AuthenticationError` (`ErrorCodes.MFA_REQUIRED`) on single-factor tokens, `ConflictError` (`ErrorCodes.USER_ALREADY_ASSIGNED`) on UID collision, `ErrorCodes.AUTH_TOKEN_EXPIRED` on expired or logged-out (`jti`) signatures, and `0` findings in `audit_technical_debt.py`. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Read the `<required_context_rules>` block, `00-antigravity-core.md`, and `01-python-backend.md` before modifying any files.</action>
    <constraint>Enforce `single_pipeline_invariant_mandate`, `ban_heuristic_identifier_matching`, `single_router_ssot_mandate`, and `anemic_routers` across all auth service and router modifications.</constraint>
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
    <backend>@[backend_v2/services/auth/token_service.py#L32-L232]</backend>
    <backend>@[backend_v2/services/auth/token_service.py#L94-L232]</backend>
    <backend>@[backend_v2/services/auth/__init__.py#L59-L202]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L43-L104]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L107-L148]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L163-L217]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L220-L234]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L237-L303]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L306-L371]</backend>
    <backend>@[backend_v2/api/routers/iam/auth.py#L374-L399]</backend>
    <backend>@[backend_v2/api/routers/iam/users.py#L19-L47]</backend>
    <backend>@[backend_v2/api/routers/iam/users.py#L71-L89]</backend>
    <backend>@[backend_v2/api/routers/iam/organizations.py#L19-L46]</backend>
    <backend>@[backend_v2/api/dependencies.py#L379-L403]</backend>
    <backend>@[backend_v2/api/dependencies.py#L410-L454]</backend>
    <backend>@[scripts/run_e2e_variance_test.py#L875-L986]</backend>
    <backend>@[scripts/run_e2e_variance_test.py#L1539-L1593]</backend>
    <backend>@[scripts/run_e2e_variance_test.py#L1596-L2014]</backend>
    <backend>@[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]</backend>
    <backend>@[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]</backend>
    <backend>@[backend_v2/tests/unit/test_token_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_organization_service.py]</backend>
    <backend>@[backend_v2/tests/unit/test_user_service.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>`TokenService.exchange_firebase_token` (`@[backend_v2/services/auth/token_service.py#L32-L232]`) verifies MFA (`firebase.sign_in_second_factor` when `require_mfa` on `Settings` is `True`) or validates headless CLI `target_user_id` exchange and issues a 15-minute `Quorum Local JWT` with an RFC 7519 `jti` claim.</item>
    <item>`TokenService.verify_token` (`@[backend_v2/services/auth/token_service.py#L94-L232]`) decodes `Quorum Local JWT` tokens in RAM (`< 0.1 ms`) with zero database queries and zero `mock-token:` string prefix checks.</item>
    <item>`POST /api/v2/iam/auth/exchange`, `POST /api/v2/iam/auth/logout`, and RFC 8693 `POST /api/v2/iam/auth/impersonate` are wired in `@[backend_v2/api/routers/iam/auth.py#L43-L104]` and `@[backend_v2/services/auth/__init__.py#L59-L202]`, `verify_user_token` and duplicate `/auth/users*` routes are deleted from `auth.py`, and `require_role` in `@[backend_v2/api/dependencies.py#L410-L454]` accepts `Sequence[UserRole] | UserRole` with RFC 7807 dual-reporting.</item>
    <item>`@[scripts/run_e2e_variance_test.py#L875-L986]`, `@[scripts/run_e2e_variance_test.py#L1539-L1593]`, `@[scripts/run_e2e_variance_test.py#L1596-L2014]`, and `@[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]` use `_get_or_refresh_cli_session` (`CliSessionStateDTO`) with 13-minute auto-refresh and `0` `TD_DICT_GET` or `TD_MODEL_FACTORY` warnings.</item>
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
    <file>@[backend_v2/llm/provider/litellm_provider.py] (Do not modify LLM provider credentials in Phase 2; reserved for Phase 3)</file>
    <file>@[client_app_v2/lib/features/auth/presentation/auth_controller.dart] (Do not modify Flutter client auth controller in Phase 2; reserved for Phase 6)</file>
  </anti_targets>

  <step id="2.1" name="`TokenService` Session Upgrade (`exchange_firebase_token`), Mandatory 2FA Enforcement &amp; 0.1 ms RAM Verification">
    <action>
      - **`[MODIFY] @[backend_v2/services/auth/token_service.py#L32-L232]`, `[MODIFY] @[backend_v2/services/auth/token_service.py#L94-L232]`, `[MODIFY] @[backend_v2/tests/unit/test_token_service.py]`, `[MODIFY] @[backend_v2/tests/unit/test_organization_service.py]`, & `[MODIFY] @[backend_v2/tests/unit/test_user_service.py]`**:
        - Implement `async def exchange_firebase_token(self, payload: TokenExchangeRequestDTO) -> TokenExchangeResponseDTO` (using `TokenExchangeRequestDTO` and `TokenExchangeResponseDTO` created in `@[backend_v2/models/auth.py]`):
          1. **Branch A — Interactive IdP Exchange (`payload.firebase_token is not None`)**:
             - Verify `payload.firebase_token` against Firebase Admin SDK (`await asyncio.to_thread(self.firebase_auth.verify_id_token, payload.firebase_token)`).
             - Enforce **Mandatory Two-Factor Authentication (2FA / NIST SP 800-63B AAL2)**: when `require_mfa` on `Settings` is `True`, verify that the decoded Firebase ID token contains a non-empty `firebase.sign_in_second_factor` claim (`totp`, `phone`, or WebAuthn second factor). If `sign_in_second_factor` is missing or empty, log a structured RFC 7807 error with `ErrorCodes.MFA_REQUIRED.name` and raise `AuthenticationError` (`ErrorCodes.MFA_REQUIRED.value`), refusing to issue a `Quorum Local JWT` to any single-factor session.
             - Lookup the user by `firebase_uid` via `await self.repo.get_by_firebase_uid(firebase_uid)`. If no record matches `firebase_uid`, perform a deterministic first-time pre-provisioned account bind by email ONLY when the Firebase token's `email_verified` claim is `True` and the matched `User` has `user.firebase_uid is None` (if `user.firebase_uid` is already bound to a different UID, log `ErrorCodes.USER_ALREADY_ASSIGNED` and raise `ConflictError`).
          2. **Branch B — Headless CLI, E2E Runner & Local Dev Exchange (`payload.target_user_id is not None`)**:
             - Permit exchanging `payload.target_user_id` ONLY when `allow_mock_tokens` on `Settings` is `True` (`use_firebase_auth=False` on PostgreSQL 19 as configured in `run_local.bat`, or `environment="development"`) OR when `payload.service_auth_secret` matches the environment-injected `service_auth_secret` on `Settings` via `secrets.compare_digest`. If neither condition is satisfied, log `ErrorCodes.PERMISSION_DENIED` and raise `AuthenticationError`.
             - Resolve `user = await self.repo.get_by_id(payload.target_user_id)`.
          3. Reject with `AuthenticationError` (`ErrorCodes.AUTHENTICATION_FAILED` or `ErrorCodes.AUTH_TOKEN_EXPIRED`) if no matching user exists, if `user.deleted_at is not None`, if `not user.is_active`, or if `RevocationCache` (created in Phase 4) holds an active `revoked:usr:{user.id}` lock when `payload.firebase_token` was issued prior to the administrative revocation (NIST SP 800-63B reauthentication guard preventing silent 13-minute background refresh of a revoked session).
          4. Mint a 15-minute `Quorum Local JWT` signed with `jwt_secret_key` from `Settings` containing `sub: user.id` (`usr_<hex32>`), `org: user.organization_id` (`org_<hex32>`), `role: user.role.value`, `email: user.email`, `mfa: True`, `jti: generate_uuid7_str()`, `iat: int(now_epoch)`, `exp: int(now_epoch + expire_seconds)`, and `type: "access"`.
          5. Return `TokenExchangeResponseDTO(access_token=signed_jwt, token_type="bearer", expires_in_seconds=expire_seconds, user=user)`.
        - Refactor `async def verify_token(self, token: str) -> TokenData` (`@[backend_v2/services/auth/token_service.py#L94-L232]`):
          1. Permanently delete all `token.startswith("mock-token:")` string prefix checks and per-request database queries (`ban_heuristic_identifier_matching` & `single_pipeline_invariant_mandate`).
          2. Decode `token` in RAM using `jwt.decode(token, settings_jwt_secret, algorithms=[settings_jwt_algorithm])`.
          3. Validate `sub`, `role`, `org`, `mfa`, `jti`, `act` (extracting `act["sub"]` into `actor_id` when present on RFC 8693 impersonation tokens), `iat`, `exp`, and `type` claims directly into `TokenData(id=..., role=..., organization_id=..., email=..., mfa_verified=..., jti=..., actor_id=..., iat=..., exp=...)` in `< 0.1 ms` with **zero database queries** (rejecting tokens with `ErrorCodes.MFA_REQUIRED` when `require_mfa` on `Settings` is `True` and `mfa` claim is not `True`). On `jwt.ExpiredSignatureError`, log `ErrorCodes.AUTH_TOKEN_EXPIRED` and raise `AuthenticationError`.
    </action>
  </step>

  <step id="2.2" name="Token Exchange &amp; Logout Router Endpoints, IAM Router SSOT Consolidation &amp; Multi-Role Dependency Guard">
    <action>
      - **`[MODIFY] @[backend_v2/api/routers/iam/auth.py#L43-L104]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L107-L148]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L163-L217]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L220-L234]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L237-L303]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L306-L371]`, `[MODIFY] @[backend_v2/api/routers/iam/auth.py#L374-L399]`, `[MODIFY] @[backend_v2/services/auth/__init__.py#L59-L202]`, `[MODIFY] @[backend_v2/api/routers/iam/users.py#L19-L47]`, `[MODIFY] @[backend_v2/api/routers/iam/users.py#L71-L89]`, & `[MODIFY] @[backend_v2/api/routers/iam/organizations.py#L19-L46]`**:
        - Replace the legacy `@router.post("/verify", response_model=LoginResponse)` endpoint (`verify_user_token` and demolished `LoginResponse` created/removed in Phase 1 at `@[backend_v2/api/routers/iam/auth.py#L43-L104]`) with `@router.post("/exchange", response_model=TokenExchangeResponseDTO)` delegating strictly to `await auth_service.exchange_firebase_token(payload)`.
        - Add `@router.post("/logout", response_model=LogoutResponseDTO)` (using `LogoutRequestDTO` and `LogoutResponseDTO` defined in `@[backend_v2/models/auth.py]`) in `@[backend_v2/api/routers/iam/auth.py#L43-L104]` delegating to `await auth_service.logout(current_user, payload)` in `@[backend_v2/services/auth/__init__.py#L59-L202]`:
          1. Computes the remaining token lifetime $\text{remaining\_ttl} = \max(1, \min(900, (\text{current\_user.exp} - \text{int}(\text{time.time}()))))$ and writes `revoked:jti:{current_user.jti}` via `await self.revocation_cache.revoke_token_jti(current_user.jti, ttl_seconds=remaining_ttl)` so the logged-out JWT is immediately invalidated on the wire while allowing the user to immediately sign back in with a newly minted `jti`.
          2. When `payload.revoke_all_sessions` is `True` ("Sign out from all devices"), additionally calls `await self.revocation_cache.revoke_user_sessions(current_user.id, ttl_seconds=900)` and, when `use_firebase` is enabled and the user has a bound `firebase_uid`, invokes `await asyncio.to_thread(self.token_service.firebase_auth.revoke_refresh_tokens, user.firebase_uid)` inside a bounded `asyncio.timeout`.
          3. Records a structured `USER_LOGGED_OUT` security audit event via `await self.audit_service.log_event(...)` and returns `LogoutResponseDTO(status="logged_out", revoked_jti=current_user.jti, all_sessions_revoked=payload.revoke_all_sessions)`.
        - Delete the four duplicate shadow `/auth/users*` routes (`create_user` at `@[backend_v2/api/routers/iam/auth.py#L163-L217]`, `list_users` at `@[backend_v2/api/routers/iam/auth.py#L220-L234]`, `delete_user` at `@[backend_v2/api/routers/iam/auth.py#L237-L303]`, and `update_user` at `@[backend_v2/api/routers/iam/auth.py#L306-L371]`) from `@[backend_v2/api/routers/iam/auth.py]` and expose `POST /api/v2/iam/users` (`UserCreate` -> `User`) and `PUT /api/v2/iam/users/{id}` (`UserUpdate` -> `User`) exclusively in canonical `@[backend_v2/api/routers/iam/users.py#L71-L89]` (`single_router_ssot_mandate`).
        - Eliminate direct `await auth_service.repo.get_by_id(...)` repository calls from `impersonate_user` (`@[backend_v2/api/routers/iam/auth.py#L107-L148]`) and `get_my_profile` (`@[backend_v2/api/routers/iam/auth.py#L374-L399]`), delegating both endpoints strictly through `AuthService` methods (`anemic_routers`), and harden `AuthService.impersonate_user(initiator: TokenData, payload: ImpersonationRequest) -> ImpersonationResponse` (`@[backend_v2/services/auth/__init__.py#L59-L202]` and `TokenService.create_impersonation_token` in `@[backend_v2/services/auth/token_service.py#L32-L232]`) to enforce RFC 8693 Section 4.1 Break-Glass Impersonation: mint a 15-minute `Quorum Local JWT` embedding full stateless claims (`sub: target.id`, `org: target.organization_id`, `role: target.role.value`, `email: target.email`, `mfa: True`, `jti: generate_uuid7_str()`, and `act: {"sub": initiator.id}`) and log a structured `USER_IMPERSONATION_STARTED` audit event recording `actor_id` (`initiator.id`), `target_id` (`target.id`), and `reason` (`payload.reason`).
        - Remove the catch-all `try ... except Exception` blocks in `get_all_organizations` (`@[backend_v2/api/routers/iam/organizations.py#L19-L46]`) and `get_all_users` (`@[backend_v2/api/routers/iam/users.py#L19-L47]`) that previously swallowed `PermissionDeniedError` (`403`) into `500 Internal Server Error` (`the_duct_tape_ban` & `universal_fail_fast`).
      - **`[MODIFY] @[backend_v2/api/dependencies.py#L379-L403]` & `[MODIFY] @[backend_v2/api/dependencies.py#L410-L454]`**:
        - Replace the raw string literal `"AUTH_TOKEN_MISSING"` in `get_current_user_from_header` (`@[backend_v2/api/dependencies.py#L379-L403]`) with `ErrorCodes.AUTHENTICATION_FAILED.value`.
        - Update `require_role(allowed_roles: Sequence[UserRole] | UserRole)` in `@[backend_v2/api/dependencies.py#L410-L454]` so routers can declare multi-role guards (`ADMIN` and `MANAGER` members of `UserRole`) while preserving `ROOT` superuser access, logging a structured RFC 7807 `logger.error` with `ErrorCodes.PERMISSION_DENIED.name`, and raising `PermissionDeniedError` with `"error_code": ErrorCodes.PERMISSION_DENIED.value` in `details` (`QGR009`) when the caller's role is not in `allowed_roles`.
    </action>
  </step>

  <step id="2.3" name="Headless CLI, E2E Variance Runner (`run_e2e_variance_test.py`) &amp; Background Worker Session Governance">
    <action>
      - **`[MODIFY] @[scripts/run_e2e_variance_test.py#L875-L986]`, `[MODIFY] @[scripts/run_e2e_variance_test.py#L1539-L1593]`, `[MODIFY] @[scripts/run_e2e_variance_test.py#L1596-L2014]`, `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]`, & `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]`**:
        - Replace all hardcoded `"Authorization": f"Bearer mock-token:{settings.mock_admin_user_id}"` headers in `trigger_execution` (`@[scripts/run_e2e_variance_test.py#L875-L986]`), `poll_database_for_execution` (`@[scripts/run_e2e_variance_test.py#L1539-L1593]`), `run_variance_test` (`@[scripts/run_e2e_variance_test.py#L1596-L2014]`), and `test_real_llm_pdf_execution` (`@[backend_v2/tests/integration/test_integration_real_llm.py#L283-L332]` and `@[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]`) with a deterministic, strictly typed CLI Token Exchange & Auto-Refresh helper (`_get_or_refresh_cli_session(base_url: str, target_user_id: PrefixedUUID7, current_session: CliSessionStateDTO | None = None) -> CliSessionStateDTO`, using `CliSessionStateDTO` defined in `@[backend_v2/models/auth.py]`), remediate the 2 `TD_MODEL_FACTORY` warnings in `@[backend_v2/tests/integration/test_integration_real_llm.py#L810-L1073]`, and remediate all `TD_DICT_GET` dictionary `.get()` calls in `@[scripts/run_e2e_variance_test.py#L875-L986]`, `@[scripts/run_e2e_variance_test.py#L1539-L1593]`, and `@[scripts/run_e2e_variance_test.py#L1596-L2014]` so `audit_technical_debt.py --plan docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md --strict` passes with `0` findings:
          1. **Initial Token Exchange (Zero `or` Fallbacks)**: Requires an explicit `target_user_id: PrefixedUUID7` passed from `settings.mock_admin_user_id` at the caller boundary (`anti_lazy_fallback_mandate`), calls `POST {base_url}/iam/auth/exchange` with `TokenExchangeRequestDTO(target_user_id=target_user_id, service_auth_secret=configured_service_secret)`, validates the response via `TokenExchangeResponseDTO.model_validate(response.json())`, and returns an immutable `CliSessionStateDTO(access_token=dto.access_token, expires_at_monotonic=time.monotonic() + dto.expires_in_seconds - 120.0, user_id=dto.user.id)`.
          2. **Automatic 13-Minute Refresh in Long-Running Polling Loops**: Checks `current_session is None or time.monotonic() >= current_session.expires_at_monotonic`. Because multi-step production E2E variance runs (`poll_database_for_execution` in `@[scripts/run_e2e_variance_test.py#L1539-L1593]`) execute for 20–120 minutes while a `Quorum Local JWT` expires in 15 minutes, the polling loop automatically re-invokes `POST {base_url}/iam/auth/exchange` whenever `< 120 seconds` remain before token expiry, preventing mid-run `401 AUTH_TOKEN_EXPIRED` failures.
    </action>
  </step>

  <test_contracts>
    <contract name="test_exchange_firebase_token_mfa_verified_positive" category="positive">
      <input>Valid `TokenExchangeRequestDTO` with `firebase_token` containing verified `firebase.sign_in_second_factor="totp"` for an active `User`</input>
      <expected>Returns `TokenExchangeResponseDTO` with 15-minute signed `Quorum Local JWT` carrying `sub`, `org`, `role`, `mfa: True`, `jti`, `iat`, `exp`</expected>
    </contract>
    <contract name="test_exchange_firebase_token_missing_mfa_negative" category="negative">
      <input>`TokenExchangeRequestDTO` with `firebase_token` lacking `firebase.sign_in_second_factor` when `require_mfa` on `Settings` is `True`</input>
      <expected>Logs `ErrorCodes.MFA_REQUIRED.name` and raises `AuthenticationError` (`ErrorCodes.MFA_REQUIRED`)</expected>
    </contract>
    <contract name="test_exchange_firebase_token_uid_collision_negative" category="negative">
      <input>Firebase token whose verified email matches a `User` already bound to a different `firebase_uid`</input>
      <expected>Logs `ErrorCodes.USER_ALREADY_ASSIGNED.name` and raises `ConflictError` (`409 Conflict`)</expected>
    </contract>
    <contract name="test_exchange_headless_user_token_unauthorized_negative" category="negative">
      <input>`TokenExchangeRequestDTO(target_user_id=...)` when `allow_mock_tokens=False` and `service_auth_secret` is missing or mismatched</input>
      <expected>Logs `ErrorCodes.PERMISSION_DENIED.name` and raises `AuthenticationError` (`401 Unauthorized`)</expected>
    </contract>
    <contract name="test_verify_token_ram_decode_zero_db_queries_positive" category="positive">
      <input>Valid signed `Quorum Local JWT` passed to `TokenService.verify_token`</input>
      <expected>Returns `TokenData` in RAM with 0 calls to `repo.get_by_id`</expected>
    </contract>
    <contract name="test_verify_token_expired_or_mock_prefix_negative" category="negative">
      <input>Expired `Quorum Local JWT` or legacy `"mock-token:..."` string passed to `TokenService.verify_token`</input>
      <expected>Raises `AuthenticationError` (`ErrorCodes.AUTH_TOKEN_EXPIRED` or `ErrorCodes.AUTHENTICATION_FAILED`)</expected>
    </contract>
    <contract name="test_require_role_multi_role_sequence_boundary" category="boundary">
      <input>`require_role([UserRole.ADMIN, UserRole.MANAGER])` invoked by `ROOT`, `ADMIN`, `MANAGER`, `MEMBER`, and `VIEWER`</input>
      <expected>Permits `ROOT`, `ADMIN`, and `MANAGER`; raises `PermissionDeniedError` (`ErrorCodes.PERMISSION_DENIED`) for `MEMBER` and `VIEWER`</expected>
    </contract>
  </test_contracts>

  <validation_gate>
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/auth/ backend_v2/api/routers/iam/ backend_v2/api/dependencies.py scripts/run_e2e_variance_test.py --test --ast-strict
    $env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_technical_debt.py --plan docs/epic/EPIC_160_B2B_SaaS_IAM_and_Enterprise_Hardening.md --strict
  </validation_gate>
</execution_protocol>
```

