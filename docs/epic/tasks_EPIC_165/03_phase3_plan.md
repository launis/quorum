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

**Overview:** Harden the 2-table `task_briefs` (`tbr_<hex32>`) <-> `execution_assignments` (`tsk_<hex32>`) architecture by freezing an immutable `task_brief_snapshot: TaskAssignmentBriefDTO | None` (`JSONB` paired with `task_brief_id` via `enforce_assignment_task_brief_snapshot_parity`) at cohort assignment publication time in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` and dropping the silent `strict: bool = False` compromise in `_validate_and_resolve_task_brief`. Upgrade `execution_assignments.task_brief_id`, `execution_assignments.output_profile_id`, and `execution_assignments.workflow_id` to kernel-level `ON DELETE RESTRICT` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` (eliminating the full-table Python scan `_check_active_assignment_usage` in `@[backend_v2/services/studio/task_brief_service.py#L83-L123]`), hydrate `"organization_id": "org_0195f3a0000070008000000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all 123 system-owned seed records in `@[backend_v2/seed/seed_data.json#L1-L50]` (`1` in `mcp_gateways`, `90` in `prompt_blocks`, `2` in `task_briefs`, `3` in `workflows`, `21` in `steps`, and `3` in `output_profiles`), enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across SQL, Python Studio domain/DTO models, `StudioAuthValidator.resolve_create_organization_id`, and Flutter Studio Freezed models (`task_brief.dart`, `workflow.dart`, `prompt_block.dart`, `output_profile.dart`), and push $O(N)$ Python table scans down into $O(1)$ indexed parameterized SQL queries on `EntityPersistencePort`.

**Source:** `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]` and `@[docs/epic/EPIC_165_audit_report.md]`

## Phase 3 Forensic Context, Producer-Consumer Contracts & SQL DDL (Verbatim from EPIC 165)

### Forensic Finding 5 [P1 HIGH]: `task_briefs` <-> `execution_assignments` Published Cohort Mutability, Silent `strict=False` Fallback & Multi-Tenant `ON DELETE SET NULL` Escalation
* **Forensic Anchors:**
  * `@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md#L1-L120]`
  * `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` (`task_briefs` and `execution_assignments` DDL, lines 400–485)
  * `@[backend_v2/models/domain/execution.py#L541-L677]`, `@[backend_v2/models/auth.py#L109-L128]`, and `@[backend_v2/services/studio/auth_validator.py#L30-L54]`
  * `@[backend_v2/services/studio/task_brief_service.py#L83-L123]` (`_check_active_assignment_usage`)
  * `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` (`_validate_and_resolve_task_brief`)
* **Architectural Verdict on the 2-Table Split (`task_briefs` vs. `execution_assignments`):**
  * Separating reusable **Task Brief Templates (`task_briefs`, `tbr_<hex32>`)** from **Published Cohort Assignments (`execution_assignments`, `tsk_<hex32>`)** is **100% textbook relational design** (1:N Definition/Catalog vs. Dispatched Recipient Instance). Extracting `task_briefs` out of `prompt_blocks` cured the Single-Table Inheritance smell where human task briefs carried 14 `NULL` BARS matrix columns.
  * Modeling a published subset of recipients (`POST /api/v2/assignments/batch`, 1 to 500 recipients) as individual rows in `execution_assignments` sharing a cohort `batch_id UUID` is also the right relational grain: each recipient requires an independent single-use token digest (`token_hash TEXT NOT NULL UNIQUE`), an independent state lifecycle (`status: pending -> activated -> submitted -> expired/revoked`), an independent activation countdown (`activated_at` + `relative_duration_seconds`), independent `draft_inputs`, and a 1:1 `execution_id` link, while avoiding a 3-table join on hot portal token lookups.
* **Five Concrete Structural Defects Closed in Phase 3 (Including Finding 7 Site 7):**
  1. **Retroactive Mutation of Published Cohort Assignments (`immutable_history_snapshot` Violation):** `execution_assignments` stores only `task_brief_id` and resolves `TaskBrief` dynamically at preview/list time (`_validate_and_resolve_task_brief`). Editing `TaskBrief.instruction_text` in Studio after publishing a task to a cohort retroactively alters published and historical assignment instructions unless frozen into `task_brief_snapshot JSONB` at publication time.
  2. **Silent `strict=False` Fallback Compromise (Finding 7 Site 7):** `_validate_and_resolve_task_brief` defines `strict: bool = True`, and both `preview_assignment` and `_to_hydrated_assignment_response` pass `strict=False`, silently returning `task_brief=None` when `task_brief_repo` is missing, the `TaskBrief` row is missing, or tenant ownership fails (`zero_backward_compatibility_planning_ban`).
  3. **`ON DELETE SET NULL` vs. `ON DELETE RESTRICT` Contradiction:** SQL declares `task_brief_id UUID REFERENCES task_briefs(id) ON DELETE SET NULL` (and `output_profile_id ... ON DELETE SET NULL`), while `StudioTaskBriefService._check_active_assignment_usage` loads 100% of `execution_assignments` across all tenants into Python RAM (`list_execution_assignments()`) to raise `ErrorCodes.DELETE_BLOCKED_BY_USAGE`.
  4. **Critical Multi-Tenant Leak via `organization_id ON DELETE SET NULL`:** `SystemOrganizations.is_system(org_id)` evaluates `return not org_id or org_id in (cls.ROOT_SYSTEM.value, "SYSTEM")`. Because `organization_id IS NULL` means "globally accessible `SYSTEM` template", declaring `organization_id UUID REFERENCES organizations(id) ON DELETE SET NULL` on `task_briefs`, `prompt_blocks`, `steps`, `workflows`, and `output_profiles` means deleting a customer tenant organization sets its private rows' `organization_id` to `NULL`—instantly promoting private customer templates into global `SYSTEM` resources visible to all other tenants.
  5. **Missing Cohort Indexes & $O(N)$ Python Table Scans:** `execution_assignments` lacks B-Tree indexes on `(organization_id, id DESC)`, `(batch_id)`, `(task_brief_id)`, and `(execution_id)`, and `ExecutionAssignmentService._find_assignment_by_token_hash`, `get_assignment_by_execution_id`, and `list_assignments` scan full tables in Python instead of executing $O(1)$ indexed SQL queries.

### Producer-Consumer Integration Check (Section 2.5 Items 2)
* **Producer 2 (`ExecutionAssignmentService` in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`):** Validates optional `task_brief_id` existence and tenant access Fail-Fast at assignment publication time and freezes `task_brief_snapshot: TaskAssignmentBriefDTO | None` (`enforce_assignment_task_brief_snapshot_parity`) into `execution_assignments` inside a single atomic `async with uow:` batch transaction.
* **Consumer 2 (Public Magic-Link Portal & Cohort Management in `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` & Flutter `TaskAssignmentPortalView`):** Resolves `get_execution_assignment_by_token_hash` in $O(1)$ via the `token_hash` unique B-Tree index and projects `task_brief=assignment.task_brief_snapshot` onto `ExecutionAssignmentResponseDTO` and `ExecutionAssignmentPreviewDTO` without live `task_briefs` mutation drift.

### Canonical `execution_assignments` PostgreSQL 19 DDL Specification (Section 1.4.1 Item 4 Verbatim)

```sql
-- 4. execution_assignments with 1:1 ExecutionAssignment Column Parity, Frozen Snapshot & ON DELETE RESTRICT
CREATE TABLE IF NOT EXISTS execution_assignments (
    id UUID PRIMARY KEY DEFAULT uuidv7() CHECK (uuid_extract_version(id) = 7),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    output_profile_id UUID REFERENCES output_profiles(id) ON DELETE RESTRICT,
    task_brief_id UUID REFERENCES task_briefs(id) ON DELETE RESTRICT,
    task_brief_snapshot JSONB,
    batch_id UUID,
    assigned_email TEXT NOT NULL,
    assigned_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    invited_role TEXT NOT NULL DEFAULT 'viewer' CHECK (invited_role IN ('root', 'admin', 'user', 'viewer')),
    token_hash TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'activated', 'submitted', 'expired', 'revoked')),
    email_delivery_status TEXT NOT NULL DEFAULT 'pending' CHECK (email_delivery_status IN ('pending', 'sent', 'failed')),
    result_visibility TEXT NOT NULL DEFAULT 'confirmation_only' CHECK (result_visibility IN ('confirmation_only', 'immediate_report')),
    locked_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    assignee_input_keys JSONB NOT NULL DEFAULT '[]'::jsonb,
    draft_inputs JSONB NOT NULL DEFAULT '{}'::jsonb,
    target_locale TEXT NOT NULL DEFAULT 'en',
    hard_deadline_at TIMESTAMPTZ,
    relative_duration_seconds INTEGER CHECK (relative_duration_seconds IS NULL OR relative_duration_seconds >= 60),
    activated_at TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    execution_id UUID REFERENCES executions(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL,
    CONSTRAINT enforce_assignment_task_brief_snapshot_parity CHECK (
        (task_brief_id IS NULL AND task_brief_snapshot IS NULL)
        OR (task_brief_id IS NOT NULL AND task_brief_snapshot IS NOT NULL)
    )
);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_org_created ON execution_assignments(organization_id, id DESC);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_batch_id ON execution_assignments(batch_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_task_brief_id ON execution_assignments(task_brief_id);
CREATE INDEX IF NOT EXISTS idx_execution_assignments_execution_id ON execution_assignments(execution_id);
```

### Target Files
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`
- `[MODIFY] @[backend_v2/models/domain/execution.py#L541-L677]`
- `[MODIFY] @[backend_v2/models/auth.py#L109-L128]`
- `[MODIFY] @[backend_v2/models/domain/task_brief.py#L27-L86]`
- `[MODIFY] @[backend_v2/models/domain/prompt_blocks.py#L38-L67]`
- `[MODIFY] @[backend_v2/models/domain/step.py#L42-L225]`
- `[MODIFY] @[backend_v2/models/domain/workflow.py#L25-L232]`
- `[MODIFY] @[backend_v2/models/domain/output_profile.py#L44-L435]`
- `[MODIFY] @[backend_v2/models/dtos/studio.py#L297-L315]`
- `[MODIFY] @[backend_v2/models/dtos/output_profile.py]`
- `[MODIFY] @[backend_v2/database/interfaces.py#L413-L426]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L563-L588]`
- `[MODIFY] @[backend_v2/services/execution/assignment_service.py#L150-L1959]`
- `[MODIFY] @[backend_v2/services/studio/task_brief_service.py#L29-L279]`
- `[MODIFY] @[backend_v2/services/studio/auth_validator.py#L30-L54]`
- `[MODIFY] @[backend_v2/seed/seed_data.json#L1-L50]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/task_brief.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/workflow.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/prompt_block.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/output_profile.dart]`
- `[MODIFY] @[backend_v2/tests/factories/model_factories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L2001-L2012]`
- `[MODIFY] @[backend_v2/tests/unit/models/domain/test_task_brief.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_assignment_service.py]`
- `[MODIFY] @[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`
- `[MODIFY] @[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]`

## Phase 3 Deprecations & Sunset Symbols

<demolish>
- `_check_active_assignment_usage`
- `count_executions_by_matrix`
</demolish>

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/domain/execution.py#L541-L677]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]` & `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` | Live `TaskBrief` lookup at assignment preview/list time (retroactive instruction mutation), `strict: bool = False` silent `None` fallback in `_validate_and_resolve_task_brief`, and `ON DELETE SET NULL` on `execution_assignments.task_brief_id` and `output_profile_id`. | Add `task_brief_snapshot: TaskAssignmentBriefDTO | None` paired with `task_brief_id` via `@model_validator(mode="after")` and SQL `CONSTRAINT enforce_assignment_task_brief_snapshot_parity`; freeze `task_brief_snapshot` at assignment creation (`create_assignment` & `create_batch_assignments`), drop `strict` from `_validate_and_resolve_task_brief`, project `task_brief=assignment.task_brief_snapshot` onto `ExecutionAssignmentResponseDTO` / `ExecutionAssignmentPreviewDTO`, and enforce `ON DELETE RESTRICT` on `task_brief_id`, `output_profile_id`, and `workflow_id`. | Do NOT introduce a 3rd `assignment_batches` parent table; keep published cohort rows in `execution_assignments` grouped by indexed nullable `batch_id` + frozen `task_brief_snapshot JSONB` for 0-join magic-link portal lookups. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/execution.py backend_v2/services/execution/assignment_service.py backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict` |
| `@[backend_v2/models/auth.py#L109-L128]`, `@[backend_v2/models/domain/task_brief.py#L27-L86]`, `@[backend_v2/models/domain/prompt_blocks.py#L38-L67]`, `@[backend_v2/models/domain/step.py#L42-L225]`, `@[backend_v2/models/domain/workflow.py#L25-L232]`, `@[backend_v2/models/domain/output_profile.py#L44-L435]`, `@[backend_v2/models/dtos/studio.py#L297-L315]`, `@[backend_v2/models/dtos/output_profile.py]`, `@[backend_v2/services/studio/task_brief_service.py#L83-L123]`, `@[backend_v2/services/studio/auth_validator.py#L30-L54]` & `@[backend_v2/seed/seed_data.json#L1-L50]` | `organization_id ON DELETE SET NULL` and `None` / `"SYSTEM"` defaults across Studio tables and models (promoting deleted tenant rows into global `SYSTEM` templates), plus Python full-table scan `_check_active_assignment_usage`. | Hydrate `"organization_id": "org_0195f3a000007000800000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all 123 system seed rows; return `ROOT_SYSTEM` in `StudioAuthValidator.resolve_create_organization_id`; enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across SQL, Python Studio models/DTOs, and `SystemOrganizations.is_system`; and drop `_check_active_assignment_usage`. | Rely directly on PostgreSQL 19 `ON DELETE RESTRICT` (`SQLSTATE 23503` -> `ErrorCodes.DELETE_BLOCKED_BY_USAGE`) and `ON DELETE CASCADE` without Python multi-table loops; touch ZERO coaching prompts in `seed_data.json`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/services/studio/ backend_v2/tests/unit/services/studio/test_task_brief_service.py backend_v2/tests/unit/models/domain/test_task_brief.py --test --ast-strict` |
| `@[backend_v2/database/interfaces.py#L309-L309]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]` & `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L563-L588]` | $O(N)$ Python table scans in `_find_assignment_by_token_hash`, `get_assignment_by_execution_id`, `list_assignments`, and `list_executions`, plus unused `count_executions_by_matrix`. | Expose `get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization`, and `list_executions_filtered` on `EntityPersistencePort` backed by parameterized `$1, $2` SQL `WHERE`, `ORDER BY id DESC`, and `LIMIT` clauses and B-Tree indexes (`idx_execution_assignments_org_created`, `idx_execution_assignments_batch_id`, `idx_execution_assignments_task_brief_id`, `idx_execution_assignments_execution_id`, `idx_executions_org_id_created`), and drop `count_executions_by_matrix`. | Expose explicit domain-typed query methods on `EntityPersistencePort` without inventing any generic filter/ORM DSL. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/tests/fakes/ --test --ast-strict` |
| `@[client_app_v2/lib/features/studio/models/task_brief.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]` & `@[client_app_v2/lib/features/studio/models/output_profile.dart]` | Nullable `String? organizationId` fields on Flutter Studio Freezed models permitting missing tenant ownership on the wire. | Enforce non-nullable `@JsonKey(name: 'organization_id') required String organizationId` across `TaskBrief`, `Workflow`, `PromptBlock`, and `OutputProfile` Freezed models (`disallowUnrecognizedKeys: true`). | Maintain 1:1 full-duplex serialization parity verified automatically by `audit_dto_parity.py --fail-on-mismatch`. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read `@[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md]`, `@[docs/epic/EPIC_165_audit_report.md]`, `@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md#L1-L120]`, `@[.agents/rules/03_seed_vault.md]`, `@[backend_v2/models/domain/execution.py#L541-L677]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, and `@[backend_v2/services/studio/task_brief_service.py#L29-L279]`.</action>
    <action>Look forward: Verify Step 3.1 freezes `task_brief_snapshot JSONB` at assignment creation and drops `strict: bool = False`, Step 3.2 enforces `ON DELETE RESTRICT` on `execution_assignments` FKs and `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across all 123 `ROOT_SYSTEM` seed rows and Studio models/DTOs, Step 3.3 pushes assignment and execution lookups down to $O(1)$ indexed SQL queries on `EntityPersistencePort`, and Step 3.4 synchronizes Flutter Studio Freezed `organizationId` parity.</action>
    <constraint invariant="prompt_preservation_mandate">When hydrating `"organization_id": "org_0195f3a0000070008000000000000001"` across the 123 system seed records in `backend_v2/seed/seed_data.json`, store a timestamped backup in `backend_v2/seed/backups/` first and preserve 100% of `system_prompt`, `ai_description`, `instruction_text`, and matrix rubric text verbatim.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_165_Postgres_19_Zero_ORM_Normalization_And_Schema_Sovereignty.md] and @[docs/epic/EPIC_165_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_165/03_phase3_plan.md] @[docs/epic/EPIC_165_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]</backend>
    <backend>@[backend_v2/models/domain/execution.py#L541-L677]</backend>
    <backend>@[backend_v2/models/auth.py#L109-L128]</backend>
    <backend>@[backend_v2/models/domain/task_brief.py#L27-L86]</backend>
    <backend>@[backend_v2/models/domain/prompt_blocks.py#L38-L67]</backend>
    <backend>@[backend_v2/models/domain/step.py#L42-L225]</backend>
    <backend>@[backend_v2/models/domain/workflow.py#L25-L232]</backend>
    <backend>@[backend_v2/models/domain/output_profile.py#L44-L435]</backend>
    <backend>@[backend_v2/models/dtos/studio.py#L297-L315]</backend>
    <backend>@[backend_v2/models/dtos/output_profile.py]</backend>
    <backend>@[backend_v2/database/interfaces.py#L413-L426]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L563-L588]</backend>
    <backend>@[backend_v2/services/execution/assignment_service.py#L150-L1959]</backend>
    <backend>@[backend_v2/services/studio/task_brief_service.py#L29-L279]</backend>
    <backend>@[backend_v2/services/studio/auth_validator.py#L30-L54]</backend>
    <backend>@[backend_v2/seed/seed_data.json#L1-L50]</backend>
    <frontend>@[client_app_v2/lib/features/studio/models/task_brief.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/workflow.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/prompt_block.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/output_profile.dart]</frontend>
    <backend>@[backend_v2/tests/factories/model_factories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py#L2001-L2012]</backend>
    <backend>@[backend_v2/tests/unit/models/domain/test_task_brief.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_assignment_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]</backend>
    <frontend>@[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`ExecutionAssignment` in `@[backend_v2/models/domain/execution.py#L541-L677]` and `execution_assignments` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` enforce `task_brief_snapshot: TaskAssignmentBriefDTO | None` paired with `task_brief_id` via `@model_validator(mode="after")` and SQL `CONSTRAINT enforce_assignment_task_brief_snapshot_parity`, and `ExecutionAssignmentService` freezes `task_brief_snapshot` at creation while dropping `strict: bool = False` from `_validate_and_resolve_task_brief`.</item>
    <item>`execution_assignments.task_brief_id`, `output_profile_id`, and `workflow_id` enforce `ON DELETE RESTRICT` in SQL (`_check_active_assignment_usage` deleted from `StudioTaskBriefService`), and all 123 system seed rows in `@[backend_v2/seed/seed_data.json#L1-L50]` plus all tenant-scoped SQL tables, Python Studio models/DTOs, and `StudioAuthValidator.resolve_create_organization_id` enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` (`org_0195f3a0000070008000000000000001` for `ROOT_SYSTEM`).</item>
    <item>`EntityPersistencePort` (`@[backend_v2/database/interfaces.py#L296-L383]`) and `PostgresEntityAdapter` expose $O(1)$ indexed SQL methods `get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization`, and `list_executions_filtered`, replacing $O(N)$ Python scans and dropping `count_executions_by_matrix`.</item>
    <item>Flutter Studio Freezed models (`task_brief.dart`, `workflow.dart`, `prompt_block.dart`, `output_profile.dart`) enforce non-null `required String organizationId` and pass `audit_dto_parity.py --fail-on-mismatch` and `flutter_audit_loop.py`.</item>
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
    <anti_target>Do NOT retain `strict: bool = False` in `_validate_and_resolve_task_brief` or `ON DELETE SET NULL` on `organization_id` (`zero_backward_compatibility_planning_ban`).</anti_target>
    <anti_target>Do NOT rename wire key `task_brief` on `ExecutionAssignmentResponseDTO` or `ExecutionAssignmentPreviewDTO`; map `task_brief=assignment.task_brief_snapshot` to preserve 1:1 Flutter `ExecutionAssignmentResponseDto` / `ExecutionAssignmentPreviewDto` parity.</anti_target>
  </anti_targets>

  <step id="3.1" name="Immutable task_brief_snapshot JSONB Parity &amp; Fail-Fast TaskBrief Resolution on execution_assignments">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/models/domain/execution.py#L541-L677]`, and `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]`: Add `task_brief_snapshot: Annotated[TaskAssignmentBriefDTO | None, Field(default=None, description="Frozen publication-time snapshot of TaskBrief instructions and metadata when task_brief_id is set")] = None` paired with an `@model_validator(mode="after")` enforcing `(self.task_brief_id is None) == (self.task_brief_snapshot is None)` on `ExecutionAssignment`, add `task_brief_snapshot JSONB` (in both `CREATE TABLE IF NOT EXISTS` and `ALTER TABLE execution_assignments ADD COLUMN IF NOT EXISTS`) plus `CONSTRAINT enforce_assignment_task_brief_snapshot_parity CHECK ((task_brief_id IS NULL AND task_brief_snapshot IS NULL) OR (task_brief_id IS NOT NULL AND task_brief_snapshot IS NOT NULL))` in `001_pg19_uuidv7_schema.sql`, and serialize/hydrate `task_brief_snapshot` via `validate_hydrated_row` in `iam_and_system_stage.py`.</action>
    <action>2. `[MODIFY]` `@[backend_v2/services/execution/assignment_service.py#L150-L1959]` and `@[backend_v2/tests/unit/services/execution/test_assignment_service.py]`: Populate `task_brief_snapshot` at assignment creation (`create_assignment` and `create_batch_assignments`) whenever `task_brief_id` is supplied after Fail-Fast validation of `task_brief_id` existence and tenant access; drop the `strict: bool = False` parameter from `_validate_and_resolve_task_brief`; and project `task_brief=assignment.task_brief_snapshot` directly onto `ExecutionAssignmentResponseDTO` and `ExecutionAssignmentPreviewDTO` with zero live `task_briefs` lookup drift.</action>
    <constraint invariant="immutable_history_snapshot">Editing a `TaskBrief` in Studio after publishing an assignment MUST NEVER mutate the instructions or metadata rendered for already-published or completed `ExecutionAssignment` rows.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/execution.py backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py backend_v2/services/execution/assignment_service.py backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict</audit_command>
  </step>

  <step id="3.2" name="Kernel-Level ON DELETE RESTRICT &amp; ROOT_SYSTEM organization_id NOT NULL ON DELETE CASCADE Across 123 Seed Rows">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]` and `@[backend_v2/services/studio/task_brief_service.py#L83-L123]`: Enforce `ON DELETE RESTRICT` on `execution_assignments.task_brief_id`, `execution_assignments.output_profile_id`, and `execution_assignments.workflow_id` in `001_pg19_uuidv7_schema.sql`, and delete `_check_active_assignment_usage` from `StudioTaskBriefService` so PostgreSQL 19 enforces `SQLSTATE 23503` -> `ErrorCodes.DELETE_BLOCKED_BY_USAGE` (400) natively.</action>
    <action>2. `[MODIFY]` `@[backend_v2/seed/seed_data.json#L1-L50]`, `@[backend_v2/models/auth.py#L109-L128]`, `@[backend_v2/models/domain/task_brief.py#L27-L86]`, `@[backend_v2/models/domain/prompt_blocks.py#L38-L67]`, `@[backend_v2/models/domain/step.py#L42-L225]`, `@[backend_v2/models/domain/workflow.py#L25-L232]`, `@[backend_v2/models/domain/output_profile.py#L44-L435]`, `@[backend_v2/models/dtos/studio.py#L297-L315]`, `@[backend_v2/models/dtos/output_profile.py]`, `@[backend_v2/services/studio/auth_validator.py#L30-L54]`, `@[backend_v2/tests/factories/model_factories.py]`, `@[backend_v2/tests/unit/models/domain/test_task_brief.py]`, and `@[backend_v2/tests/unit/services/studio/test_task_brief_service.py]`: Create a timestamped backup in `backend_v2/seed/backups/` and hydrate `"organization_id": "org_0195f3a0000070008000000000000001"` (`ROOT_SYSTEM` on `SystemOrganizations`) across all 123 system-owned seed records missing `organization_id` or set to `"SYSTEM"` (`1` in `mcp_gateways`, `90` in `prompt_blocks`, `2` in `task_briefs`, `3` in `workflows`, `21` in `steps`, and `3` in `output_profiles`). Update `StudioAuthValidator.resolve_create_organization_id` to return `ROOT_SYSTEM` (`org_0195f3a0000070008000000000000001` on `SystemOrganizations`) instead of `None`, update `SystemOrganizations.is_system` to match canonical `ROOT_SYSTEM` strictly without treating `None` or `"SYSTEM"` as valid organization IDs, enforce `organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE` across all tenant-scoped SQL tables (`mcp_gateways`, `prompt_blocks`, `task_briefs`, `steps`, `workflows`, `output_profiles`, `execution_assignments`) and non-nullable `organization_id: str` validated against `OPAQUE_STRIPE_ID_REGEX` (`EntityPrefix.ORGANIZATION`) across `PromptBlockBase`, `TaskBrief`, `Step`, `Workflow`, `OutputProfile`, `ExecutionAssignment`, `WorkflowResponseDTO`, `StepResponseDTO`, `TaskBriefResponseDTO`, `OutputProfile` DTOs, and `model_factories.py`.</action>
    <constraint invariant="service_tenant_rbac_isolation_mandate">Deleting a tenant `Organization` row MUST cascade-delete its tenant-owned Studio entities and assignments without ever setting `organization_id` to `NULL` or exposing private templates as global `ROOT_SYSTEM` resources.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/services/studio/ backend_v2/tests/factories/model_factories.py backend_v2/tests/unit/models/domain/test_task_brief.py backend_v2/tests/unit/services/studio/test_task_brief_service.py --test --ast-strict</audit_command>
  </step>

  <step id="3.3" name="O(1) Indexed SQL Query Pushdown for Execution Assignments &amp; Executions">
    <action>1. `[MODIFY]` `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L1-L407]`, `@[backend_v2/database/interfaces.py#L296-L383]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L800-L825]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L563-L588]`, `@[backend_v2/services/execution/assignment_service.py#L150-L1959]`, `@[backend_v2/tests/fakes/in_memory_repositories.py]`, and `@[backend_v2/tests/fakes/in_memory_uow.py#L741-L1887]`: Add `idx_execution_assignments_org_created`, `idx_execution_assignments_batch_id`, `idx_execution_assignments_task_brief_id`, `idx_execution_assignments_execution_id`, and `idx_executions_org_id_created` to `001_pg19_uuidv7_schema.sql`. Expose and implement `get_execution_assignment_by_token_hash(token_hash: str) -> ExecutionAssignment | None`, `get_execution_assignment_by_execution_id(execution_id: str) -> ExecutionAssignment | None`, `list_execution_assignments_by_organization(organization_id: str, *, batch_id: str | None = None, limit: int = 100) -> list[ExecutionAssignment]`, and `list_executions_filtered(*, organization_id: str | None = None, created_by: str | None = None, workflow_id: str | None = None, status: ExecutionStatus | None = None, limit: int = 100) -> list[ExecutionRecord]` on `EntityPersistencePort`, `PostgresEntityAdapter`, and `InMemoryEntityAdapter` using parameterized `$1, $2` SQL `WHERE`, `ORDER BY id DESC`, and `LIMIT` clauses. Replace $O(N)$ Python table scans in `ExecutionAssignmentService._find_assignment_by_token_hash`, `get_assignment_by_execution_id`, and `list_assignments` with these $O(1)$ SQL methods, and drop `count_executions_by_matrix` from `ExecutionRepositoryImpl` and `InMemoryUnifiedWorkflowRepository`.</action>
    <constraint invariant="primary_key_lookup_o1_mandate">Portal magic-link token lookups (`get_execution_assignment_by_token_hash`) and tenant cohort queries MUST execute in $O(1)$ / indexed SQL without full-table Python scans.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/ backend_v2/services/execution/assignment_service.py backend_v2/tests/fakes/ backend_v2/tests/unit/services/execution/test_assignment_service.py --test --ast-strict</audit_command>
  </step>

  <step id="3.4" name="Flutter Studio Freezed organizationId Non-Null Parity (TaskBrief, Workflow, PromptBlock, OutputProfile)">
    <action>1. `[MODIFY]` `@[client_app_v2/lib/features/studio/models/task_brief.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/output_profile.dart]`, and `@[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]`: Update `organizationId` (`@JsonKey(name: 'organization_id')`) across `TaskBrief`, `Workflow`, `PromptBlock`, and `OutputProfile` Freezed models from nullable `String?` to non-nullable `required String organizationId` (with zero `@Default` fallback), regenerate `.freezed.dart` / `.g.dart` siblings, and update unit tests in `task_brief_test.dart` to assert Fail-Fast Freezed deserialization failure when `organization_id` is `null` or omitted.</action>
    <constraint invariant="silent_json_fallbacks">Missing or `null` `organization_id` payloads on Studio DTOs MUST crash the Freezed parser immediately (`disallowUnrecognizedKeys: true`).</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</audit_command>
  </step>

  <test_contracts>
    <test name="test_published_assignment_task_brief_snapshot_immune_to_subsequent_studio_edits" category="positive">
      <input>Create `TaskBrief` via `TaskBriefFactory.build(...)`, publish `ExecutionAssignment` with `task_brief_id`, then update `TaskBrief.instruction_text` in Studio and call `preview_assignment` / `list_assignments`</input>
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
      <input>`ExecutionAssignmentService.create_assignment` called with non-existent `task_brief_id` or another tenant's `task_brief_id`</input>
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
    <test name="test_studio_models_reject_none_or_legacy_system_organization_id" category="negative">
      <input>`TaskBrief.model_validate`, `Workflow.model_validate`, `Step.model_validate`, `OutputProfile.model_validate`, or Flutter `TaskBrief.fromJson` called with `organization_id=None` or `organization_id="SYSTEM"`</input>
      <expected>Fails fast with `ValidationError` / Dart `CheckedFromJsonException`</expected>
    </test>
    <test name="test_indexed_assignment_and_execution_queries_filter_and_order_deterministically" category="positive">
      <input>`get_execution_assignment_by_token_hash`, `get_execution_assignment_by_execution_id`, `list_execution_assignments_by_organization(batch_id=...)`, and `list_executions_filtered(organization_id=..., status=..., limit=1)`</input>
      <expected>Returns exact matching typed models ordered by `id DESC` within `limit` and `None`/`[]` on non-matching predicates</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python backend_v2/seed/run_seed.py local --dry-run; uv run --no-sync --offline python scripts/audit_database_atoms.py --strict; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/ backend_v2/database/ backend_v2/services/execution/assignment_service.py backend_v2/services/studio/ backend_v2/tests/factories/model_factories.py backend_v2/tests/fakes/ backend_v2/tests/unit/models/domain/test_task_brief.py backend_v2/tests/unit/services/execution/test_assignment_service.py backend_v2/tests/unit/services/studio/test_task_brief_service.py --test --ast-strict; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build; uv run --no-sync --offline python scripts/audit_dto_parity.py --fail-on-mismatch</command>
  </validation_gate>
</execution_protocol>

