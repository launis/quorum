# Phase 2: MatrixDomainParser Scoring Fix (Pure Domain Logic & Denominator Correction)

## Objective
Correct the scoring calculation in `MatrixDomainParser` to handle `ExecutionStatus` enums properly, exclude `N_A` atoms from the denominator, and explicitly handle the zero-division edge case without crashing.

## Steps

### 1. Update MatrixDomainParser
**File:** `backend_v2/services/matrix_domain_parser.py`
- Import `ExecutionStatus` from `backend_v2.models.enums`.
- Modify the scoring calculation logic inside `parse_matrices`:
  - Filter out `ExecutionStatus.N_A` from valid atoms.
  - Count `ExecutionStatus.PASSED` for `true_atoms`.
  - Add explicit handling for `total_atoms == 0`: set `raw_score` and `norm_score` to `None` and log an info message indicating the Matrix was N_A.

### 2. Verification
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services --test`
