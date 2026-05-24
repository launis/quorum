# Phase 3: Frontend Admin Studio UI Update

## Source
Epic Phase 3, Steps 1-3

## Context
- `client_app_v2/lib/features/studio/models/prompt_block.dart` (TARGET)
- `client_app_v2/lib/features/studio/ui/edit_prompt_block_view.dart` (TARGET)

## Targets
- `client_app_v2/lib/features/studio/models/execution_persona.dart` (TARGET - New)
- `client_app_v2/lib/features/studio/models/prompt_block.dart` (TARGET)
- `client_app_v2/lib/features/studio/ui/edit_prompt_block_view.dart` (TARGET)

## Architectural Laws
- **Rule 00 - universal_fail_fast**: Dart 3 Freezed schema must perfectly map to the Python backend Pydantic model. If it fails, let it crash.

## Implementation Steps
- [x] 1. **Model Definition**: Create the `ExecutionPersona` enum in Dart (defined in `enums.dart` in sync with system standards).
- [x] 2. **Freezed Update**: Update the `PromptBlock` Freezed model in `prompt_block.dart` to include `ExecutionPersona executionPersona`.
- [x] 3. **Build Runner**: Run `dart run build_runner build -d` to generate the new `.g.dart` mappings.
- [x] 4. **UI Update**: Modify the Admin Studio matrix edit view (`prompt_block_builder_view.dart`) to include a dropdown/selection UI widget for `ExecutionPersona`.
- [x] 5. **Helper Text**: Ensure the `ai_description` text field clearly instructs users to only input business logic, not system rules (updated in `app_en.arb` and `app_fi.arb`).

## Testing & Quality Gate Plan
- **Unit Tests**: Update parsing tests if any in `flutter test`.
- **Quality Gate**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build` to verify Dart types and schemas.
