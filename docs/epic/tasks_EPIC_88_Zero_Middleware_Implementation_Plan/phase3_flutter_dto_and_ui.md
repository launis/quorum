# Phase 3: Flutter DTO & UI Modernization

Source: Epic 88, Step 3.

## Proposed Changes

### Target Files
- `client_app_v2/lib/features/execution/models/scorecard_dto.dart`
- `client_app_v2/lib/features/execution/widgets/scorecard_matrix_row.dart` (and related row UI widgets)

### Context Files
- `client_app_v2/lib/core/models/enums.dart`

### Task Details
1. **Flutter DTO Modernization**:
   - [DELETE] `EvidenceQuoteDto`, `LevelQuotesDto`, `RowForensicsDto` from `scorecard_dto.dart`.
   - [NEW] Create `ScorecardAtomDto` mapping exactly to the backend's new schema.
   - [MODIFY] Update `MatrixScorecardRowDto`: remove `quotesList` and `rowForensics`, add `evaluatedAtoms: List<ScorecardAtomDto>` and `clusteredRowSources: List<MCPAuditTrace>`.
2. **Smart Getter UI Grouping**:
   - [MODIFY] Inside `MatrixScorecardRowDto`, add a smart getter property (e.g., `Map<int, List<ScorecardAtomDto>> get atomsByLevel`) to group the flat `evaluatedAtoms` list by `level` at runtime, enabling efficient UI drawing.
3. **UI Widget Updates**:
   - [MODIFY] Update `ScorecardMatrixRow` (and its children) to draw exclusively from `atomsByLevel`.
   - If an atom's `status` indicates it was skipped/none, render the explicit "Ei arvioitu / Skipped" state.

## Architectural Mandates & Hardening
- **silent_json_fallbacks**: Using fallback defaults for missing server data is banned. Ensure 100% strict JSON conformity (`disallow_unrecognized_keys: true`). Missing data MUST crash the Freezed parser.
- **freezed_when_ban**: Use Dart 3 native `switch` expressions instead of Freezed `.when()` or manual `if-else` chains.
- **frontend_zero_db_hardcoding_mandate**: Flutter UI MUST NOT know about specific database record identifiers. Rendering must be purely driven by schema types.

## Testing & Quality Gate Plan
- **Unit Tests**: Run `flutter test` targeting JSON serialization and deserialization of the new `ScorecardAtomDto` to ensure strict conformity.
- **Verification Command**:
  `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`

<!-- Session Handover -->
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target c:\src\quorum\docs\epic\EPIC_88_Zero_Middleware_Implementation_Plan_tracker.md`
