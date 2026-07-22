# Phase 3C: Section Template UI & i18n Widget Updates

This plan addresses Phase 3C of Epic 109, updating the profile layout editor to use `I18nTextField` widgets for titles and descriptions, and wiring the new `is_synthesis_enabled` property to allow section-level synthesis toggles.

## Proposed Changes

### Frontend / Studio Output Profile Models
Modify the Dart domain models to maintain DTO parity with the Backend updates from Phase 2.

#### [MODIFY] [output_profile.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/models/output_profile.dart)
- Update `OutputLayoutBlock` class:
  - Add `@JsonKey(name: 'is_synthesis_enabled') @Default(true) bool isSynthesisEnabled,` to maintain cross-domain DTO parity.
- Update `EmbeddedOutputProfile` class:
  - Add `@JsonKey(name: 'is_synthesis_enabled') @Default(true) bool isSynthesisEnabled,` to maintain cross-domain DTO parity.

#### [MODIFY] [report_layout_dto.dart](file:///c:/src/quorum/client_app_v2/lib/features/execution/models/report_layout_dto.dart)
- Update `ReportLayoutDTO` class:
  - Add `@JsonKey(name: 'is_synthesis_enabled') @Default(true) bool isSynthesisEnabled,`

### Frontend / Studio Editor Views
Refactor the legacy hardcoded inputs to use localized inputs and add the UI controls for synthesis toggling.

#### [MODIFY] [layout_editor_card.dart](file:///c:/src/quorum/client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart)
- Update `SwitchListTile` for section-level synthesis (around line 252) to rely on the new `isSynthesisEnabled` property instead of checking `layout.synthesis != null`.
- Provide a clear UI state for toggling section-level synthesis on and off. 
- Refactor the hardcoded Finnish fallback for the description field (`"Osion kuvaus (valinnainen väliotsikko)"`) to use `l10n.layoutBlockDescriptionLabel` (or similar) from AppLocalizations.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/ --build` to re-generate Freezed models and test syntax.

### Manual Verification
- In Studio UI > Edit Profiles > Output Profile Editor, verify that adding a layout block reveals `I18nTextField` inputs for the Title and Description.
- Verify that toggling "Section-Level Synthesis" behaves deterministically without breaking the `isSynthesisEnabled` flag state.
