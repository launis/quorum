# Implementation Plan: Phase 4 - Validation and Scoring Hardening

## Goal
Harden the post-flight validation and scoring logic in the backend by implementing a length-weighted hybrid quote matching threshold, adding crash-protection for steps that contain only indeterminate results, and extending prompt compiler tests.

## Proposed Changes

---

### Component: Anchor Validation Service

#### [MODIFY] [anchor_validation_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/anchor_validation_service.py)
- **Changes**:
  - In `validate_evidence`, replace the simple `fuzz.partial_ratio` fallback with a length-weighted hybrid validation logic:
    ```python
    # Choose fuzzy algorithm based on length of the normalized quote
    if len(norm_quote) < 30:
        # Short quotes: enforce strict partial_ratio for contiguous matches (contiguity-guard)
        score = fuzz.partial_ratio(norm_quote, norm_pdf)
    else:
        # Long quotes: allow token_set_ratio to accommodate word ordering / Finnish morphological conjugations
        score = fuzz.token_set_ratio(norm_quote, norm_pdf)
    ```
  - *(Source: Epic Section 2.10)*

---

### Component: Scoring Hooks

#### [MODIFY] [scoring.py](file:///c:/src/quorum/backend_v2/hooks/scoring.py)
- **Changes**:
  - In `apply_scoring_logic_hook`, add a safety net to prevent crashes when all matrices are skipped (e.g., all resolved as `[INDETERMINATE]`):
    ```python
    if count == 0:
        # Check if the zero count is due to valid INDETERMINATE matrices
        is_valid_indeterminate = False
        for _, v in lookup_ctx.items():
            if isinstance(v, dict) and "[INDETERMINATE]" in str(v.get("justification", "")):
                is_valid_indeterminate = True
                break
        
        # Also check within steps payload if present
        if not is_valid_indeterminate and "steps" in lookup_ctx and isinstance(lookup_ctx["steps"], list):
            for step_val in lookup_ctx["steps"]:
                payload = step_val.get("payload") if isinstance(step_val, dict) else getattr(step_val, "payload", None)
                if isinstance(payload, dict):
                    for _, v in payload.items():
                        if isinstance(v, dict) and "[INDETERMINATE]" in str(v.get("justification", "")):
                            is_valid_indeterminate = True
                            break
                    if is_valid_indeterminate:
                        break

        if is_valid_indeterminate:
            logger.warning("[ScoringHook] All matrices are INDETERMINATE. Skipping aggregation.")
            indet_result = {
                "total_score": None,
                "final_score": None,
                "penalties_applied": penalties,
                "aggregation_status": "INDETERMINATE - Cognitive Collapse / Quality Check Failed",
            }
            return HookResult(success=True, state_delta={"scoring_result": indet_result})
    ```
  - *(Source: Epic Section 2.6)*

---

### Component: Prompt Compiler Integration Tests

#### [MODIFY] [test_prompt_compiler.py](file:///c:/src/quorum/backend_v2/tests/integration/test_prompt_compiler.py)
- **Changes**:
  - Add `contrastive_example` to `mock_matrix_block`'s assertions.
  - Assert that `<RULE_CALIBRATION_EXAMPLES>` and the `<EXAMPLE>` tags containing the contrastive text are properly compiled and present in the returned XML rubrics.
  - *(Source: Epic Section 2.6b)*

## Hardening Constraints
- **Rule 18 (`rfc7807_dual_reporting_strict`)**: Translate all caught validation exceptions to `AppException`.
- **Rule 20 (`the_self_healing_ban`)**: Do not use regex to correct validation payloads on-the-fly.

## Verification Plan

### Automated Tests
Run validation, scoring hook, and compiler integration tests:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py backend_v2/hooks/scoring.py backend_v2/tests/integration/test_prompt_compiler.py --test
```

### Documentation Update
Update [docs/architecture/reporting_and_display_theory.md](file:///c:/src/quorum/docs/architecture/reporting_and_display_theory.md) describing how indeterminate matrix hooks aggregate calculations.

## Session Handover
To execute this plan in the next session:
```powershell
/tier2-execute --target docs/epic/tasks_system2_variance_analysis_final_interventions/phase4_validation_and_scoring.md
```
