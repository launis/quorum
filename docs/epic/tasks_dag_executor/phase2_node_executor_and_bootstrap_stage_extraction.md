<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 2: NodeExecutor & Workflow Bootstrap/Preflight Stage Extraction (`phase2_node_executor_and_bootstrap_stage_extraction.md`)

## 1. Objective
Execute Phase 2 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/dag_executor.py]`:
1. Extract `NodeExecutor` (`@[backend_v2/services/orchestrator/dag_executor.py#L362-L597]`: `__init__` `@[backend_v2/services/orchestrator/dag_executor.py#L365-L374]`, `_dlq_record_node_error` `@[backend_v2/services/orchestrator/dag_executor.py#L376-L384]`, `_resolve_execution_engine` `@[backend_v2/services/orchestrator/dag_executor.py#L386-L398]`, and `execute` `@[backend_v2/services/orchestrator/dag_executor.py#L400-L597]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` (`< 260` lines), resolving `NodeStrategyFactory` and `hook_registry` dynamically via `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present so existing test patches on `backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory` and `backend_v2.services.orchestrator.dag_executor.hook_registry` intercept transparently.
2. Extract the execution-scoped `@dataclass class WorkflowExecutionState` container, DLQ helper functions (`dlq_record_step_failure` from `@[backend_v2/services/orchestrator/dag_executor.py#L603-L606]`, `dlq_handle_progress_commit_error` from `@[backend_v2/services/orchestrator/dag_executor.py#L608-L616]`, `dlq_fallback_step_exceptions` from `@[backend_v2/services/orchestrator/dag_executor.py#L618-L632]`), `bootstrap_workflow_execution_state` (unnesting `_fetch_and_validate` `@[backend_v2/services/orchestrator/dag_executor.py#L720-L730]` and the workflow/context/blueprint/strictness initialization stage of `DAGExecutor.execute_workflow` `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`), `safe_commit_execution_state` (unnesting `_safe_commit` `@[backend_v2/services/orchestrator/dag_executor.py#L991-L1004]`), and `execute_rag_preflight_stage` (unnesting `_emit_preflight_progress` `@[backend_v2/services/orchestrator/dag_executor.py#L1598-L1623]` and the Phase 0 RAG Pre-Flight stage of `DAGExecutor.execute_workflow` `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (`< 360` lines).
3. Register `"backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` during Epoch 1 lift-and-shift, update `@[backend_v2/services/orchestrator/dag_executor.py]` to re-export `NodeExecutor` and delegate workflow bootstrap, `_safe_commit`, and RAG pre-flight stages to `workflow_bootstrap_stage.py`, and create unit test suites `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | `NodeExecutor` (`__init__`, `_dlq_record_node_error`, `_resolve_execution_engine`, `execute`) executing strategy dispatch, OpenTelemetry `dag.node.{step.id}` span telemetry, and post-hooks (`< 260` lines) |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` | `WorkflowExecutionState` `@dataclass`, `dlq_record_step_failure`, `dlq_handle_progress_commit_error`, `dlq_fallback_step_exceptions`, `bootstrap_workflow_execution_state`, `safe_commit_execution_state`, and `execute_rag_preflight_stage` (`< 360` lines) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/dag_executor.py]` | Re-export `NodeExecutor` (`@[backend_v2/services/orchestrator/dag_executor.py#L362-L597]`) and delegate DLQ helpers (`@[backend_v2/services/orchestrator/dag_executor.py#L603-L606]`, `@[backend_v2/services/orchestrator/dag_executor.py#L608-L616]`, `@[backend_v2/services/orchestrator/dag_executor.py#L618-L632]`) and bootstrap/preflight stages in `DAGExecutor.execute_workflow` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) to `workflow_bootstrap_stage.py` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `"backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]` | Unit tests for `NodeExecutor` engine resolution, OpenTelemetry span attributes, post-hook delta merging, and `_dlq_record_node_error` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]` | Unit tests for `bootstrap_workflow_execution_state`, `safe_commit_execution_state`, `execute_rag_preflight_stage`, and DLQ helpers |

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
  <step id="1" name="Create NodeExecutor and Workflow Bootstrap Stage Sub-Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/dag_executor/__init__.py during Phase 2 while backend_v2/services/orchestrator/dag_executor.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither node_executor.py nor workflow_bootstrap_stage.py may import statically from backend_v2.services.orchestrator.dag_executor at module level, and both MUST remain under 360 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Add `"backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py"` to `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` so the verbatim Epoch 1 lift-and-shift of `WorkflowExecutionState` and blueprint/step_states initialization passes `QGR027` and `QGR028` prior to Epoch 2 hardening.
      2. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` (`< 260` lines, all lines `<= 120` chars) with `__all__ = ["NodeExecutor"]`:
         - Relocate `NodeExecutor` verbatim from `@[backend_v2/services/orchestrator/dag_executor.py#L362-L597]` (`__init__` `@[backend_v2/services/orchestrator/dag_executor.py#L365-L374]`, `_dlq_record_node_error` `@[backend_v2/services/orchestrator/dag_executor.py#L376-L384]`, `_resolve_execution_engine` `@[backend_v2/services/orchestrator/dag_executor.py#L386-L398]`, and `execute` `@[backend_v2/services/orchestrator/dag_executor.py#L400-L597]`).
         - Resolve `NodeStrategyFactory` and `hook_registry` dynamically from `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present so existing unit test patches on `backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory` and `backend_v2.services.orchestrator.dag_executor.hook_registry` intercept transparently.
      3. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (`< 360` lines, all lines `<= 120` chars) with `__all__ = ["WorkflowExecutionState", "bootstrap_workflow_execution_state", "dlq_fallback_step_exceptions", "dlq_handle_progress_commit_error", "dlq_record_step_failure", "execute_rag_preflight_stage", "safe_commit_execution_state"]`:
         - Define `@dataclass class WorkflowExecutionState` encapsulating the execution-scoped mutable state and Two-Lock concurrency primitives: `exec_id: str`, `workflow: Workflow`, `exec_record: ExecutionRecord`, `global_context_vars: dict[str, JsonValue]`, `projector: ResultProjector`, `step_definitions: dict[str, V2Step]`, `steps_by_id: dict[str, WorkflowStep]`, `strictness_level: int`, `lexical_strictness_level: int`, `step_exceptions: dict[str, str]`, `update_lock: asyncio.Lock`, `commit_lock: asyncio.Lock`, and `evaluated_causal_sources: set[str]`.
         - Relocate `dlq_record_step_failure` (`@[backend_v2/services/orchestrator/dag_executor.py#L603-L606]`), `dlq_handle_progress_commit_error` (`@[backend_v2/services/orchestrator/dag_executor.py#L608-L616]`), and `dlq_fallback_step_exceptions` (`@[backend_v2/services/orchestrator/dag_executor.py#L618-L632]`).
         - Implement `async def bootstrap_workflow_execution_state(...) -> WorkflowExecutionState` encapsulating the parallel `asyncio.TaskGroup` blueprint fetch (`_fetch_and_validate`), `ExecutionRecord` creation or resumption, `FrozenExecutionContext` hydration, `ResultProjector` construction, and strictness resolution from `DAGExecutor.execute_workflow` (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`), resolving `Step` and `get_settings` dynamically via `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present.
         - Implement `async def safe_commit_execution_state(...) -> ExecutionRecord` encapsulating `_safe_commit` (`@[backend_v2/services/orchestrator/dag_executor.py#L991-L1004]`).
         - Implement `async def execute_rag_preflight_stage(...) -> None` encapsulating Phase 0 RAG Pre-Flight (`_emit_preflight_progress` `@[backend_v2/services/orchestrator/dag_executor.py#L1598-L1623]` and `rag_preflight_service.execute_preflight` in `DAGExecutor.execute_workflow` `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`).
    </action>
  </step>

  <step id="2" name="Delegate NodeExecutor and Workflow Bootstrap Stage in dag_executor.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/dag_executor.py]` to import and re-export `NodeExecutor as NodeExecutor` from `backend_v2.services.orchestrator.dag_executor.node_executor` and `WorkflowExecutionState as WorkflowExecutionState`, `bootstrap_workflow_execution_state as bootstrap_workflow_execution_state`, `dlq_fallback_step_exceptions as dlq_fallback_step_exceptions`, `dlq_handle_progress_commit_error as dlq_handle_progress_commit_error`, `dlq_record_step_failure as dlq_record_step_failure`, `execute_rag_preflight_stage as execute_rag_preflight_stage`, and `safe_commit_execution_state as safe_commit_execution_state` from `backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage`.
      2. Delegate `DAGExecutor._dlq_record_step_failure`, `DAGExecutor._dlq_handle_progress_commit_error`, `DAGExecutor._dlq_fallback_step_exceptions`, and the bootstrap, `_safe_commit`, and RAG pre-flight sections of `DAGExecutor.execute_workflow` in `@[backend_v2/services/orchestrator/dag_executor.py]` to `workflow_bootstrap_stage.py`.
      3. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_node_executor.py]` testing `NodeExecutor._resolve_execution_engine`, `NodeExecutor.execute` (OpenTelemetry span attributes, post-hook delta merging, and `ValidationError` translation to `OrchestrationError`), and `NodeExecutor._dlq_record_node_error`.
      4. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_workflow_bootstrap_stage.py]` testing `bootstrap_workflow_execution_state` (fresh execution creation, resumption with existing `frozen_context`, and missing blueprint `BlueprintNotFoundError`), `safe_commit_execution_state`, and `execute_rag_preflight_stage`.
    </action>
  </step>

  <step id="3" name="Run Phase 2 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules, scripts/_ast_guardrails.py, and backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/node_executor.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` to verify all 76 baseline tests pass with `>= 90%` line coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_node_executor_resolves_engine_and_merges_post_hook_deltas">
      Verifies that NodeExecutor.execute dispatches to the resolved ExecutionEngine, executes post-hooks, and merges HookStateDelta trace events identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_bootstrap_workflow_execution_state_prefetches_blueprints_via_taskgroup">
      Verifies that bootstrap_workflow_execution_state pre-fetches all workflow step blueprints concurrently via asyncio.TaskGroup and initializes WorkflowExecutionState.
    </contract>
    <contract type="negative" name="test_bootstrap_workflow_execution_state_missing_blueprint_raises_not_found">
      Verifies that bootstrap_workflow_execution_state raises BlueprintNotFoundError when a step references a non-existent blueprint ID.
    </contract>
  </test_contracts>
</execution_protocol>
```
