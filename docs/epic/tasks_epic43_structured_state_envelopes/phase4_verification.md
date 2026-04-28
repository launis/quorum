# Phase 4: Unit Test Refactoring & Quality Loop

## Objective
The impact radius of changing the runtime state projection from `dict` to `List[StepOutputDTO]` is massive for existing unit tests. We must update all mock fixtures and test files to reflect the new strict list structure.

## Architectural Invariants (Mandatory Rules)
- **Deterministic Testing Delegation:** You are the worker, Python is the judge. The `backend_audit_loop.py` enforces >90% coverage. Analyze the `Miss` column if it fails.
- **Zero Type Ignore Shortcuts:** Do not silence test errors with `# type: ignore`. Construct proper Pydantic models in tests.
- **The Anti-TDD Trap Mandate:** If old tests conflict with the new rules (e.g. testing for dictionary outputs), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.

## Execution Steps

1. **Target (Modify): `backend_v2/tests/unit/test_blueprint.py`**
   - Update mock traces. Where `mock_fold_trace` or similar fixtures previously returned `{"stp_1_blk_1": {...}}`, instantiate and return `[StepOutputDTO(step_id="stp_1", block_id="blk_1", data_type="matrix", payload={...})]`.

2. **Target (Modify): `backend_v2/tests/unit/test_context_builder.py`**
   - Refactor mock dependencies to provide the new `StepOutputDTO` list format. Ensure Context Builder output matches expected LLM prompt injection standards.

3. **Target (Modify): `backend_v2/tests/unit/test_flattener.py` (if exists, or related StateProjector tests)**
   - Assert that `fold_trace()` returns a List of `StepOutputDTO` objects. Validate Pydantic strictness.

4. **Target (Modify): Any shared fixtures in `conftest.py` or `mock_data.py`**
   - Update global mock states that simulate `fold_trace` behavior.

## Verification & Quality Gate Plan
- **Command:** `uv run python scripts/backend_audit_loop.py backend_v2/ --test`
- MUST achieve passing tests. If coverage drops, investigate the `Miss` lines and add test cases.
- If circuit breaker trips (>3 identical test failures), STOP and ask for human guidance.
