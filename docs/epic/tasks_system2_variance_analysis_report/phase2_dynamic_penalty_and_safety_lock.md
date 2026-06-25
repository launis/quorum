# Phase 2: Kaksiportainen turvalukko ja dynaaminen sakko (Dynamic Penalty & Safety Lock)

Source: Epic System 2 Variance Analysis Report (Liite 3.2 & 3.3)
Goal: Implement a two-stage safety lock to prevent "lazy evaluation" by the LLM, and apply localized dynamic penalties for `CONTESTED` atoms at the matrix level instead of globally.

## Architectural Invariants (from .agents/rules & hardening.xml)
- **Zero-Compromise Pledge (Rule 1)**: No silent suppressions of missing data.
- **Strict Math Display Isolation (Rule 120)**: Mathematical scoring must use explicit arrays, not display bounds.
- **Tripartite Calculation Boundary**: Keep backend computation pure.

## Proposed Changes

### Backend Scoring Hooks

#### [MODIFY] backend_v2/hooks/scoring.py (CONTEXT: None)
- **Requirement 1**: Implement localized dynamic penalty in the matrix scoring logic (`matrix_scoring_hook`). Instead of a global penalty for `CONTESTED`, apply a dynamic penalty to the specific matrix based on the number of `CONTESTED` atoms (e.g., -5% per CONTESTED atom). Use the formula: `Score(M_i) = Score(M_i) * (1 - 0.05 * N_contested)`.
- **Requirement 2**: Implement the "Cognitive Collapse" safety lock. If a matrix has strictly more than 3 `CONTESTED` atoms (absolute threshold for large blocks) OR strictly more than 50% `CONTESTED` atoms (relative threshold for small blocks), the entire matrix block must be rejected and flagged as `[INDETERMINATE]` or failed.

## Verification Plan

### Automated Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py --test`
- Create a unit test `tests/unit/hooks/test_scoring.py` to verify:
  1. Matrix-level score correctly applies the dynamic penalty without affecting the global scale improperly.
  2. The Cognitive Collapse lock correctly rejects a matrix exceeding the 3 atom or 50% threshold.

---
**Session Handover**
To execute this phase, please start a NEW chat session and run:
`/tier5-resume --target docs/epic/system2_variance_analysis_report_tracker.md`
