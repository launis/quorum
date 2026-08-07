# EPIC 133B: Tripartite Pipeline Strictness (Regex & JSON Mapping Eradication)

## 1. Goal Description & Background (Objective & Problem Statement)
Following the structural decomposition in EPIC 133A, this Epic targets the eradication of remaining LLM-cleanup "Duct-Tape" inside the `AtomEvaluationItemDTO` models. Currently, the DTOs use inline regular expressions to clean LLM hallucinations (specifically `[5. VALIDATION DECISION: ...]`) and rely on legacy fallback mapping for JSON keys. This violates the Tripartite Pipeline Architecture, which mandates that the Orchestrator/Execution layer must produce clean data BEFORE hydration, and the Zero-Reasoning Mandate which requires DTOs to be pure structures, not data cleaners.

## 2. Architectural Impact & Compliance Matrix

### Deprecations & Sunset List (What We Will REMOVE)
- **INTENTIONALLY DROPPED**: The `@field_validator` `_clean_validation_decision` inside `backend_v2/models/dtos/atom_evaluation.py` (which will be created in Epic 133A) that uses `re.sub()` to strip `[5. VALIDATION DECISION: ]` traces.
- **INTENTIONALLY DROPPED**: The `map_llm_extensions_to_domain` method inside `@[backend_v2/models/dtos/lightweight_matrix.py]` which currently acts as a hardcoded legacy translation dictionary.

### Retained SSOT Invariants (What We Will RETAIN)
- The core schemas (`AtomEvaluationItemDTO`, `LightweightMatrixOutput`) remain identical in shape.

### Compliance & Modernity Gates
- **Producer-Consumer Integrity**: The LLM prompt (`PromptCompiler`) MUST output exact keys, eliminating the need for `map_llm_extensions_to_domain`. If backward compatibility is required, it must be handled in a dedicated `LegacyTranslationAdapter` in the Service layer, NOT in the DTO.
- **Service Layer Firewall**: All regex text cleaning MUST occur in the Orchestrator (`@[backend_v2/services/orchestrator/dag_executor.py]`) before calling `.model_validate()`.

### Producer-Consumer Integration Check
- **Producer**: Prompt Compiler (`@[backend_v2/services/orchestrator/prompt_compiler.py]`) and DAG Executor.
- **Consumer**: Pydantic DTOs.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Golden Master & Coverage Verification (MANDATORY PREREQUISITE)
- **Step 1.1**: Run tests to verify coverage.

### Phase 2: Regex Eradication
- **Step 2.1**: Extract the Regex cleaning logic (`[5. VALIDATION DECISION: ]`) out of `backend_v2/models/dtos/atom_evaluation.py` and into the response parsing sequence of `@[backend_v2/services/orchestrator/dag_executor.py]`.
- **Step 2.2**: Remove the `@field_validator` from the DTO.

### Phase 3: Legacy Mapping Eradication
- **Step 3.1**: Move `map_llm_extensions_to_domain` out of `@[backend_v2/models/dtos/lightweight_matrix.py]`.
- **Step 3.2**: Create `LegacyTranslationAdapter` in the orchestrator layer to handle any necessary key translations before DTO hydration.

### Phase 4: Verification & E2E Integration Gate
- **Step 4.1**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`.

## 4. Definition of Done (DoD) & Verification Plan
- No `import re` exists inside `backend_v2/models/dtos/atom_evaluation.py`.
- No hardcoded key mapping exists inside `@[backend_v2/models/dtos/lightweight_matrix.py]`.
- Tests pass.
