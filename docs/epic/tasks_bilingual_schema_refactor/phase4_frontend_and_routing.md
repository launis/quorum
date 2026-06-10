# Phase 5: Frontend DTO Sync & Admin UI (Structured Editor)
Source: Epic Phase 3: Frontend & Admin Studio V2

## Objective
Synchronize the Flutter application's Freezed models to match the backend's new structured Pydantic schema, resolving the `CheckedFromJsonException` parity breaks. Replace the old string text field in the Studio with a Structured Prompt Editor UI.

## Targets (Modify)
- `client_app_v2/lib/core/models/prompt_block.dart`
- `client_app_v2/lib/core/models/prompt_block.freezed.dart`
- `client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart`
- `client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart`

## Context (Read-Only)
- `backend_v2/models/v2_core.py`

## Architectural Invariants
- **Rule 44 (Cross-Language Parity)**: Freezed models MUST match Pydantic schemas mathematically.
- **Rule 40 (No String L10n)**: Do not hardcode strings for UI tags unless strictly necessary.
- **Universal Fail Fast**: Allow `AppExceptionBoundary` to handle any remaining parity issues.

## Implementation Steps
1. **Freezed DTO Update**: Remove `aiRuleDescription` from the `TDAAssertion` Dart class.
2. Add structured `I18nText` properties (`conceptDescription`, `acceptanceCriteria`, `antiPatterns`, `contrastiveExample`), `syntacticAnchors`, and `enforcePreFlight`.
3. Add `isLightweightProtocol` boolean to the `PromptBlock` Dart class to match the backend's new schema.
4. Ensure `TDAAssertion.evaluationTrack` default value is set to `COGNITIVE_JUDGEMENT` to mirror the backend.
4. Run `dart run build_runner build -d` to regenerate the JSON parsers.
5. **UI Refactor**: Replace the old singular text area with separate `LocalizedTextInputWidget` fields for the four new text properties. Add a list editor for `syntacticAnchors`.

## Testing & Quality Gate Plan
- **Unit Tests**: Ensure the UI components render successfully.
- **Universal Quality Gate**: `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase5_frontend_schema_ui.md`
