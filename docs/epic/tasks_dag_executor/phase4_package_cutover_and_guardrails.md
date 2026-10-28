<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 4: Atomic Package Cutover, 1-Hop Caller Verification & QGR017 Guardrail Lockdown (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute the final Epoch 1 Cutover of the `@[backend_v2/services/orchestrator/dag_executor.py]` decomposition:
1. Atomically replace `[DELETE] @[backend_v2/services/orchestrator/dag_executor.py]` with the domain package facade `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` (`< 180` lines) defining `DAGExecutor` (`__init__`, `execute_workflow`, and DLQ delegation methods) and explicit redundant re-exports (`__all__` and `Symbol as Symbol`) for all extracted sub-modules and patchable collaborators (`get_settings`, `hook_registry`, `Step`, `MatrixReducer`, `NodeStrategyFactory`).
2. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]` verifying package facade re-exports, `DAGExecutor` initialization, and end-to-end `execute_workflow` delegation, and verify 1-hop production callers (`@[backend_v2/api/dependencies.py#L376-L417]`, `@[backend_v2/services/execution/facade.py#L47-L118]`, `@[backend_v2/worker.py#L44-L85]`).
3. Update AST guardrail suites (`@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L89-L121]`, `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L124-L134]`, `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L400-L409]`, `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py#L117-L122]`) to scan the modular `backend_v2/services/orchestrator/dag_executor/` package, remove `"backend_v2/services/orchestrator/dag_executor.py"` from `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]`, lock retired path `"backend_v2/services/orchestrator/dag_executor.py"` under `QGR017` in `visit_Module` (`@[scripts/_ast_guardrails.py#L730-L820]`) with unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1637-L1644]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` | Canonical package facade (`< 180` lines) defining `DAGExecutor` and explicit `__all__` + redundant alias re-exports (`Symbol as Symbol`) |
| `[DELETE]` | `[DELETE] @[backend_v2/services/orchestrator/dag_executor.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/api/dependencies.py#L376-L417]` | Verify `get_dag_executor` DI factory wiring against `backend_v2.services.orchestrator.dag_executor.DAGExecutor` package facade |
| `[MODIFY]` | `@[backend_v2/services/execution/facade.py#L47-L118]` | Verify `ExecutionService.__init__` wiring against `backend_v2.services.orchestrator.dag_executor.DAGExecutor` package facade |
| `[MODIFY]` | `@[backend_v2/worker.py#L44-L85]` | Verify Arq worker `startup` wiring against `backend_v2.services.orchestrator.dag_executor.DAGExecutor` package facade |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]` | Unit tests for `backend_v2.services.orchestrator.dag_executor` package facade exports, `DAGExecutor.__init__`, and `DAGExecutor.execute_workflow` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L730-L820]` | Remove `"backend_v2/services/orchestrator/dag_executor.py"` from `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES` and register `"backend_v2/services/orchestrator/dag_executor.py"` under `QGR017` in `visit_Module` |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1637-L1644]` | Add `test_qgr017_banned_dag_executor_god_file_path_fatal` and `test_qgr017_modular_dag_executor_package_allowed` |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L89-L121]` | Update `test_ast_semaphore_guardrail` (`#L89-L121`) and `test_ast_taskgroup_guardrail` (`@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L124-L134]`) to scan `backend_v2/services/orchestrator/dag_executor/*.py` |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L400-L409]` | Update `test_node_strategy_registry_ast_has_no_procedural_string_routing` to scan `backend_v2/services/orchestrator/dag_executor/*.py` |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py#L117-L122]` | Update `test_ast_dag_executor_zero_sys_render_injection` to scan `backend_v2/services/orchestrator/dag_executor/*.py` |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update `backend_v2/services/` (`orchestrator/`) and `backend_v2/tests/unit/...` to list `dag_executor/` package modules and unit tests |

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
  <step id="1" name="Execute Atomic Package Cutover and Create Facade Unit Test Suite">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/services/orchestrator/dag_executor.py and create backend_v2/services/orchestrator/dag_executor/__init__.py in a single atomic step, keeping __init__.py strictly under 180 lines.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/orchestrator/dag_executor/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` (`< 180` lines, all lines `<= 120` chars) defining `DAGExecutor` (`__init__`, `execute_workflow`, `_dlq_record_step_failure`, `_dlq_handle_progress_commit_error`, `_dlq_fallback_step_exceptions`) and explicit `__all__` + redundant alias re-exports (`Symbol as Symbol`) for `ExecutionCommitter`, `ExecutionRecordUpdate`, `FrozenContextUpdate`, `NodeExecutor`, `StepOutputContentValue`, `WorkflowExecutionState`, `bootstrap_workflow_execution_state`, `compute_causal_tda_fusion_result`, `dlq_fallback_step_exceptions`, `dlq_handle_progress_commit_error`, `dlq_record_step_failure`, `execute_dag_step_wrapper`, `execute_rag_preflight_stage`, `execute_topological_waves_stage`, `finalize_step_output_and_commit`, `prepare_step_strategy_context`, `safe_commit_execution_state`, and `transform_causal_nodes_to_atoms`, plus `MatrixReducer as MatrixReducer`, `NodeStrategyFactory as NodeStrategyFactory`, `Step as Step`, `get_settings as get_settings`, and `hook_registry as hook_registry`.
      2. Physically delete `[DELETE] @[backend_v2/services/orchestrator/dag_executor.py]`.
      3. Verify and synchronize 1-hop production callers (`@[backend_v2/api/dependencies.py#L376-L417]`, `@[backend_v2/services/execution/facade.py#L47-L118]`, `@[backend_v2/worker.py#L44-L85]`) importing `DAGExecutor` from `backend_v2.services.orchestrator.dag_executor`.
      4. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_dag_executor_facade.py]` testing package facade symbol exports, `DAGExecutor` initialization, and `DAGExecutor.execute_workflow` orchestration.
    </action>
  </step>

  <step id="2" name="Update AST Guardrail Suites, Lock QGR017, and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py, and all AST guardrail tests MUST scan the modular dag_executor/ package.</constraint>
    <action>
      1. Update `@[scripts/_ast_guardrails.py]` (`@[scripts/_ast_guardrails.py#L730-L820]` `visit_Module`):
         - Remove `"backend_v2/services/orchestrator/dag_executor.py"` from `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` and `RESIDUAL_FUTURE_PHASE_QGR028_FILES`.
         - Add an explicit `elif norm_path == "backend_v2/services/orchestrator/dag_executor.py" or norm_path.endswith("/backend_v2/services/orchestrator/dag_executor.py"):` branch in `visit_Module` (`@[scripts/_ast_guardrails.py#L730-L820]`) emitting a FATAL `QGR017` violation.
      2. Update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1637-L1644]` to add `test_qgr017_banned_dag_executor_god_file_path_fatal` and `test_qgr017_modular_dag_executor_package_allowed`.
      3. Update `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L89-L121]` (`test_ast_semaphore_guardrail`) and `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L124-L134]` (`test_ast_taskgroup_guardrail`) to scan all `*.py` files in `base / "services" / "orchestrator" / "dag_executor"` for zero `asyncio.Semaphore` and verify `asyncio.TaskGroup` usage in `workflow_bootstrap_stage.py` and `wave_orchestrator_stage.py`.
      4. Update `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L400-L409]` (`test_node_strategy_registry_ast_has_no_procedural_string_routing`) and `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py#L117-L122]` (`test_ast_dag_executor_zero_sys_render_injection`) to scan all `*.py` files in `Path("backend_v2/services/orchestrator/dag_executor")`.
      5. Update `@[.agents/rules/04_directory_reference.md]` under `backend_v2/services/` (`orchestrator/`) and `backend_v2/tests/unit/...` to replace `dag_executor.py` with `dag_executor/ (causal_tda_fusion.py, execution_committer.py, node_executor.py, workflow_bootstrap_stage.py, step_execution_stage.py, wave_orchestrator_stage.py, __init__.py facade)` and list the new unit test suites under `services/orchestrator/dag_executor/`.
    </action>
  </step>

  <step id="3" name="Run Phase 4 Package Audit, Guardrail Suite, and Seed Smoke Verification">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py on the backend_v2/services/orchestrator/dag_executor/ package, 1-hop callers, and scripts/_ast_guardrails.py, followed by run_seed.py local.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/ --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/api/dependencies.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/services/execution/facade.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/worker.py --test --ast-strict`.
      4. Execute `uv run pytest backend_v2/tests/unit/test_ast_concurrency_guardrails.py backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py backend_v2/tests/unit/test_rest_only_pipeline_boundary.py` and `uv run python backend_v2/seed/run_seed.py local`.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_dag_executor_package_facade_reexports_all_public_symbols">
      Verifies that importing DAGExecutor, ExecutionCommitter, NodeExecutor, compute_causal_tda_fusion_result, and transform_causal_nodes_to_atoms from backend_v2.services.orchestrator.dag_executor works identically after replacing dag_executor.py with dag_executor/__init__.py.
    </contract>
    <contract type="positive" name="test_qgr017_modular_dag_executor_package_allowed">
      Verifies that scanning backend_v2/services/orchestrator/dag_executor/__init__.py and its submodules produces zero QGR017 violations.
    </contract>
    <contract type="negative" name="test_qgr017_banned_dag_executor_god_file_path_fatal">
      Verifies that scanning retired path backend_v2/services/orchestrator/dag_executor.py triggers a FATAL QGR017 violation in QuorumGuardrailVisitor.
    </contract>
  </test_contracts>
</execution_protocol>
```
