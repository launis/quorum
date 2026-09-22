<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>


# EPIC 153: Client Desktop Pro Tool UX & Full-Duplex Zero Permissive Typing Parity

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective

Achieve **absolute zero permissive typing** across all client API consumers, controllers, and views, while elevating Quorum's Flutter desktop client (`client_app_v2`) to meet the strict 16-invariant standard defined in `@[ki_desktop_pro_tool_studio_ux.md]` and the O(1) Dumb Painter rendering performance mandate defined in `@[ki_dumb_painter_sdui.md]`.

This Epic establishes 1:1 Full-Duplex DTO parity between backend Pydantic V2 models and frontend Freezed models across 6 distinct domains (including global `StudioClient` typing parity), eradicates intermediate render-tree calculation thrashing in SDUI adapters, virtualizes all Quorum Studio master list views with sticky pinned search controls, and hardens modal dialogs against uncommitted state loss and jarring SnackBar alerts.

### Problem Statement

Quorum's backend has achieved strict Pydantic V2 sovereignty (Epics 149–152). However, architectural forensics across `client_app_v2` reveal three critical structural bottlenecks:

1. **Full-Duplex Permissive Typing Debt (`DGR001` Violations across 6 Domains):**
   Despite strict backend Pydantic SSOT contracts, Flutter client code downgrades incoming and outgoing data to raw, untyped `Map<String, dynamic>` dictionaries across 6 key feature domains:
   - **Domain A (MCP Gateways):** Backend returns `list[SystemConfigMCPGateways]`. Flutter handles raw maps in `studio_client.dart#L272-302`, `mcp_gateways_controller.dart`, `mcp_gateways_master_view.dart`, and `mcp_gateway_view.dart`.
   - **Domain B (LLM Platforms):** Backend returns `list[LLMPlatformDTO]`. Flutter handles `Future<List<Map<String, dynamic>>>` in `studio_client.dart#L220` and `model_registry_controller.dart#L213`.
   - **Domain C (Available Workflows Ingestion):** `new_execution_view.dart#L26-37` makes an untyped API call returning `Future<List<Map<String, dynamic>>>` and stores selection in `Map<String, dynamic>? _selectedWorkflow`, manually executing fallback dictionary checks despite the existence of `@[client_app_v2/lib/features/studio/models/workflow.dart]`.
   - **Domain D (Workflow UI Schema):** Backend returns `WorkflowSchemaResponseDTO`. Flutter handles `Future<Map<String, dynamic>>` in `workflow_client.dart#L22` and parses raw maps manually in `dynamic_start_screen.dart#L42-140`.
   - **Domain E (Human Override Request):** Backend expects `HumanOverrideRequest`. Flutter manually constructs untyped dictionary literals in `human_override_dialog.dart#L62-77` and passes raw map payloads to `execution_client.dart:overrideAtom`.
   - **Domain F (StudioClient Global Full-Duplex Typed Parity):** All 33 CRUD, clone, draft, and simulation endpoints in `studio_client.dart` (`getPromptBlocks`, `getPromptBlock`, `savePromptBlock`, `simulatePromptBlock`, `clonePromptBlock`, `createPromptBlockDraft`, `getWorkflows`, `getWorkflow`, `saveWorkflow`, `simulateWorkflow`, `cloneWorkflow`, `createWorkflowDraft`, `getSteps`, `getStep`, `saveStep`, `cloneStep`, `createStepDraft`, `getSupportedPlatforms`, `getSystemConfigs`, `getSystemConfig`, `saveSystemConfig`, `cloneSystemConfig`, `createSystemConfigDraft`, `getMcpGateways`, `getMcpGateway`, `saveMcpGateway`, `cloneMcpGateway`, `createMcpGatewayDraft`, `getOutputProfiles`, `getOutputProfile`, `saveOutputProfile`, `cloneOutputProfile`, `createOutputProfileDraft`) handle raw `Map<String, dynamic>` returns and payloads, triggering 33 `DGR001` warnings.

2. **SDUI Adapter Intermediate Computation Overhead (Render Tree Thrashing):**
   - In `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`, the `build()` method executes nested sorting passes (`breakdown.keys.toList()..sort(...)`, `grouped.keys.toList()..sort(...)`) and multi-pass `.where(...).map(...)` filtering on every render tick.
   - In `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]`, dynamic mutable widget arrays (`final List<Widget> boxes = [];`) are allocated on every pass, binding hardcoded non-token colors (`AppColors.intentWarning.withValues(alpha: 0.1)`).
   - In `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`, 9 instances of `const SizedBox.shrink()` intentionally conceal empty or unrendered blocks, violating `sized_box_shrink_ban` and triggering fatal `DGR002` violations.

3. **Desktop Pro Tool Studio UX Invariant Deficits (`ki_desktop_pro_tool_studio_ux.md`):**
   - **Master List Views (`workflows_master_view.dart`, `matrices_master_view.dart`, `output_profile_list_view.dart`, `mcp_gateways_master_view.dart`):** Wrap unvirtualized `ListView.builder(shrinkWrap: true)` inside `SingleChildScrollView`, lack sticky pinned headers, stretch across 4K displays without 1200px containment, and violate `freezed_when_ban` via Freezed `.when()`.
   - **Studio Modals (`human_override_dialog.dart`, `scale_editor_modal.dart`, `step_simulation_dialog.dart`):** Lack `PopScope(canPop: false)` discard interceptors, allow uncommitted buffer evaporation, present errors via modal SnackBars instead of inline canvas banners, and lack auto-scroll to invalid fields.

### Quantitative Scope Summary

| Metric | Target Scope / Count | Architectural Context & Blast Radius |
| :--- | :--- | :--- |
| **Affected Feature Domains** | 6 Distinct Domains | Domain A (MCP Gateways), Domain B (LLM Platforms), Domain C (Available Workflows Ingestion), Domain D (Workflow UI Schema), Domain E (Human Override Request), Domain F (StudioClient Global Full-Duplex Typed Parity) |
| **Directly Touched Files** | 28 Client Target Files | 7 New Freezed Models (including PromptBlockSimulationRequest), 3 API Clients, 5 Controllers, 8 Views, 5 Widgets |
| **1-Hop Caller Blast Radius** | 14 Caller Files | Master views, dynamic start screen, new execution view, profile editor view, studio controller, prompt blocks controller, workflow builder controller, create report dialog, output profile controller, prompt block builder view, scale editor modal, and test suites |
| **`DGR001` Violations Eradicated** | 45 Methods / Providers | All 33 methods in `studio_client.dart`, 1 in `workflow_client.dart`, 1 in `execution_client.dart`, 10 in controllers (`mcp_gateways_controller.dart`, `model_registry_controller.dart`, `prompt_blocks_controller.dart`, `studio_controller.dart`), and 1 in `new_execution_view.dart` |
| **`DGR002` Violations Eradicated** | 9 Instances | All 9 `const SizedBox.shrink()` occurrences in `sdui_blocks_renderer.dart` replaced with declarative collection-`if` guards |
| **`DGR003` & L10n Eradicated** | 3 Hardcoded Text Strings | Hardcoded Finnish lookups in `workflows_master_view.dart` and dialogs replaced with bilingual `AppLocalizations` |
| **`freezed_when_ban` & Modal SnackBars** | 1 Freezed `.when()` + 8 SnackBar calls | Replaced with Dart 3 native `switch` pattern matching and inline canvas error banners across Master Views and Modals |
| **Intermediate Thrashing Cleanups** | 3 Hotspot Renderers | Monolithic 635-line `SduiMatrixTableWidget` (in-build sorting purged, decomposed into 4 cells), `XAIAxisTelemetryGrid` (mutable list purged), `AtomMatrixTableWidget` (breakpoint fixed to `< 800px`, color swatches tokenized) |
| **Virtualization & Containment** | 4 Master Views + 1 Editor | `WorkflowsMasterView`, `MatricesMasterView`, `OutputProfileListView`, `McpGatewaysMasterView` (virtualized `ListView.builder`, sticky `StudioMasterHeader`, 1200px centered canvas) + `ProfileEditorView` (1200px centered canvas) |
| **Modal UX Deficits Hardened** | 3 Studio Dialogs | `HumanOverrideDialog`, `ScaleEditorModal`, `StepSimulationDialog` (`PopScope`, focus unblur, serialization dirty checking, 480-1400px min/max bounds, auto-scroll to invalid field) |

