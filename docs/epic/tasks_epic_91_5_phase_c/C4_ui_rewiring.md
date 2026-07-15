# C4 — UI Rewiring

## Goal
Re-integrate the diagnostic scorecard directly into the execution view, wired to the unified `ReportDataDto` pipeline. After C3 deleted the `AsyncScorecardWidget` (which fetched from the separate `/scorecard` endpoint), the scorecard no longer renders. C4 restores it by passing data directly from `record.reportData`.

## Pre-Conditions
- C2 completed: `matrix_scorecard_dto.dart` exists, `scorecard_dto.dart` is a proxy.
- C3 completed: `AsyncScorecardWidget` deleted, `scorecard_provider.dart` deleted, `execution_view.dart` no longer imports/uses them.

## Proposed Changes

### client_app_v2/lib/features/execution/views/
#### [MODIFY] execution_view.dart
In the `if (record.reportData != null) ...[` block, **ADD** a new `SliverToBoxAdapter` after `ReportRendererV2Widget` that renders the scorecard directly from the unified DTO:

```dart
SliverToBoxAdapter(
  child: DiagnosticScorecardWidget(
    executionId: widget.executionId,
    evaluativeMatrices: record.reportData!.evaluativeMatrices ?? [],
    informationalMatrices: record.reportData!.informationalMatrices ?? [],
    visibleColumns: record.reportData!.matrixVisibleColumns,
  ),
),
```

**Required import** (add if not already present):
```dart
import 'package:client_app/features/execution/views/widgets/diagnostic_scorecard_widget.dart';
```

> **Note**: `DiagnosticScorecardWidget` does NOT need modification — it already accepts `List<MatrixScorecardRowDto>` and `List<String> visibleColumns` directly. No changes to its constructor or interface are required.

#### [MODIFY] widgets/report_renderer_v2_widget.dart
Remove the stale `// [BLOCKED]` comment block (lines 43-47) that says:
> "Architectural Contradiction: Phase 1 models (ReportDataDto) do not contain evaluativeMatrices..."

This contradiction was resolved by C1 when these fields were added to `ReportDataDto`. The comment is now misleading.

### NOT Modified (Explicitly Scoped Out)

- **`diagnostic_scorecard_widget.dart`**: Already has the correct interface. No changes needed.
- **`scorecard_dto.dart` proxy sunset**: Deferred to the “Proxy Sunset & Consumer Migration” quality gate.
- **`XAIEvidenceBox` integration**: The `mcpToolAudit` data is available in `ReportDataDto` but XAI integration is deferred to a future task.

## Verification Plan
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/ --build`.
- Verify `dart analyze client_app_v2/lib/features/execution/views/` reports zero errors.
- Manually confirm that the scorecard renders with data from `ReportDataDto` (same data, no separate API call).

---
# Session Handover Context
## Achieved
- Prepared C4 UI Rewiring plan.
- Red-teamed: eliminated task overlap with C3, corrected false modification target.
## Learned
- `DiagnosticScorecardWidget` already has the correct interface (`List<MatrixScorecardRowDto>`).
- `report_renderer_v2_widget.dart` has a stale `[BLOCKED]` comment that must be cleaned.
- The data path is: `record.reportData!.evaluativeMatrices` → `DiagnosticScorecardWidget`.
- `visibleColumns` maps to `record.reportData!.matrixVisibleColumns`.
## Remaining
- Execute C4.
