# Phase 2: DAG Executor Wiring & LLMNodeStrategy Synthesis Compilation Branch

> **Source**: Epic 105, Phase 2 — DAG Executor Wiring & Strategy Registry
> **Domain**: Backend (Python) ONLY
> **Max Target Files**: 2

## Goal

Wire the `SynthesisEngine` into the DAG execution pipeline by: (1) Adding a synthesis-specific pre-compilation branch inside `LLMNodeStrategy.execute()` that builds the schema, compiles static messages, and packages them into `EngineExecutionRequest`; and (2) Replacing the legacy `if/elif/else` routing chain in `dag_executor.py` with a Factory-Based Strategy Registry.

## Architectural Invariants (Injected)

- **`00-antigravity-core.md`**: `zero_compromise_pledge` — Unrecognized strategy keys MUST Fail-Fast.
- **`01-python-backend.md`**: `prompt_compiler_immutability` — Do NOT modify `prompt_compiler.py`. Invoke its existing public methods.
- **`01-python-backend.md`**: `orchestrator_god_object_fragility` — Full blast-radius analysis required for `dag_executor.py`. Must pass FULL backend audit.
- **`01-python-backend.md`**: `idiomatic_pattern_matching` — Use `match`/`case` if appropriate, but a `dict` registry is more appropriate for factory patterns.

## Proposed Changes

### TARGET (Modify): [dag_executor.py](file:///c:/src/quorum/backend_v2/services/orchestrator/dag_executor.py)

**Milestone 2.1**: Replace `if/elif/else` routing chain (lines 228-282) with a Factory-Based Strategy Registry.

The current routing chain:
```python
# Line 228-282 (CURRENT - violates Modernity Architect laws)
strategy_impl: NodeStrategy
if step_def.type == "logic":
    strategy_impl = LogicNodeStrategy(...)
elif step_def.model_strategy == "synthesis" or step.engine_override == "PRE_HYDRATED_SYNTHESIS":
    from ... import PreHydratedSynthesisStrategy
    strategy_impl = PreHydratedSynthesisStrategy(...)
elif step_def.model_strategy == "reasoning":
    from ... import TDAEngine
    strategy_impl = LLMNodeStrategy(..., engine=TDAEngine(self.compiler))
else:
    raise AppException(...)
```

**Replacement**: Strict structural routing using native `match/case` pattern (as mandated by `01-python-backend.md` rule `idiomatic_pattern_matching`):

```python
# Resolve strategy key: engine_override takes precedence, then model_strategy, then step type
strategy_key: str
if step.engine_override == EngineOverrideStrategy.SYNTHESIS:
    strategy_key = "synthesis"
elif step_def.type == "logic":
    strategy_key = "logic"
elif step_def.model_strategy:
    strategy_key = step_def.model_strategy  # "reasoning", "synthesis", "fast"
else:
    strategy_key = "reasoning"  # Will Fail-Fast if not in registry

match strategy_key:
    case "logic":
        strategy_impl = LogicNodeStrategy(
            self.exec_repo, self.workflow_repo, self.comp_repo,
            self.prompt_block_repo, self.output_profile_repo,
            self.identity_repo, self.audit_repo, self.system_repo,
            self.compiler, arq_pool=arq_pool,
        )
    case "synthesis":
        from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
        from backend_v2.services.llm_task_executor import LLMTaskExecutor
        llm_executor = LLMTaskExecutor(self.compiler)
        strategy_impl = LLMNodeStrategy(
            self.exec_repo, self.workflow_repo, self.comp_repo,
            self.prompt_block_repo, self.output_profile_repo,
            self.identity_repo, self.audit_repo, self.system_repo,
            self.compiler, engine=SynthesisEngine(llm_executor),
            arq_pool=arq_pool,
        )
    case "reasoning" | "fast":
        from backend_v2.services.orchestrator.engines.tda_engine import TDAEngine
        strategy_impl = LLMNodeStrategy(
            self.exec_repo, self.workflow_repo, self.comp_repo,
            self.prompt_block_repo, self.output_profile_repo,
            self.identity_repo, self.audit_repo, self.system_repo,
            self.compiler, engine=TDAEngine(self.compiler),
            arq_pool=arq_pool,
        )
    case _:
        msg = f"Unknown strategy key '{strategy_key}' for step {step.id}."
        logger.error("[NodeExecutor] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg, status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
        )
```

**Additional change**: Update `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS` → `.SYNTHESIS` references on lines 667 and 821 (already renamed in Phase 0).

---

### TARGET (Modify): [llm.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/llm.py) — `LLMNodeStrategy`

**Milestone 2.2**: Add synthesis-specific pre-compilation branch.

Currently, `LLMNodeStrategy.execute()` builds the `EngineExecutionRequest` with:
```python
engine_request = EngineExecutionRequest(
    compiled_schema=None,       # Epic 105 forward compatibility
    hydrated_messages=None,     # Epic 105 forward compatibility
    system_prompt=user_payload,
    ...
)
```

**New synthesis compilation branch**: Detect when the engine is a `SynthesisEngine` (by checking `step.engine_override == EngineOverrideStrategy.SYNTHESIS` or `context.model_strategy == "synthesis"`). When detected, build different `EngineExecutionRequest` fields:

Insert a branch BEFORE the existing `EngineExecutionRequest` construction (around line 606):

