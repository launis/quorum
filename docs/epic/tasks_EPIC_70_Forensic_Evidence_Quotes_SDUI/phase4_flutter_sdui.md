# Phase 4: Admin Studio Frontend (Flutter) (EPIC 70)

## Objective
Update the Flutter front-end data models, Output Profile Studio UI, and SDUI grid components to render the new quotes capability.

## Execution Steps

### 1. Update Flutter Freezed Models
**Targets:** 
- `c:\src\quorum\client_app_v2\lib\features\execution\models\scorecard_dto.dart`
- `c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_dto.dart`
- `c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart`
- Add `@JsonKey(name: 'quotes_list') @Default([]) List<String> quotesList` to `MatrixScorecardRowDto`.
- Update the default list for `@Default(['label', 'score', 'distribution', 'row_explanation'])` to remain the same, but ensure we don't break JSON parsing if `quotes` or `quotes_list` comes in.
- Run `dart run build_runner build -d` to regenerate the `.g.dart` and `.freezed.dart` files. Note: DO NOT use `flutter pub run`.

### 2. Update Studio Form UI
**Target:** `c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\synthesis_editor_card.dart`
- In the `visible_columns` checkbox mapper (around line 178), add the new option: `'quotes' => 'Lainaukset (quotes)'` alongside the existing options (label, score, distribution, row_explanation).
- Add a UI warning text: `*(Tip: saves space by replacing the standard explanation)*` specifically for the quotes option. Ensure localization logic is cleanly handled if possible, or use standard text.

### 3. Update SDUI Grid View
**Target:** `c:\src\quorum\client_app_v2\lib\features\execution\views\widgets\atom_matrix_table_widget.dart`
- In the data table renderer, check `if (visibleColumns.contains('quotes'))`.
- If true, render a Markdown column displaying the items from `quotesList` as a bulleted list.
- Ensure the UI handles empty lists gracefully.

### 4. Verification
- Verify build success with Flutter.
- Inspect the Output Profile Studio UI.
- Verify that generating a report with the "quotes" column active successfully displays the bullet points and hides the standard explanation.

## Architectural Invariants
- **Rule 30: tripartite_rendering_boundary:** The Backend produces purely raw DTO data... The Flutter frontend retains sole responsibility for Zero-Math rendering.
- **Rule 40: no_string_l10n:** Hardcoded display strings within the backend are strictly prohibited. Always reference designated Enum keys for UI text. (Integrate UI tips cleanly using localization).
- **Rule 45: cross_language_enum_parity:** Pydantic `Enum` and `Literal` definitions MUST maintain absolute strict parity with their Flutter client counterparts.
- Keep the `Isolate.run()` Pydantic-Flutter parsing fail-fast. Ensure `quotesList` defaults to `[]` so that missing lists don't crash the decoder.
