# Phase 3: The Facade (Koordinaattorin kasaus) [x] COMPLETE

## Objective
Refactor the original `LLMNodeStrategy.execute()` method in `llm.py` to act solely as a Facade/Coordinator. Replace the 300+ lines of nested logic by importing and utilizing the newly created `ContextBuilder`, `PromptFactory`, and `ChunkWorker` classes.

## Scope

### CONTEXT (Read-Only)
- `backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py`
- `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- `backend_v2/services/orchestrator/chunk_accumulator.py`

### TARGET (Modify)
- `backend_v2/services/orchestrator/strategies/llm.py` [MODIFY]

## Implementation Steps

### 1. Refactoring `LLMNodeStrategy.execute()`
- **Initialization:** Keep the existing initialization, `StateProjector` validation, and pre-hooks exactly as they are.
- **Step 1 - Context Building:** Delegate token limitation, dot notation resolution, and mapping logic to `ContextBuilder`.
- **Step 2 - Prompt Construction:** Pass the validated context and blocks to `PromptFactory` to get the final `user_payload`, dynamic schema, and `atom_to_block_ids`.
- **Step 3 - Chunk execution setup:** Keep the logic to calculate `chunks_list` and retrieve the `bound_client`.
- **Step 4 - Map-Reduce (ChunkWorker):** Replace the inline `process_chunk` function with a clean `asyncio.TaskGroup()` loop calling `ChunkWorker.execute_chunk(...)`. The semaphore logic must be respected.
- **Step 5 - Accumulation & Hooks:** Pass the results from `ChunkWorker` into the existing `ChunkAccumulator`, perform the metadata merge, run post-hooks, and return the `TraceEvent` array.

### 2. Code Cleanup
- Remove all the migrated logic from `llm.py`.
- Ensure imports are at the module level (Global Imports only), preventing any circular dependencies.
- Verify that `llm.py` now reads strictly as a sequence of high-level operations (Facade pattern).

## Verification & Quality Gate Plan
- **Integration Validation:** Run the full test suite for LLM strategies to confirm that the Facade produces identical output to the original God Method.
- **Quality Gate:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --openapi`
- **Quality Gate (All):** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/ --test`
