> **STATUS: COMPLETED / TOTEUTETTU (100% Implemented & Verified)**

# Vertex AI & AI Studio Context Cache Hardening, SSOT Infrastructure & Fail-Soft Log Harmonization

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_global_document_cache.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

## Objective
Harmonize the context caching SSOT architecture across Model Registry (`ModelProfile`), Settings (`Settings`), and Provider Adapters (`BaseLLMAdapter`, `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter`). 
1. **Absolute Single Source of Truth**: Delete the legacy generic `context_cache_minimum_token_limit` setting and replace it with explicit, dedicated platform thresholds in `Settings` (`context_cache_min_tokens_vertex = 1024`, `context_cache_min_tokens_ai_studio = 32768`, `context_cache_failed_ttl_seconds = 300`).
2. **Eliminate Hardcoded Bounds & Fallback Max**: Remove all `max(get_settings()...., 1024)` hacks from `VertexCacheAdapter` and `GoogleAIStudioCacheAdapter`.
3. **Fail-Soft Log & TTL Harmonization**: Replace noisy `logger.error(..., exc_info=True)` stack traces with structured `logger.warning(...)` Fail-Soft notifications and use dynamic Redis failure TTLs from `settings.context_cache_failed_ttl_seconds`.
4. **AST Guardrail & Technical Debt Resolution**: Cleanly annotate and resolve AST guardrail warnings (`QGR002`, `QGR003`) on touched adapter files with valid suppression reasons, and refactor legacy `asyncio.gather` concurrency calls in touched unit test files to modern Python 3.14 `asyncio.TaskGroup`.

---

## Target Scope & Boundaries

