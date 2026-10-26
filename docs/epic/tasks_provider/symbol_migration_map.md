<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Symbol & Blast-Radius Migration Map: `backend_v2/llm/provider.py`

## 1. Executive Summary & Monolith Archetype Profile
- **Source Monolith**: `[DELETE] @[backend_v2/llm/provider.py]` (1,846 lines, 6 classes, 8 module-level functions, 2 nested closures in `LiteLLMProvider.generate`, 2 module constants).
- **Target Domain Package**: `backend_v2/llm/provider/` (`< 430` lines per sub-module, `< 160` lines for `__init__.py` facade).
- **Monolith Archetype**: **Archetype C / D Hybrid — External LLM Anti-Corruption Layer (ACL) & Micro-Concurrency Core** (`LiteLLMProvider.generate` spans 747 lines `#L688-L1434`, managing dynamic RPM semaphores, Tenacity adaptive `Retry-After` loops, LiteLLM SDK ACL extraction, and OpenTelemetry GenAI semantic telemetry).
- **Test Baseline (`[BASELINE]`)**: 34 passing unit tests (`test_provider.py`, `test_provider_httpx_client.py`, `test_provider_penalties.py`, `test_provider_retry_after.py`, `test_provider_telemetry.py`, `test_provider_toolcalls.py`), **92% line coverage** (`785` statements, `66` missed). Exceeds the 75% minimum coverage gate (`Phase 0` skipped).
- **Invariant Set ($\mathcal{I}_{orig}$)**:
  1. **Two-Tier Concurrency & Dynamic RPM Semaphore SSOT**: `LiteLLMProvider.__init__` (`@[backend_v2/llm/provider.py#L558-L686]`) computes `max_concurrent` strictly from `get_settings()` (`semaphore_low_rpm_threshold`, `semaphore_low_rpm_limit`, `semaphore_max_concurrency`, `semaphore_rpm_divisor`) and bounds concurrent provider calls via `self._semaphore = asyncio.Semaphore(max_concurrent)`.
  2. **Adaptive Retry-After & Provider Pacing Invariant**: `LiteLLMProvider.generate` (`@[backend_v2/llm/provider.py#L688-L1434]`) executes `apply_provider_pacing` before each `router.acompletion` attempt inside `AsyncRetrying` governed by `_AdaptiveWaitWithRetryAfter` (`@[backend_v2/llm/provider.py#L401-L444]`) and `_is_transient_llm_error` (`@[backend_v2/llm/provider.py#L182-L320]`).
  3. **RFC 7807 Dual-Reporting & DLP Parity**: Every post-retry exception in `LiteLLMProvider.generate` (`@[backend_v2/llm/provider.py#L688-L1434]`) and `LLMFactory.create_provider` (`@[backend_v2/llm/provider.py#L1659-L1846]`) logs structured error codes (`ErrorCodes`) without leaking API keys or raw user prompts before raising `ContextWindowExceededError`, `UpstreamAuthenticationError`, `UpstreamRateLimitError`, `UpstreamTimeoutError`, `ContentPolicyViolationError`, `BadRequestError`, `UpstreamServiceError`, or `ConfigurationError`.
  4. **OpenTelemetry GenAI Semantic Span Parity**: `tracer.start_as_current_span` records `gen_ai.system`, `gen_ai.request.model`, `gen_ai.response.model`, `gen_ai.usage.input_tokens`, `gen_ai.usage.output_tokens`, `gen_ai.usage.total_tokens`, `gen_ai.usage.cost_usd`, and `gen_ai.cache.hit` without serializing raw user prompts when `settings.environment != "development"`.

---

## 2. AST Symbol-to-Target Module Mapping

