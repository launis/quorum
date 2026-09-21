# Phase 2: SDUI Dumb Painter Performance & Cell Decomposition

**Overview:** Elevate Quorum's SDUI rendering widgets to meet the O(1) Dumb Painter rendering performance mandate defined in `@[ki_dumb_painter_sdui.md]`. Decompose the monolithic 635-line `SduiMatrixTableWidget` into 4 private Dumb Painter cell widgets, eradicate in-`build` sorting passes (`..sort(...)`) and allocation thrashing, eliminate mutable list allocations from `XAIAxisTelemetryGrid`, align `AtomMatrixTableWidget` to the canonical macro-breakpoint standard (`< 800px`), and eradicate all 9 instances of `const SizedBox.shrink()` concealment from `sdui_blocks_renderer.dart` to achieve 0 `DGR002` violations.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L324-L351] Phase 2: SDUI Dumb Painter Performance & Cell Decomposition
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/sdui_blocks_renderer_test.dart]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established typed Freezed models and zero permissive typing across API boundaries.</action>
    <action>Look forward: Verify that Phase 3 and Phase 4 master views and modals render cleanly without SDUI rendering bottlenecks or DGR002 concealment.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/02_phase2_plan.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>SduiMatrixTableWidget in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] decomposed into 4 private Dumb Painter sub-widgets (_MatrixSummaryCriteriaCell, _MatrixSummaryQuotesCell, _MatrixSummaryDistributionCell, _MatrixSummaryScoreCell).</item>
    <item>In-build sorting passes (breakdown.keys.toList()..sort(...) and grouped.keys.toList()..sort(...)) completely purged from rendering loops.</item>
    <item>Table cells constrained with ConstrainedBox(maxWidth: 350) and TextOverflow.ellipsis to prevent RenderFlex hazards.</item>
    <item>XAIAxisTelemetryGrid in @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart] allocates zero mutable widget lists (final List&lt;Widget&gt; boxes = []; purged).</item>
    <item>AtomMatrixTableWidget in @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart] adheres to the canonical macro-breakpoint standard (&lt; 800px) and Material 3 colorScheme tokens.</item>
    <item>Exactly 0 SizedBox.shrink() occurrences in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart] (all 9 instances eradicated, passing DGR002).</item>
    <item>All targeted widget test suites pass with 100% green assertions.</item>
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
    <forbidden>Do NOT create new public top-level widget files for the 4 table cells; keep them private to @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] to prevent file sprawl and preserve Dumb Painter encapsulation.</forbidden>
    <forbidden>Do NOT introduce client-side matrix score calculation or synthesis logic; UI remains strictly a Dumb Painter.</forbidden>
    <forbidden>Do NOT modify master views or dialogs during Phase 2 (reserved for Phase 3 and Phase 4).</forbidden>
  </anti_targets>

  <touched_artifacts>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]</frontend>
  </touched_artifacts>

  <contract_freeze>
    <class name="_MatrixSummaryCriteriaCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryCriteriaCell extends StatelessWidget
      final String criteriaText
      final String? scaleLabel
    </class>
    <class name="_MatrixSummaryQuotesCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryQuotesCell extends StatelessWidget
      final List&lt;String&gt; quotes
    </class>
    <class name="_MatrixSummaryDistributionCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryDistributionCell extends StatelessWidget
      final Map&lt;String, int&gt; distribution
      final List&lt;String&gt; sortedLevels
    </class>
    <class name="_MatrixSummaryScoreCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryScoreCell extends StatelessWidget
      final double score
      final String status
    </class>
  </contract_freeze>

  <step id="2.1" name="SduiMatrixTableWidget Cell Decomposition &amp; In-Build Sorting Purge">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]:</action>
    <action>- Decompose monolithic 635-line layout into 4 private, const-constructible Dumb Painter sub-widgets:</action>
    <action>  * _MatrixSummaryCriteriaCell: renders criteria description without in-build sorting.</action>
    <action>  * _MatrixSummaryQuotesCell: renders verbatim quotes and citations.</action>
    <action>  * _MatrixSummaryDistributionCell: formats level distributions.</action>
    <action>  * _MatrixSummaryScoreCell: renders score badge and status chips.</action>
    <action>- Pre-sort level keys once during widget initialization or memoized getter, eliminating breakdown.keys.toList()..sort(...) and grouped.keys.toList()..sort(...) inside the rendering loop.</action>
    <action>- Enclose table cells within ConstrainedBox(maxWidth: 350) with TextOverflow.ellipsis.</action>
    <demolish>REMOVE: in-build `..sort(...)` calls on `breakdown.keys.toList()` and `grouped.keys.toList()` in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]. REPLACE WITH: memoized pre-sorted level keys.</demolish>
  </step>

  <step id="2.2" name="XAIAxisTelemetryGrid &amp; AtomMatrixTableWidget Refactoring">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]:</action>
    <action>- Eradicate dynamic mutable list allocation (final List&lt;Widget&gt; boxes = [];).</action>
    <action>- Replace with declarative Column layout using const-constructible card widgets.</action>
    <action>- Replace hardcoded AppColors with Material 3 Theme tokens (colorScheme.tertiaryContainer, colorScheme.surfaceContainerHighest, colorScheme.errorContainer).</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]:</action>
    <action>- Replace arbitrary breakpoint constraints.maxWidth &lt; 600 with the canonical macro-breakpoint standard (constraints.maxWidth &lt; 800).</action>
    <action>- Replace magic numbers with AppSpacing.h8 and AppSpacing.h16.</action>
    <action>- Replace raw Colors.amber and Colors.blue with theme tokens (colorScheme.tertiaryContainer, colorScheme.primaryContainer).</action>
    <demolish>REMOVE: `final List&lt;Widget&gt; boxes = [];` and `boxes.add(...)` in @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart]. REPLACE WITH: declarative Column children list.</demolish>
  </step>

  <step id="2.3" name="Purge SizedBox.shrink() Concealment (DGR002)">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]:</action>
    <action>- Purge all 9 instances of const SizedBox.shrink() intentionally swallowing empty markdown and paragraph blocks.</action>
    <action>- Replace with declarative collection-if empty guards (if (block.text.isNotEmpty)) or explicit typed representation.</action>
    <action>- Assert zero DGR002 violations via scripts/_dart_guardrails.py.</action>
    <demolish>REMOVE: 9 occurrences of `const SizedBox.shrink()` in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]. REPLACE WITH: collection-if empty checks and typed rendering.</demolish>
  </step>

  <test_contracts>
    <test name="test_sdui_matrix_table_widget_renders_cells_without_sorting_jank" category="positive">
      <input>SduiMatrixTableWidget with 5 criteria rows and level breakdowns</input>
      <expected>Renders 4 cell sub-widgets without throwing or layout thrashing</expected>
    </test>
    <test name="test_sdui_matrix_table_widget_narrow_viewport_no_overflow" category="boundary">
      <input>Viewport constrained to 360px width</input>
      <expected>Renders without RenderFlex overflow hazard stripes</expected>
    </test>
    <test name="test_xai_axis_telemetry_grid_declarative_rendering" category="positive">
      <input>XAIAxisTelemetryGrid with 4 telemetry axes</input>
      <expected>Renders cards declaratively using Material 3 theme tokens</expected>
    </test>
    <test name="test_sdui_blocks_renderer_zero_sized_box_shrink" category="positive">
      <input>List of SDUI blocks containing empty text</input>
      <expected>Collection-if omits empty blocks rather than returning SizedBox.shrink()</expected>
    </test>
    <test name="test_atom_matrix_table_widget_macro_breakpoint_switching" category="boundary">
      <input>Width at 799px vs 800px</input>
      <expected>Switches between mobile linear layout and desktop tabular layout at 800px</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Dart guardrails: Assert 0 DGR002 violations in sdui_blocks_renderer.dart -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart</action>
    <!-- Targeted widget test execution -->
    <action>Run matrix table test: cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart</action>
    <action>Run telemetry grid test: cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart</action>
    <action>Run blocks renderer test: cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_blocks_renderer_test.dart</action>
  </validation_gate>
</execution_protocol>
```
