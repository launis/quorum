# EPIC 101: RAG Pre-Flight Pipeline & Deterministic Anchoring
**Status**: APPROVED  
**Targeted Subsystem**: Backend Macro-Orchestrator (`backend_v2/services/orchestrator/`), RAG Pipeline

## 1. Problem Statement & Root Cause
During the testing of the Epic 100 DAG execution, a catastrophic architectural bottleneck was discovered. The new Micro-DAG extraction logic (`TwoPassAtomizer` and `SlidingWindowLinker` - the "väitteiden haut") was correctly implemented, but it was executed independently for *each* of the 13 UI steps. 

Because each step splits the document into 15 chunks, the orchestrator triggers 195 heavy LLM calls simultaneously. This instantly triggers `429 Resource Exhausted` rate limits on Vertex AI and stretches a 20-minute execution into a 4+ hour crawl. 

## 2. Architectural Objectives (The RAG Pipeline)
To achieve instantaneous sub-second evaluation for the 13 UI steps **without altering the UI architecture**, we must extract the heavy cognitive lifting into a dedicated RAG (Retrieval-Augmented Generation) Pipeline that runs invisibly "under the hood".

1. **RAG Pre-Flight Pipeline**: We will create an invisible "Pre-Flight" RAG phase inside the Macro-Orchestrator (`DAGExecutor`). Before the UI workflow steps even begin, this pipeline will autonomously aggregate all Matrix Block rules from the 13 steps. It will execute the `TwoPassAtomizer` Map-Reduce over the document exactly **ONCE** and store the extracted facts (`DraftAtomList`) into the `ExecutionRecord.context_variables` (The "Blackboard").
2. **Virtual Step Injection (Live UI)**: To ensure the UI is "alive" during the 2-minute RAG extraction without polluting the admin configuration, the `DAGExecutor` will automatically inject a Virtual Step (e.g., "Asiakirjan Esianalyysi") into the runtime state. It will emit `TraceEvent(event_type="progress")` against this virtual step. (Note: `state.py` must be updated to include `"progress"` in the `TraceEvent.event_type` Literal). The user sees a dedicated loading card, while the actual defined 13 steps remain `PENDING`.
3. **Pre-Hydrated Synthesis Strategy**: We will create a new strategy for all subsequent UI steps. Instead of running their own heavy Map-Reduce chunking (which caused the 429 errors), these steps will read the pre-computed RAG Blackboard. They will then make EXACTLY ONE fast LLM call per step. This single call is fed the pre-extracted facts and the step's Matrix Block, allowing the AI to write rich analytical and coaching texts without re-reading the entire document.

## 2.5 The "Dual-Input" Synthesis Model (The Map & The Encyclopedia)
To ensure the UI's deep analytical capabilities (e.g., Toulmin's Model, "Missing Context" detection, BARS scales) are preserved, the Pre-Hydrated Synthesis Strategy uses a **Dual-Input Context** approach:
1. **The Blueprint**: `PromptCompiler` imports the step's Matrix Block rules exactly as defined in the UI. No UI logic is lost.
2. **The Map (`GlobalAtomBlackboard`)**: The AI is fed the pre-extracted facts (atoms). It does not need to scan the document, it just reads this "map" of claims.
3. **The Encyclopedia (Context Cache)**: The raw, 50-page source document (`$inputs.product_text`) is still loaded invisibly into the Vertex AI Context Cache. This acts as a free, instantaneous "encyclopedia" the AI can glance at if it needs to find "missing context" or deep background for its coaching tips.

**Mathematical Impact:**
- **Old Architecture:** 15 map-reduce chunks * 13 steps = **195 concurrent calls**. This caused instantaneous 429 Rate Limit (Pacing Lock) crashes.
- **Epic 101 Architecture:** 15 chunks (Pre-Flight) + 13 steps (Synthesis) = **28 controlled calls**. The bottleneck is completely eliminated while maintaining 100% of the cognitive depth.

## 3. High-Level Implementation Phases

