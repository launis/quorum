<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 3B: Orchestrator Subsystem Suppression & Duck-Typing Eradication

## Overview

Eradicate all `# noqa: QGR` suppressions, `dict[str, Any]` annotations, and `isinstance(..., dict)` checks across 19 files in the Orchestrator subsystem (`backend_v2/services/orchestrator/`). Implement category pre-filtering and Discriminated Union validation for polymorphic DAG states (`synthesis_payload_compressor.py`, `strategies/llm.py`, `dag_executor.py`), and eliminate unhandled Pydantic validation bubbles.

## Target Files

- `[MODIFY]` `@[backend_v2/services/orchestrator/dag_executor.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompt_compiler.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/context_router.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_reducer.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/base.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/logic.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/enriched_dag_executor.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/two_pass_atomizer.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/synthesis_distiller.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/matrix_explanation_service.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/rag_preflight_service.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/localization_compiler.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/extraction_schema_factory.py]`
- `[MODIFY]` `@[backend_v2/services/orchestrator/anchor_validation_service.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 3: Hooks, Orchestrator & Repository Suppression Eradication]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/services/orchestrator/dag_executor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/synthesis_payload_compressor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/prompt_compiler.py]</backend>
      <backend>@[backend_v2/services/orchestrator/prompt_compiler_adapter.py]</backend>
      <backend>@[backend_v2/services/orchestrator/context_router.py]</backend>
      <backend>@[backend_v2/services/orchestrator/matrix_reducer.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/base.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/logic.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py]</backend>
      <backend>@[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py]</backend>
      <backend>@[backend_v2/services/orchestrator/enriched_dag_executor.py]</backend>
      <backend>@[backend_v2/services/orchestrator/two_pass_atomizer.py]</backend>
      <backend>@[backend_v2/services/orchestrator/synthesis_distiller.py]</backend>
      <backend>@[backend_v2/services/orchestrator/matrix_explanation_service.py]</backend>
      <backend>@[backend_v2/services/orchestrator/rag_preflight_service.py]</backend>
      <backend>@[backend_v2/services/orchestrator/localization_compiler.py]</backend>
      <backend>@[backend_v2/services/orchestrator/extraction_schema_factory.py]</backend>
      <backend>@[backend_v2/services/orchestrator/anchor_validation_service.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="OrchestratorPolymorphicPayloadHandling">
      # Heterogeneous DAG states validated strictly via Discriminated Unions or Category Pre-filtering
      # Zero isinstance(data, dict) checks
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/database/repositories/]</file>
    <file>@[backend_v2/models/domain/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero # noqa: QGR suppressions across all 19 orchestrator files</item>
    <item>Zero isinstance(..., dict) duck-typing checks in orchestrator</item>
    <item>SynthesisPayloadCompressor and DAGExecutor handle polymorphic payloads without naked dicts</item>
    <item>AST guardrails pass 100% clean on backend_v2/services/orchestrator/ in --strict mode</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 3A hook hardening passes AST guardrails cleanly.</action>
    <action>Inspect orchestrator strategies and executors for suppressions and duck-typing.</action>
  </step>

  <step id="1" name="HARDEN ORCHESTRATOR EXECUTORS & COMPILERS">
    <action>In @[backend_v2/services/orchestrator/dag_executor.py], eliminate 8 dict[str, Any] annotations, 2 QGR003, and 3 QGR012 suppressions.</action>
    <action>In @[backend_v2/services/orchestrator/synthesis_payload_compressor.py], eliminate 6 dict[str, Any] annotations via category pre-filtering and Discriminated Union TypeAdapters.</action>
    <action>In @[backend_v2/services/orchestrator/prompt_compiler.py] and @[backend_v2/services/orchestrator/prompt_compiler_adapter.py], eliminate dict[str, Any] and QGR001 reflection.</action>
    <action>In @[backend_v2/services/orchestrator/context_router.py] and @[backend_v2/services/orchestrator/matrix_reducer.py], eliminate QGR007, QGR012, and dict annotations.</action>
  </step>

  <step id="2" name="HARDEN STRATEGIES & PIPELINE SERVICES">
    <action>In @[backend_v2/services/orchestrator/strategies/llm.py], eliminate 9 dict[str, Any] annotations, 2 QGR003, and 19 QGR012 suppressions using direct DTO access and guarded TypeAdapter hydration.</action>
    <action>In @[backend_v2/services/orchestrator/strategies/base.py], @[backend_v2/services/orchestrator/strategies/logic.py], @[backend_v2/services/orchestrator/strategies/llm_execution/context_builder.py], and @[backend_v2/services/orchestrator/strategies/llm_execution/prompt_factory.py], eliminate dict[str, Any] annotations.</action>
    <action>In @[backend_v2/services/orchestrator/enriched_dag_executor.py], @[backend_v2/services/orchestrator/two_pass_atomizer.py], @[backend_v2/services/orchestrator/synthesis_distiller.py], @[backend_v2/services/orchestrator/matrix_explanation_service.py], @[backend_v2/services/orchestrator/rag_preflight_service.py], @[backend_v2/services/orchestrator/localization_compiler.py], @[backend_v2/services/orchestrator/extraction_schema_factory.py], and @[backend_v2/services/orchestrator/anchor_validation_service.py], eliminate all QGR suppressions and duck-typing.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_dag_executor_handles_discriminated_union_outputs">
      <input>DAG step emitting polymorphic atom result payload</input>
      <expected>validates and processes without dictionary coercion or KeyError</expected>
      <category>positive</category>
    </contract>
    <contract id="2" name="test_synthesis_compressor_category_prefiltering">
      <input>Synthesis payload containing mixed MATRIX and EXTRACTION step outputs</input>
      <expected>compresses and strata-sorts cleanly based on category_id without isinstance(dict)</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run AST guardrail scan and backend audit loop on Orchestrator subsystem:</action>
    <command>uv run python scripts/_ast_guardrails.py backend_v2/services/orchestrator/ --strict</command>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ --test</command>
  </validation_gate>
</execution_protocol>
