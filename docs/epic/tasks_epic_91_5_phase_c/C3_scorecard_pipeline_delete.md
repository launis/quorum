# C3 — Scorecard Pipeline Delete

## Goal
Remove the entire `/scorecard` endpoint pipeline — backend endpoint, service method, Pydantic model, Flutter API client method, Riverpod provider, and the async wrapper widget. The pipeline is completely redundant because `ReportDataDto` already contains `evaluativeMatrices` and `informationalMatrices` via the unified `build_report_dto()` transformer.

## Proposed Changes

### backend_v2/api/routers/execution/
#### [MODIFY] executions.py
1. Remove the `get_execution_scorecard` endpoint (`/{execution_id}/scorecard`) — lines 255-265.
2. Remove `ScorecardResponseDTO` from the import block (line 21). Leave the other imports untouched.

### backend_v2/services/
#### [MODIFY] execution.py
1. Remove the `get_scorecard_dto` method (lines 1204-1241).
2. Remove `ScorecardResponseDTO` from the top-level import (line 51). The inline import at line 1233 disappears with the method.

### backend_v2/models/
#### [MODIFY] v2_core.py
1. Remove the `ScorecardResponseDTO` class definition (lines 1106-1115).
2. Remove `"ScorecardResponseDTO"` from the `__all__` export list (line 82).

> **Rationale**: Leaving a dead Pydantic model violates `single_source_of_truth_mandate` and `the_no_legacy_mandate`. All consumers are deleted in this task.

### client_app_v2/lib/core/api/
#### [MODIFY] execution_client.dart
Remove the `getScorecard()` method (lines 73-79). This is the HTTP client method that calls the now-deleted `/scorecard` endpoint.

### client_app_v2/lib/features/execution/
#### [DELETE] providers/scorecard_provider.dart
Remove the Riverpod provider that fetches the separate scorecard.

#### [DELETE] providers/scorecard_provider.g.dart
Remove the generated Riverpod code. (Will also be cleaned by `build_runner`, but explicit deletion prevents stale file confusion.)

#### [DELETE] views/widgets/async_scorecard_widget.dart
Remove the widget that consumes the scorecard provider.

#### [MODIFY] views/execution_view.dart
1. Remove the import of `async_scorecard_widget.dart` (line 12).
2. Remove the `SliverToBoxAdapter` containing `AsyncScorecardWidget(executionId: widget.executionId)` (line 277-279).

> **Note**: `DiagnosticScorecardWidget` intentionally survives — C4 will rewire it to consume data from the unified `ReportDataDto` pipeline instead.

## Verification Plan

### Backend
- Run `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/execution/ --test`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test`.

### Frontend
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`.
- Verify `dart analyze client_app_v2/lib/` reports zero errors related to scorecard imports.

---
# Session Handover Context
## Achieved
- Prepared C3 Scorecard Pipeline Delete plan.
- Red-teamed: discovered 4 missing files that would have caused build failures.
## Learned
- The `/scorecard` endpoint is redundant as all data is provided in `ReportDataDto`.
- `execution_view.dart` actively imports and instantiates `AsyncScorecardWidget` — must be cleaned.
- `execution_client.dart` has a `getScorecard()` method that must be removed.
- `ScorecardResponseDTO` in `v2_core.py` must be deleted (not just orphaned) per No Legacy Mandate.
- `DiagnosticScorecardWidget` survives — it will be rewired in C4.
## Remaining
- Execute C3.
