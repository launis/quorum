# C5 — Controller Updates

## Goal
Verify and finalize the controller layer for the unified `ReportDataDto` pipeline. The original plan assumed controllers needed updating, but both `ExecutionController._performHeavyFetch()` and `ReportController.build()` already parse `ReportDataDto` off-main-thread and do NOT call the deleted `/scorecard` endpoint.

The remaining work is:
1. Add `DiagnosticScorecardWidget` to `execution_report_view.dart` (which uses `ReportController` but currently lacks scorecard rendering).
2. (Optional) Fix a pre-existing double-serialization inefficiency in `ExecutionController._performHeavyFetch()`.

## Pre-Conditions
- C1 completed: `ReportDataDto` has `evaluativeMatrices`, `informationalMatrices`, `matrixVisibleColumns`.
- C3 completed: `/scorecard` endpoint and `getScorecard()` client method deleted.
- C4 completed: `execution_view.dart` renders `DiagnosticScorecardWidget` from `record.reportData`.

## Controllers Already Correct (Verification Only)

### ExecutionController._performHeavyFetch() — NO CHANGES NEEDED
Location: [execution_controller.dart:L176-227](file:///c:/src/quorum/client_app_v2/lib/features/execution/controllers/execution_controller.dart#L176-L227)
- Already calls `client.renderExecution(executionId)` (not scorecard).
- Already uses `ReportDataDto.parseInBackground(jsonEncode(renderData))` for isolate parsing.
- Already merges into `state.value!.copyWith(reportData: reportData)`.

### ReportController.build() — NO CHANGES NEEDED
Location: [report_controller.dart:L22-61](file:///c:/src/quorum/client_app_v2/lib/features/execution/controllers/report_controller.dart#L22-L61)
- Already calls `client.renderExecution(executionId, lang: lang, variant: variant)`.
- Already uses `safeIsolateRun(() => ReportDataDto.fromJson(rawData))` for isolate parsing.
- Already handles 202 polling with max attempts.

## Proposed Changes

### client_app_v2/lib/features/execution/views/
#### [MODIFY] execution_report_view.dart
`ExecutionReportView` renders the standalone report page via `ReportController`. After C4, the live `execution_view.dart` shows the scorecard, but this report view does NOT. Add `DiagnosticScorecardWidget` below `ReportRendererV2Widget` in the `AsyncData` branch:

```dart
AsyncData(:final value) => SingleChildScrollView(
  child: Column(
    children: [
      ReportRendererV2Widget(
        payload: value,
        executionId: widget.executionId,
      ),
      DiagnosticScorecardWidget(
        executionId: widget.executionId,
        evaluativeMatrices: value.evaluativeMatrices ?? [],
        informationalMatrices: value.informationalMatrices ?? [],
        visibleColumns: value.matrixVisibleColumns,
      ),
    ],
  ),
),
```

**Required import** (add if not already present):
```dart
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
```

### client_app_v2/lib/features/execution/controllers/
#### [MODIFY] execution_controller.dart (Optional Performance Fix)
In `_performHeavyFetch()`, the current code does:
```dart
final reportData = await ReportDataDto.parseInBackground(
  jsonEncode(renderData),  // Map → String (unnecessary)
);
```
This double-serializes: `Map → String → Map → DTO`. Replace with the more efficient:
```dart
final reportData = await safeIsolateRun(
  () => ReportDataDto.fromJson(renderData),
);
```
This is a performance optimization, not a correctness fix. It aligns `ExecutionController` with the pattern already used by `ReportController`.

> **Note**: Requires adding `import 'package:client_app/core/utils/safe_isolate.dart';` if not already present.

## NOT Modified (Explicitly Scoped Out)

- **`report_controller.dart`**: Already correct. No changes needed.
- **Stale comments** (e.g., `// Epic 14:` at L185): Deferred to Tier 2 Hardening.

## Verification Plan
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/controllers/ --build`.
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/ --build`.
- Verify `dart analyze client_app_v2/lib/features/execution/` reports zero errors.
- Manually verify that both `ExecutionView` (live SSE) and `ExecutionReportView` (standalone) render the scorecard.

---
# Session Handover Context
## Achieved
- Prepared C5 Controller Updates plan.
- Red-teamed: discovered C5 was a no-op — both controllers already use ReportDataDto with isolate parsing.
## Learned
- `_performHeavyFetch` is in `ExecutionController`, NOT `ReportController`.
- Both controllers already parse `ReportDataDto` off-main-thread.
- `execution_report_view.dart` uses `ReportController` but lacks scorecard rendering.
- Double-serialization (`jsonEncode` → `parseInBackground`) is an unnecessary perf hit.
## Remaining
- Execute C5.

