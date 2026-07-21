# EPIC 107: Execution Pipeline Optimization & Pacing Lock Resolution

## 1. Objective
Optimize the Quorum DAG execution pipeline to eliminate massive "Pacing Lock" bottlenecks, reduce redundant LLM Map-Reduce calls, and parallelize slow Agentic loops. This will drastically reduce execution time (from hours to minutes for large documents in Production) and minimize token burn.

## 2. Background & Problem Statement
### 2. Replacing Pacing Lock with LiteLLM Router (Confirmed)
**Problem:** `base_adapter.py`'s custom `_apply_provider_pacing` utilizes a Redis asynchronous polling loop (`while True: await asyncio.sleep(0.5)`). When the Gemini Flash 100 RPM limit is exceeded (e.g., due to 9 concurrent roles), the loop creates a Thundering Herd phenomenon (hundreds of tasks waking up every 0.5s to make a network call). This blocks the Python event loop and times out even lightweight background tasks such as `litellm_core_utils\logging_worker.py`.

**Solution (Option 2):**
- Completely remove custom `Semaphore` logic from `provider.py`.
- Remove `_apply_provider_pacing` loop from `base_adapter.py`.
- Provide Redis configuration (`redis_host`, `redis_port`) directly to LiteLLM's `Router` class in `provider.py`.
- LiteLLM will centrally track RPM limits. If the limit is exceeded, it throws a `RateLimitError`. This delegates responsibility to our existing `Tenacity` library (which uses smart exponential backoff with jitter), eliminating event loop congestion.

During local development testing (Fast Mode) and Production telemetry analysis, severe performance bottlenecks were identified in the DAG Engine:
1. **Artificial RPM Bottleneck**: `LiteLLM` and the internal Vertex AI adapters are enforcing a 100 RPM Pacing Lock for `gemini-2.5-flash`, despite the GCP quota being 200 RPM. This causes the system to sleep (`0.6s` per request) when the 9-role Floodgate opens.
2. **Redundant Map-Reduce (Guard Step)**: The `Guard` step processes the entire document identically to `Input Processing`, doubling the LLM calls and token usage strictly for a security check.
3. **Agentic Loop Freezing (Fact Checker)**: The Fact Checker utilizes an iterative agent loop (`mcp_tavily_search`) per atom. Executing this sequentially inside the concurrent Floodgate paralyzes the `asyncio.TaskGroup`, as all other roles must wait for the slowest agent to finish its network requests.

## 3. Architectural Constraints & Modernity Gates
* **Central Config Sovereignty**: All RPM limits and concurrency divisors must be strictly defined in `backend_v2/settings.py`. Hardcoding values inside the LLM adapters is strictly prohibited.
* **Fail-Fast & Strict Typing**: Any new schemas introduced for Multi-Search batching must enforce `ConfigDict(strict=True, extra='forbid')`.
* **Python 3.14 Concurrency**: The Fact Checker's Multi-Search network calls MUST be orchestrated using `asyncio.TaskGroup` (not `asyncio.gather`).
* **Zero-Compromise Pledge**: The Guard step fusion must not weaken security. If the merged Input Processing step detects a violation, it must Fail-Fast via a strictly typed exception or DTO flag, not via silent fallback.

## 4. Execution Phases

### Phase 1: RPM Quota Alignment & Semaphore Purge
* **Goal**: Unlock full throughput for Gemini Flash and enforce Central Config Sovereignty by removing legacy throttling without compromising Fail-Fast.
* **Architecture**:
  * Remove all old `Semaphore` logic configurations from `backend_v2/settings.py` (e.g., `semaphore_rpm_divisor`, `semaphore_max_concurrency`, `semaphore_low_rpm_threshold`, `semaphore_low_rpm_limit`).
  * Ensure `provider.py` does not contain any residual custom Semaphore logic, completely delegating rate limit handling to LiteLLM Router and Tenacity backoff, avoiding "Duct-Tape" dead configuration paths.
  * **Exception Whitelisting (Tenacity)**: The Tenacity `@retry` decorator MUST be strictly restricted using `retry_if_exception_type` to catch ONLY infrastructure-level, transient network errors (e.g., `RateLimitError`, `ServiceUnavailableError`, `APIConnectionError`, `Timeout`). It MUST NOT catch the generic `Exception` base class. This guarantees that fatal domain errors (e.g., `AppException(403)` from the Guard step, or 500 Internal crashes) instantly bypass the retry loop and successfully Fail-Fast the pipeline, avoiding infinite retry black holes.

