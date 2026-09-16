# Implementation Plan: Option A Sovereign Model Stack Architecture, Deterministic Workflow Binding & Pro Tool UX

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

## Objective

Evolve Quorum's model configuration architecture into **Option A: Sovereign Model Stack Architecture (One Document = One Coherent 4-Tier Model Stack)** with deterministic workflow-level binding (`Workflow.model_registry_id`), eradicate vendor name leakage from workflow step authoring, upgrade the Model Registry UI to strictly comply with Desktop Pro Tool UX standards (`@[ki_desktop_pro_tool_studio_ux.md]`), and modernize `run_e2e_variance_test.py` to source all model telemetry dynamically from the database without hardcoding and support automated `--compare-registries` differential benchmark runs.

This plan delivers five core pillars:
1. **Option A Sovereign Model Stack Architecture:** Flattens `SystemConfigModelRegistry.tier_definitions` from a nested multi-provider map (`dict[provider, dict[tier, profile]]`) to a direct 4-tier mapping: `tier_definitions: dict[CognitiveTier, ModelProfile]`. Each registry document represents a single named, self-contained model stack (specifically: "Google Gemini Sovereign Stack", "OpenAI O-Series Stack", or a custom hybrid stack). Each tier profile encapsulates its own `provider`, `model_name`, and execution parameters.
2. **Strict Vendor-Neutral Step Authoring:** Eradicates physical model strings (specifically `[gemini/gemini-3.8-flash]`) and hardcoded vendor chips from `StepBuilderView`. Workflow steps author pure abstract cognitive tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`), decoupling workflow blueprints from underlying physical model infrastructure.
3. **Deterministic Workflow-to-Registry Binding:** Establishes `Workflow.model_registry_id` across backend domain models, studio DTOs, Flutter Freezed models, and `WorkflowGeneralTab`, enabling workflows to deterministically target dedicated model stacks.
4. **Desktop Pro Tool UX for Model Registry CRUD & Clone:** Upgrades `ModelRegistryView` and `StudioDashboardView` to satisfy `ki_desktop_pro_tool_studio_ux.md`:
   - Enforces Bounded Canvas Containment (`maxWidth: 1200px`) centered on screen.
   - Dual-Shield `PopScope` navigation guards with serialization-based dirty checking and localized discard confirmation modals.
   - In-view deep clone trigger (`Icons.copy`) in the top AppBar.
   - Clean 4-card tier layout (`FAST`, `BALANCED`, `DEEP`, `REASONING`) without nested expansion tiles.
   - Scalable list browsing in Studio Dashboard Tab 6 with real-time search, count indicator, and density-optimized tiles.
5. **Dynamic Database Sourcing & Automated Multi-Model Comparison in E2E Variance Harness:**
   - In `scripts/run_e2e_variance_test.py`, all model telemetry and execution parameters are dynamically resolved from the active database (`data/db_v2.json` or `seed_data.json`) eliminating hardcoded assumptions.
   - All printed telemetry displays human-readable stack names (specifically: "Google Gemini Sovereign Stack"), default providers, and actual physical model names (specifically: `gemini/gemini-3.8-flash`, `openai/gpt-5.1`) rather than opaque ID strings.
   - Adds `--model-registry` CLI option enabling ad-hoc override of the model stack for a single execution run.
   - Adds automated `--compare-registries` CLI option (supporting zero-argument automatic pairing of workflow registry against alternative DB stack, or explicit two-argument pairing) that executes sequential runs across two distinct model stacks with identical inputs and automatically synthesizes a differential report via `scripts/diff_executions.py`.

---

## User Review Required

> [!IMPORTANT]
> **Option A Schema Flattening:**
> `SystemConfigModelRegistry` simplifies from `dict[LLMProvider, dict[CognitiveTier, ModelProfile]]` to `dict[CognitiveTier, ModelProfile]`. Each registry document represents one complete 4-tier stack. A workflow binds to exactly one registry via `Workflow.model_registry_id`. When a step requests `CognitiveTier.FAST`, the orchestrator queries `registry.tier_definitions[CognitiveTier.FAST]`, resolving the exact physical model and provider configured for that stack.

> [!IMPORTANT]
> **Workflow General Tab Selection:**
> In `WorkflowGeneralTab` (Quorum Studio), the workflow author selects which Model Registry stack is used by that specific workflow from a dedicated dropdown (`Workflow.model_registry_id`). Individual workflow steps only choose abstract cognitive tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`) with zero vendor leakage.

