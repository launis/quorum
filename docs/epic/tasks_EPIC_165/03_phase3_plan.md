<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_gateway_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# EPIC 165 - Phase 3: `task_briefs` <-> `execution_assignments` Publication Snapshot (`task_brief_snapshot JSONB`), `ON DELETE RESTRICT`, `organization_id NOT NULL ON DELETE CASCADE` & $O(1)$ Indexed SQL Query Pushdown

**Overview:** Harden the 2-table `task_briefs` (`tbr_<hex32>`) <-> `execution_assignments` (`tsk_<hex32>`) architecture by moving `TaskAssignmentBriefDTO` onto frozen `V2CoreBase` in `@[backend_v2/models/domain/task_brief.py#L27-L86]` (re-exported in `@[backend_v2/models/auth.py#L110-L129]` to prevent circular imports with `@[backend_v2/models/domain/execution.py#L565-L701]`), freezing an immutable `task_brief_snapshot: TaskAssignmentBriefDTO | None` (`JSONB` paired with `task_brief_id` via `enforce_assignment_task_brief_snapshot_parity`) at cohort assignment publication time in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, and dropping the silent `strict: bool = False` compromise in `_validate_and_resolve_task_brief`. Upgrade `execution_assignments.task_brief_id`, `execution_assignments.output_profile_id`, and `execution_assignments.workflow_id` to kernel-level `ON DELETE RESTRICT` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]` and `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]` (eliminating the full-table Python scan `_check_active_assignment_usage` in `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`), hydrate `"organization_id": "org_0195f3a0000070008000000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all **120** system-owned tenant-scoped seed records in `@[backend_v2/seed/seed_data.json#L1-L50]` (`1` already hydrated in `mcp_gateways` plus **119** Studio records: `90` in `prompt_blocks`, `2` in `task_briefs`, `3` in `workflows`, `21` in `steps`, and `3` in `output_profiles`, while keeping global `model_registries` strictly tenant-agnostic), enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across SQL (including idempotent pre-seed backfill migration), Python Studio domain/DTO models (overriding `exclude=True` on `OutputProfileResponseDTO`), module-level `resolve_create_organization_id` in `@[backend_v2/services/studio/auth_validator.py#L30-L54]`, PostgreSQL row hydrators (`@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]`), and Flutter Studio Freezed models (`task_brief.dart`, `workflow.dart` including `NodeStrategy`, `prompt_block.dart`, `output_profile.dart`, and their 3 Studio UI callers), and push $O(N)$ Python table scans down into $O(1)$ indexed parameterized SQL queries on `EntityPersistencePort` (`@[backend_v2/database/interfaces.py#L291-L382]`) and `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]`).

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 3 Forensic Context, Producer-Consumer Contracts & SQL DDL (Synchronized with EPIC 165)

### Forensic Finding 5 [P1 HIGH]: `task_briefs` <-> `execution_assignments` Published Cohort Mutability, Silent `strict=False` Fallback & Multi-Tenant `ON DELETE SET NULL` Escalation
* **Forensic Anchors:**
  * `@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md#L1-L120]`
  * `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L498-L557]` (`task_briefs` and `execution_assignments` DDL)
  * `@[backend_v2/models/domain/execution.py#L565-L701]`, `@[backend_v2/models/auth.py#L110-L129]`, and `@[backend_v2/services/studio/auth_validator.py#L30-L54]`
  * `@[backend_v2/services/studio/task_brief_service.py#L83-L123]`
  * `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` (`_validate_and_resolve_task_brief`, `create_assignment`, and `create_assignment_batch`)
* **Architectural Verdict on the 2-Table Split (`task_briefs` vs. `execution_assignments`):**
  * Separating reusable **Task Brief Templates (`task_briefs`, `tbr_<hex32>`)** from **Published Cohort Assignments (`execution_assignments`, `tsk_<hex32>`)** is **100% textbook relational design** (1:N Definition/Catalog vs. Dispatched Recipient Instance). Extracting `task_briefs` out of `prompt_blocks` cured the Single-Table Inheritance smell where human task briefs carried 14 `NULL` BARS matrix columns.
  * Modeling a published subset of recipients (`POST /api/v2/assignments/batch`, 1 to 500 recipients) as individual rows in `execution_assignments` sharing a cohort `batch_id UUID` is also the right relational grain: each recipient requires an independent single-use token digest (`token_hash TEXT NOT NULL UNIQUE`), an independent state lifecycle (`status` across `AssignmentStatus`), an independent activation countdown (`activated_at` + `relative_duration_seconds`), independent `draft_inputs`, and a 1:1 `execution_id` link, while avoiding a 3-table join on hot portal token lookups.
