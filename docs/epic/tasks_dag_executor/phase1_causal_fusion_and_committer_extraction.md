<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 1: Leaf Causal TDA Fusion & ExecutionCommitter Extraction (`phase1_causal_fusion_and_committer_extraction.md`)

## 1. Objective
Execute Phase 1 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/services/orchestrator/dag_executor.py]`:
1. Create the test package marker `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/__init__.py]` (`strangler_fig_mandate` rule 2: test subpackages require `__init__.py` from Step 1 to prevent Pytest flat-namespace collisions, while the source domain sub-directory `backend_v2/services/orchestrator/dag_executor/` MUST NOT contain `__init__.py` while `backend_v2/services/orchestrator/dag_executor.py` exists).
2. Extract depth-0 leaf causal TDA fusion functions (`transform_causal_nodes_to_atoms` `@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]` and `compute_causal_tda_fusion_result` `@[backend_v2/services/orchestrator/dag_executor.py#L128-L300]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` (`< 240` lines).
3. Extract depth-0 leaf PEP 695 type aliases (`FrozenContextUpdate`, `ExecutionRecordUpdate`, `StepOutputContentValue` from lines 89–93 of `@[backend_v2/services/orchestrator/dag_executor.py]`) and `ExecutionCommitter` (`@[backend_v2/services/orchestrator/dag_executor.py#L303-L359]`, including `__init__` `@[backend_v2/services/orchestrator/dag_executor.py#L306-L314]` and `commit_trace` `@[backend_v2/services/orchestrator/dag_executor.py#L316-L359]`) into `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` (`< 120` lines).
4. Add `"backend_v2/services/orchestrator/dag_executor/execution_committer.py"` to `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` in `@[scripts/_ast_guardrails.py]` during Epoch 1 pure structural lift-and-shift, wire `__path__` submodule resolution and explicit redundant re-exports (`Symbol as Symbol`) in `@[backend_v2/services/orchestrator/dag_executor.py]`, and create dedicated unit test suites in `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]` and `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` | Pure leaf functions `transform_causal_nodes_to_atoms` and `compute_causal_tda_fusion_result` (`< 240` lines, without `__init__.py` in `backend_v2/services/orchestrator/dag_executor/`) |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` | PEP 695 type aliases (`FrozenContextUpdate`, `ExecutionRecordUpdate`, `StepOutputContentValue`) and `ExecutionCommitter` (`__init__`, `commit_trace`) (`< 120` lines) |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/dag_executor.py]` | Declare `__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]` and replace `transform_causal_nodes_to_atoms` (`@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`), `compute_causal_tda_fusion_result` (`@[backend_v2/services/orchestrator/dag_executor.py#L128-L300]`), and `ExecutionCommitter` (`@[backend_v2/services/orchestrator/dag_executor.py#L303-L359]`) with explicit redundant re-exports (`Symbol as Symbol`) |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py]` | Register `"backend_v2/services/orchestrator/dag_executor/execution_committer.py"` in `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` during Epoch 1 pure structural lift-and-shift |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/__init__.py]` | Mandatory Pytest test package marker |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]` | Dedicated unit tests for `transform_causal_nodes_to_atoms` and `compute_causal_tda_fusion_result` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]` | Dedicated unit tests for `ExecutionCommitter.__init__` and `ExecutionCommitter.commit_trace` (dual-storage write, DB update, and DLQ error propagation) |

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
  <step id="1" name="Create Test Package Marker and Extract Leaf Causal TDA Fusion and ExecutionCommitter Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/services/orchestrator/dag_executor/__init__.py during Phase 1 while backend_v2/services/orchestrator/dag_executor.py exists on disk. Create backend_v2/tests/unit/services/orchestrator/dag_executor/__init__.py immediately.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither causal_tda_fusion.py nor execution_committer.py may import from backend_v2.services.orchestrator.dag_executor, and both MUST remain under 250 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/__init__.py]` containing a module docstring.
      2. Add `"backend_v2/services/orchestrator/dag_executor/execution_committer.py"` to `RESIDUAL_FUTURE_PHASE_JSONVALUE_FILES` in `@[scripts/_ast_guardrails.py]` so the relocated PEP 695 type aliases (`FrozenContextUpdate`, `ExecutionRecordUpdate`, `StepOutputContentValue`) inherit the exact same Open-JSON exemption as `dag_executor.py` during Epoch 1 lift-and-shift.
      3. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py]` (`< 240` lines, all lines `<= 120` chars) with `__all__ = ["compute_causal_tda_fusion_result", "transform_causal_nodes_to_atoms"]`:
         - Relocate `transform_causal_nodes_to_atoms` verbatim from `@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`.
         - Relocate `compute_causal_tda_fusion_result` verbatim from `@[backend_v2/services/orchestrator/dag_executor.py#L128-L300]`.
      4. Create `[NEW] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py]` (`< 120` lines, all lines `<= 120` chars) with `__all__ = ["ExecutionCommitter", "ExecutionRecordUpdate", "FrozenContextUpdate", "StepOutputContentValue"]`:
         - Relocate PEP 695 type aliases `FrozenContextUpdate`, `ExecutionRecordUpdate`, and `StepOutputContentValue` from lines 89–93 of `@[backend_v2/services/orchestrator/dag_executor.py]`.
         - Relocate `ExecutionCommitter` verbatim from `@[backend_v2/services/orchestrator/dag_executor.py#L303-L359]` (`__init__` `@[backend_v2/services/orchestrator/dag_executor.py#L306-L314]` and `commit_trace` `@[backend_v2/services/orchestrator/dag_executor.py#L316-L359]`).
    </action>
  </step>

  <step id="2" name="Rewire Explicit Redundant Re-Exports in dag_executor.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) and __path__ submodule bridging in backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Update `@[backend_v2/services/orchestrator/dag_executor.py]` (`@[backend_v2/services/orchestrator/dag_executor.py#L96-L125]`, `@[backend_v2/services/orchestrator/dag_executor.py#L128-L300]`, and `@[backend_v2/services/orchestrator/dag_executor.py#L303-L359]`):
         - Declare `__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]` before importing from `backend_v2.services.orchestrator.dag_executor.causal_tda_fusion` and `backend_v2.services.orchestrator.dag_executor.execution_committer` so Python's `importlib` resolves the sub-modules cleanly without `dag_executor/__init__.py`.
         - Replace the extracted definitions of `FrozenContextUpdate`, `ExecutionRecordUpdate`, `StepOutputContentValue`, `transform_causal_nodes_to_atoms`, `compute_causal_tda_fusion_result`, and `ExecutionCommitter` with explicit redundant re-exports (`Symbol as Symbol`).
      2. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_causal_tda_fusion_unit.py]` testing `transform_causal_nodes_to_atoms` (empty node list, multi-node mapping with `evidence_quote` and `confidence_prior`) and `compute_causal_tda_fusion_result` (strict falsification override to `scale_min`, epistemic elevation to `scale_max` when `raw_score == scale_min` and `confidence_prior >= 0.85`, and `CausalDiscoveryError` when `scale_min == scale_max`).
      3. Create `[NEW] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]` testing `ExecutionCommitter.commit_trace` (dual-storage `save_execution_trace` and `save_frozen_context` writes, lightweight DB `update` stripping `execution_trace` and `frozen_context`, and DLQ `logger.error` + re-raise when repository persistence fails).
    </action>
  </step>

  <step id="3" name="Run Phase 1 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules, scripts/_ast_guardrails.py, and backend_v2/services/orchestrator/dag_executor.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/causal_tda_fusion.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor/execution_committer.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/dag_executor.py --test --ast-strict` to verify all 76 baseline tests pass with `>= 90%` line coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_compute_causal_tda_fusion_result_falsification_and_elevation">
      Verifies that compute_causal_tda_fusion_result enforces strict falsification override to scale_min and epistemic elevation to scale_max identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_execution_committer_dual_storage_and_lightweight_db_update">
      Verifies that ExecutionCommitter.commit_trace persists execution_trace and frozen_context via StorageService and updates ExecutionRepository with lightweight state.
    </contract>
    <contract type="negative" name="test_compute_causal_tda_fusion_result_degenerate_scale_raises_error">
      Verifies that compute_causal_tda_fusion_result raises CausalDiscoveryError when scale_min equals scale_max and a falsified claim match occurs.
    </contract>
  </test_contracts>
</execution_protocol>
```
