# Phase 2: Kognitio-Reititys ja Best-of-Three Flash (Jälki-Epic C)
Source: Epic Jälki-Epic C: Kognitio-Reititys ja Best-of-Three Flash

## Objective
Implement task routing between "Lightweight" and "Deep Analysis" protocols, and introduce a 2/3 Best-of-Three execution strategy using `asyncio.TaskGroup`. This is executed early as it provides immediate cost/stability benefits without breaking the existing schema.

## Targets (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution/execution_strategy.py` (or equivalent execution orchestrator file)
- `backend_v2/llm/llm_task_executor.py`

## Context (Read-Only)
- `backend_v2/models/dtos/lightweight_matrix.py`

## Architectural Invariants
- **Rule 61 (TaskGroup Mandate)**: Use `asyncio.TaskGroup`, NOT `asyncio.gather`.
- **Rule 32 (System Concurrency)**: Use `asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS)`.
- **Rule 130 (Strict Physical Anchoring Mandate)**: Lexical auditing MUST use deterministic `str.find()`. `RapidFuzz` or heuristic searching is strictly FORBIDDEN.
- **Rule 28 (LLM Structured Mandate)**: Direct LLM SDK calls are forbidden; route through `LLMTaskExecutor`.

## Implementation Steps
1. **Implement Best-of-Three Executor**: Create the `execute_best_of_three_task` logic using `asyncio.TaskGroup` guarded by the concurrency semaphore. This function will spawn exactly 3 parallel AI calls.
2. **Lexical Auditing**: Implement the strict `str.find()` mechanism to verify the returned `exact_quote` against the target text to reject hallucinatory matches.
3. **Consensus Decision**: Implement the 2/3 consensus aggregation.
4. **DORMANT ROUTING (CRITICAL RULE 46 & FLUTTER PARITY GUARANTEE)**: Do NOT wire this logic into the live orchestrator yet, and do NOT add schema flags (like `is_lightweight_protocol`) in this phase. Adding schema flags now would crash the Flutter app (`CheckedFromJsonException`). The executor must be built and unit-tested in isolation as "dark code", ready to be wired up during the Phase 4/5 God Commit.

## Testing & Quality Gate Plan
- **Unit Tests**: Test the consensus logic and the lexical `str.find()` rules thoroughly.
- **Universal Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase2_best_of_three_routing.md`
