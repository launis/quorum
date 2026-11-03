# Tracker: 3-Tier RBAC User CRUD UI in Organization & IAM Governance (`POST / PUT / DELETE /api/v2/iam/users/`)

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md] @[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]`
  - [x] Step 1: Phase 1: Align UserCreate DTO Defaults and Add UserRepository CRUD Methods
  - [x] Step 2: Phase 2: Implement 3-Tier RBAC User CRUD UI in OrganizationIamSettingsView
  - [x] Step 3: Phase 3: Global Quality Gates and Atomic Commit
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md] @[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[client_app_v2/lib/features/auth/domain/models/user.dart]
  - [ ] @[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document 3-tier RBAC User CRUD UI enforcement in `OrganizationIamSettingsView` (`ROOT` cross-organization switcher with tenant provider invalidation, `ADMIN` own-organization direct user creation and member editing, and Fail-Fast `Either<AppException, T>` unpacking across all `UserRepository` mutations).
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` if any IAM or settings module descriptions require updating.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the 3-tier RBAC User CRUD frontend-backend contract in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_3_Tier_RBAC_User_CRUD_UI.md] @[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[client_app_v2/lib/features/auth/domain/models/user.dart]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Align `UserCreate` in `@[client_app_v2/lib/features/auth/domain/models/user.dart#L120-L142]` with `@Default('fi') String language` and `@Default('system') String themeMode` for 1:1 parity with `UserBase` in `@[backend_v2/models/auth.py#L261-L304]`. | Step 1 | [x] Completed |
| REQ-002 | Add `createUser(UserCreate payload)` (`POST /iam/users/`) and `listOrganizations()` (`GET /iam/organizations/`) to `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart#L57-L137]` returning `Either<AppException, T>`. | Step 1 | [x] Completed |
| REQ-003 | Extend `@[client_app_v2/test/unit/features/auth/domain/models/user_test.dart#L116-L138]` to verify `UserCreate.toJson()` emits non-null `language`, `theme_mode`, `is_active`, `name`, and `password`. | Step 1 | [x] Completed |
| REQ-004 | Add English and Finnish localization keys (`orgSelectOrganizationLabel`, `orgCreateUserDirectBtn`, `orgCreateUserPasswordLabel`, `orgCreateUserPasswordHint`, `orgCreateUserSuccess`, `orgEditMemberTooltip`, `orgEditMemberDialogTitle`, `orgMemberActiveStatusLabel`) to `@[client_app_v2/lib/l10n/app_en.arb#L3020-L3036]` and `@[client_app_v2/lib/l10n/app_fi.arb#L2270-L2284]`. | Step 2 | [x] Completed |
| REQ-005 | Add `availableOrganizationsProvider` and a `ROOT`-only organization switcher (`org_root_selector_card` / `org_root_selector_dropdown`) in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L20-L143]` with `tenant_data_isolation` provider invalidation on selection change. | Step 2 | [x] Completed |
| REQ-006 | Implement direct user creation (`org_create_user_mode_chip`), organization-scoped member filtering, RBAC-filtered role dropdowns without hardcoded DB IDs, member edit dialog (`org_edit_member_dialog` for `name`, `isActive`, and `ROOT`-only `organizationId`), and Fail-Fast `res.fold((err) => throw err, ...)` unpacking in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L587-L878]`. | Step 2 | [x] Completed |
| REQ-007 | Add positive (`ADMIN` own-org CRUD, `ROOT` cross-org CRUD), negative boundary (`password.length == 5`), and backend error widget tests in `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L30-L411]`. | Step 2 | [x] Completed |
| REQ-008 | Pass global backend (`scripts/backend_audit_loop.py`) and frontend (`scripts/flutter_audit_loop.py`) quality gates and create an atomic Conventional Commit. | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Step 1: Aligned `UserCreate` in `@[client_app_v2/lib/features/auth/domain/models/user.dart]` (`@Default('fi') String language`, `@Default('system') String themeMode`), added `createUser` (`POST /iam/users/`) and `listOrganizations` (`GET /iam/organizations/`) to `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]`, and verified roundtrip serialization in `@[client_app_v2/test/unit/features/auth/domain/models/user_test.dart]`.
- Completed Step 2: Added English/Finnish localization keys to `@[client_app_v2/lib/l10n/app_en.arb]` and `@[client_app_v2/lib/l10n/app_fi.arb]`, implemented `availableOrganizationsProvider`, `_RootOrganizationSelectorCard`, direct user creation (`org_create_user_mode_chip`), RBAC-filtered role dropdowns, `_EditMemberDialog` (`name`, `isActive`, and `ROOT`-only `organizationId`), and Fail-Fast `res.fold((err) => throw err, ...)` unpacking in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`, and added positive (`ADMIN` own-org CRUD, `ROOT` cross-org CRUD), negative boundary (`password.length == 5`), and backend error widget tests in `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart]`.
- Completed Step 3: Passed global backend (`scripts/backend_audit_loop.py backend_v2/ --test` — 6,872 passed, 97.45% coverage, 81/81 DTO Parity aligned) and global frontend (`scripts/flutter_audit_loop.py client_app_v2/ --build` — 1,359 tests passed, 0 analyzer/guardrail issues) quality gates and committed changes atomically.
- Completed Tier 8 Plan Audit (`/tier8-audit-plan`): Verified 100% physical implementation across all 7 target files (`REQ-001` through `REQ-008`), 81/81 cross-language DTO parity (`audit_dto_parity.py`), 0 technical debt findings (`audit_technical_debt.py`), and 100% plan-tracker parity (`audit_plan_tracker_parity.py`).

## Learned
- `OrganizationIamSettingsView` uses `useState<String?>(null)` at the top of `build` before `switch (authState)` so `ROOT` can dynamically switch `activeOrgId` across organizations while invalidating `organizationMembersProvider` and `organizationAssignmentsProvider` on switch (`tenant_data_isolation`).
- Filtering displayed members in `_InvitationsAndMembersCard` by `member.organizationId == orgId` ensures `ROOT` views and manages members of the currently selected organization while `ADMIN` remains strictly scoped to their own organization.
- During `Tier 2 Hardening (Frontend)` (`--micro` mode), `resolve_flutter_unit_test_files` in `@[scripts/flutter_audit_loop.py#L62-L92]` requires a matching unit test file for `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]` at `client_app_v2/test/unit/features/auth/data/repositories/user_repository_test.dart`.

## Remaining
- Execute Tier 2 Frontend Hardening via `scripts/auto_hardening_runner.py` and `/tier7-describe-architecture`.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_3_Tier_RBAC_User_CRUD_UI.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
```
