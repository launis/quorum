# Epic 46: Soft Scoring Engines - Phase 2: Frontend UI & DTOs

## Objective
Implement Strictness Level DTO Enums in Flutter to ensure the UI correctly maps the levels without hardcoding database structures. Fix the duplicate text issue in the Strictness dropdown, and enforce strict type-safety across all related UI elements.

## Architectural Invariants
- **Rule 1 (The Zero Compromise Pledge):** No `?? 'default'` or null-coalescing for missing strings/data.
- **Rule 2 (Fail-Fast State Management):** No `.maybeWhen()` or `.orElse()`. Use strict Dart 3 `switch` or `when()` pattern matching.
- **Rule 3 (Frontend Zero DB Hardcoding Mandate):** The UI must not rely on magic database IDs, names, or hardcoded integer keys (e.g., `Map<int, String> strictnessOptions = {50: 'Tasapainoinen'};`).
- **Rule 4 (No String Mandate):** All UI strings MUST be placed in `.arb` files and resolved via `AppLocalizations`.

## Target Files
**TARGET (Modify):**
- `client_app_v2/lib/core/models/enums.dart`
- UI Widget containing the Strictness Dropdown (Search for the component rendering `strictness_level`)
- `client_app_v2/lib/l10n/app_en.arb`
- `client_app_v2/lib/l10n/app_fi.arb`

**CONTEXT (Read-Only):**
- `client_app_v2/lib/features/execution/views/widgets/report_renderer_widget.dart`

## Milestones

### Milestone 1: Strong Typing for Strictness (`enums.dart` & `l10n`)
1. **Define StrictnessEnum:** In `enums.dart`, define a `@JsonEnum()` backed enum `StrictnessLevel` with mapped values matching the backend (e.g. `lenient` maps to 15, `balanced` maps to 50, `strict` maps to 85, `absolute` maps to 100, `fullFlexibility` maps to 0). Note: Depending on backend payload format, it could be integer `@JsonValue(15)` or string representation.
2. **Localization:** Add matching keys in `app_fi.arb` and `app_en.arb`:
   - `strictnessLenient`: "Salliva (15)"
   - `strictnessBalanced`: "Tasapainoinen (50 - Oletus)"
   - `strictnessStrict`: "Tiukka (85)"
   - `strictnessAbsolute`: "Ehdottomuus (100)"
   - `strictnessFullFlex`: "Täysi joustavuus (0)"
3. **Run CodeGen:** Instruct user to run `cd client_app_v2; flutter gen-l10n; dart run build_runner build -d`.

### Milestone 2: UI Presentation Fix (Duplicate Text)
1. **Locate Dropdown:** Find the Flutter widget rendering the `strictness_level` dropdown.
2. **Refactor Rendering:** The current implementation manually appends keys and values (e.g. `Text('${entry.value} (${entry.key})')`), causing the duplicate `Salliva (15) (15)` bug. Remove this logic entirely.
3. **Use the Enum & Localizations:** Render the options purely from `StrictnessLevel.values` and resolve the display text via a `switch (strictnessLevel)` returning the exact `AppLocalizations.of(context)!.strictnessX` string.

### Milestone 3: XAI Calculation Log Rendering Validation
1. **Verify Log Display:** Ensure that the Markdown block containing the calculation logs (XAI) renders perfectly without UI layout overflows. The new Soft Scaling rationale sentences must be clearly readable.
2. **Fail-Fast Enforcement:** Ensure there are no hidden `SizedBox.shrink()` wrappers around the report renderer catching parse exceptions.

### Verification & Quality Gate Plan
- **Tools to Run:** `uv run python scripts/flutter_audit_loop.py client_app_v2/[modified_files]`
- **Tests:** Verify UI layout passes static analysis, custom linter, and ensure there are no generated model mismatch errors. Run `flutter test` to ensure stability.
