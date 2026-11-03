<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# IMPLEMENTATION PLAN: 3-Tier RBAC User CRUD UI in Organization & IAM Governance (`POST / PUT / DELETE /api/v2/iam/users/`)

## 1. Objective & Architectural Background

The backend IAM service in `@[backend_v2/services/auth/user_service.py#L54-L1104]` and `@[backend_v2/services/auth/organization_service.py#L307-L344]` already implements a strict 3-tier RBAC User CRUD model over `/api/v2/iam/users/` and `/api/v2/iam/organizations/`:
1. **`ROOT` (`UserRole.root`)**: Full User CRUD (`list_users`, `create_user`, `update_user`, `delete_user`) across **all organizations**, including switching between organizations (`list_organizations`) and transferring users across organizations (`organization_id`).
2. **`ADMIN` (`UserRole.admin`)**: Full User CRUD scoped strictly to **their own organization** (`organization_id == currentUser.organizationId`): can list organization members, create new users directly with `email`, `name`, `password`, and `role` (`viewer`, `member`, `manager`, `admin`), update member `name`, `role`, and `is_active`, and execute GDPR soft-delete (`delete_user`), while blocked from creating/modifying `ROOT` users or accessing other organizations.
3. **Regular User (`VIEWER`, `MEMBER`, `MANAGER`, and self-service in `@[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart#L58-L377]`)**: Can view their own profile and update only their own personal attributes (`name`, `language`, `themeMode`) via `PUT /api/v2/iam/users/{id}`, while `email`, `organization_id`, and `role` are strictly read-only (`readOnly: true`) and protected against mutation by `UserService._validate_update_user_permissions` and `UserService._validate_self_update_fields`.

On the Flutter frontend, three gaps currently prevent `ROOT` and `ADMIN` from exercising full User CRUD in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L57-L878]`:
1. **`UserCreate` & `UserRepository` Gaps:** `UserCreate` in `@[client_app_v2/lib/features/auth/domain/models/user.dart#L120-L142]` defines `language` and `themeMode` as nullable with `includeIfNull: false`, whereas `UserBase` in `@[backend_v2/models/auth.py#L261-L304]` and `UserCreate` in `@[backend_v2/models/auth.py#L441-L452]` require non-null `language` and `theme_mode`. Furthermore, `UserRepository` in `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart#L57-L137]` lacks `createUser(UserCreate payload)` (`POST /iam/users/`) and `listOrganizations()` (`GET /iam/organizations/`).
2. **`ROOT` Cross-Organization Selector Missing:** `OrganizationIamSettingsView` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L101-L135]` locks `orgId` to `value.organizationId`, preventing `ROOT` from selecting target organizations across the system (`GET /iam/organizations/`) and filtering/managing users per organization.
3. **Direct User Creation (C), Member Update (U), & Silent `Either` Swallowing in `_InvitationsAndMembersCard`:** `_InvitationsAndMembersCard` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L587-L878]` only supports email invitations (no direct user creation form with `email`, `name`, `password`, `role`), its member role dropdown iterates over `UserRole.values` (exposing `UserRole.unknown` and `UserRole.root` to `ADMIN`), member rows lack editing for `name` and `is_active` (plus `organization_id` for `ROOT`), and existing `updateUser`, `deleteUser`, and `revokeInvitation` calls ignore returned `Left(AppException)` values without `res.fold((err) => throw err, ...)`.

## 2. Scope & Target Boundaries (5-Column Directives Table)

### Context Files (Read-Only)
- `@[backend_v2/api/routers/iam/users.py#L116-L150]`
- `@[backend_v2/api/routers/iam/organizations.py#L57-L72]`
- `@[backend_v2/models/auth.py#L261-L304]`
- `@[backend_v2/models/auth.py#L441-L452]`
- `@[backend_v2/services/auth/user_service.py#L112-L172]`
- `@[backend_v2/services/auth/user_service.py#L623-L685]`
- `@[client_app_v2/lib/features/settings/presentation/user_profile_settings_view.dart#L58-L377]`

