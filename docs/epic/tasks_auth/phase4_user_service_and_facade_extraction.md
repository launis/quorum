# Phase 4: User Service and Facade Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract user lifecycle management, role hierarchy enforcement, Last Admin Protection, and root bootstrapping from `@[backend_v2/services/auth.py#L237-L514]`, `@[backend_v2/services/auth.py#L594-L805]`, and `@[backend_v2/services/auth.py#L825-L989]` into `@[backend_v2/services/auth/user_service.py]` [NEW]. Assemble the sovereign `AuthService` facade in `@[backend_v2/services/auth/__init__.py]` [NEW] orchestrating `TokenService`, `OrganizationService`, and `UserService`, while retaining a thin Strangler Fig proxy in `@[backend_v2/services/auth.py]` to preserve 100% backward compatibility during the transition.

```xml
<execution_protocol level="phase4_extraction">
  <context>
    <target_file action="MODIFY">@[backend_v2/services/auth.py]</target_file>
    <extracted_user_service action="NEW">[NEW] @[backend_v2/services/auth/user_service.py]</extracted_user_service>
    <extracted_facade action="NEW">[NEW] @[backend_v2/services/auth/__init__.py]</extracted_facade>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/constants.py]</dependencies>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/repositories.py]</dependencies>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/token_service.py]</dependencies>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/organization_service.py]</dependencies>
    <test_file action="MODIFY">@[backend_v2/tests/unit/test_auth.py]</test_file>
  </context>

  <test_contracts>
    <contract id="TC-P4-01" category="regression">
      <name>test_create_user_root_creator_success</name>
      <input>creator_id with UserRole.ROOT, valid UserCreate payload with role=UserRole.ADMIN</input>
      <expected_output>Creates user in repo (and Firebase if enabled), logs audit event, and returns User instance</expected_output>
    </contract>
    <contract id="TC-P4-02" category="regression">
      <name>test_create_user_admin_creator_same_org_success</name>
      <input>creator_id with UserRole.ADMIN in org_123, UserCreate payload with organization_id="org_123" and role=UserRole.MEMBER</input>
      <expected_output>Creates user in repo and returns User instance</expected_output>
    </contract>
    <contract id="TC-P4-03" category="error_path">
      <name>test_create_user_admin_creator_foreign_org_raises_permission_denied</name>
      <input>creator with org_123, UserCreate targeting org_456</input>
      <expected_output>Raises PermissionDeniedError("Cannot create users in other organizations.")</expected_output>
    </contract>
    <contract id="TC-P4-04" category="error_path">
      <name>test_create_user_admin_creating_root_raises_permission_denied</name>
      <input>creator with UserRole.ADMIN, UserCreate with role=UserRole.ROOT</input>
      <expected_output>Raises PermissionDeniedError("Admins cannot create Roots.")</expected_output>
    </contract>
    <contract id="TC-P4-05" category="error_path">
      <name>test_create_user_manager_creating_user_raises_permission_denied</name>
      <input>creator with UserRole.MANAGER, UserCreate payload</input>
      <expected_output>Raises PermissionDeniedError("Managers are Technical Leads and cannot manage users. Ask an Admin.")</expected_output>
    </contract>
    <contract id="TC-P4-06" category="error_path">
      <name>test_create_user_member_creating_user_raises_permission_denied</name>
      <input>creator with UserRole.MEMBER, UserCreate payload</input>
      <expected_output>Raises PermissionDeniedError("This user role cannot create users")</expected_output>
    </contract>
    <contract id="TC-P4-07" category="boundary">
      <name>test_create_user_non_existent_creator_raises_app_exception_404</name>
      <input>creator_id="usr_missing" not in repo</input>
      <expected_output>Raises AppException with status_code=404 and ErrorCodes.RESOURCE_NOT_FOUND</expected_output>
    </contract>
    <contract id="TC-P4-08" category="error_path">
      <name>test_create_user_non_existent_target_org_raises_app_exception_404</name>
      <input>valid creator, target org_id not found in org_repo and not system org</input>
      <expected_output>Raises AppException with status_code=404 and ErrorCodes.VALIDATION_FAILED</expected_output>
    </contract>
    <contract id="TC-P4-09" category="error_path">
      <name>test_create_user_root_role_in_non_system_org_raises_permission_denied</name>
      <input>creator with UserRole.ROOT, user_data.role=UserRole.ROOT with organization_id="org_other"</input>
      <expected_output>Raises PermissionDeniedError("Root users can only be created within the System Organization.")</expected_output>
    </contract>
    <contract id="TC-P4-10" category="regression">
      <name>test_get_user_root_initiator_any_user_success</name>
      <input>initiator with UserRole.ROOT, target_id="usr_any"</input>
      <expected_output>Returns requested User instance</expected_output>
    </contract>
    <contract id="TC-P4-11" category="regression">
      <name>test_get_user_self_fetch_success</name>
      <input>initiator with UserRole.MEMBER and id="usr_self", target_id="usr_self"</input>
      <expected_output>Returns requested User instance</expected_output>
    </contract>
    <contract id="TC-P4-12" category="regression">
      <name>test_get_user_admin_same_org_success</name>
      <input>initiator with UserRole.ADMIN in org_1, target user in org_1</input>
      <expected_output>Returns requested User instance</expected_output>
    </contract>
    <contract id="TC-P4-13" category="error_path">
      <name>test_get_user_foreign_user_raises_permission_denied</name>
      <input>initiator with UserRole.MEMBER in org_1, target user in org_2</input>
      <expected_output>Raises PermissionDeniedError("You do not have permission to view this user.")</expected_output>
    </contract>
    <contract id="TC-P4-14" category="boundary">
      <name>test_get_user_not_found_raises_resource_not_found</name>
      <input>initiator with UserRole.ROOT, target_id="usr_missing"</input>
      <expected_output>Raises ResourceNotFoundError(resource_type="user", resource_id="usr_missing")</expected_output>
    </contract>
    <contract id="TC-P4-15" category="regression">
      <name>test_list_users_root_initiator_returns_all_users</name>
      <input>initiator with UserRole.ROOT</input>
      <expected_output>Returns full list of users across all organizations</expected_output>
    </contract>
    <contract id="TC-P4-16" category="regression">
      <name>test_list_users_tenant_initiator_returns_own_org_users_only</name>
      <input>initiator with organization_id="org_test"</input>
      <expected_output>Returns filtered list of users where organization_id=="org_test"</expected_output>
    </contract>
    <contract id="TC-P4-17" category="regression">
      <name>test_get_users_by_organization_returns_matching_users</name>
      <input>organization_id="org_1"</input>
      <expected_output>Returns list of users from user_repo.get_by_organization</expected_output>
    </contract>
    <contract id="TC-P4-18" category="regression">
      <name>test_update_user_root_initiator_success</name>
      <input>initiator with UserRole.ROOT, updates=UserUpdate(name="New Name")</input>
      <expected_output>Updates user in repo, logs audit event, and returns refreshed User</expected_output>
    </contract>
    <contract id="TC-P4-19" category="regression">
      <name>test_update_user_self_update_non_role_fields_success</name>
      <input>initiator_id==target_id, updates=UserUpdate(language=SystemLocale.FI)</input>
      <expected_output>Updates user successfully</expected_output>
    </contract>
    <contract id="TC-P4-20" category="error_path">
      <name>test_update_user_self_update_role_raises_permission_denied</name>
      <input>initiator_id==target_id with UserRole.MEMBER, updates=UserUpdate(role=UserRole.ADMIN)</input>
      <expected_output>Raises PermissionDeniedError("Users cannot change their own role.")</expected_output>
    </contract>
    <contract id="TC-P4-21" category="error_path">
      <name>test_update_user_admin_foreign_org_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN in org_1, target user in org_2</input>
      <expected_output>Raises PermissionDeniedError("Cannot update users from other organizations")</expected_output>
    </contract>
    <contract id="TC-P4-22" category="error_path">
      <name>test_update_user_non_root_transferring_org_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, updates=UserUpdate(organization_id="org_other")</input>
      <expected_output>Raises PermissionDeniedError("Only ROOT can transfer users between organizations.")</expected_output>
    </contract>
    <contract id="TC-P4-23" category="error_path">
      <name>test_update_user_demoting_last_admin_raises_conflict_error</name>
      <input>initiator with UserRole.ROOT, target is sole ADMIN in org, updates=UserUpdate(role=UserRole.MEMBER)</input>
      <expected_output>Raises ConflictError with LAST_ADMIN_PROTECTION message and ErrorCodes.CONFLICT_ERROR</expected_output>
    </contract>
    <contract id="TC-P4-24" category="regression">
      <name>test_update_user_role_root_initiator_success</name>
      <input>initiator with UserRole.ROOT, target user, new_role=UserRole.ADMIN</input>
      <expected_output>Updates user role, logs audit event, and returns refreshed User</expected_output>
    </contract>
    <contract id="TC-P4-25" category="error_path">
      <name>test_update_user_role_lower_hierarchy_modifying_higher_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, target user with UserRole.ROOT</input>
      <expected_output>Raises PermissionDeniedError("Cannot modify users with higher or equal privileges.")</expected_output>
    </contract>
    <contract id="TC-P4-26" category="error_path">
      <name>test_update_user_role_promoting_above_own_role_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, new_role=UserRole.ROOT</input>
      <expected_output>Raises PermissionDeniedError("Cannot promote user to a role higher than your own.")</expected_output>
    </contract>
    <contract id="TC-P4-27" category="error_path">
      <name>test_update_user_role_admin_modifying_foreign_org_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN in org_1, target user in org_2</input>
      <expected_output>Raises PermissionDeniedError("Cannot manage users in other organizations.")</expected_output>
    </contract>
    <contract id="TC-P4-28" category="error_path">
      <name>test_update_user_role_demoting_last_admin_raises_conflict_error</name>
      <input>target is sole ADMIN of org, new_role=UserRole.MEMBER</input>
      <expected_output>Raises ConflictError with ErrorCodes.CONFLICT_ERROR and reason="LAST_ADMIN_PROTECTION"</expected_output>
    </contract>
    <contract id="TC-P4-29" category="regression">
      <name>test_delete_user_root_initiator_regular_user_success</name>
      <input>initiator with UserRole.ROOT, target is standard MEMBER user</input>
      <expected_output>Deletes user from repo (and Firebase if enabled), logs audit event, and returns True</expected_output>
    </contract>
    <contract id="TC-P4-30" category="regression">
      <name>test_delete_user_admin_same_org_success</name>
      <input>initiator with UserRole.ADMIN in org_1, target MEMBER in org_1</input>
      <expected_output>Deletes user and returns True</expected_output>
    </contract>
    <contract id="TC-P4-31" category="error_path">
      <name>test_delete_user_admin_foreign_org_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN in org_1, target user in org_2</input>
      <expected_output>Raises PermissionDeniedError("Cannot delete users from other organizations")</expected_output>
    </contract>
    <contract id="TC-P4-32" category="error_path">
      <name>test_delete_user_root_account_protection_raises_permission_denied</name>
      <input>initiator with UserRole.ROOT, target_id=SYSTEM_ROOT_USER_ID (or LEGACY_ROOT_MASTER_ID)</input>
      <expected_output>Raises PermissionDeniedError("The primary Root account cannot be deleted.")</expected_output>
    </contract>
    <contract id="TC-P4-33" category="error_path">
      <name>test_delete_user_last_admin_protection_raises_conflict_error</name>
      <input>target is sole ADMIN in organization</input>
      <expected_output>Raises ConflictError with ErrorCodes.CONFLICT_ERROR and reason="LAST_ADMIN_PROTECTION"</expected_output>
    </contract>
    <contract id="TC-P4-34" category="boundary">
      <name>test_delete_user_not_found_raises_app_exception_404</name>
      <input>initiator with UserRole.ROOT, target_id="usr_missing"</input>
      <expected_output>Raises AppException with status_code=404 and ErrorCodes.RESOURCE_NOT_FOUND</expected_output>
    </contract>
    <contract id="TC-P4-35" category="regression">
      <name>test_ensure_root_user_creates_system_org_if_missing</name>
      <input>system org missing from org_repo, root user present in repo</input>
      <expected_output>Creates system organization in org_repo and returns root user</expected_output>
    </contract>
    <contract id="TC-P4-36" category="regression">
      <name>test_ensure_root_user_success_when_root_exists</name>
      <input>system org and root user exist with correct organization_id</input>
      <expected_output>Returns root User instance</expected_output>
    </contract>
    <contract id="TC-P4-37" category="regression">
      <name>test_ensure_root_user_heals_organization_id_if_drifted</name>
      <input>root user exists but with organization_id drifted from system org</input>
      <expected_output>Updates root user organization_id to ROOT_SYSTEM and returns refreshed root User</expected_output>
    </contract>
    <contract id="TC-P4-38" category="error_path">
      <name>test_ensure_root_user_missing_from_db_raises_app_exception_500</name>
      <input>root user missing from user repo</input>
      <expected_output>Raises AppException with status_code=500 and ErrorCodes.CONFIGURATION_ERROR</expected_output>
    </contract>
    <contract id="TC-P4-39" category="regression">
      <name>test_auth_service_facade_delegates_all_operations</name>
      <input>AuthService facade initialized with mock repositories</input>
      <expected_output>All token, organization, and user operations delegate cleanly to respective subservices</expected_output>
    </contract>
  </test_contracts>

  <step id="1" name="CREATE_USER_SERVICE_MODULE">
    <action>Create module `@[backend_v2/services/auth/user_service.py]` [NEW].</action>
    <action>Import required dependencies:
      - `asyncio`, `logging`, `uuid`, `datetime`, `timezone`, `Any`
      - `AppException`, `ConflictError`, `ErrorCodes`, `PermissionDeniedError`, `ResourceNotFoundError` from `backend_v2.exceptions`
      - `Organization`, `SubscriptionStatus`, `SystemOrganizations`, `TokenData`, `User`, `UserCreate`, `UserRole`, `UserUpdate` from `backend_v2.models.auth`
      - `SystemLocale` from `backend_v2.models.enums`
      - `LEGACY_ROOT_MASTER_ID`, `LEGACY_SYSTEM_ORG_ID`, `LEGACY_SYSTEM_ROOT_USER_ID`, `SYSTEM_ROOT_USER_ID` from `backend_v2.services.auth.constants`
      - `OrganizationRepository`, `UserRepository` from `backend_v2.services.auth.repositories`
    </action>
    <action>Define class `UserService` [NEW] with constructor:
      ```python
      def __init__(
          self,
          user_repo: UserRepository,
          org_repo: OrganizationRepository,
          audit_service: Any = None,
          use_firebase: bool = False,
          firebase_auth: Any = None,
      ) -> None:
          pass
      ```
    </action>
    <action>Extract exact business logic from `@[backend_v2/services/auth.py]`:
      - `create_user(creator_id: str, user_data: UserCreate) -> User` (Lines 237-251)
      - `_create_user_internal(creator_id: str, user_data: UserCreate, force_org_id: str | None = None) -> User` (Lines 253-379)
      - `_enforce_hierarchy(creator: User, target_role: UserRole) -> None` (Lines 381-405)
      - `_count_org_admins(org_id: str) -> int` (Lines 407-420)
      - `get_users_by_organization(organization_id: str) -> list[User]` (Lines 422-431)
      - `delete_user(initiator_id: str, target_id: str) -> bool` (Lines 433-514)
      - `update_user(initiator_id: str, target_id: str, updates: UserUpdate) -> User` (Lines 594-685)
      - `update_user_role(initiator_id: str, target_id: str, new_role: UserRole) -> User` (Lines 687-786)
      - `list_users(initiator: TokenData) -> list[User]` (Lines 790-805)
      - `get_user(initiator: TokenData, target_id: str) -> User` (Lines 825-854)
      - `ensure_root_user(email: str = "root@example.com") -> User` (Lines 918-989)
    </action>
    <action>Preserve RFC 7807 structured dual-logging, Last Admin Protection, and audit logging verbatim.</action>
  </step>

  <step id="2" name="CREATE_SOVEREIGN_AUTH_FACADE_INIT">
    <action>Create module `@[backend_v2/services/auth/__init__.py]` [NEW].</action>
    <action>Import subservices and repositories:
      - `constants` symbols (`JWT_ALGORITHM`, `JWT_SECRET`, `LEGACY_ROOT_MASTER_ID`, `LEGACY_SYSTEM_ORG_ID`, `LEGACY_SYSTEM_ROOT_USER_ID`, `SYSTEM_ROOT_USER_ID`)
      - `OrganizationRepository`, `UserRepository` from `.repositories`
      - `TokenService` from `.token_service`
      - `OrganizationService` from `.organization_service`
      - `UserService` from `.user_service`
    </action>
    <action>Implement sovereign `AuthService` facade:
      - Accepts `(repo: IIdentityRepository, use_firebase: bool = False, audit_service: Any = None)`.
      - Instantiates `self.repo = UserRepository(repo)` and `self.org_repo = OrganizationRepository(repo)`.
      - Instantiates `self.token_service = TokenService(...)`.
      - Instantiates `self.user_service = UserService(...)`.
      - Instantiates `self.org_service = OrganizationService(..., create_user_fn=self.user_service._create_user_internal)`.
      - Delegates properties (`use_firebase`, `firebase_auth`, `_initialized_firebase`) to `token_service`.
      - Delegates token methods (`_init_firebase`, `create_impersonation_token`, `verify_token`) to `token_service`.
      - Delegates organization methods (`create_organization`, `delete_organization`, `list_organizations`, `get_organization`, `update_organization`) to `org_service`.
      - Delegates user methods (`create_user`, `_create_user_internal`, `_enforce_hierarchy`, `_count_org_admins`, `get_users_by_organization`, `delete_user`, `update_user`, `update_user_role`, `list_users`, `get_user`, `ensure_root_user`) to `user_service`.
      - Exposes explicit `__all__ = ["AuthService", "OrganizationRepository", "OrganizationService", "TokenService", "UserRepository", "UserService", "JWT_SECRET", "JWT_ALGORITHM", "SYSTEM_ROOT_USER_ID", "LEGACY_SYSTEM_ROOT_USER_ID", "LEGACY_SYSTEM_ORG_ID", "LEGACY_ROOT_MASTER_ID"]`.
    </action>
  </step>

  <step id="3" name="CONVERT_LEGACY_AUTH_FILE_TO_STRANGLER_FIG_PROXY">
    <action>In `@[backend_v2/services/auth.py]`:
      - Replace monolithic implementation with thin Strangler Fig proxy importing from `backend_v2.services.auth`.
      - Add `@deprecated` warning notification on module import or proxy access.
      - Explicitly re-export all symbols via `as Symbol` and `__all__` to satisfy `mypy --strict`.
    </action>
  </step>

  <step id="4" name="VALIDATE_AND_EXPAND_UNIT_TESTS">
    <action>In `@[backend_v2/tests/unit/test_auth.py]`:
      - Implement regression and boundary test cases for contracts `TC-P4-01` through `TC-P4-39`.
      - Test both direct `UserService` / `AuthService` facade execution and legacy proxy execution.
    </action>
    <action>Run quality gate: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`.</action>
    <action>Verify all 70+ tests pass with zero regressions and line coverage on `user_service.py` is &gt;90%.</action>
  </step>
</execution_protocol>
```
