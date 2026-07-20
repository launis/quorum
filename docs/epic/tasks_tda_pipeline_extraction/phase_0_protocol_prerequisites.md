# Phase 0: Protocol Prerequisites & Directory Structure

> **Source**: Epic 104, Phase 0 + Phase 1 (Protocol Definition)
> **Domain**: Backend (Python)
> **Max Target Files**: 3

## Goal

Establish the foundational directory structure, Pydantic V2 DTOs (`EngineExecutionRequest`, `EngineExecutionResult`), and the `ExecutionEngine` Protocol before any business logic extraction begins. This is a pure structural prerequisite — zero behavioral changes.

## Architectural Invariants (Injected from `.agents/rules/`)

- **`strict_pydantic_v2_rust`**: All DTOs MUST use `ConfigDict(strict=True, extra='forbid', frozen=True)`. Use `model_validate()`, NOT `**kwargs`.
- **`pydantic_annotated_fields_mandate`**: ALWAYS use PEP 593 `Annotated[T, Field(...)]` syntax.
- **`python_314_modern_syntax`**: PEP 695 generics, `X | None` unions, `from typing import Self`, `@override`.
- **`pep257_google_style_docstrings`**: Every module, class, and function MUST have Google-style docstrings.
- **`strict_configuration_segregation`**: No magic numbers. All limits from `settings.py`.
- **`circular_dependency_prevention`**: DTOs go into `models/dtos/engine.py` to prevent circular imports between strategies and engines.
- **`zero_defaults_mandate`**: No mutable default arguments.
- **`english_language_mandate`**: All code artifacts exclusively in English.

## Target Files (Modify/Create)

### [NEW] `backend_v2/services/orchestrator/engines/__init__.py`
- Create the `engines/` directory under `backend_v2/services/orchestrator/`.
- The `__init__.py` exports `ExecutionEngine` Protocol and `TDAEngine`.

### [NEW] `backend_v2/services/orchestrator/engines/base.py`
- Define the `ExecutionEngine` Protocol using `typing.Protocol`.
- Single method: `async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult`.
- The Protocol MUST be `@runtime_checkable` for DI validation.
- Docstrings MUST specify that engines are stateless across `execute()` calls and MUST explicitly list `Raises: AppException` with specific error codes in the docstring to enforce `docstring_fail_fast_ban`.

### [NEW] `backend_v2/models/dtos/engine.py`
- **`EngineExecutionRequest`**: A Pydantic `BaseModel`. Even though it holds complex runtime objects (`LLMClient`, `asyncio.Semaphore`, `Callable`), it MUST NOT bypass Pydantic. Use `model_config = ConfigDict(arbitrary_types_allowed=True, strict=True, extra='forbid', frozen=True)`. Fields:
  - `bound_client: LLMClient` — The initialized LLM client.
  - `compiled_schema: type[BaseModel] | None` — Forward compatibility for Epic 105's SynthesisEngine. `TDAEngine` ignores this.
  - `hydrated_messages: list[dict[str, str]] | None` — Forward compatibility for Epic 105. `TDAEngine` ignores this.
  - `system_prompt: str` — The compiled system prompt.
  - `step: StepRule` — The step configuration.
  - `context: StrategyContext` — Immutable strategy context.
  - `global_source_text: str` — The full source document text.
  - `target_locale: str | None` — The target locale for the evaluation.
  - `semaphore: asyncio.Semaphore` — Concurrency limiter.
  - `running_event: asyncio.Event | None` — Cancellation trigger.
  - `progress_callback: Callable[[int, int], Awaitable[None]] | None` — Progress reporting.
  - `trace_callback: Callable[[TraceEvent], Awaitable[None]] | None` — Live telemetry flush.
  - `prompt_compiler: Any` — The prompt compiler (typed as `Any` to avoid circular imports; use `TYPE_CHECKING` for the type hint).

- **`EngineExecutionResult`**: A strict Pydantic V2 model. Fields:
  - `results: list[AtomResultDTO]` — Projected atom results.
  - `hydrated_references: dict[str, HydratedAtomDTO]` — Hydrated atom references.
  - `model_config = ConfigDict(strict=True, extra='forbid', frozen=True)`

### [MODIFY] `backend_v2/models/dtos/__init__.py`
- Add `"engine"` to the `__all__` list.

## Context Files (Read-Only)

- `backend_v2/models/v2_core.py` — For `StepRule`, `AtomResultDTO`, `HydratedAtomDTO`.
- `backend_v2/services/orchestrator/strategies/base.py` — For `StrategyContext`.
- `backend_v2/models/state.py` — For `TraceEvent`.
- `backend_v2/llm/client.py` — For `LLMClient` type reference.
- `backend_v2/models/dtos/base.py` — For `BaseDTO` pattern reference.

## Verification Plan

### Automated Tests
- **Unit**: Create `backend_v2/tests/unit/models/dtos/test_engine.py`:
  - Test `EngineExecutionResult` rejects extra fields (`extra='forbid'`).
  - Test `EngineExecutionResult` is frozen (immutable).
  - Test `EngineExecutionRequest` is frozen (dataclass).
  - Test Protocol structural subtyping check.
- **Quality Gate**: `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/engine.py --test`

### Baseline
- Run existing tests first: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and record passing count as `[BASELINE]`.

## Session Handover

```
Achieved: Created engines/ directory structure, ExecutionEngine Protocol, EngineExecutionRequest dataclass, EngineExecutionResult Pydantic V2 DTO.
Learned: EngineExecutionRequest uses @dataclass(frozen=True) due to non-serializable runtime objects. EngineExecutionResult is strict Pydantic V2.
Remaining: Phase 1 (TDA Engine extraction from llm.py), Phase 2 (LLMNodeStrategy refactoring), Phase 3 (DAG Executor wiring).
```
