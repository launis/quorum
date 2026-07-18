# EPIC 103: TDA Best-Of-Three Flash Architecture

## 1. Goal Description
The current Quorum Phase 3 execution (specifically downstream TDA and Fact-checking matrices) relies on sequential processing using the heavy `gemini-2.5-pro` model. Due to strict Google Cloud API quotas (e.g., 5 RPM), the system is artificially throttled using a global 12-second Pacing Lock. This creates an unacceptable bottleneck where even parallelized atoms (e.g., 13 atoms) take several minutes to process.

**Objective**: Eliminate the Pacing Lock bottleneck by shifting the downstream matrix evaluation to `gemini-2.5-flash` and executing 3 parallel evaluations per atom using `asyncio.TaskGroup`. The final truth state will be determined by a deterministic 2/3 Majority Vote (`resolve_majority_vote`), achieving massive concurrency, >98% consistency, and zero-crash fault tolerance.

## 2. Architectural Impact & Safeguards
- **Data Flow (Producer -> Consumer)**: The `AtomFlatteningHook` (Producer) flattens semantic atoms. The `EnrichedDagExecutor` (Consumer) routes these atoms to the `ExtractiveSensorService` for boolean evaluation. Currently, `evaluate_atom_boolean_batch()` fires **one** `executor.execute_structured_task()` call per batch of up to `sensor_batch_size=15` atoms. The Bo3 architecture wraps this **entire batch call** — firing 3 identical batch prompts and voting on the merged results per `tda_id`.
- **Fail-Fast & Resilience**: Individual Bo3 tasks MUST NOT raise exceptions into the `asyncio.TaskGroup`. Each task MUST be wrapped in an internal `try/except` that catches transient errors (`_is_transient_llm_error`) and returns a `None` sentinel instead. The TaskGroup only sees successful results or sentinels. If ≥2 valid results exist, consensus is formed. If <2 valid results exist, the atoms are marked `SYSTEM_ERROR` (DLQ routing), NOT `AppException` — to prevent crashing the entire execution tree.
- **Lexical Anchoring**: Before a `PASS` vote is accepted, any extracted `source_quote` MUST pass the Tiered Lexical Validation per `strict_physical_anchoring_mandate`: (1) Primary Gate: `str.find` on normalized strings (MANDATORY), (2) Entropy Gate: quotes <10 chars require 100% exact match, (3) Fuzzy Fallback: RapidFuzz permitted ONLY when Primary Gate fails, quote >10 chars, and strictness <100. Note: RapidFuzz is UNRESTRICTED for non-forensic pre-flight evaluation in `ExtractiveSensorService._fuzzy_match()`. Hallucinated quotes cast an immediate `FAIL` vote.
- **No Legacy Constraints**: We do not maintain fallback support for single-shot processing in this pipeline. The Best-of-Three Flash pipeline is the absolute Single Source of Truth for TDA analysis.

## 3. Implementation Phases

### Phase 0: Model Registry & Pacing Lock Resolution (CRITICAL PRE-CONDITION)
- **Problem**: The current `pacing_delay_vertex_seconds = 12` in `settings.py` enforces a Redis-backed lock between ALL Vertex AI calls. Firing 3 Flash calls in parallel would serialize them (12s + 24s = 36s per atom), defeating the entire purpose.
- **Existing Infrastructure**: A `"fast"` strategy already exists in `seed_data.json` using `vertex_ai/gemini-2.5-flash` with `rpm_limit: 100`. The `apply_provider_pacing()` function in `base_adapter.py` already supports `rpm_limit`-driven dynamic pacing (`delay = 60.0 / float(rpm_limit)`).
- **Decision (RESOLVED)**: We will exclusively reuse the existing `"fast"` strategy (`vertex_ai/gemini-2.5-flash` with `rpm_limit: 100`). No new strategy is needed. The `apply_provider_pacing()` function in `base_adapter.py` will dynamically pace the ensemble calls.
- **Config Sovereignty**: Add the following settings to `backend_v2/settings.py` (accessed via `get_settings()` per the global settings import rule):
  - `ensemble_parallelism: Annotated[int, Field(description="Number of parallel Bo3 calls")] = 3`
  - `ensemble_min_consensus: Annotated[int, Field(description="Minimum agreeing votes for consensus")] = 2`
  - `ensemble_strategy_name: Annotated[str, Field(description="Model Registry strategy for ensemble")] = "fast"`

### Phase 1: Parallel Task Dispatcher (`ExtractiveSensorService`)
- **Target File**: `backend_v2/services/orchestrator/extractive_sensor_service.py` — specifically the `evaluate_atom_boolean_batch()` method (NOT `dag_executor.py` or `enriched_dag_executor.py`, which handle macro-level workflow orchestration).
- **Bo3 Wrapping Level**: The Bo3 wraps the **entire batch call**. The same `prompt` (containing all N atom claims) is sent 3 times to the Flash model. 
- Replace the single `executor.execute_structured_task()` call with an `asyncio.TaskGroup` that dispatches `get_settings().ensemble_parallelism` (default: 3) identical calls to a helper function `_single_ensemble_call`.
- **Helper Responsibilities (`_single_ensemble_call`)**: This inner async function must:
  1. Call `executor.execute_structured_task()` targeting the `ensemble_client`.
  2. Perform the `AliasEngine` hydration mapping (converting `BatchEvaluationResponse` into the `dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]`).
  3. Catch transient network errors (`_is_transient_llm_error` from `backend_v2.llm.provider` OR `AgentExecutionError`) and return `None` instead of raising, shielding the `TaskGroup` from cascading cancellation.
