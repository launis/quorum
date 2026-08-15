# EPIC 142: Matrix Atom Boolean Evaluation Fix

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore accurate matrix scoring and Holistic Executive Synthesis (XAI Row Explanations) by fixing how atomic `true/false` evaluation results are processed in the backend logic pipeline.

### Problem Statement
Currently, all matrices incorrectly score 100% regardless of actual atom failures, and the row explanations (XAI) fail to generate contextual justifications for missed criteria. This is caused by two distinct logic errors in how `ExecutionStatus` strings are evaluated in Python.

### Root Cause / Gap Analysis
1. **Duck Typing Leakage (DTO Boundary Failure)**: The `LightweightMatrixOutput` DTO defines `evaluated_atoms` as `dict[str, bool | str]`. This loose typing allowed both legacy booleans and `"FAILED"` strings to bypass Pydantic's strict validation, forcing downstream services to handle dirty data.
2. **Boolean Coercion Bug in MatrixDomainParser**: In @[backend_v2/services/matrix_domain_parser.py], the calculation `sum(1 for v in matrix_payload.evaluated_atoms.values() if v)` incorrectly evaluates the string `"FAILED"` as boolean `True` (Python's truthy trap). This results in all atoms being counted as passed.
3. **Context Erasure in MatrixExplanationService**: In @[backend_v2/services/orchestrator/matrix_explanation_service.py] (line 102, inside `assemble_matrices_to_explain`), the loop filtering evaluates `if hit_status is True or str(hit_status).upper() == "PASS":`. First, the check uses `"PASS"` instead of the strict Enum value `"PASSED"`. Second, by completely dropping failed atoms, it starves the XAI Matrix LLM of the very context (specifically ALL failed assertion criteria from the evaluated atoms) it needs to explain *why* a matrix score dropped. Note: The `SynthesisDistiller` delegates this operation to `MatrixExplanationService`; it is NOT the owner of this bug.
4. **Atomic Test Data Migration (CI/CD Protection)**: If MatrixDomainParser's scoring logic is fixed and starts returning results < 100%, all previous unit tests that relied on the buggy 100% output will fail. The mandatory Phase 4 ensures tests are synchronously updated alongside the business logic to prove mathematical correctness and prevent CI/CD pipeline failures.
5. **Zero-Division Edge Case & Determinism (Valid N_A State)**: If a matrix's atoms are all evaluated as `ExecutionStatus.N_A`, the `total_atoms` denominator becomes `0`. This is a mathematically valid state indicating the matrix criteria do not apply to the source text. However, silently bypassing the calculation via `if total_atoms > 0` resembles duct-tape and obscures the intent. We must explicitly handle `total_atoms == 0` with an `elif` branch that documents the `N_A` state and explicitly sets `raw_score = None`, rather than silently ignoring it. (Note: A Fail-Fast crash is incorrect here, as a 0-atom state is a legitimate business logic outcome, and `blueprint.py` already safely ignores `None` scores during global averaging).
6. **Producer Contamination (scoring.py Raw Boolean Output)**: The `_calculate_matrix_scores_from_evaluations` function in @[backend_v2/hooks/scoring.py] (lines 924-929) writes raw Python `True`/`False` booleans into `evaluated_atoms_by_block[pb_id][aid]` instead of `ExecutionStatus.PASSED`/`ExecutionStatus.FAILED`. The type annotation at line 710 is explicitly `dict[str, dict[str, bool | str]]`. This means the PRODUCER is contaminating the pipeline with loose types, and if Phase 1 enforces `LaxExecutionStatus` on the DTO boundary, the raw `True`/`False` will crash Pydantic validation. Additionally, @[backend_v2/services/execution.py] (line 990) writes `payload.new_status.value` (a raw string) during human overrides, which must also emit the native Enum object.

### Tier 0 Research Findings (Execution Context)
- **Schema Validation**: Confirmed that `LaxExecutionStatus` is exported from `backend_v2.models.enums`, enabling `dict[str, LaxExecutionStatus]` in `LightweightMatrixOutput`.
- **Domain Parser**: The bug in `parse_matrices` is on lines 146-151 of `backend_v2/services/matrix_domain_parser.py`. The `if v:` check will be replaced with explicit `ExecutionStatus.PASSED` filtering and `N_A` exclusion.
- **Matrix Explanation**: The `assemble_matrices_to_explain` method (lines 98-106 of `backend_v2/services/orchestrator/matrix_explanation_service.py`) handles the extraction. We confirmed that failed atoms are currently being dropped entirely. N/A atoms must be skipped manually (`if hit_status == ExecutionStatus.N_A: continue`).
- **Legacy Test Fixtures**: Multiple tests inject raw `True`/`False` or string `"PASS"` values directly into the `evaluated_atoms` payload which will break strict Pydantic parsing. We must update the mocked JSON/fixtures globally in `backend_v2/tests/` before completing the Epic.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- We will REMOVE the filtering condition `if hit_status is True or str(hit_status).upper() == "PASS":` in `SynthesisDistiller`. Failed atoms MUST be passed forward.

### Retained SSOT Invariants (`What We Will RETAIN`)
- `ExecutionStatus` Enum (`"PASSED"`, `"FAILED"`) remains the strict standard.
- `evaluated_atoms` dictionary payload structure remains intact.

### Compliance & Modernity Gates
- **Zero-Compromise Strict Typing (The Duct-Tape Ban)**: Service-layer fallback logic (`if v is True or v == ExecutionStatus.PASSED.value`) is explicitly banned. The boundary MUST enforce the `ExecutionStatus` Enum purely at the DTO level. The `MatrixDomainParser` must execute pure mathematical logic (`if v == ExecutionStatus.PASSED`), shifting all coercion responsibility to Pydantic's `@field_validator(mode="before")`.
- **Pydantic Double-Serialization Ban (TypeAdapter Mandate)**: Serializing lists of Pydantic models via list comprehension `[obj.model_dump(...) for obj in ...] -> json.dumps()` is strictly banned. Converting models to Python `dict`s wastes CPU/memory allocations and causes `TypeError` on non-primitive types (specifically `datetime`, `UUID`). Downstream serializations MUST use `TypeAdapter(list[ModelDTO]).dump_json(instances, indent=2, exclude_none=True).decode("utf-8")` to execute directly in pydantic-core's Rust/C layer.
- **CoT Ordering Mandate (Pydantic Schema Strictness)**: All LLM structured output schemas (specifically and exhaustively: `StepDTOStrict` and `StepDTOSemantic` in @[backend_v2/models/dtos/evaluation_steps.py]) MUST rigorously enforce Chain-of-Thought ordering. Any field representing the final conclusion (`decision`, `status`, `is_true`) MUST physically be placed at the VERY BOTTOM of the class, explicitly AFTER the final reasoning fields (including `semantic_reasoning`). This forces the autoregressive LLM to generate analytical tokens before committing to a final outcome, eliminating post-hoc rationalization.

### Producer-Consumer Integration Check
- **Producer (Primary)**: `ExtractiveSensorService` (Produces `ExecutionStatus.FAILED` / `ExecutionStatus.PASSED`).
- **Producer (Legacy/Scoring)**: `scoring.py` `_calculate_matrix_scores_from_evaluations` (Currently produces raw `True`/`False` booleans and `"DLQ"`/`"CONTESTED"` strings. Must be fixed in Phase 1.5).
- **Producer (Override)**: `execution.py` `apply_human_override` (Currently writes `payload.new_status.value` string. Must be fixed in Phase 1.5).
- **Consumer**: `MatrixDomainParser` and `MatrixExplanationService` (Consumes and interprets the status values).

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: DTO Boundary Lockdown & Pre-flight Coercion
- **Target Files**:
  - @[backend_v2/models/dtos/lightweight_matrix.py]
  - @[backend_v2/models/dtos/trace.py]
- **Action 1a**: Modify `LightweightMatrixOutput.evaluated_atoms` (in `lightweight_matrix.py`, line 58) from `dict[str, bool | str]` to `dict[str, LaxExecutionStatus]`. *(Architectural Note: Pydantic V2 will automatically coerce valid string inputs, specifically `"PASSED"`, `"FAILED"`, `"SYSTEM_ERROR"`, `"N_A"`, into the native `ExecutionStatus` enum via the `LaxExecutionStatus` alias (`strict=False`). However, Pydantic V2 strictly rejects raw Python booleans `True`/`False` for Enum fields, raising a `ValidationError`.)*
- **Action 1b**: Modify `TraceMatrixPayloadDTO.evaluated_atoms` (in `trace.py`, line 51) from `dict[str, bool | str] | None` to `dict[str, LaxExecutionStatus] | None`. This is the actual DTO hydrated by `MatrixDomainParser` at `matrix_domain_parser.py` line 133 via `TraceMatrixPayloadDTO.model_validate(block_data)`. Failing to update this DTO makes the Phase 2 scoring fix impossible since the parser never touches `LightweightMatrixOutput` directly.
- **Action 2 (Compliance Enforcement & Co-ordinated Deployment Mandate)**: Ensure that no `@field_validator(mode="before")` or fallback logic is added to handle legacy raw `True`/`False` values. According to the `zero_legacy_fallback_hacks` mandate, models must remain mathematically pure. Because Pydantic V2 immediately rejects raw booleans under `LaxExecutionStatus`, Phase 1 and Phase 1.5 MUST be deployed concurrently in the exact same atomic commit (Co-ordinated Step Deployment). Enforcing Phase 1 without Phase 1.5 will trigger an immediate Pipeline Hazard (`ValidationError` in all runtime executions).

### Phase 1.5: Producer Contract Fix (scoring.py & execution.py)
- **Target Files**:
  - @[backend_v2/hooks/scoring.py]
  - @[backend_v2/services/execution.py]
- **Justification**: Upstream PRODUCERS previously emitted raw `True`/`False` booleans and `.value` strings. Because Phase 1 locks the DTO boundary to `LaxExecutionStatus` (which strictly forbids raw booleans), this phase MUST be synchronized atomically with Phase 1 before downstream scoring in Phase 2.
- **Action 1 (scoring.py)**: In the `_calculate_matrix_scores_from_evaluations` function:
  - Change the type annotation at line 710 from `dict[str, dict[str, bool | str]]` to `dict[str, dict[str, ExecutionStatus]]`.
  - At line 925, change `evaluated_atoms_by_block[pb_id][aid] = True` to `evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.PASSED`.
  - At line 929, change `evaluated_atoms_by_block[pb_id][aid] = False` to `evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.FAILED`.
  - At line 915, change `evaluated_atoms_by_block[pb_id][aid] = "DLQ"` to `evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.SYSTEM_ERROR`.
  - At line 920, change `evaluated_atoms_by_block[pb_id][aid] = "CONTESTED"` to `evaluated_atoms_by_block[pb_id][aid] = ExecutionStatus.PASSED`. (Rationale: "CONTESTED" means it was passed via override. The domain parser strictly counts `ExecutionStatus.PASSED` for the score numerator. The override metadata is preserved in `matrix_extensions_by_block` and `atom_quotes_by_block`, so the DTO only needs the mathematical status).
- **Action 2 (execution.py)**: At line 990, change `v["evaluated_atoms"][atom_id] = payload.new_status.value` to `v["evaluated_atoms"][atom_id] = payload.new_status` (pass the native Enum object, per `strict_enum_hydration_and_validation` mandate).

### Phase 2: MatrixDomainParser Scoring Fix (Pure Domain Logic & Denominator Correction)
- **Target File**: @[backend_v2/services/matrix_domain_parser.py]
- **Action**: Update the `true_atoms` calculation. Because Phase 1 guarantees pure `ExecutionStatus` enums, we can remove all duct-tape type checking and execute pure domain logic. **Crucially, you MUST fix the denominator bug**: `ExecutionStatus.N_A` atoms must NOT be included in the total atom count for scoring. Furthermore, we must explicitly handle the `total_atoms == 0` edge case. Instead of crashing (Fail-Fast), which would destroy a valid evaluation, we explicitly log and bypass it, as `N_A` is a valid mathematical outcome.
  ```python
  valid_atoms = [v for v in matrix_payload.evaluated_atoms.values() if v != ExecutionStatus.N_A]
  true_atoms = sum(1 for v in valid_atoms if v == ExecutionStatus.PASSED)
  total_atoms = len(valid_atoms)

  if total_atoms > 0 and raw_score is None:
      raw_score = true_atoms / total_atoms
      norm_score = raw_score * 100.0
  elif total_atoms == 0 and raw_score is None:
      # Valid Domain State: The entire matrix is Not Applicable.
      # We explicitly leave raw_score as None and log the intentional bypass.
      logger.info("[MatrixDomainParser] Matrix '%s' evaluated to N_A (0 valid atoms). Bypassing scoring.", b_id)
      raw_score = None
      norm_score = None
  ```

### Phase 3: Synthesis Context Preservation
- **Target Files**:
  - @[backend_v2/services/orchestrator/matrix_explanation_service.py]
  - @[backend_v2/models/dtos/synthesis.py]
  - @[backend_v2/worker.py]
- **Action 1 (Context)**: The matrix explanation logic is already abstracted into `MatrixExplanationService` (separated from `SynthesisDistiller`). We will augment this service rather than creating redundant extractors.
- **Action 2**: Remove the restrictive passing-only check (`if hit_status is True or str(hit_status).upper() == "PASS":`) inside `MatrixExplanationService.assemble_matrices_to_explain` (line 102). The extraction must iterate over ALL atoms inside `atoms.items()` (both PASSED and FAILED). You MUST programmatically bypass N/A items using exactly: `if atom_status == ExecutionStatus.N_A: continue`.
- **Action 2b (Duck-Typing Removal)**: Remove the `isinstance(atoms, dict)` guard at line 100 and the `payload.get("evaluated_atoms", {})` duct-tape at line 98. After Phase 1.5 ensures all producers emit strict `ExecutionStatus` values and Phase 1 locks the DTO boundary, the payload's `evaluated_atoms` field is guaranteed to be a typed dict. Access it via direct typed attribute access once the service receives the `TraceMatrixPayloadDTO` instead of raw `dict` payloads.
- **Action 3**: Enforce structured status formatting via Strict Pydantic DTOs. Extract both passed evidence quotes and failed claim labels, deduplicating them to compress the token budget. Structure the context into formal sections (`SUPPORTING EVIDENCE:` for `PASSED` atoms with verbatim quotes, and `UNMET CRITERIA:` for `FAILED` atoms with localized claim labels). Inject the result cleanly into a Strict Pydantic DTO (specifically: [NEW] MatrixExplanationContextDTO located in @[backend_v2/models/dtos/synthesis.py]) rather than a mutable state dictionary, adhering to the Tripartite Pipeline Architecture event-driven data envelopes mandate. (Note: Advanced ranked round-robin claim diversity and quote length limits are delegated to EPIC 143).
- **Action 4 (Downstream Integration & TypeAdapter Serialization Mandate)**: Update @[backend_v2/worker.py] (lines 922 and 964 serializing `matrices_to_explain`). It currently expects raw dictionaries and directly serializes them with `json.dumps()`. Because Action 3 now enforces that the service returns native `MatrixExplanationContextDTO` objects, calling `[obj.model_dump(...) for obj in ...] -> json.dumps()` is strictly banned as an anti-pattern (Double-Serialization Ban). List comprehension with `.model_dump()` causes intermediate Python `dict` allocations and risks `TypeError` crashes on complex types (specifically `datetime`, `UUID`). Instead, define `MatrixExplanationContextList = TypeAdapter(list[MatrixExplanationContextDTO])` in @[backend_v2/models/dtos/synthesis.py] (or module-level in `worker.py`) and serialize directly via `MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode("utf-8")` into the LLM prompt, leveraging pydantic-core's optimized C/Rust serialization engine.
- **Action 5 (Tests)**: Update @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py] and @[backend_v2/tests/unit/test_epic93_contract_verification.py] (which contain `assemble_matrices_to_explain` tests) and downstream SDUI Parity / E2E assertions to expect the new realistic matrix scores and verify that failed context is correctly forwarded.