> [!IMPORTANT]
> **Automated Multi-Model Comparison (`--compare-registries`):**
> In `scripts/run_e2e_variance_test.py`, `--compare-registries` supports both automatic and explicit modes:
> - **Automatic Mode (`--compare-registries` without arguments):** Automatically discovers the active workflow's bound registry (specifically: "Google Gemini Sovereign Stack") and pairs it against the alternative registry available in the database (specifically: "OpenAI O-Series Stack").
> - **Explicit Mode (`--compare-registries <REG1> <REG2>`):** Allows specifying any two registries by ID, slug, or title (specifically: `--compare-registries sys_e26807f3bfa3454d sys_6f8b1c4a2e0d49f1`).
> - **Execution & Differential Synthesis:** Executes Run 1 with Registry A, Run 2 with Registry B using identical inputs, and automatically spawns `scripts/diff_executions.py` to compare scoring variance, Cohen's Kappa, quote provenance, latency, and FinOps costs between the two models, saving the diff report to `data/files/executions/`.

---

## Scope & Target Boundaries

### Phase 1: Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Database System Repository Determinism (`@[backend_v2/database/repositories/system.py#L26-L61]`):**
   - Current `get_model_registry()` ignores `id` parameter and queries `Filter("type", "==", "model_registry")` with `limit=1`, always returning whichever registry happens to be first.
   - Current `update_model_registry()` forces `doc_id = res_list[0]["id"]`, clobbering existing registries rather than upserting strictly by `registry_data.id`.
   - Add parameter `registry_id: str | None = None` to `get_model_registry` and implement `get_all_model_registries() -> list[SystemConfigModelRegistry]`.
2. **System Config Service Multi-Registry Parity (`@[backend_v2/services/studio/system_config_service.py#L182-L360]`):**
   - `get_system_config(initiator, id)` ignores the `id` argument and calls `get_model_registry()`.
   - `save_system_config(initiator, id, data)` re-fetches with parameterless `get_model_registry()`.
   - `create_system_config_draft` passes obsolete `models={}` not defined in `SystemConfigModelRegistry`.
   - `clone_system_config(initiator, id)` clones whatever registry is first, ignores `id`, and omits `name = f"{data.name} (Copy)"`.
   - `delete_system_config(initiator, id)` queries the first registry instead of target `id` and lacks a repository delete call.
3. **Internal Vocabulary Ban Compliance (`@[backend_v2/services/orchestrator/strategies/llm.py#L597]`):**
   - Eradicate `"Epic 27 Telemetry: ..."` log string in `LLMNodeStrategy.execute` to strictly comply with `<rule_block id="internal_language_and_epic_ban">`.
4. **E2E Test Runner Telemetry Sourcing (`@[scripts/run_e2e_variance_test.py#L870-L968]`):**
   - `resolve_model_telemetry` assumes nested provider mapping `tier_defs[prov_name][tier_name]` and breaks on the first `model_registry` entry, failing when multi-registry or flat schemas are present.
5. **Studio Dashboard Tab 6 Virtualization & Pro-Tool Density (`@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L526-L630]`):**
   - Line 571 `config.tierDefinitions.values.fold` crashes with `NoSuchMethodError` on flat `tierDefinitions: Map<String, LlmModelConfig>`.
   - Violates `scalable_list_browsing_and_virtualization_standard` by using `ListView.builder(shrinkWrap: true)` inside `SingleChildScrollView`.
   - Missing real-time search, count badge indicator, and displays only raw opaque IDs without human-readable names.
6. **Step Builder Vendor Suffix Leakage (`@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L440-L470]`):**
   - Eradicate physical model suffix `[${physical.modelName}]` and hardcoded vendor chip (`${defaultProvider.toUpperCase()}: ${resolvedModel.modelName}`) to restore vendor-neutral cognitive tier selection.
7. **Model Registry Desktop Pro Tool UX Standards (`@[client_app_v2/lib/features/studio/views/model_registry_view.dart#L1-L300]`):**
   - Implement `ConstrainedBox(constraints: BoxConstraints(maxWidth: 1200))` canvas containment.
   - Implement `PopScope` serialization-based dirty checking with localized discard confirmation modal.
   - Add in-view Clone action button (`Icons.copy`) in AppBar.
   - Replace nested expansion tiles with 4 clean Tier cards (`FAST`, `BALANCED`, `DEEP`, `REASONING`).
   - Add `TextFormField` for editing human-readable `name`.
