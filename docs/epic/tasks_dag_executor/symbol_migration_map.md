<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Symbol & Blast-Radius Migration Map: `backend_v2/services/orchestrator/dag_executor.py`

## 1. Executive Summary & Monolith Archetype Profile
- **Target God File**: `@[backend_v2/services/orchestrator/dag_executor.py]` (`1,803` lines)
- **Target Domain Package**: `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` (`backend_v2/services/orchestrator/dag_executor/`)
- **Monolith Archetype**: **Archetype D: Macro Orchestrator & Concurrency Core** (`orchestrator_god_object_fragility` permission granted; Two-Tier Concurrency SSOT; Two-Lock execution state synchronization via `_update_lock` and `_commit_lock`; `asyncio.TaskGroup` wave concurrency with `except* BaseException` error trapping; OpenTelemetry `dag.orchestration` and `dag.node.{step_id}` spans; RFC 7807 + Dead Letter Queue error routing).
- **Test Baseline (`[BASELINE]`)**:
  - Command: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test`
  - Result: **10/10 Quality Gates PASSED**, **76 passed unit tests** across 8 discovered test suites (`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`, `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`).
  - Line Coverage: **90%** (`785` statements, `81` missed). Because baseline coverage exceeds the `75%` threshold (`90% >= 75%`), `Phase 0: Coverage Bootstrap` is skipped.
- **Invariant Set ($\mathcal{I}_{orig}$)**:
  1. **Zero Semaphore Invariant**: `@[backend_v2/services/orchestrator/dag_executor.py]` and all extracted sub-modules under `backend_v2/services/orchestrator/dag_executor/` MUST contain zero `asyncio.Semaphore` or `asyncio.Event` primitives (enforced by `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L89-L121]`).
  2. **Two-Lock State & Persistence Synchronization**: In-memory mutations to `ExecutionRecord` execute exclusively inside `async with _update_lock:`, while database persistence executes inside `async with _commit_lock:` via `ExecutionCommitter.commit_trace` (`@[backend_v2/services/orchestrator/dag_executor.py#L316-L359]`).
  3. **Python 3.14 `asyncio.TaskGroup` Concurrency**: Blueprint pre-fetching (`@[backend_v2/services/orchestrator/dag_executor.py#L720-L730]`) and topological wave step execution (`@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]`) execute exclusively via `async with asyncio.TaskGroup() as tg:` with `except* BaseException as eg:` error trapping (enforced by `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L124-L134]`).
  4. **OpenTelemetry Span Hierarchy**: Root workflow orchestration starts span `dag.orchestration` with `execution.id`, `workflow.id`, and `workflow.node_count`, while step execution starts or reuses span `dag.node.{step_id}` with `node.id`, `node.blueprint`, `node.depends_on`, and `node.duration_ms` without serializing raw user prompts or PII.
  5. **Dead Letter Queue (DLQ) & RFC 7807 Dual-Reporting**: All step, node, and commit failures route deterministically through `ExecutionCommitter.commit_trace`, `NodeExecutor._dlq_record_node_error`, `DAGExecutor._dlq_record_step_failure`, `DAGExecutor._dlq_handle_progress_commit_error`, and `DAGExecutor._dlq_fallback_step_exceptions`.

---

## 2. AST Symbol-to-Target Module Mapping (`_ast_boundary_utils.py`)

| Symbol Name | AST Kind | Original Bounds (`dag_executor.py`) | Target Sub-Module (`backend_v2/services/orchestrator/dag_executor/`) | Extraction Phase | Re-Exported in `dag_executor/__init__.py` |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FrozenContextUpdate` | PEP 695 `type` Alias | Lines `89` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Yes (`__all__`) |
| `ExecutionRecordUpdate` | PEP 695 `type` Alias | Lines `90-91` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Yes (`__all__`) |
| `StepOutputContentValue` | PEP 695 `type` Alias | Lines `93` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Yes (`__all__`) |
| `transform_causal_nodes_to_atoms` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` | Phase 1 | Yes (`__all__`) |
| `compute_causal_tda_fusion_result` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L128-L300]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` | Phase 1 | Yes (`__all__`) |
| `ExecutionCommitter` | `ClassDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L303-L359]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Yes (`__all__`) |
| `ExecutionCommitter.__init__` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L306-L314]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Via `ExecutionCommitter` |
| `ExecutionCommitter.commit_trace` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L316-L359]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | Phase 1 | Via `ExecutionCommitter` |
| `NodeExecutor` | `ClassDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L362-L597]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | Phase 2 | Yes (`__all__`) |
| `NodeExecutor.__init__` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L365-L374]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | Phase 2 | Via `NodeExecutor` |
| `NodeExecutor._dlq_record_node_error` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L376-L384]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | Phase 2 | Via `NodeExecutor` |
| `NodeExecutor._resolve_execution_engine` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L386-L398]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | Phase 2 | Via `NodeExecutor` |
| `NodeExecutor.execute` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L400-L597]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/node_executor.py]` | Phase 2 | Via `NodeExecutor` |
| `WorkflowExecutionState` | `@dataclass` State Container | Unnested from `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` | Phase 2 | Yes (`__all__`) |
| `DAGExecutor._dlq_record_step_failure` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L603-L606]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (delegated from `DAGExecutor`) | Phase 2 | Via `DAGExecutor` |
| `DAGExecutor._dlq_handle_progress_commit_error` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L608-L616]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (delegated from `DAGExecutor`) | Phase 2 | Via `DAGExecutor` |
| `DAGExecutor._dlq_fallback_step_exceptions` | `FunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L618-L632]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` (delegated from `DAGExecutor`) | Phase 2 | Via `DAGExecutor` |
| `_fetch_and_validate` / `bootstrap_workflow_execution_state` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L720-L730]` & `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` | Phase 2 | Yes (`__all__`) |
| `_safe_commit` / `safe_commit_execution_state` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L991-L1004]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` | Phase 2 | Yes (`__all__`) |
| `_emit_preflight_progress` / `execute_rag_preflight_stage` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L1598-L1623]` & `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/workflow_bootstrap_stage.py]` | Phase 2 | Yes (`__all__`) |
| `run_step_wrapper` & `progress_callback` / `execute_dag_step_wrapper` | `AsyncFunctionDef` | `@[backend_v2/services/orchestrator/dag_executor.py#L1006-L1564]` & `@[backend_v2/services/orchestrator/dag_executor.py#L1264-L1293]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/step_execution_stage.py]` | Phase 3 | Yes (`__all__`) |
| `execute_topological_waves_stage` | `AsyncFunctionDef` | Unnested from `@[backend_v2/services/orchestrator/dag_executor.py#L686-L1803]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/wave_orchestrator_stage.py]` | Phase 3 | Yes (`__all__`) |
| `DAGExecutor` (`__init__`, `execute_workflow`) | `ClassDef` Facade | `@[backend_v2/services/orchestrator/dag_executor.py#L600-L1803]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` | Phase 4 | Yes (`__all__`) |

---

## 3. 1-Hop Caller & Guardrail Blast-Radius Inventory

### 3.1 Production 1-Hop Callers (3 Files)
| Caller File | AST Symbol Bounds | Imported Symbol(s) | Migration Strategy |
| :--- | :--- | :--- | :--- |
| `@[backend_v2/api/dependencies.py]` | `@[backend_v2/api/dependencies.py#L376-L417]`, `@[backend_v2/api/dependencies.py#L423-L458]` | `from backend_v2.services.orchestrator.dag_executor import DAGExecutor` | Preserved 100% via canonical package root `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` |
| `@[backend_v2/services/execution/facade.py]` | `@[backend_v2/services/execution/facade.py#L44-L271]`, `@[backend_v2/services/execution/facade.py#L47-L118]` | `from backend_v2.services.orchestrator.dag_executor import DAGExecutor` | Preserved 100% via canonical package root `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` |
| `@[backend_v2/worker.py]` | `@[backend_v2/worker.py#L44-L85]` | `from backend_v2.services.orchestrator.dag_executor import DAGExecutor` | Preserved 100% via canonical package root `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` |

### 3.2 AST Guardrail & Boundary Scripts Referencing `dag_executor.py` (4 Files)
| Guardrail File | AST Symbol Bounds | Reference Detail | Cutover Action |
| :--- | :--- | :--- | :--- |
| `@[scripts/_ast_guardrails.py]` | `@[scripts/_ast_guardrails.py#L730-L820]` (`visit_Module`) & module-level sets | `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` & `RESIDUAL_FUTURE_PHASE_QGR028_FILES` list `"backend_v2/services/orchestrator/dag_executor.py"` | Register new sub-modules as they are created in Phases 1–3; in Phase 4 remove `"backend_v2/services/orchestrator/dag_executor.py"` from residual sets and lock `"backend_v2/services/orchestrator/dag_executor.py"` under `QGR017` in `visit_Module` |
| `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py]` | `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L89-L121]`, `@[backend_v2/tests/unit/test_ast_concurrency_guardrails.py#L124-L134]` | Checks `base / "services" / "orchestrator" / "dag_executor.py"` for zero `asyncio.Semaphore` and presence of `asyncio.TaskGroup` | In Phase 4, scan all `*.py` files in `base / "services" / "orchestrator" / "dag_executor"` for zero `Semaphore` and verify `TaskGroup` in `workflow_bootstrap_stage.py` and `wave_orchestrator_stage.py` |
| `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]` | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L400-L409]` | Scans `Path("backend_v2/services/orchestrator/dag_executor.py")` for `StepType` enum dispatch | In Phase 4, scan all `*.py` files in `Path("backend_v2/services/orchestrator/dag_executor")` |
| `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py]` | `@[backend_v2/tests/unit/test_rest_only_pipeline_boundary.py#L117-L122]` | Asserts `"sys_render"` is absent from `Path("backend_v2/services/orchestrator/dag_executor.py")` | In Phase 4, scan all `*.py` files in `Path("backend_v2/services/orchestrator/dag_executor")` |

### 3.3 Existing Test Suite Callers & Monkeypatch Compatibility (13 Files)
1. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py]`
2. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_causal_fusion.py]`
3. `@[backend_v2/tests/unit/services/orchestrator/test_causal_tda_fusion.py]`
4. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_atom_ceiling.py]`
5. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_dlq_routing.py]`
6. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_audit.py]`
7. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]`
8. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_preflight.py]`
9. `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor_telemetry.py]`
10. `@[backend_v2/tests/unit/test_concurrency_fuzzer.py]`
11. `@[backend_v2/tests/unit/test_dag_executor_prompt_blocks.py]`
12. `@[backend_v2/tests/unit/test_dag_taskgroup.py]`
13. `@[backend_v2/tests/unit/test_llm_context_bounds.py]`

- **Test Patch Forwarding Contract**: Existing test suites patch `backend_v2.services.orchestrator.dag_executor.hook_registry`, `backend_v2.services.orchestrator.dag_executor.get_settings`, `backend_v2.services.orchestrator.dag_executor.Step.model_validate`, `backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix`, and `backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy`. Extracted sub-modules MUST resolve module-level patchable collaborators (`get_settings`, `hook_registry`, `Step`, `MatrixReducer`, `NodeStrategyFactory`) dynamically from `sys.modules.get("backend_v2.services.orchestrator.dag_executor")` when present (falling back to their direct module imports), and `[NEW] @[backend_v2/services/orchestrator/dag_executor/__init__.py]` MUST explicitly re-export those symbols (`get_settings as get_settings`, `hook_registry as hook_registry`, `Step as Step`, `MatrixReducer as MatrixReducer`, `NodeStrategyFactory as NodeStrategyFactory`) so 100% of existing test patches continue functioning without modification.
