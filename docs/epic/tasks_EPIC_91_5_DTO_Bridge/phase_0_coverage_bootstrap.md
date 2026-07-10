# Phase 0: Coverage Bootstrap (Golden Master) & ResultProjector Interface
Source: Epic Phase 0

## Objective
Convert all existing mocks and fixtures in `backend_v2/tests/test_data/` to match the new DTO base (`ReportDataDto`). Remove orphaned fixtures and create "Golden Master" tests (Characterization Tests) to lock in current behavior before starting Epic 92. Define abstract `ResultProjector` interface.

## Target Files (Modify)
- `backend_v2/services/orchestrator/result_projector.py` [NEW]
- `backend_v2/tests/scripts/legacy_golden_master_converter.py` [NEW]
- `backend_v2/tests/unit/test_golden_master_dto_bridge.py` [NEW]
- `backend_v2/tests/test_data/e2e_new_trace.json`
- `backend_v2/tests/test_data/exe_c0bc_inputs.json`
- `backend_v2/tests/test_data/exe_c0bc_inputs_NOISY.json`
- `backend_v2/tests/test_data/...` (any other relevant fixtures)

## Context Files (Read-Only)
- `c:\src\quorum\docs\epic\EPIC_91_5_DTO_Bridge.md`

## Architectural Invariants Injected
1. `tdd_mandate`: You MUST write Characterization Tests to lock in current behavior.
2. `zero_legacy_fallback_hacks`: Fixtures MUST strictly adhere to the new V2 spec without loose fallbacks.
3. `mocking_mandate_for_llm`: All test data must remain local, no live HTTP calls to LLMs during these tests.
4. `test_coverage_prerequisite`: The test suite must be green against the new DTO structure before any domain extraction begins (Zero Behavioral Change).

## Proposed Changes
1. **ResultProjector Interface**: Define abstract interface `ResultProjector` in `backend_v2/services/orchestrator/result_projector.py` which will be responsible for converting atom-level results to the new `ReportDataDto`.
2. **Automated Fixture Conversion Script**: Create a temporary programmatic script (`legacy_golden_master_converter.py`) to run the existing V1 JSON fixtures (e.g., the massive 2.1MB files) through the `ResultProjector` to automatically generate the new `ReportDataDto` formats. Manual conversion of these files is strictly prohibited due to size and complexity.
3. **Orphan Cleanup**: Delete any orphaned test fixtures that do not align with the new architecture.
4. **Golden Master Tests**: Create `backend_v2/tests/unit/test_golden_master_dto_bridge.py` to ensure the newly formatted data is successfully parsed and validated, serving as our Golden Master for parity checks.

## Destructive Operation Inventory
- `backend_v2/tests/test_data/*`: Any obsolete V1 legacy structures inside these files will be DELETED/REPLACED with V2 `ReportDataDto` compatible payload structures.

## Bidirectional Integration Check
- Producer: The test mocks generate `ReportDataDto`.
- Consumer: The test cases ingest `ReportDataDto` and ensure validation succeeds without regression.

## Testing & Quality Gate Plan
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_golden_master_dto_bridge.py --test`
- Goal: Lock in 100% passing tests and record the passing test count/coverage as a `[BASELINE]` metric before handing off to the next phase.

# Session Handover Context
**Achieved:** Tier 0 Research & Analysis completed. Validated Phase 0 Implementation Plan. Corrected catastrophic manual JSON data entry by defining an automated script legacy_golden_master_converter.py.
**Learned:** Massive JSON fixtures (2.1MB) cannot be manually converted. We must use an automated script to pass V1 engine output through the new ResultProjector.
**Remaining:** Execute Phase 0 Implementation Plan.

> To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
