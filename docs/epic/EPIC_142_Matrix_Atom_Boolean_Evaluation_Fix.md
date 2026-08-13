# EPIC 142: Matrix Atom Boolean Evaluation Fix

## 1. Goal Description & Background (Objective & Problem Statement)

### Business Objective
Restore accurate matrix scoring and Holistic Executive Synthesis (XAI Row Explanations) by fixing how atomic `true/false` evaluation results are processed in the backend logic pipeline.

### Problem Statement
Currently, all matrices incorrectly score 100% regardless of actual atom failures, and the row explanations (XAI) fail to generate contextual justifications for missed criteria. This is caused by two distinct logic errors in how `ExecutionStatus` strings are evaluated in Python.

### Root Cause / Gap Analysis
1. **Duck Typing Leakage (DTO Boundary Failure)**: The `LightweightMatrixOutput` DTO defines `evaluated_atoms` as `dict[str, bool | str]`. This loose typing allowed both legacy booleans and `"FAILED"` strings to bypass Pydantic's strict validation, forcing downstream services to handle dirty data.
2. **Boolean Coercion Bug in MatrixDomainParser**: In @[backend_v2/services/matrix_domain_parser.py], the calculation `sum(1 for v in matrix_payload.evaluated_atoms.values() if v)` incorrectly evaluates the string `"FAILED"` as boolean `True` (Python's truthy trap). This results in all atoms being counted as passed.
3. **Context Erasure in SynthesisDistiller**: In @[backend_v2/services/orchestrator/synthesis_distiller.py], the loop filtering evaluates `if hit_status is True or str(hit_status).upper() == "PASS":`. First, the check uses `"PASS"` instead of the strict Enum value `"PASSED"`. Second, by completely dropping failed atoms, it starves the XAI Matrix LLM of the very context (specifically: missing requirements, falsification, coaching) it needs to explain *why* a matrix score dropped.
4. **Atomic Test Data Migration (CI/CD Protection)**: If MatrixDomainParser's scoring logic is fixed and starts returning results < 100%, all previous unit tests that relied on the buggy 100% output will fail. The mandatory Phase 4 ensures tests are synchronously updated alongside the business logic to prove mathematical correctness and prevent CI/CD pipeline failures.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (`What We Will REMOVE`)
- We will REMOVE the filtering condition `if hit_status is True or str(hit_status).upper() == "PASS":` in `SynthesisDistiller`. Failed atoms MUST be passed forward.

### Retained SSOT Invariants (`What We Will RETAIN`)
- `ExecutionStatus` Enum (`"PASSED"`, `"FAILED"`) remains the strict standard.
- `evaluated_atoms` dictionary payload structure remains intact.

### Compliance & Modernity Gates
- **Zero-Compromise Strict Typing (The Duct-Tape Ban)**: Service-layer fallback logic (`if v is True or v == ExecutionStatus.PASSED.value`) is explicitly banned. The boundary MUST enforce the `ExecutionStatus` Enum purely at the DTO level. The `MatrixDomainParser` must execute pure mathematical logic (`if v == ExecutionStatus.PASSED`), shifting all coercion responsibility to Pydantic's `@field_validator(mode="before")`.
- **CoT Ordering Mandate (Pydantic Schema Strictness)**: All LLM structured output schemas (specifically and exhaustively: `StepDTOStrict` and `StepDTOSemantic` in @[backend_v2/models/dtos/evaluation_steps.py]) MUST rigorously enforce Chain-of-Thought ordering. Any field representing the final conclusion (`decision`, `status`, `is_true`) MUST physically be placed at the VERY BOTTOM of the class, explicitly AFTER the final reasoning fields (including `semantic_reasoning`). This forces the autoregressive LLM to generate analytical tokens before committing to a final outcome, eliminating post-hoc rationalization.

### Producer-Consumer Integration Check
- **Producer**: `ExtractiveSensorService` (Produces `ExecutionStatus.FAILED` / `ExecutionStatus.PASSED`).
- **Consumer**: `MatrixDomainParser` and `SynthesisDistiller` (Consumes and interprets the boolean equivalent).

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: DTO Boundary Lockdown & Pre-flight Coercion
- **Target File**: @[backend_v2/models/dtos/lightweight_matrix.py]
- **Action 1**: Modify `LightweightMatrixOutput.evaluated_atoms` from `dict[str, bool | str]` to `dict[str, LaxExecutionStatus]`. *(Architectural Note: Pydantic V2 will automatically coerce valid string inputs specifically `"FAILED"` into the `ExecutionStatus.FAILED` enum via the `LaxExecutionStatus` alias, guaranteeing structural purity without breaking strict Enum hydration rules.)*
- **Action 2 (Compliance Enforcement)**: Ensure that no `@field_validator(mode="before")` or fallback logic is added to handle legacy raw `True`/`False` values. According to the `zero_legacy_fallback_hacks` mandate, models must remain mathematically pure. If legacy data crashes the validation, it must be fixed at the source (in Phase 4 via `seed_data.json` updates) rather than polluting the domain layer with duct-tape parsing logic.

### Phase 2: MatrixDomainParser Scoring Fix (Pure Domain Logic & Denominator Correction)
- **Target File**: @[backend_v2/services/matrix_domain_parser.py]
- **Action**: Update the `true_atoms` calculation. Because Phase 1 guarantees pure `ExecutionStatus` enums, we can remove all duct-tape type checking and execute pure domain logic. **Crucially, you MUST fix the denominator bug**: `ExecutionStatus.NOT_EVALUATED` atoms must NOT be included in the total atom count for scoring, otherwise they act as hidden penalties that deflate the score.
  ```python
  valid_atoms = [v for v in matrix_payload.evaluated_atoms.values() if v != ExecutionStatus.NOT_EVALUATED]
  true_atoms = sum(1 for v in valid_atoms if v == ExecutionStatus.PASSED)
  total_atoms = len(valid_atoms)

  if total_atoms > 0 and raw_score is None:
      raw_score = true_atoms / total_atoms
      norm_score = raw_score * 100.0
  ```

### Phase 3: SynthesisDistiller Context Preservation
- **Target File**: @[backend_v2/services/orchestrator/synthesis_distiller.py]
- **Action 1**: Remove the restrictive passing-only check inside `_assemble_matrices_to_explain`. The extraction must iterate over ALL atoms inside `atoms.items()` (both PASSED and FAILED).
- **Action 2**: Enforce structured status tagging via Strict Pydantic DTOs. Building LLM prompts via raw string concatenation is strictly forbidden (to protect Context Caching parity). However, you MUST NOT dynamically instantiate `PromptBlock` objects in the service layer, as this violates the `<prompt_asset_ssot_mandate>` and causes a "Lost in the Middle" token flood during the holistic XAI Synthesis phase (which cannot be chunked). Instead, you MUST extract the failed claims and quotes, and rigorously deduplicate them to compress the token budget. **God Code Prevention**: Because `synthesis_distiller.py` is already over 500 lines (violating the 200-line hard architectural smell threshold), you MUST NOT write this complex extraction and deduplication logic inside `synthesis_distiller.py`. You MUST create a new, dedicated file (specifically: `backend_v2/services/orchestrator/matrix_context_extractor.py`) to hold this pure, testable extraction logic. Inject the result cleanly into a Strict Pydantic DTO (specifically: [NEW] MatrixExplanationContextDTO) rather than a mutable state dictionary, adhering to the Tripartite Pipeline Architecture event-driven data envelopes mandate. The `PromptCompiler` will automatically handle the strict XML serialization dynamically at the end of the payload. Ensure `ExecutionStatus.NOT_EVALUATED` is safely skipped if present.

### Phase 4: Atomic Test Alignment (Test Expansion)
- **Target Files**:
  - @[backend_v2/tests/unit/services/test_matrix_domain_parser.py]
  - @[backend_v2/tests/unit/services/orchestrator/test_synthesis_distiller.py]
  - @[backend_v2/seed/seed_data.json]
- **Action 1 (Unit Tests)**: Update the unit test assertions. Tests that previously relied on "FAILED" evaluating to a 100% pass rate must be updated to expect the correct mathematical percentage. Update the mocked assertions in `test_synthesis_distiller.py` to ensure failed atoms are correctly verified as present in the prompt context.
- **Action 2 (E2E & Seed Data Alignment)**: Update `seed_data.json` and all statically defined mock fixtures that assume a 100% matrix score (specifically: you MUST run `grep_search` to find all matrix score assertions in `backend_v2/tests/`). Correcting the logic bug will cause matrix scores to legitimately drop; therefore, all downstream SDUI Parity tests and E2E integration assertions MUST be synchronously updated with the new expected scores to prevent a CI/CD pipeline collapse (preventing "Fake Green").

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

### AST Guardrails & Structural Tests
- Ensure no bare `if status:` string coercion exists for `ExecutionStatus` variables.

### Manual Verification Steps
- Re-run a full execution via UI and verify that a matrix containing failed criteria correctly displays a `< 100%` score and explains the missing criteria.

## 5. Required Knowledge Items (KI Registry)

<required_knowledge_items>
- @[ki_god_code_prevention.md]
- @[ki_tripartite_pipeline_architecture.md]
- @[ki_sdui_matrix_synthesis.md]
- @[ki_context_enriched_decompose_verify.md]
- @[ki_matrix_sensor_prompt_builder.md]
- @[ki_dag_engine_dto_projection_rules.md]
- @[ki_ai_testing_standards.md]
- @[ki_ast_guardrail_testing.md]
- @[ki_llm_extraction_architecture.md]
- @[.agents/rules/00-antigravity-core.md]
- @[.agents/rules/01-python-backend.md]
- @[.agents/rules/05_llm_architecture.md]
</required_knowledge_items>
