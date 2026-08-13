# Phase 3: Synthesis Context Preservation

## Objective
Preserve synthesis context by ensuring `MatrixExplanationService` forwards failed quotes to the downstream LLM, removing the restrictive `if hit_status is True` filtering. Enforce the Tripartite Pipeline Architecture by returning Strict Pydantic DTOs (`MatrixExplanationContextDTO`) instead of raw dictionaries.

## User Review Required
> [!IMPORTANT]
> - `worker.py` will now assume that `matrices_to_explain` contains `MatrixExplanationContextDTO` instances and dump them directly with `[m.model_dump(exclude_none=True) for m in matrices_to_explain]`.
> - If `synthesis_distiller_hook` is bypassed or modified in the future to return dictionaries, this will fail. The DTO boundary is now strictly enforced.

## Open Questions
None. The Epic requirements are strict and exact.

## Proposed Changes

### Synthesis DTO
#### [MODIFY] [synthesis.py](file:///c:/src/quorum/backend_v2/models/dtos/synthesis.py)
- **Add DTO**: `MatrixExplanationContextDTO(V2CoreBase)` with strict settings (`extra="forbid"`).
- **Fields**:
  - `real_matrix_id`: Annotated[str, Field(description="The original PromptBlock ID")]
  - `matrix_id`: Annotated[str, Field(description="The alias for the LLM")]
  - `matrix_label`: Annotated[str, Field(description="The localized matrix title")]
  - `score`: Annotated[float | None, Field(description="The normalized score", default=None)]
  - `justification`: Annotated[str, Field(description="The structured justification text including quotes")]

### Matrix Explanation Logic
#### [MODIFY] [matrix_explanation_service.py](file:///c:/src/quorum/backend_v2/services/orchestrator/matrix_explanation_service.py)
- **Change Return Type**: Update `assemble_matrices_to_explain` return type to `list[MatrixExplanationContextDTO]`.
- **Remove Duck-Typing**: 
  - Remove `payload.get("evaluated_atoms", {})`.
  - Remove `isinstance(atoms, dict)`.
  - Introduce explicit Pydantic parsing: `lw_matrix = LightweightMatrixOutput.model_validate(payload, strict=False)` and access `atoms = lw_matrix.evaluated_atoms`.
- **Bypass Logic**: Replace `if hit_status is True or str(hit_status).upper() == "PASS":` with exactly: `if hit_status == ExecutionStatus.N_A: continue` (where `hit_status` is checked as `ExecutionStatus`).
- **Return DTO**: Build and return instances of `MatrixExplanationContextDTO`.

### Background Worker Integration
#### [MODIFY] [worker.py](file:///c:/src/quorum/backend_v2/worker.py)
- **Update Serialization (Line 922)**: 
  - Change `json.dumps(matrices_to_explain, indent=2)` to `json.dumps([m.model_dump(exclude_none=True) for m in matrices_to_explain], indent=2)` to serialize the new DTO objects correctly.

### Automated Tests
#### [MODIFY] [test_synthesis_distiller.py](file:///c:/src/quorum/backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py)
- **Update Existing Tests**: Modify assertions from `result[0]["score"]` to `result[0].score` (attribute access for the DTO).
- **Add New Test**: Create `test_assemble_matrices_to_explain_includes_failed_claims` to verify that `ExecutionStatus.FAILED` is included in the explanation while `ExecutionStatus.N_A` is skipped.

## Verification Plan

### Automated Tests
- `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py --test`
- `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/matrix_explanation_service.py --test`

### Manual Verification
- N/A, unit tests will ensure correctness of DTO boundaries and failed claim preservation.
