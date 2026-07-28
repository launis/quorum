# Phase 4: Flutter UI Implementation (View-Only Parity)

Source: @[c:\src\quorum\docs\epic\EPIC_122_legacy_parity_output_profile.md#L221-L225] Phase 4: Flutter UI Implementation (View-Only Parity)

## Objective
Update the Flutter matrix rendering to enforce the "Zero Exception Mandate" by making the matrix strictly view-only. This involves removing in-place interactive atom editing (drill-downs, bottom sheets) and styling the `normalized_score` column as a green percentage pill for 100% visual parity with the PDF output.

## Target Files
- TARGET (Modify): `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart]`
- CONTEXT (Read-Only): `@[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart]`

## Execution Protocol

```xml
<execution_protocol level="2_execute">
  <constraint invariant="strict_sdui_rendering_mandate">The frontend MUST NOT contain any hardcoded business logic, layout states, or fallback UI strings for dynamic views. All dynamic content MUST be strictly driven by backend DTOs.</constraint>
  <constraint invariant="sdui_native_schizophrenia_prevention">Do not leak business logic back into the Flutter frontend.</constraint>
  <constraint invariant="design_token_absolute_rule">Exclusively use global Design Tokens (e.g., AppSpacing.p16, Theme.of(context).textTheme). ANY use of hardcoded numeric doubles for heights, widths, or padding is STRICTLY PROHIBITED.</constraint>

  <step id="4_1" name="Remove In-Place Atom Editing and Add External Link Strategy">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart]` to remove all interactive UI elements (e.g., the `IconButton` that triggers `HumanOverrideDialog`) and any associated override rendering logic inside the matrix row.</action>
    <action>Remove the `HumanOverrideDialog` import from `atom_matrix_table_widget.dart`.</action>
    <action>Note: The Epic specifies that Atom Overrides will be handled via a separate, external link (e.g., routing the user to a dedicated admin view). Since `atom_matrix_table_widget.dart` is just the view component, ensure it does not contain local edit buttons anymore. This component is now strictly view-only.</action>
    <demolish>REMOVE: `import 'package:client_app/features/execution/views/widgets/human_override_dialog.dart';`</demolish>
    <demolish>REMOVE: The `hasOverride` calculation and `overrideBox` widget rendering logic inside `_buildQuotesColumn`.</demolish>
    <demolish>REMOVE: The `IconButton` inside `_buildQuotesColumn` that calls `showDialog(...)` and its associated `ScaffoldMessenger` logic.</demolish>
    <demolish>REPLACE WITH: Simple AI evidence rendering without human override fading/boxes.</demolish>
  </step>

  <step id="4_2" name="Update Normalized Score Rendering">
    <action>Update the rendering of the `normalized_score` column in `atom_matrix_table_widget.dart` (and its mobile view) to render as a "green percentage pill" (e.g., using a `Container` with a green background and rounded corners) rather than plain blue text, for parity with the PDF template.</action>
    <action>Ensure it explicitly uses a `Container` with rounded edges matching the backend Jinja template visual design for normalized score.</action>
    <demolish>REMOVE: The plain blue text rendering for `normalized_score` in both `_buildDataTable` and `_buildMobileList`.</demolish>
    <demolish>REPLACE WITH: Green percentage pill Container styling.</demolish>
  </step>

  <step id="4_3" name="Testing &amp; Quality Gate Plan">
    <action>Run the Flutter audit loop on the modified file to ensure no compilation errors or linter warnings: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart`.</action>
  </step>
</execution_protocol>
```
