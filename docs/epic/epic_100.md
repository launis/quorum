# EPIC 100: Radical Speedup & DAG Scalability

## 1. Executive Summary
This Epic addresses the critical scalability bottlenecks discovered when processing large matrices and documents in the Quorum V2 engine. The implementation focuses on three primary architectural enhancements: replacing the 8192 output token limit crash with output-aware windowing for the Linker, batching micro-prompts into single LLM requests using the primary strategy model, and intensifying deterministic Python pre-flight filtering to bypass the LLM entirely where possible.

## 2. Problem Statement
When running massive execution graphs (e.g., parsing large PDFs with hundreds of atoms), the `SlidingWindowLinker` feeds the LLM an input context that easily fits within the 2-million token limit, but expects an output graph that exceeds the model's 8192 output token ceiling. This results in truncated JSON and fatal `ValidationError` crashes (`JSONDecodeError`).

Concurrently, the Map-Reduce phase (`ExtractiveSensorService`) executes hundreds of independent True/False assertions against the LLM using the heavy primary model. Due to the Vertex AI rate limit (100 RPM), this triggers a 0.6-second exponential backoff pacing lock per claim, slowing down the extraction phase drastically.

## 3. Architectural Directives (Tier 0 Verified)

### 3.1. Output-Aware Window Sizing with Deterministic Python Reduction
The root cause of the `SlidingWindowLinker` crash is the **Output Token vs. Input Context paradox**: the system checks the 2M input token capacity but ignores the 8192 output token ceiling. The existing `link_graph` method already implements a correct sliding window with `master_deps` dictionary merging (a pure O(N) Python reducer). This means the **Reduce** phase is already deterministic. The fix is therefore surgical: limit the **number of atoms per window** (not chunks) so that the LLM response for each window stays safely under 8192 output tokens.

**Max Atoms Per Window Calculation:** Each `LinkerDependencyDTO` (alias, edges with reasoning) produces ~200 output tokens. To stay at 50% of the 8192 ceiling (~4000 tokens), the maximum atoms per window MUST be capped at **20 atoms**. This value MUST be defined in `settings.py` as `LINKER_MAX_ATOMS_PER_WINDOW` (Global Config Sovereignty mandate).

**Critical Discovery (As-Built):** The current `master_deps` dictionary merge at lines 196-202 of `sliding_window_linker.py` already performs deterministic O(N) Python reduction. The overlapping windows ensure cross-chunk edges are discovered. No LLM-based recursive reduction is needed or proposed.

### 3.2. Micro-Prompt Batching with Mathematical Bounds
The system will exclusively use the primary strategy model (resolved via `LLMClient.from_strategy()` per the Model Registry mandate — no hardcoded model strings). To bypass the RPM limit and pacing lock, the `ExtractiveSensorService` will batch Boolean assertions into a single LLM request.

**Addressing Root-JSON Truncation:** To ensure the returned JSON array never truncates and causes a root-level `JSONDecodeError`, the batch size must be mathematically strictly bounded. A single evaluation requires at most ~300 tokens (chain-of-thought + boolean). By capping the batch size strictly at 15 atoms per request, the maximum theoretical output is ~4500 tokens, completely insulating the request from the 8192 token ceiling. 

**Atomic Batch Failure (Fail-Fast) & Transient Retry:** Because we use `execute_structured_task()` with a strict Pydantic `List[BooleanEvaluationResult]` response model, Pydantic will evaluate the entire array at once. If the LLM hallucinates a missing key, Pydantic will raise a `ValidationError`. We will NOT attempt to "salvage" the batch using custom JSON parsing loops, as that violates the `llm_structured_execution_mandate`. Instead, we enforce **Atomic Batch Failure**. However, to prevent bypassing Quorum's workflow-level retries for network issues, the `EnrichedDagExecutor` MUST verify the error type using `_is_transient_error(e)`. If the error is transient (e.g., 503, 429), the executor MUST re-raise it to trigger the Arq worker retry loop. Only if the error is a persistent, non-transient schema failure (after internal `LLMClient` retries are exhausted) will the 15 atoms be routed to `ExecutionStatus.SYSTEM_ERROR` (DLQ). Because we use Native Structured Outputs, the probability of persistent schema violations is statistically near zero, making the token cost of dropping 14 atoms an acceptable trade-off for architectural purity.

**Deterministic Wave Evaluation (Kahn's Algorithm):** Time-based waits (e.g., `0.1s` Debounce) are strictly forbidden ("Duct-Tape" Anti-Pattern) because they create non-determinism, race conditions, and flaky tests. To batch safely without deadlocks or timeouts, the `TopologicalEvaluator` MUST be refactored to use **Wave-Based Topological Sorting (Kahn's Algorithm)** instead of dynamic `asyncio.Event` waits. The Evaluator will collect all mathematically independent nodes into a deterministic `ready_nodes` list (a topological "wave"). It will then slice this wave into strict batches (max 15 atoms) and pass them to the `EnrichedDagExecutor` via a new `batch_evaluation_callback`. This guarantees 100% deterministic batching with zero race conditions and zero time-based deadlocks.
1. The batched Pydantic response MUST include the `alias` (e.g., `a0`) for each evaluation.
2. The `EnrichedDagExecutor` MUST iterate over the *requested* batch (the 15 sent aliases), not the *returned* batch.
3. Any requested alias missing from the LLM's response MUST be explicitly caught and marked as `ExecutionStatus.SYSTEM_ERROR`. This guarantees the DAG's `asyncio.Event` is set, completely eliminating the deadlock risk.

