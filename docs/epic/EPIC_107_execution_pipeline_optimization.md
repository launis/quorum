# EPIC 107: Execution Pipeline Optimization & Pacing Lock Resolution

## 1. Objective
Optimize the Quorum DAG execution pipeline to eliminate massive "Pacing Lock" bottlenecks, reduce redundant LLM Map-Reduce calls, and parallelize slow Agentic loops. This will drastically reduce execution time (from hours to minutes for large documents in Production) and minimize token burn.

## 2. Background & Problem Statement
### 2.1 Pacing Lock Resolution (COMPLETED)
**Problem (Resolved):** The legacy custom `_apply_provider_pacing` in `base_adapter.py` and custom `Semaphore` logic in `provider.py` created a Thundering Herd phenomenon. This has been replaced with LiteLLM Router with Redis-backed distributed rate limiting and Tenacity exponential backoff with jitter.

**Current State:**
- Custom `Semaphore` logic: **REMOVED** from `provider.py`.
- `_apply_provider_pacing` loop: **REMOVED** from `base_adapter.py`.
- LiteLLM Router with Redis: **IMPLEMENTED** in `provider.py` (lines 262-272).
- Tenacity exception whitelisting: **IMPLEMENTED** via `_is_transient_llm_error()` in `provider.py`.
- Legacy semaphore settings (`semaphore_rpm_divisor`, etc.): **REMOVED** from `settings.py`.
- **REMAINING CLEANUP**: 2 legacy test fixtures still reference `semaphore_rpm_divisor` (`test_provider_penalties.py:32`, `test_provider_httpx_client.py:21`).

### 2.2 Remaining Pipeline Bottlenecks
The following bottlenecks remain to be addressed:
1. **Redundant Map-Reduce (Guard Step)**: The `Guard` step processes the entire document identically to `Input Processing`, doubling the LLM calls and token usage strictly for a security check.
2. **Agentic Loop Freezing (Fact Checker)**: The Fact Checker utilizes an iterative agent loop (`mcp_tavily_search`) per atom. Executing this sequentially inside the concurrent Floodgate paralyzes the `asyncio.TaskGroup`, as all other roles must wait for the slowest agent to finish its network requests.
3. **9x Token Duplication**: The identical source document is uploaded 9 times (once per role) to the LLM, causing massive bandwidth-induced Pacing Locks and inflated API costs.

## 3. Architectural Constraints & Modernity Gates
* **Central Config Sovereignty**: All RPM limits and concurrency divisors must be strictly defined in `backend_v2/settings.py`. Hardcoding values inside the LLM adapters is strictly prohibited.
* **Fail-Fast & Strict Typing**: Any new schemas introduced for Multi-Search batching must enforce `ConfigDict(strict=True, extra='forbid')`.
* **Python 3.14 Concurrency**: The Fact Checker's Multi-Search network calls MUST be orchestrated using `asyncio.TaskGroup` (not `asyncio.gather`).
* **Zero-Compromise Pledge**: The Guard step fusion must not weaken security. If the merged Input Processing step detects a violation, it must Fail-Fast via a strictly typed exception or DTO flag, not via silent fallback.

## 4. Execution Phases

### Phase 1: RPM Quota Alignment & Semaphore Purge — ✅ COMPLETED
* **Status**: Core implementation completed in prior sessions. LiteLLM Router with Redis and Tenacity exception whitelisting are fully operational.
* **Remaining Cleanup**:
  * Purge legacy test fixture references to `semaphore_rpm_divisor` in `test_provider_penalties.py` and `test_provider_httpx_client.py`.
  * Run `backend_audit_loop.py` to confirm zero regressions.

