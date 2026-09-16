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
| REQ-12 | Modernize `run_e2e_variance_test.py` with dynamic DB resolution, `--model-registry`, and automated `--compare-registries` differential benchmark runs | Step 8 | [x] |

# Session Handover Context
## Achieved
- **Step 1 (`5141d571`):** `SystemConfigModelRegistry` flattened with 4 canonical tiers (`fast`, `balanced`, `deep`, `reasoning`), `name: str`, `Workflow.model_registry_id`, `ExecutionCreate.model_registry_id`, and Studio DTOs.
- **Step 2 (`eb37e926`):** `ISystemRepository` & `SystemRepositoryImpl` with keyed lookup `get_model_registry(registry_id)`, `get_all_model_registries()`, and `delete_system_config`; `StudioSystemConfigService` multi-registry CRUD with deep clone appending ` (Copy)`; `start_execution` stamps `model_registry_id`.
- **Step 3 (`c1dfb9b5`):** `StrategyContext.model_registry_id` forwarded through `DAGExecutor` to `LLMNodeStrategy` and `worker.py`; `LLMClient.from_tier` resolves in O(1) from flat `tier_definitions`; 476/476 orchestrator tests passed.
- **Step 4 (`0b95a576`):** Eradicated physical model suffixes `[${physical.modelName}]` and vendor preview chips in `StepBuilderView`.
- **Step 5 (`afc97c1a`):** Desktop Pro Tool UX in `ModelRegistryView` (1200px canvas, `PopScope` dirty checking, in-view clone, 4-tier cards) and `StudioDashboardView` Tab 6 (real-time search, count badge).
- **Step 6 (`19e7190a`):** `WorkflowGeneralTab` Sovereign Model Stack selector dropdown showing name and provider badge; dual-axis localization; 142/142 studio view tests passed.
- **Step 7 (`2862fb94`):** `seed_data.json` synchronized with Option A flat schema (`sys_e26807f3bfa3454d` Google Gemini Sovereign Stack and `sys_6f8b1c4a2e0d49f1` OpenAI O-Series Stack), all workflows bound to `sys_e26807f3bfa3454d`; passed strict seed audit and local seeding. Quality gates in `system.py` (100% cov) and `v2_core.py` (92% cov) passed.
- **Step 8 (`075bb47f`):** Modernized `scripts/run_e2e_variance_test.py` with dynamic model registry resolution (`resolve_model_telemetry`, `print_model_telemetry`, `resolve_comparison_registries`), CLI flags `--model-registry` and `--compare-registries`, side-by-side telemetry and automated differential execution flow. 35/35 tests passed in `test_run_e2e_variance_test.py`.

## Learned
- Using typed Pydantic model validation on queried dictionaries prior to sorting (`models = [SystemConfigModelRegistry.model_validate(r, strict=False) for r in res_list]`) completely eliminates dictionary `.get()` calls and cleanly satisfies AST guardrail `QGR002`.
- `InMemorySystemRepository` previously used a single `_model_registry` slot with obsolete `models={}`; refactoring it to a dictionary store `_model_registries` with Option A 4-tier default guarantees true stateful multi-registry roundtrip fidelity.
- Eradicating physical model inspection from `StepBuilderView` completely decouples individual workflow step authoring from physical provider/model configs, allowing step definitions to remain 100% vendor-neutral and solely driven by the workflow's attached Sovereign Model Registry stack.
- Dynamic registry resolution in `scripts/run_e2e_variance_test.py` cleanly supports both direct ID and loose name/provider matching (e.g. `openai` -> `sys_6f8b1c4a2e0d49f1`), and automatic comparison defaults to comparing the workflow's configured stack against the primary alternate stack in the database.

## Remaining
- **Next Primary Gate:** Run `/tier2-hardening-backend` specifying the modified backend files.
- **Post-Implementation Hardening Gates:**
  - Execute `/tier2-hardening-backend` on modified backend files.
  - Execute `/tier2-hardening-frontend` on modified Flutter files.
