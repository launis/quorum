# Epic 100 Phase 4: Unit Test Mock Migration (Batch Evaluation Recovery)

## Source: Epic 100, Phase 4

## Context
During Phase 2, `ExtractiveSensorService.evaluate_atom_boolean_batch` was rewritten to use the `BatchEvaluationResponse` format for parallel processing. However, the legacy unit tests in `test_enriched_dag_executor.py` were not updated. The tests have been silently failing or skipped because they still return a scalar mock object instead of the required batch response structure.

This phase is required to restore the 100% test coverage baseline before proceeding to Phase 5.

## Target Files (Modify)
- `tests/unit/services/orchestrator/test_enriched_dag_executor.py`

## Execution Steps

### 1. `tests/unit/services/orchestrator/test_enriched_dag_executor.py`
- **[MODIFY]**: Update the `mock_llm_executor.execute_structured_task.return_value` in all test functions.
- **Detail**:
  - `ExtractiveSensorService.evaluate_atom_boolean_batch` generates aliases sequentially per batch (e.g., `a0`, `a1`). Since our tests evaluate one node per wave (batch size 1 for a single node), the expected alias in the mock response MUST be `"a0"`.
  - Replace the old scalar `mock_result` with a structured batch response:
    ```python
    mock_eval = MagicMock()
    mock_eval.alias = "a0"
    mock_eval.is_true = True  # or False depending on the test
    mock_eval.reasoning = "mock"
    mock_eval.coaching = None
    mock_eval.falsification = None
    mock_eval.remediation_steps = None

    mock_batch = MagicMock()
    mock_batch.results = [mock_eval]

    mock_llm_executor.execute_structured_task.return_value = (mock_batch, None)
    ```
  - Apply this fix to `test_enriched_dag_happy_path` (set `is_true = True`).
  - Apply this fix to `test_enriched_dag_short_circuit_cascade` (set `is_true = False`).
  - `test_enriched_dag_blocked_cascade` and `test_enriched_dag_deadlock_prevention` mock `side_effect = Exception(...)` and do not need their return structures updated.

### 2. Validation
- Run `uv run pytest tests/unit/services/orchestrator/test_enriched_dag_executor.py` and ensure it passes (4/4 tests GREEN).

## Next Steps
Upon completion of this plan, update the tracker and proceed to Phase 5.
