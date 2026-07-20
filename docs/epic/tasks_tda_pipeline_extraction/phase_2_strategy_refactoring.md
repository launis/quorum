# Phase 2 & 3: LLMNodeStrategy Refactoring, Engine Delegation, & DAG Wiring

> **Source**: Epic 104, Phase 2 (LLMNodeStrategy Refactoring)
> **Domain**: Backend (Python)
> **Max Target Files**: 2
> **Prerequisite**: Phase 0 AND Phase 1 MUST be complete.

## Goal

Refactor `LLMNodeStrategy` to accept a mandatory `engine: ExecutionEngine` parameter and replace the 50+ line inline TDA pipeline (lines 560-614) with a single `await self._engine.execute(...)` delegation call. The anomaly retry loop, telemetry, schema compilation, and post-hook execution REMAIN in `llm.py`.

## Architectural Invariants (Injected from `.agents/rules/`)

- **`strict_dependency_injection`**: The `engine` parameter MUST be mandatory. No `None` defaults, no fallback instantiation.
- **`inline_imports_ban` (TYPE_CHECKING exception)**: Use `from typing import TYPE_CHECKING` at the top of `llm.py` to type-hint `ExecutionEngine` without runtime import.
- **`the_zero_compromise_pledge`**: No fallback chains. If engine is not injected, Fail-Fast.
- **`orchestrator_god_object_fragility`**: Modifying `llm.py` requires full blast-radius analysis. The existing tests in `test_llm.py` MUST be updated.
- **`strict_variable_preservation`**: Do NOT rename existing variables like `final_dict`, `usage_agg`, `strategy_name`.
- **`documentation_present_tense_mandate`**: Docstrings describe current state, not historical context.
- **`pep257_google_style_docstrings`**: Verify updated docstrings.
- **`anti_tdd_trap`**: If existing tests create `LLMNodeStrategy` without an engine, those tests MUST be updated to inject a mock engine. Do NOT add `engine: Any | None = None` to preserve old tests.

## Destructive Operation Inventory

The following lines are **DELETED** from `llm.py`:

| Line Range | Code | Replacement |
|-----------|------|-------------|
| 560-564 | 5x inline imports (`LLMTaskExecutor`, `EnrichedDagExecutor`, etc.) | **DELETED** — moved to `tda_engine.py` |
| 566-576 | Sub-service instantiation + text chunking | **DELETED** — handled by `TDAEngine.execute()` |
| 578-596 | 4x progress callback wrapper functions | **DELETED** — handled by `TDAEngine.execute()` |
| 598-607 | Pipeline execution (atomizer → linker → dag_executor) | **REPLACED** by `result = await self._engine.execute(request)` |
| 609-614 | `ResultProjector.project()` + dict construction | **REPLACED** by consuming `result.results` and `result.hydrated_references` |

**What STAYS in `llm.py`:**
- Lines 529-540: `strategy_name` resolution + `LLMClient.from_strategy()` (lifecycle concern)
- Lines 542-548: Retry loop setup (`MAX_RETRIES`, `retry_count`, `final_dict`, `usage_agg`)
- Lines 548-558: While-loop header + telemetry logging
- Lines 616-695: Post-hook execution, anomaly retry, telemetry aggregation, TraceEvent construction

## Target Files (Modify)

### [MODIFY] `backend_v2/services/orchestrator/dag_executor.py`

1. **Lazy Engine Import**: To prevent PyO3 Zero Cold Start failures, import `TDAEngine` lazy inside `NodeExecutor.execute()`:
   ```python
   from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
   ```
2. **Inject Engine**: When instantiating `LLMNodeStrategy`, pass `engine=TDAEngine(compiler=self.compiler)` as a parameter.
3. **Fail-Fast Routing**: Replace the default `else:` block (which currently acts as a catch-all for `LLMNodeStrategy`) with a strict `AppException` crash to enforce schema-driven routing. Only explicitly map `model_strategy == "reasoning"` to `LLMNodeStrategy`.

### [MODIFY] `backend_v2/services/orchestrator/strategies/llm.py`

1. **Add `__init__` override**: Override `NodeStrategy.__init__` to accept all base positional arguments PLUS a mandatory `engine` parameter.
   ```python
   def __init__(
       self,
       exec_repo: IExecutionRepository,
       # ... all base repos ...
       prompt_compiler: Any,
       engine: ExecutionEngine,  # Mandatory, no default
       arq_pool: Any | None = None,
   ) -> None:
   ```
   - Use `from typing import TYPE_CHECKING` and `if TYPE_CHECKING: from backend_v2.services.orchestrator.engines.base import ExecutionEngine` for the type hint.
   - Store as `self._engine = engine`.

2. **Replace inline pipeline** (lines 560-614) with:
   ```python
   from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
   
   engine_request = EngineExecutionRequest(
       bound_client=bound_client,
       compiled_schema=None,  # Epic 105 forward compatibility
       hydrated_messages=None,  # Epic 105 forward compatibility
       system_prompt=user_payload,
       step=step,
       context=context,
       global_source_text=global_source_text,
       target_locale=target_locale,
       semaphore=semaphore,
       running_event=running_event,
       progress_callback=progress_callback,
       trace_callback=None,  # Phase 2+ telemetry
       prompt_compiler=self.compiler,
   )
   engine_result = await self._engine.execute(engine_request)
   
   final_dict = {
       "results": [r.model_dump() for r in engine_result.results],
       "hydrated_references": {k: v.model_dump() for k, v in engine_result.hydrated_references.items()},
   }
   ```

3. **Retain** all post-hook, anomaly retry, and telemetry logic unchanged.

### [MODIFY] `backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py`

1. **Update `llm_strategy` fixture**: Add a `mock_engine` fixture and inject it into `LLMNodeStrategy(...)`:
   ```python
   @pytest.fixture
   def mock_engine() -> MagicMock:
       engine = AsyncMock()
       engine.execute = AsyncMock()
       return engine
   
   @pytest.fixture
   def llm_strategy(mock_repo, mock_compiler, mock_engine) -> LLMNodeStrategy:
       return LLMNodeStrategy(
           exec_repo=mock_repo,
           # ... repos ...
           prompt_compiler=mock_compiler,
           engine=mock_engine,
       )
   ```

2. **Update ALL existing tests** to use the updated fixture. No test should instantiate `LLMNodeStrategy` without an `engine`.

## Context Files (Read-Only)

- `backend_v2/services/orchestrator/strategies/base.py` — `NodeStrategy` ABC.
- `backend_v2/models/dtos/engine.py` — `EngineExecutionRequest`, `EngineExecutionResult`.
- `backend_v2/services/orchestrator/engines/base.py` — `ExecutionEngine` Protocol.
- `backend_v2/models/v2_core.py` — `StepRule`, `AtomResultDTO`, `HydratedAtomDTO`.

## Verification Plan

### Automated Tests
- Run ALL existing tests in `test_llm.py` — they MUST pass with the mock engine injection.
- Verify that no test uses `LLMNodeStrategy(...)` without `engine=`.
- **Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/ --test`

## Session Handover

```
Achieved: LLMNodeStrategy refactored with mandatory engine DI. Inline TDA pipeline replaced by single delegation call. dag_executor.py wired with Fail-Fast routing and lazy DI imports. All tests updated.
Learned: Anomaly retry loop, telemetry, and post-hooks remain in llm.py (lifecycle concerns). Only the execution pipeline is delegated.
Remaining: Post-phases (Hardening, Proxy Sunset, Pre-Delete Audit, Semantic Coverage Audit, Documentation Update).
```
