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
- **Producer-Consumer Integrity**: The LLM prompt (`PromptCompiler`) MUST output exact keys, eliminating the need for `map_llm_extensions_to_domain`. Per `the_no_legacy_mandate`, backward compatibility is STRICTLY FORBIDDEN. No `LegacyTranslationAdapter` may be created. The system MUST rely purely on strict `.model_validate()` and Fail-Fast.
- **Zero Self-Healing Mandate**: Per `the_self_healing_ban`, ALL regex text cleaning (specifically stripping `[5. VALIDATION DECISION: ]`) MUST be completely deleted without replacement. The system must crash (Fail-Fast) if the LLM hallucinates prefixes. Data validation belongs 100% to Pydantic and `LLMTaskExecutor.execute_structured_task()`.
- **Atomic Test Mock Migration**: When `map_llm_extensions_to_domain` is removed, the corresponding mock data in `backend_v2/tests/` and `seed_data.json` MUST be atomically updated in the same phase to prevent test loop crashes.

### Producer-Consumer Integration Check
- **Producer**: Prompt Compiler (`@[backend_v2/services/orchestrator/prompt_compiler.py]`) and DAG Executor.
- **Consumer**: Pydantic DTOs.

## 3. Phased Execution Plan (Implementation Strategy)

### Phase 1: Golden Master & Coverage Verification (MANDATORY PREREQUISITE)
- **Step 1.1**: Run `uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --test` to verify baseline coverage.

### Phase 2: Regex Eradication
- **Step 2.1**: Completely DELETE the Regex cleaning logic (`[5. VALIDATION DECISION: ]`) from `backend_v2/models/dtos/atom_evaluation.py`. Do NOT move it to the orchestrator.
- **Step 2.2**: Remove the `@field_validator` `_clean_validation_decision` from the DTO.

### Phase 3: Legacy Mapping Eradication
- **Step 3.1**: Completely DELETE `map_llm_extensions_to_domain` from `@[backend_v2/models/dtos/lightweight_matrix.py]`.
- **Step 3.2**: Update all explicitly identified call sites in the backend (specifically and exhaustively: `@[backend_v2/services/orchestrator/context_router.py]`, `@[backend_v2/services/matrix_domain_parser.py]`, `@[backend_v2/tests/unit/models/dtos/test_lightweight_matrix.py]`, `@[backend_v2/worker.py]`, and `@[backend_v2/hooks/scoring.py]`) to remove the function call and pass raw data directly to Pydantic hydration.
- **Step 3.3**: Atomically update any legacy test fixtures that relied on the old keys to match the strict Phase 9 schema.

### Phase 4: Verification & E2E Integration Gate
- **Step 4.1**: Run `uv run python scripts/backend_audit_loop.py backend_v2 --test`.

## 4. Definition of Done (DoD) & Verification Plan
- No `import re` exists inside `backend_v2/models/dtos/atom_evaluation.py`.
- No hardcoded key mapping exists inside `@[backend_v2/models/dtos/lightweight_matrix.py]`.
- No `LegacyTranslationAdapter` or regex cleanup loops exist in the orchestrator.
- `uv run python scripts/backend_audit_loop.py backend_v2 --test` passes with 100% type strictness.
