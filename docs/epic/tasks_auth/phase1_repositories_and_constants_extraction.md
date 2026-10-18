# Phase 1: Repositories and Constants Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract leaf-level identity constants and repository wrapper classes from `@[backend_v2/services/auth.py]` into isolated modules `@[backend_v2/services/auth/constants.py]` [NEW] and `@[backend_v2/services/auth/repositories.py]` [NEW] following Bottom-Up Topological Leaf-First Order, preserving 100% backward compatibility via explicit re-exports in `auth.py`.

```xml
<execution_protocol level="phase1_extraction">
  <context>
    <target_file action="MODIFY">@[backend_v2/services/auth.py]</target_file>
    <extracted_constants action="NEW">[NEW] @[backend_v2/services/auth/constants.py]</extracted_constants>
    <extracted_repositories action="NEW">[NEW] @[backend_v2/services/auth/repositories.py]</extracted_repositories>
    <test_file action="MODIFY">@[backend_v2/tests/unit/test_auth.py]</test_file>
  </context>

  <test_contracts>
    <contract id="TC-P1-01" category="regression">
      <name>test_organization_repository_get_by_id_found_returns_organization</name>
      <input>org_id="org_123", mock_repo returns valid organization dictionary</input>
      <expected_output>Instance of Organization matching org_id</expected_output>
    </contract>
    <contract id="TC-P1-02" category="boundary">
      <name>test_organization_repository_get_by_id_not_found_returns_none</name>
      <input>org_id="org_missing", mock_repo returns None</input>
      <expected_output>None</expected_output>
    </contract>
    <contract id="TC-P1-03" category="regression">
      <name>test_organization_repository_create_persists_and_returns</name>
      <input>Organization instance with valid fields</input>
      <expected_output>Calls mock_repo.create_organization and returns input organization</expected_output>
    </contract>
    <contract id="TC-P1-04" category="regression">
      <name>test_organization_repository_list_all_returns_list</name>
      <input>mock_repo.list_organizations returns list of Organization instances</input>
      <expected_output>Exact list of Organization instances returned</expected_output>
    </contract>
    <contract id="TC-P1-05" category="regression">
      <name>test_user_repository_get_by_id_found_returns_user</name>
      <input>user_id="usr_abc", mock_repo returns User instance</input>
      <expected_output>Instance of User matching user_id</expected_output>
    </contract>
    <contract id="TC-P1-06" category="boundary">
      <name>test_user_repository_get_by_id_not_found_returns_none</name>
      <input>user_id="usr_none", mock_repo returns None</input>
      <expected_output>None</expected_output>
    </contract>
    <contract id="TC-P1-07" category="regression">
      <name>test_user_repository_get_by_email_found_returns_user</name>
      <input>email="admin@example.com", mock_repo returns User instance</input>
      <expected_output>Instance of User matching email</expected_output>
    </contract>
    <contract id="TC-P1-08" category="boundary">
      <name>test_user_repository_get_by_email_not_found_returns_none</name>
      <input>email="unknown@example.com", mock_repo returns None</input>
      <expected_output>None</expected_output>
    </contract>
    <contract id="TC-P1-09" category="error_path">
      <name>test_user_repository_create_duplicate_id_raises_app_exception</name>
      <input>User instance with ID already existing in mock_repo</input>
      <expected_output>Raises AppException with status_code=409 and error_code=CONFLICT_ERROR</expected_output>
    </contract>
    <contract id="TC-P1-10" category="boundary">
      <name>test_user_repository_update_not_found_returns_none</name>
      <input>user_id="usr_missing", updates=UserUpdate(name="New Name")</input>
      <expected_output>None</expected_output>
    </contract>
    <contract id="TC-P1-11" category="regression">
      <name>test_user_repository_update_success_returns_updated_user</name>
      <input>user_id="usr_exists", updates=UserUpdate(name="Updated")</input>
      <expected_output>Returns refreshed User instance after mock_repo.update_user</expected_output>
    </contract>
    <contract id="TC-P1-12" category="regression">
      <name>test_user_repository_delete_calls_underlying_repo</name>
      <input>user_id="usr_delete"</input>
      <expected_output>Returns boolean result from mock_repo.delete_user</expected_output>
    </contract>
    <contract id="TC-P1-13" category="regression">
      <name>test_user_repository_get_by_organization_filters_and_validates</name>
      <input>org_id="org_test", mock_repo returns raw user dictionary list</input>
      <expected_output>List of User instances validated via User.model_validate</expected_output>
    </contract>
  </test_contracts>

  <step id="1" name="CREATE_CONSTANTS_MODULE">
    <action>Create directory `backend_v2/services/auth/` if not present.</action>
    <action>Create module `@[backend_v2/services/auth/constants.py]` [NEW].</action>
    <action>Extract lines 46-53 from `@[backend_v2/services/auth.py]` into `constants.py`:
      - `JWT_SECRET = "cognitive-quorum-internal-secret-change-me"`
      - `JWT_ALGORITHM = "HS256"`
      - `SYSTEM_ROOT_USER_ID = "usr_a3fd6b3d77c748f4"`
      - `LEGACY_SYSTEM_ROOT_USER_ID = "10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b"`
      - `LEGACY_SYSTEM_ORG_ID = "436d84de-c526-43b7-93ef-634912be0d2f"`
      - `LEGACY_ROOT_MASTER_ID = "root_master"`
    </action>
    <action>Declare explicit `__all__` list in `@[backend_v2/services/auth/constants.py]` [NEW].</action>
  </step>

  <step id="2" name="CREATE_REPOSITORIES_MODULE">
    <action>Create module `@[backend_v2/services/auth/repositories.py]` [NEW].</action>
    <action>Import required dependencies from interfaces, exceptions, models, and constants:
      - `IIdentityRepository` from `backend_v2.database.interfaces`
      - `AppException`, `ErrorCodes` from `backend_v2.exceptions`
      - `Organization`, `User`, `UserUpdate` from `backend_v2.models.auth`
    </action>
    <action>Extract `OrganizationRepository` from `@[backend_v2/services/auth.py#L73-L116]` into `@[backend_v2/services/auth/repositories.py]` [NEW].</action>
    <action>Extract `UserRepository` from `@[backend_v2/services/auth.py#L122-L223]` into `@[backend_v2/services/auth/repositories.py]` [NEW].</action>
    <action>Declare explicit `__all__ = ["OrganizationRepository", "UserRepository"]` in `@[backend_v2/services/auth/repositories.py]` [NEW].</action>
  </step>

  <step id="3" name="REWIRE_AUTH_FACADE_PROXY">
    <action>In `@[backend_v2/services/auth.py]`, replace inline implementations of `OrganizationRepository` and `UserRepository` with explicit imports:
      ```python
      from backend_v2.services.auth.constants import (
          JWT_ALGORITHM as JWT_ALGORITHM,
          JWT_SECRET as JWT_SECRET,
          LEGACY_ROOT_MASTER_ID as LEGACY_ROOT_MASTER_ID,
          LEGACY_SYSTEM_ORG_ID as LEGACY_SYSTEM_ORG_ID,
          LEGACY_SYSTEM_ROOT_USER_ID as LEGACY_SYSTEM_ROOT_USER_ID,
          SYSTEM_ROOT_USER_ID as SYSTEM_ROOT_USER_ID,
      )
      from backend_v2.services.auth.repositories import (
          OrganizationRepository as OrganizationRepository,
          UserRepository as UserRepository,
      )
      ```
    </action>
    <action>Retain `__all__` in `@[backend_v2/services/auth.py]` to guarantee 100% strict re-export compliance under MyPy.</action>
  </step>

  <step id="4" name="VERIFY_QUALITY_GATE">
    <action>Execute baseline test suite: `uv run pytest backend_v2/tests/unit/test_auth.py --cov=backend_v2.services.auth`</action>
    <action>Execute backend audit loop on extracted targets: `uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test`</action>
    <action>Verify all 30 baseline tests pass with zero regressions.</action>
  </step>
</execution_protocol>
```
