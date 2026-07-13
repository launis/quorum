# Phase 1.1: SSOT Models & Topological Evaluator Core

## Goal
Establish the SSOT domain models for the Enriched Atom Graph (`LinkedAtomGraph`, `AtomExecutionState`, etc.) and build the `TopologicalEvaluator` engine that resolves these graphs using `TaskGroup` cascade and deterministic cycle breaking.

## Context (Read-Only)
- `backend_v2/models/enums.py` (ExecutionStatus)

## Target (Modify)
- `[NEW] backend_v2/models/dtos/dag_models.py`
- `[NEW] backend_v2/services/orchestrator/topological_evaluator.py`
- `[NEW] backend_v2/tests/unit/services/orchestrator/test_topological_evaluator.py`

## Destructive Operation Inventory
- None (Additive phase)

## Architectural Rules Injected
- **01-python-backend.md**: Strict Pydantic V2 config (`extra='forbid', strict=True, frozen=True`). TaskGroup ExceptionGroup Mandate. Zero Duct-Tape Ban.
- **00-antigravity-core.md**: SSOT Reuse Mandate. Fail-Fast.

## Implementation Steps
1. **DAG Models (`dag_models.py`)**:
   - Create `CausalEdge` with `edge_reasoning`, `tda_id`, `source_id`, `expected_status` (default to `ExecutionStatus.PASSED`).
   - Create `ExtractedAtom` with `reasoning`, `resolved_claim`, `source_quote`, `tda_id` (Regex pattern `^tda_[a-fA-F0-9]{16,32}$`), `source_id`.
   - Create `LinkedAtomGraph` with `atom`, `depends_on`.
   - Create `AtomExecutionState` with `tda_id`, `status` (`ExecutionStatus`), `short_circuit_reason_tda_ids`, `evaluation_reasoning`.
   - Ensure all inherit from `BaseModel` with strict immutable config (`frozen=True`).
2. **Topological Evaluator (`topological_evaluator.py`)**:
   - Create `TopologicalEvaluator` service class.
   - Implement deterministic graph validation: cycle detection using `networkx.simple_cycles()` (must be executed in `await asyncio.to_thread()` to prevent Event Loop freezing) or equivalent O(V+E) logic.
   - If cycle detected, set all involved nodes to `SYSTEM_ERROR` (Reason: `CYCLIC_DEPENDENCY_DETECTED`).
   - If phantom edges are detected (reference to missing node), set child node to `SYSTEM_ERROR` (Reason: `UNRESOLVED_DEPENDENCY`).
   - Implement `TaskGroup` async execution with `asyncio.Event()` for parent-child synchronization.
   - Child tasks wait for parent events (`await parent.finished_event.wait()`). Do NOT use `asyncio.gather`.
   - Parent priority matrix: if parent is `SYSTEM_ERROR` or `BLOCKED`, child becomes `BLOCKED`. If parent status != expected, child becomes `N_A` (Short-Circuit) and records parent's `tda_id` in `short_circuit_reason_tda_ids`.
   - Ensure `finally` block ALWAYS calls `finished_event.set()` to prevent deadlocks on DLQ / unhandled exceptions.
3. **Unit Tests (`test_topological_evaluator.py`)**:
   - Test cycle breaking isolating the cycle to `SYSTEM_ERROR`.
   - Test short-circuit `N_A` propagation cascade.
   - Test `BLOCKED` propagation cascade.
   - Test successful parallel execution without deadlocks.

## Testing & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --test`
- [BASELINE] Record passing test count and coverage before proceeding to Phase 1.2.

---
**Session Handover**
To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
