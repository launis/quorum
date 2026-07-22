# Phase 3D: Excel Action Button (VERIFY & ENHANCE)

This plan addresses the final phase of Epic 109, ensuring the Excel Export functionality is prominently available in the Execution Report view, correctly parses backend RFC-7807 Fail-Fast exceptions, and provides strictly synchronized localized column headers.

## Proposed Changes

### Frontend / Execution Views

#### [MODIFY] [execution_report_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/execution_report_view.dart)
- Because `_downloadExcel` uses `ResponseType.bytes`, an HTTP 400 response from the backend will be returned as raw bytes in `e.response.data`. You MUST explicitly catch the `DioException` in the `catch (e, st)` block, decode the byte array using `utf8.decode(e.response!.data)` and `jsonDecode()`, and extract the RFC-7807 `detail` string.
- Display this explicitly extracted `detail` string in the `SnackBar` to ensure the exact backend reason (e.g., "Empty execution: No scored atoms") is shown to the user.
- Do NOT rely entirely on `AppExceptionX` since it will fail to parse raw bytes.
- Ensure the imports `dart:convert` is present.

### Frontend / Localization Dictionaries
- *(Note: Verified during Tier 0 analysis that all required ARB keys like `excelHeaderAiRule` and `excelHeaderResultStatus` were already implemented in Phase 1. No `.arb` modifications are needed in this phase.)*

## Verification Plan

### Automated Tests
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/l10n/ --build` to re-generate the localization keys.

### Manual Verification
- In the Execution Monitor, open a completed execution and click the "Lataa Excel" / "Download Excel" button.
- Verify the Excel export succeeds for a valid execution.
- Attempt to export an execution with zero scored atoms and verify the application displays a red Error Boundary snackbar containing the exact 400 Bad Request error string from the backend, instead of crashing or generating an empty file.