* **Nine Concrete Structural & Red-Team Defects Closed in Phase 3 (Including Finding 7 Site 7):**
  1. **Retroactive Mutation of Published Cohort Assignments (`immutable_history_snapshot` Violation):** `execution_assignments` stores only `task_brief_id` and resolves `TaskBrief` dynamically at preview/list time (`_validate_and_resolve_task_brief`). Editing `TaskBrief.instruction_text` in Studio after publishing a task to a cohort retroactively alters published and historical assignment instructions unless frozen into `task_brief_snapshot JSONB` at publication time.
  2. **Circular Import & Mutable Base Class on `TaskAssignmentBriefDTO`:** `@[backend_v2/models/auth.py#L1048-L1069]` imports `ExecutionAssignment` at runtime (`from backend_v2.models.domain.execution import ExecutionAssignment`) and defines `TaskAssignmentBriefDTO(BaseResponseDTO)` as mutable with `organization_id: str | None = Field(default=None, exclude=True)`. Defining `TaskAssignmentBriefDTO(V2CoreBase)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) in `@[backend_v2/models/domain/task_brief.py#L27-L86]` and re-exporting it in `@[backend_v2/models/auth.py]` prevents circular `ImportError` while enforcing strict immutability inside `ExecutionAssignment`.
  3. **Silent `strict=False` Fallback Compromise (Finding 7 Site 7):** `_validate_and_resolve_task_brief` defines `strict: bool = True`, and both `preview_assignment` and `_to_hydrated_assignment_response` pass `strict=False`, silently returning `task_brief=None` when `task_brief_repo` is missing, the `TaskBrief` row is missing, or tenant ownership fails (`zero_backward_compatibility_planning_ban`).
  4. **`ON DELETE SET NULL` vs. `ON DELETE RESTRICT` Contradiction:** SQL declares `task_brief_id UUID REFERENCES task_briefs(id) ON DELETE SET NULL`, `output_profile_id UUID REFERENCES output_profiles(id) ON DELETE SET NULL`, and `workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE`, while `StudioTaskBriefService._check_active_assignment_usage` loads 100% of `execution_assignments` across all tenants into Python RAM (`list_execution_assignments()`) to raise `ErrorCodes.DELETE_BLOCKED_BY_USAGE`.
  5. **Critical Multi-Tenant Leak via `organization_id ON DELETE SET NULL` & `"SYSTEM"` Hydration Shims:** `SystemOrganizations.is_system(org_id)` evaluates `return not org_id or org_id in (cls.ROOT_SYSTEM.value, "SYSTEM")`, and `_format_org_uuid7` in `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]` converts `0195f3a0-0000-7000-8000-000000000001` back into literal `"SYSTEM"` (`default_system=True` in step/workflow/profile hydrators). Enforcing `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` and canonical `org_0195f3a0000070008000000000000001` (`ROOT_SYSTEM` on `SystemOrganizations`) across all 120 tenant-scoped system seed rows, SQL tables, adapters, repositories, Studio services/factories, and models eliminates both the `NULL` promotion leak and the `"SYSTEM"` hydration crash.
  6. **Pre-Seed `apply_migrations()` Cutover Ordering on Existing Phase 2 PostgreSQL Volumes:** `run_seed.py` executes `apply_migrations()` BEFORE `seed_collection_batch`. Because the legacy `system_configs` drop gate does not drop Phase 2 tables, `001_pg19_uuidv7_schema.sql` MUST include an idempotent `DO $$` block that ensures `0195f3a0-0000-7000-8000-000000000001` exists in `organizations` when `NULL` Studio rows exist, backfills `organization_id` across `prompt_blocks`, `task_briefs`, `steps`, `workflows`, and `output_profiles`, swaps `ON DELETE SET NULL` / `CASCADE` constraints to `ON DELETE CASCADE` (on `organization_id`) and `ON DELETE RESTRICT` (on `execution_assignments` FKs), backfills `task_brief_snapshot` for any pre-existing `execution_assignments`, and sets `ALTER COLUMN organization_id SET NOT NULL` without ever emitting the banned substring `"UPDATE executions"`.
  7. **`OutputProfileResponseDTO` Wire-Stripping Crash (`exclude=True`) & Missing `organization_id` Mapping:** `OutputProfileResponseDTO` (`@[backend_v2/models/dtos/output_profile.py#L519-L661]`) inherits `BaseResponseDTO.organization_id` (`Field(default=None, exclude=True)`), stripping `"organization_id"` from JSON responses, and `StudioWorkflowService._to_output_profile_dto` (`@[backend_v2/services/studio/workflow_service.py#L49-L974]`) omits `organization_id=profile.organization_id`. Overriding `organization_id` with `exclude=False` on `OutputProfileResponseDTO`, passing `organization_id=profile.organization_id` in `_to_output_profile_dto`, and registering `"outputprofileresponsedto": "outputprofile"` in `@[scripts/audit_dto_parity.py]` prevents Flutter deserialization crashes.
  8. **Missing Cohort Indexes & $O(N)$ Python Table Scans:** `execution_assignments` lacks composite `(organization_id, id DESC)` and `(batch_id)` B-Tree indexes, `executions` lacks `(organization_id, id DESC)`, and `ExecutionAssignmentService._find_assignment_by_token_hash`, `get_assignment_by_execution_id`, `list_assignments`, `ExecutionRepositoryImpl.get_all_executions` / `get_recent_completed_executions`, and `AuditRepositoryImpl.get_detailed_usage` scan full tables in Python instead of executing $O(1)$ / indexed parameterized SQL queries on `EntityPersistencePort` and `PostgresEntityAdapter`.
  9. **Flutter `NodeStrategy` Union, `@StrictOpaqueIdConverter()` & Studio UI Constructor Parity:** `client_app_v2/lib/features/studio/models/workflow.dart` defines both `Workflow` and the 3-variant `NodeStrategy` union (`Step` wire equivalent: `NodeStrategy.llm`, `NodeStrategy.logic`, `NodeStrategy.causalDiscovery`), and 3 Flutter Studio UI widgets (`profile_editor_view.dart`, `scale_editor_modal.dart`, `workflow_step_card.dart`) construct optimistic Studio models without `organizationId`. All Studio Freezed models MUST enforce `@StrictOpaqueIdConverter() @JsonKey(name: 'organization_id') required String organizationId`.

### Producer-Consumer Integration Check (Section 2.5 Item 2)
* **Producer 2 (`ExecutionAssignmentService` in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`):** Validates optional `task_brief_id` existence and tenant access Fail-Fast at assignment publication time (`create_assignment` and `create_assignment_batch`) and freezes `task_brief_snapshot: TaskAssignmentBriefDTO | None` (`enforce_assignment_task_brief_snapshot_parity`) into `execution_assignments` inside a single atomic `async with uow:` transaction.
* **Consumer 2 (Public Magic-Link Portal & Cohort Management in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` & Flutter `TaskAssignmentPortalView`):** Resolves `get_execution_assignment_by_token_hash` in $O(1)$ via the `token_hash` unique B-Tree index and projects `task_brief=assignment.task_brief_snapshot` onto `ExecutionAssignmentResponseDTO` and `ExecutionAssignmentPreviewDTO` without live `task_briefs` mutation drift.

### Canonical `execution_assignments` PostgreSQL 19 DDL Specification (100% Aligned with `001_pg19_uuidv7_schema.sql` & `enums.py`)

```sql
-- 19. Execution Assignments (Pre-Configured Task Assignments & Cohort Batches)
CREATE TABLE IF NOT EXISTS execution_assignments (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    batch_id UUID,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assigned_email TEXT NOT NULL,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    invited_role TEXT NOT NULL DEFAULT 'MEMBER' CHECK (invited_role IN ('ROOT', 'ADMIN', 'MANAGER', 'MEMBER', 'VIEWER')),
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE RESTRICT,
    task_brief_id UUID REFERENCES task_briefs(id) ON DELETE RESTRICT,
    task_brief_snapshot JSONB,
    target_locale TEXT NOT NULL,
    locked_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    assignee_input_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    draft_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'activated', 'submitted', 'completed', 'expired', 'revoked')),
    email_delivery_status VARCHAR(32) NOT NULL DEFAULT 'pending' CHECK (email_delivery_status IN ('pending', 'sent', 'failed')),
    result_visibility TEXT NOT NULL DEFAULT 'confirmation_only' CHECK (result_visibility IN ('confirmation_only', 'full_report_access')),
    hard_deadline_at TIMESTAMPTZ NOT NULL,
    relative_duration_seconds INTEGER CHECK (relative_duration_seconds IS NULL OR relative_duration_seconds >= 60),
    activated_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_assignment_uuidv7 CHECK (uuid_extract_version(id) = 7),
    CONSTRAINT enforce_assignment_batch_uuidv7 CHECK (batch_id IS NULL OR uuid_extract_version(batch_id) = 7),
    CONSTRAINT enforce_assignment_organization_uuidv7 CHECK (uuid_extract_version(organization_id) = 7),
    CONSTRAINT enforce_assignment_assigned_user_uuidv7 CHECK (assigned_user_id IS NULL OR uuid_extract_version(assigned_user_id) = 7),
    CONSTRAINT enforce_assignment_workflow_uuidv7 CHECK (uuid_extract_version(workflow_id) = 7),
    CONSTRAINT enforce_assignment_output_profile_uuidv7 CHECK (output_profile_id IS NULL OR uuid_extract_version(output_profile_id) = 7),
    CONSTRAINT enforce_assignment_task_brief_uuidv7 CHECK (task_brief_id IS NULL OR uuid_extract_version(task_brief_id) = 7),
    CONSTRAINT enforce_assignment_execution_uuidv7 CHECK (execution_id IS NULL OR uuid_extract_version(execution_id) = 7),
    CONSTRAINT enforce_assignment_created_by_uuidv7 CHECK (uuid_extract_version(created_by) = 7),
    CONSTRAINT enforce_assignment_task_brief_snapshot_parity CHECK (
        (task_brief_id IS NULL AND task_brief_snapshot IS NULL)
        OR (task_brief_id IS NOT NULL AND task_brief_snapshot IS NOT NULL)
    )
);
ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_id UUID REFERENCES task_briefs(id) ON DELETE RESTRICT;
ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_snapshot JSONB;
CREATE INDEX IF NOT EXISTS idx_execution_assignments_org_created ON execution_assignments(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_batch_id ON execution_assignments(batch_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_organization_id ON execution_assignments(organization_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_assigned_user_id ON execution_assignments(assigned_user_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_workflow_id ON execution_assignments(workflow_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_output_profile_id ON execution_assignments(output_profile_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_task_brief_id ON execution_assignments(task_brief_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_execution_id ON execution_assignments(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_created_by ON execution_assignments(created_by);
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L565-L701]`
- `[MODIFY] @[backend_v2/models/auth.py#L110-L129]`
- `[MODIFY] @[backend_v2/models/domain/task_brief.py#L27-L86]`
- `[MODIFY] @[backend_v2/models/domain/prompt_blocks.py#L38-L67]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L42-L225]`
- `[MODIFY] @[backend_v2/models/domain/workflow.py#L30-L279]`
- `[MODIFY] @[backend_v2/models/domain/output_profile.py#L45-L458]`
- `[MODIFY] @[backend_v2/models/dtos/studio.py#L342-L360]`
- `[MODIFY] @[backend_v2/models/dtos/output_profile.py#L519-L661]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L291-L382]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L398-L439]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L235-L285]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L572-L597]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L41-L440]`
- `[MODIFY] @[backend_v2/database/repositories/audit.py#L25-L263]`
- `[MODIFY] @[backend_v2/database/repositories/workflow.py#L26-L499]`
- `[MODIFY] @[backend_v2/services/execution/assignment_service.py#L150-L1959]`
- `[MODIFY] @[backend_v2/services/studio/auth_validator.py#L30-L54]`
- `[MODIFY] @[backend_v2/services/studio/task_brief_service.py#L29-L279]`
- `[MODIFY] @[backend_v2/services/studio/workflow_service.py#L49-L974]`
- `[MODIFY] @[backend_v2/services/studio/prompt_block_service.py#L31-L320]`
- `[MODIFY] @[backend_v2/services/studio/output_profile_service.py#L26-L343]`
- `[MODIFY] @[backend_v2/services/factories/output_profile_factory.py#L86-L184]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L1-L50]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py]`
- `[MODIFY] @[scripts/audit_database_atoms.py]`
- `[MODIFY] @[scripts/sanitize_seed_vault.py]`
- `[MODIFY] @[scripts/audit_dto_parity.py]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/task_brief.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/prompt_block.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/output_profile.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_task_brief.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_auth_validator.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_workflow_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/repositories/test_execution.py]`
- `[MODIFY] @[backend_v2/tests/unit/database/test_repository.py]`
- `[MODIFY] @[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`
- `[MODIFY] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py]`
- `[MODIFY] @[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]`
- `[MODIFY] @[client_app_v2/test/models/domain_parity_test.dart]`

## Phase 3 Deprecations & Sunset Symbols

<demolish>
- `_check_active_assignment_usage`
- `count_executions_by_matrix`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]`, `@[backend_v2/models/domain/task_brief.py#L27-L86]`, `@[backend_v2/models/auth.py#L110-L129]`, `@[backend_v2/models/domain/execution.py#L565-L701]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` & `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]` | Live `TaskBrief` lookup at assignment preview/list time (retroactive instruction mutation), circular-import-inducing mutable `TaskAssignmentBriefDTO(BaseResponseDTO)` in `auth.py`, `strict: bool = False` silent `None` fallback in `_validate_and_resolve_task_brief`, and `ON DELETE SET NULL` / `CASCADE` on `execution_assignments.task_brief_id`, `output_profile_id`, and `workflow_id`. | Define `TaskAssignmentBriefDTO(V2CoreBase)` (`frozen=True`) in `task_brief.py` (re-exported in `auth.py`); add `task_brief_snapshot: TaskAssignmentBriefDTO | None` paired with `task_brief_id` via `@model_validator(mode="after")` and SQL `CONSTRAINT enforce_assignment_task_brief_snapshot_parity`; register `task_brief_snapshot` in `ZORM006` and `ZORM007`; freeze `task_brief_snapshot` at assignment creation (`create_assignment` & `create_assignment_batch`), drop `strict` from `_validate_and_resolve_task_brief`, default `_to_assignment_response` `task_brief` to `assignment.task_brief_snapshot`, and enforce `ON DELETE RESTRICT` on `task_brief_id`, `output_profile_id`, and `workflow_id`. | Do NOT introduce a 3rd `assignment_batches` parent table; keep published cohort rows in `execution_assignments` grouped by indexed nullable `batch_id` + frozen `task_brief_snapshot JSONB` for 0-join magic-link portal lookups. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/task_brief.py backend_v2/models/domain/execution.py backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py backend_v2/services/execution/assignment_service.py scripts/audit_zero_orm_strictness.py backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict` |
| `@[backend_v2/seed/seed_data.json#L1-L50]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/audit_database_atoms.py]`, `@[scripts/audit_dto_parity.py]`, `@[backend_v2/models/domain/prompt_blocks.py#L38-L67]`, `@[backend_v2/models/domain/step.py#L42-L225]`, `@[backend_v2/models/domain/workflow.py#L30-L279]`, `@[backend_v2/models/domain/output_profile.py#L45-L458]`, `@[backend_v2/models/dtos/studio.py#L342-L360]`, `@[backend_v2/models/dtos/output_profile.py#L519-L661]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L398-L439]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L235-L285]`, `@[backend_v2/database/repositories/workflow.py#L26-L499]`, `@[backend_v2/services/studio/auth_validator.py#L30-L54]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, `@[backend_v2/services/studio/workflow_service.py#L49-L974]`, `@[backend_v2/services/studio/prompt_block_service.py#L31-L320]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L343]`, `@[backend_v2/services/factories/output_profile_factory.py#L86-L184]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]`, `@[backend_v2/tests/unit/models/domain/test_task_brief.py]`, `@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`, `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`, `@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`, `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]` & `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]` | `organization_id ON DELETE SET NULL`, `None` / `"SYSTEM"` sentinels across Studio tables, `_format_org_uuid7` / `default_system=True` adapter shims, `OutputProfileResponseDTO` `exclude=True` wire stripping, `sanitize_task_briefs` stripping `organization_id`, and Python full-table scan `_check_active_assignment_usage`. | Hydrate `"organization_id": "org_0195f3a0000070008000000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all 119 unhydrated Studio seed rows (bringing all 120 tenant-scoped system seed rows across 6 collections to `ROOT_SYSTEM`); add idempotent pre-seed SQL backfill + `NOT NULL ON DELETE CASCADE` migration; add module-level `resolve_create_organization_id` in `auth_validator.py`; remove `"SYSTEM"` shims across `SystemOrganizations`, `coercion_and_constants.py`, stage hydrators, `repositories/workflow.py`, `sanitize_seed_vault.py`, and `audit_database_atoms.py`; expose non-excluded `organization_id` on `OutputProfileResponseDTO` and `_to_output_profile_dto`; enforce `ON DELETE RESTRICT` in SQL and `InMemoryUnitOfWork`; and delete `_check_active_assignment_usage`. | Rely directly on PostgreSQL 19 `ON DELETE RESTRICT` (`SQLSTATE 23503` -> `ErrorCodes.DELETE_BLOCKED_BY_USAGE`) and `ON DELETE CASCADE` without Python multi-table loops; touch ZERO coaching prompts in `seed_data.json` and keep global `model_registries` free of `organization_id`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/postgres/entity_adapter/ backend_v2/database/repositories/workflow.py backend_v2/services/studio/ backend_v2/services/factories/output_profile_factory.py scripts/sanitize_seed_vault.py scripts/audit_database_atoms.py backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/models/domain/test_task_brief.py backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/database/postgres/entity_adapter/ backend_v2/tests/unit/scripts/test_audit_database_atoms.py backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict` |
| `@[backend_v2/database/interfaces.py#L291-L382]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L572-L597]`, `@[backend_v2/database/repositories/execution.py#L41-L440]`, `@[backend_v2/database/repositories/audit.py#L25-L263]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `@[backend_v2/tests/unit/database/repositories/test_execution.py]`, `@[backend_v2/tests/unit/database/test_repository.py]` & `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]` | $O(N)$ Python table scans in `_find_assignment_by_token_hash`, `get_assignment_by_execution_id`, `list_assignments`, `ExecutionRepositoryImpl.get_all_executions` / `get_recent_completed_executions`, and `AuditRepositoryImpl.get_detailed_usage`, plus unused `count_executions_by_matrix`. | Expose `get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization` (supporting optional `batch_id` and `workflow_id`), and `list_executions_filtered` across `EntityPersistencePort`, `PostgresEntityAdapter`, and `InMemoryEntityAdapter` backed by parameterized `$1, $2` SQL `WHERE`, `ORDER BY id DESC`, and `LIMIT` clauses and B-Tree indexes (`idx_execution_assignments_org_created`, `idx_execution_assignments_batch_id`, `idx_executions_org_id_created`), wire repositories and services to these methods, and drop `count_executions_by_matrix`. | Expose explicit domain-typed query methods on `EntityPersistencePort` without inventing any generic filter/ORM DSL. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/fakes/ backend_v2/tests/unit/database/ backend_v2/tests/unit/fakes/test_in_memory_repositories.py --test --ast-strict` |
| `@[client_app_v2/lib/features/studio/models/task_brief.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/output_profile.dart]`, `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`, `@[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]` & `@[client_app_v2/test/models/domain_parity_test.dart]` | Nullable `String? organizationId` fields on Flutter Studio Freezed models (`TaskBrief`, `Workflow`, `NodeStrategy`, `PromptBlock`, `OutputProfile`), missing `@StrictOpaqueIdConverter()`, and Studio UI constructors omitting `organizationId`. | Enforce `@StrictOpaqueIdConverter() @JsonKey(name: 'organization_id') required String organizationId` across `TaskBrief`, `Workflow`, all 3 `NodeStrategy` variants, all 6 `PromptBlock` variants, and `OutputProfile` (`disallowUnrecognizedKeys: true`), and bind explicit `organizationId` in `profile_editor_view.dart`, `scale_editor_modal.dart`, and `workflow_step_card.dart`. | Maintain 1:1 full-duplex serialization parity verified automatically by `audit_dto_parity.py --fail-on-mismatch` (including `OutputProfileResponseDTO` -> `OutputProfile`). | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md#L1-L120]`, `@[.agents/rules/03_seed_vault.md]`, `@[backend_v2/models/domain/execution.py#L565-L701]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, and `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`.</action>
    <action>Look forward: Verify Step 3.1 moves `TaskAssignmentBriefDTO` onto frozen `V2CoreBase` in `task_brief.py`, freezes `task_brief_snapshot JSONB` at assignment creation (`create_assignment` and `create_assignment_batch`), and drops `strict: bool = False`; Step 3.2 enforces `ON DELETE RESTRICT` on `execution_assignments` FKs and `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across all 120 tenant-scoped `ROOT_SYSTEM` seed rows (`119` Studio rows hydrated + `1` existing `mcp_gateways` row), SQL migrations, Studio adapters/services/DTOs, and `InMemoryUnitOfWork`; Step 3.3 pushes assignment and execution lookups down to $O(1)$ indexed SQL queries on `EntityPersistencePort` and `PostgresEntityAdapter`; and Step 3.4 synchronizes Flutter Studio Freezed `organizationId` parity across models, `NodeStrategy`, Studio UI widgets, and test suites.</action>
    <constraint invariant="prompt_preservation_mandate">When hydrating `"organization_id": "org_0195f3a0000070008000000000000001"` across the 119 unhydrated Studio seed records in `backend_v2/seed/seed_data.json`, store a timestamped backup in `backend_v2/seed/backups/` first, preserve 100% of `system_prompt`, `ai_description`, `instruction_text`, and matrix rubric text verbatim, and NEVER add `organization_id` to global `model_registries`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/03_phase3_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L565-L701]</backend>
    <backend>@[backend_v2/models/auth.py#L110-L129]</backend>
    <backend>@[backend_v2/models/domain/task_brief.py#L27-L86]</backend>
    <backend>@[backend_v2/models/domain/prompt_blocks.py#L38-L67]</backend>
    <backend>@[backend_v2/models/domain/step.py#L42-L225]</backend>
    <backend>@[backend_v2/models/domain/workflow.py#L30-L279]</backend>
    <backend>@[backend_v2/models/domain/output_profile.py#L45-L458]</backend>
    <backend>@[backend_v2/models/dtos/studio.py#L342-L360]</backend>
    <backend>@[backend_v2/models/dtos/output_profile.py#L519-L661]</backend>
    <backend>@[backend_v2/database/interfaces.py#L291-L382]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L398-L439]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L235-L285]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L572-L597]</backend>
    <backend>@[backend_v2/database/repositories/execution.py#L41-L440]</backend>
    <backend>@[backend_v2/database/repositories/audit.py#L25-L263]</backend>
    <backend>@[backend_v2/database/repositories/workflow.py#L26-L499]</backend>
    <backend>@[backend_v2/services/execution/assignment_service.py#L150-L1959]</backend>
    <backend>@[backend_v2/services/studio/auth_validator.py#L30-L54]</backend>
    <backend>@[backend_v2/services/studio/task_brief_service.py#L29-L279]</backend>
    <backend>@[backend_v2/services/studio/workflow_service.py#L49-L974]</backend>
    <backend>@[backend_v2/services/studio/prompt_block_service.py#L31-L320]</backend>
    <backend>@[backend_v2/services/studio/output_profile_service.py#L26-L343]</backend>
    <backend>@[backend_v2/services/factories/output_profile_factory.py#L86-L184]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L1-L50]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py]</backend>
    <backend>@[scripts/audit_database_atoms.py]</backend>
    <backend>@[scripts/sanitize_seed_vault.py]</backend>
    <backend>@[scripts/audit_dto_parity.py]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/task_brief.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/output_profile.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_task_brief.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_auth_validator.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_workflow_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/database/repositories/test_execution.py]</backend>
    <backend>@[backend_v2/tests/unit/database/test_repository.py]</backend>
    <backend>@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]</backend>
    <backend>@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</backend>
    <frontend>@[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]</frontend>
    <frontend>@[client_app_v2/test/models/domain_parity_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`TaskAssignmentBriefDTO(V2CoreBase)` (`frozen=True`) lives in `@[backend_v2/models/domain/task_brief.py#L27-L86]` (re-exported in `@[backend_v2/models/auth.py#L110-L129]`), `ExecutionAssignment` in `@[backend_v2/models/domain/execution.py#L565-L701]` and `execution_assignments` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]` enforce `task_brief_snapshot: TaskAssignmentBriefDTO | None` paired with `task_brief_id` via `@model_validator(mode="after")` and SQL `CONSTRAINT enforce_assignment_task_brief_snapshot_parity`, `ZORM006` and `ZORM007` register `task_brief_snapshot` in `@[scripts/audit_zero_orm_strictness.py]`, and `ExecutionAssignmentService` freezes `task_brief_snapshot` in `create_assignment` and `create_assignment_batch` while dropping `strict: bool = False` from `_validate_and_resolve_task_brief`.</item>
    <item>`execution_assignments.task_brief_id`, `output_profile_id`, and `workflow_id` enforce `ON DELETE RESTRICT` in SQL and `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]` (`_check_active_assignment_usage` deleted from `StudioTaskBriefService`), and all 120 tenant-scoped system seed rows in `@[backend_v2/seed/seed_data.json#L1-L50]` (`119` Studio rows hydrated + `1` existing `mcp_gateways` row) plus all tenant-scoped SQL tables, PostgreSQL hydrators (`coercion_and_constants.py` without `"SYSTEM"` shims), Python Studio models/DTOs (including non-excluded `OutputProfileResponseDTO.organization_id`), and `resolve_create_organization_id` in `auth_validator.py` enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` (`org_0195f3a0000070008000000000000001` for `ROOT_SYSTEM`).</item>
    <item>`EntityPersistencePort` (`@[backend_v2/database/interfaces.py#L291-L382]`), `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]`), and `InMemoryEntityAdapter` expose $O(1)$ indexed SQL methods `get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization`, and `list_executions_filtered`, wired into `ExecutionAssignmentService`, `ExecutionRepositoryImpl`, and `AuditRepositoryImpl` while dropping `count_executions_by_matrix`.</item>
    <item>Flutter Studio Freezed models (`TaskBrief`, `Workflow`, `NodeStrategy`, `PromptBlock`, `OutputProfile`) and their 3 Studio UI callers (`profile_editor_view.dart`, `scale_editor_modal.dart`, `workflow_step_card.dart`) enforce `@StrictOpaqueIdConverter() @JsonKey(name: 'organization_id') required String organizationId` and pass `audit_dto_parity.py --fail-on-mismatch` and `flutter_audit_loop.py client_app_v2/ --build`.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
    <knowledge_item>@[ki_frontend_iam_role_segregation.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_mcp_gateway_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT introduce a 3rd `assignment_batches` parent table; retain cohort grouping via indexed nullable `batch_id UUID` + frozen `task_brief_snapshot JSONB` on `execution_assignments`.</anti_target>
    <anti_target>Do NOT retain `strict: bool = False` in `_validate_and_resolve_task_brief`, `"SYSTEM"` / `default_system=True` coercion shims in `coercion_and_constants.py`, or `ON DELETE SET NULL` on `organization_id` (`zero_backward_compatibility_planning_ban`).</anti_target>
    <anti_target>Do NOT rename wire key `task_brief` on `ExecutionAssignmentResponseDTO` or `ExecutionAssignmentPreviewDTO`; map `task_brief=assignment.task_brief_snapshot` to preserve 1:1 Flutter `ExecutionAssignmentResponseDto` / `ExecutionAssignmentPreviewDto` parity.</anti_target>
    <anti_target>Do NOT add `organization_id` to global `model_registries` in `seed_data.json` (`SystemConfigModelRegistry` enforces `extra="forbid"`), and NEVER emit the substring `"UPDATE executions"` in `001_pg19_uuidv7_schema.sql` (`test_execution_and_report_stage.py` invariant).</anti_target>
  </anti_targets>

  <step id="3.1" name="Immutable task_brief_snapshot JSONB Parity &amp; Fail-Fast TaskBrief Resolution on execution_assignments">
    <action>1. `[MODIFY]` `@[backend_v2/models/domain/task_brief.py#L27-L86]`, `@[backend_v2/models/auth.py#L110-L129]`, and `@[backend_v2/models/domain/execution.py#L565-L701]`: Move `TaskAssignmentBriefDTO` into `backend_v2/models/domain/task_brief.py` inheriting `V2CoreBase` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with its exact 4 wire fields (`id`, `label`, `instruction_text`, `source_url`), re-export `TaskAssignmentBriefDTO` in `backend_v2/models/auth.py` (`__all__`) to prevent circular imports between `auth.py` and `execution.py`, and add `task_brief_snapshot: Annotated[TaskAssignmentBriefDTO | None, Field(default=None, description="Frozen publication-time snapshot of TaskBrief instructions and metadata when task_brief_id is set")] = None` paired with an `@model_validator(mode="after")` enforcing `(self.task_brief_id is None) == (self.task_brief_snapshot is None)` on `ExecutionAssignment`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, and `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`: Add `task_brief_snapshot JSONB` (in both `CREATE TABLE IF NOT EXISTS execution_assignments` and `ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS task_brief_snapshot JSONB`), uppercase `UserRole` (`DEFAULT 'MEMBER'`), `AssignmentStatus` (including `'completed'`), `EmailDeliveryStatus`, and `AssignmentResultVisibility` (`'confirmation_only'`, `'full_report_access'`) `CHECK` constraints, `NOT NULL` `hard_deadline_at`, all 9 `enforce_assignment_*_uuidv7` checks, and `CONSTRAINT enforce_assignment_task_brief_snapshot_parity` in `001_pg19_uuidv7_schema.sql` (including an idempotent `DO $$` backfill of `task_brief_snapshot` from `task_briefs` for any pre-existing `execution_assignments` rows before adding the parity constraint). Register `"task_brief_snapshot"` in `APPROVED_ADAPTER_RECORD_COLUMNS` (`ZORM006`) and `REQUIRED_IDEMPOTENT_ALTER_COLUMNS["execution_assignments"]` (`ZORM007`) in `scripts/audit_zero_orm_strictness.py`, and serialize/hydrate `task_brief_snapshot` via `validate_hydrated_row` in `iam_and_system_stage.py` (`upsert_execution_assignment_row` and `hydrate_execution_assignment_row`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` and `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`: Populate `task_brief_snapshot` at assignment creation (`create_assignment` and `create_assignment_batch`) whenever `task_brief_id` is supplied after Fail-Fast validation of `task_brief_id` existence and tenant access; drop the `strict: bool = False` parameter from `_validate_and_resolve_task_brief` (eliminating `_to_hydrated_assignment_response` live `task_briefs` lookups); and default `task_brief` in `_to_assignment_response` directly to `assignment.task_brief_snapshot` across `ExecutionAssignmentResponseDTO` and `ExecutionAssignmentPreviewDTO`.</action>
    <constraint invariant="immutable_history_snapshot">Editing a `TaskBrief` in Studio after publishing an assignment MUST NEVER mutate the instructions or metadata rendered for already-published or completed `ExecutionAssignment` rows.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/task_brief.py backend_v2/models/auth.py backend_v2/models/domain/execution.py backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py backend_v2/services/execution/assignment_service.py scripts/audit_zero_orm_strictness.py backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict</audit_command>
  </step>

  <step id="3.2" name="Kernel-Level ON DELETE RESTRICT &amp; ROOT_SYSTEM organization_id NOT NULL ON DELETE CASCADE Across All 120 Tenant-Scoped System Seed Rows">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]`, and `@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`: Enforce `ON DELETE RESTRICT` on `execution_assignments.task_brief_id`, `execution_assignments.output_profile_id`, and `execution_assignments.workflow_id` in `001_pg19_uuidv7_schema.sql` (including idempotent `DROP CONSTRAINT IF EXISTS ... / ADD CONSTRAINT ... ON DELETE RESTRICT` migration for existing Phase 2 databases) and in `InMemoryEntityAdapter` (`delete_task_brief`, `delete_workflow`, `_is_output_profile_referenced`) + `InMemoryAsyncPgConnection.execute` (`ErrorCodes.DELETE_BLOCKED_BY_USAGE`, `status_code=400`), delete `_check_active_assignment_usage` from `StudioTaskBriefService`, and rewire `test_task_brief_service.py` from disconnected `InMemoryTaskBriefRepository()` onto `TaskBriefRepositoryImpl(uow_factory=lambda: uow)`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/seed/seed_data.json#L1-L50]`, `@[scripts/sanitize_seed_vault.py]`, `@[scripts/audit_database_atoms.py]`, `@[backend_v2/tests/unit/scripts/test_audit_database_atoms.py]`, and `@[backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py]`: Create a timestamped backup in `backend_v2/seed/backups/` and hydrate `"organization_id": "org_0195f3a0000070008000000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all **119** unhydrated Studio seed records (`90` in `prompt_blocks`, `2` in `task_briefs`, `3` in `workflows`, `21` in `steps`, and `3` in `output_profiles`), bringing all **120** tenant-scoped system seed records (including `1` existing record in `mcp_gateways`) to canonical `ROOT_SYSTEM` while leaving global `model_registries` (`3` records) untouched. Remove `"organization_id"` stripping from `sanitize_task_briefs` in `scripts/sanitize_seed_vault.py`, and remove `_SYSTEM_ORGANIZATION_SENTINELS` (`"SYSTEM"`) while enforcing required non-null `organization_id` FK membership across all 6 tenant-scoped collections in `scripts/audit_database_atoms.py`. Add an idempotent pre-seed `DO $$` block in `001_pg19_uuidv7_schema.sql` (ensuring `0195f3a0-0000-7000-8000-000000000001` exists in `organizations` when `NULL` Studio rows are present, backfilling `organization_id` across `prompt_blocks`, `task_briefs`, `steps`, `workflows`, and `output_profiles`, replacing `ON DELETE SET NULL` FKs with `ON DELETE CASCADE`, removing `organization_id IS NULL OR` from `enforce_*_organization_uuidv7` checks, and setting `ALTER COLUMN organization_id SET NOT NULL` without emitting `"UPDATE executions"`).</action>
    <action>3. `[MODIFY]` `@[backend_v2/models/auth.py#L110-L129]`, `@[backend_v2/models/domain/task_brief.py#L27-L86]`, `@[backend_v2/models/domain/prompt_blocks.py#L38-L67]`, `@[backend_v2/models/domain/step.py#L42-L225]`, `@[backend_v2/models/domain/workflow.py#L30-L279]`, `@[backend_v2/models/domain/output_profile.py#L45-L458]`, `@[backend_v2/models/dtos/studio.py#L342-L360]`, `@[backend_v2/models/dtos/output_profile.py#L519-L661]`, `@[scripts/audit_dto_parity.py]`, `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L251-L269]`, `@[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py#L398-L439]`, `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L235-L285]`, `@[backend_v2/database/repositories/workflow.py#L26-L499]`, `@[backend_v2/services/studio/auth_validator.py#L30-L54]`, `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`, `@[backend_v2/services/studio/workflow_service.py#L49-L974]`, `@[backend_v2/services/studio/prompt_block_service.py#L31-L320]`, `@[backend_v2/services/studio/output_profile_service.py#L26-L343]`, `@[backend_v2/services/factories/output_profile_factory.py#L86-L184]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/unit/models/domain/test_task_brief.py]`, `@[backend_v2/tests/unit/services/studio/test_auth_validator.py]`, `@[backend_v2/tests/unit/services/studio/test_workflow_service.py]`, `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py]`, `@[backend_v2/tests/unit/services/studio/test_output_profile_service.py]`, `@[backend_v2/tests/unit/services/studio/test_settings_persistence_rca.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, and `@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`: Update `SystemOrganizations.is_system` to match `cls.ROOT_SYSTEM.value` strictly (rejecting `None` and `"SYSTEM"`); remove `"SYSTEM"` and `default_system` shims from `_parse_org_uuid7` and `_format_org_uuid7` in `coercion_and_constants.py` (preserving `None -> None` on corrupt-row hydration so `validate_hydrated_row` raises HTTP 500 `ErrorCodes.VALIDATION_FAILED` with `table_name` and `entity_id`) and enforce `parse_prefixed_uuid7(..., EntityPrefix.ORGANIZATION)` in `prompt_block_and_step_stage.py`, `workflow_and_profile_stage.py`, and `repositories/workflow.py`; add module-level `resolve_create_organization_id(initiator: TokenData) -> str` in `auth_validator.py` (returning `ROOT_SYSTEM` on `SystemOrganizations` for `UserRole.ROOT` and raising `PermissionDeniedError` 403 when a non-`ROOT` initiator lacks `organization_id`) and wire it into `StudioTaskBriefService`, `StudioWorkflowService` (including passing `organization_id=profile.organization_id` in `_to_output_profile_dto`), `StudioPromptBlockService`, `StudioOutputProfileService`, and `build_draft_output_profile` in `output_profile_factory.py`; enforce non-nullable `organization_id: str` validated for `EntityPrefix.ORGANIZATION` across `PromptBlockBase`, `TaskBrief`, `Step`, `Workflow`, `OutputProfile`, `WorkflowResponseDTO`, `StepResponseDTO`, `TaskBriefResponseDTO`, and `OutputProfileResponseDTO` (explicitly setting `exclude=False` to override `BaseResponseDTO` wire stripping and registering `"outputprofileresponsedto": "outputprofile"` in `scripts/audit_dto_parity.py`); and update `StepFactory.organization_id` in `model_factories.py` (`generate_opaque_id(EntityPrefix.ORGANIZATION)`) plus local Studio constructors/factories across companion tests.</action>
    <constraint invariant="service_tenant_rbac_isolation_mandate">Deleting a tenant `Organization` row MUST cascade-delete its tenant-owned Studio entities and assignments without ever setting `organization_id` to `NULL` or exposing private templates as global `ROOT_SYSTEM` resources.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/postgres/entity_adapter/ backend_v2/database/repositories/workflow.py backend_v2/services/studio/ backend_v2/services/factories/output_profile_factory.py scripts/sanitize_seed_vault.py scripts/audit_database_atoms.py backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/models/domain/test_task_brief.py backend_v2/tests/unit/services/studio/ backend_v2/tests/unit/database/postgres/entity_adapter/ backend_v2/tests/unit/scripts/test_audit_database_atoms.py backend_v2/tests/unit/scripts/test_sanitize_seed_vault.py backend_v2/tests/integration/test_sdui_semantic_parity.py --test --ast-strict</audit_command>
  </step>

  <step id="3.3" name="O(1) Indexed SQL Query Pushdown for Execution Assignments &amp; Executions">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L658]`, `@[backend_v2/database/interfaces.py#L291-L382]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py#L208-L1212]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L852-L897]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L572-L597]`, `@[backend_v2/database/repositories/execution.py#L41-L440]`, `@[backend_v2/database/repositories/audit.py#L25-L263]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L759-L2233]`, `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `@[backend_v2/tests/unit/database/repositories/test_execution.py]`, `@[backend_v2/tests/unit/database/test_repository.py]`, and `@[backend_v2/tests/unit/fakes/test_in_memory_repositories.py]`: Add `idx_execution_assignments_org_created`, `idx_execution_assignments_batch_id`, and `idx_executions_org_id_created` (preserving existing `idx_execution_assignments_task_brief_id` and `idx_execution_assignments_execution_id`) in `001_pg19_uuidv7_schema.sql`. Expose and implement `get_execution_assignment_by_token_hash(token_hash: str) -> ExecutionAssignment | None`, `get_execution_assignment_by_execution_id(execution_id: str) -> ExecutionAssignment | None`, `list_execution_assignments_by_organization(organization_id: str, *, batch_id: str | None = None, workflow_id: str | None = None, limit: int = 100) -> list[ExecutionAssignment]`, and `list_executions_filtered(*, organization_id: str | None = None, created_by: str | None = None, workflow_id: str | None = None, status: ExecutionStatus | None = None, limit: int = 100) -> list[ExecutionRecord]` across `EntityPersistencePort`, `PostgresEntityAdapter` (plus `iam_and_system_stage.py` and `execution_and_report_stage.py`), and `InMemoryEntityAdapter` + `InMemoryAsyncPgConnection` using parameterized `$1, $2` SQL `WHERE`, `ORDER BY id DESC`, and `LIMIT` clauses. Replace $O(N)$ Python table scans in `ExecutionAssignmentService._find_assignment_by_token_hash`, `get_assignment_by_execution_id`, and `list_assignments`, `ExecutionRepositoryImpl.get_all_executions` and `get_recent_completed_executions` (preserving `limit <= 0 -> []` and `_completed_at_sort_key` ordering over `status=ExecutionStatus.PASSED`), and `AuditRepositoryImpl.get_detailed_usage` with these indexed SQL methods, and delete `count_executions_by_matrix` from `IExecutionRepository`, `ExecutionRepositoryImpl`, `InMemoryExecutionRepository`, `InMemoryUnifiedWorkflowRepository`, and repository unit tests.</action>
    <constraint invariant="primary_key_lookup_o1_mandate">Portal magic-link token lookups (`get_execution_assignment_by_token_hash`) and tenant cohort/execution queries MUST execute in $O(1)$ / indexed SQL without full-table Python scans.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/services/execution/assignment_service.py backend_v2/tests/fakes/ backend_v2/tests/unit/database/ backend_v2/tests/unit/fakes/test_in_memory_repositories.py backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict</audit_command>
  </step>

  <step id="3.4" name="Flutter Studio Freezed organizationId Non-Null Parity Across Models, NodeStrategy &amp; Studio Views">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/studio/models/task_brief.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/output_profile.dart]`, `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`, `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`, `@[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]`, and `@[client_app_v2/test/models/domain_parity_test.dart]`: Update `organizationId` across `TaskBrief`, `Workflow` + all 3 `NodeStrategy` union constructors (`NodeStrategy.llm`, `NodeStrategy.logic`, `NodeStrategy.causalDiscovery`), all 6 `PromptBlock` union constructors, and `OutputProfile` Freezed models from nullable `String?` to `@StrictOpaqueIdConverter() @JsonKey(name: 'organization_id') required String organizationId` (with zero `@Default` fallback); pass explicit `organizationId` in `profile_editor_view.dart`, `scale_editor_modal.dart`, and `workflow_step_card.dart`; regenerate `.freezed.dart` and `.g.dart` siblings; and update `task_brief_test.dart`, `domain_parity_test.dart`, and Studio model/widget test constructors across `client_app_v2/test/` to assert Fail-Fast Freezed deserialization failure (`CheckedFromJsonException`) when `organization_id` is `null`, omitted, or `"SYSTEM"`.</action>
    <constraint invariant="silent_json_fallbacks">Missing, `null`, or non-UUIDv7 `"SYSTEM"` `organization_id` payloads on Studio DTOs MUST crash the Freezed parser immediately (`@StrictOpaqueIdConverter()` + `disallowUnrecognizedKeys: true`).</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</audit_command>
  </step>

  <test_contracts>
    <test name="test_published_assignment_task_brief_snapshot_immune_to_subsequent_studio_edits" category="positive">
      <input>Create `TaskBrief` via `TaskBriefFactory.build(...)`, publish `ExecutionAssignment` with `task_brief_id`, then update `TaskBrief.instruction_text` in Studio and call `preview_assignment`, `list_assignments`, and `get_assignment_by_execution_id`</input>
      <expected>Published `ExecutionAssignmentResponseDTO.task_brief` and `ExecutionAssignmentPreviewDTO.task_brief` retain the exact publication-time `task_brief_snapshot` instructions without drift</expected>
    </test>
    <test name="test_execution_assignment_without_task_brief_id_satisfies_snapshot_parity" category="boundary">
      <input>`ExecutionAssignmentFactory.build(task_brief_id=None, task_brief_snapshot=None)` persisted and re-fetched</input>
      <expected>Passes both Pydantic `@model_validator(mode="after")` and SQL `enforce_assignment_task_brief_snapshot_parity` with `task_brief=None`</expected>
    </test>
    <test name="test_execution_assignment_mismatched_task_brief_id_and_snapshot_raises_validation_error" category="negative">
      <input>`ExecutionAssignment` instantiated with `task_brief_id="tbr_..."` and `task_brief_snapshot=None` (or `task_brief_id=None` and non-null `task_brief_snapshot`)</input>
      <expected>Fails fast with Pydantic `ValidationError` (and SQL `CheckViolationError` if bypassed)</expected>
    </test>
    <test name="test_create_assignment_with_missing_or_cross_tenant_task_brief_fails_fast" category="negative">
      <input>`ExecutionAssignmentService.create_assignment` and `create_assignment_batch` called with non-existent `task_brief_id` or another tenant's `task_brief_id`</input>
      <expected>Raises `AppException` (`ErrorCodes.RESOURCE_NOT_FOUND` 404 or `ErrorCodes.FORBIDDEN` 403) with zero `strict=False` fallback</expected>
    </test>
    <test name="test_delete_task_brief_referenced_by_assignment_raises_delete_blocked_by_usage" category="negative">
      <input>`StudioTaskBriefService.delete_task_brief` called on a `TaskBrief` referenced by an existing `ExecutionAssignment`</input>
      <expected>Raises `AppException(ErrorCodes.DELETE_BLOCKED_BY_USAGE, status_code=400)` via kernel `ON DELETE RESTRICT` (`SQLSTATE 23503`) without `_check_active_assignment_usage` Python scan</expected>
    </test>
    <test name="test_delete_tenant_organization_cascades_studio_entities_with_zero_null_promotion" category="positive">
      <input>Tenant `Organization` owning `TaskBrief`, `PromptBlock`, `Step`, `Workflow`, `OutputProfile`, and `ExecutionAssignment` rows is deleted</input>
      <expected>All tenant-owned rows cascade-delete cleanly; zero rows survive with `organization_id=None` or become visible to other tenants</expected>
    </test>
    <test name="test_studio_models_and_dtos_reject_none_or_legacy_system_organization_id_and_serialize_organization_id" category="negative">
      <input>`TaskBrief.model_validate`, `Workflow.model_validate`, `Step.model_validate`, `OutputProfile.model_validate`, or Flutter `TaskBrief.fromJson` / `NodeStrategy.fromJson` called with `organization_id=None` or `organization_id="SYSTEM"`, plus `OutputProfileResponseDTO.model_dump(mode="json")`</input>
      <expected>Invalid inputs fail fast with `ValidationError` / Dart `CheckedFromJsonException`, and `OutputProfileResponseDTO.model_dump(mode="json")` emits `"organization_id"` without `exclude=True` stripping</expected>
    </test>
    <test name="test_indexed_assignment_and_execution_queries_filter_and_order_deterministically" category="positive">
      <input>`get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization(batch_id=..., workflow_id=...)`, and `list_executions_filtered(organization_id=..., status=..., limit=1)`</input>
      <expected>Returns exact matching typed models ordered by `id DESC` within `limit` and `None`/`[]` on non-matching predicates</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</command>
  </validation_gate>
</execution_protocol>
