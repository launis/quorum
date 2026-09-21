# Phase 1: Pre-Implementation Technical Debt Cleanups & Full-Duplex Zero Permissive Typing Foundation

**Overview:** Eradicate permissive typing debt (`DGR001`), layout concealment (`DGR002`), render-tree thrashing, and unvirtualized list anti-patterns across Quorum's Flutter desktop client (`client_app_v2`). Establish 1:1 Full-Duplex DTO parity with backend Pydantic V2 SSOT contracts across 6 distinct feature domains by generating 6 new immutable Freezed models, strongly typing all 33 endpoints in `StudioClient`, refactoring `WorkflowClient` and `ExecutionClient`, modernizing controllers and views, and updating test mock fixtures.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L177-L321] Phase 1: Pre-Implementation Technical Debt Cleanups & Full-Duplex Zero Permissive Typing Foundation
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/core/models/enums.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L272-302]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/workflows_master_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/workflow_client.dart#L42-140]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37]
- `[MODIFY]` @[client_app_v2/lib/core/api/studio_client.dart#L272-302]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]
- `[MODIFY]` @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/models/llm_platform.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]
- `[NEW]` @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]
- `[NEW]` @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/execution_client.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/studio_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart#L42-140]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]
- `[MODIFY]` @[client_app_v2/test/core/api/studio_client_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/controllers/studio_controller_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/reports/execution_reports_generating_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/studio_dashboard_tab6_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/widgets/step_simulation_dialog_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/studio/views/model_registry_view_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the codebase baseline state and verify existing DGR001 loose map warnings in @[client_app_v2/lib/core/api/studio_client.dart#L272-302] and controllers.</action>
    <action>Look forward: Verify that subsequent phases (Phase 2 through 4) rely on the new Freezed DTO models and strongly typed API methods to eliminate render-tree jank and modal uncommitted state loss.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/01_phase1_plan.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Zero DGR001 violations in @[client_app_v2/lib/core/api/studio_client.dart] across all 33 CRUD, draft, clone, and simulation endpoints.</item>
    <item>Strongly typed Freezed domain models authored and generated with disallowUnrecognizedKeys: true: McpGateway, AllowedMcpTool, LlmPlatform, WorkflowUiSchema, HumanOverrideRequestDto, PromptBlockSimulationRequest, PromptBlockSimulationResponse, WorkflowSimulationResponse.</item>
    <item>[NEW] WorkflowUiSchema matching @[backend_v2/models/dtos/workflow_schema.py#L13-22] is consumed strongly typed by @[client_app_v2/lib/core/api/workflow_client.dart#L42-140] and @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart#L42-140].</item>
    <item>[NEW] HumanOverrideRequestDto matching @[backend_v2/models/dtos/matrix_scorecard.py#L34-53] is constructed with typed QuoteEvidenceDto instances and passed to @[client_app_v2/lib/core/api/execution_client.dart].</item>
    <item>Available workflows ingestion in @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37] binds typed Workflow models directly, eliminating loose map dictionary lookups.</item>
    <item>All 10 mock test suites updated to stub and return typed Freezed models instead of raw maps.</item>
    <item>Automated quality gate passes: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build with 0 errors.</item>
  </dod_checklist>

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

  <anti_targets>
    <forbidden>Do NOT modify monolithic layout or sorting in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] during Phase 1 (reserved for Phase 2).</forbidden>
    <forbidden>Do NOT modify Master View virtualization or StudioMasterHeader in @[client_app_v2/lib/features/studio/views/workflows_master_view.dart], @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart], @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart] beyond Phase 1 tech debt cleanups (reserved for Phase 3).</forbidden>
    <forbidden>Do NOT modify PopScope discard interception in @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart], @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart], @[client_app_v2/lib/features/studio/views/widgets/step_simulation_dialog.dart] during Phase 1 (reserved for Phase 4).</forbidden>
    <forbidden>Do NOT touch studio_dashboard_view.dart (out of scope, registered as future technical debt).</forbidden>
    <forbidden>Do NOT modify backend Python DTO models or persistence schemas in backend_v2/ (pure read-only SSOT producers).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/core/models/enums.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/workflow_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/new_execution_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/studio_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/models/llm_platform.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/execution_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/studio_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]</frontend>
  </touched_artifacts>

  <!-- Pre-Implementation Technical Debt Cleanups (Scoped Boy Scout Rule) -->
  <pre_implementation_cleanups>
    <cleanup id="C1" target="@[client_app_v2/lib/core/models/enums.dart]">
      <description>Add static final List&lt;String&gt; matrixCategories = ['matrix']; to PromptBlockCategoryGroups to satisfy dropdown_database_alignment.</description>
      <remedy>Define matrixCategories in PromptBlockCategoryGroups.</remedy>
    </cleanup>
    <cleanup id="C2" target="@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L272-302]">
      <description>Eradicate legacy duct-tape map lookups: gateway['allowed_tools'] field mismatch (tools is backend SSOT in SystemConfigMCPGateways), nonexistent gateway['is_active'], loose map id traversal gateway['id']?.toString() ?? l10n.unnamedGateway, and ScaffoldMessenger.showSnackBar.</description>
      <remedy>Replace loose map keys with typed properties and inline error banners.</remedy>
    </cleanup>
    <cleanup id="C3" target="@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]">
      <description>Eradicate loose map indexing payload['id'], payload['slug'] and purge 2 modal ScaffoldMessenger.showSnackBar() calls in favor of inline banner feedback.</description>
      <remedy>Bind typed McpGateway properties and inline error indicators.</remedy>
    </cleanup>
    <cleanup id="C4" target="@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]">
      <description>Replace raw string filter b.categoryId == 'matrix' with PromptBlockCategoryGroups.matrixCategories.contains(b.categoryId) and purge 3 modal showSnackBar calls.</description>
      <remedy>Use PromptBlockCategoryGroups and inline error state.</remedy>
    </cleanup>
    <cleanup id="C5" target="@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]">
      <description>Replace hardcoded workflow.name.translations['fi'] with workflow.name.get(Localizations.localeOf(context).languageCode), replace SizedBox(height: 16) with AppSpacing.h16, replace Freezed .when() with native switch (workflowsState), and replace modal SnackBar with localized banner.</description>
      <remedy>Apply localized getters, AppSpacing, native switch matching, and inline banner.</remedy>
    </cleanup>
    <cleanup id="C6" target="@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]">
      <description>Purge ScaffoldMessenger.of(context).showSnackBar() call in favor of inline error handling.</description>
      <remedy>Replace modal alert with canvas error banner.</remedy>
    </cleanup>
    <cleanup id="C7" target="@[client_app_v2/lib/core/api/workflow_client.dart#L42-140]">
      <description>Delete obsolete 'De-Generator policy' docstring and loose map return in preparation for strongly typed WorkflowUiSchema.</description>
      <remedy>Remove obsolete comment and update return type.</remedy>
    </cleanup>
    <cleanup id="C8" target="@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37]">
      <description>Eradicate redundant raw map mapping in availableWorkflows provider and loose dictionary indexing (_selectedWorkflow!['id'], expected_inputs, name, output_profiles, default_profile_id).</description>
      <remedy>Type availableWorkflows provider to Future&lt;List&lt;Workflow&gt;&gt; and type _selectedWorkflow to Workflow?.</remedy>
    </cleanup>
    <cleanup id="C9" target="@[client_app_v2/lib/core/api/studio_client.dart#L272-302]">
      <description>Eradicate banned ?? [] fallback default in getWorkflowAvailableExtensions (line 131): replace data['available_extensions'] ?? [] with direct typed response parsing.</description>
      <remedy>Parse typed List directly from response.</remedy>
    </cleanup>
    <cleanup id="C10" target="@[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]">
      <description>Replace ScaffoldMessenger.showSnackBar(SnackBar(content: Text(l10n.humanOverrideReasonRequired))) with inline Form validation error.</description>
      <remedy>Validate reason via FormField validator.</remedy>
    </cleanup>
    <cleanup id="C11" target="@[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]">
      <description>Eradicate manual OutputProfile.fromJson(m) map deserialization in _loadProfiles(), consuming typed List&lt;OutputProfile&gt; directly from studioClient.getOutputProfiles().</description>
      <remedy>Directly assign returned List&lt;OutputProfile&gt;.</remedy>
    </cleanup>
    <cleanup id="C12" target="@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]">
      <description>Eradicate redundant in-controller safeIsolateRun(() =&gt; rawList.map((e) =&gt; OutputProfile.fromJson(e)).toList()), returning await client.getOutputProfiles() directly.</description>
      <remedy>Delegate directly to client.getOutputProfiles().</remedy>
    </cleanup>
    <cleanup id="C13" target="@[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]">
      <description>Replace ScaffoldMessenger.of(context).showSnackBar DAG simulation feedback with an inline canvas banner, and type validateMutation to WorkflowSimulationResponse.</description>
      <remedy>Type mutation and render inline status banner.</remedy>
    </cleanup>
    <cleanup id="C14" target="@[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart]">
      <description>Replace ScaffoldMessenger.of(context).showSnackBar prompt simulation error feedback with an inline canvas banner, and type validateMutation to PromptBlockSimulationResponse.</description>
      <remedy>Type mutation and render inline status banner.</remedy>
    </cleanup>
    <cleanup id="C15" target="@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]">
      <description>Replace non-standard breakpoint constraints.maxWidth &lt; 600 with canonical macro-breakpoint standard constraints.maxWidth &lt; 800, replace magic numbers with AppSpacing.h8/h16, and replace raw Colors.blue[800]/grey[600] with Material 3 tokens.</description>
      <remedy>Apply LayoutBuilder macro-breakpoint and theme token swatches.</remedy>
    </cleanup>
    <cleanup id="C16" target="@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]">
      <description>Eradicate dynamic mutable list allocation (final List&lt;Widget&gt; boxes = [];) and replace hardcoded AppColors.intentWarning.withValues(alpha: 0.1) with Material 3 theme tokens.</description>
      <remedy>Replace mutable list with declarative Column and theme tokens.</remedy>
    </cleanup>
    <cleanup id="C17" target="@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]">
      <description>Update mcpGateways parameter type from List&lt;Map&lt;String, dynamic&gt;&gt; to List&lt;McpGateway&gt; to maintain 100% typed propagation from WorkflowStepsTab down to individual step cards.</description>
      <remedy>Type mcpGateways parameter as List&lt;McpGateway&gt;.</remedy>
    </cleanup>
  </pre_implementation_cleanups>

  <!-- 5-Column Architectural Directives Table -->
  <directives_table>