### Phase 1: RAG Pre-Flight Pipeline & Virtual Step Injection
- **Component**: `backend_v2/services/orchestrator/dag_executor.py` and `backend_v2/models/state.py`
- **Cross-Boundary MANDATORY Sub-Step**: Adding `"progress"` to `TraceEvent.event_type` Literal in `backend_v2/models/state.py` REQUIRES a simultaneous Flutter Freezed model update (`TraceEvent` in `client_app_v2`) to prevent `disallowUnrecognizedKeys` crashes. This is enforced by the `cross_language_enum_parity` mandate. The `test_enum_parity.py` test MUST be updated to include the new value.
- **Logic**: Implement the RAG Pre-Flight hook before the step iteration loop. It must:
  1. Inject an ephemeral `ExecutionStepState` with a dynamically generated opaque ID (e.g., `f"stp_{uuid.uuid4().hex[:8]}"`) with status `RUNNING`. **CRITICAL UI INTEGRITY**: To prevent Flutter `AppErrorBoundary` crashes (where the UI cannot find the rule for this state), the orchestrator MUST also dynamically inject a Virtual `StepRule` into the runtime `workflow.steps` list (following the existing `sys_render_*` virtual step pattern in `dag_executor.py`) so the SDUI has a valid rendering target. This injection occurs on the in-memory `Workflow` object passed to `execute_workflow()`, NOT on any persisted blueprint.
  2. Inspect the `workflow` object to collect all `expected_inputs`. For EACH input file (e.g., `product_text`, `chat_log`), chunk it independently using the existing `ChunkingService` and run `TwoPassAtomizer` + `SlidingWindowLinker` per file. This Atomization MUST occur exclusively via `LLMTaskExecutor.execute_structured_task()` to eradicate syntactic self-healing regex loops. The LLM client MUST be resolved via `LLMClient.from_strategy("fast", repo)` (where `"fast"` is an existing strategy defined in the `seed_data.json` database) for cost-efficient parallel chunking.
  3. Execute using `asyncio.TaskGroup` constrained by `asyncio.Semaphore(settings.max_concurrent_llm_steps)`. The use of `asyncio.gather` is STRICTLY BANNED to prevent zombie tasks (straggler issue). Furthermore, if a worker node crashes in a TaskGroup, the entire DAG execution is cancelled. We must enforce Dead Letter Queue (DLQ) routing (`dlq_arq_fallback_routing`) instead of raising naked exceptions to safely isolate task failures.
  4. Emit `progress` TraceEvents tied to the virtual step dynamically during the Map-Reduce loop to keep the SSE connection alive.
  5. The extracted atoms MUST be grouped by their source file using a new strict Pydantic model: `class GlobalAtomBlackboard(BaseModel): atoms_by_input: dict[str, DraftAtomList]`. This model MUST be defined in `backend_v2/models/domain/blackboard.py` (per `strict_model_location` mandate). The `DraftAtomList` and `DraftExtractedAtom` models currently defined in `two_pass_atomizer.py` MUST be migrated to `backend_v2/models/domain/` as the SSOT during implementation. This model MUST enforce `model_config = ConfigDict(frozen=True, extra="forbid", strict=True)` to prevent in-place mutation violations. Project this Pydantic model into `context_variables["global_atoms"]` via `.model_dump(mode="json")`. **NOTE**: Cloud Storage offload via `context_variables_storage_path` is completely removed from the scope of this Epic and deferred. Typical RAG atom payloads (~50-200KB) are well within TinyDB limits.
  6. Mark the Virtual Step as `ExecutionStatus.PASSED`.