### Phase 2: Guard Step Fusion & Pydantic Fail-Fast Security
* **Goal**: Eliminate the standalone `Guard` DAG step to save ~120 LLM calls per large document without leaking security logic into the DAG engine.
* **Pre-condition**: The Guard step has already been removed from `seed_data.json` SSOT. This phase focuses on the prompt fusion, DTO refactoring, and domain model sunset.
* **Architecture**:
  * **Static-First Caching Topology**: Update the system prompt exclusively in `seed_data.json` for `Input Processing` to inherently include the Guard security constraints. To prevent LLM context cache misses, absolutely NO string concatenation (e.g., f-strings) may be used to inject dynamic variables into the static system prompt. All prompt assembly MUST utilize `PromptBlock` objects, appending any volatile or dynamic variables exclusively at the absolute end of the prompt sequence.
  * Define a strictly typed Pydantic response struct indicating `is_safe: bool` and `rejection_reason: Annotated[str | None, Field(default=None)]`. The DTO MUST enforce `model_config = ConfigDict(strict=True, extra='forbid')` to prevent implicit optionals and silently ignored LLM hallucinations.
  * **Application-Layer Fail-Fast Enforcement**: Do NOT leak the boolean check into the DAG orchestrator. However, do NOT enforce the security check inside the Pydantic model's validators either. Pydantic V2 swallows internal exceptions into generic `ValidationError`s, which triggers catastrophic LLM Schema Healing loops and massive token burn. The Pydantic model must only guarantee structural integrity. The actual `AppException(status_code=403)` MUST be raised in the Application Layer (e.g., Extraction Hook) immediately after a successful `model_validate()`. Crucially, this MUST utilize the **RFC-7807 Dual-Reporting** pattern (a structured `logger.error` trace immediately preceding the exception) to prevent opaque black-box security failures. This bypasses Schema Healing and securely halts the pipeline.
  * **Guard Domain Model Sunset Plan**: The following artifacts MUST be explicitly refactored or deleted:
    * `backend_v2/models/domain/guard.py` — DELETE. Migrate `is_safe` / `rejection_reason` fields into the Input Processing output DTO as a flat sub-section (not a nested sub-model).
    * `backend_v2/models/domain/scoring.py` (`StepGuardDTO`) — REFACTOR to read security data from the unified Input Processing output state instead of a separate `step_guard` key.
    * `backend_v2/hooks/scoring.py` (line 117) — REFACTOR `sanitization_result` accessor to read from the Input Processing state context.
    * `backend_v2/models/state.py` (line 229) — DELETE `step_guard` accessor. Replace with a new accessor on the Input Processing state.
    * `backend_v2/models/domain/judge.py` (`step_guard` field) — REFACTOR to source security data from the unified Input Processing output.
    * `backend_v2/llm/mock_data.py` (`MOCK_GUARD_OUTPUT`) — DELETE and replace with mock data that includes security fields in the Input Processing mock output.
    * `backend_v2/tests/unit/models/domain/test_guard.py` — DELETE or refactor to test the new unified Input Processing security DTO.
    * `backend_v2/models/domain/__init__.py` — PURGE all `GuardInput`, `GuardOutput` exports.
### Phase 3: Fact Checker Multi-Search Architecture & Bounded Concurrency
* **Goal**: Replace the slow, sequential 1-by-1 Agentic Loop with a concurrent Batch Multi-Search, while avoiding external API Thundering Herd scenarios.
* **New Settings Required** (Central Config Sovereignty — `backend_v2/settings.py`):
  * `tavily_max_concurrent_requests: Annotated[int, Field(description="Max parallel Tavily search requests")] = 5`
* **Enum Definition Required** (Tripartite Architecture — `backend_v2/models/enums.py`):
  * `SearchStatus(StrEnum)` with values: `COMPLETED`, `DLQ_TIMEOUT`, `DLQ_ERROR`. MUST NOT be defined inline in a DTO.
