# Phase 6: Decompose _extract_matrices_and_extensions God Method

Provide a brief description of the problem, any background context, and what the change accomplishes:
Decompose the 530-line `_extract_matrices_and_extensions` method from `BlueprintTransformer` into a stateless `MatrixExtractorService.extract(...)` utility. To comply with the `structured_state_envelopes_mandate` and `strict_model_location` invariants, the 15 parameters will be encapsulated into a frozen Pydantic state model `MatrixExtractionContext` located within the `models/` directory.

## User Review Required
None

## Open Questions
None

## Proposed Changes

### 1. State Models
#### [MODIFY] [state.py](file:///c:/src/quorum/backend_v2/models/state.py)
- Create a `MatrixExtractionContext` Pydantic model (`ConfigDict(frozen=True, strict=True, extra='forbid')`).
- Encapsulate all 14+ parameters (results, locale, blocks_by_id, workflow_steps, profile, etc.) currently required by `_extract_matrices_and_extensions`.

### 2. Services
#### [NEW] [matrix_extractor.py](file:///c:/src/quorum/backend_v2/services/sdui/matrix_extractor.py)
- Implement `MatrixExtractorService` as a **stateless utility class** containing a single `@staticmethod extract(context: MatrixExtractionContext)`.
- **Exact Return Type**: `tuple[list[MatrixScorecardRowDTO], list[MatrixScorecardRowDTO], dict[str, MatrixScorecardRowDTO], dict[str, dict[str, ScorecardAtomDTO]]]`
- Enforce strict parsing of LLM trace output (`TraceMatrixPayloadDTO`) using Pydantic's `TypeAdapter` or `.model_validate()`. Manual dictionary scraping or `isinstance(data, dict)` fallback chains are strictly banned per `strict_pydantic_v2_rust`.

### 3. Orchestration
#### [MODIFY] [blueprint.py](file:///c:/src/quorum/backend_v2/services/blueprint.py#L218-L745)
- Delete the 530-line `_extract_matrices_and_extensions` God Method.
- Replace internal invocations with a call to `MatrixExtractorService.extract(context)` by constructing the `MatrixExtractionContext` state envelope locally.

## Verification Plan

### Automated Tests
- **Mandatory Negative Tests in `test_matrix_extractor.py`** (`anti_happy_path_mandate`):
  1. Pass an improperly structured dictionary inside `context.results` (violating `TraceMatrixPayloadDTO`) and assert it raises a Fail-Fast `AppException` (or Pydantic `ValidationError`).
  2. Pass a missing mandatory config field in the `context` instantiation and assert it raises `ValidationError`.
- Execute global integration script: `uv run python scripts/backend_audit_loop.py backend_v2/services/sdui/matrix_extractor.py --test`
- Execute global integration script: `uv run python scripts/backend_audit_loop.py backend_v2/services/blueprint.py --test`
