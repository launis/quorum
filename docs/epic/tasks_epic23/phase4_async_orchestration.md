# TIER 2 EXECUTION PLAN: Phase 4 - Async Orchestration & Map-Reduce (Execution)

## Objective
Implement phase 4 of Epic 23. Introduce the `TaskGroup` pattern to `strategies/llm.py` so that it can dispatch the chunks concurrently up to the fixed `MAX_CONCURRENT_LLM_STEPS` limit. Safely reduce the structured `ChunkResponseSchema` responses back into the master `state_delta` without mutating event variables in place.

## Target & Context Files
- **TARGET (Modify):** `backend_v2/services/orchestrator/strategies/llm.py`
- **TARGET (Modify):** `backend_v2/models/enums.py` (Add missing concurrency globals if needed).
- **CONTEXT (Read-Only):** `backend_v2/services/orchestrator/chunking_service.py`, `backend_v2/llm/client.py`

## Architectural Sequence
1. **Concurrency Globals:** Ensure `SystemConcurrency.MAX_CONCURRENT_LLM_STEPS` and `SystemConcurrency.LLM_MAX_RETRIES` (fixed to 2 limit) are strictly defined in `enums.py`.
2. **Orchestrator Refactor:** Inject `ChunkingService` into `strategies/llm.py`. Slice the input into chunks if size > threshold.
3. **Execution Loop:** Wrap calls in `async with asyncio.TaskGroup() as tg:` ensuring asyncio Semaphores natively map to the Enum limit ONLY.
4. **Reducer:** Safely combine the Opaque Stripe ID arrays returned by concurrent workers back into the `state_delta` event copy.

## Strict Constraints
- **System Concurrency SSOT:** API limits must be enforced via `SystemConcurrency` strict reference. Hardcoded parallel limits are permanently banned.
- **Zero-Type-Ignore Shortcuts:** `asyncio.TaskGroup` mappings must be strongly typed using `PEP 695 generics` with no `Any` types returned.
- **Fail-Fast Partial Retry limits:** Retry loop bounded exactly by `LLM_MAX_RETRIES`. Do not create infinite retry while-loops. 

## Verification & Quality Gate Plan
- Construct Async mocking tests in `tests/backend_v2/services/orchestrator/strategies/test_llm_strategy.py` mimicking hitting rate limits.
- Assert parallel calls strictly don't exceed `MAX_CONCURRENT_LLM_STEPS`.
- Run: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py`.