- **As-Built Architectural Sync:**
  - Execute `/tier7-describe-architecture` to update architectural documents and sync Knowledge Items (`ki_desktop_pro_tool_studio_ux.md`, `ki_provider_agnostic_caching.md`).

### Hardening State Snapshot
TARGETS: 74, DONE: 9, REMAINING: [@[backend_v2/database/repositories/execution.py], @[backend_v2/hooks/scoring/__init__.py], @[backend_v2/hooks/scoring/falsifier_hook.py], @[backend_v2/hooks/scoring/passivity_hook.py], @[backend_v2/hooks/scoring/matrix_hook.py], @[backend_v2/hooks/scoring/normalization_hook.py], @[backend_v2/tests/unit/hooks/test_scoring.py], @[backend_v2/hooks/validation.py], @[backend_v2/hooks/source_verification_hook.py], @[backend_v2/hooks/atom_flattening.py], @[backend_v2/hooks/input_processing.py], @[backend_v2/hooks/integrity.py], @[backend_v2/hooks/linguistics.py], @[backend_v2/hooks/llm.py], @[backend_v2/hooks/context_mapper.py], @[backend_v2/hooks/archival.py], @[backend_v2/hooks/security.py], @[backend_v2/hooks/hydration.py], @[backend_v2/hooks/dlq_guard.py], @[backend_v2/hooks/metadata.py], @[backend_v2/hooks/metrics.py], @[backend_v2/hooks/references.py], @[backend_v2/hooks/interaction_hook.py], @[backend_v2/services/orchestrator/dag_executor.py], @[backend_v2/services/orchestrator/enriched_dag_executor.py], @[backend_v2/services/orchestrator/strategies/llm.py], @[backend_v2/services/orchestrator/strategies/base.py], @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py], @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py], @[backend_v2/services/orchestrator/prompt_compiler.py], @[backend_v2/services/orchestrator/prompt_compiler_adapter.py], @[backend_v2/services/orchestrator/context_router.py], @[backend_v2/services/orchestrator/dag_compiler.py], @[backend_v2/services/orchestrator/synthesis_payload_compressor.py], @[backend_v2/services/orchestrator/synthesis_distiller.py], @[backend_v2/services/orchestrator/matrix_explanation_service.py], @[backend_v2/services/orchestrator/rag_preflight_service.py], @[backend_v2/services/orchestrator/localization_compiler.py], @[backend_v2/services/orchestrator/extraction_schema_factory.py], @[backend_v2/services/orchestrator/atomizer.py], @[backend_v2/services/orchestrator/two_pass_atomizer.py], @[backend_v2/services/orchestrator/anchor_validation_service.py], @[backend_v2/services/orchestrator/matrix_reducer.py], @[backend_v2/services/orchestrator/engines/tda_engine.py], @[backend_v2/services/orchestrator/engines/synthesis_engine.py], @[backend_v2/services/orchestrator/extractive_sensor_service.py], @[backend_v2/services/orchestrator/result_projector.py], @[backend_v2/services/execution.py], @[backend_v2/services/usage_service.py], @[backend_v2/services/llm_task_executor.py], @[backend_v2/services/translation_service.py], @[backend_v2/services/source_verification_service.py], @[backend_v2/services/blueprint.py], @[backend_v2/services/studio/system_config_service.py], @[backend_v2/services/studio/workflow_service.py], @[backend_v2/services/studio/output_profile_service.py], @[backend_v2/services/studio/prompt_block_service.py], @[backend_v2/services/mcp/mcp_tool_loop.py], @[backend_v2/worker.py], @[backend_v2/services/cache/__init__.py], @[backend_v2/services/cache/typed_cache.py], @[scripts/_ast_guardrails.py], @[scripts/backend_audit_loop.py]]

## Resume Command
`/tier5-resume --target="@[docs/implementationplans/TRACKER_Workflow_Model_Registry_Binding.md]" --plan="@[docs/implementationplans/IMPLEMENTATION_PLAN_Workflow_Model_Registry_Binding.md]" --workflow="/tier2-hardening-backend" --rules="@[.agents/rules/00-antigravity-core.md],@[.agents/rules/01-python-backend.md],@[.agents/rules/04_directory_reference.md]"`
