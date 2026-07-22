# Epic 110: Frontend Models & Renderer Plan (Phases 1 & 2)

Source: Epic 110 Phase 1 & 2

This plan focuses on strictly aligning the Flutter frontend with the Dumb Painter SDUI Architecture, enforcing complete parity with the PDF rendering by removing hardcoded UI intelligence, and extending the DTOs to support terminology sovereignty.

## Target & Context Files
- TARGET (Modify): `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`
- TARGET (Modify): `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`

## Rule Injections & Invariants (from `.agents/rules/02_flutter_desktop.md`)
- **Strict SDUI Rendering Mandate**: The frontend MUST NOT contain any hardcoded business logic, layout states, or fallback UI strings. The Flutter UI only renders what the backend provides (`resolved_title`).
- **SDUI Native Schizophrenia Prevention**: All new UI logic and rendering flows MUST be driven by the backend. Do NOT leak business logic into the Flutter frontend.
- **Cross-Domain DTO Parity**: Any changes to `OutputLayoutBlock` MUST be synchronized with the Python backend models (`v2_core.py`), which was completed in the previous backend plan.
- **Automated Code Generation Mandate**: When Freezed models are modified, you MUST autonomously execute the build script (`flutter_audit_loop.py ... --build`).
- **I18nText Domain Model SSOT**: Use `I18nTextDto` for all localized text fields.

## Proposed Implementation Steps

### 1. Flutter Models (Phase 2: Terminology Sovereignty)
Target: `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`

- Add `Map<String, I18nTextDto>? matrixColumnLabels` to the `OutputLayoutBlock` class.
- Add `Map<String, I18nTextDto>? extensionLabels` to the `OutputLayoutBlock` class.
- These fields must be nullable to match the Python strict backend and prevent deserialization errors on older records that might lack these fields prior to seeding.

### 2. Freezed Build Execution
Target: Terminal

- Run the flutter audit loop to generate `.g.dart` and `.freezed.dart` files.
- Command: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`

### 3. Flutter Renderer (Phase 1: Reverting Architectural Violations)
Target: `@[c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\report_renderer_v2_widget.dart]`

- **Destructive Operation Inventory**:
  - DELETE the redundant "2.5 Global Synthesis" rendering block. This logic is an architectural violation because Jinja only renders `content_blocks`. Both must render identically.
  - INTENTIONALLY DROPPED: Manual `l10n.reportExecutiveSummary` or similar UI intelligence fallbacks for titles.
  - Reason: The Dumb Painter Law mandates that section titles MUST come exclusively from the backend payload (`block['resolved_title']`).
- **Update Logic**: Modify the widget rendering loop to simply render `block.resolvedTitle` (or equivalent DTO property if it exists in the payload). Do not use any conditional logic to deduce titles.

## Bidirectional Integration Check
- **Producer**: `blueprint.py` (Backend) now fully resolves and injects `matrix_column_labels`, `extension_labels`, and `resolved_title` into the payload.
- **Consumer**: `report_renderer_v2_widget.dart` now acts as a pure dumb painter, consuming `resolved_title` without any fallback logic, and `output_profile.dart` matches the expected `OutputLayoutBlock` schema.

## Testing Strategy & Quality Gate
1. Execute the Universal Quality Gate on modified Flutter files.
2. Run Flutter Audit Loop: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`
3. Run Flutter Audit Loop on Renderer: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/report_renderer_v2_widget.dart`
4. Verify that the build completes successfully and there are no Dart analysis errors.
