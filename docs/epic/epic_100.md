# EPIC 100: Radical Speedup & DAG Scalability

## 1. Executive Summary
This Epic addresses the critical scalability bottlenecks discovered when processing large matrices and documents in the Quorum V2 engine. The implementation focuses on three primary architectural enhancements: replacing the 8192 output token limit crash with an iterative Chunk Worker for the Linker, batching micro-prompts into single LLM requests using the primary Gemini 2.5 Flash model, and intensifying deterministic Python pre-flight filtering to bypass the LLM entirely where possible.

## 2. Problem Statement
When running massive execution graphs (e.g., parsing large PDFs with hundreds of atoms), the `SlidingWindowLinker` feeds the LLM an input context that easily fits within the 2-million token limit, but expects an output graph that exceeds the model's 8192 output token ceiling. This results in truncated JSON and fatal `ValidationError` crashes (`JSONDecodeError`).

Concurrently, the Map-Reduce phase (`ExtractiveSensorService`) executes hundreds of independent True/False assertions against the LLM using the heavy primary model. Due to the Vertex AI rate limit (100 RPM), this triggers a 0.6-second exponential backoff pacing lock per claim, slowing down the extraction phase drastically.

## 3. Architectural Directives (Tier 0 Verified)

### 3.1. Iterative Linker with Deterministic Python Reduction
To solve the Output Token vs. Input Context paradox, the `SlidingWindowLinker` will be refactored to utilize an iterative sliding window pattern. Large datasets will be aggressively windowed and evaluated as partial sub-graphs by the LLM (Map). Crucially, the subsequent combination of these sub-graphs (Reduce) will NOT be performed by the LLM. Instead, the edges will be unified using purely deterministic O(N) Python logic. This eliminates the hallucination risk and latency of LLM-based recursive reduction, ensuring no single LLM call is required to output more than 8192 tokens while strictly maintaining Fail-Fast Pydantic integrity.

### 3.2. Micro-Prompt Batching with Mathematical Bounds
Instead of using multiple different LLM actors or routing to a smaller model, the system will exclusively use the primary `gemini-2.5-flash` model. To bypass the 100 RPM limit and 0.6s pacing lock, the `ExtractiveSensorService` will batch Boolean assertions into a single LLM request. 

**Addressing Root-JSON Truncation:** To ensure the returned JSON array never truncates and causes a root-level `JSONDecodeError`, the batch size must be mathematically strictly bounded. A single evaluation requires at most ~300 tokens (chain-of-thought + boolean). By capping the batch size strictly at 15 atoms per request, the maximum theoretical output is ~4500 tokens, completely insulating the request from the 8192 token ceiling. 

Inside this safe boundary, we will implement **Resilient Batch Parsing**. The backend will validate the results atom-by-atom in a loop, ensuring that if one atom fails Pydantic validation due to a syntax hallucination, only that specific atom is marked as failed, salvaging the rest of the batch.

**Cache Survival Strategy (Prefix-Aware Batching):** Naive batching poses a risk to cache hit rates if dynamic variables alter the prompt. To guarantee Vertex AI Context Cache survival (as per the KI rules), the heavy `source_text` MUST be anchored at the absolute beginning of the prompt. The batched atoms must be placed at the absolute end. Because Vertex AI caches based on precise prefix matching, the 2-million token document prefix will score a 100% cache hit, and only the lightweight batched atoms at the tail end will be processed dynamically.

### 3.3. Deterministic Pre-Flight Falsification & Event Loop Protection
The `ExtractiveSensorService` will adopt an aggressive `_fuzzy_match` pre-flight threshold. If the required syntactic anchors are wholly absent from the target text, the LLM will be entirely bypassed (`decided=True`), saving tens of thousands of tokens and eliminating unnecessary API calls.

**Event Loop Protection:** Because scanning millions of tokens with `rapidfuzz` is a heavy, CPU-bound $O(N \times M)$ operation, executing this synchronously within an `async` function would starve the FastAPI event loop. To prevent blocking the server, this deterministic extraction must be explicitly offloaded using `asyncio.to_thread()` (which leverages the ThreadPoolExecutor and takes advantage of RapidFuzz's GIL release), ensuring asynchronous scalability.

## 4. Execution Phases

### Phase 1: SlidingWindowLinker Deterministic Reduction
- **Target:** `backend_v2/services/orchestrator/sliding_window_linker.py`
- **Action:** Implement iterative sliding windows for LLM generation of `LinkerResponseDTO`, and build a deterministic O(N) Python reducer to merge the resulting graph edges safely.

### Phase 2: Micro-Prompt Batching
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **Action:** Refactor the evaluation logic to process atoms in batches within a single LLM call, drastically reducing the number of Vertex AI queries.

### Phase 3: Aggressive Pre-Flight Tuning
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **Action:** Fine-tune the fallback constraints in the syntactic anchor checking to fail assertions deterministically before LLM invocation.

### Phase 4: Validation & Audit
- Run the universal quality gate `scripts/backend_audit_loop.py` to enforce strict coverage and typing.
- Run a manual end-to-end trace to verify that `JSONDecodeError` is resolved and micro-prompts execute without Vertex AI rate limits.
