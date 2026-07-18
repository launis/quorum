# Implementation Plan: Phase 1, 2, & 4 - Extractive Sensor Bo3 Architecture

## Goal Description
Refactor the `ExtractiveSensorService.evaluate_atom_boolean_batch` to wrap the evaluation batch in an `asyncio.TaskGroup` for Best-Of-Three ensemble processing using the `"fast"` strategy. Implement a strict consensus resolver (`resolve_majority_vote`) to form 2/3 majorities and appropriately route transient failures vs semantic splits to DLQ.

## Open Questions
None.

## Red-Team Audit Notes
- **Invalid Semantic Split Logic**: The plan previously mentioned a `NEEDS_REVIEW` status. `ExecutionStatus` for boolean TDA only yields `PASSED` or `FAILED`. A 2/3 consensus failure (split) only happens if exactly 1 call drops/fails transiently AND the remaining two disagree (1 `PASSED`, 1 `FAILED`).
- **Semaphore Restored**: A previous audit incorrectly removed the `asyncio.Semaphore` assuming it was redundant. However, cross-referencing `05_llm_architecture.md` confirms it is an explicit architectural mandate (`ensemble_parallel_evaluation_mandate`) acting as a Micro-Level Concurrency Exemption against the global macro-level locks. It has been restored.
- **Import Note**: `_is_transient_llm_error` must be imported from `backend_v2.llm.provider`.

## User Review Required
- None.

## Architectural Invariants Injected
- `ensemble_parallel_evaluation_mandate`: Use `asyncio.TaskGroup` for parallel Best-of-3 ensemble calls.
- `taskgroup_exceptiongroup_mandate`: Use `asyncio.TaskGroup` over `asyncio.gather`.
- `dlq_arq_fallback_routing`: TaskGroup exceptions must be handled; transient errors should be returned as sentinels inside the group rather than crashing it.
- `strict_physical_anchoring_mandate`: Handled downstream, but semantic splits and dropouts MUST trigger `SYSTEM_ERROR`.

## Scope
- TARGET (Modify): `backend_v2/services/orchestrator/extractive_sensor_service.py`
- TARGET (New): `tests/unit/services/orchestrator/test_extractive_sensor_service.py`
- CONTEXT (Read-Only): `backend_v2/settings.py`

## Proposed Changes

### Business Logic
#### [MODIFY] [extractive_sensor_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/extractive_sensor_service.py)
- In `evaluate_atom_boolean_batch()`, introduce a localized `asyncio.Semaphore(get_settings().ensemble_parallelism)` to limit micro-concurrency and prevent global locks per the `ensemble_parallel_evaluation_mandate`.
- Refactor the main LLM call `executor.execute_structured_task()` inside a new private `async def _single_ensemble_call` helper method inside the function block.
- The `_single_ensemble_call` MUST catch transient network errors (`AgentExecutionError`, `_is_transient_llm_error`) and return `None` rather than crashing.
- Execute `get_settings().ensemble_parallelism` copies of `_single_ensemble_call` within an `asyncio.TaskGroup`.
- Implement `@staticmethod def resolve_majority_vote(expected_tda_ids: list[str], results: list[dict | None]) -> dict`:
  - Calculate tally per `tda_id`.
  - If a single status >= `get_settings().ensemble_min_consensus`, elect it.
  - If total valid results < 2 due to transient errors, RAISE `AgentExecutionError` so Arq retries the entire batch step.
  - If results are semantically split without a majority (e.g., 1 PASSED, 1 FAILED, and 1 transiently missing) or the LLM dropped the ID across multiple calls, return `ExecutionStatus.SYSTEM_ERROR` with `"INSUFFICIENT_CONSENSUS"`.

### Testing
#### [NEW] [test_extractive_sensor_service.py](file:///c:/src/quorum/tests/unit/services/orchestrator/test_extractive_sensor_service.py)
- Create pytest suite mocking `gemini-2.5-flash` responses via `backend_v2/llm/mock.py`.
- Tests to include: 
  - 2/3 consensus logic (3 valid results, 2 agree).
  - 1-fail resilience (1 transient timeout, 2 valid results -> consensus).
  - 2-fail transient bubble-up (2 timeouts, <2 valid -> raise AgentExecutionError).
  - Missing-key DLQ scenario (LLM hallucinates and drops key -> SYSTEM_ERROR).

## Testing & Quality Gate Plan
### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test` to enforce strict formatting, coverage, and ensure the unit tests pass correctly.

## Documentation & Knowledge Item Mandate
- Ensure a KI for `TDA Best-Of-Three Flash Architecture` exists or instruct the execution agent to create/update it in the IDE's Knowledge Base.

---
## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