### Phase 2: Pre-Hydrated Synthesis Strategy (The Fast Path)
- **Component**: `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
- **Logic**: Implement a strategy that replaces the heavy Map-Reduce `LLMExecutionStrategy` for all analytical steps while preserving 100% of the UI's prompt configuration. It must:
  1. **Hydrate Facts**: Read the step's specific input mappings (e.g., only `$inputs.product_text`). Hydrate the Blackboard explicitly using `GlobalAtomBlackboard.model_validate(context_variables["global_atoms"])`. Extract ONLY the corresponding `DraftAtomList`s for the mapped files. This ensures steps only receive facts from the files selected in the UI.
  2. **Preserve Prompt Logic & XML Structural Sovereignty**: Use the existing `PromptCompiler` to perfectly preserve the step's Matrix rules (BARS scales, Toulmin models, XAI requirements) exactly as defined in the UI. Developers are STRICTLY BANNED from injecting raw, unstructured f-strings. The compiled prompt MUST be deterministically fenced within immutable XML boundaries (e.g., `<system_directive>`, `<user_payload>`) to prevent injection leakage and cache-busting.
  3. **Dual-Input Context (Ephemeral Caching Topology)**: Formulate a single LLM prompt that passes the raw source files (e.g., `$inputs.product_text`) into the Vertex AI Context Cache. To prevent cache-busting and FinOps cost explosions, you MUST enforce the Ephemeral Caching Topology: The System Prompt must be 100% static, and the `global_atoms` working memory MUST be injected at the absolute end inside a dynamic `<user_payload>`.
  4. **Single-Call Synthesis**: Execute EXACTLY ONE LLM call via `LLMTaskExecutor.execute_structured_task()` (routed through `LLMClient.from_strategy()` using the step's native `model_strategy`, which corresponds to existing values in the `seed_data.json` database like `"synthesis"`, `"deep"`, or `"strict"`) to generate the creative SDUI DTOs (e.g., CoachingCard, InsightCard) based on those verified facts and rules.

### Phase 3: SDUI Routing (Immutable Definition UI)
- **Component**: `backend_v2/services/orchestrator/strategies/` and `backend_v2/models/v2_core.py`
- **Logic**: Maintain the exact UI definition visual architecture while routing the engine.
  1. Add a new strictly typed Enum `class EngineOverrideStrategy(str, Enum): PRE_HYDRATED_SYNTHESIS = "PRE_HYDRATED_SYNTHESIS"` to `enums.py`.
  2. Add a new optional field to `StepRule`: `engine_override: EngineOverrideStrategy | None = None`. When set to `EngineOverrideStrategy.PRE_HYDRATED_SYNTHESIS`, `NodeExecutor` routes to the new `PreHydratedSynthesisStrategy` instead of the default `LLMNodeStrategy`. (Strict Enum mapping prevents Magic String violations).
  3. Do NOT add the RAG step to the `seed_data.json` configuration UI. The visual definition architecture remains exactly as designed. The step only appears at runtime via Virtual Injection.
  4. Map all 13 existing steps (Guard, Analyst, etc.) by setting their `engine_override` to `"PRE_HYDRATED_SYNTHESIS"` in `seed_data.json`.

## 4. Quality Gates & Red-Teaming (System 2 Safeguards)
- **State Sovereignty**: The RAG Pipeline must adhere strictly to `ki_dag_engine_dto_projection_rules.md`. It must NOT return raw Python dictionaries.
- **Fail-Fast Hydration**: If `context_variables["global_atoms"]` is missing, the `PreHydratedSynthesisStrategy` must log a structured `logger.error` with execution context (Dual-Reporting Mandate) and then crash immediately with a `DependencyError`.
- **Single-Call Mandate**: The `PreHydratedSynthesisStrategy` MUST be hardcoded to never loop or map-reduce. It must guarantee exactly 1 LLM request per step.
- **Physical Anchoring & Null Hypothesis**: The extraction pipeline MUST enforce strict O(N) physical anchoring (`str.find`) for all quotes. Fuzzy matching is strictly banned. To support facts deduced purely through logic, the AI must use the `is_logical_deduction == True` flag to intentionally force the quote to `None`.
- **Tripartite Configuration Architecture**: All configuration parameters (such as `max_concurrent_llm_steps` and `context_variables_offload_threshold_bytes`) MUST be explicitly segregated and enforced via the explicit Tripartite structure (`enums.py`, `settings.py`, `DTO blueprints`). Do not hardcode magic numbers.
- **Rogue SDK Ban**: The `PreHydratedSynthesisStrategy` MUST NOT import provider SDKs directly. All model calls MUST be routed through the mandated `LLMClient.from_strategy()` abstraction to maintain Model Agnosticism.
- **DLQ vs Duct-Tape Exception (Transient Failures)**: The Fail-Fast mandate applies strictly to logical data schema violations. However, to prevent a single transient network failure or LLM latency timeout from tearing down the entire `TaskGroup` DAG and destroying hours of valid processing, background workers MUST explicitly enforce Dead Letter Queue (DLQ) routing (`dlq_arq_fallback_routing`) for transient errors. Catching a transient error and yielding it to the DLQ is NOT considered forbidden duct-tape; it is the mandated mechanism for protecting sibling tasks while preserving forensic evidence.
