# Phase 1: TDA Engine Extraction & Settings Migration

> **Source**: Epic 104, Phase 1 (TDA Engine Implementation) + Phase 0 (Settings migration)
> **Domain**: Backend (Python)
> **Max Target Files**: 3
> **Prerequisite**: Phase 0 MUST be complete (DTOs and Protocol exist).

## Goal

Extract the inline TDA pipeline from [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py#L560-L614) into a standalone `TDAEngine` class implementing the `ExecutionEngine` Protocol. Migrate hardcoded linker configuration to `settings.py`.

## Architectural Invariants (Injected from `.agents/rules/`)

- **`inline_imports_ban`**: The 5 sub-services (`LLMTaskExecutor`, `TwoPassAtomizer`, `SlidingWindowLinker`, `EnrichedDagExecutor`, `ResultProjector`) are standard Python modules — they MUST be imported at the TOP of `tda_engine.py` globally.
- **`strict_configuration_segregation`**: The hardcoded `SlidingWindowLinker(window_size=4, overlap=2)` MUST be replaced with `get_settings().tda_linker_window_size` and `get_settings().tda_linker_overlap`.
- **`pydantic_annotated_fields_mandate`**: New settings fields MUST use `Annotated[int, Field(...)]`.
- **`global_settings_import`**: `get_settings` MUST be imported at the TOP of `tda_engine.py`.
- **`pep257_google_style_docstrings`**: Every module, class, method.
- **`rfc7807_dual_reporting_mandate`**: The engine MUST act as an Exception ACL — catch sub-service exceptions and wrap into `AppException` with a `logger.error` preceding the raise.
- **`frozen_state_mutability`**: Engine MUST NOT store state in `self` between `execute()` calls (stateless).
- **`taskgroup_exceptiongroup_mandate`**: No `asyncio.gather`. Use `asyncio.TaskGroup` if parallel operations are needed.
- **`dlq_arq_fallback_routing`**: Sub-service errors MUST be routed to the DLQ via AppException, not swallowed.
- **`the_zero_compromise_pledge`**: No `.get()` defaults, no fallback chains.
- **`python_314_modern_syntax`**: PEP 695 generics, `@override`.

## Destructive Operation Inventory

The following inline block from `llm.py` (lines 560-614) will be **MOVED** to `tda_engine.py`:

| Symbol | Current Location | New Location | Notes |
|--------|-----------------|-------------|-------|
| `from ...LLMTaskExecutor import` | `llm.py:560` | `tda_engine.py` (top-level) | Inline → top-level |
| `from ...EnrichedDagExecutor import` | `llm.py:561` | `tda_engine.py` (top-level) | Inline → top-level |
| `from ...ResultProjector import` | `llm.py:562` | `tda_engine.py` (top-level) | Inline → top-level |
| `from ...SlidingWindowLinker import` | `llm.py:563` | `tda_engine.py` (top-level) | Inline → top-level |
| `from ...TwoPassAtomizer import` | `llm.py:564` | `tda_engine.py` (top-level) | Inline → top-level |
| `LLMTaskExecutor(...)` instantiation | `llm.py:566-568` | `tda_engine.py:execute()` | — |
| `TwoPassAtomizer(...)` instantiation | `llm.py:569` | `tda_engine.py:execute()` | — |
| `SlidingWindowLinker(window_size=4, overlap=2)` | `llm.py:570` | `tda_engine.py:execute()` | Config → `settings.py` |
| `EnrichedDagExecutor(...)` instantiation | `llm.py:571` | `tda_engine.py:execute()` | — |
| Text chunking logic | `llm.py:573-576` | `tda_engine.py:execute()` | `chunk_size` from `get_settings()` |
| Progress callback functions (phase_0/1/linker/dag) | `llm.py:578-596` | `tda_engine.py:execute()` | 0-15%, 15-35%, 35-60%, 60-100% |
| `atomizer.execute_phase_0(...)` call | `llm.py:598` | `tda_engine.py:execute()` | — |
| `atomizer.execute_phase_1(...)` call | `llm.py:599-601` | `tda_engine.py:execute()` | — |
| `linker.link_graph(...)` call | `llm.py:602-604` | `tda_engine.py:execute()` | — |
| `dag_executor.execute_graph(...)` call | `llm.py:605-607` | `tda_engine.py:execute()` | — |
| `ResultProjector.project(...)` call | `llm.py:609` | `tda_engine.py:execute()` | — |
| Result dict construction | `llm.py:611-614` | `tda_engine.py:execute()` | Returns `EngineExecutionResult` DTO instead |

**INTENTIONALLY DROPPED: None** — All symbols are migrated.

## Target Files (Modify/Create)

### [NEW] `backend_v2/services/orchestrator/engines/tda_engine.py`
- Class `TDAEngine` implementing `ExecutionEngine` Protocol.
- **Constructor**: Accepts `prompt_compiler: Any` (use `TYPE_CHECKING` for `PromptCompiler` type hint). Do NOT inject repositories, `arq_pool`, or `LLMClient` — the TDA pipeline receives the `LLMClient` via the request DTO.
- **`async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult`**:
  1. Extract fields from `request`: `bound_client`, `global_source_text`, `target_locale`, `semaphore`, `running_event`, `progress_callback`, `step`, and `context`.
  2. Instantiate sub-services: `LLMTaskExecutor(self._compiler, default_validation_context={"execution_id": request.context.execution_id, "step_id": request.step.id})`, `TwoPassAtomizer(llm_executor)`, `SlidingWindowLinker(window_size=get_settings().tda_linker_window_size, overlap=get_settings().tda_linker_overlap)`, `EnrichedDagExecutor(llm_executor, request.bound_client)`.
  3. Text chunking using `get_settings().rag_preflight_chunk_size`.
  4. Define 4 progress callback wrappers (0-15%, 15-35%, 35-60%, 60-100%).
  5. Execute TDA pipeline: Phase 0 → Phase 1 → Linker → DAG → ResultProjector.
  6. Return `EngineExecutionResult(results=results_dto, hydrated_references=hydrated_refs)`.
  7. **Exception ACL**: Wrap the pipeline in `try...except`. You MUST explicitly catch `AppException` first and re-raise it to prevent double-wrapping and losing the original error code. Then catch general `Exception as e`, log it via `logger.error(..., exc_info=True)`, and raise a new `AppException(message=str(e), details={"error_code": "TDA_ENGINE_ERROR"})`.
- **Statelessness**: Engine MUST NOT store any state in `self` variables between calls. Only `self._compiler` is stored.

### [MODIFY] `backend_v2/settings.py`
- Add two new fields to `GlobalSettings`:
  - `tda_linker_window_size: Annotated[int, Field(description="Sliding window size for TDA linker.")] = 4`
  - `tda_linker_overlap: Annotated[int, Field(description="Overlap between sliding windows in TDA linker.")] = 2`

### [MODIFY] `backend_v2/services/orchestrator/engines/__init__.py`
- Export `TDAEngine` alongside the Protocol.

## Context Files (Read-Only)

- `backend_v2/services/orchestrator/two_pass_atomizer.py` — Sub-service API.
- `backend_v2/services/orchestrator/sliding_window_linker.py` — Sub-service API.
- `backend_v2/services/orchestrator/enriched_dag_executor.py` — Sub-service API.
- `backend_v2/services/orchestrator/result_projector.py` — Sub-service API.
- `backend_v2/services/llm_task_executor.py` — Sub-service API.
- `backend_v2/models/dtos/engine.py` — DTOs (created in Phase 0).
- `backend_v2/services/orchestrator/engines/base.py` — Protocol (created in Phase 0).

## Bidirectional Integration Check

- **Producer**: `TDAEngine.execute()` produces `EngineExecutionResult`.
- **Consumer**: `LLMNodeStrategy` (Phase 2) will consume this result in place of the inline dict construction.
- The `EngineExecutionResult` fields (`results`, `hydrated_references`) match the existing dict keys at `llm.py:611-614`.

## Verification Plan

### Automated Tests
- **Unit**: Create `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py`:
  - Mock all 5 sub-services (`TwoPassAtomizer`, `SlidingWindowLinker`, `EnrichedDagExecutor`, `LLMTaskExecutor`, `ResultProjector`).
  - Verify proportional progress callback routing (0-15%, 15-35%, 35-60%, 60-100%).
  - Verify `EngineExecutionResult` is returned (not a raw dict).
  - Verify Exception ACL: sub-service `Exception` → `AppException`.
  - Verify statelessness: no `self` mutation between calls.
  - Verify settings integration: `tda_linker_window_size` and `tda_linker_overlap` are read from `get_settings()`.
- **Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/ --test`

## Session Handover

```
Achieved: TDAEngine extracted with full sub-service delegation, settings migration for linker config, Exception ACL, statelessness.
Learned: TDAEngine receives LLMClient via request DTO (not constructor). PromptCompiler is the only constructor dependency.
Remaining: Phase 2 (LLMNodeStrategy refactoring to delegate to engine), Phase 3 (DAG Executor wiring).
```