| Symbol Name | AST Kind & Source Line Bounds | Target Module (Epoch 1) | Visibility / Export Facade |
| :--- | :--- | :--- | :--- |
| `_safe_static_getattr` | `def` (`@[backend_v2/llm/provider.py#L64-L83]`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_safe_static_hasattr` | `def` (`@[backend_v2/llm/provider.py#L86-L99]`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_INTERNAL_NON_API_KEYS` | Module `frozenset[str]` (`#L101-L105`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `resolve_env_variables` | `def` (`@[backend_v2/llm/provider.py#L108-L132]`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_normalize_mcp_tool_schema_for_llm` | `def` (`@[backend_v2/llm/provider.py#L135-L159]`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_sync_diagnostic_dump` | `def` (`@[backend_v2/llm/provider.py#L162-L179]`) | `[NEW] @[backend_v2/llm/provider/env_and_schema_utils.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_is_transient_llm_error` | `def` (`@[backend_v2/llm/provider.py#L182-L320]`) | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_RETRY_AFTER_REGEX` | Module `re.Pattern[str]` (`#L322-L323`) | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_extract_retry_after_seconds` | `def` (`@[backend_v2/llm/provider.py#L326-L398]`) | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_AdaptiveWaitWithRetryAfter` | `class _AdaptiveWaitWithRetryAfter(wait_base)` (`@[backend_v2/llm/provider.py#L401-L444]`) | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `_format_attempt_error` | `def` (`@[backend_v2/llm/provider.py#L447-L453]`) | `[NEW] @[backend_v2/llm/provider/transient_retry_policy.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `LLMProvider` | `class LLMProvider(ABC)` (`@[backend_v2/llm/provider.py#L459-L511]`) | `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `LogfireShieldedClient` | `class LogfireShieldedClient` (`@[backend_v2/llm/provider.py#L514-L544]`) | `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `MockProvider` | `class MockProvider(LLMProvider)` (`@[backend_v2/llm/provider.py#L1437-L1653]`) | `[NEW] @[backend_v2/llm/provider/base_and_mock_provider.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `LLMFactory` | `class LLMFactory` (`@[backend_v2/llm/provider.py#L1656-L1846]`) | `[NEW] @[backend_v2/llm/provider/provider_factory.py]` | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `LiteLLMProvider.generate` — Response, Telemetry & Error Classification Stage (`_truncate_for_debug`, choice/tool-call extraction, `TokenUsage` & cost computation, OpenTelemetry span attributes, RFC 7807 error mapping) | Nested `def _truncate_for_debug` (`@[backend_v2/llm/provider.py#L820-L829]`) and Stage 2 of `@override async def generate` (`@[backend_v2/llm/provider.py#L688-L1434]`, lines 1020–1434) | `[NEW] @[backend_v2/llm/provider/litellm_response_stage.py]` (`_truncate_for_debug`, `extract_litellm_content_and_usage`, `classify_and_raise_litellm_error`) | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |
| `LiteLLMProvider` (`__init__`, `_execute_paced_completion`, and `generate`) | `class LiteLLMProvider(LLMProvider)` (`@[backend_v2/llm/provider.py#L547-L1434]`) | `[NEW] @[backend_v2/llm/provider/litellm_provider.py]` (`< 430` lines) | Re-exported in `[NEW] @[backend_v2/llm/provider/__init__.py]` |

---

## 3. 1-Hop Caller Blast-Radius Inventory (Epoch 1 Phase 4 Cutover)

| Caller Category | File Path & AST Boundaries | Current Import / Reference | Target Rewired Import / Reference |
| :--- | :--- | :--- | :--- |
| Production LLM Client | `@[backend_v2/llm/client.py#L46-L58]` | `from backend_v2.llm.provider import LLMFactory` (line 24) | `from backend_v2.llm.provider.provider_factory import LLMFactory` |
| Production LLM Handler | `@[backend_v2/llm/handler.py#L878-L1057]` | `from backend_v2.llm.provider import LLMFactory, LLMProvider` (line 21) | `from backend_v2.llm.provider.base_and_mock_provider import LLMProvider` and `from backend_v2.llm.provider.provider_factory import LLMFactory` |
| Production Generic MCP Client | `@[backend_v2/services/mcp/generic_mcp_client.py#L447-L509]` | `from backend_v2.llm.provider import _is_transient_llm_error` (line 24) | `from backend_v2.llm.provider.transient_retry_policy import _is_transient_llm_error` |
| Production Orchestrator Consumers (Protected by `orchestrator_god_object_fragility`) | `@[backend_v2/services/orchestrator/dag_executor.py#L400-L597]`, `@[backend_v2/services/orchestrator/enriched_dag_executor.py#L50-L214]`, `@[backend_v2/services/orchestrator/extractive_sensor_service.py#L589-L734]` | `from backend_v2.llm.provider import _is_transient_llm_error` | Resolved directly via package facade `[NEW] @[backend_v2/llm/provider/__init__.py]` with zero mutations to `backend_v2/services/orchestrator/` |
| Monolithic Unit Test Suite (Split in Phase 4) | `[DELETE] @[backend_v2/tests/unit/llm/test_provider.py]` (1,153 lines, 16 tests) | `from backend_v2.llm.provider import ...` | Split into modular test suites under `backend_v2/tests/unit/llm/provider/` (`test_env_and_schema_utils.py`, `test_transient_retry_policy.py`, `test_base_and_mock_provider.py`, `test_provider_factory.py`, `test_litellm_response_stage.py`, `test_litellm_provider.py`, `test_provider_facade.py`) |
| Provider Sibling Unit Tests | `@[backend_v2/tests/unit/llm/test_provider_httpx_client.py#L34-L99]`, `@[backend_v2/tests/unit/llm/test_provider_penalties.py#L14-L76]`, `@[backend_v2/tests/unit/llm/test_provider_retry_after.py#L49-L90]`, `@[backend_v2/tests/unit/llm/test_provider_toolcalls.py#L11-L89]` | `from backend_v2.llm.provider import ...` | Rewired to import from `backend_v2.llm.provider` package submodules and facade |
| AST Guardrail Script & Tests | `@[scripts/_ast_guardrails.py#L98-L107]`, `@[scripts/_ast_guardrails.py#L619-L678]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1146-L1180]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2065-L2075]` | `"backend_v2/llm/provider.py"` in `BOUNDARY_EXEMPTION_FILES` | Extend `is_boundary_exempt` to cover `backend_v2/llm/provider/`, update `BOUNDARY_EXEMPTION_FILES` to `"backend_v2/llm/provider/__init__.py"`, and lock `"backend_v2/llm/provider.py"` under `QGR017` in `visit_Module` |