### Target Files (Read/Write)
- `[MODIFY]` @[backend_v2/settings.py#L51-L746]
- `[MODIFY]` @[backend_v2/llm/adapters/base_adapter.py#L129-L366]
- `[MODIFY]` @[backend_v2/llm/adapters/vertex_adapter.py#L72-L506]
- `[MODIFY]` @[backend_v2/llm/adapters/ai_studio_adapter.py#L72-L381]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L127-L170]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L205-L243]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L406-L424]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L557-L583]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L77-L94]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L184-L219]
- `[MODIFY]` @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L222-L258]

### Context Files (Read-Only)
- `[READ_ONLY]` @[backend_v2/models/prompt.py#L20-L119]
- `[READ_ONLY]` @[backend_v2/models/v2_core.py#L351-L377]
- `[READ_ONLY]` @[backend_v2/llm/client.py#L34-L698]
- `[READ_ONLY]` @[backend_v2/llm/caching_service.py#L14-L118]

---

## Architecture & SSOT Alignment

| Domain Layer | Responsibility | SSOT Location |
| :--- | :--- | :--- |
| **Model Registry** | Strategic user intent (`caching_strategy: "prompt_caching" \| "none"`) per model profile. | `ModelProfile` (`models/v2_core.py`) |
| **System Settings** | Platform infrastructure constraints (`context_cache_min_tokens_vertex = 1024`, `context_cache_min_tokens_ai_studio = 32768`, `context_cache_failed_ttl_seconds = 300`). Legacy `context_cache_minimum_token_limit` completely removed. | `Settings` (`backend_v2/settings.py`) |
| **Base Adapter** | Reusable DRY token estimation for conversational `contents` turns (`estimate_static_tokens`). | `BaseLLMAdapter` (`base_adapter.py`) |
| **Concrete Adapters** | Platform-specific GAPIC cache generation, Redis distributed locking, and Fail-Soft execution. | `VertexCacheAdapter`, `GoogleAIStudioCacheAdapter` |

---

## Tri-Axis Dialectical Audit & Red Team Analysis

### 1. Prosecution (Over-Engineering & YAGNI Advocate)
- **Critique**: Why introduce two separate settings (`context_cache_min_tokens_vertex` and `context_cache_min_tokens_ai_studio`) and `context_cache_failed_ttl_seconds` instead of just keeping a single setting or hardcoding provider constants?
- **Mandatory Deletion Test**: If we deleted `context_cache_failed_ttl_seconds` and hardcoded 300s, what breaks? Nothing immediately, but operations loses the ability to tune blackout windows during provider transient outages without code deployment.
- **Resolution**: The two provider thresholds represent completely different upstream infrastructure constraints (Vertex GAPIC 1024 / 2048 vs. Google AI Studio 32768). Merging them into a single setting caused the exact bug where `max(limit, 32768)` or `max(limit, 1024)` hacks were required. Separating them enforces Single Source of Truth.

### 2. Defense (Architectural Sovereignty & Fail-Fast Advocate)
- **Proof**: Having distinct settings eliminates all runtime `max(get_settings()...., 1024)` fallback duct-tapes across adapters.
- **Fail-Soft Ledger Harmonization**: When GCP API throws a quota or permission error during cache creation, logging at `ERROR` with full traceback floods production monitoring with false alerts during normal graceful degradation. Switching to `logger.warning` with explicit reason while writing `PromptCacheStatus.FAILED.value` to Redis with `settings.context_cache_failed_ttl_seconds` guarantees graceful degradation without noisy stack traces.

### 3. Realist (Duct-Tape & Blast Radius Interrogator)
- **Blast Radius Audit**: Are there any remaining callers of `context_cache_minimum_token_limit` across `backend_v2`?
  - `grep_search` confirmed only `settings.py`, `vertex_adapter.py`, and `ai_studio_adapter.py` touched this setting. No other services or models depend on it.
- **Unit Test Fixtures & Touched Scope Technical Debt**:
  - Found legacy `asyncio.gather(*tasks)` usage in `test_vertex_adapter.py` and `test_ai_studio_adapter.py` thundering herd tests. These must be upgraded to `async with asyncio.TaskGroup() as tg:` to comply with Python 3.14 Fail-Fast concurrency standards.

### 4. Binding Architectural Verdict & Decision Matrix
- **(A) Approved Best Practice**:
  1. Separate provider token thresholds (`context_cache_min_tokens_vertex`, `context_cache_min_tokens_ai_studio`) in `Settings` with strict Pydantic `Annotated[int, Field(ge=..., le=...)]` constraints.
  2. Dynamic Redis sentinel failure TTL via `settings.context_cache_failed_ttl_seconds`.
  3. Structured `logger.warning(...)` without raw prompt leaks or noisy gRPC trace dumps during graceful Fail-Soft fallback.
- **(B) Pruned Over-Engineering**:
  - Direct Pydantic model settings access without intermediate DTO wrappers or artificial abstraction layers.
- **(C) Eradicated Duct-Tape**:
  - Completely eradicated all `max(limit, 1024)` and `max(limit, 32768)` heuristic checks from adapter runtime paths.
  - Upgraded `asyncio.gather(*tasks)` in unit test fixtures to `asyncio.TaskGroup`.

### 5. Red Team Vulnerability Matrix & Falsification Checklist
1. **Zero / Negative TTL Guardrail**: If `context_cache_failed_ttl_seconds` were configured to `<= 0`, Redis `set(ex=...)` would raise an `InvalidArgument` crash. Pydantic `Field(ge=1, le=86400)` must be enforced at the schema boundary.
2. **Data Leak Prevention (DLP)**: When logging cache bypass or failure warnings, log format strings MUST NOT serialize the prompt text or user payload; log only `%d` token metrics and `%s` exception error codes.
3. **AST Guardrail Compliance**: Intentional Fail-Soft exception handlers must include explicit `# noqa: QGR003 [REASON: Fail-Soft graceful degradation to uncached completion on cloud SDK failure]` comments to maintain quality gate compliance.

---

## Execution Protocol

```xml
<execution_protocol>
  <phase id="1" name="SSOT_SETTINGS_PURGE_AND_TECH_DEBT_CLEANUP">
    <step id="1.1" name="TOUCHED_SCOPE_TECH_DEBT_CLEANUP">
      <action>In @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L127-L170] and @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L184-L219], refactor thundering herd concurrency tests from legacy `asyncio.gather(*tasks)` to modern `async with asyncio.TaskGroup() as tg:`.</action>
      <constraint invariant="taskgroup_exceptiongroup_mandate">Never use asyncio.gather; always use asyncio.TaskGroup for concurrency.</constraint>
    </step>

    <step id="1.2" name="REPLACE_LEGACY_SETTINGS_WITH_PLATFORM_SSOT">
      <action>Modify @[backend_v2/settings.py#L51-L746]:</action>
      <action>1. DELETE legacy generic field: `context_cache_minimum_token_limit`.</action>
      <action>2. Add `context_cache_min_tokens_vertex: Annotated[int, Field(ge=1024, le=1000000, description="Minimum non-system content tokens required by Vertex AI Context Caching")] = 1024`.</action>
      <action>3. Add `context_cache_min_tokens_ai_studio: Annotated[int, Field(ge=1024, le=1000000, description="Minimum non-system content tokens required by Google AI Studio Context Caching")] = 32768`.</action>
      <action>4. Add `context_cache_failed_ttl_seconds: Annotated[int, Field(ge=1, le=86400, description="TTL in seconds for marking context cache state as FAILED in Redis")] = 300`.</action>
      <constraint invariant="pydantic_annotated_fields_mandate">All fields must use PEP 593 Annotated[int, Field(...)] syntax with explicit bounds.</constraint>
      <constraint invariant="universal_ssot_and_normalization_mandate">One Concept = One Single Source of Truth. No secondary fallback keys.</constraint>
    </step>
  </phase>

  <phase id="2" name="GATE_ENFORCEMENT_AND_LOG_HARMONIZATION">
    <step id="2.1" name="HARDEN_VERTEX_ADAPTER">
      <action>Modify @[backend_v2/llm/adapters/vertex_adapter.py#L72-L506]:</action>
      <action>1. Replace `min_threshold = max(get_settings().context_cache_minimum_token_limit, 1024)` with pure SSOT lookup `min_threshold = get_settings().context_cache_min_tokens_vertex`.</action>
      <action>2. In `prepare_caching_payload`, if `static_content_token_count &lt; min_threshold` or `not has_non_system_static`, log concise message: `logger.info("Vertex AI caching bypassed: Static conversational contents (%d tokens) below GCP explicit cache minimum (%d tokens) or lacking non-system turns.", static_content_token_count, min_threshold)` and return `compiled_prompt.to_flat_messages(), {}`.</action>
      <action>3. In `except Exception as exc:` block (around line 236), annotate with `# noqa: QGR003 [REASON: Fail-Soft graceful degradation to uncached completion on cloud SDK failure]`, replace `logger.error(..., exc_info=True)` with `logger.warning("Fail-Soft: Vertex AI Context Cache creation bypassed/failed (%s). Continuing with uncached completion.", str(exc))` and set Redis TTL using `ex=get_settings().context_cache_failed_ttl_seconds`.</action>
      <constraint invariant="rfc7807_dual_reporting_mandate">Ensure clean warning logging without full gRPC stack traces.</constraint>
      <constraint invariant="data_leak_logging">Do not log raw prompt payloads; log token metrics and error strings only.</constraint>
    </step>

    <step id="2.2" name="HARDEN_AI_STUDIO_ADAPTER">
      <action>Modify @[backend_v2/llm/adapters/ai_studio_adapter.py#L72-L381]:</action>
      <action>1. Replace `min_threshold = max(get_settings().context_cache_minimum_token_limit, 32768)` with pure SSOT lookup `min_threshold = get_settings().context_cache_min_tokens_ai_studio`.</action>
      <action>2. In `prepare_caching_payload`, if `static_content_token_count &lt; min_threshold` or `not has_non_system_static`, log concise message: `logger.info("Google AI Studio caching bypassed: Static conversational contents (%d tokens) below minimum threshold (%d tokens) or lacking non-system turns.", static_content_token_count, min_threshold)` and return `compiled_prompt.to_flat_messages(), {}`.</action>
      <action>3. In `except Exception as exc:` block (around line 212), annotate with `# noqa: QGR003 [REASON: Fail-Soft graceful degradation to uncached completion on cloud SDK failure]`, replace `logger.error(..., exc_info=True)` with `logger.warning("Fail-Soft: Google AI Studio Context Cache creation bypassed/failed (%s). Continuing with uncached completion.", str(exc))` and set Redis TTL using `ex=get_settings().context_cache_failed_ttl_seconds`.</action>
      <constraint invariant="data_leak_logging">Do not log sensitive prompt contents; log token metrics and error strings only.</constraint>
    </step>
  </phase>

  <phase id="3" name="ISTQB_TEST_EXPANSION_AND_AUDIT_VERIFICATION">
    <step id="3.1" name="EXPAND_NEGATIVE_AND_BOUNDARY_UNIT_TESTS">
      <action>Update @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L127-L170], @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L205-L243], @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L406-L424], @[backend_v2/tests/unit/llm/adapters/test_vertex_adapter.py#L557-L583], @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L77-L94], @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L184-L219], and @[backend_v2/tests/unit/llm/adapters/test_ai_studio_adapter.py#L222-L258] with exhaustive ISTQB boundary test cases:</action>
      <action>1. Positive Partition: Static system prompt + large user turn (&gt;= 1024 tokens for Vertex, &gt;= 32768 tokens for AI Studio) successfully proceeds to cache creation.</action>
      <action>2. Negative Partition A (Empty Contents): Multiple large system messages with zero non-system turns must bypass cache creation without invoking Google GAPIC SDK.</action>
      <action>3. Negative Partition B (Sub-Threshold Contents): Large system messages with a small user turn (&lt; 1024 tokens for Vertex, &lt; 32768 tokens for AI Studio) must bypass cache creation without invoking Google GAPIC SDK.</action>
      <action>4. Negative Partition C (Fail-Soft Warning &amp; TTL): Simulated SDK exception triggers `logger.warning`, writes `FAILED` status to Redis for `context_cache_failed_ttl_seconds`, and returns flat uncached messages.</action>
      <action>5. Concurrency Partition D: Thundering herd protection executed via `asyncio.TaskGroup` confirming exactly 1 SDK creation call.</action>
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

