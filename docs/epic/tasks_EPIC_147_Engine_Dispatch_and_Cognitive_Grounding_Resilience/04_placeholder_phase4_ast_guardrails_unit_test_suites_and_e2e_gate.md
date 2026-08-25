# Phase 4: AST Guardrails, Unit Test Suites, Mock Migrations & E2E Integration Gate

**Overview:** Establish the comprehensive AST Guardrail suite in `test_ast_engine_dispatch_guardrails.py` locking all 5 architectural invariants (hook registration, zero procedural string routing in DAGExecutor, zero in-place `frozen_ctx.generated_schemas` mutations, mathematical set parity in `PromptBlockRepository`, and hook state immutability), finalize all unit test suites and mock migrations across the backend, run the full backend quality loop, and execute the final Live E2E REST API verification gate.
**Target Files:**
- `[NEW]` @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/engines/test_prompt_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/database/repositories/components/test_prompt_block.py#L25-L35]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_source_verification_service.py#L109-L139]
- `[NEW]` @[backend_v2/tests/unit/hooks/test_source_verification_hook.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/strategies/test_node_strategy_registry.py]
- `[NEW]` @[backend_v2/tests/unit/services/orchestrator/test_dag_executor_mcp_concurrency.py]
- `[MODIFY]` @[backend_v2/tests/integration/test_integration_real_llm.py]

Source: @[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md#L638-L654] Phase 4: AST Guardrails, Unit Test Suites, Mock Migrations & E2E Integration Gate

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3. Verify all domain components, engines, strategies, and hooks are modernized and passing their unit tests.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true across all modified files before locking AST guardrails and running the full integration gate.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_147_Engine_Dispatch_and_Cognitive_Grounding_Resilience.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [x] All 5 AST guardrails implemented and passing in [NEW] @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py].
    - [x] Comprehensive unit test suites created/updated for `PromptEngine`, `NodeStrategyFactory`, `test_dag_executor_mcp_concurrency.py`, `test_prompt_block.py`, and `test_source_verification_hook.py`.
    - [x] Full backend audit loop passes: `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
    - [x] Live E2E verification passes: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (Bash) / `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py` (PowerShell).
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
  </touched_artifacts>

  <anti_targets>
    - Do NOT skip or silence any unit tests.
    - Do NOT modify Flutter frontend files in this backend plan.
  </anti_targets>

  <step id="1" name="Create AST Guardrail Suite">
    <action>Create [NEW] @[backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py] locking all 5 architectural invariants:
      1. `test_source_verification_hook_registered_and_safe`: Inspects AST of `source_verification_hook.py` in @[backend_v2/hooks/source_verification_hook.py#L34-L85] to verify `@hook_registry.register` is attached and no hardcoded mock API keys exist.
      2. `test_node_strategy_registry_ast_has_no_procedural_string_routing`: Inspects AST of `dag_executor.py` in @[backend_v2/services/orchestrator/dag_executor.py#L115-L324] to assert that no raw string comparisons `step_def.type == "logic"` exist and routing strictly utilizes `StepType` enum keys in `NODE_STRATEGY_REGISTRY`.
      3. `test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation`: Inspects AST of `backend_v2/services/orchestrator/strategies/llm.py` in @[backend_v2/services/orchestrator/strategies/llm.py#L56-L781] to assert that zero in-place mutations of `frozen_ctx.generated_schemas` exist.
      4. `test_prompt_block_repo_ast_strict_missing_parity`: Inspects AST of `backend_v2/database/repositories/components/prompt_block.py` in @[backend_v2/database/repositories/components/prompt_block.py#L14-L174] to verify that `get_prompt_blocks_by_ids` performs mathematical set difference validation (`unique_requested - found_ids`) and raises `AppException(RESOURCE_NOT_FOUND)` when `missing_ids` is non-empty.
      5. `test_hook_state_immutability_and_no_inplace_metadata_mutation`: Inspects AST of `backend_v2/services/orchestrator/strategies/llm.py` and `backend_v2/hooks/` to assert that zero in-place mutations of `hook_state.metadata[...]` or `hook_state.inputs[...]` exist, enforcing immutable state copies.
    </action>
    <test_contracts>
      <test name="test_source_verification_hook_registered_and_safe" category="positive">
        <input>backend_v2/hooks/source_verification_hook.py AST</input>
        <expected>@hook_registry.register is present, 0 mock api keys</expected>
      </test>
      <test name="test_node_strategy_registry_ast_has_no_procedural_string_routing" category="positive">
        <input>backend_v2/services/orchestrator/dag_executor.py AST</input>
        <expected>0 raw string step_def.type == "logic" checks</expected>
      </test>
      <test name="test_llm_strategy_ast_has_no_frozen_ctx_generated_schemas_mutation" category="positive">
        <input>backend_v2/services/orchestrator/strategies/llm.py AST</input>
        <expected>0 in-place frozen_ctx.generated_schemas assignments</expected>
      </test>
      <test name="test_prompt_block_repo_ast_strict_missing_parity" category="positive">
        <input>backend_v2/database/repositories/components/prompt_block.py AST</input>
        <expected>contains mathematical set difference and raises AppException(RESOURCE_NOT_FOUND)</expected>
      </test>
      <test name="test_hook_state_immutability_and_no_inplace_metadata_mutation" category="positive">
        <input>backend_v2/services/orchestrator/strategies/llm.py and hooks AST</input>
        <expected>0 in-place hook_state.metadata mutations</expected>
      </test>
    </test_contracts>
    <constraint invariant="ast_guardrail_mandate">AST Guardrail tests mathematically enforce structural invariants before completion.</constraint>
  </step>

  <step id="2" name="Global Unit Test Verification">
    <action>Execute all unit test suites across repositories, engines, strategies, hooks, and AST guardrails.</action>
    <constraint invariant="universal_fail_fast">Zero tolerance for failing tests or deprecation warnings.</constraint>
  </step>

  <step id="3" name="Live E2E Integration Gate">
    <action>Run the live E2E REST API integration test:
      - Windows PowerShell: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
      - Linux / macOS Bash: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`
    </action>
    <constraint invariant="universal_quality_gate">Full E2E suite must pass with live foundational models.</constraint>
  </step>

  <validation_gate>
    <action>Execute AST Guardrail Suite: `uv run pytest backend_v2/tests/unit/test_ast_engine_dispatch_guardrails.py`</action>
    <action>Execute Global Backend Quality Loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
    <action>Execute Live E2E Integration Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`</action>
  </validation_gate>
</execution_protocol>
```
