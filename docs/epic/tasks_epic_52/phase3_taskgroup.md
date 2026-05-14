# Phase 3: TaskGroup Concurrency Refactor

## Objective
Ensure the Fail-Fast Map-Reduce orchestration pattern leverages modern `asyncio.TaskGroup` for high-throughput concurrency, maintaining absolute atomic limits via `asyncio.Semaphore`.

## Target Files
1. `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py`
2. `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm_execution\chunk_worker.py`

## Tasks
1. **Audit TaskGroup**: Review the current TaskGroup usage in `llm.py` (approx line 337). Ensure `async with asyncio.TaskGroup() as tg:` correctly handles task exceptions and propagates `AppException` reliably without deadlocking.
2. **Enforce Semaphore**: Verify that the semaphore `sem = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)` is passed correctly and strictly limits simultaneous LLM executions across the chunk workers.
3. **Anomaly Circuit Breaker**: Confirm that the circuit breaker semantics (checking `llm_anomaly_retry_requested`) remain intact and gracefully cancel remaining tasks if a fatal error occurs in one chunk.

## Acceptance Criteria
- `asyncio.TaskGroup` is the sole concurrency mechanism for non-Redis chunk execution.
- Max concurrency does not exceed `MAX_CONCURRENT_LLM_STEPS`.
- Error in one chunk correctly cancels the TaskGroup.