---

## 2. Architectural Impact & Compliance Matrix

### Destructive Operation Inventory & Sunset List (What We Will REMOVE)

| File / Component | Deprecated / Deleted Symbol | Target Replacement | Disposition / Sunset Rationale |
| :--- | :--- | :--- | :--- |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getPromptBlocks()` | `Future<List<PromptBlock>> getPromptBlocks()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getPromptBlock(id)` | `Future<PromptBlock> getPromptBlock(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> savePromptBlock(id, data)` | `Future<PromptBlock> savePromptBlock(id, PromptBlock data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> clonePromptBlock(id)` | `Future<PromptBlock> clonePromptBlock(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createPromptBlockDraft()` | `Future<PromptBlock> createPromptBlockDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getWorkflows()` | `Future<List<Workflow>> getWorkflows()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getWorkflow(id)` | `Future<Workflow> getWorkflow(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> saveWorkflow(id, data)` | `Future<Workflow> saveWorkflow(id, Workflow data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> cloneWorkflow(id)` | `Future<Workflow> cloneWorkflow(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createWorkflowDraft()` | `Future<Workflow> createWorkflowDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getSteps()` | `Future<List<NodeStrategy>> getSteps()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getStep(id)` | `Future<NodeStrategy> getStep(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> saveStep(id, data)` | `Future<NodeStrategy> saveStep(id, NodeStrategy data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> cloneStep(id)` | `Future<NodeStrategy> cloneStep(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createStepDraft()` | `Future<NodeStrategy> createStepDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getSystemConfigs()` | `Future<List<ModelConfig>> getSystemConfigs()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getSystemConfig(id)` | `Future<ModelConfig> getSystemConfig(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> saveSystemConfig(id, data)` | `Future<ModelConfig> saveSystemConfig(id, ModelConfig data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> cloneSystemConfig(id)` | `Future<ModelConfig> cloneSystemConfig(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createSystemConfigDraft()` | `Future<ModelConfig> createSystemConfigDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getOutputProfiles()` | `Future<List<OutputProfile>> getOutputProfiles()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getOutputProfile(id)` | `Future<OutputProfile> getOutputProfile(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> saveOutputProfile(id, data)` | `Future<OutputProfile> saveOutputProfile(id, OutputProfile data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> cloneOutputProfile(id)` | `Future<OutputProfile> cloneOutputProfile(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createOutputProfileDraft()` | `Future<OutputProfile> createOutputProfileDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> getMcpGateway(id)` | `Future<McpGateway> getMcpGateway(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getMcpGateways()` | `Future<List<McpGateway>> getMcpGateways()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> saveMcpGateway(id, data)` | `Future<McpGateway> saveMcpGateway(id, McpGateway data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> cloneMcpGateway(id)` | `Future<McpGateway> cloneMcpGateway(id)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> createMcpGatewayDraft()` | `Future<McpGateway> createMcpGatewayDraft()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<List<Map<String, dynamic>>> getSupportedPlatforms()` | `Future<List<LlmPlatform>> getSupportedPlatforms()` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> simulatePromptBlock(data)` | `Future<PromptBlockSimulationResponse> simulatePromptBlock(PromptBlockSimulationRequest request)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/studio_client.dart]` | `Future<Map<String, dynamic>> simulateWorkflow(data)` | `Future<WorkflowSimulationResponse> simulateWorkflow(Workflow data)` | `DGR001` Zero Permissive Typing enforcement |
| `@[client_app_v2/lib/core/api/workflow_client.dart]` | `Future<Map<String, dynamic>> getWorkflowUiSchema(id)` | `Future<WorkflowUiSchema> getWorkflowUiSchema(id)` | Eradication of obsolete "De-Generator policy" comment and loose map |
| `@[client_app_v2/lib/core/api/execution_client.dart]` | `required Map<String, dynamic> payload` in `overrideAtom` | `required HumanOverrideRequestDto payload` | Full-Duplex DTO parity with `HumanOverrideRequest` |
| `@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]` | `rawList.map((m) => OutputProfile.fromJson(m))` | Directly consume `List<OutputProfile>` from `getOutputProfiles()` | Redundant client deserialization purge |
| `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` | In-controller `safeIsolateRun(() => rawList.map((e) => OutputProfile.fromJson(e)).toList())` | Directly return `await client.getOutputProfiles()` | Redundant intermediate deserialization purge |
| `@[client_app_v2/test/features/reports/execution_reports_generating_test.dart]` | `when(() => mockStudioClient.getOutputProfiles()).thenAnswer((_) async => profilesJson);` | `when(() => mockStudioClient.getOutputProfiles()).thenAnswer((_) async => profilesList);` | Typed Freezed mock fixture alignment |
| `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]` | `useMutation<Map<String, dynamic>>` + `ScaffoldMessenger.showSnackBar` for DAG validation | `useMutation<WorkflowSimulationResponse>` + inline canvas status banner | Zero Permissive Typing and modal SnackBar ban |
| `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]` | `useMutation<Map<String, dynamic>>` + `ScaffoldMessenger.showSnackBar` for prompt simulation | `useMutation<PromptBlockSimulationResponse>` + inline canvas status banner | Zero Permissive Typing and modal SnackBar ban |
| `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]` | Untyped `availableWorkflows` provider returning raw maps | `Future<List<Workflow>>` provider delegating to `Workflow.parseListInBackground` | Elimination of manual dictionary extraction loops |
| `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]` | `Map<String, dynamic>? _selectedWorkflow` | Strongly typed `Workflow? _selectedWorkflow` | INTENTIONALLY DROPPED loose map state; replaced with typed getters |
| `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]` | `const SizedBox.shrink()` (9 occurrences) | Declarative collection-`if` empty guards (`if (block.text.isNotEmpty)`) | `DGR002` fatal guardrail compliance |
| `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]` | In-`build` sorting (`..sort(...)`) and nested filtering loops | Pre-sorted level keys during initialization and 4 private Dumb Painter cell widgets | Eliminate UI-thread jank and render tree thrashing |
| `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]` | Mutable `final List<Widget> boxes = [];` and hardcoded `AppColors` | Const-constructible card widgets and Material 3 theme tokens | Theme token purity and zero mutable allocations |
| `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]` | Arbitrary breakpoint `constraints.maxWidth < 600` and raw colors | Canonical Macro-Breakpoint `< 800px` and Material 3 `colorScheme` tokens | Responsive standard alignment (`ki_desktop_pro_tool_studio_ux.md`) |
| All 4 Studio Master Views | `SingleChildScrollView` + `ListView.builder(shrinkWrap: true)` | Virtualized `ListView.builder` with `prototypeItem` and sticky `StudioMasterHeader` | Buttery 60 FPS scrolling and sticky search controls |
| Studio Master Views & Modals | Freezed `.when()` and modal `ScaffoldMessenger.showSnackBar()` | Dart 3 native `switch (state)` and inline canvas error banners | Banned Freezed `.when()` (`freezed_when_ban`) and absolute modal SnackBar ban |

### 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **StudioClient Global Full-Duplex Typing**<br>`client_app_v2/lib/core/api/studio_client.dart` | Banned raw `Map<String, dynamic>` returns and parameter payloads across all 33 Studio methods (specifically and exhaustively: `getPromptBlocks`, `getPromptBlock`, `savePromptBlock`, `simulatePromptBlock`, `clonePromptBlock`, `createPromptBlockDraft`, `getWorkflows`, `getWorkflow`, `saveWorkflow`, `simulateWorkflow`, `cloneWorkflow`, `createWorkflowDraft`, `getSteps`, `getStep`, `saveStep`, `cloneStep`, `createStepDraft`, `getSupportedPlatforms`, `getSystemConfigs`, `getSystemConfig`, `saveSystemConfig`, `cloneSystemConfig`, `createSystemConfigDraft`, `getMcpGateways`, `getMcpGateway`, `saveMcpGateway`, `cloneMcpGateway`, `createMcpGatewayDraft`, `getOutputProfiles`, `getOutputProfile`, `saveOutputProfile`, `cloneOutputProfile`, `createOutputProfileDraft`). | Strongly typed Freezed domain models returned directly: `PromptBlock`, `Workflow`, `NodeStrategy`, `ModelConfig`, `OutputProfile`, `McpGateway`, `PromptBlockSimulationResponse`, `WorkflowSimulationResponse`. | Pruned redundant in-controller map deserialization steps (`rawData.map((e) => Model.fromJson(e))`). Controllers consume typed Freezed models directly. | `_dart_guardrails.py` asserts exactly 0 `DGR001` violations across `studio_client.dart`. Unit tests (`studio_client_test.dart`) verify typed deserialization. |
| **Prompt Block & Workflow Simulation Typing**<br>`client_app_v2/lib/features/studio/models/prompt_block_simulation.dart`<br>`client_app_v2/lib/features/studio/models/workflow_simulation.dart`<br>`client_app_v2/lib/core/api/studio_client.dart` | Banned `Future<Map<String, dynamic>>` in `simulatePromptBlock` and `simulateWorkflow`. Banned loose map subscripts (`data['valid']`, `data['errors']`) and loose dictionary request assembly in builders and modals. | Strongly typed Freezed `PromptBlockSimulationRequest` (matching `backend_v2/models/dtos/studio.py#L388`), `PromptBlockSimulationResponse` (matching `backend_v2/models/dtos/studio.py#L347`), and `WorkflowSimulationResponse` (matching `backend_v2/models/dtos/studio.py#L500`). | Pruned ad-hoc simulation dictionary unpacking; views bind directly to typed properties (`res.valid`, `res.renderedPrompt`, `res.promptContext`). | `_dart_guardrails.py` asserts 0 `DGR001` violations on simulation methods. Unit tests verify simulation responses parse without errors. |
| **Output Profiles 1-Hop Callers & Fixtures**<br>`client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart`<br>`client_app_v2/lib/features/studio/controllers/output_profile_controller.dart`<br>`client_app_v2/test/features/reports/execution_reports_generating_test.dart` | Banned redundant in-caller map deserialization loops (`rawList.map((m) => OutputProfile.fromJson(m))`) and raw map test mocks (`when(...).thenAnswer((_) async => profilesJson)`). | Direct consumption of `List<OutputProfile>` returned by `studioClient.getOutputProfiles()`. Test stubs updated to return typed `List<OutputProfile>` instances. | Pruned intermediate `safeIsolateRun` JSON parsing layer in controller; client delivers instantiated Freezed models. | `execution_reports_generating_test.dart` passes 100% without deserialization crashes. |
| **MCP Gateways Models & Clients**<br>`client_app_v2/lib/features/studio/models/mcp_gateway.dart`<br>`client_app_v2/lib/core/api/studio_client.dart` | Banned raw `Map<String, dynamic>` returns and parameter bags. Banned hallucinating root `name`, `description`, `isActive` fields not present in backend SSOT. | Immutable `@Freezed(equal: false)` model with `@JsonSerializable(disallowUnrecognizedKeys: true)`. Properties matching `SystemConfigMCPGateways`: `id`, `type`, `slug`, `tools: List<AllowedMcpTool>`. | Pruned speculative custom gateway builders. Tools are edited directly via `AllowedMcpTool` sub-models. | `_dart_guardrails.py` asserts 0 `DGR001` violations on `studio_client.dart:getMcpGateways`. Freezed parser crashes fail-fast on unknown keys. |
| **LLM Platforms Models & Clients**<br>`client_app_v2/lib/features/studio/models/llm_platform.dart`<br>`client_app_v2/lib/core/api/studio_client.dart`<br>`client_app_v2/lib/features/studio/controllers/model_registry_controller.dart` | Banned `Future<List<Map<String, dynamic>>>` in `studio_client.dart#L220` and `model_registry_controller.dart#L213`. Banned dictionary indexing (`p['id']`). | Immutable Freezed `LlmPlatform` matching `LLMPlatformDTO`: `id: String`, `label: String`, `@JsonKey(name: 'has_regions') bool hasRegions`. | Pruned redundant view-model layer; `supportedPlatformsProvider` returns `Future<List<LlmPlatform>>` directly. | `model_registry_view_test.dart` asserts platform dropdown renders strictly via `LlmPlatform` models. |
| **Available Workflows Ingestion**<br>`client_app_v2/lib/features/execution/views/new_execution_view.dart` | Banned untyped in-file `availableWorkflows` provider returning raw maps (`data.map((e) => e as Map<String, dynamic>)`) and `Map<String, dynamic>? _selectedWorkflow`. | Strongly typed `Workflow` domain model with `_selectedWorkflow: Workflow?`. Properties read strictly via typed dot-notation (`wf.id`, `wf.name.get(locale)`). | Pruned ad-hoc HTTP call inside view file; delegates parsing to `Workflow.parseListInBackground`. | `dart test client_app_v2/test/` unit test asserting typed workflow selection lifecycle. |
| **Workflow UI Schema Parity**<br>`client_app_v2/lib/features/studio/models/workflow_ui_schema.dart`<br>`client_app_v2/lib/core/api/workflow_client.dart`<br>`client_app_v2/lib/features/execution/views/dynamic_start_screen.dart` | Banned "De-Generator policy" loose map in `workflow_client.dart#L22`. Banned dictionary duck-typing (`details['input_key']`, `details['required']`) in `dynamic_start_screen.dart`. | Strongly typed `WorkflowUiSchema` containing `List<ExpectedInput>`. Consumer reads typed attributes (`input.inputKey`, `input.required`, `input.label.get(locale)`). | Pruned intermediate wrapper classes; `ExpectedInput` from `workflow.dart` reused directly as SSOT. | `_dart_guardrails.py` asserts 0 `DGR001` violations on `workflow_client.dart`. Unit test verifying dynamic form renders without null map lookups. |
| **Human Override Request DTO**<br>`client_app_v2/lib/features/execution/models/human_override_request_dto.dart`<br>`client_app_v2/lib/core/api/execution_client.dart`<br>`client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart` | Banned raw dictionary literal construction in `human_override_dialog.dart#L62-77` and `required Map<String, dynamic> payload` in `execution_client.dart:overrideAtom`. | Strongly typed `HumanOverrideRequestDto` matching `HumanOverrideRequest`: `@JsonKey(name: 'new_status') ExecutionStatus newStatus` (using existing `ExecutionStatus` enum from `enums.dart`, matching backend `LaxExecutionStatus`), `reason: String`, `evidenceQuotes: List<QuoteEvidenceDto>`. `QuoteEvidenceDto` MUST NOT include the backend-excluded `source_alias` field. | Pruned manual map serialization loops; `toJson()` handles DTO serialization automatically. | Unit test verifying payload serialization matches backend `HumanOverrideRequest` schema with `disallowUnrecognizedKeys: true`. |
| **SDUI Matrix Table Performance**<br>`client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart` | Banned nested in-`build` sorting (`breakdown.keys.toList()..sort(...)`, `grouped.keys.toList()..sort(...)`) and multi-pass filtering on render ticks. | Pre-sorted immutable level keys during initialization/getter. Monolithic 635-line layout decomposed into 4 private const-constructible Dumb Painter sub-widgets. | Pruned separate public widget files; 4 sub-widgets remain private to `sdui_matrix_table_widget.dart` for O(1) Dumb Painter encapsulation. | `sdui_matrix_table_widget_test.dart` asserts zero sorting overhead and identical visual layout under 360px viewport stress. |
| **XAI Telemetry & Atom Matrix**<br>`client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart`<br>`client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart` | Banned dynamic mutable list allocation (`final List<Widget> boxes = [];`), hardcoded non-token colors, and non-standard breakpoint `< 600`. | Declarative Column layout with const cards. Macro-breakpoint `< 800px` via `LayoutBuilder`. Material 3 theme tokens (`colorScheme.tertiaryContainer`, `colorScheme.surfaceContainerHighest`). | Pruned dynamic box list; replaces with declarative collection-`if` elements. | Widget test asserting zero runtime list allocations and zero RenderFlex warnings on narrow viewports. |
| **SDUI Blocks Concealment Purge**<br>`client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart` | Banned all 9 instances of `const SizedBox.shrink()` concealing unrendered or empty blocks (`sized_box_shrink_ban`). | Declarative collection-`if` empty guards (`if (block.text.isNotEmpty)`) or explicit typed representation. | Pruned silent swallow paths; invalid blocks bubble to `AppErrorBoundary` natively. | `_dart_guardrails.py` asserts exactly 0 `DGR002` violations in `sdui_blocks_renderer.dart`. |
| **Studio Master Lists Virtualization**<br>`workflows_master_view.dart`<br>`matrices_master_view.dart`<br>`output_profile_list_view.dart`<br>`mcp_gateways_master_view.dart` | Banned `SingleChildScrollView` wrapping `ListView.builder(shrinkWrap: true)`. Banned Freezed `.when()`. Banned raw category string filters (`b.categoryId == 'matrix'`). | Virtualized `ListView.builder` with `prototypeItem`. Centered 1200px max-width containment. Sticky `StudioMasterHeader` with search, count badge, and add action. Dart 3 native `switch (state)`. | Pruned heavy full-page re-renders; instant search filters in-memory collection reactively. | Smooth 60 FPS scrolling verified. Zero Freezed `.when()` violations (`freezed_when_ban`). |
| **Studio Modals & Dialogs Hardening**<br>`human_override_dialog.dart`<br>`scale_editor_modal.dart`<br>`step_simulation_dialog.dart`<br>`profile_editor_view.dart` | Banned un-intercepted dismissals, modal SnackBars (`ScaffoldMessenger.showSnackBar`), uncommitted buffer evaporation, and unconstrained body widths on 4K monitors. | `PopScope(canPop: false)` routing to `_handleDismiss()`. Focus unblur before dirty evaluation. Serialization dirty check (`jsonEncode != initialJson`). Inline error banners. Auto-scroll to first invalid field. Centered 1200px containment. | Pruned repetitive dismiss boilerplate by standardizing on the canonical `scale_editor_modal.dart` reference pattern. | `human_override_dialog_test.dart` testing negative ISTQB partitions: inline error without SnackBar, PopScope discard dialog on dirty state, pristine instant dismiss. |

### Retained SSOT Invariants (What We Will RETAIN)

1. **Dumb Painter SDUI Architecture (`ki_dumb_painter_sdui.md`):**
   Client UI remains strictly a Dumb Painter. All scoring logic, metric calculation, and structural SDUI block assembly remain 100% on the backend.
2. **Backend Pydantic SSOT Contracts (`backend_v2/models/`):**
   `SystemConfigMCPGateways`, `LLMPlatformDTO`, `WorkflowSchemaResponseDTO`, `HumanOverrideRequest`, and `WorkflowResponseDTO` remain unchanged as authoritative writer contracts.
3. **Dual-Axis Localization SSOT (`ki_dual_axis_localization_architecture.md`):**
   Structural chrome strings resolve strictly through `AppLocalizations` (`app_fi.arb`, `app_en.arb`), preserving complete bilingual parity without hardcoded string literals.
4. **Out-of-Scope Technical Debt Registry:**
   `studio_dashboard_view.dart` contains 4 Freezed `.when()` violations (lines 200, 324, 446, 560) and 4 modal `showSnackBar()` calls (lines 194, 318, 441, 555). These are OUT OF SCOPE for this Epic and registered as future technical debt.
5. **Desktop Pro Tool Design Tokens (`ki_desktop_pro_tool_studio_ux.md`):**
   All visual spacing, padding, and layout geometries anchor to `AppSpacing` (`AppSpacing.h8`, `AppSpacing.h16`, `AppSpacing.w16`) and Material 3 `Theme.of(context).colorScheme`.

### Compliance & Modernity Gates

- **Zero Legacy State Support Mandate:** No legacy fallbacks, no `v.get('field', '')` loose access. Missing data crashes immediately.
- **Cross-Domain DTO Parity:** Every backend Pydantic model crossing the network boundary has an identical, strictly typed Dart Freezed counterpart with `disallowUnrecognizedKeys: true`.
- **AST Guardrail Mandate:** Guardrails `DGR001` (Loose Map API/Controller returns), `DGR002` (`SizedBox.shrink()`), and `DGR003` are mathematically enforced across `client_app_v2`.
- **Macro-Breakpoint Standard:** All responsive logic uses `LayoutBuilder` boundaries (< 800px mobile, >= 800px desktop table, >= 1200px centered canvas).
- **Uncommitted State Loss Shield:** Modal dialogs intercept dismissals via `PopScope(canPop: false)`, flush focus blur, and perform serialization dirty checking before discarding user input.

### Producer-Consumer Integration Check

```
[Backend Pydantic V2 SSOT Producer]               [Flutter Freezed Consumer]
-----------------------------------------------------------------------------------------------------------------
SystemConfigMCPGateways                         -> McpGateway & AllowedMcpTool (mcp_gateway.dart)
LLMPlatformDTO                                  -> LlmPlatform (llm_platform.dart)
WorkflowSchemaResponseDTO                       -> WorkflowUiSchema (workflow_ui_schema.dart)
HumanOverrideRequest (Consumer)                 <- HumanOverrideRequestDto (human_override_request_dto.dart Producer)
Workflow / WorkflowResponseDTO                  -> Workflow (workflow.dart)
```

---

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups & Full-Duplex Zero Permissive Typing Foundation

#### Step 1.0: Pre-Implementation Technical Debt Cleanups
- In `@[client_app_v2/lib/core/models/enums.dart]`:
  - Add `static final List<String> matrixCategories = ['matrix'];` to `PromptBlockCategoryGroups` to satisfy `dropdown_database_alignment`.
- In `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`:
  - Eradicate legacy duct-tape map lookups: fix `gateway['allowed_tools']` field name mismatch (`tools` is the backend SSOT field in `SystemConfigMCPGateways`).
  - Purge nonexistent `gateway['is_active']` check and loose map id traversal `gateway['id']?.toString() ?? l10n.unnamedGateway`.
  - Purge `ScaffoldMessenger.of(context).showSnackBar()` creation error handling in favor of inline banner / error logging.
- In `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`:
  - Eradicate loose map indexing `payload['id']`, `payload['slug']` and purge 2 modal `ScaffoldMessenger.showSnackBar()` calls in favor of inline banner feedback.
- In `@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]`:
  - Replace raw string filter `b.categoryId == 'matrix'` with `PromptBlockCategoryGroups.matrixCategories.contains(b.categoryId)`.
  - Purge 3 `ScaffoldMessenger.of(context).showSnackBar()` calls in favor of inline canvas error feedback.
- In `@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]`:
  - Replace hardcoded `workflow.name.translations['fi']` and `['en']` dictionary traversal with localized getter `workflow.name.get(Localizations.localeOf(context).languageCode)`.
  - Replace `const SizedBox(height: 16)` magic number with `AppSpacing.h16`.
  - Replace Freezed `.when()` with Dart 3 native `switch (workflowsState)` pattern matching.
  - Replace `ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed to mint: $e')))` with localized inline error banner.
- In `@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]`:
  - Purge `ScaffoldMessenger.of(context).showSnackBar()` call in favor of inline error handling.
- In `@[client_app_v2/lib/core/api/workflow_client.dart]`:
  - Delete obsolete "De-Generator policy" docstring and loose map return in preparation for strongly typed `WorkflowUiSchema`.
- In `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`:
  - Eradicate redundant raw map mapping in `availableWorkflows` provider (`data.map((e) => e is Map ? e as Map<String, dynamic> : <String, dynamic>{})`).
  - Eradicate loose dictionary indexing (`_selectedWorkflow!['id']`, `_selectedWorkflow!['expected_inputs']`, `_selectedWorkflow!['name']`, `_selectedWorkflow!['output_profiles']`, `_selectedWorkflow!['default_profile_id']`).
- In `@[client_app_v2/lib/core/api/studio_client.dart]`:
  - Eradicate banned `?? []` fallback default in `getWorkflowAvailableExtensions` (line 131): replace `data['available_extensions'] ?? []` with direct typed response parsing.
- In `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`:
  - Replace `ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(l10n.humanOverrideReasonRequired)))` with inline `Form` validation error.
- In `@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]`:
  - Eradicate manual `OutputProfile.fromJson(m)` map deserialization in `_loadProfiles()`, consuming typed `List<OutputProfile>` directly from `studioClient.getOutputProfiles()`.
- In `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]`:
  - Eradicate redundant in-controller `safeIsolateRun(() => rawList.map((e) => OutputProfile.fromJson(e)).toList())`, returning `await client.getOutputProfiles()` directly.
- In `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`:
  - Replace `ScaffoldMessenger.of(context).showSnackBar` DAG simulation feedback with an inline canvas banner, and type `validateMutation` to `WorkflowSimulationResponse`.
- In `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]`:
  - Replace `ScaffoldMessenger.of(context).showSnackBar` prompt simulation error feedback with an inline canvas banner, and type `validateMutation` to `PromptBlockSimulationResponse`.
- In `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]`:
  - Replace arbitrary non-standard breakpoint `constraints.maxWidth < 600` with canonical macro-breakpoint standard `constraints.maxWidth < 800`.
  - Replace magic numbers with `AppSpacing.h8` and `AppSpacing.h16`.
  - Replace raw `Colors.blue[800]` and `Colors.grey[600]` with Material 3 theme tokens (`colorScheme.tertiaryContainer`, `colorScheme.onSurfaceVariant`).
- In `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]`:
  - Eradicate dynamic mutable list allocation (`final List<Widget> boxes = [];`).
  - Replace hardcoded `AppColors.intentWarning.withValues(alpha: 0.1)` with Material 3 theme tokens.

#### Step 1.1: Freezed DTO Model Generation
- Author `[NEW] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` matching backend SSOT `SystemConfigMCPGateways` (`backend_v2/models/domain/system_config.py#L183-194`) and `seed_data.json#L209-235`:
  - `McpGateway`:
    - `@StrictOpaqueIdConverter() required String id`
    - `@Default('mcp_gateways') String type`
    - `String? slug`
    - `@Default([]) List<AllowedMcpTool> tools`
  - `AllowedMcpTool` matching `AllowedMCPTool` (`backend_v2/models/domain/system_config.py#L146-157`):
    - `@JsonKey(name: 'tool_id') required String toolId`
    - `required I18nText name`
    - `required String description`
    - `@Default({}) @JsonKey(name: 'input_schema') Map<String, dynamic> inputSchema`
  - Root `name`, `description`, and `isActive` are INTENTIONALLY NOT INCLUDED as they do not exist on the backend `SystemConfigMCPGateways` domain model.
- Author `[NEW] @[client_app_v2/lib/features/studio/models/llm_platform.dart]` matching backend SSOT `LLMPlatformDTO` (`backend_v2/models/dtos/studio.py#L56-70`):
  - Properties: `required String id`, `required String label`, `@JsonKey(name: 'has_regions') required bool hasRegions`.
- Author `[NEW] @[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]` matching backend SSOT `WorkflowSchemaResponseDTO` (`backend_v2/models/dtos/workflow_schema.py#L13-22`):
  - Properties: `@JsonKey(name: 'expected_inputs') @Default([]) List<ExpectedInput> expectedInputs`.
  - Reuses existing `ExpectedInput` Freezed model from `@[client_app_v2/lib/features/studio/models/workflow.dart]` as permanent SSOT.
- Author `[NEW] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]` matching backend SSOT `HumanOverrideRequest` (`backend_v2/models/dtos/matrix_scorecard.py#L34-53`):
  - Properties: `@JsonKey(name: 'new_status') required ExecutionStatus newStatus` (using existing `ExecutionStatus` enum from `@[client_app_v2/lib/core/models/enums.dart]`, matching backend `LaxExecutionStatus`), `required String reason`, `@JsonKey(name: 'evidence_quotes') @Default([]) List<QuoteEvidenceDto> evidenceQuotes`.
  - Reuses existing `QuoteEvidenceDto` from `@[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart]` as permanent SSOT.
  - `QuoteEvidenceDto` MUST NOT include the `source_alias` field (backend `QuoteEvidenceDTO.source_alias` is `exclude=True`).
- Author `[NEW] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]` matching backend SSOT `PromptBlockSimulationRequest` (`backend_v2/models/dtos/studio.py#L388-405`) and `PromptBlockSimulationResponse` (`backend_v2/models/dtos/studio.py#L347-371`):
  - `PromptBlockSimulationRequest`:
    - `required PromptBlock block`
    - `@Default({}) @JsonKey(name: 'mock_inputs') Map<String, dynamic> mockInputs`
    - `@JsonKey(name: 'target_scale_score') int? targetScaleScore`
    - `@JsonKey(name: 'target_locale') String? targetLocale`
    - `@JsonKey(name: 'context_text') String? contextText`
  - `PromptBlockSimulationResponse`:
    - `bool valid`, `List<String> errors`, `@JsonKey(name: 'rendered_prompt') String renderedPrompt`, `@Default({}) Map<String, dynamic> trace`, `@JsonKey(name: 'prompt_context') PromptContextDto? promptContext`.
  - Reuses existing `PromptContextDto` from `@[client_app_v2/lib/features/studio/models/step_simulation.dart]` as permanent SSOT.
- Author `[NEW] @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]` matching backend SSOT `WorkflowSimulationResponse` (`backend_v2/models/dtos/studio.py#L500-520`):
  - Properties: `bool valid`, `List<String> errors`, `@JsonKey(name: 'step_status') @Default({}) Map<String, String> stepStatus`, `@JsonKey(name: 'execution_order') @Default([]) List<String> executionOrder`, `@Default({}) Map<String, dynamic> trace`.
- Run build_runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build`.

#### Step 1.2: API Clients & Controllers Typing Refactor
- In `@[client_app_v2/lib/core/api/studio_client.dart]`:
  - Matrices / PromptBlocks:
    - Refactor `getPromptBlocks()` to return `Future<List<PromptBlock>>`.
    - Refactor `getPromptBlock(String id)`, `clonePromptBlock(String id)`, and `createPromptBlockDraft()` to return `Future<PromptBlock>`.
    - Refactor `savePromptBlock(String id, PromptBlock data)` to accept `PromptBlock data` and return `Future<PromptBlock>`.
    - Refactor `simulatePromptBlock(PromptBlockSimulationRequest request)` to return `Future<PromptBlockSimulationResponse>`.
  - Workflows:
    - Refactor `getWorkflows()` to return `Future<List<Workflow>>`.
    - Refactor `getWorkflow(String id)`, `cloneWorkflow(String id)`, and `createWorkflowDraft()` to return `Future<Workflow>`.
    - Refactor `saveWorkflow(String id, Workflow data)` to accept `Workflow data` and return `Future<Workflow>`.
    - Refactor `simulateWorkflow(Workflow data)` to return `Future<WorkflowSimulationResponse>`.
  - Steps:
    - Refactor `getSteps()` to return `Future<List<NodeStrategy>>`.
    - Refactor `getStep(String id)`, `cloneStep(String id)`, and `createStepDraft()` to return `Future<NodeStrategy>`.
    - Refactor `saveStep(String id, NodeStrategy data)` to accept `NodeStrategy data` and return `Future<NodeStrategy>`.
  - Model Registries (System Configs):
    - Refactor `getSystemConfigs()` to return `Future<List<ModelConfig>>`.
    - Refactor `getSystemConfig(String id)`, `cloneSystemConfig(String id)`, and `createSystemConfigDraft()` to return `Future<ModelConfig>`.
    - Refactor `saveSystemConfig(String id, ModelConfig data)` to accept `ModelConfig data` and return `Future<ModelConfig>`.
  - Output Profiles:
    - Refactor `getOutputProfiles()` to return `Future<List<OutputProfile>>`.
    - Refactor `getOutputProfile(String id)`, `cloneOutputProfile(String id)`, and `createOutputProfileDraft()` to return `Future<OutputProfile>`.
    - Refactor `saveOutputProfile(String id, OutputProfile data)` to accept `OutputProfile data` and return `Future<OutputProfile>`.
  - MCP Gateways & LLM Platforms:
    - Refactor `getSupportedPlatforms()` to return `Future<List<LlmPlatform>>`.
    - Refactor `getMcpGateways()` to return `Future<List<McpGateway>>`.
    - Refactor `getMcpGateway(id)`, `cloneMcpGateway(id)`, and `createMcpGatewayDraft()` to return `Future<McpGateway>`.
    - Refactor `saveMcpGateway(id, McpGateway data)` to accept `McpGateway data` and return `Future<McpGateway>`.
- In `@[client_app_v2/lib/core/api/workflow_client.dart]`:
  - Refactor `getWorkflowUiSchema(workflowId)` to return `Future<WorkflowUiSchema>`.
- In `@[client_app_v2/lib/core/api/execution_client.dart]`:
  - Refactor `overrideAtom` to accept `required HumanOverrideRequestDto payload`.
- In Controllers (`@[client_app_v2/lib/features/studio/controllers/]`):
  - In `prompt_blocks_controller.dart`: consume `List<PromptBlock>` directly from `client.getPromptBlocks()`, and refactor `simulatePromptBlock` to return `Future<PromptBlockSimulationResponse>`.
  - In `studio_controller.dart`: consume `List<NodeStrategy>` directly from `client.getSteps()`, and refactor `simulateWorkflow` to return `Future<WorkflowSimulationResponse>`.
  - In `output_profile_controller.dart`: consume `List<OutputProfile>` directly from `client.getOutputProfiles()`, returning typed models without intermediate `safeIsolateRun`.
  - In `model_registry_controller.dart`: consume `List<ModelConfig>` directly from `client.getSystemConfigs()`, and update `supportedPlatforms` provider to return `Future<List<LlmPlatform>>`.
  - In `mcp_gateways_controller.dart`: manage `FutureOr<List<McpGateway>>` and form provider as `McpGateway`.
- In Unit Test Suites:
  - Synchronously update mock stubbing across all 10 test files mocking `StudioClient` (`studio_client_test.dart`, `studio_controller_test.dart`, `execution_reports_generating_test.dart`, `output_profile_crud_view_test.dart`, `prompt_block_builder_view_test.dart`, `step_builder_view_dropdown_test.dart`, `studio_dashboard_tab6_test.dart`, `scale_editor_modal_test.dart`, `step_simulation_dialog_test.dart`, `model_registry_view_test.dart`) to return strongly typed Freezed models instead of raw maps.

#### Step 1.3: Views Permissive Typing Elimination
- In `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`:
  - Refactor `availableWorkflows` provider to return `Future<List<Workflow>>`.
  - Type `_selectedWorkflow` state variable to `Workflow?`.
  - Access properties strictly via typed getters (`wf.id`, `wf.name.get(locale)`, `wf.expectedInputs`, `wf.outputProfiles`).
- In `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`:
  - Type `workflowUiSchemaProvider` as `WorkflowUiSchema`.
  - Pass `List<ExpectedInput>` directly to `_buildContent`, reading `input.inputKey`, `input.label.get(locale)`, and `input.required`.
- In `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]` and `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`:
  - Access properties via static dot-notation (`draft.id`, `gateway.id`, `gateway.tools.length`).
- In `@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]`:
  - Consume typed `List<OutputProfile>` directly from `studioClient.getOutputProfiles()` without `OutputProfile.fromJson(m)` map parsing.
- In `@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]`:
  - Type `validateMutation` to `WorkflowSimulationResponse`, binding directly to `data.valid` and `data.errors`.
- In `@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]` and `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]`:
  - Type simulation responses to `PromptBlockSimulationResponse`, binding to `data.valid`, `data.renderedPrompt`, and `data.promptContext`.
- In `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`:
  - Construct `HumanOverrideRequestDto` directly using `_quotes: List<QuoteEvidenceDto>`.
- In `@[client_app_v2/test/features/studio/views/model_registry_view_test.dart]`:
  - Update `mockPlatforms` fixture to `List<LlmPlatform>`.

---

### Phase 2: SDUI Dumb Painter Performance & Cell Decomposition

#### Step 2.1: SduiMatrixTableWidget Cell Decomposition & In-Build Sorting Purge
- In `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]`:
  - Decompose monolithic 635-line layout into 4 private, const-constructible Dumb Painter sub-widgets:
    - `_MatrixSummaryCriteriaCell`: renders criteria description without in-build sorting.
    - `_MatrixSummaryQuotesCell`: renders verbatim quotes and citations.
    - `_MatrixSummaryDistributionCell`: formats level distributions.
    - `_MatrixSummaryScoreCell`: renders score badge and status chips.
  - Pre-sort level keys once during widget initialization or memoized getter, eliminating `breakdown.keys.toList()..sort(...)` and `grouped.keys.toList()..sort(...)` inside the rendering loop.
  - Enclose table cells within `ConstrainedBox(maxWidth: 350)` with `TextOverflow.ellipsis`.

#### Step 2.2: XAIAxisTelemetryGrid & AtomMatrixTableWidget Refactoring
- In `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]`:
  - Eradicate dynamic mutable list allocation (`final List<Widget> boxes = [];`).
  - Replace with declarative Column layout using const-constructible card widgets.
  - Replace hardcoded `AppColors` with Material 3 Theme tokens (`colorScheme.tertiaryContainer`, `colorScheme.surfaceContainerHighest`, `colorScheme.errorContainer`).
- In `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]`:
  - Replace arbitrary breakpoint `constraints.maxWidth < 600` with the canonical macro-breakpoint standard (`constraints.maxWidth < 800`).
  - Replace magic numbers with `AppSpacing.h8` and `AppSpacing.h16`.
  - Replace raw `Colors.amber` and `Colors.blue` with theme tokens (`colorScheme.tertiaryContainer`, `colorScheme.primaryContainer`).

#### Step 2.3: Purge SizedBox.shrink() Concealment (`DGR002`)
- In `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]`:
  - Purge all 9 instances of `const SizedBox.shrink()` intentionally swallowing empty markdown and paragraph blocks.
  - Replace with declarative collection-`if` empty guards (`if (block.text.isNotEmpty)`) or explicit typed representation.
  - Assert zero `DGR002` violations via `scripts/_dart_guardrails.py`.

---

### Phase 3: Desktop Pro Tool Studio Master Views Virtualization & Containment

#### Step 3.1: Standardized Master View Virtualization & Containment
- Standardize layout architecture across all 4 Quorum Studio master list views:
  1. `@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]`
  2. `@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]`
  3. `@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]`
  4. `@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]`
- Purge unvirtualized `SingleChildScrollView` wrapping `ListView.builder(shrinkWrap: true, physics: NeverScrollableScrollPhysics())` in all 4 views.
- Implement pure virtualized `ListView.builder` with `prototypeItem` for buttery 60 FPS scrolling.
- Implement centered 1200px max-width boundary via `Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ...))` to eliminate stretched layouts on 4K displays.
- Implement sticky pinned header (`StudioMasterHeader`) containing view title, subtitle, real-time instant search input with clear trigger, active item count badge (`X / Y kohteesta`), and primary action button (`+ Uusi`).

#### Step 3.2: Banned Freezed .when() Purge & Enum Alignment
- In `workflows_master_view.dart#L65`, replace Freezed `.when()` with Dart 3 native `switch (workflowsState)` pattern matching.
- In `matrices_master_view.dart`, replace raw category string filters (`b.categoryId == 'matrix'`) with `PromptBlockCategoryGroups.matrix` enum grouping in `@[client_app_v2/lib/core/models/enums.dart]`.
- Enclose title `Text` widgets inside horizontal header rows with `Expanded(child: Text(..., overflow: TextOverflow.ellipsis))` to eliminate `RenderFlex` overflow.

---

### Phase 4: Studio Modals, Dialogs UX Hardening & E2E Quality Gates

#### Step 4.1: HumanOverrideDialog Hardening & Test Suite
- In `@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]`:
  - Implement `PopScope(canPop: false, onPopInvokedWithResult: ...)` routing to `_handleDismiss()`.
  - Synchronous `FocusScope.of(context).unfocus()` prior to exit check.
  - Serialization-based dirty check comparing current draft DTO `jsonEncode(_buildRequestDto().toJson()) != _initialRequestJson` (verifying changes across `_selectedStatus`, `_reasonController.text.trim()`, and `_quotes`).
  - Replace modal `ScaffoldMessenger.of(context).showSnackBar()` with inline canvas error banner (`colorScheme.errorContainer`).
  - Enforce modal bounds `ConstrainedBox(constraints: const BoxConstraints(minWidth: 480, maxWidth: 1400, minHeight: 600))`.
  - Replace mutable `bool _isLoading = false` with atomic submission lock `bool _isSaving = false`.
- Author `[NEW] @[client_app_v2/test/features/execution/views/widgets/human_override_dialog_test.dart]` with mandatory negative ISTQB partitions:
  - Empty reason validation error rendered inline without SnackBar.
  - PopScope discard confirmation when text buffer is dirty vs immediate pop when pristine.
  - Atomic button disable during in-flight save.

#### Step 4.2: Studio Modals & Complex Editors Hardening
- In `@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]` and `@[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart]`:
  - Enforce auto-scroll to first invalid `FocusNode` via `Scrollable.ensureVisible`.
  - Enforce modal bounds `ConstrainedBox(minWidth: 480, maxWidth: 1400, minHeight: 600)`.
  - Enforce inline error surfaces (absolute SnackBar ban inside modals).
- In `@[client_app_v2/lib/features/studio/views/profile_editor_view.dart]`:
  - Wrap single-column form body in centered 1200px max-width containment.
  - Verify relational sub-collection card header flexbox triad (`Expanded` title + `AppSpacing.w16` + `Row` actions) and language-neutral indexing (`#${index + 1}`).

#### Step 4.3: Universal Quality Gates & Static Guardrails
- Run build_runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build`.
- Run Dart static guardrails gate on touched feature targets:
  `uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/ client_app_v2/lib/features/studio/views/ client_app_v2/lib/core/api/` asserting zero `DGR001` (across target domains), zero `DGR002` in `sdui_blocks_renderer.dart`, and zero Freezed `.when()` violations.
- Run complete widget and API client test suites:
  - `cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart`
  - `cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart`
  - `cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_blocks_renderer_test.dart`
  - `cd client_app_v2; flutter test test/features/execution/views/widgets/human_override_dialog_test.dart`
  - `cd client_app_v2; flutter test test/features/studio/views/model_registry_view_test.dart`
  - `cd client_app_v2; flutter test test/core/api/studio_client_test.dart`
- Verify bilingual localization parity: `cd client_app_v2; flutter gen-l10n`.

---

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

1. **Zero Permissive Typing (`DGR001`):** Zero raw `Map<String, dynamic>` returns or state stores in API clients, controllers, providers, or views across all 6 target domains (including all 33 methods in `StudioClient` and 10 controller methods).
2. **Zero `SizedBox.shrink()` Concealment (`DGR002`):** Zero occurrences of `SizedBox.shrink()` concealing unrendered blocks across `sdui_blocks_renderer.dart` and touched SDUI renderers.
3. **Pure Dumb Painter SDUI:** Zero in-`build` sorting calls, zero mutable list allocations, and zero RenderFlex overflows under 360px viewport stress.
4. **Desktop Pro Tool Master Lists:** All 4 Studio master browsing lists utilize virtualized `ListView.builder` with sticky search headers, active count badges, and centered 1200px containment.
5. **Desktop Pro Tool Modals:** All dialogs implement `PopScope(canPop: false)` with dirty check shields, auto-scroll to invalid fields, and 100% inline error surfaces (zero modal SnackBars).
6. **100% Bilingual Parity:** All new strings defined in both `app_fi.arb` and `app_en.arb` without key drift.

### Automated Unit Tests

```powershell
# 1. Full Flutter Audit Loop (Build Runner + Analyzer + Tests)
uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/ --build

# 2. Dart Static Guardrails Gate on Target Directories (0 DGR001 in core/api, 0 DGR002 in sdui_blocks_renderer)
uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/ client_app_v2/lib/features/studio/views/ client_app_v2/lib/core/api/

# 3. Targeted Widget & Client Test Suites (Executed inside client_app_v2 package)
cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart
cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart
cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_blocks_renderer_test.dart
cd client_app_v2; flutter test test/features/execution/views/widgets/human_override_dialog_test.dart
cd client_app_v2; flutter test test/features/studio/views/model_registry_view_test.dart
cd client_app_v2; flutter test test/core/api/studio_client_test.dart
cd client_app_v2; flutter test test/features/reports/execution_reports_generating_test.dart
cd client_app_v2; flutter test test/features/studio/views/widgets/scale_editor_modal_test.dart
cd client_app_v2; flutter test test/features/studio/views/prompt_block_builder_view_test.dart

# 4. Localization Generation Verification
cd client_app_v2; flutter gen-l10n
```

### AST Guardrails & Structural Tests

- `_dart_guardrails.py` enforces:
  - `DGR001`: Bans loose Map return types (`Future<Map>`, `Future<List<Map>>`, `FutureOr<List<Map>>`) in `api/`, `controllers/`, and `providers/`.
  - `DGR002`: Bans `SizedBox.shrink()` error or layout concealment in widgets and renderers.
  - `DGR003`: Bans unlocalized raw hardcoded string literals in `Text("...")` widgets.
  - `DGR004`: Bans Dart lint suppressions (`// ignore:`, `// ignore_for_file:`).
- Architectural Rules in `02_flutter_desktop.md`:
  - `freezed_when_ban`: Mandates Dart 3 native `switch (state)` pattern matching destructuring; strictly bans Freezed `.when()`, `.map()`, and manual `if-else` chains.

### Manual Verification Steps

1. **60 FPS Virtualized Scrolling:** Open Quorum Studio Master Views (`/studio/workflows`, `/studio/matrices`, `/studio/profiles`, `/studio/gateways`), verify smooth scrolling with pinned sticky header, instant search filtering, and active count badge calculation.
2. **Ultrawide Monitor Inspection:** Resize desktop window to > 1920px; verify that master list views and editor forms remain bounded to 1200px centered without stretching across the entire monitor.
3. **Narrow Desktop & Multi-Locale Stress Test:** Resize viewport to 360px and switch locale to Finnish (`fi`). Verify that all tables, dialogs, and cards remain 100% free of RenderFlex hazard stripes.
4. **Modal Dirty State Shield:** Open `HumanOverrideDialog` or `ScaleEditorModal`, type in a text buffer, press `Esc` or click close button; verify that discard confirmation appears. Click "Jatka muokkausta"; verify that buffer is retained.
5. **Full-Duplex Typed Lifecycle:** Navigate to `/studio/gateways`, click `+ Uusi`, verify gateway draft mints via typed Freezed model `draft.id` without runtime map parsing errors. Open Model Registry view; verify platforms dropdown populates strictly via `LlmPlatform` models.
6. **Workflow Selection in Execution:** Navigate to `/execution/new`, verify workflow sidebar populates strictly through `Workflow` domain models, selecting a workflow binds properties cleanly, and navigating to dynamic start screen passes `WorkflowUiSchema` with `List<ExpectedInput>` without dictionary subscripting.

### MANDATORY Final E2E REST API Verification Gate

```powershell
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 5. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
