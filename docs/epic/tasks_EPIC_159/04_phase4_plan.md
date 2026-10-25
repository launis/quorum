<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_system_audit_trail_xai.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

# Phase 4: Frontend Flutter Studio Integration, Freezed DTO Synchronization & E2E Verification Gate

**Overview:** Implement Studio UI client and controller actions for live MCP tool discovery, integrate Connection/Auth Cards, parameter schema inspection tables, and tool allowlist toggles in `McpGatewayView`, integrate dynamic `{gateway_slug}__{tool_id}` filter chips in `StepBuilderView` and `WorkflowStepCard`, enforce wide-canvas containment (1200px max width) and Theme Sovereignty, and pass live full-stack E2E integration verification gates.

**Source:** @[docs/epic/EPIC_159_DYNAMIC_MCP_ARCHITECTURE.md#L349-L432] Phase 4: Frontend Flutter Studio Integration, Freezed DTO Synchronization & E2E Verification Gate

**Target Files:**
- `[MODIFY] @[client_app_v2/lib/core/api/studio_client.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/step_builder_view.dart]`
- `[MODIFY] @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_en.arb]`
- `[MODIFY] @[client_app_v2/lib/l10n/app_fi.arb]`
- `[NEW] @[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/mcp_gateway_view_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/controllers/mcp_gateways_controller_test.dart]`
- `[MODIFY] @[client_app_v2/test/features/studio/views/workflow_general_tab_model_registry_test.dart]`
- `[MODIFY] @[backend_v2/tests/integration/test_sdui_semantic_parity.py]`
- `[MODIFY] @[backend_v2/tests/integration/test_integration_real_llm.py]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[client_app_v2/lib/core/api/studio_client.dart]` & `controllers/mcp_gateways_controller.dart` | Banned stale cached gateway state after save/discover and silent error swallowing in controllers. | Call `ref.invalidate(mcpGatewayByIdProvider(id))` and propagate errors unconditionally via `if (state.hasError) throw state.error!;`. | Reused existing Riverpod state notifier architecture without custom bus mechanisms. | `flutter test test/features/studio/controllers/mcp_gateways_controller_test.dart`. |
| `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]` | Banned manual raw JSON schema text editing, full-bleed unconstrained layouts, and header text truncation. | Wrap form in `ConstrainedBox(maxWidth: 1200)` and header titles in `Expanded`; replace manual editor with structured parameter `DataTable` and allowlist switches. | Pruned manual schema editing; dynamic read-only parameter previews directly from inspected manifests. | `uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/lib/features/studio/views/mcp_gateway_view.dart`. |
| `@[client_app_v2/lib/features/studio/views/step_builder_view.dart]` & `workflow_step_card.dart` | Banned un-namespaced tool chips colliding across multiple gateways. | Render per-gateway `{gateway.slug}__{tool.toolId}` `FilterChip` selectors filtered by `tool.enabled == true`. | Single consistent namespacing standard from backend to Flutter UI presentation. | `flutter test test/features/studio/views/workflow_general_tab_model_registry_test.dart`. |
| `[NEW] @[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]` & `test_integration_real_llm.py` | Banned deploying dynamic MCP architecture without live end-to-end integration proof. | Spin up in-process mock JSON-RPC 2.0 MCP server, run Studio discovery, dynamic schema compilation, execution loop, and SDUI audit trail verification. | Consolidated E2E validation in dedicated end-to-end pipeline test suite. | `pytest backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py` and live E2E gate. |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Backend SchemaFactory, GenericMCPClient, and ToolDispatcher (Phases 1-3) are completely operational.</action>
    <action>Look forward: Verify Flutter models and controllers are ready for live discovery action and step builder integration.</action>
    <constraint invariant="universal_fail_fast">Enforce AppErrorBoundary wrapping and compile-time localization parity.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: Mark Step 4.1, 4.2, 4.3 checkboxes in @[docs/epic/EPIC_159_tracker.md] upon completion of each sub-step.</directive>
  </step>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/core/api/studio_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/step_builder_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <backend>[NEW] @[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py]</backend>
    <backend>@[backend_v2/tests/integration/test_sdui_semantic_parity.py]</backend>
    <backend>@[backend_v2/tests/integration/test_integration_real_llm.py]</backend>
  </touched_artifacts>

  <dod_checklist>
    <item>StudioClient.discoverMcpGatewayTools calling POST /api/studio/mcp-gateways/$id/discover implemented.</item>
    <item>McpGatewaysController.discoverTools and McpGatewayForm.discoverTools implemented with cache invalidation.</item>
    <item>Dual-Axis localization keys added to app_en.arb and app_fi.arb with 100% parity.</item>
    <item>McpGatewayView updated with 1200px constraint, Connection/Auth Card, discovery button, and parameter preview table.</item>
    <item>StepBuilderView updated with dynamic {gateway.slug}__{tool.toolId} filter chips.</item>
    <item>WorkflowStepCard updated with namespaced tool badge summaries.</item>
    <item>End-to-end integration test test_dynamic_mcp_pipeline_e2e.py passing 100%.</item>
    <item>SDUI semantic parity and live E2E real LLM tests verified.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
    <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
    <knowledge_item>@[ki_dual_axis_localization_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  </required_context_rules>

  <step id="4.1" name="Studio Client API, Controller Discovery Action &amp; Localization">
    <action>In @[client_app_v2/lib/core/api/studio_client.dart], add discoverMcpGatewayTools calling POST /api/studio/mcp-gateways/$id/discover.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/mcp_gateways_controller.dart], add discoverTools on controller and form, invalidating mcpGatewayByIdProvider.</action>
    <action>In @[client_app_v2/lib/l10n/app_en.arb] and @[client_app_v2/lib/l10n/app_fi.arb], add localization keys for discovery, transport/auth dropdowns, parameter table, and allowlist toggles.</action>
    <action>Update controller unit tests in test/features/studio/controllers/mcp_gateways_controller_test.dart.</action>
    <constraint invariant="universal_fail_fast">Unconditionally re-throw controller errors via if (state.hasError) throw state.error!.</constraint>
    <audit_command>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
  </step>

  <step id="4.2" name="Studio MCP Gateway View, Step Builder View &amp; Workflow Step Card Integration">
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart], wrap form in 1200px ConstrainedBox, add Connection/Auth Card, discovery button, and parameter preview table.</action>
    <action>In @[client_app_v2/lib/features/studio/views/step_builder_view.dart], render FilterChip selectors grouped by gateway ({gateway.slug}__{tool.toolId}) for enabled tools.</action>
    <action>In @[client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart], render read-only summary badges for bound tools.</action>
    <action>Update widget tests in test/features/studio/views/mcp_gateway_view_test.dart and workflow_general_tab_model_registry_test.dart.</action>
    <constraint invariant="theme_sovereignty">Strictly eliminate naked TextStyle declarations in favor of Theme.of(context).textTheme.</constraint>
    <audit_command>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
    <audit_command>uv run python scripts/audit_flutter_theme_sovereignty.py client_app_v2/lib/features/studio/views/mcp_gateway_view.dart client_app_v2/lib/features/studio/views/step_builder_view.dart client_app_v2/lib/features/studio/views/widgets/workflow/workflow_step_card.dart</audit_command>
  </step>

  <step id="4.3" name="Mandatory Live E2E Integration Gate &amp; SDUI Audit Trail Parity">
    <action>Create [NEW] @[backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py] testing full discovery, schema compilation, execution, and SDUI audit trace emission.</action>
    <action>Execute SDUI parity tests in @[backend_v2/tests/integration/test_sdui_semantic_parity.py].</action>
    <action>Execute live E2E real LLM verification gate in @[backend_v2/tests/integration/test_integration_real_llm.py].</action>
    <constraint invariant="universal_fail_fast">All E2E pipeline integration assertions must pass 100%.</constraint>
    <audit_command>uv run python scripts/backend_audit_loop.py backend_v2/tests/integration/test_dynamic_mcp_pipeline_e2e.py --test --ast-strict</audit_command>
  </step>
</execution_protocol>
```
