# Epic 100 Phase 3: Aggressive Pre-Flight Tuning & Thread Starvation Prevention

## Source: Epic 100, Phase 3

## Architectural Invariants
- **Global Config Sovereignty**: Pre-flight thresholds MUST be centralized in `settings.py`. No hardcoded values allowed.
- **Thread Starvation Prevention**: CPU-bound operations (`rapidfuzz`) MUST be executed in bulk using `asyncio.to_thread` instead of individual thread dispatches.
- **Fail-Fast**: Deterministic pre-flight logic should exit early if anchors are absent.
- **SSOT Migration**: The hardcoded `FuzzThresholdConfig` MUST be removed. `get_lexical_fuzz_threshold()` must read its values dynamically from `settings.py` to ensure all callers use configurable values.

## Target Files (Modify)
- `backend_v2/settings.py`
- `backend_v2/models/enums.py`
- `backend_v2/services/orchestrator/extractive_sensor_service.py`
- `backend_v2/services/orchestrator/enriched_dag_executor.py`
- `backend_v2/services/orchestrator/strategies/llm.py`

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py` (provides `TDAAssertion`)

## Proposed Changes

### 1. `backend_v2/settings.py`
- **[MODIFY]**: Add the 4 linguistic fuzzy thresholds.
- **Detail**:
  ```python
  pre_flight_fuzz_agglutinative: Annotated[float, Field(description="Fuzzy threshold for Finnish/Hungarian/Turkish")] = 85.0
  pre_flight_fuzz_analytic: Annotated[float, Field(description="Fuzzy threshold for English/Swedish/German")] = 92.0
  pre_flight_fuzz_isolating: Annotated[float, Field(description="Fuzzy threshold for Chinese/Japanese")] = 98.0
  pre_flight_fuzz_default: Annotated[float, Field(description="Fallback threshold")] = 90.0
  ```
- **Rationale**: Removes hardcoded values from the system so that pre-flight thresholds can be tuned dynamically.
- **Dropped Symbols**: None.

### 2. `backend_v2/models/enums.py`
- **[MODIFY]**: Enforce Tripartite Configuration Architecture by purging logic from Enums.
- **Detail**:
  - Delete `FuzzThresholdConfig` entirely.
  - Delete `get_lexical_fuzz_threshold` entirely. (This logic will be moved directly into `ExtractiveSensorService` to prevent `settings.py` pollution in `enums.py`).
- **Dropped Symbols**: `FuzzThresholdConfig`, `get_lexical_fuzz_threshold`.

### 3. `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **[MODIFY]**: Add `_batch_fuzzy_match`, `batch_pre_evaluate`, and update `_fuzzy_match` to use `settings.py` natively.
- **Detail**:
  - Add `import asyncio` and `from backend_v2.settings import get_settings` at the top.
  - Modify `@staticmethod def _fuzzy_match` to resolve the language threshold directly using `get_settings()` and a `match locale.lower():` block (migrating the logic removed from `enums.py`). Remove the import of `get_lexical_fuzz_threshold` from `enums.py`.
  - Implement `@staticmethod def _batch_fuzzy_match(nodes: list[LinkedAtomGraph], source_text: str, locale: str | None = None) -> tuple[dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]], list[LinkedAtomGraph]]:` — a synchronous method that:
    1. Iterates over all nodes.
    2. For each node, calls `ExtractiveSensorService.pre_evaluate(node.atom, source_text, locale)`.
    3. If `decided=True`, maps the pre-flight result to the standard `(ExecutionStatus, str | None, dict)` tuple format. `ExecutionStatus.PASSED` if `result == "PASS"` else `ExecutionStatus.FAILED`.
    4. If `decided=False`, appends the node to the `undecided` list.
    5. Returns `(decided_results, undecided_nodes)`.
  - Implement `@staticmethod async def batch_pre_evaluate(nodes: list[LinkedAtomGraph], source_text: str, locale: str | None = None) -> tuple[dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]], list[LinkedAtomGraph]]:` — an async wrapper that offloads `_batch_fuzzy_match` via `await asyncio.to_thread(...)`.
- **Dropped Symbols**: None.

### 4. `backend_v2/services/orchestrator/enriched_dag_executor.py` (CRITICAL PRODUCTION WIRING)
- **[MODIFY]**: Wire `batch_pre_evaluate` into the `process_chunk` method.
- **Detail**:
  - Inside `process_chunk()`, BEFORE calling `evaluate_atom_boolean_batch`, call `ExtractiveSensorService.batch_pre_evaluate(chunk, source_text, locale)`.
  - Unpack the result into `(pre_flight_results, undecided_nodes)`.
  - If `undecided_nodes` is empty, return `pre_flight_results` directly (100% LLM bypass).
  - If `undecided_nodes` is non-empty, call `evaluate_atom_boolean_batch(undecided_nodes, ...)` for LLM evaluation.
  - Merge `pre_flight_results` with `llm_results` and return the combined dict.
  - **IMPORTANT**: The `locale` parameter must be threaded through. Add it to `execute_graph()` signature: `async def execute_graph(self, nodes: list[LinkedAtomGraph], source_text: str, locale: str | None = None)` and propagate it down to `process_chunk`.
- **Dropped Symbols**: None.

### 5. `backend_v2/services/orchestrator/strategies/llm.py` (DEPENDENCY INJECTION)
- **[MODIFY]**: Pass `target_locale` into `execute_graph`.
- **Detail**:
  - Inside `LLMNodeStrategy.execute()`, the variable `target_locale` is already extracted and strictly validated (e.g., `target_locale = str(context.metadata["target_locale"])`).
  - Pass this existing `target_locale` variable to `dag_executor.execute_graph(nodes, global_source_text, target_locale)`.

> [!IMPORTANT]
> **Pre-flight result mapping**: When `pre_evaluate` returns `decided=True, result="FAIL"`, map to `(ExecutionStatus.FAILED, "PRE_FLIGHT_DETERMINISTIC_REJECT", {})`. When `result="PASS"`, map to `(ExecutionStatus.PASSED, "PRE_FLIGHT_DETERMINISTIC_PASS", {})`.

## Testing & Quality Gate Plan
1. **Unit Tests**:
   - Write new tests in `test_extractive_sensor_service.py` for `batch_pre_evaluate`:
     - Test that decided TDAs are filtered out and undecided TDAs remain.
     - Assert that `asyncio.to_thread` is only called once per batch.
   - Write/Update tests in `test_enriched_dag_executor.py` to verify pre-flight integration:
     - Test that when all atoms are pre-flight decided, `evaluate_atom_boolean_batch` is NOT called.
     - Test that partial pre-flight results are correctly merged with LLM results.
   - Verify all 6 existing `pre_evaluate` unit tests still pass unchanged.
   - Run the Universal Quality Gate.
2. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/extractive_sensor_service.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/enriched_dag_executor.py --test
   ```
3. **Baseline**: 16 tests pass as of Phase 2 completion. Coverage must not drop.

## Documentation & Knowledge Item Mandate
- Update `docs/architecture/` with the new bulk pre-flight extraction architecture and the production wiring diagram.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
