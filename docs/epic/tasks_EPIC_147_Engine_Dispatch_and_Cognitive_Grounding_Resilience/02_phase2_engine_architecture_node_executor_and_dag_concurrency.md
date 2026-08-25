# Phase 2: Engine Architecture, NodeExecutor Decomposition, Single-Fetch DI & DAG Concurrency Hardening

**Overview:** Extract `PromptEngine` for structured non-matrix prompt tasks, decompose `NodeExecutor` with `_resolve_execution_engine` and single-fetch DI injecting `StrategyContext.prompt_blocks`, refactor `LLMNodeStrategy` to delegate to `ExecutionEngine` and emit schemas via `TraceEvent.metadata["generated_schema"]`, eliminate in-memory double-serialization by updating `EngineExecutionResult.synthesis_output` to `BaseModel | None` and updating `HookState` / `HookResult`, update `SynthesisEngine` to preserve typed models, and synchronize DAGExecutor trace appends and state updates under `_update_lock` with atomic deduplicating `MCPAuditTrace` and `generated_schemas` accumulation.
**Target Files:**
- `[NEW]` @[backend_v2/services/orchestrator/engines/prompt_engine.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/__init__.py]
- `[MODIFY]` @[backend_v2/models/dtos/engine.py]
- `[MODIFY]` @[backend_v2/core/hook_registry.py#L55-L66]
- `[MODIFY]` @[backend_v2/core/hook_registry.py#L69-L73]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L219]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L115-L324]
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py#L560-L766]
- `[MODIFY]` @[backend_v2/models/state.py#L115-L138]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L346]
- `[MODIFY]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L69-L95]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 1. Verify `StrategyDependencies`, `get_prompt_blocks_by_ids`, and `NodeStrategyFactory` are active and passing tests.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/dag_executor.py#L115-L324], @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781], @[backend_v2/models/dtos/engine.py], and @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L219].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] Strongly-typed payload and `EngineExecutionResult.synthesis_output` updated in @[backend_v2/models/dtos/engine.py] (typed as `BaseModel | None`) and adopted in `LLMNodeStrategy.execute()` to eliminate raw `final_dict` state passing and enforce In-Memory Purity with Zero Double-Serialization.
    - [x] `HookState` and `HookResult` updated in @[backend_v2/core/hook_registry.py#L55-L66] and @[backend_v2/core/hook_registry.py#L69-L73] to support `BaseModel | dict[str, Any]`, eliminating premature `.model_dump()` in hooks.
    - [x] In-place `hook_state.metadata[...]` mutations in @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781] eliminated and replaced with immutable state accumulation and `model_copy(update=...)`.
    - [x] `SynthesisEngine.execute()` updated in @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L219] to preserve typed synthesis outputs without premature in-memory `.model_dump()` dict conversion.
    - [x] `PromptEngine` extracted in [NEW] @[backend_v2/services/orchestrator/engines/prompt_engine.py], exported in @[backend_v2/services/orchestrator/engines/__init__.py], and implementing `ExecutionEngine` protocol with Fail-Fast validations and native typed model returns.
    - [x] `NodeExecutor` decomposed into `_resolve_execution_engine` and `NodeStrategyFactory` dispatch in @[backend_v2/services/orchestrator/dag_executor.py#L115-L324]; prompt blocks single-fetched and injected via `StrategyContext(..., prompt_blocks=...)`, removing redundant caller-side adapter validation.
    - [x] Decoupled `_resolve_execution_engine` from `model_strategy == "synthesis"`, determining engine dispatch purely via `PromptBlockCategory` (`MATRIX` -> `TDAEngine`, `SYNTHESIS` -> `SynthesisEngine`, other -> `PromptEngine`).
    - [x] Full-table scan `get_all_prompt_blocks()` completely eliminated from `NodeExecutor` and `LLMNodeStrategy`.
    - [x] `DAGExecutor.run_step_wrapper` executes all state mutations, trace appends, `mcp_tool_audit` merging, and `generated_schemas` merging inside `async with _update_lock:` with strict Pydantic `model_copy(update=...)` state updates with shallow dict unpacking strictly synchronized inside `_update_lock` preventing double-serialization.
    - [x] In-place mutation of `frozen_ctx.generated_schemas` in `LLMNodeStrategy` completely eliminated; schemas propagated via `TraceEvent.metadata["generated_schema"]`.
    - [x] Atomic unit test and mock migrations completed for `test_dag_executor.py`, `test_llm.py`, `test_prompt_engine.py`, and `test_dag_executor_mcp_concurrency.py`.
    - [x] Quality gate `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test` passes.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_polymorphic_rule_routing.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_testing.md]</knowledge_item>
    <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
    <knowledge_item>@[ki_llm_extraction_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_sdui_matrix_synthesis.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <!-- [NEW] backend_v2/services/orchestrator/engines/prompt_engine.py -->
    <backend>@[backend_v2/services/orchestrator/engines/__init__.py]</backend>
    <backend>@[backend_v2/models/dtos/engine.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/models/state.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/hooks/source_verification_hook.py` in Phase 2 (reserved for Phase 3).
    - Do NOT modify `backend_v2/services/source_verification_service.py` in Phase 2 (reserved for Phase 3).
    - Do NOT modify Flutter frontend files in this backend plan.
  </anti_targets>

  <step id="1" name="Decompose NodeExecutor &amp; Single-Fetch DI in dag_executor.py">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L115-L324]:
      1. Update `NodeExecutor.__init__(self, deps: StrategyDependencies) -> None: self.deps = deps`.
      2. Update `DAGExecutor.__init__` in @[backend_v2/services/orchestrator/dag_executor.py#L327-L916] to instantiate `self.deps = StrategyDependencies(...)` and pass `self.node_executor = NodeExecutor(deps=self.deps)`.
      3. Add helper method `def _resolve_execution_engine(self, step_def: Step, prompt_blocks: list[PromptBlock]) -> ExecutionEngine`:
         - Filter criteria blocks from already-injected `prompt_blocks`: `criteria_blocks = [b for b in prompt_blocks if b.id in step_def.criteria_block_ids]`.
         - Check if criteria contains `PromptBlockCategory.MATRIX` (or `isinstance(b, MatrixPromptBlock)`): return `TDAEngine(self.deps.prompt_compiler)`.
         - Check if criteria contains `PromptBlockCategory.SYNTHESIS` (or `getattr(b, "is_synthesis", False)`): return `SynthesisEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
         - Else (non-matrix structured prompt step): return `PromptEngine(LLMTaskExecutor(self.deps.prompt_compiler))`.
      4. In `NodeExecutor.execute_node`:
         - Resolve criteria block IDs: `criteria_ids = list(step_def.criteria_block_ids)`.
         - Single-fetch hydrated blocks via `loaded_prompt_blocks = await self.deps.prompt_block_repo.get_prompt_blocks_by_ids(criteria_ids, strict=True)`.
         - Resolve engine: `engine = self._resolve_execution_engine(step_def, loaded_prompt_blocks) if step_def.type == StepType.LLM else None`.
         - Create strategy via factory: `strategy_impl = NodeStrategyFactory.create_strategy(step_type=step_def.type, deps=dataclasses.replace(self.deps, arq_pool=arq_pool) if arq_pool else self.deps, engine=engine)`.
         - Inject `loaded_prompt_blocks` into `StrategyContext(..., prompt_blocks=loaded_prompt_blocks, model_strategy=step_def.model_strategy)`.
         - Execute quota and strategy: `await strategy_impl.assert_quota(org_id=org_id); return await strategy_impl.execute(...)`.
    </action>
    <demolish>REMOVE: Procedural `if step_def.type == "logic"` branching in `NodeExecutor.execute_node` at @[backend_v2/services/orchestrator/dag_executor.py#L115-L324]. REPLACE WITH: `NodeStrategyFactory.create_strategy`.</demolish>
    <demolish>REMOVE: Procedural `if step_def.model_strategy == "synthesis"` branching in `NodeExecutor` at @[backend_v2/services/orchestrator/dag_executor.py#L115-L324]. REPLACE WITH: `_resolve_execution_engine`.</demolish>
    <constraint invariant="strategy_pattern_mandate">Dynamic inference driven purely by StepType and PromptBlockCategory eliminates procedural string branches.</constraint>
  </step>

  <step id="2" name="Atomic Deduplicating State Accumulation under _update_lock in DAGExecutor">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py#L560-L766]:
      Move unsynchronized trace append for-loop inside `_update_lock`, eliminate Pydantic Double-Serialization by retaining optimized `.model_copy(update=...)` state updates with shallow dict unpacking strictly synchronized inside `_update_lock`, and implement atomic deduplicating accumulation of both `MCPAuditTrace` into `exec_record.frozen_context.mcp_tool_audit` AND `generated_schemas` into `exec_record.frozen_context.generated_schemas` under `_update_lock` with strict typed Pydantic models:
```python
has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
async with _update_lock:
    step_mcp_traces: list[MCPAuditTrace] = []
    new_cv = dict(exec_record.context_variables)
    new_schemas = dict(exec_record.frozen_context.generated_schemas)
    has_cv_updates = False
    has_schema_updates = False

    for evt in events:
        exec_record.execution_trace.append(evt)
        projector.apply_delta(evt)
        if (
            evt.event_type == "decision"
            and evt.metadata
            and "is_context_update" in evt.metadata
            and evt.metadata["is_context_update"]
        ):
            new_cv.update(evt.content)
            has_cv_updates = True

        if evt.metadata and "generated_schema" in evt.metadata:
            new_schemas[step_id] = evt.metadata["generated_schema"]
            has_schema_updates = True

        if hasattr(evt, "mcp_audit_traces") and evt.mcp_audit_traces:
            step_mcp_traces.extend(evt.mcp_audit_traces)
        elif evt.metadata and "mcp_audit_traces" in evt.metadata:
            raw_traces = evt.metadata["mcp_audit_traces"]
            if isinstance(raw_traces, list):
                for t in raw_traces:
                    if isinstance(t, MCPAuditTrace):
                        step_mcp_traces.append(t)
                    elif isinstance(t, dict):
                        step_mcp_traces.append(MCPAuditTrace.model_validate(t))

    existing_mcp = list(exec_record.frozen_context.mcp_tool_audit)
    if step_mcp_traces:
        existing_ids = {t.id for t in existing_mcp}
        unique_new = [t for t in step_mcp_traces if t.id not in existing_ids]
        existing_mcp.extend(unique_new)

    fc_updates: dict[str, Any] = {}
    if step_mcp_traces:
        fc_updates["mcp_tool_audit"] = existing_mcp
    if has_schema_updates:
        fc_updates["generated_schemas"] = new_schemas

    updated_fc = (
        exec_record.frozen_context.model_copy(update=fc_updates)
        if fc_updates
        else exec_record.frozen_context
    )

    rec_updates: dict[str, Any] = {
        "frozen_context": updated_fc,
        "completed_steps": exec_record.completed_steps + [step_id],
    }
    if has_cv_updates:
        rec_updates["context_variables"] = new_cv
    if has_error_evt:
        rec_updates["status"] = ExecutionStatus.FAILED

    exec_record = exec_record.model_copy(update=rec_updates)
```
    </action>
    <action>In @[backend_v2/models/state.py#L115-L138], ensure `mcp_audit_traces: list[MCPAuditTrace] = Field(default_factory=list)` is declared on `TraceEvent`.</action>
    <demolish>REMOVE: Unsynchronized append loop on `exec_record.execution_trace` outside `_update_lock` in `run_step_wrapper` at @[backend_v2/services/orchestrator/dag_executor.py#L560-L766].</demolish>
    <constraint invariant="frozen_state_mutability">Parallel state updates must be synchronized inside async with _update_lock: with atomic deduplication.</constraint>
  </step>

  <step id="3" name="Extract PromptEngine">
    <action>Create [NEW] @[backend_v2/services/orchestrator/engines/prompt_engine.py]:
      - Implement `ExecutionEngine` protocol:
```python
import logging
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.llm_task_executor import LLMTaskExecutor

logger = logging.getLogger(__name__)


class PromptEngine(ExecutionEngine):
    """Engine executing structured non-matrix LLM prompt tasks."""

    def __init__(self, task_executor: LLMTaskExecutor) -> None:
        self.task_executor = task_executor

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Execute structured LLM prompt task with Fail-Fast validations."""
        if request.compiled_schema is None:
            msg = f"PromptEngine requires compiled_schema on Step '{request.step.id}'."
            logger.error("[PromptEngine] %s: %s", ErrorCodes.PROMPT_ENGINE_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROMPT_ENGINE_ERROR.value, "step_id": request.step.id},
            )

        if not request.hydrated_messages:
            msg = f"PromptEngine received empty hydrated_messages on Step '{request.step.id}'."
            logger.error("[PromptEngine] %s: %s", ErrorCodes.PROMPT_ENGINE_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROMPT_ENGINE_ERROR.value, "step_id": request.step.id},
            )

        if request.running_event:
            request.running_event.set()

        async with request.semaphore_cm:
            synthesis_output, usage = await self.task_executor.execute_structured_task(
                client=request.client,
                messages=request.hydrated_messages,
                response_model=request.compiled_schema,
            )

        return EngineExecutionResult(
            results=[],
            hydrated_references={},
            synthesis_output=synthesis_output,
            usage=usage,
        )
```
    </action>
    <action>In @[backend_v2/services/orchestrator/engines/__init__.py]:
      - Export `PromptEngine`: `__all__ = ["ExecutionEngine", "TDAEngine", "SynthesisEngine", "PromptEngine"]`.
    </action>
    <constraint invariant="ki_execution_engine_protocol.md">All LLM execution logic delegates to an ExecutionEngine resolved orthogonally from model_strategy.</constraint>
  </step>

  <step id="4" name="Refactor LLMNodeStrategy to Delegate to ExecutionEngine">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]:
      1. Update `__init__(self, deps: StrategyDependencies, engine: ExecutionEngine) -> None`: Store `self.deps = deps` and `self.engine = engine`.
      2. Consume `context.prompt_blocks`: Completely remove `await self.prompt_block_repo.get_all_prompt_blocks()`.
      3. Eliminate in-place `frozen_ctx.generated_schemas[step.id] = ...` mutation: propagate `generated_schema` via `TraceEvent(..., metadata={"generated_schema": compiled_schema.model_json_schema()})`.
      4. Delegate execution purely to `self.engine.execute(engine_req)`:
         - Construct `engine_req = EngineExecutionRequest(client=client, step=step, context=context, compiled_schema=compiled_schema, hydrated_messages=hydrated_messages, criteria_blocks_models=criteria_blocks_models, criteria_blocks=criteria_blocks, matrix_context=matrix_context, semaphore_cm=semaphore_cm, running_event=running_event)`.
         - Await `engine_result = await self.engine.execute(engine_req)`.
      5. Eliminate in-memory double-serialization and raw dictionary state passing:
         - In @[backend_v2/models/dtos/engine.py]:
```python
class EngineExecutionResult(V2CoreBase):
    """Result payload returned by an ExecutionEngine."""
    results: list[AtomResultDTO]
    hydrated_references: dict[str, HydratedAtomDTO]
    synthesis_output: Annotated[BaseModel | None, Field(default=None, description="Typed structured synthesis DTO (specifically RenderedSynthesisCache).")] = None
    usage: TokenUsage | None = None

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
```
         - Declare `EngineExecutionResult` with `synthesis_output: Annotated[BaseModel | None, Field(...)] = None` as strongly-typed engine output.
         - Assemble payload model: `payload = EngineExecutionResult(results=engine_result.results, hydrated_references=engine_result.hydrated_references, synthesis_output=engine_result.synthesis_output, usage=engine_result.usage)`.
         - Pass `payload` directly to `post_hook_state = hook_state.model_copy(update={"global_context_vars": safe_context, "inputs": payload})` for post-hooks (Zero Double-Serialization in memory).
         - Emit `TraceEvent(step_name=step.id, event_type="output", content=payload.model_dump(mode="python"), metadata=...)` strictly at the Event Sourcing persistence boundary.
    </action>
    <action>In @[backend_v2/core/hook_registry.py#L55-L66] and @[backend_v2/core/hook_registry.py#L69-L73]: Update `HookState.inputs: BaseModel | dict[str, Any]` and `HookResult.state_delta: BaseModel | dict[str, Any] | None`.</action>
    <action>In @[backend_v2/services/orchestrator/engines/synthesis_engine.py#L25-L219]: Update `execute` to preserve typed validated models in `EngineExecutionResult.synthesis_output` without premature `.model_dump()`.</action>
    <demolish>REMOVE: `get_all_prompt_blocks()` table scan in `LLMNodeStrategy.execute` at @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]. REPLACE WITH: `context.prompt_blocks` single-fetch injection.</demolish>
    <demolish>REMOVE: In-place `frozen_ctx.generated_schemas[step.id] = ...` mutation in `_execute_llm_internal` at @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]. REPLACE WITH: `TraceEvent.metadata["generated_schema"]`.</demolish>
    <demolish>REMOVE: Raw dict `final_dict` state passing at @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781]. REPLACE WITH: strongly-typed payload model.</demolish>
    <constraint invariant="the_zero_compromise_pledge">Pydantic models must be preserved strongly typed across in-memory boundaries.</constraint>
  </step>

  <step id="5" name="Atomic Unit Test Migration for NodeExecutor &amp; DAGExecutor">
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L287-L346]: Update instantiations of `DAGExecutor` and `NodeExecutor` to pass `deps = StrategyDependencies(...)`, and update mock return values for repositories to typed Pydantic V2 models (`Step`, `PromptBlock`, `Workflow`, `OutputProfile`).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py#L69-L95]: Update fixtures to `StrategyDependencies`, migrate mocks to typed Pydantic models, test `PromptEngine` payload compilation.</action>
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]: Implement ISTQB unit tests for `PromptEngine` covering successful structured task execution, Fail-Fast missing schema, Fail-Fast empty messages, exception re-raising, and semaphore context manager acquisition with running_event signaling.</action>
    <action>In [NEW] @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]: Implement multi-step concurrent `mcp_tool_audit` and `generated_schemas` accumulation tests under `_update_lock`.</action>
    <test_contracts>
      <test name="test_prompt_engine_success_structured_task" category="positive">
        <input>Valid compiled_schema and hydrated_messages</input>
        <expected>returns EngineExecutionResult with synthesis_output containing validated model</expected>
      </test>
      <test name="test_prompt_engine_fail_fast_missing_schema" category="error_path">
        <input>compiled_schema=None</input>
        <expected>raises AppException(PROMPT_ENGINE_ERROR)</expected>
      </test>
      <test name="test_prompt_engine_fail_fast_empty_messages" category="error_path">
        <input>hydrated_messages=[]</input>
        <expected>raises AppException(PROMPT_ENGINE_ERROR)</expected>
      </test>
      <test name="test_dag_executor_concurrent_steps_accumulate_mcp_traces" category="positive">
        <input>4 concurrent steps generating 2 MCPAuditTrace each</input>
        <expected>All 8 unique traces preserved in frozen_context.mcp_tool_audit</expected>
      </test>
      <test name="test_dag_executor_mcp_trace_deduplication" category="boundary">
        <input>Concurrent steps emitting duplicate MCPAuditTrace(id="mcp_001")</input>
        <expected>mcp_tool_audit contains exactly 1 instance of mcp_001</expected>
      </test>
      <test name="test_dag_executor_concurrent_steps_accumulate_generated_schemas" category="positive">
        <input>4 concurrent steps generating dynamic JSON schemas</input>
        <expected>All 4 step schemas safely accumulated into frozen_context.generated_schemas under _update_lock</expected>
      </test>
    </test_contracts>
    <constraint invariant="python_314_concurrency_strictness">Parallel task executions must synchronize shared state mutations under _update_lock.</constraint>
  </step>

  <validation_gate>
    <action>Execute Prompt Engine Unit Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py`</action>
    <action>Execute DAG Concurrency Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py`</action>
    <action>Execute DAG &amp; Strategy Tests: `uv run pytest backend_v2/tests/unit/services/orchestrator/test_dag_executor.py backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py`</action>
    <action>Execute Quality Loop: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator --test`</action>
  </validation_gate>
</execution_protocol>
```