* **Architecture**:
  * **Step 3.1**: The LLM evaluates flattened atoms and returns a `BatchSearchQueryDTO` containing a list of required Tavily queries. In strict alignment with LLM Architecture constraints, this MUST be invoked via `LLMTaskExecutor.execute_structured_task()` to guarantee Fail-Fast Native Structured Outputs validation without regex/fallback parsing. If the document is massive, atoms must be processed in **Chunks** to prevent LLM context explosion.
  * **Step 3.1b (Native Deduplication & Bipartite Mapping)**: Before executing external API calls, the backend MUST programmatically deduplicate the queries using dictionaries keyed by **case-folded, whitespace-normalized** query strings. This eliminates redundant concurrent requests for identical or near-identical facts (e.g., "What is X?" vs "what is X?").
    * **Bipartite Mapping Mandate**: The deduplication mechanism MUST maintain a two-way mapping (`Original Query -> Normalized Hash -> Result`). When the results are injected back into the LLM synthesis prompt in Step 3.3, they MUST be labeled with the *exact original query string* the LLM requested. If the LLM receives results labeled with modified/normalized strings it doesn't recognize, it will hallucinate the missing mappings.
  * **Step 3.2**: The Backend natively executes all unique Tavily queries concurrently using `asyncio.TaskGroup`.
    * **Thundering Herd Mitigation**: A local `asyncio.Semaphore` MUST be implemented inside the `TaskGroup` to bound the concurrency (max value sourced from `settings.tavily_max_concurrent_requests`). This guarantees we do not hit HTTP 429 Too Many Requests errors from Tavily.
    * **Transient Error & DLQ Routing Mandate**: To prevent a single Tavily network timeout or 502 error from crashing the entire `TaskGroup` (which would instantly orphan all parallel searches), individual workers MUST trap transient errors using Tenacity with exception whitelisting. If retries are exhausted, the worker MUST yield a strictly typed Pydantic Dead Letter Queue (DLQ) state (e.g., returning a `TavilySearchResultDTO` with `status: SearchStatus = SearchStatus.DLQ_TIMEOUT`) back to the aggregator, rather than bubbling up the exception to the `TaskGroup`. The use of raw untyped dictionaries (e.g., `{"_dlq_status": "FAILED"}`) for state transit is strictly prohibited.
  * **Step 3.3**: The aggregated search results are injected into a final synthesis prompt to generate the Fact Checker's definitive Output Matrix.
    * **DLQ Anti-Hallucination Directive**: The synthesis `PromptBlock` MUST explicitly instruct the LLM on how to handle DLQ states (e.g., "If `SearchStatus` is `DLQ_TIMEOUT`, you MUST NOT invent or hallucinate the fact. You must explicitly state that the validation timed out."). Without this, the LLM will fall back on latent knowledge to fill the void.
  * This drastically reduces LLM calls and bypasses the Pacing Lock queue, while enforcing safe, bounded external network IO.

### Phase 4: Global Document Context Caching (Token Burn Resolution)
* **Goal**: Eradicate the massive 9x token duplication (uploading the identical source document for every role) across the DAG Floodgate, drastically cutting API costs and bandwidth-induced Pacing Locks.
* **Adapter Delegation Mandate**: The new `LLMTaskExecutor.create_context_cache()` and `delete_context_cache()` methods MUST delegate to the existing `BaseLLMAdapter.prepare_caching_payload()` and `BaseLLMAdapter.teardown_cache()` via the `LLMCacheAdapterFactory`. Creating a parallel caching system that bypasses the adapter pattern is strictly prohibited per the `provider_abstraction_mandate` and the Global Document Cache KI.
* **Architecture**:
  * **Composite Cache Segmentation (Model + Inputs)**: Because the UI allows individual DAG roles to override their LLM `Model Strategy` AND dynamically select which input documents they receive, a single monolithic cache is structurally impossible and logically dangerous (passing a 2MB document to a role that only requested a 10KB chat log violates UI mapping isolation and increases hallucination risk).
    * Before the concurrent `asyncio.TaskGroup` (Floodgate) opens, the DAG Orchestrator MUST calculate a composite cache signature for each active role: `(physical_model_name, sorted_tuple_of_input_keys)`.
    * The Orchestrator MUST group roles by this signature and upload the static source text exactly ONCE **per unique signature** via `LLMTaskExecutor.create_context_cache()`. 
    * For example, if Roles A and B use `flash` + `[product_text, chat_log]`, they share Cache 1. If Role C uses `flash` + `[chat_log]`, it gets Cache 2. If Role D uses `pro` + `[product_text]`, it gets Cache 3. This guarantees perfect UI mapping fidelity while maximizing FinOps across identical payload requirements.
  * **Dynamic Injection**: The Orchestrator receives a `cache_id` and passes it down to the parallel execution roles. The LLM calls within the TaskGroup MUST ONLY send their specific dynamic `PromptBlock` instructions alongside the `cache_id`.
  * **FinOps Explicit Cleanup Mandate**: Especially in `development` and `fast` modes (where runs are frequent or cancelled mid-execution), orphaned context caches cause exponential passive storage billing. The cache lifecycle MUST be strictly managed using a `try...finally` block.
  * **Race Condition Guard (Orchestrator-Level Lifecycle)**: The `try...finally` block that guarantees `LLMTaskExecutor.delete_context_cache(cache_id)` execution MUST be placed at the Orchestrator level, entirely wrapping the `asyncio.TaskGroup`. If cache teardown is injected into individual worker/role execution loops, the first task to complete will trigger the `finally` block, destroying the shared `cache_id`. This creates a catastrophic race condition (Context Not Found) for all other parallel agents still executing within the TaskGroup. The cache must outlive all parallel executions.