8. **Architectural Guardrail Seed Test Fixture Parity (`@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L129-L133]`):**
   - Guardrail test iterates `.values()` assuming nested provider dictionaries; update to inspect flat `tier_definitions.keys()`.
9. **LLM Client Tier Test Fixture Parity (`@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L198-L202]`, `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L230-L232]`):**
   - Test fixtures manipulate nested `tier_definitions["google"]["reasoning"]` instead of flat `tier_definitions["reasoning"]`.

---

### Target Files & Precise AST Bounds

- **Python Backend Domain & Schemas (`backend_v2/`):**
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L464-L489]` (`SystemConfigModelRegistry`: flatten `tier_definitions` to `dict[LaxCognitiveTier, ModelProfile]`; add `name: str`; enforce 4-tier completeness)
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L1379-L1540]` (`Workflow`: add `model_registry_id: str = Field(default="sys_e26807f3bfa3454d", ...)`)
  - `[MODIFY]` `@[backend_v2/models/v2_core.py#L1560-L1598]` (`ExecutionCreate`: add optional `model_registry_id: str | None = None`)
  - `[MODIFY]` `@[backend_v2/models/execution_core.py#L22-L44]` (`ExecutionMetadata`: add `model_registry_id: str | None = None`)
  - `[MODIFY]` `@[backend_v2/models/dtos/studio.py#L100-L150]` (`WorkflowCreateDTO`: add optional `model_registry_id: str | None = None`)
  - `[MODIFY]` `@[backend_v2/models/dtos/studio.py#L583-L614]` (`WorkflowUpdateDTO`: add optional `model_registry_id: str | None = None`)
  - `[MODIFY]` `@[backend_v2/database/interfaces.py#L206-L217]` (`ISystemRepository`: declare `get_model_registry(registry_id: str | None = None)` and `get_all_model_registries()`)
  - `[MODIFY]` `@[backend_v2/database/repositories/system.py#L26-L61]` (`SystemRepositoryImpl`: implement keyed lookup, upsert by `registry_data.id`, and `get_all_model_registries()`)
  - `[MODIFY]` `@[backend_v2/services/studio/system_config_service.py#L182-L360]` (`StudioSystemConfigService`: multi-registry lookup, save, draft, clone, delete)
  - `[MODIFY]` `@[backend_v2/services/execution.py#L385-L617]` (`ExecutionService.start_execution`: stamp `model_registry_id` on `ExecutionMetadata` and `ExecutionRecord`)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py#L37-L67]` (`StrategyContext`: add `model_registry_id: str | None = None`)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py#L161-L306]` (`NodeExecutor.execute`: forward `model_registry_id` to `StrategyContext`)
  - `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py#L565-L605]` (`LLMNodeStrategy.execute`: forward `registry_id=context.model_registry_id` to `LLMClient.from_tier`; eradicate line 597 telemetry text)
  - `[MODIFY]` `@[backend_v2/llm/client.py#L124-L214]` (`LLMClient.from_tier`: accept `registry_id: str | None = None` and resolve directly from flat `tier_definitions[tier]`)
  - `[MODIFY]` `@[backend_v2/worker.py#L1050-L1075]` (`generate_profile_synthesis_and_pdf_task`: forward `registry_id` to `LLMClient.from_tier`)
  - `[MODIFY]` `@[backend_v2/services/studio/workflow_service.py#L279-L306]` (`StudioWorkflowService.create_workflow_draft`: bind default `model_registry_id`)

- **Target Data Vault (`backend_v2/seed/seed_data.json`):**
  - `[MODIFY]` `@[backend_v2/seed/seed_data.json#L4-L131]` (Migrate `sys_e26807f3bfa3454d` to Option A flat schema with `name: "Google Gemini Sovereign Stack"`; add `sys_6f8b1c4a2e0d49f1` with `name: "OpenAI O-Series Stack"`; bind `model_registry_id: "sys_e26807f3bfa3454d"` to all workflows)

- **E2E Variance & Reliability Test Harness (`scripts/`):**
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L717-L820]` (`trigger_execution`: forward `model_registry_id` in execution payload)
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L870-L968]` (`resolve_model_telemetry`: resolve Option A flat schema by registry ID or workflow binding)
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L970-L1010]` (`print_model_telemetry`: display human-readable stack names and physical model names)
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L1333-L1641]` (`run_variance_test`: implement sequential multi-model comparison and diff report generation)
  - `[MODIFY]` `@[scripts/run_e2e_variance_test.py#L1643-L1707]` (`main`: add `--model-registry` and `--compare-registries` CLI flags with argument validation)

