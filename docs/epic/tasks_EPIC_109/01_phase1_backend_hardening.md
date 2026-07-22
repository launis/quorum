# Phase 1: Backend Domain Models & Service Engine Hardening
Source: Epic Phase 1

## Objective
Harden the Excel export service to strictly Fail-Fast. Remove openpyxl fallback sheet generation, enforce typed AppExceptions with RFC-7807 dual-reporting, and replace hardcoded Finnish column headers with ARB translation keys.

## Target Files (Modify)
- @[c:\src\quorum\backend_v2\services\execution.py]
- @[c:\src\quorum\backend_v2\api\routers\execution\executions.py]

## Context Files (Read-Only)
- @[c:\src\quorum\backend_v2\models\v2_core.py]
- @[c:\src\quorum\client_app_v2\lib\l10n\app_en.arb]
- @[c:\src\quorum\client_app_v2\lib\l10n\app_fi.arb]

## Implementation Steps
1. In `execution.py` (`get_execution_export_bytes`):
   - Harden the method to strictly Fail-Fast. Remove existing openpyxl empty fallback sheet generation.
   - If `execution.step_states` has no atoms or `status != PASSED`, throw an `AppException(status_code=400)`.
   - Remove the `try/except Exception` catch-all, replacing it with strict typed `except AppException` and RFC-7807 dual-reporting (`logger.error`).
   - Replace `getattr(q, "verified_source_ids", None)` and `getattr(q, "unverified_aliases", None)` with direct Pydantic DTO attribute access.
   - Extract `target_locale` securely from `execution.metadata["target_locale"]`.
   - Read the Flutter localization files (`client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb`) using `json.load()` as the single source of truth for string resolution.
   - Replace hardcoded Finnish column headers (e.g., `"Matriisi"`, `"Kriteerin Nimi (UI)"`, `"Tekoälyn Sääntö"`) with their respective `.arb` keys (e.g., `excelHeaderMatrix`, `excelHeaderCriterion`).
2. In `executions.py` (`/api/v2/executions/{execution_id}/export`):
   - Ensure it does NOT add a `locale` query parameter. Rely solely on the `target_locale` bound to the execution's metadata.
   - Verify proper `Content-Disposition` headers are set.

## Testing & Quality Gate Plan
- Strict unit tests: Update `tests/unit/services/test_execution.py` to assert the 400 Bad Request on empty states.
- Run Universal Quality Gate (Backend Audit Loop):
  `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test`
- Run Universal Quality Gate (Backend Audit Loop):
  `uv run python scripts/backend_audit_loop.py backend_v2/api/routers/execution/executions.py --test`

## Documentation & Knowledge Item Mandate
- No new SSOT to update, but ensure no "duct-tape" code rules are broken.