### Phase 5: Zero-Chunking Cache Pagination (Atomizer Optimization)
* **Goal**: Eradicate physical string chunking during Atom Extraction (`TwoPassAtomizer.py`) to eliminate Context/Recall collapse and maximize Context Cache utilization.
* **Architecture**:
  * **Semantic Anchor Pagination**: Instead of physically splitting large documents via `chunk.split("\n\n")` (which destroys semantic integrity and prevents caching), the backend MUST upload the entire unified source text (already hydrated with `[Block: src_1]`, `[Msg: chat_5]` by `AliasEngine`) exactly ONCE into the Global Context Cache.
  * **Attention Steering**: The `TwoPassAtomizer` will spawn parallel extraction workers that all share the exact same `cache_id`. Instead of sending raw text chunks, each worker's dynamic prompt will instruct it to extract atoms strictly from a specific semantic ID range (e.g., *"Analyze the cached document. Extract atoms ONLY from [Block: src_1] to [Block: src_20]"*).
  * **Contextual Preservation**: Because the entire document is resident in the cache, the LLM retains access to the global context (e.g., resolving pronouns or acronyms defined on page 1, even if the worker is assigned to extract atoms from page 15). This prevents the hallucinations caused by arbitrary line/paragraph chunking mid-dialogue.

## 5. Verification Plan
* **Mandatory Quality Gate (Per Phase)**: After EVERY code mutation, you MUST run `uv run python scripts/backend_audit_loop.py <target_path> --test` to enforce Ruff + MyPy + Pytest before proceeding.
* **Telemetry Audit**: Run `finops_trace_analyzer.py` post-execution to verify that Pacing Locks (`Wait-and-Poll`) have decreased by at least 80%.
* **Token Burn**: Verify a 40-50% reduction in total tokens processed during the pre-floodgate phase due to the Guard fusion.
* **Unit Testing**: Ensure the new `BatchSearchQueryDTO` and `SearchStatus` enum are covered by standard `backend_audit_loop.py` tests with mocked Tavily network responses.
* **Guard Sunset Validation**: After Phase 2, grep for `GuardInput`, `GuardOutput`, `StepGuardDTO` across the entire `backend_v2/` tree. Zero references MUST remain outside of git history.

## 6. Tier 4 RCA Findings: WinError 5 (File Locking)
* **Root Cause**: The DAG Executor crashed with `PermissionError: [WinError 5]` at 97% completion because `os.replace` on Windows is not atomic if another process (e.g. `finops_trace_analyzer.py` or antivirus) is reading the file. The original `LocalFileDriver` retry loop was too short (5 retries * 0.1s = 0.5s total), causing a hard timeout. Additionally, the specific `AppException(409)` thrown by the retry loop was incorrectly swallowed by an outer `except Exception` block and re-thrown as a generic `500` error, destroying the forensic audit trail.
* **Resolution**: 
  1. Increased file locking retry window. To enforce **Central Config Sovereignty**, the hardcoded limits (`MAX_REPLACE_RETRIES` = 15, `REPLACE_RETRY_DELAY_SEC` = 0.5s) in `local_file_driver.py` (lines 18-19) MUST be removed and migrated to `backend_v2/settings.py` as:
     * `file_replace_max_retries: Annotated[int, Field(description="Max retries for Windows os.replace file locking")] = 15`
     * `file_replace_retry_delay_sec: Annotated[float, Field(description="Delay between file replace retries in seconds")] = 0.5`
  2. Fixed `LocalFileDriver.save` to explicitly catch and re-raise `AppException` without wrapping it, restoring the RFC-7807 Fail-Fast pipeline.
  3. Added `test_local_file_driver.py` regression tests to enforce retry logic exhaustion and success paths.
