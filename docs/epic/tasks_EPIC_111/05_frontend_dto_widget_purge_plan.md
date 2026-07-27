# Phase 1D: Frontend DTO & Widget Purge [PLACEHOLDER]

> Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L61-L65] Phase 1 (Flutter)

## Objective

Mirror the backend field deletions in the Flutter Freezed model and purge all legacy field consumption from Flutter widgets.

## Expected Target Files

1. @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart#L46-L49] — Delete `evaluativeMatrices`, `informationalMatrices`, `contentBlocks` fields
2. @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\diagnostic_scorecard_widget.dart] — Remove direct `evaluativeMatrices` / `informationalMatrices` consumption
3. @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart#L319] — Remove `evaluativeMatrices` passthrough
4. @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_view.dart#L315] — Remove `evaluativeMatrices` passthrough
5. @[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart#L71-L72] — Purge legacy `contentBlocks` fallback rendering

## Expected Verification Commands

- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/`

> [!NOTE]
> **PLACEHOLDER**: This plan requires detailed generation by re-invoking the Tier 1 Planner after the backend phases are completed, based on the updated codebase state.
