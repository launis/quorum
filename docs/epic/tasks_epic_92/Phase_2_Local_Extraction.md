# Phase 2: Local Extraction & GECL (LLM Pipeline)

Source: Epic 92, Section 4 (Phase 2)

## Context (Read-Only)
- `c:\src\quorum\backend_v2\utils\alias_engine.py`

## Target (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\strategies\local_extraction_strategy.py` [NEW]
- `c:\src\quorum\backend_v2\prompts\dag_extraction.py` [NEW]
- `c:\src\quorum\backend_v2\services\global_condition_ledger.py` [NEW]

## Milestones

### 1. Global Condition & Event Ledger (GCEL)
- Implement `GlobalConditionLedger` service in `global_condition_ledger.py`.
- **Map-Reduce Phase 0**: Extract core entities, conditions, rules, and macro-events from the full document into a `GlobalOntologyMap` to resolve Cross-Chunk Amnesia.

### 2. DAG Extraction Prompts (`backend_v2\prompts\dag_extraction.py`)
- Define prompt templates using English (`required_reasoning_language = English`).
- Inject `GlobalOntologyMap` into local prompts to enable implicit anaphora resolution (e.g., resolving "It crashed" to the actual entity).
- Use proper XML fencing (`<user_payload>`) for all injected source text.

### 3. Local Sub-Graph Builder (`local_extraction_strategy.py`)
- Implement a two-pass chunk extractor.
- First pass: Extract flattened `resolved_claim` and `source_quote` atoms from chunks.
- Sub-graph mapping: Establish local dependencies between atoms in the same chunk.
- **AliasEngine Mandate**: The LLM MUST output short aliases (`a0`, `a1`). 
- **Pre-Validation Hydration**: The service MUST call `AliasEngine.hydrate_dict_list()` on the raw dict list BEFORE invoking `ExtractedAtom.model_validate(data)`, preventing validation crashes.
- Map the extracted structure to the `ExtractedAtom` and `LinkedAtomGraph` models.

## Testing & Quality Gate Plan
- **Unit Tests**: Test the hydration logic with `AliasEngine` extensively. Ensure Pydantic `ValidationError` is avoided by hydrating dicts first.
- **Mocks**: Use `polyfactory` and the LLM mock framework (`backend_v2/llm/mock.py`) to simulate LLM extraction outputs.
- **Mandate**: Run the backend audit loop (`uv run python scripts/backend_audit_loop.py`).

---
# Session Handover
To execute this phase iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker: `c:\src\quorum\docs\epic\epic_92_tracker.md`
