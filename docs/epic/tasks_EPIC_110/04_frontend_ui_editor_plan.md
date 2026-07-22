# Epic 110: Frontend UI Editor Plan (Phase 4)

Source: Epic 110 Phase 4

This plan focuses on strictly aligning the Flutter frontend Studio Editor with the Dumb Painter SDUI Architecture, specifically refactoring the `LayoutEditorCard` to accommodate the restored terminology mapping dictionaries (`matrixColumnLabels`, `extensionLabels`) through a structured 3-part layout, matching the parent `OutputProfile` structure.

## Target & Context Files
- TARGET (Modify): `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]`
- CONTEXT (Read-Only): `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`

## Rule Injections & Invariants (from `.agents/rules/02_flutter_desktop.md`)
- **I18nText Domain Model SSOT**: You MUST use the `I18nTextField` UI widget in Flutter when presenting a text input bound to an `I18nText` object. The component inherently encapsulates the logic for displaying the current locale's translation while managing the fallback and structural integrity.
- **Design Token Absolute Rule**: Exclusively use global Design Tokens (e.g., `AppSpacing.p16`, `Theme.of(context).textTheme`). ANY use of hardcoded numeric doubles for heights, widths, or padding (e.g., `SizedBox(height: 15)`) is STRICTLY PROHIBITED.
- **Rigid Macro-Breakpoint Standard**: Components must be agnostic of the global UI window and adapt strictly via `LayoutBuilder`. (Since this is an editor card, ensure it degrades gracefully within its container constraints).

## Proposed Implementation Steps

### 1. Flutter UI Refactoring (Phase 4: 3-Part Layout Block Editor)
Target: `@[c:\src\quorum\client_app_v2\lib\features\studio\views\widgets\profile\layout_editor_card.dart]`

- **Destructive Operation Inventory**:
  - REFACTOR: Extract the `_buildLayoutEditor` logic into a new private `HookConsumerWidget` (e.g., `_LayoutBlockEditorItem`) to manage local state.
  - REORGANIZE: Replace the single-column flat list with a 3-part conditionally rendered UI. Use `useState(0)` to track the active section and a `SegmentedButton` (or styled row) to switch between them. Do NOT use `TabBarView` as it will cause a fatal unbounded height crash inside the parent `ListView.builder`.
  - DESIGN TOKENS: You MUST replace all existing hardcoded padding/margins (e.g., `EdgeInsets.all(12)`) in this component with `AppSpacing` tokens (e.g., `AppSpacing.p12`).
- **Update Logic**:
  - **Part 1: Perustiedot (Basic Info)**: Move existing fields here: View Model, Text Delivery Mode, Section Title, Section Description.
  - **Part 2: Datasiilot & Stepit (Data & Blocks)**: Move existing fields here: Target Blocks, Steps, and Synthesis configurations.
  - **Part 3: Terminologia & Laajennokset (Terminology & Extensions)**: 
    - Create a dedicated private stateless widget (e.g., `_DictionaryMapEditor`) that takes a `Map<String, I18nText>` and an `onChanged` callback.
    - Use this widget for both `matrixColumnLabels` and `extensionLabels`.
    - Provide a button to "Add Term" (adds a new key), and render a row for each entry containing a standard `TextField` for the Key (e.g. "coaching") and an `I18nTextField` for the Value.
  - Ensure state updates correctly use the parent `onChanged(OutputLayoutBlock)` callback. Do NOT attempt to read/write directly to global Riverpod notifiers from inside this controlled component.

## Bidirectional Integration Check
- **Producer**: `layout_editor_card.dart` allows users to author terminology mappings in the Studio UI and saves them back to the database.
- **Consumer**: `blueprint.py` (Backend) will consume these exact user-authored label configurations during synthesis generation, and pass them to the Dumb Painter renderers.

## Testing Strategy & Quality Gate
1. Execute the Universal Quality Gate on modified Flutter files.
2. Run Flutter Audit Loop on UI Editor: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/views/widgets/profile/layout_editor_card.dart`
3. Verify that the build completes successfully and there are no Dart analysis errors.
