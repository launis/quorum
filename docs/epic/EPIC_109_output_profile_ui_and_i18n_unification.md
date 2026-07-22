# EPIC 109: Output Profile UI and i18n Unification

## 1. Goal Description & Background (Objective & Problem Statement)
The current Output Profile configuration in the Studio UI suffers from visual clutter, inconsistent internationalization (i18n) handling, and missing section-level synthesis features. Concurrently, the Excel export functionality crashes when encountering executions with zero scored atoms. 

This Epic unifies the Studio Workflow Top Navigation into a strict 3-tab layout, restructures the Output Profile Admin UI into clear sub-tabs, standardizes bilingual (`fi`/`en`) support across section templates, restores the Executive Summary binding in `seed_data.json`, and hardens the Excel export service to enforce strict Fail-Fast boundaries on empty execution states.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **Visual Clutter in Output Profile Editor**: Moving away from the monolithic scrollable form. The old monolithic profile editor view will be structurally deprecated in favor of a 3-tab architecture (Perustiedot, XAI, Raporttipohjat).
- **Hardcoded Single-Language Text Fields**: Deprecating raw string inputs for UI titles/descriptions in favor of `I18nTextField` widgets with explicit localization boundaries (`fi`, `en`).

### Retained SSOT Invariants (`What We Will RETAIN`)
- **Form State Preservation**: The Riverpod `workflowFormProvider` will remain the SSOT for transient form state to prevent data loss when switching sub-tabs.
- **Excel Export Structure**: Retaining the two-sheet architecture (`Yhteenveto` and `Raakadata`), but adding safety boundaries.
- **Seed Data Root Architecture**: `seed_data.json` remains the root immutable state for database seeding.

### Compliance & Modernity Gates
1. **Zero Legacy State Support Mandate**: Re-seeding required via `uv run python backend_v2/seed/run_seed.py local`.
2. **Pydantic Strictness**: `ConfigDict(strict=True, extra='forbid')` must be enforced on all modified backend DTOs.
3. **Cross-Domain DTO Parity**: Any changes to `OutputLayoutBlock` or i18n structures in Python MUST be strictly mirrored in Dart Freezed models, verified via `flutter_audit_loop.py --build`.
4. **RFC-7807 Dual-Reporting**: If Excel export catches an unexpected data shape or `ReportDataDTO` generation fails, it must NOT use a generic `try/except Exception` catch-all. It must catch typed `AppException`s and log a structured error via RFC-7807.
5. **Fail-Fast Boundary (Zero Duct-Tape)**: If an execution lacks data (no scorecard atoms) or is not in a PASSED state, the Excel export MUST NOT generate empty formatted fallback sheets. It must Fail-Fast and throw an `AppException(status_code=400)` rejecting the export entirely, preventing silent failures and "Ei atomeja löytynyt" hallucinated exports.

