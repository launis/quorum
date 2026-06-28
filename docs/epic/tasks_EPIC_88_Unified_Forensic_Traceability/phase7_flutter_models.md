# Phase 7: Flutter Frontend DTOs

Source: Epic Phase 3.1 and Appendix F.1

## Target Files (Modify)
- `client_app_v2/lib/features/execution/models/scorecard_dto.dart` (or wherever `MatrixScorecardRowDto` resides)
- `client_app_v2/lib/features/execution/models/scorecard_dto.freezed.dart` [GENERATED]
- `client_app_v2/lib/features/execution/models/scorecard_dto.g.dart` [GENERATED]

## Requirements
1. **New DTOs**:
   - Create `EvidenceQuoteDto` (Freezed model).
     - `id`: String
     - `text`: String
     - `sourceReference`: String?
     - `userRejected`: bool (default false)
     - `rejectionReason`: String?
     - `isMcpVerified`: bool (default false)
   - Create `LevelQuotesDto` (Freezed model).
     - `level`: int
     - `levelName`: String
     - `quotes`: List<EvidenceQuoteDto> (default empty list)
   - Create `RowForensicsDto` (Freezed model).
     - `levelQuotes`: List<LevelQuotesDto> (default empty list)
     - `allEvidenceRejected`: bool (default false)
2. **Update ScorecardRow**:
   - In `MatrixScorecardRowDto` (or equivalent), replace the old `quotesList: List<String>?` with `forensics: RowForensicsDto?` (nullable to support old executions).
3. **Code Generation**:
   - You MUST instruct the user to run `dart run build_runner build -d` in the `client_app_v2` directory to regenerate the serialization code.

## Architectural Invariants & Hardening Mandate
- **Rule 18 (silent_json_fallbacks)**: (Flutter Rule) Ensure `disallow_unrecognized_keys: true` or strict JSON conformity. Do not use silent empty string fallbacks for missing critical data.
- **Rule 181 (manual_code_generation_crises)**: (Flutter Rule) Do NOT try to modify `.g.dart` or `.freezed.dart` manually. Demand the user to run the build runner.

## Documentation Update
Update `docs/architecture/07_desktop_first_flutter.md` regarding the new deep forensics DTO structures in the client.

## Testing & Quality Gate Plan
- **Integration Tests**: Verify that `MatrixScorecardRowDto.fromJson()` correctly parses the new `forensics` JSON payload from the backend.
- **Verification**: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/scorecard_dto.dart --build`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