### Target Files (`[NEW]`, `[MODIFY]`, `[DELETE]`)

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `[MODIFY] @[client_app_v2/lib/features/auth/domain/models/user.dart#L120-L142]` | Nullable `language` and `themeMode` omitted from `UserCreate.toJson()`, causing backend Pydantic `ValidationError` on `POST /api/v2/iam/users/`. | Enforce `@Default('fi') String language` and `@Default('system') String themeMode` in `UserCreate` with `disallowUnrecognizedKeys: true` for 1:1 parity with `UserBase` in `@[backend_v2/models/auth.py#L261-L304]`. | Reuse existing `UserCreate` and `UserUpdate` Freezed DTOs without inventing parallel models. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/auth/domain/models/user.dart --build` |
| `[MODIFY] @[client_app_v2/lib/features/auth/data/repositories/user_repository.dart#L57-L137]` | Missing `POST /iam/users/` and `GET /iam/organizations/` client methods in `UserRepository`. | Add `createUser(UserCreate payload)` (`POST /iam/users/`) and `listOrganizations()` (`GET /iam/organizations/`) to `UserRepository` returning `Either<AppException, T>`. | Keep all HTTP transport strictly inside `UserRepository` with `_handleError` mapping. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/auth/data/repositories/user_repository.dart` |
| `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb#L3020-L3036]` | Hardcoded UI strings in widgets (banned by `no_magic_strings_l10n`). | Add localization keys `orgSelectOrganizationLabel`, `orgCreateUserDirectBtn`, `orgCreateUserPasswordLabel`, `orgCreateUserPasswordHint`, `orgCreateUserSuccess`, `orgEditMemberTooltip`, `orgEditMemberDialogTitle`, and `orgMemberActiveStatusLabel` to `app_en.arb`. | Reuse existing `profileEmailLabel`, `profileDisplayNameLabel`, `profileOrganizationIdLabel`, `orgInviteRoleLabel`, `save`, and `cancel`. | `cd client_app_v2; flutter gen-l10n` |
| `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb#L2270-L2284]` | Missing Finnish translations for 3-tier User CRUD controls. | Add matching Finnish localization keys `orgSelectOrganizationLabel`, `orgCreateUserDirectBtn`, `orgCreateUserPasswordLabel`, `orgCreateUserPasswordHint`, `orgCreateUserSuccess`, `orgEditMemberTooltip`, `orgEditMemberDialogTitle`, and `orgMemberActiveStatusLabel` to `app_fi.arb`. | Maintain 1:1 ARB key parity with `app_en.arb`. | `cd client_app_v2; flutter gen-l10n` |
| `[MODIFY] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L20-L878]` | Fixed `orgId` blocking `ROOT` cross-organization management, missing direct user creation form, unfiltered `UserRole.values` dropdown, missing member `name`/`isActive` update controls, and silent ignoring of `Left(AppException)` in `updateUser`/`deleteUser`/`revokeInvitation`. | Add `availableOrganizationsProvider`, a `ROOT`-only organization switcher (`org_root_selector_dropdown`) with provider invalidation on switch, direct user creation mode (`org_create_user_mode_chip`), RBAC-filtered role dropdown options without hardcoded DB IDs, organization-scoped member filtering, an edit member dialog (`name`, `isActive`, and `ROOT`-only `organizationId`), and fail-fast `res.fold((err) => throw err, ...)` unpacking across all repository mutations. | Keep all organization and member CRUD cohesive inside `OrganizationIamSettingsView` without introducing extra routes. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart --build` |
| `[MODIFY] @[client_app_v2/test/unit/features/auth/domain/models/user_test.dart#L116-L138]` | Unverified `language` and `theme_mode` serialization in `UserCreate.toJson()`. | Assert that `UserCreate.toJson()` emits non-null `language` and `theme_mode` and supports explicit `password` and `name` fields. | Extend the existing `UserCreate` unit test group. | `cd client_app_v2; flutter test test/unit/features/auth/domain/models/user_test.dart --no-pub` |
| `[MODIFY] @[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L30-L411]` | Missing widget tests for 3-tier User CRUD (`ROOT` cross-org selection, `ADMIN` own-org User CRUD, and boundary/error handling). | Extend `_FakeUserRepository` with `listOrganizations`, `createUser`, `updateUser`, and `deleteUser`, and add positive, negative, and boundary widget tests verifying `ROOT` all-org CRUD and `ADMIN` own-org CRUD. | Reuse `_buildIamViewForRole` and `_FakeUserRepository` test harness. | `cd client_app_v2; flutter test test/features/settings/presentation/organization_iam_settings_view_test.dart --no-pub` |

## 3. Pre-Implementation Technical Debt Cleanups (Phase 1)

1. **`UserCreate` Required Backend Fields Parity (`@[client_app_v2/lib/features/auth/domain/models/user.dart#L120-L142]`):** `audit_technical_debt.py` reported 0 static AST findings across the target files, but schema inspection revealed that `UserBase` in `@[backend_v2/models/auth.py#L261-L304]` requires `language` and `theme_mode` on `UserCreate`, whereas Dart `UserCreate` declared them as nullable with `includeIfNull: false`. Step 1 resolves this mismatch first by setting `@Default('fi') String language` and `@Default('system') String themeMode` on `UserCreate`.
2. **Unfiltered `UserRole.values` & Silent `Left(AppException)` Swallowing in `_InvitationsAndMembersCard` (`@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L774-L866]`):** The member row dropdown previously iterated over `UserRole.values` (exposing `UserRole.unknown` and `UserRole.root` to `ADMIN`), and `revokeInvitation`, `updateUser`, and `deleteUser` ignored `Left(AppException)` returns inside `mutation.mutate(...)`. Step 2 replaces `UserRole.values` with an RBAC-filtered role list (`viewer`, `member`, `manager`, `admin`, plus `root` when `currentUser.role == UserRole.root || member.role == UserRole.root` without hardcoded organization ID strings) and enforces `res.fold((err) => throw err, ...)` on every repository call inside `mutation.mutate(...)`.

## 4. Detailed Execution Protocol (Hybrid XML Sandwich)

```xml
<execution_protocol>
  <step id="1" name="Phase 1: Align UserCreate DTO Defaults and Add UserRepository CRUD Methods">
    <constraint invariant="anti_semantic_drift_renaming">Field names in `UserCreate` and `UserUpdate` (`email`, `name`, `role`, `organization_id`, `is_active`, `language`, `theme_mode`, `created_by`, `password`) MUST remain 1:1 identical with `backend_v2/models/auth.py`.</constraint>
    <constraint invariant="ignore_generated">NEVER manually edit `user.freezed.dart`, `user.g.dart`, or `user_repository.g.dart`; regenerate them via `scripts/flutter_audit_loop.py` with `--build`.</constraint>
    <action>Modify `@[client_app_v2/lib/features/auth/domain/models/user.dart#L120-L142]` so `language` is `@JsonKey(name: 'language') @Default('fi') String language` and `themeMode` is `@JsonKey(name: 'theme_mode') @Default('system') String themeMode`.</action>
    <action>Modify `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart#L57-L137]` to add:
      1. `Future<Either<AppException, User>> createUser(UserCreate payload)` calling `_client.post<Map<String, Object?>>('/iam/users/', data: payload.toJson())`,
      2. `Future<Either<AppException, List<Organization>>> listOrganizations()` calling `_client.get<List<Object?>>('/iam/organizations/')`.
    </action>
    <action>Update `@[client_app_v2/test/unit/features/auth/domain/models/user_test.dart#L116-L138]` to assert that `UserCreate.toJson()` includes `'language': 'fi'`, `'theme_mode': 'system'`, `'is_active': true`, and serializes `name` and `password` when provided.</action>
    <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/auth/domain/models/user.dart --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/auth/data/repositories/user_repository.dart`.</action>
  </step>

  <step id="2" name="Phase 2: Implement 3-Tier RBAC User CRUD UI in OrganizationIamSettingsView">
    <constraint invariant="no_magic_strings_l10n">NEVER hardcode literal UI strings or pixel padding numbers in `OrganizationIamSettingsView`; resolve all labels via `AppLocalizations` and spacing via `AppSpacing`.</constraint>
    <constraint invariant="async_build_context_mounted_ban">ALWAYS verify `if (context.mounted)` after `await` before calling `ScaffoldMessenger.of(context)` or `Navigator.of(context)`.</constraint>
    <constraint invariant="horizontal_overflow_prevention">ALWAYS set `isExpanded: true` on `DropdownButtonFormField` and wrap row text in `Expanded` or `Flexible` with `overflow: TextOverflow.ellipsis`.</constraint>
    <action>Add localization keys `orgSelectOrganizationLabel`, `orgCreateUserDirectBtn`, `orgCreateUserPasswordLabel`, `orgCreateUserPasswordHint`, `orgCreateUserSuccess`, `orgEditMemberTooltip`, `orgEditMemberDialogTitle`, and `orgMemberActiveStatusLabel` to `@[client_app_v2/lib/l10n/app_en.arb#L3020-L3036]` and `@[client_app_v2/lib/l10n/app_fi.arb#L2270-L2284]`.</action>
    <action>Modify `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L20-L143]` to:
      1. Add `@riverpod Future<List<Organization>> availableOrganizations(Ref ref)` calling `ref.watch(userRepositoryProvider).listOrganizations()`,
      2. Hold `final selectedOrgId = useState<String?>(value.organizationId);` in `OrganizationIamSettingsView`,
      3. When `value.role == UserRole.root`, render a `Card` (`key: const Key('org_root_selector_card')`) evaluating `ref.watch(availableOrganizationsProvider)` via Dart 3 `switch` (`AsyncLoading` -> `CircularProgressIndicator`, `AsyncError` -> `ErrorView`, `AsyncData` -> Fail-Fast `ErrorView` if `activeOrgId` is missing from returned organizations, otherwise `DropdownButtonFormField<String>` with `key: const Key('org_root_selector_dropdown')`, `isExpanded: true`, invalidating `organizationMembersProvider` and `organizationAssignmentsProvider` on selection change per `tenant_data_isolation`) so `ROOT` can switch the active target `activeOrgId` across any organization in the system, while `ADMIN` and `MANAGER` remain strictly scoped to `value.organizationId`.
    </action>
    <action>Modify `_InvitationsAndMembersCard` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L587-L878]` to provide full RBAC-scoped User CRUD:
      1. **Create (C):** Add a third `ChoiceChip` mode (`key: const Key('org_create_user_mode_chip')`, label `l10n.orgCreateUserDirectBtn`) rendering `org_create_user_email_field`, `org_create_user_name_field`, `org_create_user_password_field` (`obscureText: true`), `org_invite_role_dropdown`, and `org_create_user_submit_btn` (`POST /iam/users/` with `organizationId: orgId`, validating non-empty email and password length `>= 6`, and unpacking `createUser` with `res.fold((err) => throw err, ...)`).
      2. **Read (R):** Filter displayed members in `_InvitationsAndMembersCard` to `member.organizationId == orgId` (showing `member.name` and `member.email`) so `ROOT` sees members of whichever organization is selected in `org_root_selector_dropdown` and `ADMIN` sees members of their own organization.
      3. **Update (U):** Restrict inline role dropdown options to assignable roles (`viewer`, `member`, `manager`, `admin`, plus `root` only when `currentUser.role == UserRole.root || member.role == UserRole.root` with zero hardcoded organization IDs, disabling `onChanged` when `currentUser.role != UserRole.root && (member.role == UserRole.root || member.id == currentUser.id)`), and add an edit button (`Key('org_edit_member_btn_${member.id}')`) that opens an edit dialog (`Key('org_edit_member_dialog')`) allowing `ROOT` or `ADMIN` to update `name` (`Key('org_edit_member_name_field')`), `isActive` (`SwitchListTile` with `Key('org_edit_member_active_switch')`, disabled for self when `currentUser.role != UserRole.root`), and (exclusively when `currentUser.role == UserRole.root`) `organizationId` (`DropdownButtonFormField<String>` with `Key('org_edit_member_org_dropdown')`) via `UserRepository.updateUser` unpacked with `res.fold((err) => throw err, ...)`.
      4. **Delete (D) & Revoke:** Preserve the GDPR soft-delete button (`Key('org_delete_member_btn_${member.id}')`, shown when `member.id != currentUser.id`) calling `UserRepository.deleteUser(member.id)` and `revokeInvitation`, unpacking both with `res.fold((err) => throw err, ...)`.
    </action>
    <action>Update `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L30-L411]` to implement `listOrganizations`, `createUser`, `updateUser`, and `deleteUser` on `_FakeUserRepository` and add widget tests covering:
      1. Positive (`ADMIN` own-organization CRUD): `ADMIN` creates a user directly (`org_create_user_mode_chip`), updates a member's `name` and `isActive` via `org_edit_member_btn_<id>`, updates a member's `role`, and deletes a member within their own organization, while `org_root_selector_dropdown` is not shown to `ADMIN`.
      2. Positive (`ROOT` cross-organization CRUD): `ROOT` sees `org_root_selector_dropdown`, switches to a second organization, creates a user in that organization, and edits a member (including organization transfer via `org_edit_member_org_dropdown`).
      3. Negative 1 (Boundary `< 6` char password): entering a 5-character password (`'12345'`) in direct user creation raises `AppException.validation` rendered in `ErrorView` without calling `userRepo.createUser`.
      4. Negative 2 (Backend failure): when `userRepo.createUser` returns `Left(AppException.server('Firebase provisioning failed'))`, `ErrorView` renders inside `_InvitationsAndMembersCard`.
    </action>
    <action>Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart --build` and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart`.</action>
  </step>

  <step id="3" name="Phase 3: Global Quality Gates and Atomic Commit">
    <constraint invariant="atomic_checkpoint_mandate">NEVER use `git add .` or discard runtime changes in `data/db_v2.json`. Stage only the explicitly modified files.</constraint>
    <action>Run the global backend quality gate (`$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`) to verify 100% cross-language DTO parity (`audit_dto_parity.py`).</action>
    <action>Run the global frontend quality gate (`$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`).</action>
    <action>Inspect `git diff` and create an atomic Conventional Commit in English staging all modified target files.</action>
  </step>
</execution_protocol>
```

## 5. Architectural Safeguards & Verification Plan (ISTQB Test Matrix)

### Automated Unit & Structural Tests
- **Scenario 1 (Happy Path - `ADMIN` Own-Organization User CRUD):** `ADMIN` opens `OrganizationIamSettingsView` (scoped to their own `orgId`, no `org_root_selector_dropdown`), creates a new user via `org_create_user_mode_chip` (`email`, `name`, `password`, `role: UserRole.manager`), edits an existing member's `name` and `isActive` via `org_edit_member_btn_<id>`, and deletes a member -> `UserRepository.createUser`, `updateUser`, and `deleteUser` are invoked for `orgId`.
- **Scenario 2 (Happy Path - `ROOT` All-Organization User CRUD):** `ROOT` opens `OrganizationIamSettingsView`, selects a secondary organization in `org_root_selector_dropdown`, views that organization's members, creates a user in that organization, and opens `org_edit_member_dialog` where `org_edit_member_org_dropdown` allows transferring a user between organizations.
- **Scenario 3 (Happy Path - Regular User Self-Service Profile without Org/Role Edit):** Verified in `@[client_app_v2/test/features/settings/presentation/user_profile_settings_view_test.dart#L143-L320]` that `MEMBER` can update only `name`, `language`, and `themeMode` while `profile_email_readonly_field` and `profile_org_id_readonly_field` are `readOnly: true` and `profile_role_badge` is non-editable.
- **Scenario 4 (Negative Path 1 - Boundary Value Violation `password.length == 5`):** Submitting a 5-character password (`'12345'`, `min - 1` against backend `min_length=6`) raises `AppException.validation`, renders `ErrorView` inside `_InvitationsAndMembersCard`, and does not invoke `UserRepository.createUser`.
- **Scenario 5 (Negative Path 2 - Repository / Backend Provisioning Failure):** When `UserRepository.createUser` returns `Left(AppException.server('Firebase provisioning failed'))`, `mutation.hasError` is true and `ErrorView` is rendered audibly.

### Global Completion Gates & Mandatory Final E2E REST API Verification Gate
- **Global Backend Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test`
- **Global Flutter Audit Loop:** `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`
- **Mandatory Final E2E REST API Verification Gate:**
  - Windows / PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
  - Unix / Bash: `RUN_LIVE_E2E="true" uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`

