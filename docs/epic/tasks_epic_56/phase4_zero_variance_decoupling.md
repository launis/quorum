# Implementation Plan: Phase 4 - Zero-Variance Decoupling (EPIC 56)

## 1. Goal
Eliminate the 14.9% cognitive drift and lexical variance in the TDA pipeline by enforcing an absolute "Zero-Variance Protocol". This requires decoupling the extraction (Map) from the decision (Evaluate). The LLM is stripped of its authority to generate a Pass/Fail score and is demoted to a "blind text scanner." A deterministic Python AST Evaluator will handle the final scoring logic.

## 2. Architectural Rules & Invariants
- **Rule 1: The Zero Compromise Pledge (00-antigravity-core)**: Strict Pydantic V2 schemas MUST be enforced. Fallbacks (`v.get()`, `if None: pass`), naked dicts, and lazy `try-except pass` are strictly banned. If extraction fails or data is missing, raise an exception and CRASH (Fail-Fast).
- **Rule 2: No Legacy Mandate (00-antigravity-core)**: Obsolete code, fallback chains, and backwards compatibility loops MUST be ruthlessly deleted.
- **Rule 3: TDD Mandate (00-antigravity-core)**: Write a failing Pytest that reproduces the extraction/logic failure BEFORE fixing domain code. Use `mock_data.py` for LLM responses (Live LLM calls are banned in tests).
- **Rule 4: Zero-Variance Protocol**: The LLM must NOT evaluate. Pass/Fail decisions must be executed in native Python using strict 1D Lexical Mapping.
- **Rule 5: Strict Pydantic V2 Rust (01-python-backend)**: Use native `.model_validate()`, `.model_dump()`, and `TypeAdapter.validate_json()`. Python `json.loads()` and `.dict()` are banned.
- **Rule 6: Silent Failures Ban (01-python-backend)**: No `try: ... except Exception: pass`. Exceptions must ALWAYS be logged natively (`logger.error`) and re-thrown or handled explicitly via `AppException`.
- **Rule 7: Native Structured Outputs Mandate (05-llm-architecture)**: Rely ONLY on `LLMTaskExecutor.execute_structured_task()`. All syntactic self-healing loops must be deleted.
- **Rule 8: High-Fidelity Prompting (05-llm-architecture)**: System prompts MUST be 100% in English, use Hybrid Prompting (XML tags), and remain perfectly static for caching.
- **Source**: Mismatch analysis (`scratch/mismatch_traces_raw.md`), Epic 56 Tracker.

## 3. Implementation Steps

### [x] Step 1: Schema Decoupling (Extraction Factory)
**Target File**: `backend_v2/extraction_schema_factory.py` & `backend_v2/models/v2_core.py`
- Modify the dynamic Pydantic schema generation.
- **Ruthless Deletion (Rule 2)**: Delete the legacy `step_1_evidence_scan`, `step_2_mitigating_context`, `score`, and `verdict` fields entirely.
- **Extract-and-Justify Schema (Mini-CoT + Escape Hatch)**: The new strict LLM schema (`BaseTDAExtraction` in `v2_core.py` and dynamically generated models) must contain exactly these 4 fields:
  1. `localized_anchors_found: list[str]`: Forces LLM to map English rules to Finnish text.
  2. `semantic_reasoning: str`: Replaces old scan/mitigating fields. LLM explains its mapping logic briefly.
  3. `exact_quote: str | None`: The physical extraction. **CRITICAL (Native Structured Outputs)**: This field MUST be typed explicitly as `str | None` using `Field(...)` (NO default values like `default=None`). This forces the API to recognize the field as universally required but nullable, adhering to strict LLM provider constraints (OpenAI `strict: true` / Gemini JSON Schema).
  4. `contextual_override: bool`: Escape hatch for implicit matches when `exact_quote` is None.
- **Strict Pydantic Config**: Ensure all dynamically generated models in `extraction_schema_factory.py` and `BaseTDAExtraction` use `model_config = ConfigDict(extra="forbid", strict=True)`. All fields must be explicitly required for cross-provider compatibility.
- **DLQ Type Support**: Ensure that any downstream components (e.g., `v2_core.py` status fields, Scoring Engines, and BFF API responses) are typed to allow a 3-state String/Enum (`"PASS"`, `"FAIL"`, `"DLQ"`) and are no longer strictly locked to `bool` (True/False). This guarantees that the database and the frontend UI will not crash due to Type Errors.