### Phase 4: Atomic Test Alignment (Test Expansion)
- **Target Files**:
  - @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
  - @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]
  - @[backend_v2/tests/unit/test_epic93_contract_verification.py]
  - @[backend_v2/tests/unit/hooks/test_scoring.py]
  - @[backend_v2/tests/unit/services/orchestrator/test_context_router.py]
  - @[backend_v2/tests/unit/services/orchestrator/strategies/llm_execution/test_context_builder.py]
  - @[backend_v2/tests/unit/services/test_blueprint.py]
  - @[backend_v2/seed/seed_data.json]
  - @[client_app_v2/test/]
- **Action 1 (Unit Tests - Scoring Logic)**: Update the unit test assertions. Tests that previously relied on "FAILED" evaluating to a 100% pass rate must be updated to expect the correct mathematical percentage. Update the mocked assertions in `test_synthesis_distiller.py` and `test_epic93_contract_verification.py` to ensure failed atoms are correctly verified as present in the prompt context.
- **Action 2 (Unit Tests - Fixture Type Migration)**: ALL test fixtures that use raw `True`/`False` booleans or raw `"PASS"`/`"FAIL"` strings in `evaluated_atoms` dictionaries MUST be updated to use `ExecutionStatus.PASSED`/`ExecutionStatus.FAILED` (or their string equivalents `"PASSED"`/`"FAILED"` which `LaxExecutionStatus` will coerce). Specifically, the following files contain legacy boolean fixtures that MUST be migrated:
  - `test_epic93_contract_verification.py` (lines 275, 285: `{"a1": True}`)
  - `test_scoring.py` (lines 1116, 1181, 1245: `is True`/`is False` assertions on evaluated_atoms output)
  - `test_context_router.py` (line 156: `{"atom_1": True, "atom_2": False}`)
  - `test_context_builder.py` (line 100: `{"atom1": True, "atom2": False}`)
  - `test_synthesis_distiller.py` (lines 129, 189, 218, 228: `{"a1": True}`)
  - `test_blueprint.py` (line 1929: `{"tda_...": True}`)
