# Phase 2: SDUI Dumb Painter Performance & Cell Decomposition

**Overview:** Elevate Quorum's SDUI rendering widgets to meet the O(1) Dumb Painter rendering performance mandate defined in `@[ki_dumb_painter_sdui.md]`. Decompose the monolithic 635-line `SduiMatrixTableWidget` into 4 private Dumb Painter cell widgets, eradicate in-`build` sorting passes (`..sort(...)`) and allocation thrashing, eliminate mutable list allocations from `XAIAxisTelemetryGrid`, align `AtomMatrixTableWidget` to the canonical macro-breakpoint standard (`< 800px`), and eradicate all 9 instances of `const SizedBox.shrink()` concealment from `sdui_blocks_renderer.dart` to achieve 0 `DGR002` violations.
**Source:** @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md#L324-L351] Phase 2: SDUI Dumb Painter Performance & Cell Decomposition
**Target Files:**
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L10-L634]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart#L10-L407]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L12-L744]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L18-L645]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart#L10-L691]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart#L9-L220]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/sdui_blocks_renderer_test.dart#L8-L300]
- `[MODIFY]` @[client_app_v2/test/features/execution/views/widgets/atom_matrix_table_widget_test.dart#L10-L299]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify that Phase 1 established typed Freezed models and zero permissive typing across API boundaries.</action>
    <action>Look forward: Verify that Phase 3 and Phase 4 master views and modals render cleanly without SDUI rendering bottlenecks or DGR002 concealment.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document @[docs/epic/EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing.md] and synchronize architectural corrections back into the Epic. If a Tracker document exists (@[docs/epic/EPIC_153_tracker.md]), you MUST update its # Session Handover Context and set Resume Command to /tier2-execute @[docs/epic/tasks_EPIC_153_Client_Pro_Tool_UX_and_Zero_Permissive_Typing/02_phase2_plan.md] @[docs/epic/EPIC_153_tracker.md] (ALWAYS passing BOTH the plan file and the tracker file).</directive>
  </step>

  <dod_checklist>
    <item>Pre-implementation cleanups in Step 2.0 resolve mutable list allocation, in-build sorting passes, and hardcoded colors in AtomMatrixTableWidget.</item>
    <item>SduiMatrixTableWidget in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart] decomposed into 4 private Dumb Painter sub-widgets (_MatrixSummaryCriteriaCell, _MatrixSummaryQuotesCell, _MatrixSummaryDistributionCell, _MatrixSummaryScoreCell).</item>
    <item>In-build sorting passes (breakdown.keys.toList()..sort(...) and grouped.keys.toList()..sort(...)) completely purged from rendering loops across all table widgets.</item>
    <item>Table cells constrained with ConstrainedBox(maxWidth: 350) and TextOverflow.ellipsis to prevent RenderFlex hazards.</item>
    <item>XAIAxisTelemetryGrid in @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart] token-bound with Material 3 Theme tokens (colorScheme.tertiaryContainer, colorScheme.surfaceContainerHighest, colorScheme.errorContainer).</item>
    <item>AtomMatrixTableWidget in @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart] adheres to the canonical macro-breakpoint standard (&lt; 800px) and Material 3 colorScheme tokens.</item>
    <item>Exactly 0 SizedBox.shrink() occurrences in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart] (all 9 instances eradicated, passing DGR002 with 0 violations).</item>
    <item>All 4 targeted widget test suites pass with 100% green assertions.</item>
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
    <frontend>@[client_app_v2/test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/execution/views/widgets/sdui_blocks_renderer_test.dart]</frontend>
    <frontend>@[client_app_v2/test/features/execution/views/widgets/atom_matrix_table_widget_test.dart]</frontend>
  </touched_artifacts>

  <contract_freeze>
    <class name="_MatrixSummaryCriteriaCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryCriteriaCell extends StatelessWidget
      final List&lt;ScorecardAtomDto&gt; criteriaAtoms
      final Map&lt;int, List&lt;ScorecardAtomDto&gt;&gt; atomsByLevel
      final List&lt;int&gt; sortedLevels
      final Map&lt;String, String&gt;? levelNames
    </class>
    <class name="_MatrixSummaryQuotesCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryQuotesCell extends StatelessWidget
      final List&lt;ScorecardAtomDto&gt; quoteAtoms
      final Map&lt;int, List&lt;ScorecardAtomDto&gt;&gt; atomsByLevel
      final List&lt;int&gt; sortedLevels
      final Map&lt;String, String&gt;? levelNames
      final bool allowContextualOverride
    </class>
    <class name="_MatrixSummaryDistributionCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryDistributionCell extends StatelessWidget
      final Map&lt;String, String&gt; breakdown
      final List&lt;String&gt; sortedKeys
      final Map&lt;String, String&gt;? levelNames
    </class>
    <class name="_MatrixSummaryScoreCell" path="@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]">
      class _MatrixSummaryScoreCell extends StatelessWidget
      final String? scoreLabel
      final double? uiPlotRatio
      final bool isNormalized
    </class>
  </contract_freeze>

  <step id="2.0" name="Pre-Implementation Technical Debt Cleanups">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L12-L744]:</action>
    <action>- Eradicate mutable widget list allocation `final itemsToRender = &lt;Widget&gt;[];` and imperative `.add(...)` loop in `_buildQuotesColumn` (#L466-#L560), replacing with declarative collection-for and collection-if.</action>
    <action>- Replace hardcoded colors (`Colors.black54` at #L208, `Colors.amber` at #L505/#L517, `Colors.amber.shade300` at #L506, `Colors.amber.shade900` at #L527/#L543, `Colors.black26`/`Colors.black38` at #L610-#L614) with semantic Material 3 tokens (`theme.colorScheme.onSurfaceVariant`, `theme.colorScheme.tertiaryContainer`, `theme.colorScheme.onTertiaryContainer`).</action>
    <action>- Eradicate in-build sorting passes on `levelBreakdown!.keys.toList()..sort(...)` (#L163, #L315) and `atomsByLevel.keys.toList()..sort(...)` (#L443), pre-sorting once per row or using memoized keys.</action>
    <action>- Resolve DGR003 warning at line 416 (`title: Text('$numLvl - $name: $display')`).</action>
    <demolish>REMOVE: mutable `itemsToRender` list allocation, `..sort(...)` passes in build methods, and hardcoded `Colors.amber`/`Colors.black` in @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart]. REPLACE WITH: declarative widget collections and Material 3 theme tokens.</demolish>
  </step>

  <step id="2.1" name="SduiMatrixTableWidget Cell Decomposition &amp; In-Build Sorting Purge">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L10-L634]:</action>
    <action>- Decompose monolithic 635-line layout into 4 private, const-constructible Dumb Painter sub-widgets:</action>
    <action>  * `_MatrixSummaryCriteriaCell`: renders criteria description with pre-sorted level keys.</action>
    <action>  * `_MatrixSummaryQuotesCell`: renders verbatim quotes, semantic reasoning, cognitive overrides, and source citations.</action>
    <action>  * `_MatrixSummaryDistributionCell`: formats level distributions with pre-sorted keys.</action>
    <action>  * `_MatrixSummaryScoreCell`: renders score badge and normalized score chip.</action>
    <action>- Pre-sort level keys once per row before passing to cells, eliminating `breakdown.keys.toList()..sort(...)` (#L130-L131) and `grouped.keys.toList()..sort(...)` (#L164-L165, #L221-L222) inside the cell rendering loop.</action>
    <action>- Enclose table cells within `ConstrainedBox(maxWidth: 350)` with `TextOverflow.ellipsis` to prevent RenderFlex overflow hazards.</action>
    <demolish>REMOVE: in-build `..sort(...)` calls on `breakdown.keys.toList()` and `grouped.keys.toList()` in @[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart]. REPLACE WITH: memoized pre-sorted level keys passed to sub-widgets.</demolish>
  </step>

  <step id="2.2" name="XAIAxisTelemetryGrid &amp; AtomMatrixTableWidget Refactoring">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart#L10-L407]:</action>
    <action>- Replace hardcoded `AppColors` (#L98, #L102, #L115, #L182, #L189, #L205, #L208, #L220, #L228, #L360) with Material 3 Theme tokens (`colorScheme.tertiaryContainer`, `colorScheme.surfaceContainerHighest`, `colorScheme.errorContainer`).</action>
    <action>- Ensure declarative Column layout with zero mutable allocations.</action>
    <action>In @[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L12-L744]:</action>
    <action>- Verify adherence to the canonical macro-breakpoint standard (`constraints.maxWidth &lt; 800`).</action>
    <action>- Replace any remaining magic numbers with `AppSpacing.h8` and `AppSpacing.h16` tokens.</action>
  </step>

  <step id="2.3" name="Purge SizedBox.shrink() Concealment (DGR002)">
    <action>In @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L18-L645]:</action>
    <action>- Purge all 9 instances of `const SizedBox.shrink()` (#L49, #L56, #L101, #L132, #L139, #L167, #L253, #L554, #L587).</action>
    <action>- Refactor block-building methods to return `Widget?` (returning `null` when content is empty) and compose the Column children array using declarative pattern matching: `for (final block in blocks) if (_renderBlock(context, block) case final widget?) widget`.</action>
    <action>- In `_buildBulletList`, replace item-level `SizedBox.shrink()` with collection-for and collection-if: `for (final item in block.items) if (item.text.isNotEmpty) Padding(...)`.</action>
    <action>- Assert zero `DGR002` violations via `scripts/_dart_guardrails.py`.</action>
    <demolish>REMOVE: all 9 occurrences of `const SizedBox.shrink()` in @[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart]. REPLACE WITH: `Widget?` return types with collection-if null omission.</demolish>
  </step>

  <five_column_directives>
    <!-- 5-Column Architectural Directives Table -->
    | 1. Target Scope &amp; Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification &amp; Fail-Fast (Proof Anchor) |
    | :--- | :--- | :--- | :--- | :--- |
    | **SduiMatrixTableWidget** `@[client_app_v2/lib/features/execution/views/widgets/sdui_matrix_table_widget.dart#L10-L634]` | In-`build` sorting (`..sort(...)`), unbounded table cells, monolithic 635-line `build()` method. | Private const-constructible cell widgets (`_MatrixSummaryCriteriaCell`, `_MatrixSummaryQuotesCell`, `_MatrixSummaryDistributionCell`, `_MatrixSummaryScoreCell`) with pre-sorted keys and `ConstrainedBox(maxWidth: 350)`. | Kept sub-widgets private within the same file to prevent top-level file sprawl and unnecessary public API surface. | `cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart` passes with 0 exceptions. |
    | **SduiBlocksRenderer** `@[client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart#L18-L645]` | 9 instances of `const SizedBox.shrink()` swallowing empty blocks and concealing layout hazards (`DGR002`). | Clean `Widget?` returns with declarative collection-if (`if (_renderBlock(...) case final w?) w`) completely omitting empty widgets from the element tree. | No redundant wrapper widgets or proxy builders; direct Dart 3 switch expression destructuring. | `uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart` reports 0 `DGR002` violations. |
    | **AtomMatrixTableWidget** `@[client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart#L12-L744]` | Mutable list allocation (`final itemsToRender = &lt;Widget&gt;[];`), hardcoded `Colors.amber` and `Colors.black54`, in-build sorting. | Declarative widget lists, Material 3 `Theme.of(context).colorScheme` tokens, pre-sorted level keys, and canonical macro-breakpoint (`&lt; 800px`). | Zero extra stateful classes or complex layout wrappers; pure `ConsumerWidget` presentation. | `cd client_app_v2; flutter test test/features/execution/views/widgets/atom_matrix_table_widget_test.dart` passes 100% green. |
    | **XAIAxisTelemetryGrid** `@[client_app_v2/lib/features/execution/views/widgets/xai_axis_telemetry_grid.dart#L10-L407]` | Hardcoded `AppColors.intent*` static palette bypasses Material 3 dynamic theming. | Declarative Column layout bound strictly to `Theme.of(context).colorScheme` and `AppSpacing` tokens. | Zero bespoke grid abstractions; straightforward Flex/Column layout. | `cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart` passes 100% green. |
  </five_column_directives>

  <red_team_falsification_scenarios>
    <scenario id="1" name="Contract Freeze Semantic Regression">
      <attack>If cell sub-widgets are created with overly simplified primitive parameters (e.g. `List&lt;String&gt; quotes`), rich quote rendering (claim labels, reasoning arrows, cognitive override styling, URL launchers) is wiped out.</attack>
      <defense>Sub-widgets take typed domain models (`ScorecardAtomDto`, `QuoteEvidenceDto`, `levelNames`) and pre-sorted keys, guaranteeing 100% parity with existing unit test assertions in `sdui_matrix_table_widget_test.dart`.</defense>
    </scenario>
    <scenario id="2" name="DGR002 Evasion via SizedBox()">
      <attack>Replacing `const SizedBox.shrink()` with `const SizedBox()` would evade static AST regex detection while still polluting the element tree with empty nodes and layout bloat.</attack>
      <defense>Block helpers return `Widget?` and are filtered via collection-if `if (_renderBlock(...) case final widget?) widget`, ensuring zero empty nodes enter the Column children array.</defense>
    </scenario>
    <scenario id="3" name="RenderFlex Overflow in Narrow Viewports">
      <attack>When criteria, quotes, or distribution columns render extensive multiline text inside a `DataTable`, cells can expand horizontally and trigger RenderFlex overflow stripes on viewports &lt; 1200px.</attack>
      <defense>All decomposed cell widgets wrap their contents in `ConstrainedBox(maxWidth: 350)` and enforce `TextOverflow.ellipsis` on unbounded textual elements.</defense>
    </scenario>
  </red_team_falsification_scenarios>

  <test_contracts>
    <test name="test_sdui_matrix_table_widget_renders_cells_without_sorting_jank" category="positive">
      <input>SduiMatrixTableWidget with 5 criteria rows and level breakdowns</input>
      <expected>Renders 4 cell sub-widgets without throwing, layout thrashing, or in-build sorting</expected>
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
      <input>List of SDUI blocks containing empty text and empty cards</input>
      <expected>Collection-if completely omits empty blocks from the element tree; zero SizedBox.shrink() nodes exist</expected>
    </test>
    <test name="test_atom_matrix_table_widget_macro_breakpoint_switching" category="boundary">
      <input>Width at 799px vs 800px</input>
      <expected>Switches between mobile linear layout and desktop tabular layout at 800px</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Dart guardrails: Assert 0 DGR002 violations in sdui_blocks_renderer.dart -->
    <action>Run guardrails: uv run python scripts/_dart_guardrails.py client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart</action>
    <!-- Targeted widget test execution -->
    <action>Run matrix table test: cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_matrix_table_widget_test.dart</action>
    <action>Run telemetry grid test: cd client_app_v2; flutter test test/features/execution/views/widgets/xai_axis_telemetry_grid_test.dart</action>
    <action>Run blocks renderer test: cd client_app_v2; flutter test test/features/execution/views/widgets/sdui_blocks_renderer_test.dart</action>
    <action>Run atom matrix table test: cd client_app_v2; flutter test test/features/execution/views/widgets/atom_matrix_table_widget_test.dart</action>
  </validation_gate>
</execution_protocol>
```
