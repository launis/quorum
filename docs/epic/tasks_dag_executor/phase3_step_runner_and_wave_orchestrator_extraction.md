<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 3: Step Execution Stage & Topological Wave Orchestrator Extraction (`phase3_step_runner_and_wave_orchestrator_extraction.md`)

## 1. Objective
Execute Phase 3 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/dag_executor.py]`:
1. Extract step preparation and execution (`prepare_step_strategy_context` and `execute_dag_step_wrapper` unnesting `run_step_wrapper` `@[backend_v2/services/orchestrator/dag_executor.py#L1006-L1564]` and `progress_callback` `@[backend_v2/services/orchestrator/dag_executor.py#L1264-L1293]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]` (`< 380` lines), resolving `MatrixReducer` and `get_settings` dynamically via `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present so existing unit test patches on `backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix` and `backend_v2.services.orchestrator.dag_executor.get_settings` intercept transparently.
2. Extract post-step causal fusion/trace commit (`finalize_step_output_and_commit`) and topological wave `asyncio.TaskGroup` orchestration (`execute_topological_waves_stage`, unnesting the topological wave loop, `except* BaseException` error trapping, downstream `ExecutionStatus.BLOCKED` transition logic, final status verification, and top-level `unexpected_err` fail-fast handling from `DAGExecutor.execute_workflow` `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` (`< 320` lines).
3. Register `"backend_v2/services/orchestrator/dag_executor/step_execution_stage.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES`, and register `"backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` during Epoch 1 lift-and-shift.
4. Update `@[backend_v2/services/orchestrator/dag_executor.py]` so `DAGExecutor.execute_workflow` delegates step execution and wave orchestration to `step_execution_stage.py` and `wave_orchestrator_stage.py`, reducing `@[backend_v2/services/orchestrator/dag_executor.py]` to `< 180` lines, and create dedicated unit test suites `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]` | `prepare_step_strategy_context` and `execute_dag_step_wrapper` (upstream causal graph extraction, `MatrixReducer` pre-synthesis reduction, `progress_callback`, `AsyncRetrying` node execution, and `ContextRouter.verify_execution_compliance`) (`< 380` lines) |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` | `finalize_step_output_and_commit` (post-step causal cohesion/fusion evaluation and atomic `_update_lock` trace/schema/MCP-audit persistence) and `execute_topological_waves_stage` (`asyncio.TaskGroup` wave dispatch, `except* BaseException` error trapping, and downstream `BLOCKED` transitions) (`< 320` lines) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/dag_executor.py]` | Delegate `run_step_wrapper` and wave execution in `DAGExecutor.execute_workflow` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) to `step_execution_stage.py` and `wave_orchestrator_stage.py` with explicit redundant re-exports (`Symbol as Symbol`) |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `"backend_v2/services/orchestrator/dag_executor/step_execution_stage.py"` and `"backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]` | Unit tests for `prepare_step_strategy_context` and `execute_dag_step_wrapper` (resumption skip, upstream causal graph wiring, `MatrixReducer` invocation, retry loop, and failure state recording) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]` | Unit tests for `finalize_step_output_and_commit` and `execute_topological_waves_stage` (multi-wave `TaskGroup` execution, `ExceptionGroup` trapping, and downstream `BLOCKED` propagation) |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `dag_executor.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` (Phase 1)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` (Phase 1)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` (Phase 2)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/api/dependencies.py#L376-L417]` (Phase 4)
- `[MODIFY] @[backend_v2/services/execution/facade.py#L47-L118]` (Phase 4)
- `[MODIFY] @[backend_v2/worker.py#L44-L85]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Step Execution Stage and Topological Wave Orchestrator Sub-Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/dag_executor/__init__.py during Phase 3 while backend_v2/services/orchestrator/dag_executor.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither step_execution_stage.py nor wave_orchestrator_stage.py may import statically from backend_v2.services.orchestrator.dag_executor at module level, and both MUST remain under 380 lines with all lines <= 120 characters.</constraint>
    <constraint invariant="frozen_state_mutability">Bind _update_lock = state.update_lock locally before entering async with _update_lock: so AST guardrail QGR025 statically verifies lock-protected model_copy updates.</constraint>
    <action>
      1. Add `"backend_v2/services/orchestrator/dag_executor/step_execution_stage.py"` and `"backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py"` to `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` during Epoch 1 lift-and-shift.
      2. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]` (`< 380` lines, all lines `<= 120` chars) with `__all__ = ["execute_dag_step_wrapper", "prepare_step_strategy_context"]`:
         - Implement `prepare_step_strategy_context(...)` encapsulating upstream causal discovery graph extraction/validation, step-scoped state projection (`projector.project_state_for_step`), `MatrixReducer.reduce_matrix` pre-synthesis reduction, and `StrategyContext` construction from `run_step_wrapper` (`@[backend_v2/services/orchestrator/dag_executor.py#L1006-L1564]`), resolving `MatrixReducer` and `get_settings` dynamically via `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present.
         - Implement `async def execute_dag_step_wrapper(...) -> None` encapsulating `run_step_wrapper` (`@[backend_v2/services/orchestrator/dag_executor.py#L1006-L1564]`) and `progress_callback` (`@[backend_v2/services/orchestrator/dag_executor.py#L1264-L1293]`), binding `_update_lock = state.update_lock` for `async with _update_lock:` state transitions and delegating post-step causal fusion and trace persistence to `finalize_step_output_and_commit` in `wave_orchestrator_stage.py`.
      3. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` (`< 320` lines, all lines `<= 120` chars) with `__all__ = ["execute_topological_waves_stage", "finalize_step_output_and_commit"]`:
         - Implement `async def finalize_step_output_and_commit(...) -> None` encapsulating post-step causal discovery graph validation, `CausalCohesionEvaluator.evaluate`, `compute_causal_tda_fusion_result`, and atomic `_update_lock` `ExecutionRecord` trace/schema/MCP-audit updates + `safe_commit_execution_state` from `run_step_wrapper` (`@[backend_v2/services/orchestrator/dag_executor.py#L1006-L1564]`).
         - Implement `async def execute_topological_waves_stage(...) -> ExecutionRecord` encapsulating `DAGCompiler.validate_and_sort`, per-wave `async with asyncio.TaskGroup() as tg:` step dispatch, `except* BaseException as eg:` cancellation and downstream `ExecutionStatus.BLOCKED` propagation, final `ExecutionStatus` verification, and top-level `unexpected_err` fail-fast handling from `DAGExecutor.execute_workflow` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`).
    </action>
  </step>

  <step id="2" name="Delegate Step and Wave Orchestration in dag_executor.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/dag_executor.py]` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) to import and re-export `execute_dag_step_wrapper as execute_dag_step_wrapper` and `prepare_step_strategy_context as prepare_step_strategy_context` from `backend_v2.services.orchestrator.dag_executor.step_execution_stage` and `execute_topological_waves_stage as execute_topological_waves_stage` and `finalize_step_output_and_commit as finalize_step_output_and_commit` from `backend_v2.services.orchestrator.dag_executor.wave_orchestrator_stage`.
      2. Replace `run_step_wrapper` and the topological wave loop in `DAGExecutor.execute_workflow` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) with delegation to `execute_topological_waves_stage(...)` (while keeping a lightweight `asyncio.TaskGroup` reference or delegating cleanly so `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py]` continues passing before Phase 4 cutover).
      3. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_step_execution_stage.py]` testing `prepare_step_strategy_context` (upstream causal graph extraction and `MatrixReducer` invocation) and `execute_dag_step_wrapper` (skipping `PASSED` steps on resumption, executing `NodeExecutor`, and recording `FAILED` state on step error).
      4. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_wave_orchestrator_stage.py]` testing `finalize_step_output_and_commit` and `execute_topological_waves_stage` (multi-wave `asyncio.TaskGroup` execution and marking dependent steps `BLOCKED` when an upstream wave fails).
    </action>
  </step>

  <step id="3" name="Run Phase 3 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules, scripts/_ast_guardrails.py, and backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/step_execution_stage.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` and `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py` to verify all 76 baseline tests and AST guardrails pass.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_execute_dag_step_wrapper_reduces_matrix_and_commits_trace">
      Verifies that execute_dag_step_wrapper prepares StrategyContext, invokes NodeExecutor.execute, and commits StepOutputDTO and generated_schemas identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_execute_topological_waves_stage_runs_parallel_wave_steps">
      Verifies that execute_topological_waves_stage dispatches independent wave steps concurrently inside asyncio.TaskGroup and returns a completed ExecutionRecord.
    </contract>
    <contract type="negative" name="test_execute_topological_waves_stage_marks_downstream_steps_blocked_on_failure">
      Verifies that execute_topological_waves_stage traps step exceptions via except* BaseException, marks dependent downstream steps as BLOCKED, and re-raises the step failure.
    </contract>
  </test_contracts>
</execution_protocol>
```
