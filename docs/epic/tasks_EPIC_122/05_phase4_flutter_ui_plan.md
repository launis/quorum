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
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart]` to remove all interactive UI elements (specifically the `IconButton` that triggers `HumanOverrideDialog`).</action>
    <action>Remove the `HumanOverrideDialog` import from `atom_matrix_table_widget.dart`.</action>
    <action>Note: The Epic specifies that Atom Overrides will be handled via a separate, external link. The matrix is now view-only, meaning we cannot edit it here. HOWEVER, you MUST preserve the read-only visual rendering of the `overrideBox` and the `hasOverride` calculation so users can still see that a human overrode the AI. Do NOT hide the data.</action>
    <demolish>REMOVE: `import 'package:client_app/features/execution/views/widgets/human_override_dialog.dart';`</demolish>
    <demolish>REMOVE: ONLY the `IconButton` inside `_buildQuotesColumn` that calls `showDialog(...)` and its associated `ScaffoldMessenger` logic.</demolish>
    <demolish>PRESERVE: The `hasOverride` calculation, fading logic, and `overrideBox` widget rendering, as they are required for read-only visibility.</demolish>
  </step>

  <step id="4_2" name="Update Normalized Score Rendering">
    <action>Update the rendering of the `normalized_score` column in `atom_matrix_table_widget.dart` (and its mobile view) to render as a percentage pill rather than plain blue text, for parity with the PDF template.</action>
    <action>CRITICAL TOKEN COMPLIANCE: Do NOT use hardcoded colors like `Colors.green` or magic padding numbers. You MUST use semantic theme tokens (e.g., `theme.colorScheme.tertiaryContainer` for the background and `theme.colorScheme.onTertiaryContainer` for text, assuming tertiary maps to success/green in this app's semantic palette, or whatever the local equivalent is) and global spacing tokens (if applicable).</action>
    <action>Graceful Fallback: Ensure the rendering handles a null `normalized_score` safely without crashing or rendering an empty green box.</action>
    <demolish>REMOVE: The plain blue text rendering for `normalized_score` in both `_buildDataTable` and `_buildMobileList`.</demolish>
    <demolish>REPLACE WITH: Percentage pill Container styling strictly utilizing Theme context colors and avoiding magic numbers.</demolish>
  </step>

  <step id="4_3" name="Testing &amp; Quality Gate Plan">
    <action>Update the associated widget tests to ensure the `IconButton` is verified as removed, and that a null `normalized_score` falls back correctly (Negative Path Testing).</action>
    <action>Run the Flutter audit loop on BOTH the modified widget file and the test file to ensure no compilation errors or linter warnings: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart`.</action>
    <action>Execute the test file to guarantee coverage does not drop.</action>
  </step>
</execution_protocol>
```
