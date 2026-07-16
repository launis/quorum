# EPIC 100: Radical Speedup & DAG Scalability

## 1. Executive Summary
This Epic addresses the critical scalability bottlenecks discovered when processing large matrices and documents in the Quorum V2 engine. The implementation focuses on three primary architectural enhancements: replacing the 8192 output token limit crash with an iterative Chunk Worker for the Linker, batching micro-prompts into single LLM requests using the primary Gemini 2.5 Flash model, and intensifying deterministic Python pre-flight filtering to bypass the LLM entirely where possible.

## 2. Problem Statement
When running massive execution graphs (e.g., parsing large PDFs with hundreds of atoms), the `SlidingWindowLinker` feeds the LLM an input context that easily fits within the 2-million token limit, but expects an output graph that exceeds the model's 8192 output token ceiling. This results in truncated JSON and fatal `ValidationError` crashes (`JSONDecodeError`).

Concurrently, the Map-Reduce phase (`ExtractiveSensorService`) executes hundreds of independent True/False assertions against the LLM using the heavy primary model. Due to the Vertex AI rate limit (100 RPM), this triggers a 0.6-second exponential backoff pacing lock per claim, slowing down the extraction phase drastically.

## 3. Architectural Directives (Tier 0 Verified)

### 3.1. Reinstating the Linker Chunk Worker
To solve the Output Token vs. Input Context paradox, the `SlidingWindowLinker` will be refactored to utilize a recursive "Chunk Worker" pattern. Large datasets will be aggressively windowed, evaluated as partial sub-graphs, and then recursively reduced. This ensures no single LLM call is required to output more than 8192 tokens, maintaining the Fail-Fast Pydantic integrity.

### 3.2. Micro-Prompt Batching (Gemini 2.5 Flash)
Instead of using multiple different LLM actors or routing to a smaller model, the system will exclusively use the primary `gemini-2.5-flash` model. To bypass the 100 RPM limit and 0.6s pacing lock, the `ExtractiveSensorService` will batch multiple Boolean assertions (e.g., 10-20 atoms at a time) into a single LLM request. To prevent a single hallucination from crashing the entire batch via strict Pydantic validation, we will implement **Resilient Batch Parsing**. The backend will validate the results atom-by-atom in a loop, ensuring that if one atom fails validation, only that specific atom is marked as failed, salvaging the rest of the batch.

### 3.3. Deterministic Pre-Flight Falsification
The `ExtractiveSensorService` will adopt an aggressive `_fuzzy_match` pre-flight threshold. If the required syntactic anchors are wholly absent from the target text, the LLM will be entirely bypassed (`decided=True`), saving tens of thousands of tokens and eliminating unnecessary API calls.

## 4. Execution Phases

### Phase 1: SlidingWindowLinker Refactoring
- **Target:** `backend_v2/services/orchestrator/sliding_window_linker.py`
- **Action:** Implement Map-Reduce Chunk Worker logic to paginate the LLM generation of `LinkerResponseDTO`.

### Phase 2: Micro-Prompt Batching
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **Action:** Refactor the evaluation logic to process atoms in batches within a single LLM call, drastically reducing the number of Vertex AI queries.

### Phase 3: Aggressive Pre-Flight Tuning
- **Target:** `backend_v2/services/orchestrator/extractive_sensor_service.py`
- **Action:** Fine-tune the fallback constraints in the syntactic anchor checking to fail assertions deterministically before LLM invocation.

### Phase 4: Validation & Audit
- Run the universal quality gate `scripts/backend_audit_loop.py` to enforce strict coverage and typing.
- Run a manual end-to-end trace to verify that `JSONDecodeError` is resolved and micro-prompts execute without Vertex AI rate limits.