- **Action 3 (E2E & Seed Data Alignment)**: Update `seed_data.json` and all statically defined mock fixtures that assume a 100% matrix score (specifically: you MUST run `grep_search` to find all matrix score assertions in `backend_v2/tests/`). **CRITICAL MANDATE**: You MUST use scoped line boundaries (`StartLine`/`EndLine`) when reading `seed_data.json` with `view_file`. Reading the massive file entirely will trigger Context Amnesia and wipe out your systemic rules. Correcting the logic bug will cause matrix scores to legitimately drop; therefore, all downstream SDUI Parity tests and E2E integration assertions MUST be synchronously updated with the new expected scores to prevent a CI/CD pipeline collapse (preventing "Fake Green").
- **Action 4 (Frontend SDUI Parity Tests)**: The backend score drops will mathematically break the Flutter UI parity tests. You MUST synchronously run and fix the frontend test suite in `client_app_v2/test/` to expect the updated `< 100%` matrix scores in their SDUI JSON fixture equivalents.

### Phase 5: Pydantic Schema CoT Ordering Audit & Fix
- **Target Files**: @[backend_v2/models/dtos/evaluation_steps.py]
- **Action**: Physically audit the Pydantic classes defining the LLM's response schema (specifically and exhaustively: `StepDTOStrict` and `StepDTOSemantic`). 
  1. For `StepDTOStrict`: Ensure that the boolean field that dictates the pass/fail outcome (`decision`) is placed at the very bottom of the class definition, explicitly AFTER the `semantic_reasoning` field.
  2. For `StepDTOSemantic`: Ensure that `override_reason` (the reasoning step for overriding) is placed explicitly BEFORE `contextual_override` (the boolean flag) to respect the exact same CoT flow, handling the Pydantic inheritance structure correctly.
  Reorder the fields if they are currently violating this CoT principle to restore analytical rigor.

