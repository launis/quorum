# Phase 2.1: GECL Prompts & Atomizer Pipeline

## Goal
Implement the Global Entity/Concept Logic (GECL) extraction and Two-Pass Atomization. Build the Phase 0 Map-Reduce for global concepts and Phase 1 Local Chunk Extraction.

## Context (Read-Only)
- `backend_v2/services/orchestrator/prompt_compiler.py`

## Target (Modify)
- `[MODIFY] backend_v2/services/orchestrator/atomizer.py` (or `[NEW] backend_v2/services/orchestrator/two_pass_atomizer.py`)
- `[NEW] backend_v2/services/orchestrator/prompts/atom_extraction.py`
- `[MODIFY] backend_v2/tests/unit/services/orchestrator/test_atomizer.py`

## Destructive Operation Inventory
- Refactoring the legacy single-pass `atomizer.py` (if it exists) to the Two-Pass architecture. Retain deprecated proxies if other systems depend on the old interface during migration.

## Architectural Rules Injected
- **01-python-backend.md**: De-Generator Mandate (No XML tags in LLM behavior strings directly). High-Fidelity Prompting (use `<execution_parameters>` tags).
- **Epic 92 Specific**: Reason-then-Format Mandate (LLM outputs reasoning before structured metadata).

## Implementation Steps
1. **Prompt Structures (`atom_extraction.py`)**:
   - Define constants for Phase 0 (Global Ontology Extraction): Instruction to extract `GlobalOntologyMap` (entities, macro-rules) from document chunks.
   - Define constants for Phase 1 (Local Atom Extraction with Anaphora Resolution): Instruction to extract atoms (`ExtractedAtom`) utilizing the injected `GlobalOntologyMap` to resolve implicit pronouns and references.
2. **Two-Pass Pipeline (`atomizer.py` or `two_pass_atomizer.py`)**:
   - Implement Phase 0 logic: Iterate through chunks, extract entities/rules, and deduplicate them into a `GlobalOntologyMap`.
   - Implement Phase 1 logic: Inject `GlobalOntologyMap` into the Prompt Compiler context for each chunk. Request `ExtractedAtom` objects using `LLMTaskExecutor.execute_structured_task()`.
   - Connect the output to `AliasEngine` (to be fully integrated in 2.2) to map opaque `tda_id` fields instead of returning raw UUIDs from the LLM.
3. **Tests (`test_atomizer.py`)**:
   - Mock LLM responses (Live LLM calls are strictly forbidden in Pytest; use `mock.py`).
   - Test Phase 0 global entity map extraction.
   - Test Phase 1 local extraction receiving the ontology map.

## Testing & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/atomizer.py --test`
- Verify prompt schemas via `schema_factory` mock logic.

---
**Session Handover**
To execute this Epic iteratively, start a NEW chat session and run the /tier5-resume command found at the bottom of your tracker.
