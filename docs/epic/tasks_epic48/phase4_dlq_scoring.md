# Phase 4: DLQ and Math Scoring Architecture

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** Strict Math Display Isolation (`01-python-backend.md`).
- **Rule 2:** Tripartite Rendering Boundary (`01-python-backend.md`). No scoring logic outside of `scoring.py`.
- **Rule 3:** No Naked Dicts in State (`01-python-backend.md`). Immutable Domain Objects.
- **Rule 4:** Stateless Workers. Do NOT pass heavy Pydantic `ValidationInfo.context` over Redis. Read via `get_storage_driver().read_file()`.

## Targets (Modify)
- `c:\src\quorum\backend_v2\utils\scoring\scoring.py` (or relevant scoring hooks)
- `c:\src\quorum\backend_v2\utils\redis_patcher.py` (for Lua atomic scripts, or wherever Arq state is kept)
- `c:\src\quorum\backend_v2\services\orchestrator\matrix_reducer.py` (CREATE/MODIFY)

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Milestones
### 1. Error Routing [x]
- [x] Ensure errors are routed correctly without catching all exceptions silently.
- [x] `PydanticSyntaxError` -> LLM Retry.
- [x] `SemanticEvidenceError` -> Direct routing to DLQ without AI reasoning.

### 2. Math Rules & Compliance Score [x]
- [x] File: `backend_v2/utils/scoring/`
- [x] Dual-Metric calculation (Safe Float Divider):
  - `Compliance Score = sum(Passed) / (total_atoms - dlq_count)`. DLQ states are dropped from the denominator.
  - `System Confidence = (total_atoms - dlq_count) / total_atoms`.
- [x] Dynamic Hard Gate: If `System Confidence` < 90%, reject matrix automatically (`FAILED_UNSCORABLE`).
- [x] Disable Passivity Penalty and Post-Hoc penalties in TDA architecture.

### 3. Map-Reduce / Three-State Logic [x]
- [x] Ensure Arq workers only receive primitives (ID, index, file path).
- [x] Fetch raw PDF via `get_storage_driver().read_file()` to leverage OS Page Cache.
- [x] Implement Asynchronous State Accumulator (Atomic Lua Script) in Redis to update `HSET` and completed-counter without Race Conditions.
- [x] Create `MatrixReducer` (Synchronous Reduction): Executed only when Lua script confirms all N chunks finished.
  - [x] `EXISTS`: `ANY(Passed) -> Passed`. `ALL(Failed) -> Failed`. Else `DLQ`.
  - [x] `ALL_MUST_COMPLY`: 1. `ANY(Failed) -> Failed`. 2. `ANY(DLQ) -> DLQ`. 3. `ALL(Passed) -> Passed`.

## Testing & Quality Gate Plan [x]
- [x] **Unit Tests:** `tests/unit/test_scoring.py`, `tests/unit/test_matrix_reducer.py` focusing on Three-state ANY/ALL logic and DLQ math.
- [x] **Integration Tests:** Test Redis Lua script concurrency.
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/[files] --test`

## Documentation Update [x]
- [x] Update `c:\src\quorum\docs\architecture\06_evaluation_and_scoring.md` with Three-State Logic math.

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-backend @[c:\src\quorum\docs\epic\tasks_epic48\phase4_dlq_scoring.md]`
