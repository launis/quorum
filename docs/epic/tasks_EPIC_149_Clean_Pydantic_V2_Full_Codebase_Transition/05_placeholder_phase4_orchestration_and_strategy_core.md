# Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)

**Phase Title:** Phase 4: Orchestration & Strategy Core Refactoring & Tests (CONSUMERS SECOND)
**Objective:** Eliminate ALL `isinstance(..., dict)`, `getattr()`, `.get()` branches from the orchestration engine and execution strategies, updating state transitions to use strictly typed dot-notation and immutable `model_copy(update={...})` within `async with _update_lock:`, and modernizing orchestrator unit tests atomically.

**Source Reference:** @[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md#L259-L286] (Phase 4: Orchestration & Strategy Core Refactoring & Tests)

**Expected Target Files:**
- `[MODIFY]` @[backend_v2/services/orchestrator/dag_executor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/base.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/prompt_compiler_adapter.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/context_router.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_payload_compressor.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/synthesis_distiller.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_explanation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/rag_preflight_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/localization_compiler.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/extraction_schema_factory.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/atomizer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/anchor_validation_service.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/matrix_reducer.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/tda_engine.py]
- `[MODIFY]` @[backend_v2/services/orchestrator/engines/synthesis_engine.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_dag_executor_prompt_blocks.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_dag_taskgroup.py]
- `[MODIFY]` @[backend_v2/tests/unit/services/test_llm_task_executor.py]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 3B. Verify hooks emit strictly typed HookDeltaDTO.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/services/orchestrator/dag_executor.py] and @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] All `isinstance(..., dict)`, `getattr()`, and `.get()` branches eliminated across all 19 orchestrator and strategy files.
    - [ ] `StrategyContext` and `ExecutionMetadata` accessed via direct typed dot-notation.
    - [ ] State mutations execute inside `async with _update_lock:` using `.model_copy(update=...)` strictly with typed instances.
    - [ ] Orchestrator unit tests in @[backend_v2/tests/unit/services/] modernized with polyfactory and typed fixtures.
    - [ ] Quality gate passes: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]</backend>
    <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/execution_time_resolver.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler.py]</backend>
    <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]</backend>
    <backend>@[backend_v2/services/orchestrator/context_router.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
    <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
    <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py]</backend>
    <backend>@[backend_v2/services/orchestrator/atomizer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/tda_engine.py]</backend>
    <backend>@[backend_v2/services/orchestrator/engines/synthesis_engine.py]</backend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `backend_v2/services/execution.py` in Phase 4 (reserved for Phase 5).
    - Do NOT re-introduce loose `dict` handling in DAG execution steps.
  </anti_targets>

  <step id="1" name="ORCHESTRATOR & STRATEGIES REFACTORING">
    <action>Refactor all orchestrator engines, strategies, and prompt compilers to use typed DTOs and direct dot-notation.</action>
    <action>Modernize orchestrator unit tests in `backend_v2/tests/unit/services/`.</action>
  </step>

  <validation_gate>
    uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test
  </validation_gate>
</execution_protocol>
```