## 4. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)
- MatrixDomainParser correctly maps `"FAILED"` (or `ExecutionStatus.FAILED`) to a boolean `False` equivalent, allowing matrix scores to legitimately fall below 100%.
- SynthesisDistiller correctly forwards quotes and claims for failed atoms into the XAI justification pipeline, prefixed with their execution status.
- All unit tests pass, explicitly asserting that failed context is preserved and scores are calculated correctly.

### Automated Unit Tests
- `uv run python scripts/backend_audit_loop.py backend_v2 --test`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/test --build`

### AST Guardrails & Structural Tests
- Ensure no bare `if status:` string coercion exists for `ExecutionStatus` variables.

### Manual Verification Steps
- Re-run a full execution via UI and verify that a matrix containing failed criteria correctly displays a `< 100%` score and explains the missing criteria.

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
- @[ki_matrix_boolean_evaluation_strictness.md]
- @[ki_god_code_prevention.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_context_enriched_decompose_verify.md]
- @[ki_matrix_sensor_prompt_builder.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_ai_testing_standards.md]
- @[ki_ast_guardrail_testing.md]
- @[ki_llm_extraction_architecture.md]
- @[ki_synthesis_payload_compression.md]
- @[ki_python_314_concurrency_strictness.md]
- @[ki_execution_engine_protocol.md]
- @[ki_de_generator_execution_paradigm.md]
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[.agents/rules/02_flutter_desktop.md]
- @[.agents/rules/05_llm_architecture.md]
</required_knowledge_items>
