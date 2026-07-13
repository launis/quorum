# Phase 0: End-to-End Golden Master Test

## Goal Description
Implement an end-to-end integration test (`test_epic_chain_e2e.py`) to verify the data flow from `seed_data.json` → DAG (Epic 92) → ResultProjector → ReportDataDto (Epic 91.5) → SDUI Mapper (Epic 93) → SduiComponent tree. This ensures the foundational DTO bridge and DAG engine correctly propagate data without degradation before we start unifying the outputs and destroying legacy code.

## Target & Context
- **TARGET (Modify)**: 
  - `backend_v2/tests/integration/test_epic_chain_e2e.py` [NEW]
- **CONTEXT (Read-Only)**:
  - `backend_v2/seed/seed_data.json`
  - `backend_v2/models/dtos/report/root.py`

## Proposed Changes

### `backend_v2/tests/integration/`
#### [NEW] [test_epic_chain_e2e.py](file:///c:/src/quorum/backend_v2/tests/integration/test_epic_chain_e2e.py)
- Create a comprehensive Golden Master test that mocks the LLM (using `backend_v2/llm/mock.py`) and executes a full workflow.
- Ensure the test asserts that `ReportDataDto` is correctly generated and that no legacy fallbacks are triggered.
- Assert that the final SDUI component tree translates the DTO accurately without data loss.

## Verification Plan
### Automated Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/integration/test_epic_chain_e2e.py --test`
- MUST record the passing test count and coverage as a `[BASELINE]` metric before proceeding to Phase 1.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