```python
from backend_v2.models.enums import EngineOverrideStrategy

is_synthesis_step = (
    step.engine_override == EngineOverrideStrategy.SYNTHESIS
    or context.model_strategy == "synthesis"
)

if is_synthesis_step:
    # Synthesis compilation path: build schema and messages for SynthesisEngine
    # Load criteria blocks (already loaded above as criteria_blocks_models)
    target_locale = str(context.metadata.get("target_locale", "en"))
    
    # Extract global context variables safely generated in DAG preflight
    blackboard = hook_state.global_context_vars.get("__GLOBAL_ATOM_BLACKBOARD__", {})
    doc_aliases = list(blackboard.get("atoms_by_input", {}).keys()) or ["N/A"]

    dynamic_schema = self.compiler.build_dynamic_schema(
        schema_name=f"Step_{step.id}_Response",
        criteria=criteria_blocks,
        has_shuffled_atoms=False,
        target_locale=target_locale,
        strictness_level=context.strictness_level,
        source_document_ids=doc_aliases,
    )

    static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
    static_msg = {"role": "system", "content": static_instructions}

    engine_request = EngineExecutionRequest(
        bound_client=bound_client,
        compiled_schema=dynamic_schema,
        hydrated_messages=[static_msg],
        system_prompt="",  # Not used by SynthesisEngine
        step=step,
        context=context,
        global_source_text=global_source_text,
        target_locale=target_locale,
        semaphore=semaphore,
        running_event=running_event,
        progress_callback=progress_callback,
        trace_callback=None,
        prompt_compiler=self.compiler,
    )
else:
    # Existing TDA/standard path (unchanged)
    engine_request = EngineExecutionRequest(
        bound_client=bound_client,
        compiled_schema=None,
        hydrated_messages=None,
        system_prompt=user_payload,
        ...  # existing fields unchanged
    )
```

**Post-execution handling** for synthesis results:

After `engine_result = await self._engine.execute(engine_request)`, add a branch:

```python
if is_synthesis_step and engine_result.synthesis_output is not None:
    final_dict = engine_result.synthesis_output
    # Trace events from engine contain telemetry
    # Standard post-hook processing continues
else:
    # Existing TDA path
    final_dict = {
        "results": [r.model_dump() for r in engine_result.results],
        "hydrated_references": {k: v.model_dump() for k, v in engine_result.hydrated_references.items()},
    }
```

---

### TARGET (Modify): [engine.py](file:///c:/src/quorum/backend_v2/models/dtos/engine.py)

**Milestone 2.3**: Allow SynthesisEngine output inside `EngineExecutionResult`.

Because `EngineExecutionResult` is mathematically locked via `ConfigDict(strict=True, extra="forbid", frozen=True)`, the `SynthesisEngine` cannot return synthesis dictionaries unless it is explicitly defined in the schema. 

Add `synthesis_output` to the DTO:

```python
class EngineExecutionResult(BaseModel):
    """Result DTO for execution engines.

    Carries the final projected atom results and their hydrated references.
    """

    results: list[AtomResultDTO]
    hydrated_references: dict[str, HydratedAtomDTO]
    synthesis_output: dict[str, Any] | None = None  # Synthesis engine results

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
```

---

## CONTEXT (Read-Only)

| File | Reason |
|------|--------|
| [synthesis_engine.py](file:///c:/src/quorum/backend_v2/services/orchestrator/engines/synthesis_engine.py) | Created in Phase 1. Verify interface compatibility. |
| [engine.py (DTOs)](file:///c:/src/quorum/backend_v2/models/dtos/engine.py) | `EngineExecutionRequest` / `EngineExecutionResult` contracts. |
| [base.py (strategies)](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/base.py) | `NodeStrategy` ABC, `StrategyContext` DTO. |
| [pre_hydrated_synthesis.py](file:///c:/src/quorum/backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py) | Verify all compilation logic is correctly lifted. |
| [prompt_compiler.py](file:///c:/src/quorum/backend_v2/services/orchestrator/prompt_compiler.py) | Read-only reference for `build_dynamic_schema()` and `compile_static_instructions()` signatures. |

## Bidirectional Integration Check

| Producer (LLMNodeStrategy) | Consumer (SynthesisEngine) |
|---|---|
| `hydrated_messages=[static_msg]` | Engine reads `request.hydrated_messages`, copies, appends blackboard |
| `compiled_schema=dynamic_schema` | Engine passes to `LLMTaskExecutor.execute_structured_task(response_model=...)` |
| `bound_client=bound_client` | Engine passes to executor |
| Context variables with blackboard | Engine extracts `__GLOBAL_ATOM_BLACKBOARD__` from `request.context.context_variables` |

## State & Transaction Audit

No database writes in this phase. All operations are read-only against repositories. Session lifecycle unchanged — existing `strategy_impl.execute()` call pattern is preserved. The DAG executor's atomic transaction scope is NOT altered.

## Testing & Quality Gate Plan

1. **BASELINE**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` before any modifications.
2. **After modifications**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` (FULL backend — blast radius analysis required per `orchestrator_god_object_fragility`).
3. **Verify**: All existing `test_dag_executor*.py` tests still pass with the new registry pattern.
4. **Integration test**: Manually verify via UI that an existing workflow with synthesis steps completes end-to-end.

## Documentation Update

- No directory structure changes in this phase.

---

## Session Handover

```
Phase 2 complete. DAG executor uses Factory-Based Strategy Registry.
LLMNodeStrategy has synthesis-specific pre-compilation branch.
SynthesisEngine is now wired as LLMNodeStrategy(engine=SynthesisEngine(llm_executor)).
Next: Execute Phase 3 (Legacy deletion) + Phase 4 (Testing) + Hardening.
```
