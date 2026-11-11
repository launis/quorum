# Tracker: Independent `task_briefs` Database Table, Seed Collection & Frontend Architecture

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_api_router_ssot_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md] @[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]`
  - [x] Step 1: Phase 1: Backend Domain Schema, Enums, Studio DTOs & Polyfactory
  - [x] Step 2: Phase 2: PostgreSQL 19 16-Table Schema, Zero-ORM Entity Adapter, Repository & In-Memory Fakes
  - [x] Step 3: Phase 3: StudioTaskBriefService, ExecutionAssignmentService Wiring & FastAPI Router
  - [x] Step 4: Phase 4: Seed Vault Pipeline, Sanitizer, Atom Auditor & seed_data.json Migration
  - [x] Step 5: Phase 5: Flutter TaskBrief Freezed Model, StudioClient, IAM & Execution Views, Tests & Directory Index
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md] @[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[backend_v2/api/dependencies.py]
  - [x] @[backend_v2/api/routers/studio/__init__.py]
  - [x] @[backend_v2/api/routers/studio/task_briefs.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [x] @[backend_v2/database/repositories/components/task_brief.py]
  - [ ] @[backend_v2/database/repository.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/domain/__init__.py]
  - [ ] @[backend_v2/models/domain/prompt_blocks.py]
  - [ ] @[backend_v2/models/domain/task_brief.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/seed/seed_registry.py]
  - [ ] @[backend_v2/services/execution/assignment_service.py]
  - [ ] @[backend_v2/services/studio/__init__.py]
  - [ ] @[backend_v2/services/studio/prompt_block_service.py]
  - [ ] @[backend_v2/services/studio/task_brief_service.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[client_app_v2/lib/core/api/studio_client.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/task_brief.dart]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols (`PromptBlockCategory.TASK_DEFINITION`, `TaskDefinitionPromptBlock`, `PromptBlockCategory.taskDefinition`, `categoryTaskDefinition`) or legacy synthesis block references (`blk_0195f3a0000070018a2b3c4d5e6f7a8b`, `blk_0195f3a0000070088b7a6f5e4d3c2b1a`) remain across Python, SQL, JSON, or Dart files.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md] @[ki_router_ssot_and_crud_clone_lifecycle.md] @[ki_api_router_ssot_governance.md] @[ki_zero_permissive_typing.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_router_ssot_and_crud_clone_lifecycle.md]`: Document `StudioTaskBriefService` 5-operation CRUD+Clone lifecycle (`create_task_brief_draft`, `get_task_brief`, `list_task_briefs`, `save_task_brief`, `delete_task_brief`, `clone_task_brief`), `EntityPrefix.TASK_BRIEF = "tbr"`, and `TaskBriefResponseDTO` wire parity with Flutter `TaskBrief`.
     - `@[ki_api_router_ssot_governance.md]`: Document canonical `/api/v2/studio/task-briefs` single-router SSOT (`@[backend_v2/api/routers/studio/task_briefs.py]`) and its registration in `BLUEPRINT_ROUTERS`.
     - `@[ki_zero_permissive_typing.md]`: Document immutable `TaskBrief(V2CoreBase)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`), removal of `PromptBlockCategory.TASK_DEFINITION`, and normalized `execution_assignments.task_brief_id` foreign key pointing to `task_briefs(id) ON DELETE SET NULL`.
     - `@[ki_god_code_prevention.md]`: Document the 16-table PostgreSQL 19 Zero-ORM schema, 12 `CANONICAL_SEED_TABLES`, and 8-collection `audit_database_atoms.py` seed verification pipeline.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `@[backend_v2/models/domain/task_brief.py]`, `@[backend_v2/database/repositories/components/task_brief.py]`, `@[backend_v2/services/studio/task_brief_service.py]`, `@[backend_v2/api/routers/studio/task_briefs.py]`, `@[client_app_v2/lib/features/studio/models/task_brief.dart]`, the 16-table PostgreSQL 19 schema, 12-table `CANONICAL_SEED_TABLES`, and 8-collection `audit_database_atoms.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the independent `task_briefs` domain table, seed collection, Studio CRUD+Clone lifecycle, and `execution_assignments.task_brief_id` foreign key resolution in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md] @[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[backend_v2/target.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Add `TASK_BRIEF = "tbr"` to `EntityPrefix` and remove `TASK_DEFINITION = "task_definition"` from `PromptBlockCategory` in `@[backend_v2/models/enums.py#L246-L268]` and `@[backend_v2/models/enums.py#L368-L377]`. | Step 1 | [x] Completed |
| REQ-002 | Create `[NEW] @[backend_v2/models/domain/task_brief.py]` defining immutable `TaskBrief(V2CoreBase)` (`ConfigDict(strict=True, extra="forbid", frozen=True)`) with `id` (`OPAQUE_STRIPE_ID_REGEX` + `parse_prefixed_uuid7(v, EntityPrefix.TASK_BRIEF)`), `slug`, `organization_id`, `label`, `description`, `instruction_text`, and `source_url`, and re-export in `@[backend_v2/models/domain/__init__.py]`. | Step 1 | [x] Completed |
| REQ-003 | Remove `PromptBlockCategory.TASK_DEFINITION` from `SystemRulePromptBlock.category_id` and `PROMPT_BLOCK_REGISTRY` in `@[backend_v2/models/domain/prompt_blocks.py#L133-L154]`, and update `task_brief_id` metadata in `@[backend_v2/models/auth.py#L1017-L1038]` and `@[backend_v2/models/domain/execution.py#L541-L677]` to reference `tbr_<hex32>`. | Step 1 | [x] Completed |
| REQ-004 | Define `TaskBriefResponseDTO(BaseResponseDTO, TaskBrief)` (explicitly exposing `organization_id: str \| None = None`) and `TaskBriefDeleteResponse(BaseResponseDTO)` in `@[backend_v2/models/dtos/studio.py#L315-L326]`, and register `"taskbriefresponsedto": "taskbrief"` and `"taskbrief": "taskbriefresponsedto"` in `@[scripts/audit_dto_parity.py#L338-L385]`. | Step 1 | [x] Completed |
| REQ-005 | Add `TaskBriefFactory(ModelFactory[TaskBrief])` in `@[backend_v2/tests/factories/model_factories.py#L215-L280]`, register in `@[backend_v2/tests/factories/test_model_factories.py#L103-L121]`, create `[NEW] @[backend_v2/tests/unit/models/domain/test_task_brief.py]` (with >=2 negative boundary tests), and update `@[backend_v2/tests/unit/test_ast_prompt_fallback_guardrails.py#L125-L140]`, `@[backend_v2/tests/unit/test_prompt_blocks.py#L243-L251]`, `@[backend_v2/tests/unit/test_auth_models.py#L387-L447]`, and `@[backend_v2/tests/unit/models/domain/test_execution.py#L404-L418]`. | Step 1 | [x] Completed |
| REQ-006 | Add `task_briefs` as the 16th PostgreSQL 19 table before `execution_assignments` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` with `uuidv7()` PK, `VIRTUAL` generated `created_at` (plus PG < 18 fallback), UUIDv7 CHECK constraints, and idempotent migration of `execution_assignments.task_brief_id` FK to `REFERENCES task_briefs(id) ON DELETE SET NULL`. | Step 2 | [x] Completed |
| REQ-007 | Register `"task_briefs"` and `"source_url"` in `@[scripts/audit_zero_orm_strictness.py#L830-L1024]` (`CANONICAL_ENTITY_PK_TABLES`, `CANONICAL_NAMED_ENTITY_TABLES`, `CLOSED_POSTGRES_TABLES`, `APPROVED_ADAPTER_RECORD_COLUMNS`) and update `@[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py#L203-L248]`. | Step 2 | [x] Completed |
| REQ-008 | Wire `"task_briefs"` across `@[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py#L286-L331]` (12 `CANONICAL_SEED_TABLES`), `@[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py#L426-L446]`, `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L761-L803]` and `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L806-L853]` (`EntityPrefix.TASK_BRIEF` for `task_brief_id`), `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L165-L217]`, `@[backend_v2/database/postgres/entity_adapter/__init__.py#L138-L729]`, and `@[backend_v2/database/postgres/storage_driver.py#L46-L75]`. | Step 2 | [x] Completed |
| REQ-009 | Define `ITaskBriefRepository` and `EntityPersistencePort` methods in `@[backend_v2/database/interfaces.py#L338-L359]` and `@[backend_v2/database/interfaces.py#L401-L431]`, implement `TaskBriefRepositoryImpl` in `[NEW] @[backend_v2/database/repositories/components/task_brief.py]` using $O(1)$ `await self.driver.get("task_briefs", brief_id)` (`ZORM007`), and wire into `UnifiedWorkflowRepository` in `@[backend_v2/database/repository.py#L24-L50]`. | Step 2 | [x] Completed |
| REQ-010 | Wire `"task_briefs"` across `InMemoryUnitOfWork`, `InMemoryEntityAdapter`, and `InMemoryAsyncPgConnection` in `@[backend_v2/tests/fakes/in_memory_uow.py#L692-L1290]` and `@[backend_v2/tests/fakes/in_memory_uow.py#L1351-L1891]`, add `InMemoryTaskBriefRepository` in `@[backend_v2/tests/fakes/in_memory_repositories.py#L1482-L2127]`, and update all 7 entity adapter / postgres unit test suites. | Step 2 | [x] Completed |
| REQ-011 | Create `[NEW] @[backend_v2/services/studio/task_brief_service.py]` implementing `StudioTaskBriefService` with full 5-operation CRUD+Clone lifecycle (`list_task_briefs`, `get_task_brief`, `create_task_brief_draft`, `save_task_brief`, `delete_task_brief`, `clone_task_brief`), re-export in `@[backend_v2/services/studio/__init__.py]`, and purge `PromptBlockCategory.TASK_DEFINITION` from `@[backend_v2/services/studio/prompt_block_service.py#L189-L252]`. | Step 3 | [x] Completed |
| REQ-012 | Inject `task_brief_repo: ITaskBriefRepository \| None = None` into `ExecutionAssignmentService` (`@[backend_v2/services/execution/assignment_service.py#L165-L204]` and `@[backend_v2/services/execution/assignment_service.py#L1780-L1876]`) and `ExecutionService` (`@[backend_v2/services/execution/facade.py#L69-L710]`) to resolve `TaskBrief` via `get_task_brief_by_id` with tenant/SYSTEM RBAC verification. | Step 3 | [x] Completed |
| REQ-013 | Create canonical router `[NEW] @[backend_v2/api/routers/studio/task_briefs.py]` (`/api/v2/studio/task-briefs` with `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, `POST /{id}/clone`), mount in `@[backend_v2/api/routers/studio/__init__.py]`, wire DI in `@[backend_v2/api/dependencies.py#L614-L651]`, and add `"task_briefs": 1` to `_validate_database_preflight` in `@[backend_v2/main.py#L133-L177]`. | Step 3 | [x] Completed |
| REQ-014 | Create `[NEW] @[backend_v2/tests/unit/services/studio/test_task_brief_service.py]` and update `@[backend_v2/tests/unit/services/studio/test_prompt_block_service.py#L319-L347]`, `@[backend_v2/tests/unit/services/execution/test_assignment_service.py#L201-L323]` and `@[backend_v2/tests/unit/services/execution/test_assignment_service.py#L1377-L1567]`, `@[backend_v2/tests/unit/test_main.py#L56-L66]`, and `@[backend_v2/tests/unit/api/test_router_ssot_guardrails.py#L130-L166]`. | Step 3 | [x] Completed |
| REQ-015 | Register `SeedCollectionName.TASK_BRIEFS = "task_briefs"` in `@[backend_v2/seed/seed_registry.py]` and wire `list[TaskBrief]` validation, `TOPOLOGICAL_SEED_ORDER`, and `_seed_postgres` table count verification in `@[backend_v2/seed/run_seed.py#L283-L397]`, `@[backend_v2/seed/run_seed.py#L425-L453]`, and `@[backend_v2/seed/run_seed.py#L661-L738]`. | Step 4 | [x] Completed |
| REQ-016 | Add `sanitize_task_briefs` in `@[scripts/sanitize_seed_vault.py#L128-L151]` and `@[scripts/sanitize_seed_vault.py#L1079-L1183]`, and expand `@[scripts/audit_database_atoms.py#L1117-L1310]` and `@[scripts/audit_database_atoms.py#L1313-L1391]` to audit `"task_briefs"` as the 8th canonical seed collection (`EntityPrefix.TASK_BRIEF`, `"label"` display field, `organization_id` FK check, XML tag ban on `instruction_text`, and bilingual `I18nText` parity). | Step 4 | [x] Completed |
| REQ-017 | Back up `@[backend_v2/seed/seed_data.json]`, reclassify the 11 active internal DAG instruction blocks from `"category_id": "task_definition"` to `"category_id": "system_rule"` with 100% `instruction_text` preservation (`@[backend_v2/seed/seed_data.json#L13965-L19274]`), delete unreferenced synthesis blocks `blk_0195f3a0000070018a2b3c4d5e6f7a8b` and `blk_0195f3a0000070088b7a6f5e4d3c2b1a`, and seed 2 bilingual `task_briefs` (`tbr_0195f3a00000700d8a1b2c3d4e5f6001`, `tbr_0195f3a00000700d8a1b2c3d4e5f6002`) in `@[backend_v2/seed/seed_data.json#L23130-L23139]`. | Step 4 | [x] Completed |
| REQ-018 | Remove the obsolete `blk_0195f3a0000070018a2b3c4d5e6f7a8b` exemption from `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L26-L49]`, assert `task_briefs` bilingual parity and zero `"task_definition"` blocks in `seed_data.json`, and execute `run_seed.py local --dry-run`, `audit_database_atoms.py --strict`, and `run_seed.py local`. | Step 4 | [x] Completed |
| REQ-019 | Create `[NEW] @[client_app_v2/lib/features/studio/models/task_brief.dart]` (`@Freezed(equal: false) abstract class TaskBrief`, `@JsonSerializable(disallowUnrecognizedKeys: true)`, `@StrictOpaqueIdConverter()`, `parseListInBackground`) and add 6 CRUD+Clone `studio/task-briefs` methods to `@[client_app_v2/lib/core/api/studio_client.dart]`. | Step 5 | [x] Completed |
| REQ-020 | Remove `PromptBlock.taskDefinition` / `TaskDefinitionPromptBlock`, `PromptBlockCategory.taskDefinition`, and `categoryTaskDefinition` L10n keys from `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/core/models/prompt_block_category.dart]`, `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]`, `@[client_app_v2/lib/l10n/app_en.arb]`, and `@[client_app_v2/lib/l10n/app_fi.arb]`. | Step 5 | [x] Completed |
| REQ-021 | Migrate `organizationTaskBriefsProvider`, `_TaskBriefsManagementCard`, and `_EditTaskBriefDialog` in `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` and `availableTaskBriefsProvider` + `TaskAssignmentConfigDialog` in `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]` to `TaskBrief` with post-`await` `if (!context.mounted) return;` guards (`DGR011`). | Step 5 | [x] Completed |
| REQ-022 | Create `[NEW] @[client_app_v2/test/unit/features/studio/models/task_brief_test.dart]`, update `@[client_app_v2/test/models/domain_parity_test.dart]` and all 6 affected Flutter unit/widget test suites, update `@[.agents/rules/04_directory_reference.md]`, and pass `flutter_audit_loop.py`, `audit_dto_parity.py`, and `backend_audit_loop.py`. | Step 5 | [x] Completed |

# Session Handover Context

## Achieved
- Completed all 5 steps (`REQ-001` through `REQ-022`) of `@[docs/implementationplans/IMPLEMENTATION_PLAN_Independent_Task_Briefs_Architecture.md]`:
  - **Step 1 (`6d5e78282`)**: Created `TaskBrief` (`EntityPrefix.TASK_BRIEF = "tbr"`), `TaskBriefResponseDTO`, `TaskBriefDeleteResponse`, `TaskBriefFactory`, and removed `PromptBlockCategory.TASK_DEFINITION`.
  - **Step 2 (`1898d754a`)**: Added `task_briefs` as the 16th PostgreSQL 19 table in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`, registered in `@[scripts/audit_zero_orm_strictness.py]`, implemented `TaskBriefRepositoryImpl` (`@[backend_v2/database/repositories/components/task_brief.py]`), and wired across `PostgresEntityAdapter` and `InMemoryUnitOfWork`.
  - **Step 3 (`ac0bfbf19`)**: Implemented `StudioTaskBriefService` (`@[backend_v2/services/studio/task_brief_service.py]`), wired `ITaskBriefRepository` into `ExecutionAssignmentService` and `ExecutionService`, and mounted `/api/v2/studio/task-briefs` (`@[backend_v2/api/routers/studio/task_briefs.py]`).
  - **Step 4 (`c021d4b8e`)**: Registered `SeedCollectionName.TASK_BRIEFS = "task_briefs"`, updated `sanitize_seed_vault.py` and `audit_database_atoms.py` (8 collections), reclassified 11 active DAG instruction blocks in `@[backend_v2/seed/seed_data.json#L13965-L19274]` to `"system_rule"` with 100% prompt preservation, deleted the 2 unreferenced synthesis blocks, seeded 2 bilingual `task_briefs` (`tbr_0195f3a00000700d8a1b2c3d4e5f6001`, `tbr_0195f3a00000700d8a1b2c3d4e5f6002`), and re-seeded local PostgreSQL 19 (`90` `prompt_blocks`, `2` `task_briefs`).
  - **Step 5 (`d21fab3a6`)**: Created Flutter `TaskBrief` Freezed model (`@[client_app_v2/lib/features/studio/models/task_brief.dart]`), added 6 CRUD+Clone `studio/task-briefs` methods in `@[client_app_v2/lib/core/api/studio_client.dart]`, migrated `@[client_app_v2/lib/features/settings/presentation/organization_iam_settings_view.dart]` and `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`, purged `TaskDefinitionPromptBlock` and `PromptBlockCategory.taskDefinition`, updated `@[.agents/rules/04_directory_reference.md]`, and verified `flutter_audit_loop.py` (0 violations), `audit_dto_parity.py` (93/93 shared models aligned), `backend_audit_loop.py` (7,187 passed, 97.50% coverage), and live E2E `test_integration_real_llm.py` (7/7 passed).
- Completed Tier 8 System 2 Post-Implementation Plan Audit (`/tier8-audit-plan`): verified 22/22 requirements (`REQ-001` through `REQ-022`), 0 ZORM violations across 415 files, 0 technical debt findings across 33 targets and 207 1-hop callers, and 100% plan-tracker parity (`audit_plan_tracker_parity.py` & `audit_tracker_output.py`).
- Completed Tier 7 As-Built Architectural Sync (`/tier7-describe-architecture`): synchronized `@[docs/architecture/01_system_context_and_invariants.md]`, `@[docs/architecture/02_data_seeding_and_ontology.md]`, `@[docs/architecture/04_server_driven_ui_and_presentation.md]`, `@[docs/architecture/05_resilience_and_observability.md]`, and `@[docs/architecture/09_llm_prompt_orchestration_and_matrix_evaluation.md]` with the 16-table PostgreSQL 19 schema, 12 `CANONICAL_SEED_TABLES`, 8 seeded entity collections (`task_briefs`), `TaskBrief` (`EntityPrefix.TASK_BRIEF = "tbr"`), `StudioTaskBriefService` (`/api/v2/studio/task-briefs`) 5-operation CRUD+Clone lifecycle, `execution_assignments.task_brief_id REFERENCES task_briefs(id) ON DELETE SET NULL`, and removal of `PromptBlockCategory.TASK_DEFINITION`.

## Learned
- On persistent PostgreSQL 19 volumes previously seeded before `PromptBlockCategory.TASK_DEFINITION` removal, `ON CONFLICT (id) DO UPDATE` in `run_seed.py` updates existing IDs but leaves deleted seed rows (`blk_0195f3a0000070018a2b3c4d5e6f7a8b`, `blk_0195f3a0000070088b7a6f5e4d3c2b1a`) in `prompt_blocks`. Adding idempotent `DELETE FROM prompt_blocks WHERE category_id NOT IN ('matrix', 'system_rule', 'runtime_variables', 'persona', 'protocol');` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L472-L473]` deterministically purges retired categories during `apply_migrations()`.

## Remaining
- Execute Tier 2 Hardening (`scripts/auto_hardening_runner.py` with `--gate all`).

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Independent_Task_Briefs_Architecture.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
```
