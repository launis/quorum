# Phase 3: Service Logic Extraction & Duck-Typing Eradication

**Objective:** Strip `AnchorValidationService` and `AliasEngine` logic from DTO validators and move it entirely to the Service layer. Eradicate all `hasattr()`, `isinstance()`, and `.get()` duck-typing from DTOs.
**Source:** @[c:\src\quorum\docs\epic\EPIC_133A_lightweight_matrix.md#L82-L107]

**Expected Target Files:**
- `@[c:\src\quorum\backend_v2\models\dtos\atom_evaluation.py]`
- `@[c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py]`
- `@[c:\src\quorum\backend_v2\models\enums.py]`
- `@[c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py]`

## Execution Steps

### Step 3.1: DTO Strictification (atom_evaluation.py)
1. **Remove Dependency Injections:** 
   - Remove `AnchorValidationService`, `AliasEngine`, and `get_lexical_fuzz_threshold` imports.
2. **Refactor `_enforce_null_hypothesis_before`:**
   - Remove all `AliasEngine` hydration logic.
   - Remove all `source_documents` and `mcp_source_texts` quote matching logic.
   - Keep ONLY the `contextual_override` mutation logic (setting `exact_quotes = []` and `used_evidence_ids = []`).
3. **Refactor `_enforce_zero_variance_protocols`:**
   - Keep the `contextual_override` validation (`len(reasoning) < 50` and `structural_location`).
   - Remove `AnchorValidationService` exact/fuzzy text matching entirely.
   - Keep ONLY the schema constraint loop that checks if any quote exceeds `_schema_max_quote_length`.

### Step 3.2: Duck-Typing Eradication (atom_evaluation.py)
1. In `LightweightExtractionAtom.evidence_found`: Replace all `hasattr()`, `isinstance()`, and `.get()` fallback logic. Assume `quote` is strictly a `LLMExtractedQuote` and use `quote.text`.
2. In `AtomEvaluationItemDTO.evidence_found`: Do the exact same strict `quote.text` enforcement.
3. In `AtomEvaluationItemDTO._enforce_zero_variance_protocols`: Use strict `quote.text` enforcement.

### Step 3.3: Bug Fix & Module Cleanup (atom_evaluation.py)
1. Delete the duplicate `truncate_chart_label` function that appears first (it lacks the split logic). Retain the robust `_truncate_chart_label`.
2. Move `import re` statements from inline validators to the global import section.

### Step 3.4: Context Injection (enums.py & atom_evaluation.py)
1. In `enums.py`, define `DEFAULT_NULL_HYPOTHESIS_BLACKLIST: frozenset[str]` containing the exact strings from the current `evidence_found` sets.
2. In `atom_evaluation.py` for both `LightweightExtractionAtom` and `AtomEvaluationItemDTO`, define a private attribute:
   `_null_hypothesis_blacklist: frozenset[str] = PrivateAttr(default_factory=frozenset)`
3. Add a new `@model_validator(mode="after")` named `_inject_context` that checks `info.context` for `"null_hypothesis_blacklist"`, and if absent, defaults to `DEFAULT_NULL_HYPOTHESIS_BLACKLIST` from `enums.py`.
4. Update both `evidence_found` properties to use `self._null_hypothesis_blacklist`.

### Step 3.5: Service Extraction (anchor_validation_service.py)
1. Add a `process_atom_evaluation(...)` static method to `AnchorValidationService` that takes a populated `AtomEvaluationItemDTO` and all relevant context keys.
2. Implement the spatial anchoring validation (previously in `_enforce_zero_variance_protocols`) inside this method, raising `ValueError` or `SemanticEvidenceError` on failure.
3. Implement the `used_evidence_ids` quote mapping (previously in `_enforce_null_hypothesis_before`). Because the input DTO is `frozen=True`, use `atom.model_copy(update={"exact_quotes": new_quotes, "used_evidence_ids": resolved_ids})` to return the hydrated DTO.

### Step 3.6: Test Migration & Quality Gate
1. Due to Duck-Typing eradication, update all tests in `test_lightweight_matrix.py` where `exact_quotes` contains raw strings (e.g. `exact_quotes=["This is an exact quote"]`) to strictly use dicts matching `LLMExtractedQuote` schema (e.g. `exact_quotes=[{"text": "This is an exact quote"}]`).
2. Run `uv run python scripts/backend_audit_loop.py backend_v2 --test` to verify full compilation and behavioral parity.

> [!IMPORTANT]
> The Context Window is now fully saturated with Tier 0 research. You MUST instruct the user to start a NEW session and run `/tier2-execute` to execute these changes.