### Phase 2: Guard Step Fusion & Pydantic Fail-Fast Security
* **Goal**: Eliminate the standalone `Guard` DAG step to save ~120 LLM calls per large document without leaking security logic into the DAG engine.
* **Architecture**:
  * **Static-First Caching Topology**: Update the system prompt exclusively in `seed_data.json` for `Input Processing` to inherently include the Guard security constraints. To prevent LLM context cache misses, absolutely NO string concatenation (e.g., f-strings) may be used to inject dynamic variables into the static system prompt. All prompt assembly MUST utilize `PromptBlock` objects, appending any volatile or dynamic variables exclusively at the absolute end of the prompt sequence.
  * Define a strictly typed Pydantic response struct indicating `is_safe: bool` and `rejection_reason: Annotated[str | None, Field(default=None)]`. The DTO MUST enforce `model_config = ConfigDict(strict=True, extra='forbid')` to prevent implicit optionals and silently ignored LLM hallucinations.
  * **Application-Layer Fail-Fast Enforcement**: Do NOT leak the boolean check into the DAG orchestrator. However, do NOT enforce the security check inside the Pydantic model's validators either. Pydantic V2 swallows internal exceptions into generic `ValidationError`s, which triggers catastrophic LLM Schema Healing loops and massive token burn. The Pydantic model must only guarantee structural integrity. The actual `AppException(status_code=403)` MUST be raised in the Application Layer (e.g., Extraction Hook) immediately after a successful `model_validate()`. Crucially, this MUST utilize the **RFC-7807 Dual-Reporting** pattern (a structured `logger.error` trace immediately preceding the exception) to prevent opaque black-box security failures. This bypasses Schema Healing and securely halts the pipeline.
  * **Database Synchronization & Legacy Purge Mandate**: Purge the obsolete `Guard` step from the `seed_data.json` SSOT. To prevent `ComponentNotFound` crashes due to data drift, you MUST run `uv run python backend_v2/seed/run_seed.py local` after this change. In accordance with the Zero-Legacy Mandate, absolutely NO backwards-compatibility hacks, fallback DAG logic, or database migrations may be written to support historical executions that reference the old Guard step. Old executions MUST crash and Fail-Fast natively.
### Phase 3: Fact Checker Multi-Search Architecture & Bounded Concurrency
* **Goal**: Replace the slow, sequential 1-by-1 Agentic Loop with a concurrent Batch Multi-Search, while avoiding external API Thundering Herd scenarios.
* **Architecture**:
  * **Step 3.1**: The LLM evaluates flattened atoms and returns a `BatchSearchQueryDTO` containing a list of required Tavily queries. In strict alignment with LLM Architecture constraints, this MUST be invoked via `LLMTaskExecutor.execute_structured_task()` to guarantee Fail-Fast Native Structured Outputs validation without regex/fallback parsing. If the document is massive, atoms must be processed in **Chunks** to prevent LLM context explosion.
  * **Step 3.1b (Native Deduplication)**: Before executing external API calls, the backend MUST programmatically deduplicate the queries (e.g., via `set()` or dictionaries keyed by normalized query strings). This eliminates redundant concurrent requests for identical facts, saving API credits and network latency.
  * **Step 3.2**: The Backend natively executes all unique Tavily queries concurrently using `asyncio.TaskGroup`.
    * **Thundering Herd Mitigation**: A local `asyncio.Semaphore` MUST be implemented inside the `TaskGroup` to bound the concurrency (max value sourced from `settings.tavily_max_concurrent_requests`). This guarantees we do not hit HTTP 429 Too Many Requests errors from Tavily.
    * **Transient Error & DLQ Routing Mandate**: To prevent a single Tavily network timeout or 502 error from crashing the entire `TaskGroup` (which would instantly orphan all parallel searches), individual workers MUST trap transient errors using Tenacity with exception whitelisting. If retries are exhausted, the worker MUST yield a strictly typed Pydantic Dead Letter Queue (DLQ) state (e.g., returning a `TavilySearchResultDTO` with `status: SearchStatus = SearchStatus.DLQ_TIMEOUT`) back to the aggregator, rather than bubbling up the exception to the `TaskGroup`. The use of raw untyped dictionaries (e.g., `{"_dlq_status": "FAILED"}`) for state transit is strictly prohibited.
  * **Step 3.3**: The aggregated search results are injected into a final synthesis prompt to generate the Fact Checker's definitive Output Matrix.
    * **DLQ Anti-Hallucination Directive**: The synthesis `PromptBlock` MUST explicitly instruct the LLM on how to handle DLQ states (e.g., "If `SearchStatus` is `DLQ_TIMEOUT`, you MUST NOT invent or hallucinate the fact. You must explicitly state that the validation timed out."). Without this, the LLM will fall back on latent knowledge to fill the void.
  * This drastically reduces LLM calls and bypasses the Pacing Lock queue, while enforcing safe, bounded external network IO.

## 5. Verification Plan
* **Telemetry Audit**: Run `finops_trace_analyzer.py` post-execution to verify that Pacing Locks (`Wait-and-Poll`) have decreased by at least 80%.
* **Token Burn**: Verify a 40-50% reduction in total tokens processed during the pre-floodgate phase due to the Guard fusion.
* **Unit Testing**: Ensure the new `BatchSearchQueryDTO` is covered by standard `backend_audit_loop.py` tests with mocked Tavily network responses.

## 6. Tier 4 RCA Findings: WinError 5 (File Locking)
* **Root Cause**: The DAG Executor crashed with `PermissionError: [WinError 5]` at 97% completion because `os.replace` on Windows is not atomic if another process (e.g. `finops_trace_analyzer.py` or antivirus) is reading the file. The original `LocalFileDriver` retry loop was too short (5 retries * 0.1s = 0.5s total), causing a hard timeout. Additionally, the specific `AppException(409)` thrown by the retry loop was incorrectly swallowed by an outer `except Exception` block and re-thrown as a generic `500` error, destroying the forensic audit trail.
* **Resolution**: 
  1. Increased file locking retry window. To enforce **Central Config Sovereignty**, the hardcoded limits (`MAX_REPLACE_RETRIES` = 15, `REPLACE_RETRY_DELAY_SEC` = 0.5s) MUST be removed from `LocalFileDriver` and migrated to `backend_v2/settings.py` as globally accessible configurations.
  2. Fixed `LocalFileDriver.save` to explicitly catch and re-raise `AppException` without wrapping it, restoring the RFC-7807 Fail-Fast pipeline.
  3. Added `test_local_file_driver.py` regression tests to enforce retry logic exhaustion and success paths.
