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

## 2. Implementation Steps

### A. Orchestrator-Level Cache Teardown
- [x] **Location**: `backend_v2/services/orchestrator/enriched_dag_executor.py`
  - Wrap the `TaskGroup` (or the entire DAG evaluation) inside a `try...finally` block.
  - Inside the `finally`, call `LLMCachingService.teardown_workflow_caches(execution_id)`.
- [x] **Location**: `backend_v2/services/llm_task_executor.py`
  - **REMOVE** the inner `try...finally` that clears the cache for Ephemeral providers, preventing early cache expiration.

### B. Pre-Caching Global Payload
- [x] **Location**: `backend_v2/llm/caching_service.py`
  - Implement `pre_cache_document()` to lock and create the provider-specific context cache explicitly.
- [x] **Location**: `backend_v2/services/orchestrator/enriched_dag_executor.py` (or `ExtractiveSensorService.batch_pre_evaluate`)
  - Before entering the `asyncio.TaskGroup`, invoke `LLMCachingService.pre_cache_document()` to upload the global source text once.

### C. Provider Cache Survival
- [x] **Location**: `backend_v2/services/orchestrator/prompt_compiler_adapter.py`
  - Ensure the `static` prompt chunk remains entirely intact across DAG atoms.

### D. Provider Adapters (Cache-Miss Fallback)
- [x] **Location**: `backend_v2/llm/client.py` or Adapter Layer
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
