# Phase 1: CONTESTED-tilan elvytys ja matemaattinen korjaus (Contested Revitalization)

Source: Epic System 2 Variance Analysis Report (Liite 3.1)
Goal: Fix the reverse logic bug associated with the CONTESTED status and ensure the `CONTESTED` state survives the Guttman waterfall without being improperly inverted.

## Architectural Invariants (from .agents/rules & hardening.xml)
- **Zero-Compromise Pledge (Rule 1)**: No `.get("default")` fallbacks.
- **Fail-Fast Hydration (Rule 3)**: All dictionary flows must be hydrated.
- **Duct-Tape Ban (Rule 17)**: No silent suppressions of missing data.
- **Strict Dependency Injection**: No God methods.
- **Polymorphic Routing**: Logic must be based on abstract attributes.

## Proposed Changes

### Backend Orchestrator & Models

#### [MODIFY] backend_v2/models/dtos/lightweight_matrix.py (CONTEXT: None)
- **Requirement**: In `calculate_rule_satisfied()`, if `self.status == "CONTESTED"`, return a neutral non-inverted state (e.g., `0.5` or `True` without being affected by `inverse_evidence`).
- **Details**: The epic specifically states: "CONTESTED on epistemologinen tila ('epävarma'), ei looginen väittämä ('löytyi'), ja sen invertointi on looginen virhe". The code must bypass the `inverse_evidence = True` logic if the status is `CONTESTED` to prevent the Guttman waterfall from immediately failing the matrix block.

#### [MODIFY] backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py (CONTEXT: None)
- **Requirement**: Update the `resolve_majority_vote()` function to support three-tier voting (PASS, FAIL, CONTESTED).
- **Details**: 
  - Count `contested_votes` separately from `fail_votes`.
  - Implement Confidence Gating: If the calculated confidence (e.g. `chosen["confidence"] = pass_votes / len(votes)`) is `<= 0.67` (a 2-1 split), force the output status to `CONTESTED`.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/lightweight_matrix.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py --test`
- Write or update a pytest in `tests/unit/` to verify that `inverse_evidence` does NOT invert a `CONTESTED` state.
- Ensure all tests pass.

---
**Session Handover**
To execute this phase, please start a NEW chat session and run:
`/tier5-resume --target docs/epic/system2_variance_analysis_report_tracker.md`
