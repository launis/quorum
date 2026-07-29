# Phase 6: Consumer Logic (Frontend & PDF Rendering)

## Objective
Wire the Flutter and Jinja templates to consume `inner_sdui_blocks`, and delete all legacy XAI widget code, `grouped_extensions` panels, and hardcoded `global_synthesis` UI logic.

## Target Files
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\matrix_row_item_widget.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart]` (Delete)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_axis_telemetry_grid.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]` (Modify)
- `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="universal_fail_fast">Do not leave dead code paths. If a field or parameter is removed, remove all references.</constraint>
  <constraint invariant="strict_icu_markdown_parity">The PDF template MUST remain devoid of manual HTML formatting for specific data fields, relying entirely on the `render_sdui_blocks()` macro.</constraint>

  <step id="1" name="FLUTTER: CONSUME INNER_SDUI_BLOCKS">
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\matrix_row_item_widget.dart]`, pass `row.innerSduiBlocks` directly to the `SduiRenderer` within the expandable container.</action>
    <action>Ensure that the new `innerSduiBlocks` fully replace any legacy rendering calls for row-level extensions.</action>
  </step>

  <step id="2" name="FLUTTER: XAI EXTENSIONS BOX DELETION">
    <action>Delete the file `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_extensions_box.dart]` completely.</action>
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`, remove all imports and usages of `XAIExtensionsBox`.</action>
  </step>

  <step id="3" name="FLUTTER: TELEMETRY GRID CLEANUP">
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\xai_axis_telemetry_grid.dart]`, remove the `groupedExtensions` constructor parameter.</action>
    <action>Delete the hardcoded UI rendering logic for `riskFlag`, `emotionalSentiment`, and `theoryLink`.</action>
    <action>Update the rendering of `confidence` to trigger simply on `axis.confidence != null`.</action>
  </step>

  <step id="4" name="FLUTTER: GLOBAL SYNTHESIS UI REFACTORING &amp; DTO CLEANUP">
    <action>Remove all hardcoded UI logic in Flutter that previously parsed the `globalSynthesis` object to render the header (if not already removed).</action>
    <action>In `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]`, delete the `groupedExtensions` field entirely to match the Python `ReportDataDTO` changes from Phase 5.</action>
  </step>

  <step id="5" name="JINJA: REPORT TEMPLATE REFACTORING">
    <action>In `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`, delete the hardcoded HTML block for `report_data.global_synthesis.executive_summary` and `user_role`.</action>
    <action>Delete the entire global extensions panel (the `{% if report_data.grouped_extensions %}` block).</action>
    <action>In the matrix layout loop, invoke `{{ render_sdui_blocks(axis.inner_sdui_blocks) }}`.</action>
    <action>Refactor the `confidence` rendering inside the matrix axis loop to simply check `{% if axis.confidence is not none %}`. Render `axis.confidence` in its own visual block BEFORE the `render_sdui_blocks(axis.inner_sdui_blocks)` macro call.</action>
    <action>Ensure the top of the PDF dynamically loops through `report_data.sections` instead of specific synthesis fields.</action>
  </step>

  <step id="6" name="TESTING &amp; QUALITY GATE PLAN">
    <action>Execute: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets client_app_v2/lib/features/execution/models --build`</action>
    <action>Execute: `uv run python scripts/backend_audit_loop.py backend_v2/templates/ --test` (to verify Jinja syntax parsing).</action>
    <action>Use `grep_search` to verify ZERO references to `grouped_extensions` or `groupedExtensions` remain in the Flutter codebase and Jinja templates.</action>
    <action>Commit changes atomically upon success.</action>
  </step>
</execution_protocol>
```
