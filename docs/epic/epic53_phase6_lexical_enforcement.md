# EPIC 53 Phase 6: Strict Lexical Enforcement (Trace-to-State)

## Objective
Eradicate the remaining 9.1% execution variance (haamuvarianssi) in the TDA pipeline by enforcing absolute parity between the LLM's `reasoning_trace` and the final `exact_quote`.

## Root Cause Analysis
The current `AnchorValidationService` only validates if `exact_quote` exists within the `source_text`. It ignores the LLM's `reasoning_trace`. This allows the LLM to commit Sycophancy Bypasses:
1. **Trace Contradiction**: LLM concludes `[5. VALIDATION DECISION: Fail]` but populates `exact_quote` anyway.
2. **Empty Anchor**: LLM admits `[2. SYNTACTIC ANCHOR: none]` but passes the validation.
3. **Hallucinated Anchor**: LLM invents a non-existent anchor to pass validation.

Per `the_zero_compromise_pledge` and `the_duct_tape_ban`, we MUST NOT silently mutate the data to `None` to patch these errors. We MUST enforce a Fail-Fast architecture by raising `SemanticEvidenceError` and pushing the LLM into the Self-Healing loop.

## Architectural Mandates
- **Strict Execution Mode**: This must be executed via `/tier2-hardening-backend`.
- **Fail-Fast**: Any contradiction must raise `SemanticEvidenceError`.

## Implementation Plan

### Step 1: Upgrade `AnchorValidationService`
**File**: `backend_v2/services/orchestrator/anchor_validation_service.py`

Modify `validate_evidence` to accept both `exact_quote` and `reasoning_trace` (or the whole dict/model).
Implement three strict checks before the fuzzy match:

1. **Trace Contradiction Ban**:
   If `[5. VALIDATION DECISION: Fail]` is in the trace AND `exact_quote` is not empty:
   `raise SemanticEvidenceError("Logical contradiction: Trace concluded Fail, but exact_quote was populated.")`

2. **Empty Anchor Ban**:
   If `[2. SYNTACTIC ANCHOR: none]` or `N/A` is in the trace AND `exact_quote` is not empty:
   `raise SemanticEvidenceError("Anchorless Extraction: Cannot pass validation without a physical syntactic anchor.")`

3. **Lexical Reality Ban (Anti-Hallucination)**:
   - Parse the anchor from the trace using Regex (e.g., `\[2\. SYNTACTIC ANCHOR:\s*'([^']+)'\]`).
   - If an anchor is found, run `fuzzy_match(src_text, parsed_anchor)`.
   - If the anchor is not in the source text:
   `raise SemanticEvidenceError(f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text.")`

### Step 2: Integrate Trace into `LLMTaskExecutor`
**File**: `backend_v2/services/llm_task_executor.py`

Update the `validate_recursive` function.
Instead of only sending the string value (`v`) of `exact_quote` to the validation service, it must also extract the `reasoning_trace` (or `mechanical_trace`) from the same dictionary level and pass it to `AnchorValidationService.validate_evidence`.

### Step 3: Run Audit Loop
**Command**: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/services/llm_task_executor.py --test`
Verify that no `DeprecationWarning` or typing errors exist.
