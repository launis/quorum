# Vertex AI & AI Studio Context Cache Hardening, SSOT Infrastructure & Fail-Soft Log Harmonization

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <rule>@[c:\Users\risto\.gemini\antigravity-ide\knowledge\god_code_prevention\artifacts\ki_god_code_prevention.md]</rule>
  <knowledge_item>@[ki_global_document_cache.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Objective
Harmonize the context caching SSOT architecture across Model Registry (`ModelProfile`), Settings (`Settings`), and Provider Adapters (`BaseLLMAdapter`, `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter`). Eliminate hardcoded platform token limits and noisy `logger.error(..., exc_info=True)` stack traces, replacing them with centralized SSOT settings, a shared DRY `calculate_contents_tokens` helper, and concise `logger.warning(...)` Fail-Soft notifications.

---

## Target Scope & Boundaries

### Target Files (Read/Write)
- `[MODIFY]` @[backend_v2/settings.py#L51-L723]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py#L129-L362]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py#L72-L502]
- `[MODIFY]` @[backend_v2/llm/adapters/ai_studio_adapter.py#L72-L377]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L619-L645]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L77-L94]

### Context Files (Read-Only)
- `[READ_ONLY]` @[backend_v2/models/v2_core.py#L351-L377]
- `[READ_ONLY]` @[backend_v2/llm/client.py#L34-L698]
- `[READ_ONLY]` @[backend_v2/llm/caching_service.py#L14-L118]

---

## Architecture & SSOT Alignment

| Domain Layer | Responsibility | SSOT Location |
| :--- | :--- | :--- |
| **Model Registry** | Strategic user intent (`caching_strategy: "prompt_caching" \| "none"`) per model profile. | `ModelProfile` (`models/v2_core.py`) |
| **System Settings** | Platform infrastructure constraints (`context_cache_min_tokens_vertex = 1024`, `context_cache_min_tokens_ai_studio = 32768`, `context_cache_failed_ttl_seconds = 300`). | `Settings` (`backend_v2/settings.py`) |
| **Base Adapter** | Reusable DRY token estimation for conversational `contents` turns (`calculate_contents_tokens`). | `BaseLLMAdapter` (`base_adapter.py`) |
| **Concrete Adapters** | Platform-specific GAPIC cache generation, Redis distributed locking, and Fail-Soft execution. | `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter` |

---

## Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="SSOT_SETTINGS_AND_BASE_ADAPTER_EXPANSION">
    <step id="1.1" name="ADD_SSOT_SETTINGS_FIELDS">
      <action>Modify @[backend_v2/settings.py#L51-L723]:</action>
      <action>1. Add `context_cache_min_tokens_vertex: Annotated[int, Field(description="Minimum non-system content tokens required by Vertex AI Context Caching")] = 1024`.</action>
      <action>2. Add `context_cache_min_tokens_ai_studio: Annotated[int, Field(description="Minimum non-system content tokens required by Google AI Studio Context Caching")] = 32768`.</action>
      <action>3. Add `context_cache_failed_ttl_seconds: Annotated[int, Field(description="TTL in seconds for marking context cache state as FAILED in Redis")] = 300`.</action>
      <constraint invariant="pydantic_annotated_fields_mandate">All fields must use PEP 593 Annotated[int, Field(...)] syntax.</constraint>
    </step>

    <step id="1.2" name="IMPLEMENT_SHARED_CONTENTS_TOKEN_ESTIMATOR">
      <action>Modify @[backend_v2/llm/adapters/base_adapter.py#L129-L362]:</action>
      <action>Add method `calculate_contents_tokens(self, contents: list[dict[str, Any]]) -> int` to `BaseLLMAdapter` to compute character total across all parts in non-system turns divided by 4.</action>
      <constraint invariant="pep257_google_style_docstrings">Full PEP 257 docstring with Args and Returns.</constraint>
      <constraint invariant="strict_pydantic_v2_rust">Ensure type-safe traversal without naked dict assumptions.</constraint>
    </step>
  </phase>

  <phase id="2" name="GATE_ENFORCEMENT_AND_LOG_HARMONIZATION">
    <step id="2.1" name="HARDEN_VERTEX_ADAPTER">
      <action>Modify @[backend_v2/llm/adapters/vertex_adapter.py#L72-L502]:</action>
      <action>1. Replace raw 1024 token threshold with `get_settings().context_cache_min_tokens_vertex`.</action>
      <action>2. In `prepare_caching_payload`, after assembling `vertex_contents`, call `estimated_tokens = self.calculate_contents_tokens(vertex_contents)`.</action>
      <action>3. If `estimated_tokens &lt; get_settings().context_cache_min_tokens_vertex` or `not vertex_contents`, bypass cache creation with `logger.info("Vertex AI caching bypassed: Static conversational contents (%d tokens) below GCP explicit cache minimum (%d tokens).", estimated_tokens, get_settings().context_cache_min_tokens_vertex)`, release lock, and return `compiled_prompt.to_flat_messages(), {}`.</action>
      <action>4. In `except Exception as exc:` block, replace `logger.error(..., exc_info=True)` with `logger.warning("Fail-Soft: Vertex AI Context Cache creation bypassed/failed (%s). Continuing with uncached completion.", str(exc))` and set Redis TTL using `get_settings().context_cache_failed_ttl_seconds`.</action>
      <constraint invariant="rfc7807_dual_reporting_mandate">Ensure clean warning logging without full gRPC stack traces.</constraint>
    </step>

    <step id="2.2" name="HARDEN_AI_STUDIO_ADAPTER">
      <action>Modify @[backend_v2/llm/adapters/ai_studio_adapter.py#L72-L377]:</action>
      <action>1. Replace raw 32768 token threshold with `get_settings().context_cache_min_tokens_ai_studio`.</action>
      <action>2. In `prepare_caching_payload`, after assembling `contents`, call `estimated_tokens = self.calculate_contents_tokens(contents)`.</action>
      <action>3. If `estimated_tokens &lt; get_settings().context_cache_min_tokens_ai_studio` or `not contents`, bypass cache creation with `logger.info("Google AI Studio caching bypassed: Static conversational contents (%d tokens) below minimum threshold (%d tokens).", estimated_tokens, get_settings().context_cache_min_tokens_ai_studio)`, release lock, and return `compiled_prompt.to_flat_messages(), {}`.</action>
      <action>4. In `except Exception as exc:` block, replace `logger.error(..., exc_info=True)` with `logger.warning("Fail-Soft: Google AI Studio Context Cache creation bypassed/failed (%s). Continuing with uncached completion.", str(exc))` and set Redis TTL using `get_settings().context_cache_failed_ttl_seconds`.</action>
      <constraint invariant="data_leak_logging">Do not log sensitive prompt contents; log token metrics and error strings only.</constraint>
    </step>
  </phase>

  <phase id="3" name="ISTQB_TEST_EXPANSION_AND_AUDIT_VERIFICATION">
    <step id="3.1" name="EXPAND_NEGATIVE_AND_BOUNDARY_UNIT_TESTS">
      <action>Update @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L619-L645] and @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L77-L94] with exhaustive ISTQB boundary test cases:</action>
      <action>1. Positive Partition: Static system prompt + large user turn (&gt;= 1024 tokens for Vertex, &gt;= 32768 tokens for AI Studio) successfully proceeds to cache creation.</action>
      <action>2. Negative Partition A (Empty Contents): Multiple large system messages with zero non-system turns must bypass cache creation without invoking Google GAPIC SDK.</action>
      <action>3. Negative Partition B (Sub-Threshold Contents): Large system messages with a small user turn (&lt; 1024 tokens for Vertex, &lt; 32768 tokens for AI Studio) must bypass cache creation without invoking Google GAPIC SDK.</action>
      <action>4. Negative Partition C (Fail-Soft Warning): Simulated SDK exception triggers `logger.warning`, writes `FAILED` status to Redis for `context_cache_failed_ttl_seconds`, and returns flat uncached messages.</action>
      <constraint invariant="anti_happy_path_mandate">Mandatory minimum 2 negative test cases per adapter covering sub-threshold contents and SDK exceptions.</constraint>
    </step>

    <step id="3.2" name="EXECUTE_FULL_BACKEND_AUDIT_GATE">
      <action>Execute full backend audit verification including Ruff linting, MyPy strict typing, and Pytest coverage across all touched targets.</action>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test</command>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/base_adapter.py --test</command>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/vertex_adapter.py --test</command>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/ai_studio_adapter.py --test</command>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py --test</command>
      <command>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py --test</command>
      <constraint invariant="zero_deprecation_mandate">Zero lint errors, zero MyPy errors, 100% test pass rate.</constraint>
    </step>
  </phase>
</execution_protocol>
```

---

## Verification Plan

### Automated Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/base_adapter.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/vertex_adapter.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/llm/adapters/ai_studio_adapter.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py --test`

### Boundary Audit
- `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/implementation_plan_vertex_cache_hardening.md`