- **Micro-Level Concurrency Mandate**: Per the `ensemble_parallel_evaluation_mandate` rule in `05_llm_architecture.md`, you MUST implement a localized `asyncio.Semaphore(get_settings().ensemble_parallelism)` inside `evaluate_atom_boolean_batch()` to wrap the `_single_ensemble_call` dispatch. This Micro-Level Concurrency Exemption prevents the Best-of-3 ensemble from deadlocking against the global macro-level limits managed by the TopologicalEvaluator.
- **Ensemble LLM Client (DI Simplification)**: Because Phase 4 updates the macro-level step to also run on `"fast"`, the `client: LLMClient` already passed into `evaluate_atom_boolean_batch()` is already utilizing the `"fast"` strategy. Therefore, you MUST simply reuse this existing `client` for the Bo3 parallel calls. Do NOT instantiate a separate `ensemble_client` or introduce complex dependency injection.

### Phase 2: Consensus Resolver (`resolve_majority_vote`)
- **Location**: Implement as a `@staticmethod` on `ExtractiveSensorService` in `extractive_sensor_service.py` (co-located with the evaluation logic).
- **Signature**: `resolve_majority_vote(expected_tda_ids: list[str], results: list[dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]] | None]) -> dict[str, tuple[ExecutionStatus, str | None, dict[str, str]]]`
- **Logic**: For each `tda_id` in `expected_tda_ids`, tally the exact `ExecutionStatus` votes across the valid (non-None) result dicts. If any single status achieves ≥ `get_settings().ensemble_min_consensus` (default: 2) votes, elect that status. Use the reasoning and quotes from the first agreeing vote. (CRITICAL RED-TEAM FINDING: You MUST iterate over `expected_tda_ids`, not just the keys present in `results`, to ensure that if an LLM hallucinates and silently drops an atom, it is correctly flagged as missing).
- **Insufficient Consensus & DLQ Routing (CRITICAL)**: If no single status achieves the minimum consensus for a `tda_id`:
  1. **Transient API Failure Split (< 2 valid results total)**: If the lack of consensus is due to transient API timeouts (e.g., 2 of 3 calls returned `None`), `resolve_majority_vote` MUST NOT swallow the failure into a `SYSTEM_ERROR`. Doing so would trick the Arq worker into thinking the step succeeded (with DLQ output) and bypass the built-in retry loop. You MUST raise an `AgentExecutionError` (or similar transient exception) so that the `EnrichedDagExecutor` catches it as a transient error and triggers an Arq background retry.
  2. **Semantic Split or Hallucinated Drop**: If the API succeeded but the votes are split (e.g., 1 PASS, 1 FAIL, 1 NEEDS_REVIEW) or the LLM dropped the key from its payload, mark the atom as `ExecutionStatus.SYSTEM_ERROR` with reasoning `"INSUFFICIENT_CONSENSUS"`. This routes to DLQ for manual review.

### Phase 3: Strict Lexical Gatekeeping
- The existing `AnchorValidationService.validate_evidence()` already enforces Tiered Lexical Validation per `strict_physical_anchoring_mandate`. No new validation logic is needed.
- **Integration Point**: After `resolve_majority_vote` elects a consensus, any `source_quote` fields in the elected result MUST pass through `AnchorValidationService.validate_evidence()` before being accepted. This is already handled downstream by the existing `scoring.py` hooks. No changes required here unless the Bo3 introduces a new quote extraction path.
- If the elected consensus contains a hallucinated quote, the existing `SemanticEvidenceError` mechanism preserves empirical audit integrity.

### Phase 4: Audit & Testing
- **Automated Tests**: Write Pytest cases in `tests/unit/services/orchestrator/test_extractive_sensor_service.py` mocking the `gemini-2.5-flash` responses using `backend_v2/llm/mock.py`.
  - Test the 2/3 consensus logic (3 valid results, 2 agree → elect majority).
  - Test the 1-fail resilience (1 transient timeout → 2 valid results → consensus still formed).
  - Test the 2-fail transient bubble-up scenario (2 transient timeouts → only 1 valid result → exception raised to Arq).
  - Test the missing-key DLQ scenario (API succeeds, but LLM hallucinates and drops a TDA ID -> `SYSTEM_ERROR`).
- **Performance Profiling**: Ensure the RPM-driven dynamic pacing is correctly applied for the ensemble strategy, effectively bypassing the 12-second static Pacing Lock.

## 4. Required User Review
- **Strategy Reuse**: (RESOLVED) The existing `"fast"` strategy will be reused exclusively.
- **Pro vs Flash Scope**: (RESOLVED) All Phase 3 TDA/Falsifier downstream tasks (e.g., Analyst, Falsifier, Fact Checker) MUST have their `model_strategy` updated to `"fast"` in `seed_data.json` (lines 8019-8972).
  - **Architectural Justification**: Although the architecture natively supports running the macro-level step on Pro while executing the micro-level Best-of-Three ensemble on Flash (via two completely separate `LLMClient` instances), keeping the macro-level on Pro (`"reasoning"` or `"strict"`) triggers the global 12-second Vertex AI Pacing Lock for the step's primary execution. To truly eliminate the pacing bottleneck as mandated by this Epic, both macro and micro levels must utilize Flash.
- **Actual RPM Quota**: (RESOLVED) The existing quota is sufficient to reuse the `"fast"` strategy at `rpm_limit: 100`.
