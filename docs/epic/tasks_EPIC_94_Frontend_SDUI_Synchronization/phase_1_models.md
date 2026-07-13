# Phase 1: Freezed Models Synchronization

**Source:** Epic 94, Phase 1

## Objective
Synchronize the Flutter Frontend's Dart 3 Freezed models with the new Backend `ReportDataDto` contract (Flat Adjacency List).

## Scoping
**TARGET (Modify):**
- `client_app_v2/lib/core/models/enums.dart`
- `client_app_v2/lib/features/execution/models/atom_result_dto.dart` [NEW]
- `client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart` [NEW]
- `client_app_v2/lib/features/execution/models/global_synthesis_dto.dart` [NEW]
- `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart` [NEW]
- `client_app_v2/lib/features/execution/models/execution_metrics_dto.dart` [NEW]

**CONTEXT (Read-Only):**
- `backend_v2/models/dtos/report/atoms.py`
- `backend_v2/models/dtos/report/root.py`
- `backend_v2/models/dtos/report/shared.py`

## Architectural Invariants (Injected)
- **the_zero_compromise_pledge**: All Freezed models MUST use `@JsonSerializable(disallowUnrecognizedKeys: true)`. If backend sends bad data, it must crash the parser visibly natively.
- **no_raw_string_enum_mappings**: All string literal keys from backend (like `SDUIComponentType`, `ExecutionStatus`) must map to `@JsonEnum` in `enums.dart`.
- **o1_lists**: `AtomResultDTO` arrays must use `List<AtomResultDTO>` with `@Freezed(equal: false)` to prevent deep equality jank during rendering.

## Requirements Mapping
1. **Update `enums.dart`**:
   - Add `ExecutionStatus` enum matching backend literals (`PASSED`, `FAILED`, `SYSTEM_ERROR`, etc.). Include `l10n_key` property if needed.
   - Add `SDUIComponentType` enum (`boolean_card`, `extracted_value_card`, `error_card`, `n_a_card`).

2. **Create `atom_result_dto.dart`**:
   - Map `AtomResultDTO`. Fields: `tdaId`, `status` (ExecutionStatus), `extractedData` (ExtractedValueDTO?), `sourceQuote`, `contextualOverride`, `evaluationReasoning`, `errorDetails` (ErrorDetailsDTO?), `dependsOnTdaIds`, `shortCircuitReasonTdaIds`.
   - Use `@JsonKey` mappings to ensure `snake_case` from backend resolves correctly in Dart `camelCase`.

3. **Create `hydrated_atom_dto.dart`**:
   - Map `HydratedAtomDTO`. Fields: `sduiComponent` (SDUIComponentType), `resolvedClaim`, `sourceQuote`.

4. **Create `global_synthesis_dto.dart`**:
   - Map `GlobalSynthesisDTO`. Fields: `executiveSummary`, `urgencyLevel`.

5. **Create `report_data_v2_dto.dart`**:
   - Map `ReportDataDto`. Fields: `executionId`, `workflowId`, `globalMetrics`, `globalSynthesis`, `results` (List<AtomResultDTO>), `hydratedReferences` (Map<String, HydratedAtomDTO>).

## Testing & Quality Gate Plan
- **Baseline Metric**: Since these are new classes, ensure `dart run build_runner build -d` passes without errors.
- **Unit Tests**: Create `client_app_v2/test/features/execution/models/report_data_v2_dto_test.dart` to strictly test the `fromJson` deserialization.
- **Universal Quality Gate**: Must run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models --build`

---
## Session Handover Context
**Achieved**: Defined Phase 1 plans for creating strict Freezed DTOs mirroring the Backend's flat adjacency list.
**Learned**: Backend schemas (`root.py`, `atoms.py`) strictly require `disallowUnrecognizedKeys: true`.
**Remaining**: Execution of Phase 1, followed by Phase 2 providers.

To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker (`docs\epic\EPIC_94_Frontend_SDUI_Synchronization_tracker.md`).
