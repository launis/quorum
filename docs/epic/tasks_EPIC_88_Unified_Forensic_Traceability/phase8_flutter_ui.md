# Phase 8: Flutter UI & Optimistic Soft Delete

Source: Epic Phase 7.1, 7.2, and Appendix F

## Target Files (Modify)
- `client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart`
- `client_app_v2/lib/features/execution/controllers/execution_controller.dart` (or the relevant Riverpod controller managing the execution state)
- `client_app_v2/lib/l10n/app_en.arb`, `app_fi.arb` (if localization additions needed)

## Context Files (Read-Only)
- `client_app_v2/lib/features/execution/models/scorecard_dto.dart`

## Requirements
1. **Flat UI Evidence Rendering (`atom_matrix_table_widget.dart`)**:
   - Remove the old `m.quotesList.map(...)` rendering.
   - Implement nested iteration: `forensics.levelQuotes.forEach` -> Print `levelName` as a header.
   - For each `quote` inside `levelQuotes`:
     - Render the text.
     - `if (quote.isMcpVerified)`: render `Icon(Icons.verified, color: Colors.green)`.
     - `if (quote.userRejected)`: apply `TextDecoration.lineThrough` to the text and red opacity. Hide the ✕ button if already rejected.
2. **Cascading Warning**:
   - `if (m.forensics?.allEvidenceRejected == true)`: Render a `Tooltip` with a warning icon `Icon(Icons.warning, color: Colors.amber)` next to the main scorecard row Grade/Level.
3. **Soft Delete Interaction (✕ Button)**:
   - Next to each quote, add a small red ✕ button (hidden for VIEWER roles, or if already rejected).
   - On click, open `AlertDialog` asking for confirmation and optional `rejection_reason`.
   - Call `ref.read(executionControllerProvider.notifier).rejectEvidenceQuote(quoteId, reason)`.
4. **Optimistic Update (`execution_controller.dart`)**:
   - In `rejectEvidenceQuote`:
     - Make async HTTP PUT call to `PUT /api/v2/execution/executions/{id}/evidence/{evq_id}/reject`.
     - Optimistically update the state: `state = state.copyWith(...)` modifying that specific `EvidenceQuoteDto` to `userRejected: true` instantly. If it fails, revert the state and show a SnackBar.
5. **No-String Mandate**:
   - Add new strings to `.arb` files (e.g. "reject_quote_title", "reject_quote_confirm", "quote_rejected_warning").
   - Ensure the user runs `flutter gen-l10n`.

## Architectural Invariants & Hardening Mandate
- **Rule 94 (mutation_optimistic_ui)**: (Flutter Rule) MUST use Optimistic Updates paired with error rollback (`ref.invalidate()`) on failure.
- **Rule 106 (no_magic_strings_l10n)**: (Flutter Rule) Add UI strings exclusively via `.arb` files.
- **Rule 26 (monolithic_god_widgets)**: (Flutter Rule) Keep HTTP logic purely in the controller/repository, not in the widget.

## Documentation Update
Update `docs/architecture/08_dynamic_rendering_sdui.md` with details on the optimistic UI soft delete interaction.

## Testing & Quality Gate Plan
- **Widget Tests**: Ensure `AtomMatrixTableWidget` renders line-through when `userRejected` is true, and the warning icon when `allEvidenceRejected` is true.
- **Verification**: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
