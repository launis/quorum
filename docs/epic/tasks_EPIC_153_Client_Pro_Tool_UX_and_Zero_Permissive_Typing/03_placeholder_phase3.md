# Phase 3: Desktop Pro Tool Studio Master Views Virtualization & Containment

**Overview:** Standardize layout architecture across all 4 Quorum Studio master list views by virtualizing list rendering with `prototypeItem`, eradicating unvirtualized `SingleChildScrollView` wrappers, enforcing 1200px centered max-width containment on 4K displays, mounting sticky `StudioMasterHeader` controls, and purging banned Freezed `.when()` calls in favor of Dart 3 native `switch` expressions.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L354-L372] Phase 3: Desktop Pro Tool Studio Master Views Virtualization & Containment
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/workflows_master_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established typed domain models and Phase 2 eliminated SDUI cell calculation thrashing.</action>
    <action>Look forward: Verify that subsequent Phase 4 modal dialog hardening integrates smoothly with virtualized master navigation views.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/03_placeholder_phase3.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>SingleChildScrollView wrapping ListView.builder(shrinkWrap: true) completely eradicated across all 4 Quorum Studio master list views.</item>
    <item>Pure virtualized ListView.builder with prototypeItem implemented for buttery 60 FPS scrolling.</item>
    <item>Centered 1200px max-width boundary via Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: BoxConstraints(maxWidth: 1200))) enforced.</item>
    <item>Sticky pinned header (StudioMasterHeader) with search, count badge, and add action integrated across all 4 views.</item>
    <item>Zero Freezed .when() calls in touched master views (workflows_master_view.dart#L65 refactored to native switch pattern matching).</item>
    <item>Raw category string filters replaced with PromptBlockCategoryGroups enum grouping in matrices_master_view.dart.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
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
    <forbidden>Do NOT modify modal dialogs or human override views during Phase 3 (reserved for Phase 4).</forbidden>
    <forbidden>Do NOT modify backend API routers or models during Phase 3.</forbidden>
    <forbidden>Do NOT touch studio_dashboard_view.dart (out of scope, registered as future technical debt).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]</frontend>
  </touched_artifacts>

  <step id="3.1" name="Standardized Master View Virtualization &amp; Containment">
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart], @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart], and @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]:</action>
    <action>- Eradicate SingleChildScrollView wrapping ListView.builder(shrinkWrap: true, physics: NeverScrollableScrollPhysics()) in all 4 views.</action>
    <action>- Implement pure virtualized ListView.builder with prototypeItem for buttery 60 FPS scrolling.</action>
    <action>- Implement centered 1200px max-width boundary via Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ...)) to eliminate stretched layouts on 4K displays.</action>
    <action>- Implement sticky pinned header (StudioMasterHeader) containing view title, subtitle, real-time instant search input with clear trigger, active item count badge (X / Y kohteesta), and primary action button (+ Uusi).</action>
    <demolish>REMOVE: `SingleChildScrollView` wrapping `ListView.builder(shrinkWrap: true)` across all 4 Quorum Studio master list views. REPLACE WITH: virtualized `ListView.builder` with `prototypeItem` and centered 1200px `ConstrainedBox`.</demolish>
  </step>

  <step id="3.2" name="Banned Freezed .when() Purge &amp; Enum Alignment">
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart], replace Freezed .when() with Dart 3 native switch (workflowsState) pattern matching.</action>
    <action>In @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], replace raw category string filters (b.categoryId == 'matrix') with PromptBlockCategoryGroups.matrixCategories enum grouping in @[client_app_v2/lib/core/models/enums.dart].</action>
    <action>Enclose title Text widgets inside horizontal header rows with Expanded(child: Text(..., overflow: TextOverflow.ellipsis)) to eliminate RenderFlex overflow.</action>
    <demolish>REMOVE: Freezed `.when()` in @[client_app_v2/lib/features/studio/views/workflows_master_view.dart]. REPLACE WITH: Dart 3 native `switch (workflowsState)` pattern matching.</demolish>
    <demolish>REMOVE: raw string filter `b.categoryId == 'matrix'` in @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]. REPLACE WITH: `PromptBlockCategoryGroups.matrixCategories.contains(...)`.</demolish>
  </step>

  <test_contracts>
    <test name="test_workflows_master_view_virtualized_rendering" category="positive">
      <input>Workflows master view loaded with 50 mock workflows</input>
      <expected>Renders virtualized ListView.builder without building all 50 items simultaneously</expected>
    </test>
    <test name="test_master_views_4k_display_containment" category="boundary">
      <input>Viewport resized to 3840px width</input>
      <expected>Master list container width remains clamped to 1200px centered</expected>
    </test>
    <test name="test_matrices_master_view_instant_search_filtering" category="positive">
      <input>User types search query into StudioMasterHeader</input>
      <expected>Filters in-memory items reactively and updates count badge</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Dart guardrails: Assert zero Freezed .when() calls in master views -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/studio/views/workflows_master_view.dart client_app_v2/lib/features/studio/views/matrices_master_view.dart client_app_v2/lib/features/studio/views/output_profile_list_view.dart client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart</action>
    <!-- Widget test validation -->
    <action>Run output profile view tests: cd client_app_v2; flutter test test/features/studio/views/output_profile_crud_view_test.dart</action>
  </validation_gate>
</execution_protocol>
```
