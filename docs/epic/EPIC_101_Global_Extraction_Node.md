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
- **Cross-Boundary Note**: Adding `"progress"` to `TraceEvent.event_type` Literal requires a simultaneous Flutter Freezed model update (`TraceEvent` in `client_app_v2`) to prevent `disallowUnrecognizedKeys` crashes.
- **Logic**: Implement the RAG Pre-Flight hook before the step iteration loop. It must:
  1. Inject an ephemeral `ExecutionStepState` (e.g., `stp_virtual_rag`) with status `RUNNING` so the execution UI renders a card.
  2. Inspect the `workflow` object to collect all `expected_inputs`. For EACH input file (e.g., `product_text`, `chat_log`), chunk it independently and run `TwoPassAtomizer` + `SlidingWindowLinker` per file.
  3. Execute using `asyncio.TaskGroup` constrained by `asyncio.Semaphore(settings.max_concurrent_llm_steps)`. Worker crashes must yield to DLQ instead of raising naked exceptions.
  4. Emit `progress` TraceEvents tied to the virtual step dynamically during the Map-Reduce loop to keep the SSE connection alive.
  5. The extracted atoms MUST be grouped by their source file using a new strict Pydantic model: `class GlobalAtomBlackboard(BaseModel): atoms_by_input: dict[str, DraftAtomList]`, where the key is the input mapping (e.g., `$inputs.product_text`). Project this Pydantic model into `context_variables["global_atoms"]` via `.model_dump(mode="json")`. If the serialized size exceeds `settings.context_variables_offload_threshold_bytes`, offload to Cloud Storage via `context_variables_storage_path`.
  6. Mark the Virtual Step as `ExecutionStatus.PASSED`.

### Phase 2: Pre-Hydrated Synthesis Strategy (The Fast Path)
- **Component**: `backend_v2/services/orchestrator/strategies/pre_hydrated_synthesis.py`
- **Logic**: Implement a strategy that replaces the heavy Map-Reduce `LLMExecutionStrategy` for all analytical steps while preserving 100% of the UI's prompt configuration. It must:
  1. **Hydrate Facts**: Read the step's specific input mappings (e.g., only `$inputs.product_text`). Hydrate the Blackboard explicitly using `GlobalAtomBlackboard.model_validate(context_variables["global_atoms"])`. Extract ONLY the corresponding `DraftAtomList`s for the mapped files. This ensures steps only receive facts from the files selected in the UI.
  2. **Preserve Prompt Logic**: Use the existing `PromptCompiler` to perfectly preserve the step's Matrix rules (BARS scales, Toulmin models, XAI requirements) exactly as defined in the UI.
  3. **Dual-Input Context**: Formulate a single LLM prompt that injects the `global_atoms` as the primary working memory, BUT STILL passes the raw source files (e.g., `$inputs.product_text`) into the Vertex AI Context Cache (via System Prompt). This ensures the LLM can instantly cross-reference the original text if needed for deep analytical context.
  4. **Single-Call Synthesis**: Execute EXACTLY ONE LiteLLM call to generate the creative SDUI DTOs (e.g., CoachingCard, InsightCard) based on those verified facts and rules.

### Phase 3: SDUI Routing (Immutable Definition UI)
- **Component**: `backend_v2/services/orchestrator/strategies/` and `backend_v2/models/v2_core.py`
- **Logic**: Maintain the exact UI definition visual architecture while routing the engine.
  1. Add a new optional field to `StepRule`: `engine_override: str | None = None`. When set to `"pre_hydrated_synthesis"`, `NodeExecutor` routes to the new `PreHydratedSynthesisStrategy` instead of the default `LLMNodeStrategy`.
  2. Do NOT add the RAG step to the `seed_data.json` configuration UI. The visual definition architecture remains exactly as designed. The step only appears at runtime via Virtual Injection.
  3. Map all 13 existing steps (Guard, Analyst, etc.) by setting their `engine_override` to `"pre_hydrated_synthesis"` in `seed_data.json`.

## 4. Quality Gates & Red-Teaming (System 2 Safeguards)
- **State Sovereignty**: The RAG Pipeline must adhere strictly to `ki_dag_engine_dto_projection_rules.md`. It must NOT return raw Python dictionaries.
- **Fail-Fast Hydration**: If `context_variables["global_atoms"]` is missing, the `PreHydratedSynthesisStrategy` must crash immediately with a `DependencyError`.
- **Single-Call Mandate**: The `PreHydratedSynthesisStrategy` MUST be hardcoded to never loop or map-reduce. It must guarantee exactly 1 LLM request per step.
