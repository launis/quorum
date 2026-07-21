# EPIC 108: Cognitive Pagination & Semantic Anchor Extraction (Atomizer NLP Optimization)

## 1. Objective
Eradicate physical string chunking during Atom Extraction (`TwoPassAtomizer.py`) to eliminate Context/Recall collapse, improve LLM comprehension (cognitive performance), and maximize Context Cache utilization.

## 2. Background & Problem Statement
Currently, the pipeline splits large documents physically (e.g., via `chunk.split("\n\n")`). This mechanical truncation destroys semantic integrity across chunk boundaries. When the LLM processes these disjointed chunks, it loses access to global context (such as pronouns or acronyms defined earlier in the document), leading to hallucinations or missing information during extraction. Furthermore, fragmented chunks prevent efficient utilization of a unified Context Cache.

*Note: This initiative was originally Phase 5 of EPIC 107 but was amputated and moved here to strictly isolate cognitive NLP algorithmic changes from structural Execution Pipeline orchestrator changes, enforcing the Zero-Behavioral Change rule.*

## 3. Architectural Constraints & Modernity Gates
* **Zero Legacy State Support Mandate**: Backward compatibility for past execution states or old database runs is STRICTLY PROHIBITED. No fallback logic, schema healing, or migration code is allowed for legacy runs. All development, execution, and verification MUST start from a completely clean slate by wiping the database and running `uv run python c:\src\quorum\backend_v2\seed\run_seed.py local`.

## 4. Execution Phases

### Phase 1: Zero-Chunking Cache Pagination & Attention Steering
* **Cross-Epic Delegation (EPIC 107 Integration)**: The lifecycle management (uploading and teardown) of the Global Context Cache is STRICTLY the responsibility of the DAG Orchestrator, as defined in EPIC 107 Phase 4. The Atomizer role MUST NOT attempt to create or manage its own cache. It MUST consume the `cache_id` provided by the Orchestrator.
* **New Settings Required** (Central Config Sovereignty — `backend_v2/settings.py`):
  * `max_concurrent_llm_steps: Annotated[int, Field(description="Max parallel LLM extractions within a TaskGroup")] = 3`
* **Architecture**:
  * **Semantic Anchor Pagination**: Instead of physically splitting large documents via `chunk.split("\n\n")` (which destroys semantic integrity and prevents caching), the `TwoPassAtomizer` MUST utilize the `cache_id` of the entire unified source text (already hydrated with `[Block: src_1]`, `[Msg: chat_5]` by `AliasEngine`) provided by the EPIC 107 Orchestrator.
  * **Attention Steering (User Payload Mandate)**: The `TwoPassAtomizer` will spawn parallel extraction workers that all share the exact same `cache_id`. **CRITICAL RULE**: The dynamic instruction dictating the extraction range (e.g., *"Extract atoms ONLY from [Block: src_1] to [Block: src_20]"*) MUST NEVER be injected into the System Prompt. It MUST be appended exclusively as a `user` message at the absolute end of the sequence. Injecting dynamic variables into the System Prompt instantly changes the prefix hash, destroying the 95% Context Cache survival rate and exponentially inflating token burn.
  * **Bounded Concurrency & DLQ Routing**: The parallel extraction workers MUST be orchestrated within an `asyncio.TaskGroup` constrained by a native `asyncio.Semaphore(settings.max_concurrent_llm_steps)` to prevent HTTP 429 Thundering Herd failures. Furthermore, workers MUST trap unhandled exceptions and yield a strictly typed Dead Letter Queue (DLQ) output state. An unhandled exception in a single extraction worker MUST NOT be allowed to bubble up and cancel the entire `TaskGroup` (which would orphan all other executing parallel extractions).
  * **Contextual Preservation**: Because the entire document is resident in the cache, the LLM retains access to the global context (e.g., resolving pronouns or acronyms defined on page 1, even if the worker is assigned to extract atoms from page 15). This prevents the hallucinations caused by arbitrary line/paragraph chunking mid-dialogue.
  * **Chronological Preservation Mandate**: Because parallel extraction workers complete non-deterministically (e.g., the worker for page 10 may finish before the worker for page 1), blindly merging their outputs destroys the causal timeline of the document. To prevent this, the Pydantic DTO representing the extracted output MUST strictly enforce a `source_sequence_index: int` field (representing the chunk/pagination sequence number). The DAG Orchestrator MUST use this index to explicitly `.sort()` the aggregated list of atoms before proceeding to the next DAG step.
  * **Post-Validation & Instruction Drift Mitigation**: When the entire document is cached, the LLM is susceptible to "Instruction Drift" and may hallucinate or extract atoms from outside its assigned pagination boundary (e.g., extracting a Block 50 atom when instructed to strictly extract Blocks 1-20). The Python execution layer MUST strictly post-validate the block references of the returned atoms. Any atom referencing a block outside the assigned boundary MUST be explicitly dropped to enforce structural integrity over LLM behavioral compliance.

## 5. Verification Plan
* **Cognitive Regression Testing**: Test against complex documents containing forward/backward references (e.g. acronyms defined at the start and used at the end) to ensure context preservation.
* **Token & Cache Audit**: Verify via telemetry that the unified document is only uploaded once, and subsequent atomizer workers hit the Context Cache.
