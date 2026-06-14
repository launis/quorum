# Phase 4: Frontend UI (Admin Studio V2)

**Source:** Epic Phase 4 (Frontend / Admin Studio V2)

## Objective
Update the Flutter Client UI to reflect the new granular TDA Assertion fields dynamically without relying on the single black-box string.

## Scope
- **TARGET (Modify):**
  - `client_app_v2/lib/features/studio/models/prompt_block.dart`
  - `client_app_v2/lib/features/studio/views/widgets/scale_editor_modal.dart`
  - `client_app_v2/lib/l10n/app_en.arb`
  - `client_app_v2/lib/l10n/app_fi.arb`
- **CONTEXT (Read-Only):**
  - `client_app_v2/lib/core/models/enums.dart`

## Architectural Mandates

- **<rule num="40" id="no_string_l10n">**: Hardcoded display strings within the backend are strictly prohibited. Always reference designated Enum keys for UI text. *(Applies to Flutter via .arb files)*
- **<rule num="3" id="fail_fast_hydration_mandate">**: All uncertain data flowing as dictionaries MUST be hydrated via `.model_validate()` IMMEDIATELY before processing. Fishing for dictionary values via `dict.get()` is strictly prohibited. *(Applies to Flutter Freezed models via disallowUnrecognizedKeys)*

## Implementation Steps
1. Open `app_en.arb` and `app_fi.arb` and define translations for:
   - `tdaAnchorTarget` ("Anchor Target" / "Ankkurikohde")
   - `tdaBoundingBox` ("Bounding Box Scope" / "Hakuikkunan Laajuus")
   - `tdaExtractionRule` ("Extraction Rule" / "Poiminnan Sääntö")
2. Open `prompt_block.dart` and add `anchorTarget` (String?), `boundingBoxScope` (String, default "paragraph"), and `extractionRule` (String?) to the `TDAAssertion` Freezed model.
3. Open `scale_editor_modal.dart`. Inside the TDA assertion edit loop:
   - Replace the large `conceptDescription` `TextFormField` with a smaller, generic concept description field.
   - Add a `TextFormField` for `tda.anchorTarget`.
   - Add a `DropdownButtonFormField` for `tda.boundingBoxScope` allowing selection between `sentence`, `paragraph`, `document`, `adjacent_paragraphs`.
   - Add a `TextFormField` for `tda.extractionRule`.
4. Ensure `setState` properly copies the new fields into the `_editableScale` object during UI changes.

## Testing & Quality Gate Plan
- **Code Generation:** Must instruct the user to run `dart run build_runner build -d` and `flutter gen-l10n` to rebuild serialization.
- **Universal Quality Gate:** Execute `uv run python scripts/flutter_audit_loop.py client_app_v2` to verify Flutter UI compilation.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_tda_granular_schema_refactor_tracker.md`
