<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 2: Base Contract, LogfireShieldedClient, MockProvider & LLMFactory Extraction (`phase2_base_mock_and_factory_extraction.md`)

## 1. Objective
Execute Phase 2 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/llm/provider.py]`:
1. Extract `LLMProvider` (`@[backend_v2/llm/provider.py#L459-L511]`), `LogfireShieldedClient` (`@[backend_v2/llm/provider.py#L514-L544]`), and `MockProvider` (`@[backend_v2/llm/provider.py#L1437-L1653]`) into `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (`< 340` lines).
2. Extract `LLMFactory` (`@[backend_v2/llm/provider.py#L1656-L1846]`, `create_provider` `#L1659-L1846`) into `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (`< 240` lines), resolving `get_settings`, `LiteLLMProvider`, and `MockProvider` dynamically from `sys.modules["backend_v2.llm.provider"]` when present so facade-level test patches (`patch("backend_v2.llm.provider.get_settings")`, `patch("backend_v2.llm.provider.LiteLLMProvider")`, `patch("backend_v2.llm.provider.MockLLMService")`) intercept transparently.
3. Update `@[backend_v2/llm/provider.py]` to re-export `LLMProvider`, `LogfireShieldedClient`, `MockProvider`, and `LLMFactory` using explicit redundant aliases, and create dedicated unit tests in `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` | Abstract `LLMProvider` contract, `LogfireShieldedClient` HTTPX wrapper, and `MockProvider` deterministic offline provider (`< 340` lines) |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/provider_factory.py]` | `LLMFactory.create_provider` resolving provider credentials, Vertex AI / AI Studio / OpenAI / Anthropic / DeepSeek / Mock parameters, and instantiating `LiteLLMProvider` or `MockProvider` (`< 240` lines) |
| `[MODIFY]` | `@[backend_v2/llm/provider.py]` | Replace `LLMProvider` (`@[backend_v2/llm/provider.py#L459-L511]`), `LogfireShieldedClient` (`@[backend_v2/llm/provider.py#L514-L544]`), `MockProvider` (`@[backend_v2/llm/provider.py#L1437-L1653]`), and `LLMFactory` (`@[backend_v2/llm/provider.py#L1656-L1846]`) with explicit redundant re-exports (`Symbol as Symbol`) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]` | Unit tests for `LLMProvider`, `LogfireShieldedClient`, and `MockProvider` lifecycle, `mock_identity` forwarding, and OpenTelemetry span attributes |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]` | Unit tests for `LLMFactory.create_provider` across Mock, Vertex AI, AI Studio, OpenAI, Anthropic, DeepSeek, and missing credential Fail-Fast errors |

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
  <step id="1" name="Create Base & Mock Provider and Provider Factory Sub-Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/llm/provider/__init__.py during Phase 2 while backend_v2/llm/provider.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither base_and_mock_provider.py nor provider_factory.py may import statically from backend_v2.llm.provider at module level, and both MUST remain under 350 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` (`< 340` lines, all lines `<= 120` chars) with `__all__ = ["LLMProvider", "LogfireShieldedClient", "MockProvider"]`:
         - Relocate `LLMProvider` verbatim from `@[backend_v2/llm/provider.py#L459-L511]`.
         - Relocate `LogfireShieldedClient` verbatim from `@[backend_v2/llm/provider.py#L514-L544]`.
         - Relocate `MockProvider` (`@[backend_v2/llm/provider.py#L1437-L1653]`), importing `_safe_static_getattr` and `_sync_diagnostic_dump` from `backend_v2.llm.provider.env_and_schema_utils` and resolving `get_settings` and `MockLLMService` via `sys.modules["backend_v2.llm.provider"]` when `"backend_v2.llm.provider" in sys.modules` so existing test patches on `backend_v2.llm.provider.get_settings` and `backend_v2.llm.provider.MockLLMService` intercept transparently.
      2. Create `[NEW] @[backend_v2/llm/provider/provider_factory.py]` (`< 240` lines, all lines `<= 120` chars) with `__all__ = ["LLMFactory"]`:
         - Relocate `LLMFactory` (`@[backend_v2/llm/provider.py#L1656-L1846]`, `create_provider` `#L1659-L1846`), importing `LLMProvider` and `MockProvider` from `backend_v2.llm.provider.base_and_mock_provider` and resolving `get_settings`, `LiteLLMProvider`, and `MockProvider` via `sys.modules["backend_v2.llm.provider"]` when `"backend_v2.llm.provider" in sys.modules` so existing test patches on `backend_v2.llm.provider.get_settings` and `backend_v2.llm.provider.LiteLLMProvider` intercept transparently.
    </action>
  </step>

  <step id="2" name="Rewire Re-Exports in provider.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/llm/provider.py.</constraint>
    <action>
      1. Update `@[backend_v2/llm/provider.py]` (`@[backend_v2/llm/provider.py#L459-L511]`, `@[backend_v2/llm/provider.py#L514-L544]`, `@[backend_v2/llm/provider.py#L1437-L1653]`, and `@[backend_v2/llm/provider.py#L1656-L1846]`) to import `LLMProvider`, `LogfireShieldedClient`, and `MockProvider` from `backend_v2.llm.provider.base_and_mock_provider` and `LLMFactory` from `backend_v2.llm.provider.provider_factory` using explicit redundant aliases (`Symbol as Symbol`).
      2. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_base_and_mock_provider.py]` testing `LogfireShieldedClient` async context manager delegation and `MockProvider` generation (`mock_identity` consumption, structured schema validation, and diagnostic dump).
      3. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_provider_factory.py]` testing `LLMFactory.create_provider` across Mock, Vertex AI, AI Studio, OpenAI, Anthropic, and missing API key `ConfigurationError` paths.
    </action>
  </step>

  <step id="3" name="Run Phase 2 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules and backend_v2/llm/provider.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/base_and_mock_provider.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/provider_factory.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict` to verify all 34 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_mock_provider_consumes_mock_identity_directly">
      Verifies that MockProvider forwards mock_identity to MockLLMService.get_mock_response and strips internal keys identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_logfire_shielded_client_delegates_async_context_and_attributes">
      Verifies that LogfireShieldedClient wraps httpx.AsyncClient, delegates aenter/aexit, and shields transport attributes.
    </contract>
    <contract type="negative" name="test_llm_factory_create_provider_missing_api_key_raises_configuration_error">
      Verifies that LLMFactory.create_provider logs an RFC 7807 error and raises ConfigurationError when required provider API keys are missing.
    </contract>
  </test_contracts>
</execution_protocol>
```
