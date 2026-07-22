# EPIC 110: Dumb Painter SDUI Architecture (Zero Intelligence Rendering)

## 1. Goal Description & Background (Objective & Problem Statement)
The current implementation of the output reporting engine suffers from architectural drift, where the presentation layers (PDF Jinja templates and Flutter UI) have slowly accumulated hardcoded business logic, localized text strings, and fallback mechanisms. This violates the core principle of a Server-Driven UI (SDUI), leading to a loss of parity between the PDF output and the Flutter client.

The goal of this Epic is to enforce a **100% "Dumb Painter" SDUI Architecture**. The data produced by the AI executions and the SSOT database (`seed_data.json`) must be the absolute and sole truth. The presentation layers (PDF and Flutter) must be stripped of all intelligence. They will act purely as "dumb painters" that blindly render the exact payload delivered via `ReportDataDTO`.

A perfect example of this is the preamble/preface ("alkuteksti"): it is injected purely as a markdown block from the backend payload, requiring zero definitions or styling logic in Jinja or Flutter. This exact same principle MUST apply to everything else, including section titles. The payload inputs must be identical for both rendering methods. The only exception to this rule is the `custom_preface_md` (Custom Preface), which is explicitly authored by the human user from the UI.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- **Hardcoded Jinja Strings**: Purging all hardcoded Finnish strings (`Kokonaiskeskiarvo`, `Käyttäjä`, `Yhteenveto`, `Warning`, etc.) from `report_template.jinja2`.
- **Flutter UI "Duct-Tape"**: Ruthlessly removing recent duct-tape logic in `report_renderer_v2_widget.dart` that attempted to inject titles (e.g., `l10n.reportExecutiveSummary`) or mask missing data.
- **Frontend Intelligence**: Removing any conditional logic in the renderers that attempts to deduce or format section titles that should have been provided by the backend.
- **UI/PDF Parity Violation (Global Synthesis)**: Removing the redundant `2.5 Global Synthesis` block from Flutter's `report_renderer_v2_widget.dart`. Jinja only renders `content_blocks`, so Flutter rendering both `contentBlocks` and `globalSynthesis` breaks the 100% parity law.
- **Amnesia Bug (Loss of Data)**: Removing the bug in `blueprint.py` that overwrote AI-generated scores with zero when `evaluated_atoms` were missing.

### Retained SSOT Invariants (`What We Will RETAIN`)
- **Flutter ARB Localization (`l10n`)**: The `app_fi.arb` and `app_en.arb` files remain the Single Source of Truth ONLY for system-level static UI labels (e.g., "Tallennus onnistui", "Ladataan").
- **Seed Data Root Architecture**: `seed_data.json` remains the root immutable state for profile structures. The output profile configuration is the absolute authority on ALL report-level terminology, completely replacing Jinja or ARB fallbacks.
- **The "One Exception" (Custom Preface)**: `custom_preface_md` will continue to pass directly through the pipeline, as it is a deliberate user-authored text input from the UI.

### Compliance & Modernity Gates
1. **The Dumb Painter Law (Zero Intelligence in Renderers)**: No text, title, or structural formatting shall be generated, hardcoded, or deduced by the PDF template or Flutter UI. All printed text (like the dynamically injected preamble/alkuteksti) MUST come exclusively from the backend payload as identical inputs to both renderers.
2. **Pydantic Strictness**: `ConfigDict(strict=True, extra='forbid')` remains enforced across all backend DTOs to guarantee the exact shape of the payload.
3. **Cross-Domain DTO Parity**: Any changes to the `ReportDataDTO` or `OutputLayoutBlock` structures MUST be perfectly synchronized across both Python and Flutter Freezed models (`flutter_audit_loop.py --build`).

### Producer-Consumer Integration Check
- **Producer (Backend/AI)**: `blueprint.py` must take on the full cognitive load of resolving synthesis titles from the database and loading system labels from the `.arb` dictionaries. It produces a fully self-contained payload.
- **Consumer (PDF/Flutter)**: `report_template.jinja2` and `ReportRendererV2Widget` act strictly as blind consumers, mapping directly to `block['resolved_title']` and `l10n` variables without any internal logic.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Reverting Architectural Violations (Removing Duct-Tape)
- **Flutter UI**: Modify `client_app_v2/.../report_renderer_v2_widget.dart` to strip out all recent manual title injections (e.g., `l10n.reportExecutiveSummary`). Restore the UI loop to simply render `block['resolved_title']` if it exists. MUST completely DELETE the redundant "2.5 Global Synthesis" block to restore PDF/Flutter parity.
- **Jinja PDF**: Modify `backend_v2/templates/report_template.jinja2` to remove all hardcoded UI intelligence, including `<h2 style="...">Yhteenveto</h2>` and static metadata labels. Update `render_sdui_blocks` macro to render an `<h2 style="...">{{ block.resolved_title }}</h2>` if `block.resolved_title` exists.