- **Flutter Client Domain & Quorum Studio (`client_app_v2/`):**
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/model_config.dart#L10-L24]` (`ModelConfig`: flat `tierDefinitions: Map<String, LlmModelConfig>`, `name: String`)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/models/workflow.dart#L128-L175]` (`Workflow`: add `modelRegistryId: String`)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L430-L475]` (Remove physical model name suffix and hardcoded vendor chip)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/model_registry_view.dart#L1-L300]` (Bounded canvas 1200px, PopScope dirty checks, AppBar clone action, name input, 4-tier cards)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L526-L630]` (Tab 6: real-time search, count badge, virtualized list, and pro-tool cards)
  - `[MODIFY]` `@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart#L159-L220]` (Model registry dropdown selector adjacent to output profile and MCP gateway dropdowns)
  - `[MODIFY]` `@[client_app_v2/lib/l10n/app_en.arb]` (Add model registry localization keys)
  - `[MODIFY]` `@[client_app_v2/lib/l10n/app_fi.arb]` (Add Finnish model registry localization keys)

- **Automated Verification Tests:**
  - `[NEW]` `@[backend_v2/tests/unit/database/repositories/test_system_model_registry.py]` (Test `get_model_registry(id)`, `get_all_model_registries()`, and `ResourceNotFoundError`)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_model_registry.py#L24-L41]` (Update dummy registry fixture for Option A flat schema)
  - `[MODIFY]` `@[backend_v2/tests/unit/test_seed_architectural_guardrails.py#L122-L165]` (Update seed guardrail assertions for flat `tier_definitions`)
  - `[MODIFY]` `@[backend_v2/tests/unit/llm/test_llm_client_tiers.py#L161-L241]` (Update tier test fixtures in `TestLLMClientTiersFailFast` for flat `tier_definitions`)
  - `[NEW]` `@[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]` (Test model registry dropdown selection and mutation)
  - `[MODIFY]` `@[client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart]` (Verify vendor-neutral cognitive tier dropdown labels)
  - `[MODIFY]` `@[client_app_v2/test/features/studio/views/model_registry_view_test.dart]` (Verify 1200px containment, name field, 4-tier cards, and dirty-state confirmation)

---

### Falsification & Red-Teaming Analysis (Attack Surface & Mitigations)

1. **Failure Vector 1: Seed Vault & In-Memory Pre-Flight Deserialization Shock:**
   - *Attack*: Modifying `SystemConfigModelRegistry.tier_definitions` in `backend_v2/models/v2_core.py` before updating `seed_data.json` or running database re-seed will immediately break all backend tests and application boots with Pydantic `ValidationError`.
   - *Mitigation*: Enforce strict Two-Phase Atomic Ingress per `03_seed_vault.md`: migrate `backend_v2/seed/seed_data.json` in the exact same atomic transaction as `v2_core.py`, run `scripts/audit_database_atoms.py --strict`, and execute `uv run python backend_v2/seed/run_seed.py local --dry-run` to verify 100% in-memory validation before persisting.
2. **Failure Vector 2: Tab 6 Dashboard Runtime Method Absence (`NoSuchMethodError`):**
   - *Attack*: In `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L571`, the code runs `config.tierDefinitions.values.fold(...)` assuming `tierDefinitions` is a nested map where `.values` returns maps with `.length`. With Option A flat `Map<String, LlmModelConfig>`, `.values` returns `LlmModelConfig` objects. Calling `.length` on `LlmModelConfig` throws runtime `NoSuchMethodError` crashing Tab 6.
   - *Mitigation*: Update `studio_dashboard_view.dart` in Phase 1 before running `flutter_audit_loop.py`, replacing the fold loop with direct `config.tierDefinitions.length`.
3. **Failure Vector 3: Multi-Registry Fallback Cascade vs Single Sovereign Pipeline Invariant:**
   - *Attack*: If `Workflow.model_registry_id` targets a non-existent or deleted registry ID, the orchestrator might fall back to parameterless `get_model_registry()`, violating `<rule_block id="zero_backward_compatibility_planning_ban">` and silently executing workflows on unintended models.
   - *Mitigation*: `ISystemRepository.get_model_registry(registry_id: str | None = None)` MUST raise `ResourceNotFoundError(resource_type="system_config", resource_id=registry_id)` Fail-Fast when an explicit ID is not found, preceded by structured `logger.error` per `rfc7807_dual_reporting_mandate`. Zero silent fallback to other registries.
