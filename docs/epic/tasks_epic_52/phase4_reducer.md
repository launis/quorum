# Phase 4: Reducer Logic Verification

## Objective
Harden the MatrixReducer to ensure strict adherence to Three-State Logic (Passed, Failed, DLQ) and eliminate any implicit null states during the accumulation phase.

## Target Files
1. `c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py`
2. `c:\src\quorum\backend_v2\services\orchestrator\chunk_accumulator.py`

## Tasks
1. **Audit MatrixReducer**: Review `matrix_reducer.py`. Ensure `reduce_exists` and `reduce_all_must_comply` return exactly `PASSED`, `FAILED`, or `DLQ`.
2. **Chunk Accumulator Mapping**: Verify that `chunk_accumulator.py` correctly maps the Boolean states from the LLM outputs (`rule_satisfied: bool`) to these strict states (`PASSED`/`FAILED`) before reduction.
3. **Fail-Fast Enforcement**: If `chunk_accumulator` encounters an unexpected value or missing evidence, it should map to `DLQ` or raise an `AppException`.

## Acceptance Criteria
- `MatrixReducer` is strictly typed and robust against missing chunks.
- The Map-Reduce pipeline produces a fully deterministic final score regardless of chunking order.