### Phase 2: Terminology Sovereignty (Restoring What Epic 106 Deleted)
- **Context & Correction**: Epic 106 successfully unified the SDUI pipeline schemas (`expected_sdui_type`), ensuring the printing pipeline works identically for all data. However, it incorrectly deleted the dynamic terminology controls from the Output Profile because the UI was considered "cluttered". Epic 110 restores these controls to the presentation layer (Output Profile) and solves the clutter via the new 3-Part UI.
- **DTO Restoration & Expansion**: Modify `OutputLayoutBlock` (in Python `v2_core.py` and Flutter `output_profile.dart`) to restore and expand the dynamic terminology override dictionaries. As per the core architectural law, everything must be definable in the UI:
  - `matrix_column_labels: dict[str, I18nText]` (e.g., mapping "explanation" to "Selite", "level_breakdown" to "Tasojakauma").
  - `extension_labels: dict[str, I18nText]` (e.g., mapping "coaching" to "Arjen Vinkki", "falsification" to "Vastaväite").
- **Database Migration**: Update `seed_data.json` to populate these dictionaries for existing layout blocks, fully removing the need to hardcode them in `app_fi.arb`.
- **Compile Freezed**: Execute `flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`.

### Phase 3: Backend Intelligence Delegation & Data Restoration (Python)
- **Blueprint Mapping (Titles & Terminology)**: Modify `backend_v2/services/blueprint.py` to dynamically loop through `content_blocks` and `layout.synthesis_blocks`. It must resolve `matrix_column_labels` and `extension_labels` from the layout block and pass them exactly as required into the SDUI payload.
- **Data Restoration (Matrix Selite & Tasojakauma)**: Ensure that `row_explanations_cache` (Selite), `level_breakdown` (Tasojakauma), and `raw_score` / `normalized_score` are correctly mapped from the `MatrixPayload` to the `ScoreAxisDTO` so they appear inside the matrix tables.
- **Data Restoration (Extensions / Coaching)**: Re-implement the extraction of `coaching`, `falsification`, `missing_context`, etc., from `MatrixPayload.extensions` and populate them correctly into `ReportDataDTO.grouped_extensions`. This guarantees that "Arjen vinkki" and other extensions are printed via the unified layout block system without any frontend intelligence.

### Phase 4: Flutter UI Refactoring (3-Part Layout Block Editor)
- **3-Part UI Architecture**: Modify `layout_editor_card.dart` in Flutter to split the increasingly complex Layout Block configuration into a functionally equivalent 3-part layout (e.g., nested tabs or accordions) to mirror the parent Output Profile UI:
  1. **Perustiedot (Basic Info)**: View Model, Text Delivery Mode, Section Title, Section Description.
  2. **Datasiilot & Stepit (Data & Blocks)**: Target Blocks, Steps, and Synthesis configurations.
  3. **Terminologia & Laajennokset (Terminology & Extensions)**: UI fields to dynamically edit the new `matrix_column_labels` and `extension_labels` (e.g., defining "Arjen Vinkki" in FI and EN).
- **Verification**: Ensure the user can fully customize report terminology through the UI without touching code.

### Phase 4: Verification & E2E Integration Gate
- Verify the Custom Preface (`custom_preface_md`) correctly bypasses these strict rules as intended.
- Execute automated build and audit loops across both domains.
- Validate absolute visual parity between the Flutter UI and the PDF export.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- Zero hardcoded domain text strings exist in `report_template.jinja2`.
- Zero manual text-injection fallbacks exist in `report_renderer_v2_widget.dart`.
- Cross-domain DTO parity maintained (Freezed models compile).
- Test coverage >90% for modified Python files.

### Automated Unit Tests
- Run Backend Audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`
- Run Frontend L10n Build: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/l10n/ --build`
- Run Frontend Widget Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart`

### Manual Verification Steps
- Hot reload the Flutter application.
- Observe that the executive summary correctly displays "Yhteenveto" strictly based on the backend database resolution.
- Export the PDF and verify it perfectly mirrors the UI without duplication or hardcoded strings.

### MANDATORY Final E2E REST API Verification Gate
- Run E2E Integration Suite: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