4. **Failure Vector 4: Freezed Model Dirty Checking False Positives:**
   - *Attack*: In `ModelRegistryView`, using reference inequality (`_editableConfig != widget.initialConfig`) triggers false-positive dirty confirmation dialogs on unmodified views because `@Freezed` entities do not implement deep value equality.
   - *Mitigation*: Implement Serialization-Based Dirty Checking per `desktop_pro_tool_studio_ux_mandate`: `jsonEncode(_editableConfig.toJson()) != _initialConfigJson`, guaranteeing deterministic dirty state with zero false positives.
5. **Failure Vector 5: E2E Runner Argument Count Ambiguity:**
   - *Attack*: In `scripts/run_e2e_variance_test.py`, `--compare-registries` configured with `nargs="*"` could receive 1 or 3+ arguments, causing indexing errors or ambiguous pairings.
   - *Mitigation*: Explicitly validate in `main`: `if len(args.compare_registries) not in (0, 2): parser.error("--compare-registries requires either 0 arguments (auto-paired against DB alternative) or exactly 2 arguments (<REG1> <REG2>).")`.

---

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Backend Domain Schemas**<br>`@[backend_v2/models/v2_core.py#L464-L489]`<br>`@[backend_v2/models/v2_core.py#L1379-L1540]`<br>`@[backend_v2/models/dtos/studio.py#L100-L150]` | Banned nested multi-provider dictionaries (`tier_definitions[provider][tier]`), loose string defaults, and drive-by schema mutations. | Enforce Option A flat mapping `tier_definitions: Annotated[dict[LaxCognitiveTier, ModelProfile], Field(strict=False)]`, `name: str`, `model_registry_id` on `Workflow` and DTOs, and `@model_validator(mode="after")` verifying all 4 canonical tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`). | Pruned multi-provider fallback cascades, heuristic provider detection, and custom stack wrapper classes. | `test_seed_architectural_guardrails.py`<br>`ValidationError` on missing tier. `backend_audit_loop.py` strict typing gate. |
| **Database Persistence & Studio Service**<br>`@[backend_v2/database/repositories/system.py#L26-L61]`<br>`@[backend_v2/services/studio/system_config_service.py#L182-L360]` | Banned parameterless `get_model_registry()`, hardcoded `limit=1` blind queries, ignoring `id` in service CRUD/clone, and obsolete `models={}` fields. | Deterministic `get_model_registry(registry_id: str | None = None)` raising `ResourceNotFoundError` if missing, `get_all_model_registries()`, keyed upsert by `registry_data.id`, and clone with `name = f"{data.name} (Copy)"`. | Pruned generic repository abstractions and dynamic reflection (`getattr`/`hasattr`). | `backend_v2/tests/unit/database/repositories/test_system_model_registry.py`<br>Assertion of real database persistence roundtrip. |
| **Orchestrator & LLM Dispatch**<br>`@[backend_v2/services/execution.py#L385-L617]`<br>`@[backend_v2/services/orchestrator/dag_executor.py#L161-L306]`<br>`@[backend_v2/services/orchestrator/strategies/llm.py#L565-L605]`<br>`@[backend_v2/llm/client.py#L124-L214]`<br>`@[backend_v2/worker.py#L1050-L1075]` | Banned ad-hoc strategy aliases, hardcoded model strings ("gpt-5.1"), silent fallback to default registry when execution requests override, and internal vocabulary string `"Epic 27 Telemetry"`. | Stamp `model_registry_id` on `ExecutionMetadata` and `ExecutionRecord`; forward `registry_id` through `StrategyContext` and `worker.py` into `LLMClient.from_tier(tier, repo, registry_id=...)`; resolve profile in O(1) from flat `registry.tier_definitions[tier]`. | Pruned parallel strategy loaders, heuristic provider overrides, and dual execution pipelines. | `test_llm_client_tiers.py`<br>Verification that `from_tier` loads exact physical model and provider from specified registry. |
| **Studio UI & Pro Tool UX**<br>`@[client_app_v2/lib/features/studio/views/step_builder_view.dart#L430-L475]`<br>`@[client_app_v2/lib/features/studio/views/model_registry_view.dart#L1-L300]`<br>`@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart#L526-L630]`<br>`@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart#L159-L220]` | Banned physical model leak (`[${physical.modelName}]`), vendor preview chips in step builder, unbounded form width stretching, `shrinkWrap: true` lists, and un-intercepted modal dismissal. | Enforce vendor-neutral tier dropdowns, Bounded Canvas Containment (`maxWidth: 1200px`), `PopScope` serialization dirty checking with localized discard modal, in-view clone button (`Icons.copy`), real-time search and count badge in Tab 6, and workflow dropdown selector. | Pruned nested expansion tiles in `ModelRegistryView` in favor of 4 clean tier cards; pruned redundant vendor indicator widgets. | `step_builder_view_dropdown_test.dart`<br>`model_registry_view_test.dart`<br>`workflow_general_tab_model_registry_test.dart`<br>`flutter_audit_loop.py --build`. |
| **E2E Variance Test Harness**<br>`@[scripts/run_e2e_variance_test.py#L717-L1707]`<br>`@[backend_v2/seed/seed_data.json#L4-L131]` | Banned hardcoded model assumptions, breaking on first registry document in database, and opaque ID outputs. | Dynamic database resolution of `tier_definitions` for target stack; human-readable telemetry output; `--model-registry <ID>` override flag; automated `--compare-registries` pairing workflow registry against alternative DB stack and spawning `diff_executions.py`. | Pruned manual execution diff scripting and custom pricing dictionaries. | `uv run python scripts/run_e2e_variance_test.py --help`<br>`--compare-registries --show-matrices` dry run verification. |

---

---

```xml
<execution_protocol level="0_create_plan">
  <step id="1" name="BACKEND DOMAIN SCHEMA FLATTENING FOR OPTION A">
    <action>In `backend_v2/models/v2_core.py`, update `SystemConfigModelRegistry` to implement Option A:</action>
    <action>Add `name: str = Field(default="Default Model Registry", description="Human-readable title")`.</action>
    <action>Change `tier_definitions: Annotated[dict[LaxCognitiveTier, ModelProfile], Field(strict=False)] = Field(description="Direct mapping of the four canonical cognitive tiers to physical profiles")`.</action>
    <action>Update `validate_tier_completeness` to assert that `self.tier_definitions` contains all four canonical tiers (`FAST`, `BALANCED`, `DEEP`, `REASONING`).</action>
    <action>Add `model_registry_id: str = Field(default="sys_e26807f3bfa3454d", pattern=r"^(sys_[a-fA-F0-9]{16,32}|cfg_model_registry_\d{2})$", description="System config ID of the attached model registry")` to `Workflow` in `backend_v2/models/v2_core.py`.</action>
    <action>Add `model_registry_id: str | None = Field(default=None, description="Optional execution-level model registry stack override")` to `ExecutionCreate` in `backend_v2/models/v2_core.py`.</action>
    <action>Update `WorkflowCreateDTO` and `WorkflowUpdateDTO` in `backend_v2/models/dtos/studio.py` to include optional `model_registry_id: str | None = None`.</action>
    <constraint invariant="ConfigDict(strict=True, extra='forbid')">All updated Pydantic models must preserve strict mode and forbid extra attributes.</constraint>
  </step>

  <step id="2" name="DATABASE REPOSITORY & SERVICE MULTI-REGISTRY RESOLUTION">
    <action>Update `ISystemRepository` in `backend_v2/database/interfaces.py` to declare `get_model_registry(registry_id: str | None = None) -> SystemConfigModelRegistry` and `get_all_model_registries() -> list[SystemConfigModelRegistry]`.</action>
    <action>In `backend_v2/database/repositories/system.py`, implement deterministic registry lookup:</action>
    <action>If `registry_id` is supplied, query `system_config` with filter `id == registry_id` and raise `ResourceNotFoundError` if not found.</action>
    <action>If `registry_id` is None, query `system_config` with filter `type == "model_registry"` ordered deterministically.</action>
    <action>Implement `update_model_registry` to upsert using `registry_data.id` as the document key.</action>
    <action>In `backend_v2/services/studio/system_config_service.py`, update `get_system_config` to query by `registry_id=id`, `get_all_system_configs` to call `get_all_model_registries`, and `clone_system_config` to clone source registry with updated `name = f"{data.name} (Copy)"` and new opaque ID.</action>
    <action>In `backend_v2/services/execution.py`, update `start_execution` to stamp `model_registry_id = payload.model_registry_id or workflow.model_registry_id` onto the created execution record.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Precede any ResourceNotFoundError with structured logger.error containing registry_id parameter.</constraint>
  </step>

  <step id="3" name="ORCHESTRATOR & LLM DISPATCH INTEGRATION">
    <action>Add `model_registry_id: str | None = None` to `StrategyContext` in `backend_v2/services/orchestrator/strategies/base.py`.</action>
    <action>Update `DAGExecutor` in `backend_v2/services/orchestrator/dag_executor.py` to pass `model_registry_id=execution.model_registry_id or workflow.model_registry_id` when constructing `StrategyContext`.</action>
    <action>Update `LLMNodeStrategy` in `backend_v2/services/orchestrator/strategies/llm.py` to forward `registry_id=context.model_registry_id` into `LLMClient.from_tier`.</action>
    <action>In `backend_v2/llm/client.py`, update `LLMClient.from_tier` to resolve strategy directly: `target_strategy = registry.tier_definitions[tier]`, reading `target_strategy.provider` and `target_strategy.model_name` from that profile.</action>
    <action>Update `worker.py` synthesis and explanation invocations to pass `execution.model_registry_id or workflow.model_registry_id` when instantiating `LLMClient` instances.</action>
  </step>

  <step id="4" name="VENDOR LEAK ERADICATION IN STEP BUILDER">
    <action>In `client_app_v2/lib/features/studio/views/step_builder_view.dart`, remove physical model name suffix `[${physical.modelName}]` from `DropdownMenuItem` text.</action>
    <action>Display pure abstract cognitive tier label and description via `getTierLabel(tier)`.</action>
    <action>Remove hardcoded vendor preview chip from step authoring layout.</action>
    <action>Update `client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart` to verify that dropdown menu items contain zero physical model strings.</action>
  </step>

  <step id="5" name="DESKTOP PRO TOOL UX UPGRADE FOR MODEL REGISTRY">
    <action>In `client_app_v2/lib/features/studio/models/model_config.dart`, update `tierDefinitions` to `Map<String, LlmModelConfig>` and add `name: String`.</action>
    <action>In `client_app_v2/lib/features/studio/views/model_registry_view.dart`, implement Bounded Canvas Containment by wrapping form body in `Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), ...))`.</action>
    <action>In `_buildSystemAttributes`, add a `TextFormField` for editing human-readable `name`, and add a `DropdownButtonFormField<String>` for `default_provider` (`google` versus `openai`).</action>
    <action>Replace nested provider expansion tiles in `_buildModelsSection` with 4 clean Tier cards (`FAST`, `BALANCED`, `DEEP`, `REASONING`), each displaying provider selector, model name input, and execution parameters.</action>
    <action>In `ModelRegistryView` AppBar, add an in-view Clone action button (`Icons.copy`) that invokes `modelRegistryControllerProvider.notifier.cloneConfig(id)` and navigates to the cloned draft.</action>
    <action>Implement `PopScope` with serialization-based dirty checking (`jsonEncode(_editableConfig.toJson()) != _initialConfigJson`) and localized discard confirmation modal.</action>
    <action>In `client_app_v2/lib/features/studio/views/studio_dashboard_view.dart` Tab 6, add real-time search input, active count indicator badge, and pro-tool compact card density displaying `name`, `id`, and `default_provider` badges.</action>
  </step>

  <step id="6" name="WORKFLOW GENERAL TAB MODEL REGISTRY LINKAGE">
    <action>Update `Workflow` in `client_app_v2/lib/features/studio/models/workflow.dart` to include `@JsonKey(name: 'model_registry_id') @Default('sys_e26807f3bfa3454d') String modelRegistryId`.</action>
    <action>In `client_app_v2/lib/features/studio/views/widgets/workflow/workflow_general_tab.dart`, add a `DropdownButtonFormField<String>` selector listing available model registries by `name` and `default_provider`.</action>
    <action>Add localized strings for `studioWorkflowModelRegistry` in `app_en.arb` and `app_fi.arb`.</action>
    <action>Regenerate Freezed models: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build`.</action>
  </step>

  <step id="7" name="SEED VAULT SYNCHRONIZATION & QUALITY GATES">
    <action>Migrate `sys_e26807f3bfa3454d` in `backend_v2/seed/seed_data.json` to Option A flat schema: `"name": "Google Gemini Sovereign Stack"`, `"default_provider": "google"`, and `"tier_definitions"` directly mapping `"fast"`, `"balanced"`, `"deep"`, `"reasoning"`.</action>
    <action>Add `"sys_6f8b1c4a2e0d49f1"` in `backend_v2/seed/seed_data.json`: `"name": "OpenAI O-Series Stack"`, `"default_provider": "openai"`, and `"tier_definitions"` directly mapping the four tiers to OpenAI profiles.</action>
    <action>Add `"model_registry_id": "sys_e26807f3bfa3454d"` to all workflow definitions in `backend_v2/seed/seed_data.json`.</action>
    <action>Update test fixtures in `test_model_registry.py`, `test_seed_architectural_guardrails.py`, and `test_llm_client_tiers.py` to match Option A flat schema.</action>
    <action>Execute seed verification: `uv run python scripts/audit_database_atoms.py --strict`.</action>
    <action>Execute backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/database/repositories/system.py --test`.</action>
    <action>Execute flutter audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/model_registry_view.dart`.</action>
  </step>

  <step id="8" name="E2E VARIANCE TEST HARNESS DYNAMIC TELEMETRY & AUTOMATED COMPARISON">
    <action>In `scripts/run_e2e_variance_test.py`, update `resolve_model_telemetry` to load target model registry records from `data/db_v2.json` or `seed_data.json` based on the workflow's `model_registry_id` or CLI override.</action>
    <action>Update `print_model_telemetry` to display human-readable stack names, default providers, and actual physical model names (`gemini/gemini-3.8-flash`, `openai/gpt-5.1`) without raw opaque IDs.</action>
    <action>In `main` of `scripts/run_e2e_variance_test.py`, add `--model-registry` CLI option accepting registry ID, slug, or name.</action>
    <action>In `main` of `scripts/run_e2e_variance_test.py`, add `--compare-registries` CLI option with `nargs="*"` supporting zero arguments (automatic comparison of workflow registry against alternative DB stack) or two arguments (`--compare-registries <REG1> <REG2>`).</action>
    <action>Implement `resolve_comparison_registries(db_path, workflow_id, cli_args)` to deterministically resolve Registry A and Registry B by ID, slug, or title, falling back to pairing the workflow stack with the other available database stack.</action>
    <action>In `run_variance_test`, implement the multi-model comparison flow: print side-by-side telemetry for both stacks, execute Run 1 with Registry A, execute Run 2 with Registry B using identical inputs, and automatically invoke `scripts/diff_executions.py` on the resulting execution IDs with markdown report generation.</action>
    <action>In `trigger_execution`, forward `model_registry_id` to `POST /api/v2/execution/executions/` request payload when an override is active.</action>
    <action>Verify execution test harness: `uv run python scripts/run_e2e_variance_test.py --help`.</action>
  </step>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
