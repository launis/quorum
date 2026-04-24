# Phase 2: Resolving Naked Dict Map-Reduce Aggregation

## Objective
Eliminate the generic dictionary map-reduce accumulation inside `LLMNodeStrategy.execute` (the `for t in tasks:` loop). Adhering to the Zero-Compromise and Duct-Tape Ban mandates, we will introduce a typed `ChunkAccumulator` service and `ExecutionChunk` model. This prevents implicit string concatenation of random matrix blocks and provides strong type safety during LLM orchestration.

## Architecture Sequence
1. **Pydantic Models**: Define `ExecutionChunk` and `ChunkAccumulator` (e.g. in `backend_v2/models/dtos/orchestrator.py` or a dedicated accumulator service).
2. **API/Service**: Replace the naked dict accumulator in `LLMNodeStrategy` with the new typed accumulator.

## Scope Definitions
### TARGET (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\llm.py`
- `c:\src\quorum\backend_v2\services\orchestrator\chunk_accumulator.py` (New file)
- `c:\src\quorum\backend_v2\tests\unit\test_chunk_accumulator.py` (New file)

### CONTEXT (Read-Only)
- `c:\src\quorum\docs\epic\epic32_llm_orchestrator_zero_compromise.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Implementation Steps
1. Create `backend_v2/services/orchestrator/chunk_accumulator.py`.
2. Define a `ChunkAccumulator` class providing an `add(chunk: dict[str, Any])` method or similar, strongly typing the internal `final_state` logic.
3. Replace the `for t in tasks: ...` dictionary mutations inside `LLMNodeStrategy.execute` with `accumulator = ChunkAccumulator()`, followed by `accumulator.add(c_final)` and fetching `accumulator.get_final_result()`.
4. Ensure `matrix_` and `blk_` elements are aggregated correctly without assuming all sub-values are strings.
5. Move the pure dictionary merging logic into isolated testable pure functions within `ChunkAccumulator`.

## Verification & Quality Gate Plan
- **New Unit Tests:** `backend_v2/tests/unit/test_chunk_accumulator.py` using `mock.py` fixtures simulating fragmented chunking outputs. Verify that nested structures merge accurately and do not raise `TypeError`.
- **Audit Tooling:** 
  - `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py backend_v2/services/orchestrator/chunk_accumulator.py backend_v2/tests/unit/test_chunk_accumulator.py --test`
- **Criteria:** 0 Warnings on Ruff, 100% Strict Type Coverage (Mypy), and Pytest coverage for the isolated accumulator logic.
