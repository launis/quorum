# Phase 1d: Frontend DTO and Initial UI Refactoring

## Overview
Remove legacy fields from `ReportDataV2Dto` in the Flutter client and refactor views (`execution_report_view.dart`, `execution_view.dart`, `diagnostic_scorecard_widget.dart`) to consume SDUI `layouts`.

## Target Files
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart]` (Modify)
- `@[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="silent_json_fallbacks">Ensure 100% strict JSON conformity. Missing data MUST crash the Freezed parser immediately.</constraint>
  <constraint invariant="frontend_zero_db_hardcoding_mandate">Flutter UI MUST NOT know about or rely on specific database record identifiers.</constraint>

  <step id="1" name="UPDATE FLUTTER REPORT DTO">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]`. Permanently remove `contentBlocks`, `evaluativeMatrices`, `informationalMatrices`, and `penaltiesApplied`.</action>
    <demolish>REMOVE: `contentBlocks`, `evaluativeMatrices`, `informationalMatrices`, `penaltiesApplied`.</demolish>
    <action>Run the flutter code generator: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build`.</action>
  </step>

  <step id="2" name="REFACTOR DIAGNOSTIC SCORECARD WIDGET">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart]`. Refactor to accept `axes` from the layout instead of top-level legacy matrices, passing it down to `AtomMatrixTableWidget`.</action>
    <action>The UI must be stripped of all conditional `scaleMax > scaleMin` formatting for scores and strictly render the pre-computed `scoreDisplayLabel` provided by the backend.</action>
  </step>

  <step id="3" name="REFACTOR EXECUTION REPORT VIEW">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart]`. Refactor the `DiagnosticScorecardWidget` instantiation to pass `axes: value.layouts.expand((l) => l.axes).toList()` instead of legacy passthrough variables.</action>
  </step>

  <step id="4" name="REFACTOR EXECUTION VIEW">
    <action>Modify `@[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart]`. Refactor the `DiagnosticScorecardWidget` instantiation to pass `axes` dynamically from the layouts.</action>
  </step>

  <step id="5" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run the flutter audit loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/`</action>
    <action>Ensure widget tests pass and no legacy UI components remain in these views.</action>
  </step>
</execution_protocol>
```