| 1. Target Scope &amp; Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification &amp; Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`client_app_v2/lib/core/api/studio_client.dart`** | Untyped `Future<Map<String, dynamic>>` and `Future<List<Map<String, dynamic>>>` loose dictionary returns; `data['available_extensions'] ?? []` fallback defaults | 100% strongly typed method signatures returning Freezed DTOs: `Future<List<PromptBlock>>`, `Future<List<Workflow>>`, `Future<List<McpGateway>>`, `Future<List<LlmPlatform>>`, `Future<WorkflowSimulationResponse>` | Speculative generic API response wrappers or reflection-based deserializers; direct typed DTO parsing | Zero `DGR001` violations via `uv run python scripts/_dart_guardrails.py`; `flutter test test/core/api/studio_client_test.dart` |
| **`client_app_v2/lib/core/api/workflow_client.dart`** | Obsolete 'De-Generator policy' comment and returning raw `Map<String, dynamic>` on `getWorkflowUiSchema` | Strongly typed `Future<WorkflowUiSchema> getWorkflowUiSchema(String workflowId)` | Intermediate UI schema adapter classes; reuse existing `ExpectedInput` Freezed model | `DGR001` static guardrail check; `test_workflow_ui_schema_deserialization_success` test |
| **`client_app_v2/lib/core/api/execution_client.dart`** | Loose `Map<String, dynamic> payload` accepted in `overrideAtom()` | Strictly typed `Future<GenericStatusResponseDto> overrideAtom({required String executionId, required String atomId, required HumanOverrideRequestDto payload})` | Parallel quote evidence models; reuse existing `QuoteEvidenceDto` from `matrix_scorecard_dto.dart` | `DGR001` static check; `test_human_override_request_dto_serialization` unit test |
| **`client_app_v2/lib/features/studio/models/mcp_gateway.dart`** | Loose map traversal (`gateway['allowed_tools']`, `gateway['id']?.toString() ?? 'Unnamed'`) and hallucinated `is_active` / root `description` fields | Immutable Freezed DTOs `McpGateway` and `AllowedMcpTool` with `@JsonSerializable(disallowUnrecognizedKeys: true)` matching `SystemConfigMCPGateways` SSOT | Inventing frontend-only properties (`isActive`, root `description`) not present in backend domain model | `test_mcp_gateway_hallucinated_fields_fail_fast` (FormatException on unrecognized keys) |
| **`client_app_v2/lib/features/studio/models/workflow_ui_schema.dart`** | Loose `expected_inputs` dictionary mapping in `DynamicStartScreen` | Immutable Freezed DTO `WorkflowUiSchema` with `expectedInputs: List<ExpectedInput>` and `disallowUnrecognizedKeys: true` | Redefining `ExpectedInput` schema; 100% reuse of `client_app_v2/lib/features/studio/models/workflow.dart` SSOT | `test_workflow_ui_schema_deserialization_success` test; build_runner compilation |
| **`client_app_v2/lib/features/execution/models/human_override_request_dto.dart`** | Untyped dictionary construction `{'new_status': ..., 'reason': ..., 'evidence_quotes': ...}` in `HumanOverrideDialog` | Immutable Freezed DTO `HumanOverrideRequestDto` with typed `ExecutionStatus`, `reason`, and `List<QuoteEvidenceDto>` | Duplicating `QuoteEvidenceDto` or adding backend-excluded `source_alias` | `test_human_override_request_dto_serialization` assert matching `new_status` |
| **`client_app_v2/lib/features/studio/models/prompt_block_simulation.dart`** | Untyped `simulatePromptBlock` input and response dictionaries | Immutable Freezed DTOs `PromptBlockSimulationRequest` and `PromptBlockSimulationResponse` matching backend `studio.py` | Creating separate PromptContext DTO; reuse `PromptContextDto` from `step_simulation.dart` | `test_studio_client_simulate_prompt_block_empty_request_fails_fast` |
| **`client_app_v2/lib/features/studio/models/workflow_simulation.dart`** | Untyped `simulateWorkflow` response map parsed in `WorkflowBuilderView` | Immutable Freezed DTO `WorkflowSimulationResponse` matching backend `studio.py` with `valid: bool`, `errors: List<String>`, `stepStatus: Map<String, String>` | Complex UI-only DAG validation wrappers; direct consumption of backend simulation result | Unit test asserting typed field resolution and `WorkflowBuilderView` compilation |
| **`client_app_v2/lib/features/execution/views/new_execution_view.dart`** | Redundant raw map conversion `e is Map ? e as Map<String, dynamic> : <String, dynamic>{}` and loose dictionary lookups `_selectedWorkflow!['id']` | Strongly typed Riverpod provider `Future<List<Workflow>> availableWorkflows` and typed selection state `Workflow? _selectedWorkflow` | Converting typed workflows back to maps for dropdown display; bind typed properties directly | `test_available_workflows_provider_typed_resolution`; `flutter test test/features/reports/execution_reports_generating_test.dart` |
  </directives_table>

  <contract_freeze>
    <!-- [NEW] -->
    <class name="McpGateway" path="@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]"><!-- [NEW] --></class>
    <class name="AllowedMcpTool" path="@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]"><!-- [NEW] --></class>
    <class name="LlmPlatform" path="@[client_app_v2/lib/features/studio/models/llm_platform.dart]"><!-- [NEW] --></class>
    <class name="WorkflowUiSchema" path="@[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart]"><!-- [NEW] --></class>
    <class name="HumanOverrideRequestDto" path="@[client_app_v2/lib/features/execution/models/human_override_request_dto.dart]"><!-- [NEW] --></class>
    <class name="PromptBlockSimulationRequest" path="@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]"><!-- [NEW] --></class>
    <class name="PromptBlockSimulationResponse" path="@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]"><!-- [NEW] --></class>
    <class name="WorkflowSimulationResponse" path="@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]"><!-- [NEW] --></class>
  </contract_freeze>

  <step id="1.0" name="Pre-Implementation Technical Debt Cleanups Execution">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add static final List&lt;String&gt; matrixCategories = ['matrix']; to PromptBlockCategoryGroups.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L272-302], eradicate legacy duct-tape map lookups: gateway['allowed_tools'] field name mismatch, nonexistent gateway['is_active'], loose map id traversal, and ScaffoldMessenger.showSnackBar creation error handling in favor of inline banner / error logging.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart], eradicate loose map indexing payload['id'], payload['slug'] and purge 2 modal ScaffoldMessenger.showSnackBar() calls.</action>
    <action>In @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], replace raw string filter b.categoryId == 'matrix' with PromptBlockCategoryGroups.matrixCategories.contains(b.categoryId), and purge 3 ScaffoldMessenger showSnackBar calls.</action>
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart], replace hardcoded workflow.name.translations['fi'] with workflow.name.get(Localizations.localeOf(context).languageCode), replace SizedBox(height: 16) with AppSpacing.h16, replace Freezed .when() with Dart 3 native switch (workflowsState), and replace modal SnackBar with localized inline banner.</action>
    <action>In @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart], purge ScaffoldMessenger.showSnackBar() call in favor of inline error handling.</action>
    <action>In @[client_app_v2/lib/core/api/workflow_client.dart#L42-140], delete obsolete 'De-Generator policy' docstring and loose map return in preparation for strongly typed WorkflowUiSchema.</action>
    <action>In @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37], eradicate redundant raw map mapping in availableWorkflows provider and loose dictionary indexing (_selectedWorkflow!['id'], expected_inputs, name, output_profiles, default_profile_id).</action>
    <action>In @[client_app_v2/lib/core/api/studio_client.dart#L272-302], eradicate banned ?? [] fallback default in getWorkflowAvailableExtensions (line 131): replace data['available_extensions'] ?? [] with direct typed response parsing.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77], replace ScaffoldMessenger showSnackBar with inline Form validation error.</action>
    <action>In @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart], eradicate manual OutputProfile.fromJson(m) map deserialization in _loadProfiles(), consuming typed List&lt;OutputProfile&gt; directly.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart], eradicate redundant in-controller safeIsolateRun(() =&gt; rawList.map((e) =&gt; OutputProfile.fromJson(e)).toList()), returning await client.getOutputProfiles() directly.</action>
    <action>In @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart], replace ScaffoldMessenger showSnackBar DAG simulation feedback with an inline canvas banner, and type validateMutation to WorkflowSimulationResponse.</action>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart], replace ScaffoldMessenger showSnackBar prompt simulation feedback with an inline canvas banner, and type validateMutation to PromptBlockSimulationResponse.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart], replace non-standard breakpoint constraints.maxWidth &lt; 600 with constraints.maxWidth &lt; 800, replace magic numbers with AppSpacing.h8/h16, and replace raw Colors.blue[800]/grey[600] with Material 3 tokens.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart], eradicate dynamic mutable list allocation (final List&lt;Widget&gt; boxes = [];) and replace hardcoded AppColors.intentWarning with Material 3 theme tokens.</action>
    <demolish>REMOVE: `gateway['allowed_tools']`, `gateway['is_active']`, `gateway['id']?.toString() ?? l10n.unnamedGateway` in @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L272-302]. REPLACE WITH: typed McpGateway property traversal.</demolish>
    <demolish>REMOVE: `data.map((e) =&gt; e is Map ? e as Map&lt;String, dynamic&gt; : &lt;String, dynamic&gt;{})` and `_selectedWorkflow!['id']` in @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37]. REPLACE WITH: typed Future&lt;List&lt;Workflow&gt;&gt; provider and Workflow? selection state.</demolish>
    <demolish>REMOVE: `data['available_extensions'] ?? []` in @[client_app_v2/lib/core/api/studio_client.dart#L272-302]. REPLACE WITH: direct typed list parsing.</demolish>
  </step>

  <step id="1.1" name="Freezed DTO Model Generation">
    <action>Author [NEW] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart] matching backend SSOT SystemConfigMCPGateways (@[backend_v2/models/domain/system_config.py#L183-194]) and @[backend_v2/seed/seed_data.json#L209-235]: McpGateway (StrictOpaqueIdConverter id, type, slug, tools: List&lt;AllowedMcpTool&gt;) and AllowedMcpTool (@[backend_v2/models/domain/system_config.py#L146-157]: toolId, name: I18nText, description: String, inputSchema: Map&lt;String, dynamic&gt;). Root name, description, and isActive are INTENTIONALLY NOT INCLUDED as they do not exist on the backend domain model.</action>
    <action>Author [NEW] @[client_app_v2/lib/features/studio/models/llm_platform.dart] matching backend SSOT LLMPlatformDTO (@[backend_v2/models/dtos/studio.py#L56-70]): id: String, label: String, hasRegions: bool.</action>
    <action>Author [NEW] @[client_app_v2/lib/features/studio/models/workflow_ui_schema.dart] matching backend SSOT WorkflowSchemaResponseDTO (@[backend_v2/models/dtos/workflow_schema.py#L13-22]): expectedInputs: List&lt;ExpectedInput&gt;, reusing ExpectedInput from @[client_app_v2/lib/features/studio/models/workflow.dart] as permanent SSOT.</action>
    <action>Author [NEW] @[client_app_v2/lib/features/execution/models/human_override_request_dto.dart] matching backend SSOT HumanOverrideRequest (@[backend_v2/models/dtos/matrix_scorecard.py#L34-53]): newStatus: ExecutionStatus (using existing ExecutionStatus from @[client_app_v2/lib/core/models/enums.dart]), reason: String, evidenceQuotes: List&lt;QuoteEvidenceDto&gt; (reusing QuoteEvidenceDto from @[client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart] without source_alias).</action>
    <action>Author [NEW] @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart] matching backend SSOT PromptBlockSimulationRequest (@[backend_v2/models/dtos/studio.py#L388-405]) and PromptBlockSimulationResponse (@[backend_v2/models/dtos/studio.py#L347-371]): PromptBlockSimulationRequest (block: PromptBlock, mockInputs: Map&lt;String, dynamic&gt;, targetScaleScore: int?, targetLocale: String?, contextText: String?) and PromptBlockSimulationResponse (valid: bool, errors: List&lt;String&gt;, renderedPrompt: String, trace: Map&lt;String, dynamic&gt;, promptContext: PromptContextDto?, reusing PromptContextDto from @[client_app_v2/lib/features/studio/models/step_simulation.dart]).</action>
    <action>Author [NEW] @[client_app_v2/lib/features/studio/models/workflow_simulation.dart] matching backend SSOT WorkflowSimulationResponse (@[backend_v2/models/dtos/studio.py#L500-520]): valid: bool, errors: List&lt;String&gt;, stepStatus: Map&lt;String, String&gt;, executionOrder: List&lt;String&gt;, trace: Map&lt;String, dynamic&gt;.</action>
    <action>Run build_runner: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/ --build to compile generated part files before updating consumers.</action>
  </step>

  <step id="1.2" name="API Clients &amp; Controllers Typing Refactor">
    <action>In @[client_app_v2/lib/core/api/studio_client.dart#L272-302]:</action>
    <action>- Matrices/PromptBlocks: refactor getPromptBlocks() to Future&lt;List&lt;PromptBlock&gt;&gt;; getPromptBlock(id), clonePromptBlock(id), createPromptBlockDraft() to Future&lt;PromptBlock&gt;; savePromptBlock(id, PromptBlock data) to Future&lt;PromptBlock&gt;; simulatePromptBlock(PromptBlockSimulationRequest request) to Future&lt;PromptBlockSimulationResponse&gt;.</action>
    <action>- Workflows: refactor getWorkflows() to Future&lt;List&lt;Workflow&gt;&gt;; getWorkflow(id), cloneWorkflow(id), createWorkflowDraft() to Future&lt;Workflow&gt;; saveWorkflow(id, Workflow data) to Future&lt;Workflow&gt;; simulateWorkflow(Workflow data) to Future&lt;WorkflowSimulationResponse&gt;.</action>
    <action>- Steps: refactor getSteps() to Future&lt;List&lt;NodeStrategy&gt;&gt;; getStep(id), cloneStep(id), createStepDraft() to Future&lt;NodeStrategy&gt;; saveStep(id, NodeStrategy data) to Future&lt;NodeStrategy&gt;.</action>
    <action>- Model Registries: refactor getSystemConfigs() to Future&lt;List&lt;ModelConfig&gt;&gt;; getSystemConfig(id), cloneSystemConfig(id), createSystemConfigDraft() to Future&lt;ModelConfig&gt;; saveSystemConfig(id, ModelConfig data) to Future&lt;ModelConfig&gt;.</action>
    <action>- Output Profiles: refactor getOutputProfiles() to Future&lt;List&lt;OutputProfile&gt;&gt;; getOutputProfile(id), cloneOutputProfile(id), createOutputProfileDraft() to Future&lt;OutputProfile&gt;; saveOutputProfile(id, OutputProfile data) to Future&lt;OutputProfile&gt;.</action>
    <action>- MCP Gateways &amp; Platforms: refactor getSupportedPlatforms() to Future&lt;List&lt;LlmPlatform&gt;&gt;; getMcpGateways() to Future&lt;List&lt;McpGateway&gt;&gt;; getMcpGateway(id), cloneMcpGateway(id), createMcpGatewayDraft() to Future&lt;McpGateway&gt;; saveMcpGateway(id, McpGateway data) to Future&lt;McpGateway&gt;.</action>
    <action>In @[client_app_v2/lib/core/api/workflow_client.dart#L42-140], refactor getWorkflowUiSchema(workflowId) to return Future&lt;WorkflowUiSchema&gt;.</action>
    <action>In @[client_app_v2/lib/core/api/execution_client.dart], refactor overrideAtom to accept required HumanOverrideRequestDto payload.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart], consume List&lt;PromptBlock&gt; directly from client.getPromptBlocks(), and refactor simulatePromptBlock to return Future&lt;PromptBlockSimulationResponse&gt;.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/studio_controller.dart], consume List&lt;NodeStrategy&gt; directly from client.getSteps(), and refactor simulateWorkflow to return Future&lt;WorkflowSimulationResponse&gt;.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart], consume List&lt;OutputProfile&gt; directly from client.getOutputProfiles(), returning typed models without intermediate safeIsolateRun.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/model_registry_controller.dart], consume List&lt;ModelConfig&gt; directly from client.getSystemConfigs(), and update supportedPlatforms provider to return Future&lt;List&lt;LlmPlatform&gt;&gt;.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart], manage FutureOr&lt;List&lt;McpGateway&gt;&gt; and form provider as McpGateway.</action>
    <action>In all 10 mock test suites (@[client_app_v2/test/core/api/studio_client_test.dart], @[client_app_v2/test/features/studio/controllers/studio_controller_test.dart], @[client_app_v2/test/features/reports/execution_reports_generating_test.dart], @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart], @[client_app_v2/test/features/studio/views/prompt_block_builder_view_test.dart], @[client_app_v2/test/features/studio/views/step_builder_view_dropdown_test.dart], @[client_app_v2/test/features/studio/views/studio_dashboard_tab6_test.dart], @[client_app_v2/test/features/studio/views/widgets/scale_editor_modal_test.dart], @[client_app_v2/test/features/studio/widgets/step_simulation_dialog_test.dart], @[client_app_v2/test/features/studio/views/model_registry_view_test.dart]), update mock stubbing to return strongly typed Freezed instances instead of raw maps.</action>
  </step>

  <step id="1.3" name="Views Permissive Typing Elimination">
    <action>In @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L26-37]: refactor availableWorkflows provider to return Future&lt;List&lt;Workflow&gt;&gt;; type _selectedWorkflow state variable to Workflow?; access properties strictly via typed getters (wf.id, wf.name.get(locale), wf.expectedInputs, wf.outputProfiles).</action>
    <action>In @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart#L42-140]: type workflowUiSchemaProvider as WorkflowUiSchema; pass List&lt;ExpectedInput&gt; directly to _buildContent, reading input.inputKey, input.label.get(locale), and input.required.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L272-302] and @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]: access properties via static dot-notation (draft.id, gateway.id, gateway.tools.length).</action>
    <action>In @[client_app_v2/lib/features/reports/views/dialogs/create_report_dialog.dart]: consume typed List&lt;OutputProfile&gt; directly from studioClient.getOutputProfiles() without OutputProfile.fromJson(m) map parsing.</action>
    <action>In @[client_app_v2/lib/features/studio/views/workflow_builder_view.dart]: type validateMutation to WorkflowSimulationResponse, binding directly to data.valid and data.errors.</action>
    <action>In @[client_app_v2/lib/features/studio/views/prompt_block_builder_view.dart] and @[client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart]: type simulation responses to PromptBlockSimulationResponse, binding to data.valid, data.renderedPrompt, and data.promptContext.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/human_override_dialog.dart#L62-77]: construct HumanOverrideRequestDto directly using _quotes: List&lt;QuoteEvidenceDto&gt;.</action>
    <action>In @[client_app_v2/test/features/studio/views/model_registry_view_test.dart]: update mockPlatforms fixture to List&lt;LlmPlatform&gt;.</action>
  </step>

  <test_contracts>
    <test name="test_studio_client_get_prompt_blocks_returns_typed_list" category="positive">
      <input>HTTP 200 with raw JSON list of prompt blocks</input>
      <expected>Returns List&lt;PromptBlock&gt; with verified block IDs</expected>
    </test>
    <test name="test_studio_client_get_prompt_blocks_unknown_keys_fails_fast" category="negative">
      <input>HTTP 200 with JSON containing unknown key 'legacy_field'</input>
      <expected>Throws FormatException due to disallowUnrecognizedKeys: true</expected>
    </test>
    <test name="test_studio_client_simulate_prompt_block_empty_request_fails_fast" category="boundary">
      <input>PromptBlockSimulationRequest with empty block ID</input>
      <expected>Throws validation AppException before network dispatch</expected>
    </test>
    <test name="test_mcp_gateway_json_deserialization_success" category="positive">
      <input>Valid JSON matching SystemConfigMCPGateways SSOT</input>
      <expected>Instantiates McpGateway with correct tools list</expected>
    </test>
    <test name="test_mcp_gateway_hallucinated_fields_fail_fast" category="negative">
      <input>JSON containing hallucinated 'allowed_tools' or 'is_active'</input>
      <expected>Throws FormatException due to strict schema lockdown</expected>
    </test>
    <test name="test_workflow_ui_schema_deserialization_success" category="positive">
      <input>Valid JSON matching WorkflowSchemaResponseDTO</input>
      <expected>Instantiates WorkflowUiSchema with List&lt;ExpectedInput&gt;</expected>
    </test>
    <test name="test_human_override_request_dto_serialization" category="positive">
      <input>HumanOverrideRequestDto(newStatus: ExecutionStatus.passed, reason: 'Verified', evidenceQuotes: [])</input>
      <expected>Serializes to JSON with new_status='passed' matching backend schema</expected>
    </test>
    <test name="test_human_override_request_dto_empty_reason_fails_validation" category="boundary">
      <input>HumanOverrideRequestDto with empty reason string</input>
      <expected>Triggers validation error in UI form without SnackBar</expected>
    </test>
    <test name="test_available_workflows_provider_typed_resolution" category="positive">
      <input>API returns list of workflow payloads</input>
      <expected>availableWorkflows provider resolves Future&lt;List&lt;Workflow&gt;&gt;</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Deterministic build runner and static analysis check -->
    <action>Run build_runner: uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/ --build</action>
    <!-- Dart guardrails: Assert 0 DGR001 violations in studio_client.dart -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/core/api/studio_client.dart client_app_v2/lib/core/api/workflow_client.dart client_app_v2/lib/core/api/execution_client.dart</action>
    <!-- Unit tests execution -->
    <action>Run client tests: cd client_app_v2; flutter test test/core/api/studio_client_test.dart</action>
    <action>Run controller tests: cd client_app_v2; flutter test test/features/studio/controllers/studio_controller_test.dart</action>
    <action>Run report generating tests: cd client_app_v2; flutter test test/features/reports/execution_reports_generating_test.dart</action>
  </validation_gate>
</execution_protocol>
```
