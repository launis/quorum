# Tracker: Task Assignment, Task Brief CRUD+Clone & Direct Portal End-to-End Hardening (Findings A–E)

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md] @[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]`
  - [x] Step 1: Phase 1: Harden EmailService Canonical Resend Payload & StudioPromptBlockService Task Definition Draft Lifecycle (Finding C & Finding E Part 1)
  - [x] Step 2: Phase 2: Normalize First-Class Task Brief FK, Eager Base64 Ingress Extraction, Onboarding Email Verification & 1:1 DTO Parity (Finding A, Finding D & Finding E Backend Contract)
  - [x] Step 3: Phase 3: Add Authentic Firebase Auth + TOTP JIT Onboarding, Typed Task Brief Card & File Upload to TaskAssignmentPortalView (Finding A, Finding D & Finding E Part 2)
  - [ ] Step 4: Phase 4: Add Admin/Root Task Brief CRUD+Clone UI & Direct Task Assignment Creation Dialog in OrganizationIamSettingsView (Finding B & Finding E Part 3)
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md] @[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[backend_v2/api/routers/execution/executions.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [ ] @[backend_v2/models/auth.py]
  - [ ] @[backend_v2/models/domain/execution.py]
  - [ ] @[backend_v2/services/auth/email_service.py]
  - [ ] @[backend_v2/services/execution/assignment_service.py]
  - [ ] @[backend_v2/services/execution/facade.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/features/auth/data/auth_repository.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
  - [ ] @[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]
  - [ ] @[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]
  - [ ] @[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md] @[ki_god_code_prevention.md] @[ki_global_config_sovereignty.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document normalized `execution_assignments.task_brief_id` (`REFERENCES prompt_blocks(id) ON DELETE SET NULL`, `ZORM004`/`ZORM006`/`ZORM007`) and `TaskAssignmentBriefDTO` <-> `TaskAssignmentBriefDto` 1:1 parity across `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/models/domain/execution.py]`, `@[backend_v2/models/auth.py]`, and `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]`; eager `Base64Attachment` extraction via `ExecutionAssignmentService._normalize_assignee_ingress_inputs` and onboarding `email_verified=True` pre-MFA bootstrap in `@[backend_v2/services/execution/assignment_service.py]`; `StudioPromptBlockService.create_prompt_block_draft` category preservation in `@[backend_v2/services/studio/prompt_block_service.py]`; `ADMIN`/`ROOT` Task Brief CRUD + Clone (`_TaskBriefsManagementCard` and `organizationTaskBriefsProvider` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]`); standalone `TaskAssignmentConfigDialog` (`@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`); and `AuthRepository` MFA SSOT helpers + `TaskAssignmentPortalView` TOTP enrollment, typed Task Brief card, and file upload (`@[client_app_v2/lib/features/auth/data/auth_repository.dart]`, `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart]`).
     - `@[ki_global_config_sovereignty.md]`: Document `EmailService._compose_transactional_html` and `_send_single_http_item` (`@[backend_v2/services/auth/email_service.py]`) emitting the canonical Resend REST schema (`from`, `to`, `subject`, `html`, `tags`) with HTML-escaped `SecretStr` `action_url` CTA links while maintaining `QGR033` log redaction.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` accurately reflects `email_service.py`, `prompt_block_service.py`, `assignment_service.py`, `auth_repository.dart`, `tenant_secret_dto.dart`, `task_assignment_portal_view.dart`, `new_execution_view.dart`, and `organization_iam_settings_view.dart` responsibilities.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the normalized end-to-end Task Assignment, Task Brief CRUD + Clone, Resend transactional email CTA composition, eager portal document extraction, and Direct Task Portal (`/task/:token`) Firebase + TOTP onboarding workflow in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md] @[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/services/auth/email_service.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | **Finding C (Canonical Resend Payload & Escaped HTML CTA):** Add `EmailService._compose_transactional_html` (`html.escape(..., quote=True)`) and standardize `EmailService._send_single_http_item` on Resend's `from`, `to`, `subject`, `html`, and `tags` schema in `@[backend_v2/services/auth/email_service.py#L49-L327]` while preserving `QGR033` log redaction, verified in `@[backend_v2/tests/unit/services/auth/test_email_service.py#L276-L340]`. | Step 1 | [x] Done |
| REQ-002 | **Finding E Part 1 (Backend Task Brief Draft Lifecycle):** Preserve `PromptBlockCategory.TASK_DEFINITION` and `PromptBlockCategory.RUNTIME_VARIABLES` in `StudioPromptBlockService.create_prompt_block_draft` (`@[backend_v2/services/studio/prompt_block_service.py#L188-L242]`) and verify draft creation + cloning in `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py#L288-L303]`. | Step 1 | [x] Done |
| REQ-003 | **Finding A, D & E Backend Contracts (First-Class `task_brief_id` FK, Eager Base64 Extraction, Onboarding `email_verified` Bootstrap & 1:1 DTO Parity):** Evolve `execution_assignments.task_brief_id` across `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L400-L433]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L804-L850]`, and `@[backend_v2/models/domain/execution.py#L541-L672]`; synchronize `TaskAssignmentBriefDTO` / `TaskAssignmentBriefDto` and `WorkflowInputsIngress \| WorkflowInputs` across `@[backend_v2/models/auth.py#L1154-L1215]` and `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart#L213-L448]` (including `TD_MODEL_FACTORY` cleanups in `@[backend_v2/tests/unit/test_auth_models.py]`); inject `DocumentExtractionServiceDep` into `@[backend_v2/api/routers/execution/executions.py#L311-L344]` and `@[backend_v2/services/execution/facade.py#L637-L662]`; and implement `_validate_and_resolve_task_brief`, `_normalize_assignee_ingress_inputs`, and pre-MFA `email_verified=True` ordering in `@[backend_v2/services/execution/assignment_service.py#L159-L1775]`. | Step 2 | [x] Done |
| REQ-004 | **Finding A (Authentic Firebase Auth + Mandatory TOTP JIT Task Onboarding):** Extract MFA SSOT helpers (`prepareEnrollmentForCurrentUser`, `resolveChallengeAndGetIdToken`, `enrollTotpAndGetIdToken`) and implement `authenticateForTaskOnboarding` (`'user-not-found'` + `'invalid-credential'` registration fallback, 0-arg `AppException.unauthorized()`, `VALIDATION_FAILED` / `AUTHENTICATION_FAILED` error codes) in `@[client_app_v2/lib/features/auth/data/auth_repository.dart#L50-L393]` plus in-portal `MFA_REQUIRED` TOTP enrollment (`task_portal_totp_secret_text`) in `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart#L74-L628]`. | Step 3 | [x] Done |
| REQ-005 | **Finding D & Finding E Part 2 (Portal Typed Task Brief Card, `.arb` Localization & Document File Upload):** Add symmetrical `.arb` keys in `@[client_app_v2/lib/l10n/app_en.arb#L3058-L3131]` and `@[client_app_v2/lib/l10n/app_fi.arb#L2264-L2343]`, render `Key('task_portal_task_brief_card')` from `TaskAssignmentBriefDto`, and wire `FilePicker.platform.pickFiles` + `WorkflowInputValue.file` (`fileVal.fileValue`) with `DGR011` `context.mounted` guards in `@[client_app_v2/lib/features/execution/views/task_assignment_portal_view.dart#L74-L628]`. | Step 3 | [x] Done |
| REQ-006 | **Finding B (Standalone TaskAssignmentConfigDialog, First-Class `taskBriefId`, Localized Chips & Dispatch Summary):** Promote `TaskAssignmentConfigDialog` in `@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L175-L1232]` with `Workflow`, `OutputProfile`, and `TaskDefinitionPromptBlock` (`taskBriefId`) dropdowns, localized `ExpectedInput.label` `FilterChip`s, verified dispatch confirmation text, and cohort summary CSV export. | Step 4 | [ ] Pending |
| REQ-007 | **Finding E Part 3 (Admin/Root Task Brief CRUD + Clone UI & Stateful Test Harness in OrganizationIamSettingsView):** Add `organizationTaskBriefsProvider` (`whereType<TaskDefinitionPromptBlock>()`), `ROOT` org-switch invalidation, `_TaskBriefsManagementCard` (`PromptBlockCategory.taskDefinition.id`, `null` blank-field normalization, and `ROOT_SYSTEM` edit/delete guard for tenant `ADMIN`), and direct `TaskAssignmentConfigDialog` launch in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart#L23-L760]`, backed by stateful `_FakeStudioClient` CRUD+Clone persistence in `@[client_app_v2/test/features/settings/presentation/organization_iam_settings_view_test.dart#L255-L1158]`. | Step 4 | [ ] Pending |

# Session Handover Context

## Achieved
- Completed `/tier0-research-plan` System 2 red-teaming and proactive architectural hardening on `@[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md]` and synchronized `@[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]` with 100% bidirectional parity across 4 atomic execution steps, 7 requirements (`REQ-001`–`REQ-007`), 9 surviving backend production targets, and 5 surviving frontend production targets.
- Eliminated 9 pre-execution showstopper defects: (1) portal `Base64Attachment` HTTP 422 rejection and skipped `DocumentExtractionService` extraction + non-existent `WorkflowInputValueFile`/`FilePicker.pickFiles` symbols, (2) Dart compile failure on `AppException.unauthorized('...')` and wrong `VALIDATION_ERROR`/`UNAUTHORIZED` error codes, (3) live Firebase `MFA_REQUIRED` + `emailVerified == false` + `'invalid-credential'` enumeration lockouts during JIT onboarding, (4) missing `l10n.edit` `.arb` key, (5) `PromptBlock.instructionText` compile error and raw `'task_definition'` string filtering, (6) `SmartIngressResolver` HTTP 400 slot collision from stuffing `task_brief_*` into `lockedInputs.dynamicInputs`, (7) Resend REST API HTTP 400/422 rejection on unknown root keys and unescaped query `&` in `href`, (8) backend HTTP 422 on empty `""` `instruction_text` / `TheoryGrounding.source_url` and HTTP 403 when tenant `ADMIN` edits/deletes `ROOT_SYSTEM` Task Briefs, and (9) `_FakeStudioClient` `NoSuchMethodError` in `organization_iam_settings_view_test.dart` plus tracker `--gate` / skill CLI flag mismatches.

## Learned
- `scripts/backend_audit_loop.py` executes `scripts/audit_dto_parity.py` unconditionally, so modifying `ExecutionAssignment*DTO` and adding `TaskAssignmentBriefDTO` in `@[backend_v2/models/auth.py]` MUST be coupled atomically in Step 2 with `@[client_app_v2/lib/features/settings/domain/models/tenant_secret_dto.dart]` (`--build` codegen).
- Adding `task_brief_id` to `execution_assignments` requires lockstep updates across `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` (no SQL `DEFAULT` per `ZORM004`, plus `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` per `ZORM007`), `@[scripts/audit_zero_orm_strictness.py]` (`APPROVED_ADAPTER_RECORD_COLUMNS` for `ZORM006` and `REQUIRED_IDEMPOTENT_ALTER_COLUMNS` for `ZORM007`), `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` (`missing_alter_sql`), and `@[backend_v2/models/domain/execution.py]` (`test_schema_dto_naming_parity` in `test_postgres.py`).
- In `@[backend_v2/services/execution/assignment_service.py]`, `_verify_onboarding_firebase_token` must check `IDENTITY_MISMATCH` before calling `fb_auth.update_user(uid_str, email_verified=True)` via `asyncio.to_thread` and await `update_res` if `inspect.iscoroutine(update_res)` so `AsyncMock()` fixtures in `test_assignment_service.py` never emit unawaited coroutine warnings.

## Remaining
- Start a **fresh chat session** and execute Steps 1–4 via `/tier2-execute --full-auto`, followed by Post-Implementation Gates (`auto_hardening_runner.py` for Backend and Frontend), `/tier7-describe-architecture`, and `/tier8-audit-plan`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Task_Assignment_Portal_Hardening.md] @[docs/implementationplans/TRACKER_Task_Assignment_Portal_Hardening.md]
```
