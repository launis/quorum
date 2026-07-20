# Phase 3: Flutter Admin UI Cleanup & Freezed Synchronization

Provide a brief description of the problem, any background context, and what the change accomplishes.
**Goal**: Remove deprecated OutputProfile fields from Flutter Freezed models to ensure JSON parsing parity, and clean up the Admin UI.

## Proposed Changes

### `client_app_v2/lib/features/studio/models/output_profile.dart`
#### [MODIFY] [output_profile.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/output_profile.dart)
- Remove `synthesis` (`SynthesisConfigDTO? synthesis`) from `OutputProfile` and `EmbeddedOutputProfile`.
- Remove `formattingDirectives` and `matrixColumnLabels` from `OutputProfile` and `EmbeddedOutputProfile`.
- Retain `SynthesisConfigDTO` itself as it is still used by `OutputLayoutBlock.synthesis`.

### Code Generation
- The Freezed models will be automatically regenerated during the Verification step via the `flutter_audit_loop.py --build` flag. Do not run `build_runner` manually.

### `client_app_v2/lib/features/studio/views/`
- Update the OutputProfile admin dashboard/form to reflect the pruned model.
- Remove the UI controls that edited profile-level `synthesis` (e.g. `SynthesisEditorCard` and `buildSynthesisPane()`).
- **CRITICAL**: Be sure to remove the unused `import 'package:client_app/features/studio/views/widgets/profile/synthesis_editor_card.dart';` from both `profile_editor_view.dart` and `output_profile_crud_view.dart` to prevent strict analyzer build failures.
- *(Note: `formatting_directives` and `matrix_column_labels` do not currently have UI controls, so no UI deletion is needed for them, only model deletion).*

### Repositories
- Clean up the frontend Repository classes if they construct or access these fields in outgoing API payloads, to prevent 422 errors.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build` to verify Flutter code compiles and passes tests.
- Backend `test_enum_parity.py` must pass.

### Manual Verification
- UI Validation: Deploy locally and verify existing report generation flows (report creation, PDF export, Studio Admin UI) work end-to-end through the User Interface.
