# Phase 2: Semantic Micro-Batching

## Objective
Prevent LLM Context Fatigue by standardizing chunk batch sizes to 10 atoms and guaranteeing byte-for-byte reproducibility by stripping out all non-deterministic functions like `random.shuffle()`.

## Target Files
1. `c:\src\quorum\backend_v2\hooks\atom_flattening.py`
2. `c:\src\quorum\backend_v2\services\orchestrator\chunking_service.py`
3. `c:\src\quorum\backend_v2\models\enums.py`

## Tasks
1. **Eliminate Shuffle**: Remove `rng_global.shuffle(model_list)` from `atom_flattening.py` (approx line 169).
2. **Deterministic Sort**: Replace the shuffle with a strict alphanumeric sort based on the `atom_id` hash. This ensures that every time a workflow is run with the same inputs, the chunks are formulated exactly the same.
3. **Batch Sizing**: Locate `SystemConcurrency.LLM_MAX_CHUNK_SIZE` in `enums.py` and enforce its value to `10` (if not already 10). Wait, it's currently 60, change it to 10.
4. **Chunk Integrity**: Ensure `ChunkingService.chunk_payload` respects this new max size and correctly splits the sorted `shuffled_atoms` (which should now be renamed or treated as `sorted_atoms` logically, but keep the `shuffled_atoms` variable name if it breaks external states).

## Acceptance Criteria
- `random.shuffle()` is completely removed from the flattening hook.
- Repeated executions of the same workflow yield identical `shuffled_atoms` ordering.
- Chunk sizes never exceed 10 items.
