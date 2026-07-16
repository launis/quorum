# Epic 100 Phase 2: Micro-Prompt Batching & Wave Evaluation

## Source: Epic 100, Phase 2

## Architectural Invariants
- **Deterministic Wave Evaluation**: Kahn's Algorithm for topological sorting without `asyncio.Event` timeouts.
- **Cache Survival Strategy**: Prefix-Aware Batching in the prompt (heavy text strictly at the top).
- **Atomic Batch Failure & Transient Retry**: Validate via `_is_transient_llm_error` (from `backend_v2.llm.provider`) to preserve retry logic for 503/429.
- **Alias-Mapped Determinism**: Use `AliasEngine` to register short aliases (`a0`, `a1`...) before prompt compilation and `AliasEngine.resolve_alias()` during response hydration.

> [!IMPORTANT]
> **Epic 3.4 vs 3.2 Contradiction Resolution**: The Epic's section 3.4 states that the `TopologicalEvaluator` "MUST remain untouched", while section 3.2 explicitly mandates Kahn's Algorithm refactoring *inside* `TopologicalEvaluator`. **Resolution**: Section 3.2 is the detailed functional design and takes precedence. The intent of section 3.4 is that the `TopologicalEvaluator`'s SSOT role for DAG cascade logic must be preserved — i.e., the macro-level `DAGExecutor` (`dag_executor.py`) must not be modified. The `TopologicalEvaluator` itself IS the target of the Kahn's Algorithm refactoring. However, **batch size slicing** (splitting waves into groups of 15) MUST happen in `EnrichedDagExecutor`, NOT in `TopologicalEvaluator`. The evaluator yields complete topological waves; the executor slices them.

## Target Files (Modify)
- `backend_v2/settings.py`
- `backend_v2/services/orchestrator/topological_evaluator.py`
- `backend_v2/services/orchestrator/extractive_sensor_service.py`
- `backend_v2/services/orchestrator/enriched_dag_executor.py`

## Context Files (Read-Only)
- `backend_v2/llm/client.py`
- `backend_v2/services/llm_task_executor.py`

## Proposed Changes

### 1. `backend_v2/settings.py`
- **[MODIFY]**: Add `sensor_batch_size`.
- **Detail**:
  ```python
  sensor_batch_size: Annotated[int, Field(description="Max atoms per Boolean evaluation batch to avoid rate limits")] = 15
  ```

### 2. `backend_v2/services/orchestrator/topological_evaluator.py`
- **[MODIFY]**: Rewrite `evaluate_graph` to implement Kahn's Algorithm (Wave-Based Evaluation).
- **Detail**:
  - Remove `asyncio.Event` logic used for resolving dependencies concurrently.
  - Calculate in-degrees and build an adjacency list (parent -> children).
  - Collect all nodes with `in_degree == 0` into the first wave.
  - **CRITICAL DAG DEADLOCK & SHORT-CIRCUIT MITIGATION**: 
    1. Filter the wave to find nodes that are strictly `PENDING`. Yield this list to the `batch_evaluation_callback`.
    2. After the callback resolves the wave, you MUST iterate through all nodes in the current wave and propagate state to their children in the adjacency list.
    3. If a parent's state is `SYSTEM_ERROR` or `BLOCKED`, the child becomes `BLOCKED`. If the parent's state does not match the edge's `expected_status`, the child becomes `N_A` (short-circuited).
    4. You MUST decrement the `in_degree` of the child regardless of whether it was short-circuited or not. If `in_degree == 0`, append to the next wave.
  - The callback signature changes to a `batch_evaluation_callback` taking `list[LinkedAtomGraph]` instead of a single node.
  - **The evaluator MUST NOT import `get_settings()` or enforce batch sizes**. It yields full waves. Batch slicing into groups of `sensor_batch_size` happens downstream in `EnrichedDagExecutor`.
- **Destructive Operation Inventory**:
  - INTENTIONALLY DROPPED: `asyncio.Event` based `asyncio.TaskGroup` node evaluation loop. Reason: Replaced entirely by Kahn's deterministic wave-based topological sort.

### 3. `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **[MODIFY]**: Refactor `evaluate_atom_boolean` into `evaluate_atom_boolean_batch`.
- **Detail**:
  - Accept `list[LinkedAtomGraph]` instead of a single node.
  - Modify `BooleanEvaluationResult` to include `alias` (e.g., `a0`) for each evaluation. 
  - **CRITICAL LLM SCHEMA MITIGATION**: The `execute_structured_task` requires a strict `BaseModel` subclass. You CANNOT pass a bare `list`. You MUST wrap the results in a root model: `class BatchEvaluationResponse(BaseModel): results: list[BooleanEvaluationResult]`.
  - Use `AliasEngine.register()` to create short aliases for each atom's `tda_id` before prompt compilation. After LLM response, use `AliasEngine.resolve_alias()` to hydrate back to real `tda_id` values.
  - Compile the prompt ensuring `context_text` (the massive document) is at the absolute top (Prefix-Aware Caching) and the batched claims are listed dynamically at the bottom.
  - Iterate over the **requested** batch (sent aliases), NOT the returned batch. Any alias missing from the LLM response MUST be marked `ExecutionStatus.SYSTEM_ERROR`.

### 4. `backend_v2/services/orchestrator/enriched_dag_executor.py`
- **[MODIFY]**: Update implementation to supply a `batch_evaluation_callback` and handle batch slicing.
- **Detail**:
  - Receive complete topological waves from `TopologicalEvaluator`. Slice each wave into sub-batches of `get_settings().sensor_batch_size` (15) atoms. This keeps LLM-specific config out of the DAG evaluation layer.
  - **CRITICAL CONCURRENCY MITIGATION**: You MUST use an `asyncio.TaskGroup` to execute these sub-batches concurrently. Do NOT execute the sub-batches sequentially, as that defeats the radical speedup goal.
  - Provide a `batch_evaluation_callback` to `TopologicalEvaluator` that fans out the sub-batches to `ExtractiveSensorService.evaluate_atom_boolean_batch` via the `TaskGroup`.
  - Handle transient vs persistent errors (Atomic Batch Failure). Import and validate via `_is_transient_llm_error` from `backend_v2.llm.provider`.
  - If a transient network error occurs, bubble it up for Arq retry. If it's a persistent schema extraction failure (ValidationError), mark all requested atoms in the batch as `ExecutionStatus.SYSTEM_ERROR`.

## Testing & Quality Gate Plan
1. **Unit Tests**:
   - Update `test_topological_evaluator.py` to assert the wave-based topological sort outputs correct sequence batches. Fix existing mock_callback signatures to return `tuple[ExecutionStatus, str | None, dict[str, str]]` instead of bare `ExecutionStatus`.
   - Update `test_extractive_sensor_service.py` to assert the response structure maps correctly back to aliases via `AliasEngine`.
   - Update `test_enriched_dag_executor.py` to validate batch slicing logic and transient error classification.
   - Run the Universal Quality Gate.
2. **Integration Tests**:
   - Update `backend_v2/tests/integration/test_topological_evaluator.py` (4 existing tests) to match the new wave-based API.
3. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
   ```
4. **Baseline**: Run tests first and record the passing test count and coverage as a `[BASELINE]` metric.

## Documentation & Knowledge Item Mandate
- Instruct the execution agent to create a Knowledge Item (KI) detailing the new Wave-Based Topological Evaluator and Micro-Prompt Batching standards for future LLM scale-out algorithms.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
