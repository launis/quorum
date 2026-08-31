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

Complete the Phase 1 atomic vertical slice by migrating all remaining coupled service/hook test suites to `LLMMessageDTO` contracts and dot-notation assertions. Eliminate the seeder boot crash vulnerability in `backend_v2/seed/run_seed.py` by implementing the Two-Phase Pre-Flight In-Memory Validation pattern, eliminate `isinstance(dict)` duck-typing in `seed_registry.py`, and modernize `PromptContextDTO` to strongly typed `LLMMessageDTO` collections.

## Target Files

- `[MODIFY]` `@[backend_v2/llm/provider.py]`
- `[MODIFY]` `@[backend_v2/seed/seed_registry.py]`
- `[MODIFY]` `@[backend_v2/seed/run_seed.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/prompt_context.py]`
- `[MODIFY]` `@[backend_v2/services/studio/simulation_service.py]`
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

---

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`backend_v2/seed/seed_registry.py`** | Banned `isinstance(v, dict)` in `_system_config_discriminator` (`# noqa: QGR012`). | Pure Pydantic V2 Discriminated Union via `Discriminator("type")` or direct attribute dispatch. | Pruned redundant custom discriminator callable; let Pydantic handle tag routing natively. | AST Guardrail scan passes with 0 violations; `test_run_seed.py` validates polymorphic system config hydration. |
| **`backend_v2/seed/run_seed.py`** | Banned destructive database wiping (`db.drop_tables()`) before validating seed data. | Two-Phase Pre-Flight In-Memory Validation pattern: Phase 1 validates 100% of collections in-memory before any DB drops; Phase 2 persists only if Phase 1 passes with zero errors. | Pruned speculative separate validator service classes; encapsulate clean in-memory buffer aggregation within `run_seed.py`. | Negative test `test_seeder_aborts_without_dropping_tables_on_corrupt_data` proves tables remain 100% intact on validation error. |
| **`backend_v2/models/dtos/prompt_context.py`** | Banned raw dictionaries (`list[dict[str, Any]]`) in `static_messages` and `dynamic_messages`. | Enforce `list[LLMMessageDTO]` with `ConfigDict(strict=True, extra="forbid", frozen=True)`. | Pruned nested dict conversion layers; expose direct DTO properties. | `test_prompt_context.py` validates 100% typed instantiation and defaults. |
| **Coupled MCP Test Suites** (`test_mcp_tool_loop.py`, `test_tool_loop_sanitization.py`) | Banned raw dict message fixtures (`[{"role": "user", "content": "..."}]`) and subscript access (`result.result_data["score"]`). | Pure `LLMMessageDTO` fixtures and dot-notation property access (`result_data.score` or typed assertions). | Reused central test factories (`make_llm_message`) without manual mock dict construction. | `backend_audit_loop.py` executes full test suite cleanly. |
| **Coupled Prompt Builder & Hook Test Suites** (`test_matrix_sensor_prompt_builder.py`, `test_chat_parser.py`, `test_interaction_hook.py`, etc.) | Banned subscript dictionary access on `CompiledPrompt` (`prompt.static_messages[0]["content"]`, `messages[1]["content"]`). | Enforce dot-notation access (`prompt.static_messages[0].content`, `messages[1].content`) across all 10 coupled test suites. | Pruned obsolete dictionary casting helpers. | Pytest suite passes 100% green without `TypeError: 'LLMMessageDTO' object is not subscriptable`. |

