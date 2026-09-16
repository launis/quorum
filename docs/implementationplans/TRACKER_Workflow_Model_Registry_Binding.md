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
  - [ ] Step 2: DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION
  - [ ] Step 3: ORCHESTRATOR & LLM DISPATCH INTEGRATION
  - [ ] Step 4: VENDOR LEAK ERADICATION IN STEP BUILDER
  - [ ] Step 5: DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY
  - [ ] Step 6: WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE
  - [ ] Step 7: SEED VAULT SYNCHRONIZATION & QUALITY GATES
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
| REQ-03 | Update `ISystemRepository` and `SystemRepositoryImpl` with keyed lookup `get_model_registry(registry_id)`, `get_all_model_registries()`, and upsert by ID | Step 2 | [ ] |
| REQ-04 | Modernize `StudioSystemConfigService` to support multi-registry CRUD, keyed fetch, and deep clone with `name = f"{data.name} (Copy)"` | Step 2 | [ ] |
| REQ-05 | Forward `model_registry_id` through `StrategyContext` and `DAGExecutor` to `LLMNodeStrategy` and stamp on `ExecutionRecord` | Step 2, Step 3 | [ ] |
| REQ-06 | Update `LLMClient.from_tier` to resolve profiles in O(1) from flat `tier_definitions` for specified `registry_id` and eradicate legacy telemetry strings | Step 3 | [ ] |
| REQ-07 | Eradicate physical model suffixes `[${physical.modelName}]` and vendor chips in `StepBuilderView` to enforce vendor-neutral tier selection | Step 4 | [ ] |
| REQ-08 | Implement Desktop Pro Tool UX in `ModelRegistryView` (1200px bounded canvas, PopScope dirty checking, in-view clone, 4-tier cards) | Step 5 | [ ] |
| REQ-09 | Upgrade Studio Dashboard Tab 6 with real-time search, count badge indicator, and pro-tool compact card density | Step 5 | [ ] |
| REQ-10 | Add Model Registry dropdown selector in `WorkflowGeneralTab` and wire localized strings in `app_en.arb` / `app_fi.arb` | Step 6 | [ ] |
| REQ-11 | Synchronize `seed_data.json` with Option A flat schema, bind `model_registry_id` to workflows, and update unit test fixtures | Step 7 | [ ] |
| REQ-12 | Modernize `run_e2e_variance_test.py` with dynamic DB resolution, `--model-registry`, and automated `--compare-registries` differential benchmark runs | Step 8 | [ ] |

# Session Handover Context
## Achieved
- Executed Step 1: `BACKEND DOMAIN SCHEMA FLATTENING FOR OPTION A`.
- Flattened `SystemConfigModelRegistry.tier_definitions` to `Annotated[dict[LaxCognitiveTier, ModelProfile], Field(strict=False)]` and enforced 4 canonical tiers completeness.
- Added `name: str = Field(default="Default Model Registry", ...)` to `SystemConfigModelRegistry`.
- Added `Workflow.model_registry_id` bound to `sys_e26807f3bfa3454d` with Opaque ID regex.
- Added `ExecutionCreate.model_registry_id` and `ExecutionMetadata.model_registry_id`.
- Added `WorkflowCreateDTO.model_registry_id` and `WorkflowUpdateDTO.model_registry_id`.
- Synchronized `backend_v2/seed/seed_data.json` with Option A flat schema for Gemini and OpenAI stacks and stamped `model_registry_id` across all 6 workflows.
- Successfully passed `backend_audit_loop.py backend_v2/models/v2_core.py --test` (100% PASS, 92% coverage, exit code 0).

## Learned
- Pre-flight in-memory seeder dry-run validates `seed_data.json` against `SystemConfigUnion` and `Workflow`, confirming 100% two-phase seeder integrity.
- `test_seed_architectural_guardrails.py` and `test_model_registry.py` fixtures required updating to flat `tier_definitions` to align with Option A schema.

## Remaining
- Execute Step 2: `DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION`
- Execute Step 3: `ORCHESTRATOR & LLM DISPATCH INTEGRATION`
- Execute Step 4: `VENDOR LEAK ERADICATION IN STEP BUILDER`
- Execute Step 5: `DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY`
- Execute Step 6: `WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE`
- Execute Step 7: `SEED VAULT SYNCHRONIZATION & QUALITY GATES`
- Execute Step 8: `E2E VARIANCE TEST HARNESS DYNAMIC TELEMETRY & AUTOMATED COMPARISON`

## Resume Command
`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md] @[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]`
