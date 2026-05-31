# Epic 67: Caching Architecture & FinOps Telemetry

## 1. Provider-Agnostic Caching Layer
The caching layer implements the **Zero If-Statement Principle** and the **Clean-Slate** design.

- **BaseLLMAdapter**: Defines the `prepare_caching_payload`, `teardown_cache`, and `calculate_cost` interfaces.
- **LLMCacheAdapterFactory**: Dynamically instantiates adapters (`MockCacheAdapter`, `VertexAICacheAdapter`, `AnthropicCacheAdapter`, `OpenAICacheAdapter`) without conditional branches in the core logic.
- **LLMCachingService**: The primary facade that intercepts `LLMClient` calls to prepare payloads and conduct async teardowns.

## 2. Multi-Dimensional Token Tracking
The `TokenUsage` model tracks tokens across multiple caching dimensions to ensure precise FinOps analytics:
- `prompt_tokens`: Base input tokens.
- `completion_tokens`: Output tokens.
- `cached_tokens`: Tokens successfully retrieved from the cache (hit).
- `cache_creation_input_tokens`: Tokens utilized to hydrate the cache (miss).
- `estimated_savings_usd`: The theoretical dollar amount saved through cache hits.
- `cost_usd`: The actual API cost charged by the provider.

## 3. Purity Guards and FinOps Telemetry
To prevent catastrophic cache invalidation (Thundering Herds), two observability mechanisms are implemented:
1. **Ajonaikainen Purity Scanner (Observability Guard)**:
   - Resides in `LLMCachingService._run_purity_scanner`.
   - Passively scans `role == "system"` blocks for dynamic UUIDs or timestamp patterns.
   - Raises `logger.warning("PROMPT_CACHING_PURITY_VIOLATION...")` if detected, without halting execution.

2. **PROMPT_CACHING_DRIFT_ALERT (FinOps Guard)**:
   - Resides in `UsageService.track_usage`.
   - Analyzes the last 5 workflow executions for `prompt_caching` strategies.
   - If the average cache hit rate (`cached_tokens` / total prompt tokens) drops below **80%**, it triggers `logger.error("PROMPT_CACHING_DRIFT_ALERT...")`.

## 4. Concurrency Constants
`SystemConcurrency` defines absolute limits for the lock lifecycle:
- `CONTEXT_CACHE_LOCK_TTL_SECONDS = 300`
- `CONTEXT_CACHE_LOCK_POLL_INTERVAL_MS = 500`
- `CONTEXT_CACHE_LOCK_WAIT_LIMIT_SECONDS = 20`
- `CONTEXT_CACHE_PASSIVE_TTL_SECONDS = 3600`