1. **Repository Unit Test:**
   ```powershell
   uv run pytest backend_v2/tests/unit/database/repositories/test_system_model_registry.py -vv
   ```
   Verifies:
   - Querying an existing registry ID returns that exact model registry.
   - Querying all model registries returns the complete list.
   - Querying an invalid ID raises `ResourceNotFoundError` Fail-Fast.

2. **LLMClient Dispatch Unit Test:**
   ```powershell
   uv run pytest backend_v2/tests/unit/llm/test_llm_client_tiers.py -vv
   ```
   Verifies that `LLMClient.from_tier(..., registry_id="...")` forwards the registry ID and resolves strategy directly from the flat `tier_definitions[tier]`.

3. **Step Builder Vendor Neutrality Widget Test:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart
   ```
   Verifies that the dropdown choices display only cognitive tier descriptions and contain no physical model identifiers.

4. **Model Registry Desktop Pro Tool UX Widget Test:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/model_registry_view_test.dart
   ```
   Verifies `maxWidth: 1200px` canvas containment, in-view clone action, 4-tier cards layout, and dirty-state discard confirmation.

5. **Workflow General Tab Selector Widget Test:**
   ```powershell
   uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart
   ```
   Verifies that the model registry dropdown lists registered configs and mutates `workflow.modelRegistryId`.

6. **E2E Variance Test CLI Verification:**
   ```powershell
   uv run python scripts/run_e2e_variance_test.py --help
   uv run python scripts/run_e2e_variance_test.py --compare-registries --show-matrices
   ```
   Verifies that `--model-registry` and `--compare-registries` CLI options are registered, documented, and automatically resolve comparison model stacks without error.

7. **Global Quality Gates:**
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --test
   uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/model_registry_view.dart
   ```
