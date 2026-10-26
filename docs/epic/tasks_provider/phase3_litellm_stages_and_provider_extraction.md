<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 3: LiteLLM Response/Telemetry Stage & LiteLLMProvider Extraction (`phase3_litellm_stages_and_provider_extraction.md`)

## 1. Objective
Execute Phase 3 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/llm/provider.py#L547-L1434]`:
1. Extract the response parsing, `TokenUsage` & cost computation, OpenTelemetry GenAI semantic span attribute recording, diagnostic prompt dumping, and post-retry RFC 7807 exception classification stage of `LiteLLMProvider.generate` (`@[backend_v2/llm/provider.py#L688-L1434]`, lines 820–829 and 1020–1434) into `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (`< 380` lines) defining `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error`.
2. Extract `LiteLLMProvider` (`@[backend_v2/llm/provider.py#L547-L1434]`: `__init__` `#L558-L686` and `generate` `#L688-L1434` orchestrating request parameter preparation, MCP tool schema normalization, OpenTelemetry span creation, Tenacity `AsyncRetrying` loop with `_AdaptiveWaitWithRetryAfter` and `apply_provider_pacing`, and delegation to `extract_litellm_content_and_usage` and `classify_and_raise_litellm_error`) into `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (`< 430` lines).
3. Update `@[backend_v2/llm/provider.py#L547-L1434]` to re-export `LiteLLMProvider`, `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error` with explicit redundant aliases, shrinking `backend_v2/llm/provider.py` to a thin proxy (`< 160` lines), and create unit tests in `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]` and `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` | `_truncate_for_debug`, `extract_litellm_content_and_usage` (choice/tool-call extraction, `TokenUsage`, `litellm.completion_cost` & adapter `PricingConfig` calculation, OpenTelemetry GenAI attributes, diagnostic dump), and `classify_and_raise_litellm_error` (RFC 7807 error mapping) (`< 380` lines) |
| `[NEW]` | `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` | `LiteLLMProvider` (`__init__` for adapter resolution, dynamic RPM semaphore, `LogfireShieldedClient`, `litellm.Router`; and `generate` orchestrating request preparation, Tenacity retry loop, and response/error stage delegation) (`< 430` lines) |
| `[MODIFY]` | `@[backend_v2/llm/provider.py#L547-L1434]` | Replace `LiteLLMProvider` (`#L547-L1434`) with explicit redundant re-exports from `litellm_response_stage.py` and `litellm_provider.py`, reducing `provider.py` to `< 160` lines |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]` | Unit tests for `_truncate_for_debug`, `extract_litellm_content_and_usage`, and `classify_and_raise_litellm_error` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]` | Unit tests for `LiteLLMProvider.__init__` and `LiteLLMProvider.generate` covering tool calls, penalties, HTTPX client wrapping, adaptive `Retry-After`, and telemetry |

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
  <step id="1" name="Create LiteLLM Response Stage and LiteLLMProvider Sub-Modules">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/llm/provider/__init__.py during Phase 3 while backend_v2/llm/provider.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Neither litellm_response_stage.py nor litellm_provider.py may exceed 430 lines, and all lines MUST be <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (`< 380` lines, all lines `<= 120` chars) with `__all__ = ["_truncate_for_debug", "classify_and_raise_litellm_error", "extract_litellm_content_and_usage"]`:
         - Hoist `_truncate_for_debug` from `@[backend_v2/llm/provider.py#L820-L829]`.
         - Implement `extract_litellm_content_and_usage(...) -> tuple[str, TokenUsage]` encapsulating lines 1020–1311 of `LiteLLMProvider.generate` (`@[backend_v2/llm/provider.py#L688-L1434]`: choice message & `tool_calls` extraction, empty response guard, `TokenUsage` & reasoning/cached token extraction, `litellm.completion_cost` & adapter `PricingConfig` fallback calculation, OpenTelemetry GenAI semantic span attribute recording, and `DUMP_PROMPTS_FILE` diagnostic dump).
         - Implement `classify_and_raise_litellm_error(...) -> Never` encapsulating lines 1312–1434 of `LiteLLMProvider.generate` (`@[backend_v2/llm/provider.py#L688-L1434]`: `InstructorRetryException` / `__cause__` unwrapping, OpenTelemetry span error status recording, and RFC 7807 `ContextWindowExceededError`, `UpstreamAuthenticationError`, `UpstreamRateLimitError`, `UpstreamTimeoutError`, `ContentPolicyViolationError`, `BadRequestError`, and `UpstreamServiceError` raising).
      2. Create `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (`< 430` lines, all lines `<= 120` chars) with `__all__ = ["LiteLLMProvider"]`:
         - Relocate `LiteLLMProvider` (`@[backend_v2/llm/provider.py#L547-L1434]`: `__init__` `#L558-L686` and `generate` `#L688-L1434`), delegating response extraction to `extract_litellm_content_and_usage` and post-retry exception classification to `classify_and_raise_litellm_error`.
         - Resolve `apply_provider_pacing`, `get_settings`, and `otel_trace` via `sys.modules["backend_v2.llm.provider"]` when `"backend_v2.llm.provider" in sys.modules` so existing test `monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", ...)` and `monkeypatch.setattr("backend_v2.llm.provider.get_settings", ...)` calls intercept transparently.
    </action>
  </step>

  <step id="2" name="Rewire Re-Exports in provider.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/llm/provider.py.</constraint>
    <action>
      1. Update `@[backend_v2/llm/provider.py#L547-L1434]` to replace `LiteLLMProvider` with explicit redundant re-exports from `backend_v2.llm.provider.litellm_response_stage` and `backend_v2.llm.provider.litellm_provider`, shrinking `backend_v2/llm/provider.py` to `< 160` lines.
      2. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_response_stage.py]` testing `_truncate_for_debug`, `extract_litellm_content_and_usage` (text content, tool calls, cached/reasoning tokens, cost calculation), and `classify_and_raise_litellm_error` (401/403 auth, 429 rate limit, 408/504 timeout, context window, content policy, 400 bad request, and generic 500 upstream errors).
      3. Create `[NEW] @[backend_v2/tests/unit/llm/provider/test_litellm_provider.py]` testing `LiteLLMProvider.__init__` and `LiteLLMProvider.generate` (dynamic RPM semaphore sizing, internal key stripping, MCP tool schema serialization, and adaptive `Retry-After` retry loop).
    </action>
  </step>

  <step id="3" name="Run Phase 3 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on both new sub-modules and backend_v2/llm/provider.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/litellm_response_stage.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider/litellm_provider.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/llm/provider.py --test --ast-strict` to verify all 34 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_litellm_provider_generate_full_telemetry_and_toolcalls">
      Verifies that LiteLLMProvider.generate and extract_litellm_content_and_usage extract content/tool_calls, calculate TokenUsage and cost_usd, and record OpenTelemetry GenAI attributes identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_lite_llm_provider_strips_internal_keys_and_normalizes_mcp_tools">
      Verifies that LiteLLMProvider.generate strips _INTERNAL_NON_API_KEYS and normalizes MCP tool declarations to standard JSON schema before invoking router.acompletion.
    </contract>
    <contract type="negative" name="test_classify_and_raise_litellm_error_maps_upstream_exceptions">
      Verifies that classify_and_raise_litellm_error maps ContextWindowExceededError, UpstreamAuthenticationError, UpstreamRateLimitError, UpstreamTimeoutError, ContentPolicyViolationError, and BadRequestError deterministically.
    </contract>
  </test_contracts>
</execution_protocol>
```
