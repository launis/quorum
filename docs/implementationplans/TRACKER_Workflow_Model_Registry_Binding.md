# Tracker: Option A Sovereign Model Stack Architecture, Deterministic Workflow Binding & Pro Tool UX
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md]
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`
  - [x] Step 1: BACKEND DOMAIN SCHEMA FLATTENING FOR OPTION A
  - [x] Step 2: DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION
  - [x] Step 3: ORCHESTRATOR & LLM DISPATCH INTEGRATION
  - [x] Step 4: VENDOR LEAK ERADICATION IN STEP BUILDER
  - [x] Step 5: DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY
  - [x] Step 6: WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE
  - [x] Step 7: SEED VAULT SYNCHRONIZATION & QUALITY GATES
  - [ ] Step 8: E2E VARIANCE TEST HARNESS DYNAMIC TELEMETRY & AUTOMATED COMPARISON
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` production backend files:
  - [ ] @[backend_v2/models/v2_core.py]
  - [ ] @[backend_v2/models/execution_core.py]
  - [ ] @[backend_v2/models/dtos/studio.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/repositories/system.py]
  - [ ] @[backend_v2/services/studio/system_config_service.py]
  - [ ] @[backend_v2/services/execution.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/base.py]
  - [ ] @[backend_v2/services/orchestrator/dag_executor.py]
  - [ ] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [ ] @[backend_v2/llm/client.py]
  - [ ] @[backend_v2/worker.py]
  - [ ] @[backend_v2/services/studio/workflow_service.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` specifying the explicit list of created/modified `@-referenced` production Flutter files:
  - [ ] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run `/tier7-describe-architecture` to anchor physical implementation in `docs/architecture/` (scoped to relevant documents), update relevant Knowledge Items, and synchronize `.agents/rules/04_directory_reference.md`.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After each successful quality gate verification, commit changes atomically with strict Conventional Commits syntax (`<type>(<scope>): <summary>`). List all staged files explicitly.
- **Seeding Environment**: If database re-seeding is required, execute `uv run python backend_v2/seed/run_seed.py local`.
- **Quality Gates**:
  - For Python changes: `uv run python scripts/backend_audit_loop.py <target_path> --test`
  - For Flutter changes: `uv run python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **Execution Mode**: Supports Step-by-Step (default pause per step) and Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`).
- **Context Budget Watchdog**: In Continuous Mode, proactively trigger `/tier5-session-handover` when the context budget limit is reached: >8 turns, 3 atomic commits, or >5 modified complex files.
- **Workflow Loop**: `/tier2-execute @[plan] @[tracker]` -> `/tier8-audit-plan @[plan] @[tracker]` -> Post-Implementation Hardening Gates (`/tier2-hardening-backend`, `/tier2-hardening-frontend`) -> `/tier7-describe-architecture`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-01 | Flatten `SystemConfigModelRegistry.tier_definitions` to `dict[LaxCognitiveTier, ModelProfile]` with 4 canonical tiers and add human-readable `name` | Step 1 | [x] |
| REQ-02 | Add `Workflow.model_registry_id` with regex validation and update Studio DTOs (`WorkflowCreateDTO`, `WorkflowUpdateDTO`, `ExecutionCreate`) | Step 1 | [x] |
| REQ-03 | Update `ISystemRepository` and `SystemRepositoryImpl` with keyed lookup `get_model_registry(registry_id)`, `get_all_model_registries()`, and upsert by ID | Step 2 | [x] |
| REQ-04 | Modernize `StudioSystemConfigService` to support multi-registry CRUD, keyed fetch, and deep clone with `name = f"{data.name} (Copy)"` | Step 2 | [x] |
| REQ-05 | Forward `model_registry_id` through `StrategyContext` and `DAGExecutor` to `LLMNodeStrategy` and stamp on `ExecutionRecord` | Step 2, Step 3 | [x] |
| REQ-06 | Update `LLMClient.from_tier` to resolve profiles in O(1) from flat `tier_definitions` for specified `registry_id` and eradicate legacy telemetry strings | Step 3 | [x] |
| REQ-07 | Eradicate physical model suffixes `[${physical.modelName}]` and vendor chips in `StepBuilderView` to enforce vendor-neutral tier selection | Step 4 | [x] |
| REQ-08 | Implement Desktop Pro Tool UX in `ModelRegistryView` (1200px bounded canvas, PopScope dirty checking, in-view clone, 4-tier cards) | Step 5 | [x] |
| REQ-09 | Upgrade Studio Dashboard Tab 6 with real-time search, count badge indicator, and pro-tool compact card density | Step 5 | [x] |
| REQ-10 | Add Model Registry dropdown selector in `WorkflowGeneralTab` and wire localized strings in `app_en.arb` / `app_fi.arb` | Step 6 | [x] |
| REQ-11 | Synchronize `seed_data.json` with Option A flat schema, bind `model_registry_id` to workflows, and update unit test fixtures | Step 7 | [x] |
| REQ-12 | Modernize `run_e2e_variance_test.py` with dynamic DB resolution, `--model-registry`, and automated `--compare-registries` differential benchmark runs | Step 8 | [ ] |

# Session Handover Context
## Achieved
- Executed Step 1: `BACKEND DOMAIN SCHEMA FLATTENING FOR OPTION A` (committed: `5141d571`).
- Executed Step 2: `DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION` (committed: `eb37e926`).
- Executed Step 3: `ORCHESTRATOR & LLM DISPATCH INTEGRATION`:
  - `backend_v2/services/orchestrator/strategies/base.py`: Added `model_registry_id: str | None = None` to `StrategyContext`.
  - `backend_v2/llm/client.py`: Implemented multi-registry `from_tier` and `from_strategy` resolving in O(1) from flat `registry.tier_definitions`. Eradicated legacy telemetry strings.
  - `backend_v2/services/orchestrator/strategies/llm.py`: Passed `registry_id=context.model_registry_id` into `LLMClient.from_tier`. Replaced obsolete `model_strategy` checks with typed `isinstance(self._engine, SynthesisEngine)` and `step_obj.pre_hooks` inspection.
  - `backend_v2/hooks/llm.py`: Modernized `configure_llm_context_hook` to resolve from `registry.tier_definitions`.
  - `backend_v2/services/orchestrator/dag_executor.py`: Passed `model_registry_id` to `StrategyContext`, resolved effective metadata, and modernized synthesis engine resolution to hook inspection.
  - `backend_v2/worker.py`: Updated `from_tier` invocations to forward `execution.metadata.model_registry_id`.
  - `backend_v2/services/studio/workflow_service.py`: Bound `model_registry_id="sys_e26807f3bfa3454d"` on workflow draft creation.
  - Unit Tests: Aligned all DAG executor, LLM strategy, MCP, preflight, and synthesis distiller test fixtures with Option A 4-tier definitions. 476/476 orchestrator tests passed 100%.
  - Quality Gate: Passed `backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test` with 90% coverage and 0 fatal AST violations.
  - `backend_v2/database/interfaces.py`: Updated `ISystemRepository` protocol to declare `get_model_registry(registry_id: str | None = None)`, `get_all_model_registries()`, and `delete_system_config(config_id: str)`.
  - `backend_v2/database/repositories/system.py`: Implemented deterministic keyed lookup (`ResourceNotFoundError` with RFC 7807 logging), deterministic default/all queries sorting via typed Pydantic models with zero AST QGR002 violations, authoritative in-place upsert by `registry_data.id`, and `delete_system_config`.
  - `backend_v2/services/studio/system_config_service.py`: Modernized `get_all_system_configs`, keyed `get_system_config`, `save_system_config` with keyed re-fetch, Option A compliant `create_system_config_draft`, deep clone appending ` (Copy)` to `name`, and authoritative `delete_system_config`.
  - `backend_v2/services/execution.py`: Stamped `model_registry_id = payload.model_registry_id or workflow.model_registry_id` on `ExecutionMetadata`.
  - `backend_v2/tests/fakes/in_memory_repositories.py`: Updated `InMemorySystemRepository` and `InMemoryUnifiedRepository` with multi-registry dictionary storage, keyed lookups, and deletion.
  - `backend_v2/tests/unit/database/repositories/test_system_model_registry.py`: Added 7 unit tests covering all multi-registry repository test contracts.
  - `backend_v2/tests/unit/database/repositories/test_system.py`: Added comprehensive unit tests achieving 100% test coverage on `system.py`.
  - Quality Gate Verification: Passed `backend_audit_loop.py backend_v2/database/repositories/system.py --test` with 100% coverage and exit code 0. Passed 28/28 tests in `test_system_config_service.py` and 25/25 tests in `test_execution.py`.

- Executed Step 4: `VENDOR LEAK ERADICATION IN STEP BUILDER`:
  - `client_app_v2/lib/features/studio/views/step_builder_view.dart`: Removed physical model name suffix `[${physical.modelName}]` from `DropdownMenuItem` text, displaying pure abstract cognitive tier label and description via localized strings (`l10n.studioTierFast`, etc.). Removed hardcoded vendor preview chip (`Icons.psychology`) and unnecessary `modelRegistryControllerProvider` watch, unblocking step authoring from model registry state.
  - `client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart`: Added comprehensive unit test `renders vendor-neutral cognitive tier dropdown with zero physical model suffixes` verifying all 4 canonical abstract tiers exist without any physical model names or vendor preview chips.
  - Quality Gate Verification: Passed `flutter_audit_loop.py` on both `step_builder_view.dart` and `step_builder_view_dropdown_test.dart` with 0 issues. All 3 tests pass in `step_builder_view_dropdown_test.dart`.

## Learned
- Using typed Pydantic model validation on queried dictionaries prior to sorting (`models = [SystemConfigModelRegistry.model_validate(r, strict=False) for r in res_list]`) completely eliminates dictionary `.get()` calls and cleanly satisfies AST guardrail `QGR002`.
- `InMemorySystemRepository` previously used a single `_model_registry` slot with obsolete `models={}`; refactoring it to a dictionary store `_model_registries` with Option A 4-tier default guarantees true stateful multi-registry roundtrip fidelity.
- Eradicating physical model inspection from `StepBuilderView` completely decouples individual workflow step authoring from physical provider/model configs, allowing step definitions to remain 100% vendor-neutral and solely driven by the workflow's attached Sovereign Model Registry stack.

## Remaining
- Execute Step 5: `DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY`
- Execute Step 6: `WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE`
- Execute Step 7: `SEED VAULT SYNCHRONIZATION & QUALITY GATES`
- Execute Step 8: `E2E VARIANCE TEST HARNESS DYNAMIC TELEMETRY & AUTOMATED COMPARISON`

## Resume Command
`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`