### Producer-Consumer Integration Check
- **Producer (Seed/Backend)**: `seed_data.json` and `blueprint.py` must reliably generate and serve bilingual section titles/descriptions.
- **Consumer (Flutter/UI)**: `layout_editor_card.dart` and the Report Viewer must correctly parse, edit, and render the localized SDUI payload without breaking on unrecognized keys.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 0: Seed Data & Database Prerequisite / Migration
- Modify @[c:\src\quorum\backend_v2\seed\seed_data.json#L9110-L9130] (specifically profile `prf_5d6e7f8091a2b3c4` / `holistic_audit`):
  - Populate `preamble_text` with localized `fi`/`en` intro text.
  - Set `synthesis_block_id: "blk_8f7e6d5c4b3a2019"` in `layouts[0].synthesis` to bind the executive summary layout.
  - Ensure section layout `preset_view` (snake_case — matching seed JSON convention), `title`, and `description` objects contain valid `fi` and `en` dictionaries.
  - Update `allowed_exports` arrays to include `"xlsx"` alongside existing `"pdf"` where Excel export is intended.
- Execute local re-seed: `uv run python backend_v2/seed/run_seed.py local`.

### Phase 1: Backend Domain Models & Service Engine Hardening
- Modify @[c:\src\quorum\backend_v2\services\execution.py] & @[c:\src\quorum\backend_v2\api\routers\execution\executions.py]:
  - Harden `get_execution_export_bytes()` to strictly Fail-Fast. Remove existing openpyxl empty fallback sheet generation (L799-L808). If `execution.step_states` has no atoms or `status != PASSED`, throw an `AppException` (400 Bad Request).
  - Remove the `try/except Exception` catch-all at L700, replacing with strict typed `except AppException` and RFC-7807 dual-reporting.
  - Replace `getattr(q, "verified_source_ids", None)` and `getattr(q, "unverified_aliases", None)` at L758-L761 with direct Pydantic DTO attribute access (Zero-Compromise Pledge).
  - Replace hardcoded Finnish column headers at L778-L789 (`"Matriisi"`, `"Kriteerin Nimi (UI)"`, `"Tekoälyn Sääntö"`, etc.) with locale-resolved Enum keys or at minimum English constants to comply with `no_string_l10n` invariant.
  - Verify `/api/v2/executions/{execution_id}/export` sets proper `Content-Disposition` headers.

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- Modify @[c:\src\quorum\backend_v2\services\blueprint.py] (CONTEXT-ONLY: `prompt_compiler.py` is frozen per `prompt_compiler_immutability` rule — do NOT modify it):
  - Ensure `blueprint.py`'s call-site usage relies strictly on the `I18nText.resolve(target_locale)` method for SDUI rendering. Absolutely no naked dictionary parsing or manual fallback chains allowed in the service layer.

### Phase 3A: Top Navigation Refactor
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart] and @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\workflow\workflow_general_tab.dart] to implement the new 3-tab main nav structure (Perustiedot, XAI, Raporttipohjat).

### Phase 3B: Output Profile Sub-Tab Restructuring
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\profile_editor_view.dart] to implement the 3-tab Output Profile sub-nav.

### Phase 3C: Section Template UI & i18n Widget Updates
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart] to use `I18nTextField` and section-level synthesis toggles (define whether toggle persists to DTO or is UI-only state).

### Phase 3D: Excel Action Button (VERIFY & ENHANCE)
- VERIFY existing Excel export button in @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart#L63] (`.xlsx` reference already exists). Enhance visibility/prominence alongside PDF download only if not already exposed.
- **Localization Updates**:
  - Modify @[c:\src\quorum\client_app_v2\lib\l10n\app_fi.arb] and @[c:\src\quorum\client_app_v2\lib\l10n\app_en.arb] with new tab names and button texts.

### Phase 4: Verification & E2E Integration Gate
- Run backend and flutter audit loops.
- Verify end-to-end functionality in Flutter Studio.
- Verify Excel export logic correctly crashes with an Error Boundary (400) for empty executions and succeeds for populated execution states.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- Zero warnings, strict type purity enforced.
- Cross-domain DTO parity maintained (Freezed models compile).
- Test coverage >90% for modified Python files.

### Automated Unit Tests
- Run Backend Audit: `uv run python scripts/backend_audit_loop.py tests/unit/services/test_execution.py --test`
- Run Frontend Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/profile_editor_view_test.dart`

### Manual Verification Steps
- Run `uv run python backend_v2/seed/run_seed.py local` to wipe and recreate the database with the new seed structures.
- Launch Flutter UI, navigate to Studio -> Edit Profiles, verify the 3-tab structure and the presence of `+ Lisää käännös` on i18n text fields.
- Perform a pipeline execution test, then trigger the Excel download (`.xlsx`) and verify the `Yhteenveto` and `Raakadata` sheets open correctly in Excel. Attempt to export an empty execution and verify it is explicitly rejected.

### MANDATORY Final E2E REST API Verification Gate
- `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