### [x] Step 2: Implement Deterministic Evaluator Function
**Target File**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- Do NOT create a new `ASTEvaluator` class. Keep the architecture flat and functional to avoid OOP over-engineering.
- Create a pure function `evaluate_extraction(extraction: BaseModel, source_text: str, is_negative_rule: bool) -> str` directly in the worker file (returning "PASS", "FAIL", or "DLQ").
  - **Dual-Track Python Validation**:
    - **Track A (Physical Match)**: If `extraction.exact_quote` exists, MUST call the existing `AnchorValidationService.validate_evidence(source_text, extraction.exact_quote)`. (Utilizes existing 1D Index Mapping & RapidFuzz). If it passes, return `"PASS"`. If `SemanticEvidenceError` is thrown, return `"FAIL"`.
    - **Track B (Semantic Override)**: If `extraction.exact_quote` is None, check `extraction.contextual_override`.
      - If `contextual_override` is True, return `"DLQ"` (Dead Letter Queue / Needs Human Review). Do NOT crash, and do NOT blindly pass.
      - If `contextual_override` is False, return `"FAIL"`.
  - **Negative Condition Handling**: If `is_negative_rule` is True, programmatically invert the PASS/FAIL logic (PASS becomes FAIL, FAIL becomes PASS), but DLQ ALWAYS remains DLQ.

### [x] Step 3: Radical Rule Stripping (Prompt Compiler)
**Target File**: `backend_v2/services/orchestrator/prompt_compiler.py`
- **CRITICAL MANDATE - Prompt Compiler Immutability (01-python-backend)**: The Prompt Compiler is a frozen architectural cornerstone. You MUST explicitly flag these changes and seek explicit USER CONFIRMATION before executing edits to this file.
- **High-Fidelity Prompting (05-llm-architecture)**: System prompts must be strictly English. Use Hybrid Prompting `<system_directive>` and ensure input data is fenced in `<source_data>`.
- Remove philosophical evaluation instructions from the system prompts (e.g., "evaluate user intent", "make a decision").
- Replace with: 
  ```xml
  <system_directive>
    <objective>You are a Blind Extraction Engine. Your task is to scan the text for the markers defined in the rule.</objective>
    <language_mandate>The physical markers in the rules are in English, but the source text is in Finnish. You MUST strictly map the English markers to their EXACT semantic physical equivalents in Finnish before scanning. Do not extract if the localized marker is missing.</language_mandate>
    <rules>
      <rule>If the exact marker is not physically present, return null for exact_quote.</rule>
      <rule>Keep your semantic_reasoning strictly under 2 sentences.</rule>
      <rule>Use contextual_override=true ONLY as a last resort if the target concept is clearly present but physically impossible to extract as an exact continuous quote.</rule>
    </rules>
  </system_directive>
  ```

### [x] Step 4: Map-Merge Orchestration
**Target File**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Native Structured Outputs Mandate**: Ensure the LLM execution explicitly enforces `strict: true` at the OpenAI API payload level for the JSON schema. This guarantees 100% token-level determinism and prevents Pydantic validation failures.
- Update the execution loop:
  1. `raw_extraction = await executor.execute_structured_task(...)`
  2. Extract `is_negative_rule` boolean from the local rule payload/metadata.
  3. `status = evaluate_extraction(raw_extraction, local_payload.text, is_negative_rule)`
  4. **Trace Continuity Injection**: The Python orchestrator MUST explicitly append the final status back into the reasoning string to preserve forensic auditability and UI compatibility (e.g., `final_reasoning = f"{raw_extraction.semantic_reasoning}\n\n[5. VALIDATION DECISION: {status}]"`).
  5. Merge `status` and `final_reasoning` back into the final dictionary sent to the database.

### [x] Step 5: TDD Tests
**Target File**: `tests/unit/orchestrator/test_chunk_worker.py` (or existing worker test file)
- **`test_deterministic_extraction_scoring`**: 
  - Test the `evaluate_extraction` pure function:
  - Provide `exact_quote = None`, `contextual_override = False`. Assert returns `"FAIL"`.
  - Provide `exact_quote = None`, `contextual_override = True`. Assert returns `"DLQ"`.
  - Provide invalid `exact_quote` triggering `SemanticEvidenceError`. Assert returns `"FAIL"`.
  - Provide valid `exact_quote`. Assert returns `"PASS"`.

## 4. Scoping
**TARGET (Modify)**: `extraction_schema_factory.py`, `prompt_compiler.py`, `chunk_worker.py`
**CONTEXT (Read-Only)**: `anchor_validation_service.py`

## 5. Testing & Quality Gate Plan
- **TDD Mandate**: Write `test_deterministic_extraction_scoring` using mocked JSON fixtures (Mocking Mandate) *before* writing domain code.
- **Universal Quality Gate (00-antigravity-core)**:
  - Run execution audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
  - Run testing audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py --test`
  - Run OpenAPI generation audit if schemas changed: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi`
- **Circuit Breaker Protocol**: If tests fail 3 times iteratively, STOP and ask for human guidance.

---
*Session Handover: To execute this Epic iteratively, start a NEW chat session and run: `/tier2-execute --plan docs/epic/tasks_epic_56/phase4_zero_variance_decoupling.md`*
