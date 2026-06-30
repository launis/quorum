# EPIC 92: Phase 4 - Frontend Admin Studio UI

## Goal
Implement the DAG Viewer, `N/A` state visualization, and Matrix Editor toggles in the Flutter Admin Studio to support the Enriched Atom Graph architecture.

**Source**: [EPIC_92_Enriched_Atom_Graph_Architecture.md](file:///c:/src/quorum/docs/epic/EPIC_92_Enriched_Atom_Graph_Architecture.md) Phase 6

## Scoping
**TARGET (Modify)**
- `c:\src\quorum\client_app_v2\lib\admin_studio\screens\matrix_editor_screen.dart` (Add Conditional Short-Circuit Toggle)
- `c:\src\quorum\client_app_v2\lib\admin_studio\screens\execution_viewer_screen.dart` (Add DAG tree view and N/A states)
- `c:\src\quorum\client_app_v2\lib\admin_studio\widgets\prompt_block_editor.dart` (Support Resolution Pass config)

**CONTEXT (Read-Only)**
- `c:\src\quorum\client_app_v2\lib\models\execution_models.dart`

## Architectural Invariants (Hardening Mandates)
You MUST strictly adhere to these rules during execution:
- **02_flutter_desktop.md (No-String Mandate)**: Raw strings must live exclusively in `.arb` files using ICU formats. Hardcoding display strings in the Dart UI is forbidden.
- **02_flutter_desktop.md (De-Generator)**: Optimistic Riverpod updates and SafeCast defensive parsing must be used.
- **UI/UX Desktop-First**: Plan for >1200dp three-pane layouts. The DAG Viewer should be a hierarchical tree or indented list, not a cramped mobile view.

## Implementation Steps

### Step 1: Models & DTO Parsing
- Update the Dart models to securely parse `depends_on_atom_ids`, `short_circuit_reason_atom_id`, and `short_circuit_evaluation`. Use `SafeCast` to prevent null-reference crashes.

### Step 2: Matrix Editor Updates
- Add a Switch/Toggle for "Enable Conditional Short-Circuit" in the Matrix Editor.
- Ensure the state is persisted to the backend via the Optimistic Riverpod pattern.

### Step 3: Execution Viewer DAG & N/A State
- Refactor the Execution Viewer list into an expandable Tree or Indented view based on `depends_on_atom_ids`.
- Add a new visual state for `N/A` (Gray).
- Display the short-circuit reason metadata explicitly: e.g. "Ei arvioitu: Ennakkoehto ei täyttynyt [ID]".
- Add spatial anchoring: Clicking the condition ID should highlight the condition text in the Source Text Viewer.

### Step 4: Documentation Update
- Document the new UI workflows in `c:\src\quorum\docs\architecture\architecture\sdui_and_display_tier.md`.

## Testing & Quality Gate Plan
- **UNIT TESTS**: Create/update Flutter widget tests to ensure the DAG tree renders correctly with deeply nested items.
- **QUALITY GATE**: You MUST run `uv run python scripts/flutter_audit_loop.py client_app_v2` to verify Flutter code quality.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_92_tracker.md`
