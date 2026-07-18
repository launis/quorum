# EPIC 103: TDA Best-Of-Three Flash Architecture

## 1. Goal Description
The current Quorum Phase 3 execution (specifically downstream TDA and Fact-checking matrices) relies on sequential processing using the heavy `gemini-2.5-pro` model. Due to strict Google Cloud API quotas (e.g., 5 RPM), the system is artificially throttled using a global 12-second Pacing Lock. This creates an unacceptable bottleneck where even parallelized atoms (e.g., 13 atoms) take several minutes to process.

**Objective**: Eliminate the Pacing Lock bottleneck by shifting the downstream matrix evaluation to `gemini-2.5-flash` and executing 3 parallel evaluations per atom using `asyncio.TaskGroup`. The final truth state will be determined by a deterministic 2/3 Majority Vote (`resolve_majority_vote`), achieving massive concurrency, >98% consistency, and zero-crash fault tolerance.

## 2. Architectural Impact & Safeguards
- **Data Flow (Producer -> Consumer)**: The `AtomFlatteningHook` (Producer) flattens semantic atoms. The `EnrichedDagExecutor` (Consumer) routes these atoms to the `ExtractiveSensorService` for boolean evaluation. Instead of one API call per atom batch, the sensor service will dispatch 3 parallel calls per batch.
- **Fail-Fast & Resilience**: The `asyncio.TaskGroup` must catch and tolerate up to one network timeout (`503` or `429`) per chunk. If two calls succeed, the consensus can still be formed.
- **Lexical Anchoring**: Before a `PASS` vote is accepted, any extracted `source_quote` MUST be physically verified against the source text using `str.find` (NOT fuzzy matching — `RapidFuzz` is architecturally banned per `strict_physical_anchoring_mandate`). Hallucinated quotes cast an immediate `FAIL` vote.
- **No Legacy Constraints**: We do not maintain fallback support for single-shot processing in this pipeline. The Best-of-Three Flash pipeline is the absolute Single Source of Truth for TDA analysis.

## 3. Implementation Phases

### Phase 0: Model Registry & Pacing Lock Resolution (CRITICAL PRE-CONDITION)
- **Problem**: The current `pacing_delay_vertex_seconds = 12` in `settings.py` enforces a Redis-backed lock between ALL Vertex AI calls. Firing 3 Flash calls in parallel would serialize them (12s + 24s = 36s per atom), defeating the entire purpose.
- **Solution**: Define a new Flash strategy in the Model Registry (`seed_data.json` → `model_registry.strategies`) with a high `rpm_limit` (e.g., 1000 RPM for Flash). The existing `base_adapter.py` already supports RPM-driven dynamic pacing (`delay = 60.0 / float(rpm_limit)`), which calculates to ~0.06s delay — effectively eliminating the bottleneck without code changes to the adapter.
- **Required Config**:
  - Strategy name: e.g., `"flash-ensemble"` or `"fast-ensemble"`
  - Model: `vertex_ai/gemini-2.5-flash`
  - `rpm_limit`: 1000 (or per actual Google Cloud quota)
  - `tpm_limit`: as per quota
  - Context Caching: ENABLED (the prompt is identical across all 3 calls — perfect cache candidate)

### Phase 1: Parallel Task Dispatcher (`ExtractiveSensorService`)
- **Target File**: `backend_v2/services/orchestrator/extractive_sensor_service.py` — specifically the `evaluate_atom_boolean_batch()` method (NOT `dag_executor.py`, which handles macro-level workflow orchestration).
- Replace the single `executor.execute_structured_task()` call with an `asyncio.TaskGroup` that dispatches three identical prompts targeting the Flash strategy.
- **Micro-Semaphore Exemption** (per `ensemble_parallel_evaluation_mandate` in `05_llm_architecture.md`): The Best-of-Three ensemble MUST use a **local** `asyncio.Semaphore(3)` independent of the global `max_concurrent_llm_steps = 10` macro semaphore. Without this, firing 3 calls per atom within a batch of 15 atoms would require 45 simultaneous semaphore slots — causing **deadlock** against the global limit of 10.
- Suppress single-node API timeouts (Dead Letter Queue routing for individual failed threads) without crashing the entire TaskGroup.

### Phase 2: Consensus Resolver (`resolve_majority_vote`)
- Implement a deterministic `resolve_majority_vote(results: list[DTO]) -> DTO` function in the evaluation service layer.
- The logic must compare the boolean outcomes (e.g., `PASS`/`FAIL` or `contextual_override`).
- If at least 2 out of 3 models agree on the core assertion, that result is elected as the final state.
- Handle tie-breakers or complete failures (e.g., 2 API timeouts = 1 successful response = insufficient consensus -> trigger `AppException` or DLQ).

### Phase 3: Strict Lexical Gatekeeping
- Extend the existing physical anchoring logic (per `strict_physical_anchoring_mandate`) in the `TopologicalEvaluator` or Matrix Hooks to enforce `str.find` validation on the elected consensus result.
- If the elected consensus contains a hallucinated quote, it must instantly fail validation (`SemanticEvidenceError`) to preserve empirical audit integrity.

### Phase 4: Audit & Testing
- **Automated Tests**: Write Pytest cases mocking the `gemini-2.5-flash` responses using `backend_v2/llm/mock.py`. Test the 2/3 consensus logic, the 1-fail resilience, and the 2-fail crash scenario.
- **Performance Profiling**: Ensure the RPM-driven dynamic pacing is correctly applied for the Flash strategy, effectively bypassing the 12-second static Pacing Lock.

## 4. Required User Review
- Are there specific matrices or blocks that should *still* use the `gemini-2.5-pro` model, or can all TDA/Falsifier downstream tasks be migrated to Flash?
- What is the actual Google Cloud RPM quota for `gemini-2.5-flash`? This determines the `rpm_limit` for Phase 0.
