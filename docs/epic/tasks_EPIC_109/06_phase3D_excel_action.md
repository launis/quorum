# Phase 3D: Excel Action Button (VERIFY & ENHANCE)

This plan addresses the final phase of Epic 109, ensuring the Excel Export functionality is prominently available in the Execution Report view, correctly parses backend RFC-7807 Fail-Fast exceptions, and provides strictly synchronized localized column headers.

## Proposed Changes

### Frontend / Execution Views

#### [MODIFY] [execution_report_view.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/views/execution_report_view.dart)
- Ensure the `_downloadExcel` method explicitly catches `DioException` and uses the standard RFC-7807 payload parsing (via `AppExceptionX` or explicitly extracting the server's user-friendly error message).
- **Rule Enforcement**: Ensure no frontend-side hardcoded error strings are used if the backend rejects the export. The UI must strictly render the backend's validation rejection reason.
- Enhance the Excel Export button's visibility if needed, ensuring it sits cleanly alongside the PDF download option.

### Frontend / Localization Dictionaries

#### [MODIFY] [app_fi.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_fi.arb)
- Add translation keys for Excel Export headers to ensure cross-language parity for the backend Excel generation:
  - `"excelHeaderMatrix": "Matriisi"`
  - `"excelHeaderCriterion": "Kriteerin Nimi (UI)"`
  - `"excelHeaderRule": "Tekoälyn Sääntö"`
  - `"excelHeaderVerdict": "Tuomio"`
  - `"excelHeaderScore": "Pistemäärä"`
  - `"excelHeaderExplanation": "Perustelu (Raaka)"`
  - `"layoutBlockDescriptionLabel": "Osion kuvaus (valinnainen väliotsikko)"`

#### [MODIFY] [app_en.arb](file:///c:/src/quorum/client_app_v2/lib/l10n/app_en.arb)
- Add the corresponding English translation keys for the Excel Export headers:
  - `"excelHeaderMatrix": "Matrix"`
  - `"excelHeaderCriterion": "Criterion Name (UI)"`
  - `"excelHeaderRule": "AI Rule"`
  - `"excelHeaderVerdict": "Verdict"`
  - `"excelHeaderScore": "Score"`
  - `"excelHeaderExplanation": "Explanation (Raw)"`
  - `"layoutBlockDescriptionLabel": "Section Description (optional subtitle)"`

## Verification Plan

### Automated Tests
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/l10n/ --build` to re-generate the localization keys.

### Manual Verification
- In the Execution Monitor, open a completed execution and click the "Lataa Excel" / "Download Excel" button.
- Verify the Excel export succeeds for a valid execution.
- Attempt to export an execution with zero scored atoms and verify the application displays a red Error Boundary snackbar containing the exact 400 Bad Request error string from the backend, instead of crashing or generating an empty file.
