# Phase 3: Extend Existing Physical Anchoring

Source: Epic Phase 3, Step 4 (EPIC_102_structured_provenance)

This plan modifies the `AnchorValidationService` to perform a Pre-Flight Provenance Check before proceeding to strict lexical validation.

## Target Files (Modify)
- `backend_v2/services/orchestrator/anchor_validation_service.py`
- `backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`

## Context Files (Read-Only)
- `backend_v2/exceptions.py`
- `backend_v2/models/enums.py`

## Implementation Steps

### 1. `backend_v2/services/orchestrator/anchor_validation_service.py`
**Changes**:
- Extract the core lexical threshold and fuzzy checking logic (Entropy Gate, RapidFuzz score, and Coverage Safety Net) from `validate_evidence` into a new static helper method: `_is_lexically_valid(quote: str, norm_quote: str, norm_text: str, strictness_level: int, locale: str | None) -> bool`.
- Refactor the main `validate_evidence` extraction loop to use this new helper method to prevent code duplication (SSOT mandate).
- Inside the `validate_evidence` method, after handling `contextual_override` and limits, but **BEFORE** the trace validation blocks:
- Add a new block for `Pre-Flight Provenance Check`:
  - Use `re.findall(r"<user_payload>(.*?)</user_payload>", pdf_text, re.IGNORECASE | re.DOTALL)` to find all explicitly tagged user text.
  - If any `<user_payload>` tags exist, concatenate the matches into a string `allowed_source_text` using a delimiter like `" \n\n ".join(matches)` to prevent boundary contiguity leaks.
  - Normalize this `allowed_source_text` using `AnchorValidationService.normalize_text_with_mapping(allowed_source_text)` (disregard the mapping).
  - Iterate over `exact_quotes`:
    - Normalize each `quote` via `normalize_text_with_mapping`.
    - Pass the quote to the new `_is_lexically_valid(...)` helper, checking against `norm_allowed_source`.
    - If the helper returns `False`, raise a `SemanticEvidenceError` with the exact message: `"PROVENANCE_VIOLATION: Quote breached structured provenance boundary"`.
- Do not modify the original `pdf_text` passed down to the remaining validation logic so that the `index_map` offsets are perfectly preserved.

### 2. `backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py`
**Changes**:
- Add a test `test_anchor_validation_provenance_violation`:
  - Set `pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"`
  - Set `exact_quotes = ["Some AI generated text about cats"]`
  - Assert that calling `AnchorValidationService.validate_evidence` raises `SemanticEvidenceError` with match `"PROVENANCE_VIOLATION"`.
- Add a test `test_anchor_validation_provenance_success`:
  - Use similar `pdf_text`.
  - Set `exact_quotes = ["Only this text is valid."]`
  - Assert that `validate_evidence` succeeds and returns the quote.
- Add a test `test_anchor_validation_no_tags_fallback`:
  - Set `pdf_text = "This is a normal document without XML tags."`
  - Set `exact_quotes = ["normal document"]`
  - Assert that it succeeds (when no `<user_payload>` tags exist, the entire document is allowed).

## Testing & Quality Gate Plan
- Unit tests to be added as described above.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test`
- Run `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_anchor_validation_service.py --test`
- Ensure 90%+ code coverage for the service.

## Architectural Invariants
- `universal_fail_fast`: We are ensuring data provenance fail-fast.
- `strict_physical_anchoring_mandate`: We preserve the mandatory `str.find` Primary Gate by not mutating `pdf_text` indices.

## Session Handover
The execution of this plan will fulfill the remaining code modification for Phase 3. After testing, execute the remaining audits and semantic coverage checks defined in the tracker.
