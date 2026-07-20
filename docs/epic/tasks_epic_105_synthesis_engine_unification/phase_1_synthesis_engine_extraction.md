# Phase 1: SynthesisEngine Extraction & EngineExecutionResult Adaptation

> **Source**: Epic 105, Phase 1 — Engine Extraction & Parameter Object Utilization
> **Domain**: Backend (Python) ONLY
> **Max Target Files**: 3

## Goal

Create the `SynthesisEngine` implementing the `ExecutionEngine` Protocol, move core synthesis execution logic from `PreHydratedSynthesisStrategy` into it, and adapt the `EngineExecutionResult` DTO to support Synthesis return types (which differ from TDA — synthesis returns trace-event-style dicts, not `AtomResultDTO`).

## Architectural Invariants (Injected)

- **`00-antigravity-core.md`**: `zero_compromise_pledge` — No fallback defaults. Crash if blackboard is missing.
- **`00-antigravity-core.md`**: `rfc7807_dual_reporting_mandate` — Every `AppException` preceded by structured `logger.error`.
- **`01-python-backend.md`**: `strict_pydantic_v2_rust` — `ConfigDict(extra='forbid', strict=True)` on all DTOs.
- **`01-python-backend.md`**: `pep257_google_style_docstrings` — All classes/methods documented.
- **`01-python-backend.md`**: `high_fidelity_prompting` — Blackboard data appended as separate XML-tagged message, NOT string-substituted.
- **`01-python-backend.md`**: `llm_structured_execution_mandate` — Use `LLMTaskExecutor.execute_structured_task()`.
- **KI: Provider-Agnostic Caching** — Append dynamic data at end to preserve prefix caching.
- **KI: TDA Best-Of-Three Flash** — SynthesisEngine does NOT use ensemble voting (single-pass).

## Critical Design Decisions

### 1. EngineExecutionResult Must Support Synthesis

The current `EngineExecutionResult` has:
```python
results: list[AtomResultDTO]
hydrated_references: dict[str, HydratedAtomDTO]
```

Synthesis does NOT produce `AtomResultDTO` or `HydratedAtomDTO`. It produces a validated Pydantic model that is serialized to a dict. The `EngineExecutionResult` must be adapted to carry both TDA results AND synthesis output. **CRITICAL**: We MUST NOT break the existing `TDAEngine` contract.

**Solution**: Add an optional `synthesis_output` field to `EngineExecutionResult`:
```python
synthesis_output: dict[str, Any] | None = None
trace_events: list[TraceEvent] = Field(default_factory=list)
```

- `results` + `hydrated_references` remain for TDA (unchanged).
- `synthesis_output` carries the validated Pydantic model dump for synthesis.
- `trace_events` carries telemetry events (latency, token counts).
- `LLMNodeStrategy` checks which field is populated to determine how to build the final `TraceEvent`.

### 2. SynthesisEngine Statelessness

The engine MUST be stateless. All data flows through `EngineExecutionRequest`:
- `request.hydrated_messages` — Pre-compiled static messages from `LLMNodeStrategy`
- `request.compiled_schema` — The dynamic Pydantic schema for validation
- `request.bound_client` — The LLM client
- `request.context.context_variables["__GLOBAL_ATOM_BLACKBOARD__"]` — Blackboard data
- `request.semaphore` / `request.running_event` — Concurrency controls

### 3. Immutable Request Handling

The engine creates a LOCAL COPY of `request.hydrated_messages` before appending blackboard data:
```python
local_messages = [dict(msg) for msg in request.hydrated_messages]
```

The blackboard is appended as a NEW separate message with XML boundaries:
```python
local_messages.append({
    "role": "user",
    "content": f"\n<global_atom_blackboard>\n{blackboard_json}\n</global_atom_blackboard>\n"
})
```

This preserves Static-First Context Caching and complies with the `high_fidelity_prompting` mandate.

## Proposed Changes

### TARGET (Modify): [engine.py](file:///c:/src/quorum/backend_v2/models/dtos/engine.py)

**Milestone 1.1**: Extend `EngineExecutionResult` with synthesis-compatible fields.

```diff
 class EngineExecutionResult(BaseModel):
     results: list[AtomResultDTO]
     hydrated_references: dict[str, HydratedAtomDTO]
+    synthesis_output: dict[str, Any] | None = None
+    trace_events: list[TraceEvent] = Field(default_factory=list)

     model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
```

Requires adding `Any` and `TraceEvent` to the typing imports.

**Verification**: Confirm `TDAEngine` still compiles. It sets `results` and `hydrated_references` but NOT `synthesis_output`, which defaults to `None`. No breaking change.

---

### TARGET (New): [synthesis_engine.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/synthesis_engine.py)

**Milestone 1.2**: Create `SynthesisEngine` implementing `ExecutionEngine`.

**Constructor**: Takes `LLMTaskExecutor` (injected). Does NOT accept `compiler`.

```python
class SynthesisEngine(ExecutionEngine):
    def __init__(self, llm_executor: LLMTaskExecutor) -> None:
        self._executor = llm_executor
```

**`execute()` method** — Complete logic extracted from `PreHydratedSynthesisStrategy.execute()` lines 39-150:

