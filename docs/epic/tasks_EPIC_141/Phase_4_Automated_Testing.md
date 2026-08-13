# Phase 4: Automated Testing Strategy

## Objective
Provide robust regression test coverage for the newly decomposed architecture, strictly adhering to the `ai_testing_standards` (ISTQB guidelines).

## Scope
### [NEW] `backend_v2/tests/unit/test_synthesis_payload_compression.py`
- Test cases for `SynthesisPayloadCompressor`:
  - Validating deep copy integrity.
  - Ensuring heavy metadata keys (`shuffled_atoms`, `atom_quotes`) are stripped.
  - Validating the application of `settings.max_synthesis_evaluations`.

### [NEW] `backend_v2/tests/unit/test_matrix_sensor_prompt_builder.py`
- Test cases for `MatrixSensorPromptBuilder`:
  - Validating CDATA encapsulation around user-provided strings.
  - Verifying separation of static vs dynamic messages for caching.

### [MODIFY] `backend_v2/tests/unit/test_dag_taskgroup.py`
- Update references to remove `sp_7a8b9c0d1e2f3a4b` and validate dynamic `model_strategy == "synthesis"` routing.

### [MODIFY] `backend_v2/tests/unit/test_bug_synthesis_hook.py`
- Verify that `synthesis_distiller.py` functions correctly with the newly abstracted `SynthesisPayloadCompressor`.

### [MODIFY] `backend_v2/tests/unit/test_epic93_contract_verification.py`
- Add structural assertions to ensure the new `extractive_sensor_service.py` adheres to the architectural contract.
