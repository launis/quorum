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
  - [ ] Step 1: Backend Domain Schema Flattening for Option A
  - [ ] Step 2: Database Repository & Service Multi-Registry Resolution
  - [ ] Step 3: Orchestrator & LLM Dispatch Integration
  - [ ] Step 4: Vendor Leak Eradication in Step Builder
  - [ ] Step 5: Desktop Pro Tool UX Upgrade for Model Registry
  - [ ] Step 6: Workflow General Tab Model Registry Linkage
  - [ ] Step 7: Seed Vault Synchronization & Quality Gates
  - [ ] Step 8: E2E Variance Test Harness Dynamic Telemetry & Automated Comparison
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `/tier2-hardening-backend` on target backend production files.
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
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `/tier2-hardening-frontend` on target Flutter production files.
  - [ ] @[client_app_v2/lib/features/studio/models/model_config.dart]
  - [ ] @[client_app_v2/lib/features/studio/models/workflow.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
  - [ ] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart]
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK] As-Built Architectural Sync**: Run `/tier7-describe-architecture` to automatically synchronize relevant architecture documentation in `docs/architecture/` and update `ki_provider_agnostic_caching.md`.

### Final Plan Audit

- [ ] **[NOK] System 2 Red-Team Audit**: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]` to verify 100% compliance with zero regressions.

## Instructions for the Execution Agent

- **Atomic Commits:** After any successful run of the universal quality gate, create an atomic git commit with English Conventional Commits syntax (`<type>(<scope>): <summary>`).
- **Seeding Invariant:** When modifying schemas in `backend_v2/models/v2_core.py` and `backend_v2/seed/seed_data.json`, verify with `uv run python scripts/audit_database_atoms.py --strict` before resetting or persisting.
- **Continuous Mode:** In Continuous Full-Auto Mode (invoked via `/tier2-execute --full-auto`), proceed autonomously across steps as long as quality gates pass 100%. Trigger session handover cleanly if context limits are approached (>8 turns, 3 commits, >5 complex files).
- **Mandatory Audit Loop:** Run `uv run python scripts/backend_audit_loop.py <target> --test` for Python files and `uv run python scripts/flutter_audit_loop.py <target> --build` for Dart files.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-1 | Flatten `SystemConfigModelRegistry.tier_definitions` to direct 4-tier mapping and add `name: str` | Step 1 | `[ ] PENDING` |
| REQ-2 | Add `model_registry_id` to `Workflow` and Studio DTOs | Step 1 | `[ ] PENDING` |
| REQ-3 | Update `ISystemRepository` and `SystemRepositoryImpl` with deterministic `get_model_registry(id)` and `get_all_model_registries()` | Step 2 | `[ ] PENDING` |
| REQ-4 | Update `StudioSystemConfigService` for multi-registry CRUD and clone with name copy suffix | Step 2 | `[ ] PENDING` |
| REQ-5 | Stamp `model_registry_id` onto `ExecutionRecord` in `ExecutionService.start_execution` | Step 2 | `[ ] PENDING` |
| REQ-6 | Forward `model_registry_id` through `StrategyContext` and `worker.py` into `LLMClient.from_tier` | Step 3 | `[ ] PENDING` |
| REQ-7 | Eradicate vendor name leakage and hardcoded vendor preview chips from `StepBuilderView` | Step 4 | `[ ] PENDING` |
| REQ-8 | Upgrade `ModelRegistryView` to Desktop Pro Tool UX (1200px canvas, PopScope dirty check, 4 tier cards, clone button) | Step 5 | `[ ] PENDING` |
| REQ-9 | Modernize Studio Dashboard Tab 6 with real-time search, count badge, and virtualized list | Step 5 | `[ ] PENDING` |
| REQ-10 | Add model registry dropdown selector to `WorkflowGeneralTab` in Quorum Studio | Step 6 | `[ ] PENDING` |
| REQ-11 | Migrate `seed_data.json` to Option A flat schema with Gemini and OpenAI sovereign stacks | Step 7 | `[ ] PENDING` |
| REQ-12 | Execute seed database atom audit and backend/flutter quality gates | Step 7 | `[ ] PENDING` |
| REQ-13 | Dynamic model telemetry resolution in `scripts/run_e2e_variance_test.py` from active database | Step 8 | `[ ] PENDING` |
| REQ-14 | Implement `--model-registry` override and automated `--compare-registries` differential runs | Step 8 | `[ ] PENDING` |

# Session Handover Context

## Achieved
- Created implementation plan `docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md` for Option A Sovereign Model Stack Architecture.
- Completed Tier 0 research and deconstruction into 5-column architectural directives table.
- Generated canonical Standalone Plan Tracker with 1:1 requirements traceability and file-level hardening checklists.

## Learned
- Current `SystemConfigModelRegistry` uses nested multi-provider map (`tier_definitions[provider][tier]`) which complicates step resolution and causes Tab 6 runtime crashes.
- Flattening to Option A direct 4-tier mapping (`tier_definitions[tier] = ModelProfile`) establishes clean 1 Document = 1 Sovereign Stack semantics.
- Standalone Plan Tracker Generator established durable double-entry bookkeeping for non-Epic plans in `docs/implementationplans/`.

## Remaining
- Execute Step 1: Backend Domain Schema Flattening for Option A.
- Execute Step 2: Database Repository & Service Multi-Registry Resolution.
- Execute Step 3: Orchestrator & LLM Dispatch Integration.
- Execute Step 4: Vendor Leak Eradication in Step Builder.
- Execute Step 5: Desktop Pro Tool UX Upgrade for Model Registry.
- Execute Step 6: Workflow General Tab Model Registry Linkage.
- Execute Step 7: Seed Vault Synchronization & Quality Gates.
- Execute Step 8: E2E Variance Test Harness Dynamic Telemetry & Automated Comparison.

## Resume Command
`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`