| Step | PreHydratedSynthesisStrategy Source | SynthesisEngine Implementation |
|------|-------------------------------------|-------------------------------|
| 1. Blackboard validation | Lines 40-50 | `request.context.context_variables["__GLOBAL_ATOM_BLACKBOARD__"]` → `GlobalAtomBlackboard.model_validate()`. Crash with `AppException(error_code="SYNTHESIS_ENGINE_ERROR")` if missing. |
| 2. Message preparation | Lines 101-112 | Read `request.hydrated_messages` (pre-compiled by `LLMNodeStrategy`). Create LOCAL COPY via `[dict(msg) for msg in request.hydrated_messages]`. |
| 3. Blackboard injection | N/A (was inline) | Append `{"role": "user", "content": "<global_atom_blackboard>...</global_atom_blackboard>"}` as NEW final message. |
| 4. Debug logging | New requirement | `logger.info("SynthesisEngine: Final hydrated message count: %d", len(local_messages))` before LLM call. |
| 5. LLM execution | Lines 118-123 | `self._executor.execute_structured_task(client=request.bound_client, messages=compiled_prompt, response_model=request.compiled_schema)` |
| 6. Result packaging | Lines 125-149 | Package into `EngineExecutionResult(results=[], hydrated_references={}, synthesis_output=output_dict, trace_events=[...])` |
| 7. Anti-Corruption Layer | N/A (was missing) | Catch specific exceptions (e.g. `LLMGenerationError`, `ValidationError`). Do NOT use "God Blocks" (`except Exception:`). Wrap in `AppException(error_code="SYNTHESIS_ENGINE_ERROR")` with RFC 7807 dual-reporting. |

**Symbols Extracted from `PreHydratedSynthesisStrategy`**:
- `GlobalAtomBlackboard.model_validate()` usage → preserved
- `blackboard.to_markdown_synthesis_injection()` → preserved  
- `LLMTaskExecutor.execute_structured_task()` → preserved
- `AliasEngine` hydration (lines 128-136) → preserved inside the engine
- Token usage metadata packaging (lines 139-142) → moved to `trace_events`

**Symbols NOT extracted (lifted to LLMNodeStrategy in Phase 2)**:
- Schema compilation (`self.compiler.build_dynamic_schema()`) — lines 87-95
- Static instruction compilation (`self.compiler.compile_static_instructions()`) — line 98
- Criteria block loading from DB — lines 67-79
- `LLMClient.from_strategy()` call — line 115
- Step definition loading (`self.workflow_repo.get_step_by_id()`) — lines 55-64

---

### TARGET (Modify): [__init__.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/__init__.py)

**Milestone 1.3**: Register `SynthesisEngine` in the engines package.

```diff
 from backend_v2.services.orchestrator.engines.base import ExecutionEngine
 from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
+from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine

 __all__ = [
     "ExecutionEngine",
     "TDAEngine",
+    "SynthesisEngine",
 ]
```

---

## CONTEXT (Read-Only)

| File | Reason |
|------|--------|
| [pre_hydrated_synthesis.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py) | Source of extraction. NOT modified — deletion in Phase 3. |
| [base.py (engines)](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/base.py) | Protocol definition — verify unchanged. |
| [tda_engine.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/tda_engine.py) | Reference pattern for engine implementation. |
| [llm.py (strategy)](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py) | Understand how `EngineExecutionRequest` is constructed for TDA to plan synthesis compilation in Phase 2. |
| [v2_core.py](file:///c:/src/quorum/backend_v2/models/v2_core.py) | `StepRule`, `PromptBlock`, `FrozenContext` models. |
| [blackboard.py](file:///c:/src/quorum/backend_v2/models/domain/blackboard.py) | `GlobalAtomBlackboard` model. |

## Bidirectional Integration Check

| Consumer (Engine) | Producer (LLMNodeStrategy — Phase 2) |
|---|---|
| `request.hydrated_messages` | `LLMNodeStrategy` synthesis branch compiles static + dynamic messages |
| `request.compiled_schema` | `LLMNodeStrategy` calls `compiler.build_dynamic_schema()` using `StepRule.expected_sdui_type` |
| `request.bound_client` | `LLMNodeStrategy` resolves via `LLMClient.from_strategy(context.model_strategy)` |
| `request.context.context_variables["__GLOBAL_ATOM_BLACKBOARD__"]` | Already injected by upstream DAG preflight |

## Testing & Quality Gate Plan

1. **BASELINE**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/engines/ --test` and record results.
2. **New Test File**: Create `backend_v2/tests/unit/services/orchestrator/engines/test_synthesis_engine.py` with:
   - `test_synthesis_engine_missing_blackboard_crashes` — Verify `AppException` raised when blackboard is missing.
   - `test_synthesis_engine_happy_path` — Mock `LLMTaskExecutor.execute_structured_task()` and verify correct `EngineExecutionResult` with `synthesis_output` populated.
   - `test_synthesis_engine_immutable_messages` — Verify the original `request.hydrated_messages` list is NOT mutated after execution.
   - `test_synthesis_engine_exception_wrapping` — Verify raw exceptions are wrapped in `AppException`.
3. **Run**: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` (full backend audit).

## Documentation Update

- No directory structure changes in this phase.
- KI creation deferred to tracker final steps (new SSOT: SynthesisEngine).

---

## Session Handover

```
Phase 1 complete. SynthesisEngine created at engines/synthesis_engine.py.
EngineExecutionResult extended with synthesis_output and trace_events.
Engine is fully stateless and implements ExecutionEngine Protocol.
Next: Execute Phase 2 (DAG executor wiring with factory registry + LLMNodeStrategy synthesis compilation branch).
```
