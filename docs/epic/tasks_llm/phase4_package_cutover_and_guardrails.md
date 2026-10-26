<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 4: Consumer Import Rewiring, Test Modularization, Atomic Package Cutover & QGR017 Lockdown (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute the final Epoch 1 Cutover of the `LLMNodeStrategy` (`llm.py`) decomposition:
1. Split the monolithic unit test file `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` (3,597 lines, 42 tests) across the modular unit test suites under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/` (creating `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]` and expanding the stage test suites so all 42 tests from `test_llm.py` are preserved with zero test loss) and delete `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`.
2. Atomically replace `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` with the domain package facade `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` (`< 220` lines) and rewire all 1-hop consumer imports across production strategy modules and unit test suites to import from `backend_v2.services.orchestrator.strategies.llm_strategy`.
3. Register the retired module `backend_v2.services.orchestrator.strategies.llm` in `@[scripts/_ast_guardrails.py#L1892-L1992]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1994-L2212]` (`visit_ImportFrom`) under `QGR017`, remove `"backend_v2/services/orchestrator/strategies/llm.py"` from `RESIDUAL_FUTURE_PHASE_QGR028_FILES` in `@[scripts/_ast_guardrails.py]` and `[tool.ruff.lint.per-file-ignores]` in `@[pyproject.toml]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` | Canonical package facade (`< 220` lines) defining `LLMNodeStrategy` and re-exporting stage symbols with explicit `__all__` and redundant aliases |
| `[DELETE]` | `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/strategies/__init__.py]` | Rewire `LLMNodeStrategy` re-export from `.llm` to `.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]` | Rewire `LLMNodeStrategy` import (line 10, used in `_build_llm_strategy` `@[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]`) to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L412-L420]` | Update `test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation` (`#L412-L420`) and `test_hook_state_immutability_and_no_inplace_metadata_mutation` (`@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L437-L449]`) to scan all `.py` files under `backend_v2/services/orchestrator/strategies/llm_strategy/` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L345-L421]` | Update `patch` target in `test_dag_executor_parallel_execution` (`@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L345-L421]`) to `"backend_v2.services.orchestrator.strategies.llm_strategy.LLMNodeStrategy.execute"` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py#L44-L50]` | Rewire `LLMNodeStrategy` import to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py#L44-L50]` | Rewire `LLMNodeStrategy` import to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L139-L156]` | Rewire `LLMNodeStrategy` import and `patch` targets in `#L139-L156` and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L159-L251]` to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L144-L276]` | Rewire `LLMNodeStrategy` import and `patch` targets in `test_llm_strategy_propagates_engine_usage_to_trace_event` (`#L144-L276`) to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[MODIFY]` | `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py#L147-L303]` | Rewire `LLMNodeStrategy` import in `test_output_profile_directives_relocated_to_user_payload_and_system_prompt_invariant_neg09` (`#L147-L303`) to `backend_v2.services.orchestrator.strategies.llm_strategy` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]` | Modular unit tests for `LLMNodeStrategy` package facade (`__init__.py`) |
| `[DELETE]` | `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` | Delete monolithic 3,597-line test file after migrating all 42 tests into the modular test suites under `backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1892-L1992]` | Add `backend_v2.services.orchestrator.strategies.llm` to `QGR017` banned imports in `visit_Import` and remove `"backend_v2/services/orchestrator/strategies/llm.py"` from `RESIDUAL_FUTURE_PHASE_QGR028_FILES` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L1994-L2212]` | Add `backend_v2.services.orchestrator.strategies.llm` and `from backend_v2.services.orchestrator.strategies import llm` to `QGR017` banned imports in `visit_ImportFrom` |
| `[MODIFY]` | `@[pyproject.toml]` | Remove `"backend_v2/services/orchestrator/strategies/llm.py" = ["E501"]` from `[tool.ruff.lint.per-file-ignores]` |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update Pillar 3 (`backend_v2/services/`) directory reference from `llm.py` to `llm_strategy/ (blueprint_and_metadata_stage.py, prompt_and_schema_stage.py, engine_retry_stage.py, trace_event_stage.py, __init__.py facade)` |

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Modularize Unit Test Suite under strategies/llm_strategy/">
    <constraint invariant="test_directory_isolation">All unit tests for backend_v2/services/orchestrator/strategies/llm_strategy/ MUST reside under backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/ with zero test loss across the 42 tests from test_llm.py.</constraint>
    <action>
      1. Migrate all 42 unit tests from `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]` into `[NEW] @[backend_v2/tests/unit/services/orchestrator/strategies/llm_strategy/test_llm_strategy_facade.py]` and the stage test suites (`test_blueprint_and_metadata_stage.py`, `test_prompt_and_schema_stage.py`, `test_engine_retry_stage.py`, `test_trace_event_stage.py`).
      2. Physically delete `[DELETE] @[backend_v2/tests/unit/services/orchestrator/strategies/test_llm.py]`.
    </action>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Rewire 1-Hop Callers">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/services/orchestrator/strategies/llm.py and create backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py in a single atomic step.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/services/orchestrator/strategies/llm_strategy/__init__.py]` (`< 220` lines) defining `LLMNodeStrategy` (orchestrating `execute_blueprint_and_pre_hooks_stage`, `execute_prompt_and_schema_stage`, `execute_engine_retry_stage`, and `build_llm_step_trace_events`) with explicit redundant re-exports and `__all__`.
      2. Physically delete `[DELETE] @[backend_v2/services/orchestrator/strategies/llm.py]`.
      3. Rewire all 1-hop production and test callers to import `LLMNodeStrategy` from `backend_v2.services.orchestrator.strategies.llm_strategy`:
         - `@[backend_v2/services/orchestrator/strategies/__init__.py]`
         - `@[backend_v2/services/orchestrator/strategies/registry.py#L42-L60]`
         - `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L412-L420]` and `@[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py#L437-L449]`
         - `@[backend_v2/tests/unit/services/orchestrator/test_dag_executor.py#L345-L421]`
         - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py#L44-L50]`
         - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_registry.py#L44-L50]`
         - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L139-L156]` and `@[backend_v2/tests/unit/services/orchestrator/strategies/test_tier4_matrix_shuffled_atoms_regression.py#L159-L251]`
         - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_cost_tracking.py#L144-L276]`
         - `@[backend_v2/tests/unit/services/orchestrator/strategies/test_llm_strategy.py#L147-L303]`
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/registry.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Path in QGR017 AST Guardrails and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py.</constraint>
    <action>
      1. Modify `@[scripts/_ast_guardrails.py#L1892-L1992]` (`visit_Import`) and `@[scripts/_ast_guardrails.py#L1994-L2212]` (`visit_ImportFrom`) to ban imports of `backend_v2.services.orchestrator.strategies.llm` and `from backend_v2.services.orchestrator.strategies import llm` under `QGR017`, instructing callers to import from `backend_v2.services.orchestrator.strategies.llm_strategy`, and remove `"backend_v2/services/orchestrator/strategies/llm.py"` from `RESIDUAL_FUTURE_PHASE_QGR028_FILES`.
      2. Remove `"backend_v2/services/orchestrator/strategies/llm.py" = ["E501"]` from `[tool.ruff.lint.per-file-ignores]` in `@[pyproject.toml]`.
      3. Modify `@[.agents/rules/04_directory_reference.md]` under Pillar 3 (`backend_v2/services/`) to replace `llm.py` with `llm_strategy/ (blueprint_and_metadata_stage.py, prompt_and_schema_stage.py, engine_retry_stage.py, trace_event_stage.py, __init__.py facade)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_strategy/ --test --ast-strict`, `uv run pytest backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py`, and `uv run python backend_v2/seed/run_seed.py local`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_execute_success_path_structured_output">
      Verifies that importing LLMNodeStrategy from backend_v2.services.orchestrator.strategies.llm_strategy executes the full 4-stage pipeline and returns identical TraceEvent payloads.
    </contract>
    <contract type="positive" name="test_registry_creates_llm_strategy_with_engine">
      Verifies that NodeStrategyRegistry resolves LLMNodeStrategy from backend_v2.services.orchestrator.strategies.llm_strategy.
    </contract>
    <contract type="negative" name="test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation">
      Verifies that all sub-modules in backend_v2/services/orchestrator/strategies/llm_strategy/ contain zero in-place mutations of frozen_ctx.generated_schemas or hook_state.metadata.
    </contract>
  </test_contracts>
</execution_protocol>
```
