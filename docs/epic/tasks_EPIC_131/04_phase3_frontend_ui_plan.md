<execution_protocol>
## Core Directives
1. **Zero Behavioral Change Mandate**: Enforce structural refactoring ONLY.
2. **Context Amnesia Prevention**: All targets are bounded using `@-references`.
3. **Fail-Fast Firewall**: Never use `SizedBox.shrink()` for missing fields. 

## Implementation Plan

### Step 3.2: Update SduiBlocksRenderer
**Target**: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\sdui_blocks_renderer.dart]`
- Refactor the current `if (block is ...)` chain into a native Dart 3 exhaustive `switch (block)` expression. Do NOT use a `default` wildcard branch.
- Add `switch` cases for the 4 new `SduiBlockDTO` variants:
  - `SduiRadarChartBlock` → `LogicRadarChart(axes: block.axes)`
  - `SduiScatterPlotBlock` → `LogicMatrixChart(xAxis: block.axes[0], yAxis: block.axes[1], zAxis: ...)`
  - `SduiMatrixTableBlock` → matrix summary table widget
  - `SduiMetrics1DBlock` → `Column(children: block.axes.map((axis) => SduiBlocksRenderer(blocks: axis.innerSduiBlocks)).toList())`

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
- Remove the `PresetView.complex3d` dropdown option.

### Step 3.8: Regenerate Freezed/JsonSerializable Files
**Action**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`

### Step 3.9: Flutter Tests
**Targets**: 
- `@[c:\src\quorum\client_app_v2\test\features\studio\models\output_profile_test.dart]`
- `@[c:\src\quorum\client_app_v2\test\features\execution\views\widgets\sdui_blocks_renderer_test.dart]`
- Add negative tests checking for `CheckedFromJsonException` on invalid SDUI structures.
- Add negative test checking that `ReportDataDto.fromJson` throws a fatal error if the payload contains the deleted `layouts` key.
- Verify that `SduiBlocksRenderer` native exception bubbles up on malformed charts without `SizedBox.shrink()`.
</execution_protocol>
