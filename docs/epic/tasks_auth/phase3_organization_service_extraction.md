# Phase 3: Organization Service Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract tenant organization management logic (CRUD, system organization protection, tenant isolation, and cascading user deletion) from `@[backend_v2/services/auth.py#L173-L235]`, `@[backend_v2/services/auth.py#L516-L592]`, and `@[backend_v2/services/auth.py#L807-L916]` into `@[backend_v2/services/auth/organization_service.py]` [NEW], establishing an isolated, testable `OrganizationService` [NEW] component while preserving 100% backward compatibility via `AuthService` delegation.

```xml
<execution_protocol level="phase3_extraction">
  <context>
    <target_file action="MODIFY">@[backend_v2/services/auth.py]</target_file>
    <extracted_module action="NEW">[NEW] @[backend_v2/services/auth/organization_service.py]</extracted_module>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/constants.py]</dependencies>
    <dependencies action="EXISTING">[NEW] @[backend_v2/services/auth/repositories.py]</dependencies>
    <test_file action="MODIFY">@[backend_v2/tests/unit/test_auth.py]</test_file>
  </context>

  <test_contracts>
    <contract id="TC-P3-01" category="regression">
      <name>test_create_organization_root_initiator_success</name>
      <input>initiator with UserRole.ROOT, valid OrganizationCreate payload</input>
      <expected_output>Returns Organization instance with generated org_id and creates org admin user via create_user_fn</expected_output>
    </contract>
    <contract id="TC-P3-02" category="error_path">
      <name>test_create_organization_non_root_initiator_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, valid OrganizationCreate payload</input>
      <expected_output>Raises PermissionDeniedError("Only ROOT can create organizations.")</expected_output>
    </contract>
    <contract id="TC-P3-03" category="regression">
      <name>test_create_organization_logs_audit_event_when_audit_service_configured</name>
      <input>initiator with UserRole.ROOT, mock audit_service provided</input>
      <expected_output>Calls audit_service.log_event with action="ORG_CREATED" and org details</expected_output>
    </contract>
    <contract id="TC-P3-04" category="regression">
      <name>test_get_organization_root_initiator_any_org_success</name>
      <input>initiator with UserRole.ROOT, target org_id existing in repository</input>
      <expected_output>Returns target Organization instance</expected_output>
    </contract>
    <contract id="TC-P3-05" category="regression">
      <name>test_get_organization_same_org_member_success</name>
      <input>initiator with UserRole.MEMBER and organization_id="org_123", target org_id="org_123"</input>
      <expected_output>Returns target Organization instance</expected_output>
    </contract>
    <contract id="TC-P3-06" category="error_path">
      <name>test_get_organization_foreign_org_member_raises_permission_denied</name>
      <input>initiator with UserRole.MEMBER and organization_id="org_other", target org_id="org_123"</input>
      <expected_output>Raises PermissionDeniedError("You do not have permission to view this organization.")</expected_output>
    </contract>
    <contract id="TC-P3-07" category="boundary">
      <name>test_get_organization_non_existent_org_raises_resource_not_found</name>
      <input>initiator with UserRole.ROOT, target org_id="org_missing" not in repository</input>
      <expected_output>Raises ResourceNotFoundError(resource_type="organization", resource_id="org_missing")</expected_output>
    </contract>
    <contract id="TC-P3-08" category="regression">
      <name>test_list_organizations_root_initiator_returns_all_orgs</name>
      <input>initiator with UserRole.ROOT, repo containing multiple organizations</input>
      <expected_output>Returns list containing all organizations from repository</expected_output>
    </contract>
    <contract id="TC-P3-09" category="regression">
      <name>test_list_organizations_tenant_initiator_returns_own_org_only</name>
      <input>initiator with UserRole.ADMIN and organization_id="org_mine"</input>
      <expected_output>Returns list containing only [own_org]</expected_output>
    </contract>
    <contract id="TC-P3-10" category="boundary">
      <name>test_list_organizations_tenant_initiator_no_org_id_returns_empty_list</name>
      <input>initiator with UserRole.MEMBER and organization_id=None</input>
      <expected_output>Returns empty list []</expected_output>
    </contract>
    <contract id="TC-P3-11" category="regression">
      <name>test_update_organization_root_initiator_with_update_dto_success</name>
      <input>initiator with UserRole.ROOT, existing org_id, data=OrganizationUpdateDTO(name="New Org Name")</input>
      <expected_output>Updates organization via repo and returns refreshed Organization</expected_output>
    </contract>
    <contract id="TC-P3-12" category="regression">
      <name>test_update_organization_root_initiator_with_create_dto_success</name>
      <input>initiator with UserRole.ROOT, existing org_id, data=OrganizationCreate(name="New Org Name", admin_email="a@b.com", admin_name="Admin", admin_password="pass")</input>
      <expected_output>Converts to OrganizationUpdateDTO, updates organization, and returns refreshed Organization</expected_output>
    </contract>
    <contract id="TC-P3-13" category="error_path">
      <name>test_update_organization_non_root_initiator_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, data=OrganizationUpdateDTO(name="Name")</input>
      <expected_output>Raises PermissionDeniedError("Only ROOT can update organizations.")</expected_output>
    </contract>
    <contract id="TC-P3-14" category="boundary">
      <name>test_update_organization_non_existent_org_raises_resource_not_found</name>
      <input>initiator with UserRole.ROOT, org_id="org_missing"</input>
      <expected_output>Raises ResourceNotFoundError(resource_type="organization", resource_id="org_missing")</expected_output>
    </contract>
    <contract id="TC-P3-15" category="regression">
      <name>test_delete_organization_root_empty_org_success</name>
      <input>initiator with UserRole.ROOT, target org_id having 0 users</input>
      <expected_output>Deletes organization from org_repo, logs audit event, and returns None</expected_output>
    </contract>
    <contract id="TC-P3-16" category="error_path">
      <name>test_delete_organization_non_root_raises_permission_denied</name>
      <input>initiator with UserRole.ADMIN, target org_id</input>
      <expected_output>Raises PermissionDeniedError("Only ROOT can delete organizations.")</expected_output>
    </contract>
    <contract id="TC-P3-17" category="error_path">
      <name>test_delete_organization_system_org_raises_permission_denied</name>
      <input>initiator with UserRole.ROOT, target_org_id="system" (or LEGACY_SYSTEM_ORG_ID)</input>
      <expected_output>Raises PermissionDeniedError("CRITICAL: The 'system' organization is protected and CANNOT be deleted.")</expected_output>
    </contract>
    <contract id="TC-P3-18" category="error_path">
      <name>test_delete_organization_non_empty_without_force_raises_conflict_error</name>
      <input>initiator with UserRole.ROOT, target org with 2 users, force=False</input>
      <expected_output>Raises ConflictError with ErrorCodes.CONFLICT_ERROR and reason="ORG_NOT_EMPTY"</expected_output>
    </contract>
    <contract id="TC-P3-19" category="regression">
      <name>test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit</name>
      <input>initiator with UserRole.ROOT, target org with 2 users, force=True</input>
      <expected_output>Deletes all users from user_repo (and firebase if enabled), deletes org, logs audit event with users_deleted=2</expected_output>
    </contract>
  </test_contracts>

  <step id="1" name="CREATE_ORGANIZATION_SERVICE_MODULE">
    <action>Create module `@[backend_v2/services/auth/organization_service.py]` [NEW].</action>
    <action>Import required dependencies:
      - `asyncio`, `logging`, `uuid`, `datetime`, `timezone`, `Callable`, `Coroutine`, `Any`
      - `AppException`, `ConflictError`, `ErrorCodes`, `PermissionDeniedError`, `ResourceNotFoundError` from `backend_v2.exceptions`
      - `Organization`, `OrganizationCreate`, `OrganizationUpdateDTO`, `SubscriptionStatus`, `SystemOrganizations`, `TokenData`, `User`, `UserCreate`, `UserRole` from `backend_v2.models.auth`
      - `SystemLocale` from `backend_v2.models.enums`
      - `LEGACY_SYSTEM_ORG_ID` from `backend_v2.services.auth.constants`
      - `OrganizationRepository`, `UserRepository` from `backend_v2.services.auth.repositories`
    </action>
    <action>Define class `OrganizationService` [NEW] with constructor:
      ```python
      def __init__(
          self,
          org_repo: OrganizationRepository,
          user_repo: UserRepository,
          audit_service: Any = None,
          use_firebase: bool = False,
          firebase_auth: Any = None,
          create_user_fn: Callable[[str, UserCreate, str | None], Coroutine[Any, Any, User]] | None = None,
      ) -> None:
          pass
      ```
    </action>
    <action>Extract exact business logic from `@[backend_v2/services/auth.py]`:
      - `create_organization(initiator: TokenData, org_create: OrganizationCreate) -> Organization` (Lines 173-235)
      - `delete_organization(initiator: TokenData, target_org_id: str, force: bool = False) -> None` (Lines 516-592)
      - `list_organizations(initiator: TokenData) -> list[Organization]` (Lines 807-823)
      - `get_organization(initiator: TokenData, org_id: str) -> Organization` (Lines 856-880)
      - `update_organization(initiator: TokenData, org_id: str, data: OrganizationUpdateDTO | OrganizationCreate) -> Organization` (Lines 882-916)
    </action>
    <action>Preserve RFC 7807 structured dual-logging, audit logging, and security validations verbatim.</action>
  </step>

  <step id="2" name="DELEGATE_AND_REEXPORT_IN_AUTH_SERVICE">
    <action>In `@[backend_v2/services/auth.py]`:
      - Import `OrganizationService` from `backend_v2.services.auth.organization_service`.
      - Re-export `OrganizationService` via redundant alias `OrganizationService as OrganizationService`.
      - Register `"OrganizationService"` in `__all__`.
      - In `AuthService.__init__`, instantiate `self.org_service = OrganizationService(org_repo=self.org_repo, user_repo=self.repo, audit_service=self.audit_service, use_firebase=use_firebase, firebase_auth=self.token_service.firebase_auth, create_user_fn=self._create_user_internal)`.
      - Update `AuthService.create_organization` to delegate to `self.org_service.create_organization(initiator=initiator, org_create=org_create)`.
      - Update `AuthService.delete_organization` to delegate to `self.org_service.delete_organization(initiator=initiator, target_org_id=target_org_id, force=force)`.
      - Update `AuthService.list_organizations` to delegate to `self.org_service.list_organizations(initiator=initiator)`.
      - Update `AuthService.get_organization` to delegate to `self.org_service.get_organization(initiator=initiator, org_id=org_id)`.
      - Update `AuthService.update_organization` to delegate to `self.org_service.update_organization(initiator=initiator, org_id=org_id, data=data)`.
    </action>
  </step>

  <step id="3" name="VALIDATE_AND_EXPAND_UNIT_TESTS">
    <action>In `@[backend_v2/tests/unit/test_auth.py]`:
      - Implement regression and boundary test cases for contracts `TC-P3-01` through `TC-P3-19`.
      - Test both direct `OrganizationService` execution and delegated `AuthService` execution.
    </action>
    <action>Run quality gate: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`.</action>
    <action>Verify all 55+ tests pass with zero regressions and line coverage on `organization_service.py` is &gt;90%.</action>
  </step>
</execution_protocol>
```
