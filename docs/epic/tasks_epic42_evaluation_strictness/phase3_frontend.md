# Epic 42: Phase 3 - Frontend (Flutter UI & Logic)

## Tavoite
Implement the Workflow-specific Strictness Level in the Dart UI, converting semantic categorizations into strict integer representations for the backend. Show strictness badges and EvidenceType icons in the Execution Report view.

## Architectural Laws (Must Follow)
- **Rule 1: Cross-Language Enum Parity.** All backend Pydantic Literals and Enums that control UI structures MUST be defined as strict `@JsonEnum()` elements in `enums.dart`.
- **Rule 2: Mutation Optimistic UI.** Use Riverpod 3.0 Mutation paradigms.
- **Rule 3: No Magic Strings L10n.** UI strings must be evaluated exclusively via `AppLocalizations` (`.arb`).

## Proposed Changes

### 1. `client_app_v2/lib/core/models/enums.dart`
**TARGET (Modify)**
- [NEW] Add `EvidenceType` enum (`EXPLICIT_QUOTE`, `IMPLIED_INTENT`, `NO_EVIDENCE`) marked with `@JsonEnum()`.
- Run `dart run build_runner build -d` to regenerate the freeezed/g files.

### 2. `client_app_v2/lib/features/execution/models/` (or wherever `ExecutionCreateDTO` / `ReportDataDTO` is)
**TARGET (Modify)**
- Update the Freezed models matching `ExecutionCreate` and `ExecutionRecord` / `ReportDataDTO` to include `int strictness_level`.
- Update `AtomResponse` (if defined in flutter) to include `EvidenceType step_1_evidence_type`, `String? step_2_quote`, `String? step_3_implicit_justification`, `String step_4_reasoning`, `bool step_5_boolean`.

### 3. `client_app_v2/lib/features/execution/views/new_execution_view.dart`
**TARGET (Modify)**
- Add a mandatory dropdown/segmented control for Strictness Level in the "Yleiset & Tulosteet" (General & Outputs) area.
- Options must be strictly linguistic: Absolute Leniency, Lenient, Balanced, Strict, Absolute Strictness.
- These map internally to integers: 0, 15, 50, 85, 100.
- Ensure the selected integer is passed as `strictness_level` in the POST request to create an execution.

### 4. `client_app_v2/lib/features/execution/views/execution_report_view.dart`
**TARGET (Modify)**
- Add a Chip/Badge in the report header displaying the used Strictness Level (e.g. "Strictness: Balanced (50)").
- In the Atom result box, display an icon representing the `EvidenceType` (e.g. checkmark icon for `EXPLICIT_QUOTE`, warning icon for `IMPLIED_INTENT`).

### 5. `client_app_v2/lib/l10n/app_en.arb` & `app_fi.arb`
**TARGET (Modify)**
- Add translations for the Strictness Level labels and UI elements.

## Verification & Quality Gate Plan
- Run `uv run python scripts/flutter_audit_loop.py client_app_v2 --build`
- Verify UI does not crash and compiles correctly.
- Test that selecting a strictness level correctly maps to the integer value in the Dart state.
