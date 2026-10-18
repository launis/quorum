# Symbol Migration Map: auth.py Decomposition

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Target God File Metadata
- **Source File:** `@[backend_v2/services/auth.py]`
- **Physical Line Count:** 1234 lines
- **AST Symbol Count:** 30 extracted symbols
- **Test Baseline:** 30/30 passed (100% pass rate) in 7.31s
- **Line Coverage Baseline:** 93% (394 statements, 29 missed)
- **Target Decomposition Directory:** `backend_v2/services/auth/`

## Target Architecture (Domain-Driven Bounded Contexts)
The monolithic service is decomposed into 5 single-responsibility submodules and 1 unifying facade under `backend_v2/services/auth/`:

1. `@[backend_v2/services/auth/constants.py]` [NEW]: System and legacy identifiers, JWT token parameters.
2. `@[backend_v2/services/auth/repositories.py]` [NEW]: Low-level data access wrapper repositories (`OrganizationRepository`, `UserRepository`).
3. `@[backend_v2/services/auth/token_service.py]` [NEW]: Authentication token lifecycle, PyJWT decoding, Firebase Admin SDK integration, and dev mock token verification (`TokenService` [NEW]).
4. `@[backend_v2/services/auth/organization_service.py]` [NEW]: Multi-tenant organization CRUD, system org protection, and cascading org deletion (`OrganizationService` [NEW]).
5. `@[backend_v2/services/auth/user_service.py]` [NEW]: User lifecycle management, role hierarchy validation, Last Admin Protection, and root bootstrapping (`UserService` [NEW]).
6. `@[backend_v2/services/auth/__init__.py]` [NEW]: Sovereign `AuthService` facade implementing 100% signature-preserving delegation to subservices.

## Exhaustive Symbol Inventory

