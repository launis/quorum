# Phase 2: Scoring Hook State Hoisting (EPIC 70)

## Objective
Implement state hoisting in the matrix scoring hook to extract verbatim text quotes (`exact_quote`) and override reasoning (`semantic_reasoning`) from successful evaluation atoms and push them into the workflow's intermediate `content_payload`.

## Execution Steps

### 1. Modify `matrix_scoring_hook`
**Target:** `c:\src\quorum\backend_v2\hooks\scoring.py`
- Locate `matrix_scoring_hook`.
- Add logic inside the atom iteration loop: When processing `ev_dto` (of type `AtomEvaluationItemDTO` or similar) where `final_state` evaluates to `True`, capture the quote data.
- The structure to collect: `exact_quote` (if populated) and `structural_location` & `semantic_reasoning` (if `contextual_override` is True).
- Initialize a `content_payload["atom_quotes"]` list (or dictionary keyed by `matrix_block_id` -> list of strings). 
- Note: It's best to group them by `matrix_block_id` so the BlueprintTransformer can map them to the correct matrix rows later. Store as `content_payload["atom_quotes"][block_id] = [quote1, quote2, ...]`.

### 2. Verification
- Run hook-specific unit tests (e.g. `uv run pytest tests/unit/hooks/test_scoring.py` or similar).
- Verify via log output that `content_payload["atom_quotes"]` correctly receives strings when `exact_quote` is present.

## Architectural Invariants
- **Rule 12: no_naked_dicts_in_state:** Naked dictionaries are strictly banned in state management. State projections MUST be returned as typed, structured `StepOutputDTO` or equivalent objects. (Ensure the hook state is properly encapsulated).
- **Rule 22: zero_legacy_fallback_hacks:** Legacy fallback hacks (e.g., `new_field or old_field`, `.get('key', default)`) are entirely unsupported. If a quote is missing, it simply isn't added to the array.
- **Rule 55-58 (PEP 257 & Google Style):** Every module, class, and function MUST possess a PEP 257 compliant Google-style docstring... The `Raises:` section MUST EXPLICITLY enumerate the precise Quorum `AppException` error codes. Ensure any modified functions meet this standard.
- Rely solely on explicit Pydantic properties.
