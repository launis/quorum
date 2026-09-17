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
- [x] **[OK] Execution:** `/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`
  - [x] (5141d571) Step 1: BACKEND DOMAIN SCHEMA FLATTENING FOR OPTION A
  - [x] (eb37e926) Step 2: DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION
  - [x] (c1dfb9b5) Step 3: ORCHESTRATOR & LLM DISPATCH INTEGRATION
  - [x] (0b95a576) Step 4: VENDOR LEAK ERADICATION IN STEP BUILDER
  - [x] (afc97c1a) Step 5: DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY
  - [x] (19e7190a) Step 6: WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE
  - [x] (2862fb94) Step 7: SEED VAULT SYNCHRONIZATION & QUALITY GATES
  - [x] (075bb47f) Step 8: E2E VARIANCE TEST HARNESS DYNAMIC TELEMETRY & AUTOMATED COMPARISON
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` specifying the explicit list of created/modified `@-referenced` production backend files:
  - [x] @[backend_v2/models/v2_core.py]
  - [x] @[backend_v2/models/execution_core.py]
  - [x] @[backend_v2/models/dtos/studio.py]
  - [x] @[backend_v2/database/interfaces.py]
  - [x] @[backend_v2/database/repositories/system.py]
  - [x] @[backend_v2/services/studio/system_config_service.py]
  - [x] @[backend_v2/services/execution.py]
  - [x] @[backend_v2/services/orchestrator/strategies/base.py]
  - [x] @[backend_v2/services/orchestrator/dag_executor.py]
  - [x] @[backend_v2/services/orchestrator/strategies/llm.py]
  - [x] @[backend_v2/llm/client.py]
  - [x] @[backend_v2/worker.py]
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
  - [ ] Knowledge Item Updated: @[ki_provider_agnostic_caching.md] (Option A flat tier_definitions and workflow model_registry_id resolution)
  - [ ] Knowledge Item Updated: @[ki_desktop_pro_tool_studio_ux.md] (Desktop Pro Tool UX for ModelRegistryView and Studio Dashboard Tab 6)
  - [ ] Architecture Rule Synchronized: @[.agents/rules/04_directory_reference.md]

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
| REQ-12 | Modernize `run_e2e_variance_test.py` with dynamic DB resolution, `--model-registry`, and automated `--compare-registries` differential benchmark runs | Step 8 | [x] |

# Session Handover Context
## Achieved
- **Step 1-8 Implementation Complete:** Option A Sovereign Model Stack Architecture physically implemented across backend, frontend, seed vault, and variance tests.
- **Tier 8 Plan Audit Complete (`528c79e0`):** All 12 requirements verified with 0 fatal errors.
- **Tier 2 Backend Hardening Batch 1 Complete (5/14 files):**
  - `backend_v2/models/v2_core.py`: 100% strict Pydantic V2, 92% coverage, explicit `__all__ = [...]`, passed 174-rule audit matrix and strict AST loop.
  - `backend_v2/models/execution_core.py`: Added explicit `__all__ = ["ExecutionCoreFields", "ExecutionMetadata"]`, 100% coverage, passed 174-rule audit matrix.
  - `backend_v2/models/dtos/studio.py`: Modernized test fixtures from legacy `model_strategy` to `cognitive_tier="fast"`, 99% coverage, explicit `__all__ = [...]`, passed 174-rule audit matrix.
  - `backend_v2/database/interfaces.py`: Added complete 16-protocol `__all__ = [...]` export list, 100% coverage, passed 174-rule audit matrix.
  - `backend_v2/database/repositories/system.py`: Added explicit `__all__ = ["SystemRepositoryImpl"]`, refactored ternary fallbacks into fail-fast checks eliminating `QGR016` AST violations, 97% coverage, passed 174-rule audit matrix.
- **Tier 2 Backend Hardening Batch 2 Progress (4/5 files complete, 9/14 total):**
  - `backend_v2/services/studio/system_config_service.py` (`eced272f`): Refactored ternary lazy defaults, explicit `__all__`, 96% coverage, 174-rule audit matrix passed.
  - `backend_v2/services/execution.py` (`aad81fed`): Refactored 10 ternary lazy fallbacks, explicit `__all__ = ["ExecutionService", "create_execution_record"]`, expanded unit tests to 63 cases reaching 90% statement coverage, 174-rule audit matrix passed.
  - `backend_v2/services/orchestrator/strategies/base.py` (`414c6d03`): Added `from __future__ import annotations`, explicit `__all__ = ["NodeStrategy", "StrategyContext", "StrategyDependencies"]`, RFC 7807 `logger.error` dual-reporting in `assert_quota`, updated docstrings to Option A contracts, passed 174-rule audit matrix and 96% test coverage.
  - `backend_v2/services/orchestrator/dag_executor.py`: Added `from __future__ import annotations`, eradicated 14 AST guardrail violations (`QGR016` ternary fallbacks, `QGR003` broad exception handlers), added `from backend_v2.models.auth import User` for typed user resolution, updated test fixture with valid User domain model, passed all 174 rules in audit matrix and achieved 90% test coverage.
- **DAG Orchestrator Ecosystem Blast-Radius Analysis & User Permission Granted:**
  - Scanned `backend_v2/services/orchestrator/dag_executor.py`, eradicated 14 AST violations.
  - Explicit user permission secured: "PERMISSION GRANTED to mutate DAG Orchestrator ecosystem".
- **Documentation & Knowledge Item Update Refinement:**
  - Refined tracker lines 59–64 with explicit sub-items for `ki_provider_agnostic_caching.md`, `ki_desktop_pro_tool_studio_ux.md`, and `04_directory_reference.md`.

## Learned
- In `backend_v2/services/orchestrator/strategies/base.py`, `assert_quota` was using `logger.warning` instead of RFC 7807 `logger.error` before raising `AppException(status_code=402, ErrorCodes.RATE_LIMIT_EXCEEDED)`.
- In `backend_v2/services/orchestrator/dag_executor.py`, 14 AST violations (`QGR016` ternary lazy fallbacks, `QGR003` broad exceptions) were refactored to explicit branching and typed exception handling. In `test_dag_executor.py`, mock `get_user` was modernized from a naked dictionary to a validated `User` domain model.
- `tmp/hardening_state.json` tracks progress across 14 targets: 9 completed, 5 remaining.

## Remaining
- **Next Primary Gate:** Continue `/tier2-hardening-backend` for remaining Batch 2 file:
  - `@[backend_v2/services/orchestrator/strategies/llm.py]`
- **Remaining Backend Batch 3 (4 files):**
  - `@[backend_v2/llm/client.py]`
  - `@[backend_v2/worker.py]`
  - `@[backend_v2/services/studio/workflow_service.py]`
  - `@[scripts/run_e2e_variance_test.py]`
- **Post-Implementation Hardening Gates:**
  - Execute `/tier2-hardening-frontend` on modified Flutter files.
- **As-Built Architectural Sync:**
  - Execute `/tier7-describe-architecture` to update architectural documents and sync Knowledge Items (`ki_desktop_pro_tool_studio_ux.md`, `ki_provider_agnostic_caching.md`).

### Hardening State Snapshot
TARGETS: 14, DONE: 9, REMAINING: [@[backend_v2/services/orchestrator/strategies/llm.py], @[backend_v2/llm/client.py], @[backend_v2/worker.py], @[backend_v2/services/studio/workflow_service.py], @[scripts/run_e2e_variance_test.py]]

## Resume Command
`/tier5-resume --target="@[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]" --plan="@[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md]" --workflow="/tier2-hardening-backend" --rules="@[.agents/rules/00-antigravity-core.md],@[.agents/rules/01-python-backend.md],@[.agents/rules/04_directory_reference.md]"`


