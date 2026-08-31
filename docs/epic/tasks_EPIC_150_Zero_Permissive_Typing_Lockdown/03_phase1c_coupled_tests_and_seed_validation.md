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

# Phase 1C: Coupled Service Tests & Seed Vault Pre-Flight In-Memory Validation

## Overview

Complete the Phase 1 atomic vertical slice by migrating all remaining coupled service/hook test suites to `LLMMessageDTO` contracts and dot-notation assertions. Eliminate the seeder boot crash vulnerability in `backend_v2/seed/run_seed.py` by implementing the Two-Phase Pre-Flight In-Memory Validation pattern, and eliminate `isinstance(dict)` duck-typing in `seed_registry.py`.

## Target Files

- `[MODIFY]` `@[backend_v2/seed/seed_registry.py]`
- `[MODIFY]` `@[backend_v2/seed/run_seed.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/seed/test_run_seed.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/mcp/test_tool_loop_sanitization.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_llm_task_executor.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_llm_task_executor.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_interaction_hook.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_chat_parser.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/hooks/test_input_processing.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/dtos/test_prompt_context.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_finops_telemetry.py]`
- `[MODIFY]` `@[backend_v2/tests/integration/test_caching_integration.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/services/test_source_verification_service.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/seed/seed_registry.py]</backend>
      <backend>@[backend_v2/seed/run_seed.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="SeederTwoPhaseValidation">
      def validate_all_seed_collections(seed_data: dict[str, Any]) -> list[ValidationError]:
          # Phase 1: validate 100% of items in memory across STANDARD_REGISTRY before db.drop_tables()
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/progress.py]</file>
    <file>@[backend_v2/models/v2_core.py]</file>
    <file>@[backend_v2/worker.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Two-Phase Pre-Flight In-Memory Validation implemented in run_seed.py; zero drop_tables execution if validation fails</item>
    <item>isinstance(dict) duck-typing in _system_config_discriminator in seed_registry.py replaced by direct attribute dispatch / pure discriminator tag</item>
    <item>Zero raw dict message fixtures in test_mcp_tool_loop.py, test_llm_task_executor.py, and all coupled test suites</item>
    <item>All test assertions use dot-notation (flat[n].role, msg.content) instead of dictionary subscript indexing</item>
    <item>Global Phase 1 quality gate passes 100% green</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 1A and Phase 1B models and adapter changes compile cleanly.</action>
    <action>Inspect backend_v2/seed/run_seed.py and backend_v2/seed/seed_registry.py.</action>
  </step>

  <step id="1" name="HARDEN SEED REGISTRY & IMPLEMENT TWO-PHASE SEEDER VALIDATION">
    <action>In @[backend_v2/seed/seed_registry.py], eliminate isinstance(v, dict) duck-typing check in _system_config_discriminator (# noqa: QGR012) using direct attribute dispatch or pure discriminator tag.</action>
    <action>In @[backend_v2/seed/run_seed.py], implement Two-Phase Pre-Flight In-Memory Validation: Phase 1 parses and validates 100% of all items across STANDARD_REGISTRY in memory; Phase 2 executes drop_tables() and database inserts ONLY if Phase 1 passes with zero errors.</action>
    <action>In @[backend_v2/tests/unit/seed/test_run_seed.py], add unit tests verifying that invalid seed collections trigger graceful abort without dropping database tables.</action>
  </step>

  <step id="2" name="MIGRATE COUPLED MCP & EXECUTOR TEST SUITES">
    <action>In @[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py], migrate 15 messages= raw dict fixtures and 1 subscript assertion to LLMMessageDTO and dot-notation.</action>
    <action>In @[backend_v2/tests/unit/services/mcp/test_tool_loop_sanitization.py], migrate 9 raw dict fixtures and 2 subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/services/test_llm_task_executor.py] and @[backend_v2/tests/unit/test_llm_task_executor.py], migrate 16 message fixtures and 22 assertion lines.</action>
  </step>

  <step id="3" name="MIGRATE COUPLED PROMPT BUILDER & HOOK TEST SUITES">
    <action>In @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py] and @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py], update 33 assertion lines to dot-notation.</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py], update 7 assertion lines.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_interaction_hook.py], update 5 subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/services/test_chat_parser.py], update 4 subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py], @[backend_v2/tests/unit/models/dtos/test_prompt_context.py], @[backend_v2/tests/unit/test_finops_telemetry.py], @[backend_v2/tests/integration/test_caching_integration.py], and @[backend_v2/tests/unit/services/test_source_verification_service.py], migrate message fixtures and subscript assertions.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_seeder_aborts_without_dropping_tables_on_corrupt_data">
      <input>seed_data containing malformed item failing Pydantic validation</input>
      <expected>aborts with error, leaving existing database tables completely intact</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_seeder_preflight_validates_all_standard_collections">
      <input>valid seed_data.json</input>
      <expected>pre-flight passes 100% and proceeds to clean seeding</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 1 targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py backend_v2/seed/ backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/ backend_v2/tests/unit/services/test_llm_task_executor.py --test</command>
  </validation_gate>
</execution_protocol>
