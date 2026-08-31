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

## 5-Column Architectural Directive Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`LLMMessageDTO` & `ProviderMetadataDTO`** `@[backend_v2/models/llm.py#L24-L50]` | Banned naked `dict[str, Any]` in `LLMResponse.messages`, `tool_calls`, and `provider_metadata`. Zero untyped message state transit. | `ConfigDict(strict=True, extra="forbid", frozen=True)`. Strict `role`, `content`, `tool_calls: list[OpenAIToolCallDTO] \| None`, `ProviderMetadataDTO`. | Pruned generic message interfaces and runtime reflection proxies. Plain typed Pydantic V2 DTO. | `test_llm_message_dto_missing_required_field` + `test_llm_message_dto_extra_field_forbidden` raising `ValidationError`. |
| **`PromptMetadataDTO` & `CompiledPrompt`** `@[backend_v2/models/prompt.py#L32-L136]` | Banned `msg.get("role")`, `msg.get("content")`, and loose `dict` messages in `static_messages` / `dynamic_messages`. | Pure `list[LLMMessageDTO]`, direct attribute access (`msg.role`, `msg.content`), `PromptMetadataDTO` metadata, immutable `.model_copy(update=...)` in `_merge_flat`. | Pruned custom message iterator wrappers and dynamic string schema validators. | `test_compiled_prompt_merge_flat_roles` + `test_compiled_prompt_forbids_system_in_dynamic` raising `AppException` (400). |
| **`LLMCachingService` Purity Scanner** `@[backend_v2/llm/caching_service.py#L68-L90]` | Banned `"role" in msg and msg["role"] == "system"` dictionary subscript inspection. | Direct `msg.role == "system"` and `msg.content` attribute inspection on `list[LLMMessageDTO]`. | Pruned dynamic parsing and heavy regex over non-system messages. | `test_purity_scanner_detects_violations` verifying log warning on dynamic UUID/timestamp. |
| **`StrictnessConfig` Math Model** `@[backend_v2/utils/math_utils.py#L19-L45]` | Banned loose `model_config = ConfigDict(frozen=True)` without `strict=True, extra="forbid"`. | Strict `ConfigDict(strict=True, extra="forbid", frozen=True)` with PEP 593 `Annotated` on all fields. | Pruned dynamic dictionary converters and custom float wrapper classes. | `backend_audit_loop.py` strict AST and Pydantic validation gates. |
| **Central Test Fixtures & Unit Tests** `@[backend_v2/tests/conftest.py]` | Banned ad-hoc dictionary fixtures `{"role": "user", "content": "..."}` and subscript indexing `flat[n]["role"]`. | `make_llm_message()` helper with `Literal["system", "user", "assistant", "tool"]` and dot-notation `flat[n].role` test assertions. | Pruned brittle mock dict fixtures across unit tests. | `uv run python scripts/backend_audit_loop.py backend_v2/models/prompt.py backend_v2/models/llm.py backend_v2/llm/caching_service.py backend_v2/utils/math_utils.py backend_v2/tests/unit/models/test_prompt.py backend_v2/tests/unit/llm/test_caching_service.py --test` |

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
          role: Annotated[str, Field(min_length=1, description="Message role ('system', 'user', 'assistant', 'tool').")]
          content: Annotated[str, Field(description="Message text payload.")]
          tool_calls: Annotated[list[OpenAIToolCallDTO] | None, Field(default=None, description="Optional tool calls invoked.")] = None
          tool_call_id: Annotated[str | None, Field(default=None, description="Optional tool call ID for tool outputs.")] = None
          name: Annotated[str | None, Field(default=None, description="Optional name identifier for tool messages.")] = None
    </interface>
    <interface id="PromptMetadataDTO">
      class PromptMetadataDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          token_proxy_score: Annotated[float | None, Field(default=None, description="Token proxy score for cache evaluation.")] = None
          cache_key: Annotated[str | None, Field(default=None, description="Deterministic cache identifier.")] = None
          routing_tags: Annotated[list[str] | None, Field(default=None, description="Routing or tier tags.")] = None
    </interface>
    <interface id="ProviderMetadataDTO">
      class ProviderMetadataDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          finish_reason: Annotated[str | None, Field(default=None, description="Provider termination reason.")] = None
          model_extra: Annotated[dict[str, Any] | None, Field(default=None, description="Provider-specific raw metadata.")] = None
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

  <step id="0" name="STRATEGIC ALIGNMENT CHECK & PRE-IMPLEMENTATION CLEANUPS">
    <action>Verify codebase baseline for @[backend_v2/models/prompt.py#L32-L136] and @[backend_v2/models/llm.py#L24-L50].</action>
    <action>Verify OpenAIToolCallDTO SSOT availability from @[backend_v2/models/domain/mcp.py#L30-L46].</action>
    <action>Pre-Implementation Cleanup: In @[backend_v2/utils/math_utils.py#L19-L45], harden StrictnessConfig to enforce model_config = ConfigDict(strict=True, extra="forbid", frozen=True) and ensure all fields use PEP 593 Annotated syntax.</action>
  </step>

  <step id="1" name="DEFINE DTO MODELS IN LLM & PROMPT MODULES">
    <action>In @[backend_v2/models/llm.py#L24-L50], define LLMMessageDTO with frozen=True, strict=True, extra="forbid". Fields: role (Annotated[str, Field(min_length=1)]), content (Annotated[str, Field()]), tool_calls (Annotated[list[OpenAIToolCallDTO] | None, Field(default=None)]), tool_call_id (Annotated[str | None, Field(default=None)]), name (Annotated[str | None, Field(default=None)]).</action>
    <action>In @[backend_v2/models/llm.py#L53-L66], define ProviderMetadataDTO(BaseModel) with frozen=True, strict=True, extra="forbid". Fields: finish_reason (Annotated[str | None, Field(default=None)]), model_extra (Annotated[dict[str, Any] | None, Field(default=None)]).</action>
    <action>In @[backend_v2/models/llm.py#L69-L148], refactor LLMResponse to replace messages: list[dict[str, Any]] | None with list[LLMMessageDTO] | None, tool_calls: list[dict[str, Any]] | None with list[OpenAIToolCallDTO] | None, and provider_metadata: dict[str, Any] with ProviderMetadataDTO.</action>
    <action>In @[backend_v2/models/prompt.py#L14-L29], define PromptMetadataDTO with frozen=True, strict=True, extra="forbid". Fields: token_proxy_score (Annotated[float | None, Field(default=None)]), cache_key (Annotated[str | None, Field(default=None)]), routing_tags (Annotated[list[str] | None, Field(default=None)]).</action>
    <action>In @[backend_v2/models/prompt.py#L32-L136], refactor CompiledPrompt to use list[LLMMessageDTO] for static_messages and dynamic_messages, and PromptMetadataDTO for metadata (default_factory=PromptMetadataDTO).</action>
    <demolish>
      REMOVE: msg.get("role") and msg.get("content") dictionary access in CompiledPrompt._forbid_system_in_dynamic @[backend_v2/models/prompt.py#L62-L84] and _merge_flat @[backend_v2/models/prompt.py#L86-L109].
      REPLACE WITH: direct msg.role and msg.content attribute access, and immutable .model_copy(update={"content": merged_content}) for merged message construction.
    </demolish>
    <action>Update CompiledPrompt._merge_flat, to_static_flat, to_dynamic_flat, to_flat_messages to operate directly on LLMMessageDTO instances returning list[LLMMessageDTO].</action>
  </step>

  <step id="2" name="UPDATE CACHING SERVICE & UTILS">
    <action>In @[backend_v2/llm/caching_service.py#L68-L90], update _run_purity_scanner to accept messages: list[LLMMessageDTO] with direct msg.role == "system" and msg.content attribute access.</action>
  </step>

  <step id="3" name="CENTRAL TEST FACTORIES & TEST MIGRATION">
    <action>In @[backend_v2/tests/conftest.py], implement make_llm_message(role: Literal["system", "user", "assistant", "tool"], content: str, tool_calls: list[OpenAIToolCallDTO] | None = None, tool_call_id: str | None = None, name: str | None = None) -> LLMMessageDTO.</action>
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
