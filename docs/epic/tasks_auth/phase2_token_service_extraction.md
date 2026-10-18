# Phase 2: Token Service Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract authentication token verification, Firebase Admin SDK integration, and JWT impersonation token generation from `@[backend_v2/services/auth.py]` into `@[backend_v2/services/auth/token_service.py]` [NEW], establishing an isolated, testable `TokenService` [NEW] component while preserving 100% backward compatibility via `AuthService` delegation.

```xml
<execution_protocol level="phase2_extraction">
  <context>
    <target_file action="MODIFY">@[backend_v2/services/auth.py]</target_file>
    <extracted_module action="NEW">[NEW] @[backend_v2/services/auth/token_service.py]</extracted_module>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/constants.py]</dependencies>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/repositories.py]</dependencies>
    <test_file action="MODIFY">@[backend_v2/tests/unit/test_auth.py]</test_file>
  </context>

  <test_contracts>
    <contract id="TC-P2-01" category="regression">
      <name>test_create_impersonation_token_generates_signed_jwt</name>
      <input>target_id="usr_target123", duration_seconds=3600</input>
      <expected_output>Valid signed JWT containing sub="usr_target123", type="impersonation"</expected_output>
    </contract>
    <contract id="TC-P2-02" category="regression">
      <name>test_verify_token_impersonation_token_success</name>
      <input>Valid impersonation JWT token for existing user in UserRepository</input>
      <expected_output>Returns TokenData populated with user ID, role, email, organization_id</expected_output>
    </contract>
    <contract id="TC-P2-03" category="error_path">
      <name>test_verify_token_impersonation_missing_sub_raises_authentication_error</name>
      <input>Signed JWT with missing sub claim</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.AUTHENTICATION_FAILED</expected_output>
    </contract>
    <contract id="TC-P2-04" category="error_path">
      <name>test_verify_token_impersonation_user_not_found_raises_authentication_error</name>
      <input>Signed JWT with sub claim pointing to non-existent user ID</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.AUTH_TOKEN_EXPIRED</expected_output>
    </contract>
    <contract id="TC-P2-05" category="boundary">
      <name>test_verify_token_expired_jwt_raises_authentication_error</name>
      <input>JWT token with exp timestamp in the past</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.AUTH_TOKEN_EXPIRED</expected_output>
    </contract>
    <contract id="TC-P2-06" category="error_path">
      <name>test_verify_token_invalid_jwt_raises_authentication_error</name>
      <input>Malformed or tampered JWT token string</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.AUTHENTICATION_FAILED</expected_output>
    </contract>
    <contract id="TC-P2-07" category="error_path">
      <name>test_verify_token_mock_token_in_production_forbidden_raises_authentication_error</name>
      <input>token="mock-token:usr_test", allow_mock_tokens is False</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.PERMISSION_DENIED</expected_output>
    </contract>
    <contract id="TC-P2-08" category="error_path">
      <name>test_verify_token_mock_token_user_not_found_raises_authentication_error</name>
      <input>token="mock-token:usr_missing", allow_mock_tokens is True</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.PERMISSION_DENIED</expected_output>
    </contract>
    <contract id="TC-P2-09" category="regression">
      <name>test_verify_token_mock_token_success_returns_tokendata</name>
      <input>token="mock-token:usr_exists", allow_mock_tokens is True, user in repo</input>
      <expected_output>Returns TokenData matching repository user profile</expected_output>
    </contract>
    <contract id="TC-P2-10" category="regression">
      <name>test_verify_token_firebase_token_success_returns_tokendata</name>
      <input>Valid Firebase token decoded by mock firebase_auth with existing user in repo</input>
      <expected_output>Returns TokenData matching database user profile</expected_output>
    </contract>
    <contract id="TC-P2-11" category="regression">
      <name>test_verify_token_firebase_auto_registration_success</name>
      <input>Valid Firebase token for user not present in local repo, email present</input>
      <expected_output>Creates new User with UserRole.MEMBER and returns TokenData</expected_output>
    </contract>
    <contract id="TC-P2-12" category="error_path">
      <name>test_verify_token_firebase_missing_email_raises_authentication_error</name>
      <input>Valid Firebase token for user not present in local repo, email absent</input>
      <expected_output>Raises AuthenticationError with ErrorCodes.AUTHENTICATION_FAILED</expected_output>
    </contract>
  </test_contracts>

  <step id="1" name="CREATE_TOKEN_SERVICE_MODULE">
    <action>Create module `@[backend_v2/services/auth/token_service.py]` [NEW].</action>
    <action>Import required dependencies:
      - `importlib.util`, `logging`, `time`, `datetime`, `timezone`, `jwt`
      - `firebase_admin` optional import via `importlib.util.find_spec`
      - `AuthenticationError`, `ErrorCodes` from `backend_v2.exceptions`
      - `TokenData`, `User`, `UserRole` from `backend_v2.models.auth`
      - `SystemLocale` from `backend_v2.models.enums`
      - `get_settings` from `backend_v2.settings`
      - `JWT_ALGORITHM`, `JWT_SECRET` from `backend_v2.services.auth.constants`
      - `UserRepository` from `backend_v2.services.auth.repositories`
    </action>
    <action>Define class `TokenService` [NEW] with constructor accepting `repo: UserRepository` and `use_firebase: bool = False`.</action>
    <action>Move `_init_firebase` from `@[backend_v2/services/auth.py#L249-L261]` into `TokenService` [NEW].</action>
    <action>Move `create_impersonation_token` from `@[backend_v2/services/auth.py#L263-L281]` into `TokenService` [NEW].</action>
    <action>Move `verify_token` from `@[backend_v2/services/auth.py#L283-L415]` into `TokenService` [NEW].</action>
    <action>Declare explicit `__all__ = ["TokenService"]` in `@[backend_v2/services/auth/token_service.py]` [NEW].</action>
  </step>

  <step id="2" name="DELEGATE_FROM_AUTH_SERVICE">
    <action>In `@[backend_v2/services/auth.py]`:
      - Import `TokenService` from `backend_v2.services.auth.token_service`.
      - In `AuthService.__init__`, instantiate `self.token_service = TokenService(repo=self.repo, use_firebase=self.use_firebase)`.
      - Delegate `AuthService.create_impersonation_token` to `self.token_service.create_impersonation_token`.
      - Delegate `AuthService.verify_token` to `self.token_service.verify_token`.
    </action>
    <action>Preserve method docstrings and typing annotations verbatim on `AuthService`.</action>
  </step>

  <step id="3" name="VERIFY_QUALITY_GATE">
    <action>Execute baseline test suite: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`</action>
    <action>Execute backend audit loop on auth package: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test`</action>
    <action>Verify all 30 baseline tests pass with zero regressions.</action>
  </step>
</execution_protocol>
```
