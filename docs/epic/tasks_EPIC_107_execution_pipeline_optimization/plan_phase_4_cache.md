# EPIC 107 Phase 4: Global Document Context Caching (Token Burn Resolution)

## Source: Epic Phase 4

### 1. Objective
Eradicate the massive 9x token duplication (uploading identical source documents for every DAG role) across the Floodgate `TaskGroup`. Implement composite cache signatures and orchestrator-level lifecycle management to prevent cache collision, orphan billing, and context loss during execution.

### 2. Architectural Invariants
- **`00-antigravity-core.md` / `01-python-backend.md` Mandates**:
  - **Adapter Delegation Mandate**: Must use `BaseLLMAdapter.prepare_caching_payload()` via the `LLMCacheAdapterFactory`. Do not create a parallel caching system.
  - **Static-First Caching Topology**: Dynamic variables (Role prompts) MUST be injected absolutely at the end of the payload sequence to maintain the Provider-Agnostic Prefix Hash survival.
  - **Fail-Fast Error Routing**: Handle Cache Expired states dynamically via cache-miss fallbacks rather than crashing the DAG.
  - **Race Condition Guard**: Cache teardown `try...finally` MUST reside at the Orchestrator level, strictly wrapping the `asyncio.TaskGroup`.

### 3. File Modifications & Sequence

#### A. Caching Interface & Factory (Core Infrastructure)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\services\llm_task_executor.py]`
- **CRITICAL BUG FIX (Early Teardown)**: Remove the `finally` block inside `execute_structured_task` that calls `LLMCachingService.teardown_workflow_caches`. Because this executor runs inside parallel `asyncio.TaskGroup` loops (e.g., in TDA Engine), the first task to complete currently destroys the global cache for all other parallel tasks, causing cascading 404 Cache Expired errors. Teardown MUST be hoisted to the orchestrator layer.

#### B. Orchestrator Floodgate Execution (Business Logic)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\services\orchestrator\enriched_dag_executor.py]` (and `tda_engine.py`)
- **Pre-Floodgate Upload (Cache Pre-Warming)**: Before entering the `asyncio.TaskGroup` in `EnrichedDagExecutor.execute_graph` (or `batch_evaluation_callback`), invoke `LLMCachingService.pre_cache_document()` to upload the global source text once.
- **Orchestrator Teardown**: Wrap the `TaskGroup` (or the entire DAG evaluation) inside a `try...finally` block. Inside the `finally`, call `LLMCachingService.teardown_workflow_caches(execution_id)`.

#### C. Caching Service (Adapter Delegation)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\llm\caching_service.py]`
- Implement `pre_cache_document()` to lock and create the provider-specific context cache explicitly.
- Ensure the caching layer seamlessly injects the active `cache_id` based on `workflow_run_id` / `execution_id` so `LLMClient` doesn't need signature parameters drilled down through every layer.

#### D. Provider Adapters (Cache-Miss Fallback)
**`TARGET (Modify)`**: `@[c:\src\quorum\backend_v2\llm\client.py]` or Adapter Layer
- Ensure 404 Context Not Found or Cache Expired exceptions automatically trigger a cache-miss fallback, instructing the provider to transmit the full payload natively.

### 4. Integration Checkpoint Plan
- Run full UI Execution pipeline observing Vertex/OpenAI traces to ensure perfect `Context Hit` tracking without token duplication. 

### 5. Destructive Operation Inventory
- No direct file deletions planned, but cache handling overrides in local nodes will be removed.

### 6. Documentation & Knowledge Item Mandate
- **Docs**: Document composite hash signatures in `docs/architecture/`.
- **KI**: Ensure `ki_provider_agnostic_caching.md` correctly details Orchestrator-level teardown requirements.

### 7. Testing & Quality Gate Plan
- **Coverage Prerequisite**: Baseline testing for `dag_executor.py` and `LLMTaskExecutor`.
- **Unit Testing**: Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test`.
- **Mock Cache TTL**: Add mock tests in `test_dag_executor.py` simulating mid-flight cache expiration and verifying fallback payload injection.

---
# Session Handover Context
Execute this plan as Phase 4 of Epic 107. Follow Tier 2 instructions.
