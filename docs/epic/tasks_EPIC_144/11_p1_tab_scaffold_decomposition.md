# Phase 1-B: 3-Tab Scaffold Decomposition

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 1, "Tab Architecture & UI Scaffold" (L368-L430) and 6-Step Pipeline Step 5 (L256-L260)
**Scope:** Frontend Flutter/Dart views only

**Overview:** Decompose the 856-line monolithic `output_profile_crud_view.dart` into a 3-tab `TabBarView` architecture: General Tab, Scoring & Visualization Tab, and Layouts Tab. Each extracted tab widget MUST be ≤200 lines per the God Code Prevention mandate.

**Target Files:**
- `[MODIFY]` `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]`
- `[NEW]` `@[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]`

**Context Files (Read-Only):**
- `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` — Form state controller
- `[NEW from Plan 10]` `client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart` — Golden Master baseline (Plan 10)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 10 (Golden Master Baseline) is complete — characterization tests pass green.</action>
    <action>Look forward: Verify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] is still the monolithic ~856-line file and has NOT been decomposed yet.</action>
    <constraint>If Golden Master tests do not pass, STOP. Do NOT decompose without a behavioral safety net.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/ — Do NOT touch any Python files</file>
    <file>client_app_v2/lib/features/studio/controllers/ — Do NOT modify controllers in this plan</file>
    <file>client_app_v2/lib/features/studio/models/ — Do NOT modify Freezed models (already done in Plan 07)</file>
  </anti_targets>

  <dod_checklist>
    <item>output_profile_crud_view.dart reduced to a TabBar/TabBarView shell ≤200 lines.</item>
    <item>[NEW] profile_general_tab.dart contains profile identity fields (name, description, workflow, settings) — ≤200 lines.</item>
    <item>[NEW] profile_scoring_tab.dart contains scoring configuration (strictness, scoring_strategy, display_scale, max_extension_items) — ≤200 lines.</item>
    <item>[NEW] profile_layouts_tab.dart contains layout editor and target_block_order configuration — ≤200 lines.</item>
    <item>Golden Master characterization tests from Plan 10 still pass green (behavioral parity maintained).</item>
    <item>Flutter analyze reports zero new lints in the modified/new files.</item>
  </dod_checklist>

  <step id="1" name="ANALYZE MONOLITHIC VIEW STRUCTURE">
    <action>Read @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] in full (856 lines). Map the widget tree to identify which form fields belong to each tab:

**Tab 1 - General:** Profile name, description, workflow selector, preset_view, text_delivery_mode, synthesis toggle, preamble_text, tone_instruction.
**Tab 2 - Scoring & Visualization:** display_scale, scoring_strategy, strictness_level, max_extension_items, custom scale bounds.
**Tab 3 - Layouts:** OutputLayoutBlock editor, target_block_order drag-and-drop/chips, matrix_column_labels, matrix_visible_columns.

Document exact line ranges for each extraction.</action>
    <constraint>Do NOT modify any code. This is analysis only.</constraint>
  </step>

  <step id="2" name="EXTRACT GENERAL TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_general_tab.dart]:
```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Tab 1: Profile identity, workflow selection, and synthesis configuration.
class ProfileGeneralTab extends ConsumerWidget {
  const ProfileGeneralTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Extract form fields from output_profile_crud_view.dart
    // Profile name TextField
    // Description TextField
    // Workflow selector dropdown
    // PresetView selector
    // TextDeliveryMode selector
    // Synthesis toggle + SynthesisConfigDTO editor
    // Preamble text
    // Tone instruction
  }
}
```
Use `ref.watch()` to read form state from the existing Riverpod providers. Do NOT create new state management — reuse the existing controller's form state.</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
    <constraint invariant="zero_behavioral_change">The extracted form fields MUST render identically to their current positions in the monolithic view. No visual or functional changes permitted.</constraint>
  </step>

  <step id="3" name="EXTRACT SCORING TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_scoring_tab.dart]:
```dart
/// Tab 2: Scoring & Visualization configuration.
class ProfileScoringTab extends ConsumerWidget {
  const ProfileScoringTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // DisplayScale selector (using DisplayScale enum from enums.dart)
    // ScoringStrategy selector
    // Strictness level slider/input
    // MaxExtensionItems slider (using SystemUiConstraints enum bounds)
    // Custom scale bounds (visible only when DisplayScale.custom selected)
  }
}
```
The `maxExtensionItems` slider MUST use `SystemUiConstraints.maxExtensionItemsSliderMin.value` and `SystemUiConstraints.maxExtensionItemsSliderMax.value` for its range bounds.</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
  </step>

  <step id="4" name="EXTRACT LAYOUTS TAB">
    <action>Create [NEW] @[client_app_v2/lib/features/studio/views/widgets/profile/tabs/profile_layouts_tab.dart]:
```dart
/// Tab 3: Output layout configuration and target block ordering.
class ProfileLayoutsTab extends ConsumerWidget {
  const ProfileLayoutsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // OutputLayoutBlock list editor (existing layout_editor_card.dart widgets)
    // target_block_order configuration
    // Matrix column labels
    // Matrix visible columns
  }
}
```</action>
    <constraint invariant="200_line_cap">This file MUST be ≤200 lines.</constraint>
  </step>

  <step id="5" name="REFACTOR CRUD VIEW TO TAB SHELL">
    <action>Modify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] to become a thin TabBar/TabBarView shell:
1. Add `DefaultTabController(length: 3, ...)` wrapping the existing form scaffold.
2. Add a `TabBar` with 3 tabs: "General", "Scoring", "Layouts" (use l10n keys).
3. Replace the monolithic form body with a `TabBarView` containing `ProfileGeneralTab()`, `ProfileScoringTab()`, `ProfileLayoutsTab()`.
4. Keep the AppBar with save/cancel actions, form key, and any shared form state in the parent shell.
5. DELETE all extracted form field widgets from this file.</action>
    <constraint invariant="200_line_cap">The refactored file MUST be ≤200 lines.</constraint>
    <constraint invariant="zero_behavioral_change">The save/cancel flow, form validation, and data persistence MUST remain unchanged.</constraint>
  </step>

  <step id="6" name="VERIFY GOLDEN MASTER PARITY">
    <action>Re-run the Golden Master characterization tests from Plan 10:
`uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test`</action>
    <constraint>ALL Golden Master tests MUST still pass green. Any failure indicates a behavioral change that MUST be fixed before proceeding.</constraint>
  </step>

  <step id="7" name="LINE COUNT VERIFICATION">
    <action>Verify all files satisfy the ≤200 line cap:
```powershell
Get-Content client_app_v2\lib\features\studio\views\output_profile_crud_view.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_general_tab.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_scoring_tab.dart | Measure-Object -Line
Get-Content client_app_v2\lib\features\studio\views\widgets\profile\tabs\profile_layouts_tab.dart | Measure-Object -Line
```</action>
    <constraint invariant="200_line_cap">ALL 4 files MUST report ≤200 lines. If any exceeds 200, further decompose into sub-widgets.</constraint>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/output_profile_crud_view.dart --build</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test — Golden Master parity</check>
    <check>All 4 target files ≤200 lines</check>
    <check>flutter analyze reports zero new lints in modified/new files</check>
  </validation_gate>
</execution_protocol>
```
