# Phase 0: Coverage Bootstrap (Golden Master) & ResultProjector Interface
Source: Epic Phase 0

## Objective
Convert all existing mocks and fixtures in `backend_v2/tests/test_data/` to match the new DTO base (`ReportDataDto`). Remove orphaned fixtures and create "Golden Master" tests (Characterization Tests) to lock in current behavior before starting Epic 92. Define abstract `ResultProjector` interface.

## Target Files (Modify)
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
1. **ResultProjector Interface**: Define abstract interface `ResultProjector` which will be responsible for converting atom-level results to `ReportDataDto`.
2. **Fixture Conversion**: Convert the existing JSON fixtures in `backend_v2/tests/test_data/` into the new `ReportDataDto` format, featuring the Flat Adjacency List pattern (`results`, `hydrated_references`). 
3. **Orphan Cleanup**: Delete any orphaned test fixtures that do not align with the new architecture.
4. **Golden Master Tests**: Create or update tests to ensure the newly formatted data is successfully parsed and validated, serving as our Golden Master for parity checks.

## Destructive Operation Inventory
- `backend_v2/tests/test_data/*`: Any obsolete V1 legacy structures inside these files will be DELETED/REPLACED with V2 `ReportDataDto` compatible payload structures.

## Bidirectional Integration Check
- Producer: The test mocks generate `ReportDataDto`.
- Consumer: The test cases ingest `ReportDataDto` and ensure validation succeeds without regression.

## Testing & Quality Gate Plan
- Command: `uv run python scripts/backend_audit_loop.py backend_v2/tests/test_data/ --test`
- Goal: Lock in 100% passing tests and record the passing test count/coverage as a `[BASELINE]` metric before handing off to the next phase.

# Session Handover Context
**Achieved:** Phase 0 planned.
**Learned:** The importance of Golden Master tests before dismantling the original engine.
**Remaining:** Execute Phase 0 and proceed to Phase 1.1.

> To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
