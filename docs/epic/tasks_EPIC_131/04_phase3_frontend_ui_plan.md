<execution_protocol>
## Core Directives
1. **Zero Behavioral Change Mandate**: Enforce structural refactoring ONLY.
2. **Context Amnesia Prevention**: All targets are bounded using `@-references`.
3. **Fail-Fast Firewall**: Never use `SizedBox.shrink()` for missing fields. 

## Implementation Plan

### Step 3.2: Update SduiBlocksRenderer
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\sdui_blocks_renderer.dart]`
- Refactor the current `if (block is ...)` chain into a native Dart 3 exhaustive `switch (block)` expression. Do NOT use a `default` wildcard branch.
- Add `switch` cases for ALL 15 `SduiBlockDTO` variants to prevent Dart compiler errors:
  - `SduiRadarChartBlock` → helper method `_buildChartWithTitle(context, block.title, LogicRadarChart(axes: block.axes))`
  - `SduiScatterPlotBlock` → helper method `_buildChartWithTitle(context, block.title, LogicMatrixChart(xAxis: block.axes[0], yAxis: block.axes[1], zAxis: block.axes.length > 2 ? block.axes[2] : null))`
  - `SduiMetrics1DBlock` → helper method `_buildChartWithTitle(context, block.title, Column(children: block.axes.map((axis) => MatrixRowItemWidget(matrix: axis)).toList()))`
  - `SduiMatrixTableBlock` → `SduiMatrixTableWidget(block: block)`
  - Existing supported blocks: `SduiAccordionBlock`, `SduiHeaderBlock`, `SduiAlertBoxBlock`, `SduiGridBlock`, `SduiMarkdownBlock`, `SduiParagraphBlock` → Map to their existing logic.
  - Unsupported blocks (`SduiBulletListBlock`, `SduiHeroInsightBlock`, `SduiQuoteCardBlock`, `SduiWarningCardBlock`, `SduiNACardBlock`) → `throw AppException.validation('Unsupported block type in SduiBlocksRenderer.');`
- Add a private helper `Widget _buildChartWithTitle(BuildContext context, I18nText? title, Widget chart)` that renders the title (using `title.get(Localizations.localeOf(context).languageCode)`) as a `Text` widget with `headlineSmall` styling, followed by the `chart`.

### Step 3.2.1: Create SduiMatrixTableWidget
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\sdui_matrix_table_widget.dart]`
- Create a new widget `SduiMatrixTableWidget` that accepts `SduiMatrixTableBlock block`.
- Extract the `DataTable` rendering logic currently residing in `report_renderer_v2_widget.dart` (lines 301-440) into this new widget.
- Ensure the extracted logic references `block.axes`, `block.matrixVisibleColumns`, and `block.matrixColumnLabels`.
- Ensure `block.title` is rendered above the table if it exists.
### Step 3.3: Remove layouts from ReportDataDto
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]`
- Delete `@Default([]) List<ReportLayoutDto> layouts,`
- Remove import `import 'report_layout_dto.dart';`

### Step 3.4: Delete ReportLayoutDto File
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart]`
- **DELETE FILE** via terminal command (also delete `.freezed.dart` and `.g.dart`).

### Step 3.5: Update Report Renderer
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`
- Remove the entire `for (final layout in payload.layouts)` loop.
- Ensure the renderer processes the full `payload.innerSduiBlocks` list (which already uses `SduiBlocksRenderer`).

### Step 3.6: Update Studio Editor Views
**Targets**:
- `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\studio\views\blueprint_editor_view.dart]`
- Replace `PresetView` dropdown with the retained `PresetView` enum.
- Remove the legacy fallback `PresetView.matrixSummary` dropdown option.

### Step 3.8: Regenerate Freezed/JsonSerializable Files
**Action**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Step 3.9: Flutter Tests
**Targets**: 
- `@[c:\src\quorum\client_app_v2\test\features\studio\models\output_profile_test.dart]`
- `@[c:\src\quorum\client_app_v2\test\features\execution\views\widgets\sdui_blocks_renderer_test.dart]` (Create this file if it does not exist)
- Add negative tests checking for `CheckedFromJsonException` on invalid SDUI structures.
- Add negative test checking that `ReportDataDto.fromJson` throws a fatal error if the payload contains the deleted `layouts` key.
- Verify that `SduiBlocksRenderer` throws `AppException` on unsupported or malformed charts, avoiding `SizedBox.shrink()`.
</execution_protocol>
