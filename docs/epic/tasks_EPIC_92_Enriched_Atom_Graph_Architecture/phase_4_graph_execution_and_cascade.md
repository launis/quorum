# Phase 4: The Graph Execution & Cascade (Full System Test)

Source: Epic Phase 4, Step 3.6 & 3.4

## Objective
To combine the Phase 1 `TopologicalEvaluator` and Phase 3 `LinkedAtomGraph` builder into a unified asynchronous DAG Execution pipeline. This handles the cascading `TaskGroup` logic, node-level wait locks, and Fail-Fast DLQ error routing.

## Architectural Rules Injected
- **01-python-backend.md: TaskGroup ExceptionGroup Mandate:** Use `asyncio.TaskGroup`. `asyncio.gather` is banned to prevent zombie tasks on failure.
- **01-python-backend.md: DLQ Arq Fallback Routing:** If a worker crashes, catch exception, signal `finished_event.set()` in `finally:` block, and route to DLQ status (`SYSTEM_ERROR`).
- **Epic 92: Node-Level Wait:** Use `for parent in parents: await parent.finished_event.wait()` instead of `asyncio.gather()` for waiting on dependencies to avoid deadlocks.

## Proposed Changes

### Target: `backend_v2/services/orchestrator/enriched_dag_executor.py` [NEW]
- Create `EnrichedDagExecutor` service.
- **Input:** `list[LinkedAtomGraph]` (The fully validated graph from Phase 3).
- **Execution Engine:**
  - Create global `asyncio.Event` for each `tda_id`.
  - Span an `asyncio.TaskGroup`.
  - For each `LinkedAtomGraph`, spawn a task `_execute_node(node)`.
  - **_execute_node Logic:**
    - `try`:
      - Wait for all parents: `for edge in node.depends_on: await events[edge.tda_id].wait()`.
      - **Cascade Check:** Inspect states of parents. If any parent is `SYSTEM_ERROR` or `BLOCKED`, set this node to `BLOCKED`. If parent status != `expected_status`, set to `N_A` (Short-Circuit) and log `short_circuit_reason_tda_ids`.
      - If parents passed, call `TopologicalEvaluator` (Phase 1) or `ExtractiveSensorService` to determine `PASSED`/`FAILED`.
    - `except Exception`: Catch all, set state to `SYSTEM_ERROR`.
    - `finally`: `events[node.atom.tda_id].set()` (CRITICAL: Deadlock prevention).

### Target: `backend_v2/services/orchestrator/extractive_sensor_service.py` [MODIFY]
- If exists, update to handle Boolean LLM evaluation (True/False) for the `TopologicalEvaluator` to rely on, ensuring it doesn't do complex JSON but just Boolean classification (Best-of-Three if needed).

## Verification & Quality Gate
- **Unit Tests:** `tests/unit/services/orchestrator/test_enriched_dag_executor.py` with mocked sensor results to test:
  - Happy path (all PASSED).
  - Short-circuit cascade (Parent FAILED -> Child N_A).
  - Blocked cascade (Parent SYSTEM_ERROR -> Child BLOCKED).
  - Deadlock prevention (Mock exception in parent, ensure child unblocks and becomes BLOCKED).
- **Universal Quality Gate:** Run `backend_audit_loop.py`.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