---

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/llm/provider.py]</backend>
      <backend>@[backend_v2/seed/seed_registry.py]</backend>
      <backend>@[backend_v2/seed/run_seed.py]</backend>
      <backend>@[backend_v2/models/dtos/prompt_context.py]</backend>
      <backend>@[backend_v2/services/studio/simulation_service.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="SeederTwoPhaseValidation">
      def validate_all_seed_collections(seed_data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
          # Phase 1: validate 100% of items in memory across STANDARD_REGISTRY before db.drop_tables()
    </interface>
    <interface id="PromptContextDTOContract">
      class PromptContextDTO(BaseDTO):
          static_messages: list[LLMMessageDTO]
          dynamic_messages: list[LLMMessageDTO]
          metadata: dict[str, Any]
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/progress.py]</file>
    <file>@[backend_v2/models/v2_core.py]</file>
    <file>@[backend_v2/worker.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item status="done">[x] Two-Phase Pre-Flight In-Memory Validation implemented in run_seed.py; zero drop_tables execution if validation fails</item>
    <item status="done">[x] isinstance(dict) duck-typing in _system_config_discriminator in seed_registry.py replaced by direct attribute dispatch / pure discriminator tag</item>
    <item status="done">[x] PromptContextDTO modernized to list[LLMMessageDTO] with 100% typed serialization</item>
    <item status="done">[x] Zero raw dict message fixtures in test_mcp_tool_loop.py, test_llm_task_executor.py, and all coupled test suites</item>
    <item status="done">[x] All test assertions use dot-notation (flat[n].role, msg.content) instead of dictionary subscript indexing</item>
    <item status="done">[x] Global Phase 1 quality gate passes 100% green</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>In @[backend_v2/llm/provider.py#L885-L905], append explicit justification blocks to `# noqa: QGR001` comments on lines 892, 893, 895 (e.g. `[REASON: External LiteLLM function name reflection]` and `[REASON: External LiteLLM tool call ID reflection]`) to ensure strict AST Guardrail compliance.</action>
    <action>Verify that Phase 1A and Phase 1B models and adapter changes compile cleanly.</action>
  </step>

  <step id="1" name="HARDEN SEED REGISTRY & IMPLEMENT TWO-PHASE SEEDER VALIDATION">
    <action>In @[backend_v2/seed/seed_registry.py#L1-L56], eliminate isinstance(v, dict) duck-typing check in _system_config_discriminator (# noqa: QGR012) using Discriminator("type") or direct attribute dispatch.</action>
    <action>In @[backend_v2/seed/run_seed.py#L102-L224] and @[backend_v2/seed/run_seed.py#L226-L347], implement Two-Phase Pre-Flight In-Memory Validation via `validate_all_seed_collections`: Phase 1 parses and validates 100% of all items across STANDARD_REGISTRY in memory; Phase 2 executes drop_tables() and database inserts ONLY if Phase 1 passes with zero errors.</action>
    <action>In @[backend_v2/tests/unit/seed/test_run_seed.py#L1-L430], add unit tests verifying that invalid seed collections trigger graceful abort without dropping database tables.</action>
  </step>

  <step id="2" name="MIGRATE PROMPT CONTEXT DTO & COUPLED MCP / EXECUTOR TEST SUITES">
    <action>In @[backend_v2/models/dtos/prompt_context.py#L1-L33], update static_messages and dynamic_messages fields to `list[LLMMessageDTO]` with `ConfigDict(strict=True, extra="forbid", frozen=True)`.</action>
    <action>In @[backend_v2/services/studio/simulation_service.py#L203-L208] and @[backend_v2/services/studio/simulation_service.py#L263-L266], update PromptContextDTO construction with `LLMMessageDTO` instances.</action>
    <action>In @[backend_v2/tests/unit/models/dtos/test_prompt_context.py#L1-L27], migrate unit test fixtures to `LLMMessageDTO`.</action>
    <action>In @[backend_v2/tests/unit/services/mcp/test_mcp_tool_loop.py#L55-L92], migrate raw dict fixtures and subscript assertions to `LLMMessageDTO` and dot-notation.</action>
    <action>In @[backend_v2/tests/unit/services/mcp/test_tool_loop_sanitization.py#L24-L110], migrate raw dict fixtures and subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/services/test_llm_task_executor.py#L30-L90] and @[backend_v2/tests/unit/test_llm_task_executor.py#L1-L150], migrate message fixtures and subscript assertion lines.</action>
  </step>

  <step id="3" name="MIGRATE COUPLED PROMPT BUILDER, HOOK & INTEGRATION TEST SUITES">
    <action>In @[backend_v2/tests/unit/services/orchestrator/prompts/test_matrix_sensor_prompt_builder.py#L25-L100] and @[backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py#L30-L110], update assertion lines to dot-notation (e.g. `prompt.static_messages[0].content`).</action>
    <action>In @[backend_v2/tests/unit/services/orchestrator/test_prompt_compiler_adapter.py#L50-L95], update assertion lines to dot-notation.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_interaction_hook.py#L290-L300], update subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/services/test_chat_parser.py#L70-L80], update subscript assertions.</action>
    <action>In @[backend_v2/tests/unit/hooks/test_input_processing.py#L1-L100], @[backend_v2/tests/unit/test_finops_telemetry.py#L100-L175], @[backend_v2/tests/integration/test_caching_integration.py#L110-L220], and @[backend_v2/tests/unit/services/test_source_verification_service.py#L105-L112], migrate message fixtures, json serialization, and subscript assertions.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_seeder_aborts_without_dropping_tables_on_corrupt_data">
      <input>seed_data containing malformed item failing Pydantic validation</input>
      <expected>aborts with error, leaving existing database tables completely intact without drop_tables execution</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_seeder_aborts_on_invalid_workflow_dag">
      <input>seed_data containing workflow with broken DAG compilation</input>
      <expected>aborts with error during pre-flight before database wipe</expected>
      <category>negative</category>
    </contract>
    <contract id="3" name="test_seeder_preflight_validates_all_standard_collections">
      <input>valid seed_data.json</input>
      <expected>pre-flight passes 100% and proceeds to clean seeding</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 1 targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/models/prompt.py backend_v2/models/llm.py backend_v2/models/dtos/prompt_context.py backend_v2/seed/ backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/ backend_v2/tests/unit/seed/ backend_v2/tests/unit/services/test_llm_task_executor.py backend_v2/tests/unit/services/mcp/ --test</command>
  </validation_gate>
</execution_protocol>