| Symbol Name | Symbol Type | Current AST Boundary | Target Destination | Bounded Domain Context |
| :--- | :--- | :--- | :--- | :--- |
| `JWT_SECRET` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | Token / Security Configuration |
| `JWT_ALGORITHM` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | Token / Security Configuration |
| `SYSTEM_ROOT_USER_ID` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | System Root Identity |
| `LEGACY_SYSTEM_ROOT_USER_ID` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | Legacy System Identity |
| `LEGACY_SYSTEM_ORG_ID` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | Legacy Organization Identity |
| `LEGACY_ROOT_MASTER_ID` | Constant | `@[backend_v2/services/auth.py]` | `@[backend_v2/services/auth/constants.py]` [NEW] | Legacy Master Identity |
| `OrganizationRepository` | ClassDef | `@[backend_v2/services/auth.py#L73-L116]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `OrganizationRepository.__init__` | FunctionDef | `@[backend_v2/services/auth.py#L76-L82]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `OrganizationRepository.get_by_id` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L84-L96]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `OrganizationRepository.create` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L98-L108]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `OrganizationRepository.list_all` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L110-L116]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository` | ClassDef | `@[backend_v2/services/auth.py#L122-L223]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.__init__` | FunctionDef | `@[backend_v2/services/auth.py#L125-L131]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.get_by_id` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L133-L142]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.get_by_email` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L144-L153]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.create` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L155-L175]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.update` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L177-L193]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.list_all` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L195-L201]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.delete` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L203-L212]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `UserRepository.get_by_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L214-L223]` | `@[backend_v2/services/auth/repositories.py]` [NEW] | Repository Wrapper Layer |
| `AuthService._init_firebase` | FunctionDef | `@[backend_v2/services/auth.py#L249-L261]` | `@[backend_v2/services/auth/token_service.py]` [NEW] | Authentication Token Subsystem |
| `AuthService.create_impersonation_token` | FunctionDef | `@[backend_v2/services/auth.py#L263-L281]` | `@[backend_v2/services/auth/token_service.py]` [NEW] | Authentication Token Subsystem |
| `AuthService.verify_token` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L283-L415]` | `@[backend_v2/services/auth/token_service.py]` [NEW] | Authentication Token Subsystem |
| `AuthService.create_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L417-L479]` | `@[backend_v2/services/auth/organization_service.py]` [NEW] | Tenant Organization Domain |
| `AuthService.create_user` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L481-L495]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService._create_user_internal` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L497-L623]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService._enforce_hierarchy` | FunctionDef | `@[backend_v2/services/auth.py#L625-L649]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Authorization Subsystem |
| `AuthService._count_org_admins` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L651-L664]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Authorization Subsystem |
| `AuthService.get_users_by_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L666-L675]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.delete_user` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L677-L758]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.delete_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L760-L836]` | `@[backend_v2/services/auth/organization_service.py]` [NEW] | Tenant Organization Domain |
| `AuthService.update_user` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L838-L929]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.update_user_role` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L931-L1030]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.list_users` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1034-L1049]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.list_organizations` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1051-L1067]` | `@[backend_v2/services/auth/organization_service.py]` [NEW] | Tenant Organization Domain |
| `AuthService.get_user` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1069-L1098]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService.get_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1100-L1124]` | `@[backend_v2/services/auth/organization_service.py]` [NEW] | Tenant Organization Domain |
| `AuthService.update_organization` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1126-L1160]` | `@[backend_v2/services/auth/organization_service.py]` [NEW] | Tenant Organization Domain |
| `AuthService.ensure_root_user` | AsyncFunctionDef | `@[backend_v2/services/auth.py#L1162-L1233]` | `@[backend_v2/services/auth/user_service.py]` [NEW] | User Lifecycle Domain |
| `AuthService` | ClassDef | `@[backend_v2/services/auth.py#L229-L1233]` | `@[backend_v2/services/auth/__init__.py]` [NEW] | Unified Facade Aggregator |

## Blast Radius & 1-Hop Consumer Dependencies

### Direct 1-Hop Import Consumers
1. `@[backend_v2/api/dependencies.py]` (Lines 55, 263-279): Imports `AuthService`, provides FastAPI dependency provider `get_auth_service` and `AuthServiceDep`.
2. `@[backend_v2/tests/unit/test_auth.py]` (30 unit tests): Imports `AuthService`, `OrganizationRepository`, `UserRepository`, `SYSTEM_ROOT_USER_ID`, `LEGACY_SYSTEM_ROOT_USER_ID`, `LEGACY_SYSTEM_ORG_ID`, `LEGACY_ROOT_MASTER_ID`.

### Indirect Route Consumers via AuthServiceDep
1. `@[backend_v2/api/routers/iam/auth.py]`: Uses `AuthServiceDep` for login token verification, user creation, impersonation, user deletion, profile fetch.
2. `@[backend_v2/api/routers/iam/users.py]`: Uses `AuthServiceDep` for list users, get user, update user, delete user.
3. `@[backend_v2/api/routers/iam/organizations.py]`: Uses `AuthServiceDep` for list organizations, get organization, create organization, delete organization.

## Authoritative 10-Item Technical Debt Inventory

1. **Duck Typing & Reflection**: 0 instances of `getattr` or `hasattr`. Type comparison `isinstance(data, OrganizationUpdateDTO)` on line 1151 to be retained for polymorphic DTO acceptance.
2. **Fallbacks & Raw Dicts**: Missing Pydantic V2 DTOs for audit details dictionaries passed to `audit_service.log_event(details=...)`. `strict=False` in `model_validate` calls on lines 95 and 223 bypasses strict type checking.
3. **Tuple Hell & Anonymous State Tuples**: 0 instances. All public methods return concrete domain models or typed DTOs.
4. **Error Handling & DLP**: Missing RFC 7807 structured dual-logging (`logger.error(...)`) prior to `PermissionDeniedError` raises on lines 434, 534, 539, 639, 644, 647, 709, 711, 715, 785, 788, 872, 877, 880, 885, 982, 985, 990, 1098, 1122, 1144. Broad `except Exception:` in Firebase fallback handlers on lines 574 and 581.
5. **Pydantic V2 Strictness & Annotations**: `audit_service: Any = None` on line 243 lacks protocol or abstract base class typing.
6. **Python 3.14 Modern Syntax**: Hardcoded `role_values` dictionary inside `update_user_role` can be centralized as an enum method on `UserRole`. `JWT_SECRET` hardcoded as module string constant instead of injecting from `backend_v2/settings.py`.
7. **Branching & Configuration**: Hardcoded literals: `duration_seconds: int = 3600`, default org quota limits (500.0, 5000.0), TPM limits (50000), RPM limits (500).
8. **Docstrings & Hygiene**: Incomplete `Raises:` docstring sections in `_create_user_internal` and `_enforce_hierarchy`.
9. **Flutter Frontend**: Zero direct client impact. Serialization models in `client_app_v2` remain 100% stable.
10. **ISTQB Testing & Polyfactory**: `test_auth.py` contains 30 tests in a single monolithic test file, utilizing manual dictionary-based mocks rather than strongly typed stateful in-memory fakes.
