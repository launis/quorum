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

# Phase 1A: LLM Message & Prompt DTO Foundation & Core Test Migration

## Overview

Atomically refactor the foundational LLM prompt models and client infrastructure. Define `LLMMessageDTO`, `PromptMetadataDTO`, and `ProviderMetadataDTO` with strict frozen Pydantic V2 configuration. Update `CompiledPrompt` methods (`to_flat_messages()`, `to_static_flat()`, `to_dynamic_flat()`) to return `list[LLMMessageDTO]`, and modernize central test factories and models unit tests.

## Target Files

- `[MODIFY]` `@[backend_v2/models/llm.py]`
- `[MODIFY]` `@[backend_v2/models/prompt.py]`
- `[MODIFY]` `@[backend_v2/llm/caching_service.py]`
- `[MODIFY]` `@[backend_v2/utils/math_utils.py]`
- `[MODIFY]` `@[backend_v2/tests/conftest.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/models/test_prompt.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/llm/test_caching_service.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 1: LLM Prompt & Adapter Ecosystem Atomic Lockdown]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/models/llm.py]</backend>
      <backend>@[backend_v2/models/prompt.py]</backend>
      <backend>@[backend_v2/llm/caching_service.py]</backend>
      <backend>@[backend_v2/utils/math_utils.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="LLMMessageDTO">
      class LLMMessageDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          role: str
          content: str
          tool_calls: list[OpenAIToolCallDTO] | None = None
          tool_call_id: str | None = None
          name: str | None = None
    </interface>
    <interface id="PromptMetadataDTO">
      class PromptMetadataDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          token_proxy_score: float | None = None
          cache_key: str | None = None
          routing_tags: list[str] | None = None
    </interface>
    <interface id="ProviderMetadataDTO">
      class ProviderMetadataDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          finish_reason: str | None = None
          model_extra: dict[str, Any] | None = None
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/services/progress.py]</file>
    <file>@[backend_v2/models/v2_core.py]</file>
    <file>@[backend_v2/worker.py]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>LLMMessageDTO, PromptMetadataDTO, and ProviderMetadataDTO defined with ConfigDict(strict=True, extra="forbid", frozen=True)</item>
    <item>CompiledPrompt.static_messages and dynamic_messages typed strictly as list[LLMMessageDTO]</item>
    <item>CompiledPrompt.to_flat_messages(), to_static_flat(), and to_dynamic_flat() return list[LLMMessageDTO]</item>
    <item>Direct attribute access (msg.role, msg.content) replaces .get("role") and .get("content") fallbacks</item>
    <item>conftest.py provides make_llm_message helper locking role literals to ("system" | "user" | "assistant" | "tool")</item>
    <item>Unit tests in test_prompt.py and test_caching_service.py use dot-notation flat[n].role instead of dictionary subscript indexing</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify codebase baseline for backend_v2/models/prompt.py and backend_v2/models/llm.py.</action>
    <action>Verify OpenAIToolCallDTO SSOT availability from backend_v2/models/domain/mcp.py.</action>
  </step>

  <step id="1" name="DEFINE DTO MODELS IN LLM & PROMPT MODULES">
    <action>In @[backend_v2/models/llm.py], define LLMMessageDTO with frozen=True, strict=True, extra="forbid". Fields: role (str), content (str), tool_calls (list[OpenAIToolCallDTO] | None = None), tool_call_id (str | None = None), name (str | None = None).</action>
    <action>In @[backend_v2/models/llm.py], define ProviderMetadataDTO(BaseModel) with frozen=True, strict=True, extra="forbid". Fields: finish_reason (str | None = None), model_extra (dict[str, Any] | None = None).</action>
    <action>In @[backend_v2/models/llm.py], refactor LLMResponse to replace messages: list[dict[str, Any]] | None with list[LLMMessageDTO] | None, tool_calls: list[dict[str, Any]] | None with list[OpenAIToolCallDTO] | None, and provider_metadata with ProviderMetadataDTO.</action>
    <action>In @[backend_v2/models/prompt.py], define PromptMetadataDTO with frozen=True, strict=True, extra="forbid". Fields: token_proxy_score (float | None = None), cache_key (str | None = None), routing_tags (list[str] | None = None).</action>
    <action>In @[backend_v2/models/prompt.py], refactor CompiledPrompt to use list[LLMMessageDTO] for static_messages and dynamic_messages, and PromptMetadataDTO for metadata.</action>
    <demolish>
      REMOVE: msg.get("role") in CompiledPrompt._forbid_system_in_dynamic and _merge_flat in @[backend_v2/models/prompt.py#L47-L80].
      REPLACE WITH: direct msg.role and msg.content attribute access.
    </demolish>
    <action>Update CompiledPrompt._merge_flat, to_static_flat, to_dynamic_flat, to_flat_messages to operate directly on LLMMessageDTO instances returning list[LLMMessageDTO].</action>
  </step>

  <step id="2" name="UPDATE CACHING SERVICE & UTILS">
    <action>In @[backend_v2/llm/caching_service.py], update _run_purity_scanner to accept messages: list[LLMMessageDTO] with direct msg.role and msg.content attribute access.</action>
    <action>In @[backend_v2/utils/math_utils.py], add model_config = ConfigDict(strict=True, extra="forbid", frozen=True) to StrictnessConfig.</action>
  </step>

  <step id="3" name="CENTRAL TEST FACTORIES & TEST MIGRATION">
    <action>In @[backend_v2/tests/conftest.py], implement make_llm_message(role: str, content: str, **kwargs) -> LLMMessageDTO locking roles to "system" | "user" | "assistant" | "tool".</action>
    <action>In @[backend_v2/tests/unit/models/test_prompt.py], migrate all raw dict prompt constructor calls to LLMMessageDTO and replace flat[n]["role"] subscript indexing with flat[n].role.</action>
    <action>In @[backend_v2/tests/unit/llm/test_caching_service.py], migrate message fixtures to LLMMessageDTO.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_llm_message_dto_missing_required_field">
      <input>LLMMessageDTO(content="text") without role</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_llm_message_dto_extra_field_forbidden">
      <input>LLMMessageDTO(role="user", content="text", invalid_extra="value")</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
    <contract id="3" name="test_llm_message_dto_strict_types">
      <input>LLMMessageDTO(role=123, content="text")</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>boundary</category>
    </contract>
    <contract id="4" name="test_llm_message_dto_serialization_null_omission">
      <input>LLMMessageDTO(role="user", content="hello").model_dump(mode="json", exclude_none=True)</input>
      <expected>returns {"role": "user", "content": "hello"} with zero None keys</expected>
      <category>positive</category>
    </contract>
    <contract id="5" name="test_compiled_prompt_merge_flat_roles">
      <input>CompiledPrompt with consecutive user messages</input>
      <expected>returns list[LLMMessageDTO] merged correctly</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 1A targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/models/prompt.py backend_v2/models/llm.py backend_v2/llm/caching_service.py backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/test_caching_service.py --test</command>
  </validation_gate>
</execution_protocol>
