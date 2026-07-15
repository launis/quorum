# Phase 1: Topological Engine & Deterministic Rules

Source: Epic 92, Section 4 (Phase 1)

## Context (Read-Only)
- `c:\src\quorum\backend_v2\models\enums.py` (Contains `ExecutionStatus`)
- `c:\src\quorum\client_app_v2\lib\core\models\enums.dart` (Contains `ExecutionStatus` for Flutter)
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Target (Modify)
- `c:\src\quorum\backend_v2\models\dag.py` [NEW]
- `c:\src\quorum\backend_v2\services\dag_topological_evaluator.py` [NEW]

## Milestones

### 1. Pydantic SSOT Models (`backend_v2\models\dag.py`)
- Create `CausalEdge` model:
  - `edge_reasoning` (str), `tda_id` (str), `source_id` (str), `expected_status` (ExecutionStatus default PASSED).
  - Use `ConfigDict(strict=True, frozen=True)`.
- Create `ExtractedAtom` model:
  - `reasoning` (str), `resolved_claim` (str), `source_quote` (str), `tda_id` (str, pattern `^tda_[a-fA-F0-9]{16,32}$`), `source_id` (str | None).
  - Use `ConfigDict(extra="forbid", strict=True, frozen=True)`.
- Create `LinkedAtomGraph` model:
  - `atom` (ExtractedAtom), `depends_on` (List[CausalEdge] default empty).
  - Use `ConfigDict(extra="forbid", strict=True, frozen=True)`.
- Create `AtomExecutionState` model:
  - `tda_id` (str), `status` (ExecutionStatus default PENDING), `short_circuit_reason_tda_ids` (list[str] default empty), `evaluation_reasoning` (str | None).
  - Use `ConfigDict(strict=True, frozen=True)`. All mutations must use `model_copy(update=...)`.

### 2. Topological Evaluator Service (`backend_v2\services\dag_topological_evaluator.py`)
- Implement `TopologicalEvaluator` class as a reusable SSOT engine.
- **Cycle Breaker**: Implement `networkx.simple_cycles` via `asyncio.to_thread` to detect cycles. If a cycle is detected, nodes are placed into `SYSTEM_ERROR` immediately (Fail-Fast, no silent skipping).
- **Execution Cascade**:
  - Spawn an `asyncio.Event()` and an asynchronous Task for each node inside a single `asyncio.TaskGroup`.
  - Node tasks MUST wait for parents using a sequential loop: `for parent in parents: await parent.finished_event.wait()` (Do NOT use `asyncio.gather`).
  - Implement deterministic short-circuiting (`N_A` and `BLOCKED` cascade) based on parent status.
  - Fail-Safe Boundary: Wrap execution in `try...except...finally` ensuring `finished_event.set()` is ALWAYS called in `finally` to prevent deadlocks.
- Ensure strict adherence to the 6 Core States: `PENDING`, `PASSED`, `FAILED`, `N_A`, `BLOCKED`, `SYSTEM_ERROR`.

### 3. Legacy Migration First (UI-Validation)
- Refactor the existing legacy evaluation logic (e.g., in `dag_executor.py` or equivalent) to pass through the newly created `TopologicalEvaluator` engine.
- Verify that existing functionalities run smoothly and E2E tests pass before continuing to Phase 2.

### 4. Documentation & Knowledge Base
- Add an entry in `docs\architecture\` describing the DAG Topological Evaluator.
- Create a Knowledge Item in `<appDataDir>\knowledge\` detailing how to reuse `TopologicalEvaluator` as the SSOT for all DAG evaluations.

## Testing & Quality Gate Plan
- **Unit Tests**: Create `tests\backend_v2\services\test_dag_topological_evaluator.py`. Test deterministic cascades (`N_A`, `BLOCKED`), cycle detection (`SYSTEM_ERROR`), and successful evaluations.
- **Integration Tests**: Verify legacy pipeline migration with 100% test parity.
- **Mandate**: Run the backend audit loop (`uv run python scripts/backend_audit_loop.py`). Coverage must remain above 90%.

---
# Session Handover
To execute this phase iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker: `c:\src\quorum\docs\epic\epic_92_tracker.md`
