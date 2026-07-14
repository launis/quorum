# Epic 91.5 Phase B3: Golden Master E2E Test

## Objective
Implement a robust Golden Master End-to-End (E2E) integration test for the new `v2_core.ReportDataDTO` architecture. This test will mathematically guarantee that the `ExecutionRecord -> ReportDataDTO -> SduiMapper -> ReportView` pipeline works holistically without regressions.

## Context & Architectural Mandates
- **Golden Master Mandate:** The Epic requires that before deleting legacy structures, the new architecture must have its own characterization test proving parity.
- **Fail-Fast:** All DTOs must be explicitly validated during the test.

## Target Files (Modify)
- `backend_v2/tests/integration/test_epic_chain_e2e.py`

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py`
- `backend_v2/services/execution.py`
- `backend_v2/services/sdui_mapper_service.py`

## Proposed Changes

### 1. Update `backend_v2/tests/integration/test_epic_chain_e2e.py`
- **Mock Execution Environment:** Setup an `ExecutionRecord` populated with realistic `ScorecardAtomDTO`s and a mock `OutputProfile`.
- **Pipeline Execution:** Ensure the test triggers the full parsing, DAG logic (if applicable or mock the DAG output), and explicitly tests the creation of `v2_core.ReportDataDTO` and the `ReportView`.
- **Deep Assertions:** Verify that `ReportDataDTO.layouts` are successfully mapped to `ReportView.sections` via the `SduiMapperService`.

## Testing & Quality Gate Plan
- Execute the Universal Quality Gate (`scripts/backend_audit_loop.py backend_v2/tests/integration/test_epic_chain_e2e.py --test`).

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
