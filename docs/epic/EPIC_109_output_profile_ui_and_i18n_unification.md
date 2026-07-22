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
6. **Strict SDUI Rendering Mandate**: The frontend MUST NOT contain any hardcoded business logic, layout states, or fallback UI strings for output profiles. All dynamic content, including layout configurations, section titles, and RFC-7807 error messages, MUST be strictly driven by backend DTOs and localization dictionaries.

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
  - Extract `target_locale` securely from `execution.metadata["target_locale"]`.
  - Read the Flutter localization files (`client_app_v2/lib/l10n/app_en.arb` and `app_fi.arb`) using `json.load()` to act as the single source of truth for string resolution.
  - Replace hardcoded Finnish column headers at L778-L789 (`"Matriisi"`, `"Kriteerin Nimi (UI)"`, `"Tekoälyn Sääntö"`, etc.) with their respective `.arb` keys (e.g., `excelHeaderMatrix`, `excelHeaderCriterion`) to comply with the `no_string_l10n` invariant.
  - Do NOT add a `locale` query parameter to the export endpoint. The execution endpoint must remain entirely zero-trust and rely solely on the `target_locale` inherently bound to the execution's metadata in the SSOT database.
  - Verify `/api/v2/executions/{execution_id}/export` sets proper `Content-Disposition` headers.

### Phase 2: Orchestration, Registry & Prompt Compiler Updates
- Modify @[c:\src\quorum\backend_v2\models\v2_core.py] and @[c:\src\quorum\backend_v2\models\dtos\output_profile.py]:
  - Ensure `is_synthesis_enabled: bool` is added to Pydantic domain models to enforce cross-domain SDUI parity.
  - Add the `is_synthesis_enabled: bool = Field(default=True, description="Toggle for UI section-level synthesis.")` property to `OutputLayoutBlock` to support the section-level synthesis toggle introduced in Phase 3C. The `default=True` establishes backward compatibility for layouts that already use synthesis.
  - Add `is_synthesis_enabled: bool = Field(default=True)` to `ReportLayoutDTO` to ensure the Flutter client accurately receives the state from the orchestrator.
- Modify @[c:\src\quorum\backend_v2\services\blueprint.py] (CONTEXT-ONLY: `prompt_compiler.py` is frozen per `prompt_compiler_immutability` rule — do NOT modify it):
  - Delete the legacy `@staticmethod def _resolve_i18n_str` entirely, as it violates the strict `I18nText` object pattern (naked dictionary parsing).
  - In `_build_layouts`, explicitly map `is_synthesis_enabled=layout_def.is_synthesis_enabled` to `ReportLayoutDTO`.
  - **SDUI Parity Preservation**: Ensure that `title` and `description` are passed as native `I18nText` objects to the DTOs rather than prematurely forcing `I18nText.resolve(target_locale)`. This is strictly required to maintain full dynamic localization capabilities in the Flutter frontend.

### Phase 3A: Top Navigation Refactor
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\workflow_builder_view.dart] and @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\workflow\workflow_general_tab.dart] to implement the new 3-tab main nav structure (Perustiedot, XAI, Raporttipohjat). This completely replaces the legacy monolithic scrollable form architecture to improve UI scalability.

### Phase 3B: Output Profile Sub-Tab Restructuring
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\profile_editor_view.dart] to implement the 3-tab Output Profile sub-nav, mirroring the unified layout structure of the main builder.

### Phase 3C: Section Template UI & i18n Widget Updates
- Modify @[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart] to use `I18nTextField` and section-level synthesis toggles (synchronized with backend models to prevent JSON parsing crashes).
- **Strict DTO Mapping**: Ensure the `isSynthesisEnabled` property is perfectly mapped to the frontend Dart Freezed model. In a strict SDUI architecture, all layout configuration state must reside in the backend DTO (`OutputLayoutBlock`) and be driven by `seed_data.json` to guarantee cross-domain SDUI parity.

### Phase 3D: Excel Action Button (VERIFY & ENHANCE)
- VERIFY existing Excel export button in @[c:\src\quorum\client_app_v2\lib\features\execution\views\execution_report_view.dart#L63] (`.xlsx` reference already exists). Enhance visibility/prominence alongside PDF download only if not already exposed.
- **Error Handling & Boundary Enforcement**: Enforce a Flutter-side Error Boundary interceptor when triggering the export. It must catch `DioException`s and explicitly parse the RFC-7807 payload (HTTP 400) to display the backend-provided user-friendly error message. **Architectural Rule**: Instead of creating frontend-side error localizations for failed exports in the ARB files, you MUST directly present the RFC-7807 error message provided by the backend to prevent raw app crashes and forbid frontend-hardcoded error strings.
- **Localization Updates**:
  - Modify @[c:\src\quorum\client_app_v2\lib\l10n\app_fi.arb] and @[c:\src\quorum\client_app_v2\lib\l10n\app_en.arb] with new tab names, button texts, and the new translation keys corresponding to the Excel export headers (e.g., `excelHeaderMatrix`, `excelHeaderCriterion`, `excelHeaderRule`, etc.) to enforce cross-language parity for the backend Excel generation.

### Phase 4: Verification & E2E Integration Gate
- Run backend audit loops on modified python files.
- Run frontend audit loop (`uv run python scripts/flutter_audit_loop.py client_app_v2/lib/l10n/ --build`) to ensure ARB files compile correctly.
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
