# EPIC: V3 LLM Concurrency Limiter & Rate Throttle

**STATUS:** Draft / Planning Phase  
**TIER:** Tier 1 (Epic Planner)
**CONTEXT:** Quorum V3 Architecture (Python Backend V2 + Model Registry API)

## 📌 1. Objective
Currently, the V3 `DAGExecutor` parallelizes all deeply independent nodes (`asyncio.gather`). When evaluating large matrices (e.g., Toulmin, BARS, Bloom) over a large document, the engine spawns 20-50 simultaneous LLM calls. 

Because `vertex_ai/gemini-2.5-flash` has a strict Requests Per Minute (RPM) quota of 15 and a Tokens Per Minute (TPM) quota of 100k, the backend inevitably triggers `429 Resource Exhausted` API limits. Though LiteLLM's retry mechanic catches this gracefully, hammering the API violently is structurally inefficient.

**The goal of this Epic is to:**
Implement an asynchronous **Concurrency Queue (Token Bucket / Semaphore)** in the backend that intelligently drips requests to the LLM Provider exactly within its declared limits from the Model Registry UI configurations, thereby eliminating `Exception litellm.RateLimitError` completely.

---

## 🏗️ 2. Architectural Design

1. **The Throttle (Semaphore Approach):** At minimum, limit the *inflight* (samanaikaiset) connections globally per provider. If a model allows `rpm_limit: 15`, we should not dispatch 30 parallel requests in the first second.
2. **The Bucket (Leaky Bucket / Token Bucket):** Track temporal expenditure. E.g., `requests_sent_in_last_60s`. If `>= rpm_limit`, `asyncio.sleep()` the thread instead of throwing it at LiteLLM to bounce back.
3. **Model Registry Awareness:** The configuration of the queue MUST be dynamic. `tpm_limit` and `rpm_limit` are already dynamically seeded and editable in Admin Studio V2 (Model Registry). The queue must consume these limits!

<br>

---

## 🗺️ 3. Execution Milestones

### Phase 1: Core Limiter Implementation
- [ ] **Create Component:** Create `backend_v2/utils/rate_limiter.py`.
- [ ] **Implement `RateLimiter` Singleton:** An asynchronous singleton class (`GlobalRateLimiter`) that keeps temporal state (e.g., a rolling window of timestamps of fired requests).
- [ ] **Expose Async Wrapper:** Expose an `async with throttled(model_name=...)` context manager.

### Phase 2: DAG Executor & Provider Integration
- [ ] **Inject to Router:** Integrate the `RateLimiter` directly inside `backend_v2/llm/provider.py` right before `litellm.acompletion()` is called.
- [ ] **Fetch Limits Dynamically:** Modify the provider to extract `tpm_limit` and `rpm_limit` from the Model Config provided during execution.
- [ ] **Verify Sleep:** Verify that the `RateLimiter` correctly runs `await asyncio.sleep(retry_after)` when the temporal counter exceeds the specific model's config.

### Phase 3: Empirical Validation & Testing
- [ ] **Artificial Benchmark:** Construct a workflow with 30 concurrent evaluation nodes.
- [ ] **Log Verification:** Monitor the `backend_debug.log`. The expected result is a perfectly staggered execution (e.g., executing 2 nodes every 8 seconds) rather than a giant burst followed by red `429 Resource Exhausted` retries.
- [ ] **Frontend Perception Test:** Verify that the Flutter UI properly maintains the Server-Sent Events (SSE) stream without timing out while the slower queue processes the payload.

---

## 🚨 4. Banned Patterns
- **Do not hardcode limits:** Do not write `RATE_LIMIT = 15` anywhere in code. Limits MUST come from the Model Registry system config dynamically.
- **Do not block the asyncio event loop:** Do not use `time.sleep()`. All backoff/queue mechanics must use `await asyncio.sleep()`.
- **Do not swallow errors:** If a 429 *does* somehow pierce the queue (e.g., external quota change), the existing LiteLLM retry loop must still engage as a final safety net.
