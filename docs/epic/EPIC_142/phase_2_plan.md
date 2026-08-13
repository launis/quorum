# Phase 2: MatrixDomainParser Scoring Fix (Pure Domain Logic & Denominator Correction)

## Objective
Correct the scoring calculation in `MatrixDomainParser` to handle `ExecutionStatus` enums properly, exclude `N_A` atoms from the denominator, and explicitly handle the zero-division edge case without crashing.

## Steps

### 1. Update MatrixDomainParser
**File:** `backend_v2/services/matrix_domain_parser.py`
- Import `ExecutionStatus` from `backend_v2.models.enums`.
- Modify the scoring calculation logic inside `parse_matrices`:
  - Change `true_atoms` calculation to explicitly count `ExecutionStatus.PASSED`: `sum(1 for v in matrix_payload.evaluated_atoms.values() if v == ExecutionStatus.PASSED)`
  - Change `total_atoms` calculation to exclude `ExecutionStatus.N_A`: `sum(1 for v in matrix_payload.evaluated_atoms.values() if v != ExecutionStatus.N_A)`
  - Add explicit handling for `total_atoms == 0`: set `raw_score` and `norm_score` to `None` and log an info message indicating the Matrix was N_A.

### 2. Remove xfail Markers from Integration Tests
**File:** `backend_v2/tests/unit/hooks/test_scoring.py`
- Find all tests marked with `@pytest.mark.xfail(reason="Phase 2 pending: MatrixDomainParser evaluates Enum as truthy")`.
- Remove the `@pytest.mark.xfail` decorator from these tests as the bug is now resolved.

### 3. Add Negative Test Scenarios (Anti-Happy-Path Mandate)
**File:** `backend_v2/tests/unit/services/test_matrix_domain_parser.py`
- Add an explicit negative test to verify that if all atoms evaluate to `ExecutionStatus.N_A` (i.e. `total_atoms == 0`), the parser handles it gracefully without a ZeroDivisionError and sets the scores to `None`.
- Add an explicit test to verify that `ExecutionStatus.FAILED` and `ExecutionStatus.SYSTEM_ERROR` do not increment `true_atoms`.

### 4. Verification
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services backend_v2/tests --test`
