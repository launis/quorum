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

**Atomic Batch Failure (Fail-Fast):** Because we use `execute_structured_task()` with a strict Pydantic `List[BooleanEvaluationResult]` response model, Pydantic will evaluate the entire array at once. If the LLM hallucinates a missing key or type error in even a single atom, Pydantic will raise a `ValidationError` for the *entire list*. We will NOT attempt to "salvage" the batch using custom JSON parsing loops, as that violates the `llm_structured_execution_mandate`. Instead, we enforce **Atomic Batch Failure**: if the batch schema fails, all 15 atoms in that batch are immediately marked as `ExecutionStatus.SYSTEM_ERROR` in the `TopologicalEvaluator`. Because we use Native Structured Outputs, the probability of schema violations is statistically near zero, making this aggressive Fail-Fast approach highly efficient.

**Dynamic Batch Dispatch (Topological Deadlock Prevention):** The batching queue MUST NOT block indefinitely waiting for exactly 15 atoms. Because the DAG releases atoms layer-by-layer, a specific topological layer might only have 6 independent atoms. If the batcher waits for 15, the DAG will deadlock forever (since the next layer cannot start until the first 6 finish). The `EnrichedDagExecutor` MUST implement a **Debounce/Timeout Flush** (e.g., waiting `0.1s` for new atoms). The batch is dispatched to the LLM immediately if either the capacity (15) is reached, OR the debounce timeout expires, ensuring partial layers execute without delay.

**Alias-Mapped Determinism & Deadlock Prevention:** If the LLM suffers from Attention Dilution and returns only 13 atoms instead of the requested 15, relying on index-based mapping will corrupt the data, and the 2 missing atoms will cause the `TopologicalEvaluator` to deadlock forever. To solve this:
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

### Phase 2: Micro-Prompt Batching
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`, `backend_v2/services/orchestrator/enriched_dag_executor.py`, `backend_v2/settings.py`
- **Action:** Add `SENSOR_BATCH_SIZE` to `settings.py`. Create a new `evaluate_atoms_batch()` method using `execute_structured_task()`. Modify `EnrichedDagExecutor` to collect ready nodes and dispatch them in batches, while preserving the `TopologicalEvaluator` SSOT contract.

### Phase 3: Aggressive Pre-Flight Tuning
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`, `backend_v2/settings.py`
- **Action:** Add `PRE_FLIGHT_FUZZY_THRESHOLD` (e.g., 90) to `settings.py` (Config Sovereignty). Wrap `_fuzzy_match` in `asyncio.to_thread()` for event loop safety. Fine-tune the syntactic anchor checking to fail assertions deterministically using this centralized threshold before LLM invocation.

### Phase 4: Validation & Audit
- Run the universal quality gate `scripts/backend_audit_loop.py` to enforce strict coverage and typing.
- Run a manual end-to-end trace to verify that `JSONDecodeError` is resolved and micro-prompts execute without Vertex AI rate limits.
- Verify that existing unit tests in `test_sliding_window_linker.py`, `test_enriched_dag_executor.py`, and `test_extractive_sensor_service.py` still pass.
