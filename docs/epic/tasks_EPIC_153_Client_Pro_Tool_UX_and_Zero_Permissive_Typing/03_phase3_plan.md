# Phase 3: Desktop Pro Tool Studio Master Views Virtualization & Containment

**Overview:** Standardize layout architecture across all 4 Quorum Studio master list views by virtualizing list rendering with `prototypeItem`, eradicating unvirtualized `SingleChildScrollView` wrappers, enforcing 1200px centered max-width containment on 4K displays, mounting sticky `StudioMasterHeader` controls, and purging banned Freezed `.when()` calls in favor of Dart 3 native `switch` expressions.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L354-L372] Phase 3: Desktop Pro Tool Studio Master Views Virtualization & Containment
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/workflows_master_view.dart#L1-L247]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/matrices_master_view.dart#L1-L164]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart#L1-L159]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L1-L132]
- `[NEW]` @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb#L1740-L1770]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_fi.arb#L1085-L1115]
- `[NEW]` @[client_app_v2/test/features/studio/views/widgets/studio_master_header_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/workflows_master_view_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/matrices_master_view_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/output_profile_list_view_test.dart]
- `[NEW]` @[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established typed domain models and Phase 2 eliminated SDUI cell calculation thrashing.</action>
    <action>Look forward: Verify that subsequent Phase 4 modal dialog hardening integrates smoothly with virtualized master navigation views.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/03_phase3_plan.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Pre-implementation technical debt cleanups in Step 3.0 resolve dead fallbacks, hardcoded tooltips, and uncontained empty states across the 4 master views.</item>
    <item>[NEW] StudioMasterHeader implemented in @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart] with pinned title, subtitle, real-time search field with clear trigger, active count badge (X / Y kohteesta), primary action button, and 100% theme token adherence.</item>
    <item>SingleChildScrollView wrapping ListView.builder(shrinkWrap: true) completely eradicated across all 4 Quorum Studio master list views.</item>
    <item>Pure virtualized ListView.builder with prototypeItem implemented for buttery 60 FPS scrolling across all 4 master views.</item>
    <item>Centered 1200px max-width boundary via Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: BoxConstraints(maxWidth: 1200))) enforced across all 4 master views.</item>
    <item>Zero Freezed .when() calls in touched master views (workflows_master_view.dart#L65 refactored to native switch pattern matching).</item>
    <item>Raw category string filters replaced with PromptBlockCategoryGroups.matrixCategories enum grouping in matrices_master_view.dart.</item>
    <item>All 5 master view and widget test suites pass with 100% green assertions and zero DGR001/DGR002 violations.</item>
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
    <forbidden>Do NOT modify backend API routers, services, or models during Phase 3.</forbidden>
    <forbidden>Do NOT touch studio_dashboard_view.dart (out of scope, registered as future technical debt).</forbidden>
    <forbidden>Do NOT introduce SizedBox.shrink() or SizedBox() empty widgets (violates DGR002).</forbidden>
    <forbidden>Do NOT bypass virtualization with shrinkWrap: true or SingleChildScrollView.</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/studio/views/workflows_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/matrices_master_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/output_profile_list_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_en.arb]</frontend>
    <frontend>@[client_app_v2/lib/l10n/app_fi.arb]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/widgets/studio_master_header_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/workflows_master_view_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/matrices_master_view_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/output_profile_list_view_test.dart]</frontend>
    <frontend>[NEW] @[client_app_v2/test/features/studio/views/mcp_gateways_master_view_test.dart]</frontend>
  </touched_artifacts>

  <contract_freeze>
    <class name="StudioMasterHeader" path="[NEW] @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]">
      class StudioMasterHeader extends StatelessWidget
      final String title
      final String? subtitle
      final String searchQuery
      final ValueChanged&lt;String&gt; onSearchChanged
      final int itemCount
      final int totalCount
      final String? actionLabel
      final IconData? actionIcon
      final VoidCallback? onAction
      final Widget? leading
      final Widget? bottom
    </class>
  </contract_freeze>

  <step id="3.0" name="Pre-Implementation Technical Debt Cleanups">
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart#L1-L247]:</action>
    <action>- Replace hardcoded clone tooltip string 'Duplicate (Deep Copy)' with localized string from AppLocalizations.</action>
    <action>- Replace raw exception banner string assignment `_bannerError = e.toString();` with localized user-friendly error formatting.</action>
    <action>- Enclose ListTile title text in `Text(displayName, overflow: TextOverflow.ellipsis)` to prevent horizontal overflow.</action>
    <action>In @[client_app_v2/lib/features/studio/views/matrices_master_view.dart#L1-L164]:</action>
    <action>- Eradicate dead fallback code `if (displayName.isEmpty == true &amp;&amp; matrix.id.isNotEmpty) { // Fallback }` (#L88-#L90).</action>
    <action>- Replace hardcoded clone tooltip string 'Duplicate (Deep Copy)' (#L115) with localized string.</action>
    <action>- Center empty state text via `Center(child: Text(l10n.studioViewsNoMatricesAvailable))`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart#L1-L159]:</action>
    <action>- Replace hardcoded clone tooltip string 'Duplicate (Deep Copy)' with localized string.</action>
    <action>- Center empty state text via `Center(child: Text(l10n.studioViewsNoOutputProfiles))`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart#L1-L132]:</action>
    <action>- Add user-facing error state `_bannerError` handling in State to surface failed draft creation visibly instead of silent console logging.</action>
    <action>- Center empty state text via `Center(child: Text(l10n.noMcpGatewaysDefined))`.</action>
  </step>

  <step id="3.1" name="Standardized Master View Virtualization &amp; Containment">
    <action>Implement reusable [NEW] @[client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart]:</action>
    <action>- Top row: Title wrapped in `Expanded(child: Text(title, overflow: TextOverflow.ellipsis))` alongside optional action button `FilledButton.icon`.</action>
    <action>- Subtitle wrapped in `Text(subtitle, overflow: TextOverflow.ellipsis)` using `textTheme.bodyMedium`.</action>
    <action>- Real-time instant search input `TextField` with `prefixIcon: Icon(Icons.search)`, clear trigger `IconButton(icon: Icon(Icons.clear))`, and `isDense: true`.</action>
    <action>- Active count pill badge: `Container` styled with `colorScheme.primaryContainer` and rounded borders displaying `l10n.studioMasterItemCount(itemCount, totalCount)`.</action>
    <action>In @[client_app_v2/lib/l10n/app_en.arb#L1740-L1770] and @[client_app_v2/lib/l10n/app_fi.arb#L1085-L1115]:</action>
    <action>- Add `studioMasterSearchHint` ("Search items...", "Hae kohteita...").</action>
    <action>- Add `studioMasterClearSearch` ("Clear search", "Tyhjennä haku").</action>
    <action>- Add `studioMasterItemCount` ("Showing {filtered} of {total} items", "{filtered} / {total} kohteesta").</action>
    <action>- Add `studioMasterDuplicateTooltip` ("Duplicate (Deep Copy)", "Monista (Syväkopio)").</action>
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart], @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], @[client_app_v2/lib/features/studio/views/output_profile_list_view.dart], and @[client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart]:</action>
    <action>- Eradicate SingleChildScrollView wrapping ListView.builder(shrinkWrap: true, physics: NeverScrollableScrollPhysics()) in all 4 views.</action>
    <action>- Implement pure virtualized ListView.builder with prototypeItem for buttery 60 FPS scrolling.</action>
    <action>- Implement centered 1200px max-width boundary via Align(alignment: Alignment.topCenter, child: ConstrainedBox(constraints: const BoxConstraints(maxWidth: 1200), child: ...)) to eliminate stretched layouts on 4K displays.</action>
    <action>- Mount sticky pinned header (StudioMasterHeader) with real-time query filtering updating in-memory items and count badge.</action>
    <demolish>REMOVE: `SingleChildScrollView` wrapping `ListView.builder(shrinkWrap: true)` across all 4 Quorum Studio master list views. REPLACE WITH: virtualized `ListView.builder` with `prototypeItem` and centered 1200px `ConstrainedBox`.</demolish>
  </step>

  <step id="3.2" name="Banned Freezed .when() Purge &amp; Enum Alignment">
    <action>In @[client_app_v2/lib/features/studio/views/workflows_master_view.dart#L65], replace Freezed .when() with Dart 3 native switch (workflowsState) pattern matching.</action>
    <action>In @[client_app_v2/lib/features/studio/views/matrices_master_view.dart], replace raw category string filters (b.categoryId == 'matrix') with PromptBlockCategoryGroups.matrixCategories enum grouping in @[client_app_v2/lib/core/models/enums.dart].</action>
    <action>Enclose title Text widgets inside horizontal header rows with Expanded(child: Text(..., overflow: TextOverflow.ellipsis)) to eliminate RenderFlex overflow.</action>
    <demolish>REMOVE: Freezed `.when()` in @[client_app_v2/lib/features/studio/views/workflows_master_view.dart]. REPLACE WITH: Dart 3 native `switch (workflowsState)` pattern matching.</demolish>
    <demolish>REMOVE: raw string filter `b.categoryId == 'matrix'` in @[client_app_v2/lib/features/studio/views/matrices_master_view.dart]. REPLACE WITH: `PromptBlockCategoryGroups.matrixCategories.contains(...)`.</demolish>
  </step>

  <test_contracts>
    <test name="test_studio_master_header_rendering_and_search_trigger" category="positive">
      <input>StudioMasterHeader pumped with title 'Workflows', query 'diag', itemCount 3, totalCount 10</input>
      <expected>Renders title, search TextField with clear trigger, and count pill '3 / 10 kohteesta'</expected>
    </test>
    <test name="test_workflows_master_view_virtualized_rendering" category="positive">
      <input>Workflows master view loaded with 50 mock workflows</input>
      <expected>Renders virtualized ListView.builder with prototypeItem without inflating all 50 items simultaneously</expected>
    </test>
    <test name="test_master_views_4k_display_containment" category="boundary">
      <input>Viewport resized to 3840px width by 2160px height</input>
      <expected>Master list container width remains clamped to 1200px centered</expected>
    </test>
    <test name="test_matrices_master_view_instant_search_filtering" category="positive">
      <input>User types search query into StudioMasterHeader</input>
      <expected>Filters in-memory items reactively and updates count badge</expected>
    </test>
    <test name="test_output_profile_list_view_empty_and_error_states" category="negative">
      <input>Search query matching 0 output profiles OR AsyncError state emitted</input>
      <expected>Renders centered empty feedback when search yields 0 items and ErrorView on failure</expected>
    </test>
    <test name="test_mcp_gateways_master_view_search_and_clone" category="positive">
      <input>User searches for gateway and clicks clone button</input>
      <expected>Filters list and executes cloneGateway notifier action</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Dart guardrails: Assert zero Freezed .when() calls in master views -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/studio/views/workflows_master_view.dart client_app_v2/lib/features/studio/views/matrices_master_view.dart client_app_v2/lib/features/studio/views/output_profile_list_view.dart client_app_v2/lib/features/studio/views/mcp_gateways_master_view.dart client_app_v2/lib/features/studio/views/widgets/studio_master_header.dart</action>
    <!-- Widget test validation -->
    <action>Run master views widget tests: cd client_app_v2; flutter test test/features/studio/views/widgets/studio_master_header_test.dart test/features/studio/views/workflows_master_view_test.dart test/features/studio/views/matrices_master_view_test.dart test/features/studio/views/output_profile_list_view_test.dart test/features/studio/views/mcp_gateways_master_view_test.dart</action>
  </validation_gate>
</execution_protocol>
```
