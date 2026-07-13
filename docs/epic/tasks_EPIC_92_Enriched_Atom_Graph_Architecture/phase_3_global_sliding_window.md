# Phase 3: Global Sliding Window (The Synthesizer)

Source: Epic Phase 3, Step 3.1.2 - 3.1.4

## Objective
To tie together the disconnected `ExtractedAtom`s produced in Phase 2 into a complete `LinkedAtomGraph` by determining cross-chunk causal relationships (`depends_on`). This uses a Sliding Window algorithm to prevent "Lost in the Middle" LLM amnesia and employs the `AliasEngine` for ID hydration.

## Architectural Rules Injected
- **01-python-backend.md: AliasEngine LLM Isolation Mandate:** Raw database UUIDs (`tda_...`) must never be sent to the LLM. Use `AliasEngine` to map them to semantic aliases (`a0`, `a1`) before LLM processing, and `hydrate_dict_list()` after.
- **01-python-backend.md: Zero-Compromise Pledge:** If sliding window fails, no graceful degradation. If dependencies are unresolved (Phantom Edges), they crash to `SYSTEM_ERROR`.
- **01-python-backend.md: No Naked Dicts:** Parsed LLM outputs must be immediately validated via `LinkedAtomGraph.model_validate()`.

## Proposed Changes

### Target: `backend_v2/services/orchestrator/sliding_window_linker.py` [NEW]
- Create `SlidingWindowLinker` service.
- **Input:** `list[ExtractedAtom]`, `GlobalOntologyMap`, and spatial boundaries (`chunk_index`).
- **Algorithm:**
  - Group atoms by `chunk_index`.
  - Iterate through chunks using window size `W = settings.GRAPH_LINKER_WINDOW_SIZE` (default 4) and overlap `O = settings.GRAPH_LINKER_OVERLAP` (default 2).
  - Use `AliasEngine` to register all `tda_id`s in the window to aliases (`a0`, `a1`).
  - Construct prompt (using `Context-Aware Linker` logic: include `source_quote`s + `GlobalOntologyMap`).
  - Instruct LLM to output causal relationships as a dictionary mapping alias to list of `CausalEdge` representations (using aliases for `tda_id`).
  - Use `AliasEngine.hydrate_dict_list()` on the raw dictionary output BEFORE Pydantic validation.
  - Merge inter-chunk edges deterministically. Remove duplicates.

### Target: `backend_v2/services/orchestrator/graph_validator.py` [NEW]
- Create `GraphValidatorService` to perform deterministic topological checks.
- **Responsibilities:**
  - **Phantom Edge Isolation:** If an edge references a non-existent `tda_id`, mark the child as `SYSTEM_ERROR` (`UNRESOLVED_DEPENDENCY`).
  - **Cycle Breaker (Fail-Fast):** Use `networkx.simple_cycles()` via `await asyncio.to_thread()` to detect cyclic dependencies. Any nodes in a cycle are marked `SYSTEM_ERROR` (`CYCLIC_DEPENDENCY_DETECTED`).

### Target: `backend_v2/services/orchestrator/prompts/graph_linking.py` [NEW]
- Create LLM prompts for the sliding window linker.
- Enforce output format matching the required edge structures (via Alias mapping).

## Verification & Quality Gate
- **Unit Tests:** `tests/unit/services/orchestrator/test_sliding_window_linker.py` ensuring sliding window correctly overlaps and deduplicates edges.
- **Unit Tests:** `tests/unit/services/orchestrator/test_graph_validator.py` verifying cycle detection correctly marks nodes as `SYSTEM_ERROR` and does NOT infinite loop.
- **Universal Quality Gate:** Run `backend_audit_loop.py` to ensure strictly typed passing tests.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