**Cache Survival Strategy (Prefix-Aware Batching):** Naive batching poses a risk to cache hit rates if dynamic variables alter the prompt. To guarantee Vertex AI Context Cache survival (as per the KI rules), the heavy `source_text` MUST be anchored at the absolute beginning of the prompt. The batched atoms must be placed at the absolute end. Because Vertex AI caches based on precise prefix matching, the 2-million token document prefix will score a 100% cache hit, and only the lightweight batched atoms at the tail end will be processed dynamically.

### 3.3. Deterministic Pre-Flight Falsification & Event Loop Protection
The `ExtractiveSensorService` will adopt an aggressive `_fuzzy_match` pre-flight threshold. If the required syntactic anchors are wholly absent from the target text, the LLM will be entirely bypassed (`decided=True`), saving tens of thousands of tokens and eliminating unnecessary API calls.

**Event Loop Protection:** Because scanning millions of tokens with `rapidfuzz` is a heavy, CPU-bound $O(N \times M)$ operation, executing this synchronously within an `async` function would starve the FastAPI event loop. To prevent blocking the server, this deterministic extraction must be explicitly offloaded using `asyncio.to_thread()` (which leverages the ThreadPoolExecutor and takes advantage of RapidFuzz's GIL release), ensuring asynchronous scalability.

> **Note (As-Built):** Rule `strict_physical_anchoring_mandate` in `05_llm_architecture.md` mandates `str.find` over `rapidfuzz` for LLM *evidence extraction* validation. The Pre-Flight fuzzy matching here applies to TDA *syntactic anchor* detection (a distinct domain), where fuzzy matching is the correct behavior. These are not in conflict.

### 3.4. TopologicalEvaluator Compatibility
The current `TopologicalEvaluator` evaluates atoms **one-by-one** via an `evaluation_callback`. Batching MUST NOT break this SSOT architecture. The batch optimization MUST be implemented **inside** the `EnrichedDagExecutor` layer, which collects ready-to-evaluate nodes from the `TopologicalEvaluator` and dispatches them in batches. The `TopologicalEvaluator` itself MUST remain untouched (SSOT for DAG cascade logic).

## 4. Execution Phases

### Phase 1: SlidingWindowLinker Output-Aware Windowing
- **Target:** `backend_v2/services/orchestrator/sliding_window_linker.py`, `backend_v2/settings.py`
- **Action:** Add `LINKER_MAX_ATOMS_PER_WINDOW` to `settings.py`. Refactor `_get_sliding_windows` to subdivide windows when the atom count exceeds the output-safe threshold. The existing `master_deps` dictionary merge already serves as the deterministic O(N) reducer.

### Phase 2: Micro-Prompt Batching & Wave Evaluation
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`, `backend_v2/services/orchestrator/enriched_dag_executor.py`, `backend_v2/services/orchestrator/topological_evaluator.py`, `backend_v2/settings.py`
- **Action:** Add `SENSOR_BATCH_SIZE` to `settings.py`. Refactor `TopologicalEvaluator` to use Kahn's Algorithm (Wave-Based Evaluation) to deterministically yield batches of `ready_nodes` without `asyncio.Event` timeouts. Modify `EnrichedDagExecutor` to accept `batch_evaluation_callback()` and enforce Alias-Mapped Determinism.

### Phase 3: Aggressive Pre-Flight Tuning & Thread Starvation Prevention
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`, `backend_v2/settings.py`
- **Action:** Add `PRE_FLIGHT_FUZZY_THRESHOLD` (e.g., 90) to `settings.py` (Config Sovereignty). To prevent **Thread Starvation**, the CPU-heavy `_fuzzy_match` MUST be executed in bulk. Do NOT call `asyncio.to_thread()` individually for each atom. Instead, wrap the entire batch of 15 atoms into a single `asyncio.to_thread(_batch_fuzzy_match, atoms)` call. This ensures that the global concurrency semaphore (10) perfectly matches the thread pool utilization (max 10 threads), completely eliminating starvation. Fine-tune the syntactic anchor checking to fail assertions deterministically using this centralized threshold before LLM invocation.

### Phase 4: Unit Test Mock Migration (Anti-TDD Trap Prevention)
- **Target:** `backend_v2/tests/` (Specifically tests covering `ExtractiveSensorService` and `TopologicalEvaluator`)
- **Action:** Because the return type of `execute_structured_task()` changes from a single `BooleanEvaluationResult` to a `list[BooleanEvaluationResult]`, all existing `AsyncMock` return values in the test suite will instantly break. The executor MUST systematically update all mocks patching these functions to return a `list`. Failure to do so will trigger the Anti-TDD Trap, where the executor might incorrectly revert the main business logic just to make legacy tests pass.

### Phase 5: Validation & Audit
- Run the universal quality gate `scripts/backend_audit_loop.py` to enforce strict coverage and typing.
- Run a manual end-to-end trace to verify that `JSONDecodeError` is resolved and micro-prompts execute without Vertex AI rate limits.
- Verify that existing unit tests in `test_sliding_window_linker.py`, `test_enriched_dag_executor.py`, and `test_extractive_sensor_service.py` still pass.
