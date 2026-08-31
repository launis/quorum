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

# Phase 1B: LLM Adapters, Provider Pipeline & Coupled Adapter Tests

## Overview

Refactor all LLM provider adapters, provider client pipelines, and coupled adapter unit test suites. Eliminate all `isinstance(dict)` duck-typing and `dict[str, Any]` message handling. Enforce strict `[m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]` serialization at the outer LiteLLM boundary to guarantee zero `"tool_calls": None` / `"tool_call_id": None` null-field leakage into third-party SDK calls.

## Target Files

- `[MODIFY]` `@[backend_v2/llm/provider.py]`
- `[MODIFY]` `@[backend_v2/llm/client.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/base_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/vertex_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/ai_studio_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/anthropic_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/openai_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/deepseek_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/adapters/mock_adapter.py]`
- `[MODIFY]` `@[backend_v2/llm/ingress_pipeline.py]`
- `[MODIFY]` `@[backend_v2/llm/mock.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_base_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_mock_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py]`
- `[MODIFY]` `@[backend_v2/tests/test_vertex_adapter_caching_system_role.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_client.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_structured_retry.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/llm/provider.py]</backend>
      <backend>@[backend_v2/llm/client.py]</backend>
      <backend>@[backend_v2/llm/adapters/base_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/vertex_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/ai_studio_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/anthropic_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/openai_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/deepseek_adapter.py]</backend>
      <backend>@[backend_v2/llm/adapters/mock_adapter.py]</backend>
      <backend>@[backend_v2/llm/ingress_pipeline.py]</backend>
      <backend>@[backend_v2/llm/mock.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="BaseLLMAdapter.prepare_caching_payload">
      def prepare_caching_payload(self, compiled_prompt: CompiledPrompt, ...) -> tuple[...]
    </interface>
    <interface id="LiteLLMMessageSerialization">
      [m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in messages]
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/progress.py]</file>
    <file>@[backend_v2/models/v2_core.py]</file>
    <file>@[backend_v2/worker.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>Zero dict[str, Any] annotations in LLM adapters and client.py</item>
    <item>Zero isinstance(dict) checks and zero # noqa: QGR inline suppressions in LLM adapters</item>
    <item>Broad except Exception: in base_adapter.py (L60, L121) narrowed to (RedisError, ConnectionError, OSError) with structured logging</item>
    <item>LiteLLM message arrays serialized with exclude_none=True to prevent null-field leakage</item>
    <item>All coupled test files migrated from raw dict fixtures to LLMMessageDTO and from subscript indexing flat[n]["role"] to flat[n].role</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that LLMMessageDTO, PromptMetadataDTO, and ProviderMetadataDTO from Phase 1A are established and compilable.</action>
    <action>Inspect LLM provider adapters for remaining isinstance(dict) and raw dict access.</action>
  </step>

  <step id="1" name="MODERNIZE BASE ADAPTER & PROVIDER INFRASTRUCTURE">
    <action>In @[backend_v2/llm/adapters/base_adapter.py], eliminate 3 QGR002 suppressions and 4 isinstance(dict) checks (L190-L197). Narrow broad except Exception: (L60, L121) to (RedisError, ConnectionError, OSError) with RFC-7807 structured logging.</action>
    <demolish>
      REMOVE: raw_msg.get("role") and isinstance(raw_msg, dict) checks with # noqa: QGR012 in @[backend_v2/llm/adapters/base_adapter.py#L172-L219].
      REPLACE WITH: direct msg.role and msg.content attribute access on LLMMessageDTO instances.
    </demolish>
    <action>In @[backend_v2/llm/provider.py], isolate LiteLLM SDK response introspection (_hidden_params, model_extra, status_code) via explicit protocol mapping. Enforce [m.model_dump(mode="json", exclude_none=True) if isinstance(m, BaseModel) else m for m in final_messages] before passing to litellm.acompletion.</action>
    <action>In @[backend_v2/llm/client.py], eliminate 11 dict[str, Any] annotations and 6 hasattr/getattr on response objects via direct typed attribute access.</action>
    <action>In @[backend_v2/llm/ingress_pipeline.py] and @[backend_v2/llm/mock.py], eliminate isinstance(dict) checks.</action>
  </step>

  <step id="2" name="MODERNIZE PROVIDER ADAPTERS">
    <action>In @[backend_v2/llm/adapters/vertex_adapter.py], eliminate 2 QGR002 and 1 QGR003 suppressions. Enforce exclude_none=True on dynamic messages returned with cached resources.</action>
    <action>In @[backend_v2/llm/adapters/ai_studio_adapter.py], eliminate 2 QGR002 and 1 QGR003 suppressions. Narrow exceptions to (ConnectionError, TimeoutError) and enforce exclude_none=True.</action>
    <action>In @[backend_v2/llm/adapters/anthropic_adapter.py], eliminate 1 isinstance(dict) check and 8 dict[str, Any] annotations. Enforce exclude_none=True on block-structured Anthropic payloads.</action>
    <action>In @[backend_v2/llm/adapters/openai_adapter.py], eliminate remaining QGR suppressions and 5 dict[str, Any] annotations. Enforce exclude_none=True.</action>
    <action>In @[backend_v2/llm/adapters/deepseek_adapter.py] and @[backend_v2/llm/adapters/mock_adapter.py], migrate to LLMMessageDTO contracts with exclude_none=True serialization.</action>
  </step>

  <step id="3" name="MIGRATE ADAPTER TEST SUITES">
    <action>In @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py], migrate 38 raw dict fixtures and 1 assertion to LLMMessageDTO.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py], migrate 22 raw dict fixtures and 1 assertion to LLMMessageDTO.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_anthropic_adapter.py], migrate 12 raw dict fixtures and 19 flat[n]["role"] assertions to flat[n].role.</action>
    <action>In @[backend_v2/tests/unit/llm/adapters/test_base_adapter.py], @[backend_v2/tests/unit/llm/adapters/test_deepseek_adapter.py], @[backend_v2/tests/unit/llm/adapters/test_mock_adapter.py], and @[backend_v2/tests/unit/llm/adapters/test_openai_adapter.py], migrate raw dict fixtures to LLMMessageDTO.</action>
    <action>In @[backend_v2/tests/test_vertex_adapter_caching_system_role.py], @[backend_v2/tests/unit/llm/test_client.py], and @[backend_v2/tests/unit/llm/test_structured_retry.py], migrate message fixtures to LLMMessageDTO.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_adapter_serialization_omits_null_tool_fields">
      <input>LLMMessageDTO(role="user", content="hello", tool_calls=None, tool_call_id=None)</input>
      <expected>serialized dict contains only "role" and "content", with zero tool keys</expected>
      <category>boundary</category>
    </contract>
    <contract id="2" name="test_adapter_serialization_preserves_valid_tool_calls">
      <input>LLMMessageDTO(role="assistant", content="", tool_calls=[OpenAIToolCallDTO(id="call_1", function=OpenAIFunctionCallDTO(name="test", arguments="{}"))])</input>
      <expected>serialized dict contains "tool_calls" array and omits unset scalar attributes</expected>
      <category>positive</category>
    </contract>
    <contract id="3" name="test_base_adapter_narrowed_exceptions_logged">
      <input>RedisError raised during cache preparation</input>
      <expected>caught and logged with RFC-7807 structured parameters</expected>
      <category>error_path</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 1B targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/ backend_v2/tests/unit/llm/ --test</command>
  </validation_gate>
</execution_protocol>
