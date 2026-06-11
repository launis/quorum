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
- **Rule 20 (The Self Healing Ban)**: Dynaaminen säännöllisillä lausekkeilla (Regex) korjailu on kielletty, mutta leksikaalinen joustavuus (RapidFuzz) Pydantic-rajapinnassa on sallittu arkkitehtuuripoikkeus morfologisten erojen käsittelyyn. Hallusinoidut sitaatit on silti hylättävä.
- **Rule 28 (LLM Structured Mandate)**: Direct LLM SDK calls are forbidden; route through `LLMTaskExecutor`.
- **Rule 19 (DLQ ARQ Fallback Routing)**: Bo3 consensus must route DLQ atoms correctly.
- **Rule 90 (Async IO Lock Isolation Mandate)**: Bo3 parallel execution must not deadlock.

## Implementation Steps
1. **Implement Best-of-Three Executor**: Create the `execute_best_of_three_task` logic using `asyncio.TaskGroup` guarded by the concurrency semaphore. This function will spawn exactly 3 parallel AI calls.
2. **Lexical Auditing**: Implement the validation mechanism to verify the returned `exact_quote` against the target text to reject hallucinatory matches, allowing RapidFuzz partial ratios as needed.
3. **Consensus Decision & Confidence Score**: Implement the 2/3 consensus aggregation. Laske `confidence`-arvo yksimielisyydestä: 3/3 yksimielinen = 1.0, 2/3 yksimielinen = 0.67, 1/3 tai DLQ = 0.33, ja tallenna se tulokseen.
4. **DORMANT ROUTING (CRITICAL RULE 46 & FLUTTER PARITY GUARANTEE)**: Do NOT wire this logic into the live orchestrator yet, and do NOT add schema flags (like `is_lightweight_protocol`) in this phase. Adding schema flags now would crash the Flutter app (`CheckedFromJsonException`). The executor must be built and unit-tested in isolation as "dark code", ready to be wired up during the Phase 4/5 God Commit.
5. **Poista `high_entropy`-gateway `chunk_worker.py`:stä.** Muuta logiikka siten, että ensemble laukeaa aina kaikille lightweight-evaluoinneille.
6. **Implementoi Minority Veto:** Jos yksi 3:sta ajosta palauttaa FAIL viitaten `anti_patterns`-rikkomukseen, FAIL voittaa aina riippumatta muiden tuloksesta.

## Testing & Quality Gate Plan
- **Unit Tests**: Test the consensus logic and the lexical `str.find()` rules thoroughly.
- **Universal Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier2-execute docs/epic/tasks_bilingual_schema_refactor/phase2_best_of_three_routing.md`
