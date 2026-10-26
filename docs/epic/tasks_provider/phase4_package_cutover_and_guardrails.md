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
Execute the final Epoch 1 Cutover of the `backend_v2/llm/provider.py` decomposition:
1. Migrate all 16 unit test functions from the monolithic `@[backend_v2/tests/unit/llm/test_provider.py]` (1,153 lines) into `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` and the modular submodule test suites under `backend_v2/tests/unit/llm/provider/` with zero test loss, delete `@[backend_v2/tests/unit/llm/test_provider.py]`, and update imports in `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]`, `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]`, and `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]`.
2. Atomically replace `@[backend_v2/llm/provider.py]` with the domain package facade `[NEW] @[backend_v2/llm/provider/__init__.py]` (`< 160` lines) and rewire 1-hop production callers (`@[backend_v2/llm/client.py#L46-L58]`, `@[backend_v2/llm/handler.py#L878-L1057]`, `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]`) to import from the new domain submodules while maintaining `backend_v2.llm.provider` package facade exports for orchestrator callers (`dag_executor.py`, `enriched_dag_executor.py`, `extractive_sensor_service.py`).
3. Update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L98-L107]` from `"backend_v2/llm/provider.py"` to `"backend_v2/llm/provider/__init__.py"`, register the retired file path `"backend_v2/llm/provider.py"` under `QGR017` in `visit_Module` (`@[scripts/_ast_guardrails.py#L619-L678]`), update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2065-L2075]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/__init__.py]` | Canonical package facade (`< 160` lines) re-exporting all public and internal provider symbols with explicit `__all__` and redundant aliases (`Symbol as Symbol`) |
| `[DELETE]` | `@[backend_v2/llm/provider.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/llm/client.py#L46-L58]` | Rewire `LLMFactory` import (line 24, used in `LLMClient.__init__` `#L46-L58`) to `backend_v2.llm.provider.provider_factory` |
| `[MODIFY]` | `@[backend_v2/llm/handler.py#L878-L1057]` | Rewire `LLMProvider` and `LLMFactory` imports (line 21, used in `LLMHandler.create_provider_for_strategy` `#L878-L1057`) to `backend_v2.llm.provider.base_and_mock_provider` and `backend_v2.llm.provider.provider_factory` |
| `[MODIFY]` | `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]` | Rewire `_is_transient_llm_error` import (line 24, used in `GenericMCPClient._execute_http_with_retry` `#L447-L509`) to `backend_v2.llm.provider.transient_retry_policy` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` | Modular unit tests for `backend_v2.llm.provider` package facade (`__init__.py`) migrating remaining tests from `test_provider.py` |
| `[DELETE]` | `@[backend_v2/tests/unit/llm/test_provider.py]` | Delete monolithic 1,153-line test file after migrating all 16 test functions into `backend_v2/tests/unit/llm/provider/` |
| `[MODIFY]` | `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]` | Verify imports and patch targets against `backend_v2.llm.provider` package |
| `[MODIFY]` | `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]` | Verify imports and patch targets against `backend_v2.llm.provider` package |
| `[MODIFY]` | `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]` | Verify imports and patch targets against `backend_v2.llm.provider` package |
| `[MODIFY]` | `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]` | Verify imports and patch targets against `backend_v2.llm.provider` package |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L619-L678]` | Replace `"backend_v2/llm/provider.py"` with `"backend_v2/llm/provider/__init__.py"` in `BOUNDARY_EXEMPTION_FILES` and register `backend_v2/llm/provider.py` under `QGR017` in `visit_Module` |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]` | Update `test_purged_boundary_exemption_files` (`#L1146-L1180`) and `test_qgr027_boundary_exempt_file_permitted` (`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2065-L2075]`) to `"backend_v2/llm/provider/__init__.py"`, and add `QGR017` test for banned `backend_v2/llm/provider.py` file path |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update `backend_v2/llm/` directory reference from `provider.py` to `provider/ (env_and_schema_utils.py, transient_retry_policy.py, base_and_mock_provider.py, provider_factory.py, litellm_response_stage.py, litellm_provider.py, __init__.py facade)` |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `provider.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` (Phase 1)
- `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` (Phase 1)
- `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (Phase 2)
- `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (Phase 2)
- `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (Phase 3)
- `[NEW] @[backend_v2/llm/provider/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/llm/client.py#L46-L58]` (Phase 4)
- `[MODIFY] @[backend_v2/llm/handler.py#L878-L1057]` (Phase 4)
- `[MODIFY] @[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Modularize Unit Test Suite under tests/unit/llm/provider/">
    <constraint invariant="test_directory_isolation">All unit tests from test_provider.py MUST be migrated into modular test suites under backend_v2/tests/unit/llm/provider/ with zero test loss across the 16 test functions.</constraint>
    <action>
      1. Migrate all 16 test functions from `@[backend_v2/tests/unit/llm/test_provider.py]` into `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_facade.py]` and the per-submodule test suites (`test_env_and_schema_utils.py`, `test_transient_retry_policy.py`, `test_base_and_mock_provider.py`, `test_provider_factory.py`, `test_litellm_response_stage.py`, `test_litellm_provider.py`) under `backend_v2/tests/unit/llm/provider/`, keeping each test file under 450 lines.
      2. Physically delete `@[backend_v2/tests/unit/llm/test_provider.py]`.
      3. Verify and update submodule imports in `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]`, `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]`, and `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]`.
    </action>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Rewire 1-Hop Callers">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/llm/provider.py and create backend_v2/llm/provider/__init__.py in a single atomic step.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/llm/provider/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/llm/provider/__init__.py]` (`< 160` lines) with `__all__` and explicit redundant re-exports (`Symbol as Symbol`) for all symbols from `env_and_schema_utils.py`, `transient_retry_policy.py`, `base_and_mock_provider.py`, `provider_factory.py`, `litellm_response_stage.py`, and `litellm_provider.py`, plus `apply_provider_pacing as apply_provider_pacing`, `get_settings as get_settings`, `MockLLMService as MockLLMService`, and `otel_trace as otel_trace`.
      2. Physically delete `@[backend_v2/llm/provider.py]`.
      3. Rewire 1-hop production callers outside `backend_v2/services/orchestrator/`:
         - `@[backend_v2/llm/client.py#L46-L58]` (`from backend_v2.llm.provider.provider_factory import LLMFactory`, while allowing `backend_v2.llm.provider.LLMFactory.create_provider` patches on the shared `LLMFactory` class object)
         - `@[backend_v2/llm/handler.py#L878-L1057]` (`from backend_v2.llm.provider.base_and_mock_provider import LLMProvider` and `from backend_v2.llm.provider.provider_factory import LLMFactory`)
         - `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]` (`from backend_v2.llm.provider.transient_retry_policy import _is_transient_llm_error`)
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/ --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/llm/client.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Path in QGR017 AST Guardrails and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py.</constraint>
    <action>
      1. Modify `@[scripts/_ast_guardrails.py#L619-L678]` (`visit_Module`) to emit a FATAL `QGR017` violation if `norm_path == "backend_v2/llm/provider.py" or norm_path.endswith("/backend_v2/llm/provider.py")`, and update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L98-L107]` from `"backend_v2/llm/provider.py"` to `"backend_v2/llm/provider/__init__.py"`.
      2. Update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]` (`test_purged_boundary_exemption_files`) and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2065-L2075]` (`test_qgr027_boundary_exempt_file_permitted`) to reference `"backend_v2/llm/provider/__init__.py"`, and add `test_qgr017_banned_provider_god_file_path_fatal` and `test_qgr017_modular_provider_package_allowed`.
      3. Modify `@[.agents/rules/04_directory_reference.md]` under `backend_v2/llm/` to replace `provider.py` with `provider/ (env_and_schema_utils.py, transient_retry_policy.py, base_and_mock_provider.py, provider_factory.py, litellm_response_stage.py, litellm_provider.py, __init__.py facade)`.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/ --test --ast-strict`, `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`, and `uv run python backend_v2/seed/run_seed.py local`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_provider_package_facade_reexports_all_symbols">
      Verifies that importing LiteLLMProvider, MockProvider, LLMFactory, LLMProvider, LogfireShieldedClient, and retry helpers from backend_v2.llm.provider works identically after replacing provider.py with provider/__init__.py.
    </contract>
    <contract type="positive" name="test_qgr017_modular_provider_package_allowed">
      Verifies that scanning backend_v2/llm/provider/__init__.py and its submodules produces zero QGR017 violations.
    </contract>
    <contract type="negative" name="test_qgr017_banned_provider_god_file_path_fatal">
      Verifies that scanning retired path backend_v2/llm/provider.py triggers a FATAL QGR017 violation in QuorumGuardrailVisitor.
    </contract>
  </test_contracts>
</execution_protocol>
```
