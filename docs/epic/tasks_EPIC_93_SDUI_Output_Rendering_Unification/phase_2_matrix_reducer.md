# Phase 2: Matrix Reducer & Pipeline A Integration

## Goal Description
Implement the `MatrixReducer` to deterministically filter out `PASSED` boolean cards and reduce cognitive load for the final Synthesis LLM, avoiding Context Window token explosions. Integrate synthesis generation directly into Pipeline A (the DAG Executor).

## Target & Context
- **TARGET (Modify)**: 
  - `backend_v2/services/orchestrator/matrix_reducer.py` [NEW]
  - `backend_v2/services/orchestrator/dag_executor.py`
  - `backend_v2/models/dtos/lightweight_matrix.py` (If needed, create or modify)
- **CONTEXT (Read-Only)**:
  - `backend_v2/models/dtos/report/root.py`

## Proposed Changes

### `backend_v2/services/orchestrator/`
#### [NEW] [matrix_reducer.py](file:///c:/src/quorum/backend_v2/services/orchestrator/matrix_reducer.py)
- Implement `MatrixReducer` class.
- Operates on Epic 91.5's `ReportDataDto` level data, filtering out components resolved to Boolean states (`PASSED`).
- Implements Token-compression strategies (Tier 1 Soft Reduction, Tier 2 Map-Reduce Cascade) to prevent Poison Pill DLQ loops on massive data.
- Returns a strict `LightweightMatrixDTO` containing only OpaqueIDs and necessary synthesis data.

#### [MODIFY] [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)
- Wire the DAG engine to seamlessly invoke `MatrixReducer` before executing synthesis tasks.
- Eliminate dependency on the legacy `hooks/synthesis.py` for this workflow.

## Verification Plan
### Automated Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/matrix_reducer.py --test`
- Test the Token-compression cascade by mocking a massive context payload and ensuring `MatrixReducer` successfully drops unnecessary boolean texts without losing Opaque IDs.

## Documentation Mandate
- Since `MatrixReducer` establishes a new structural pattern for avoiding Context Window explosions in the DAG, a new Knowledge Item (KI) MUST be created for it.
- Target KI path: `<appDataDir>\knowledge\matrix_reducer_token_compression\artifacts\ki_matrix_reducer.md`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
