# Phase 1: DTO Boundary Lockdown & Pre-flight Coercion

<required_context_rules>
- @[.agents/rules/00-antigravity-core.md]
- @[ki_god_code_prevention.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_ai_testing_standards.md]
- @[ki_ast_guardrail_testing.md]
- @[ki_python_314_concurrency_strictness.md]
</required_context_rules>

## Objective
Enforce the `ExecutionStatus` Enum purely at the DTO level for matrix payload data, removing loose `bool | str` typing. Pydantic V2 will coerce valid string inputs (like `"FAILED"`) into the `ExecutionStatus.FAILED` enum via the `LaxExecutionStatus` alias.

## Steps

### 1. Update LightweightMatrixOutput
**File:** `backend_v2/models/dtos/lightweight_matrix.py`
- Import `LaxExecutionStatus` from `backend_v2.models.enums`.
- Modify `evaluated_atoms` type annotation to `dict[str, LaxExecutionStatus]`.

### 2. Update TraceMatrixPayloadDTO
**File:** `backend_v2/models/dtos/trace.py`
- Import `LaxExecutionStatus` from `backend_v2.models.enums`.
- Modify `evaluated_atoms` type annotation to `dict[str, LaxExecutionStatus] | None`.

### 3. Verification
- Verify strict adherence to Zero-Compromise Strict Typing (no fallback logic added to handle raw `True`/`False` at the DTO boundary).
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos --test`

<anti_targets>
- Do not implement any fallback logic (like checking `if v is True`) in the DTO or domain parser.
- Do not add any new properties or modify unrelated fields in `LightweightMatrixOutput` or `TraceMatrixPayloadDTO`.
- Do not attempt to run the full global test suite in this phase, as downstream producers (Phase 1.5) still emit raw booleans and will fail Pydantic validation.
</anti_targets>

<dod_checklist>
- [ ] `LightweightMatrixOutput.evaluated_atoms` uses `LaxExecutionStatus`.
- [ ] `TraceMatrixPayloadDTO.evaluated_atoms` uses `LaxExecutionStatus | None`.
- [ ] No `bool` fallback logic is added.
</dod_checklist>

<validation_gate>
- [ ] Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos --test` to ensure Pydantic structures remain strict and pass type checks locally.
</validation_gate>
