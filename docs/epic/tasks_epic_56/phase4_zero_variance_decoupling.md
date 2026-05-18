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

### Step 1: Schema Decoupling (Extraction Factory)
**Target File**: `backend_v2/extraction_schema_factory.py` & `backend_v2/models/v2_core.py`
- Modify the dynamic Pydantic schema generation.
- Remove the `score`, `validation_decision`, or `verdict` fields entirely from the schema sent to the LLM.
- The LLM schema must only require `step_1_evidence_scan`, `step_2_mitigating_context`, and `exact_quote`.

### Step 2: Implement Deterministic AST Evaluator
**Target File**: `backend_v2/services/orchestrator/ast_evaluator.py` (New or Updated)
- Create a strict Python evaluation class (`ASTEvaluator`).
- Implement the `evaluate_atom(extracted_quote: str | None, source_text: str, rule_type: str) -> bool` method:
  - If `extracted_quote` is None -> Return `False` (Fail).
  - If `extracted_quote` exists -> Pass it to `AnchorValidationService.validate_evidence(source_text, extracted_quote)`.
  - If `AnchorValidationService` throws a `SemanticEvidenceError` -> Return `False`.
  - If validation passes -> Return `True` (Pass).
- Implement Negative Condition handling: If the rule targets the *absence* of something, the boolean logic is inverted.

### Step 3: Radical Rule Stripping (Prompt Compiler)
**Target File**: `backend_v2/services/orchestrator/prompt_compiler.py`
- **CRITICAL MANDATE - Prompt Compiler Immutability (01-python-backend)**: The Prompt Compiler is a frozen architectural cornerstone. You MUST explicitly flag these changes and seek explicit USER CONFIRMATION before executing edits to this file.
- **High-Fidelity Prompting (05-llm-architecture)**: System prompts must be strictly English. Use Hybrid Prompting `<system_directive>` and ensure input data is fenced in `<source_data>`.
- Remove philosophical evaluation instructions from the system prompts (e.g., "evaluate user intent", "make a decision").
- Replace with: 
  ```xml
  <system_directive>
    <objective>You are a Blind Extraction Engine. Your ONLY task is to scan the text for the physical markers defined in the rule and extract the sentence exactly as it appears. Do not rationalize.</objective>
    <rules>
      <rule>If the exact marker is not physically present, return null for exact_quote.</rule>
    </rules>
  </system_directive>
  ```

### Step 4: Map-Merge Orchestration
**Target File**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- Update the execution loop:
  1. `raw_extraction = await executor.execute_structured_task(...)`
  2. `final_score = ast_evaluator.evaluate_atom(raw_extraction.exact_quote, local_payload)`
  3. Merge `final_score` back into the final dictionary sent to the database.

### Step 5: TDD Tests
**Target File**: `tests/unit/orchestrator/test_ast_evaluator.py` (New file)
- **`test_ast_deterministic_scoring`**: 
  - Mock an LLM returning `exact_quote = None`. Assert AST returns `False`.
  - Mock an LLM returning an `exact_quote` that is not in the source text. Assert AST catches the `SemanticEvidenceError` and returns `False`.
  - Mock an LLM returning a valid `exact_quote`. Assert AST returns `True`.

## 4. Scoping
**TARGET (Modify)**: `extraction_schema_factory.py`, `ast_evaluator.py`, `prompt_compiler.py`, `chunk_worker.py`
**CONTEXT (Read-Only)**: `anchor_validation_service.py`

## 5. Testing & Quality Gate Plan
- **TDD Mandate**: Write `test_ast_deterministic_scoring` using mocked JSON fixtures (Mocking Mandate) *before* writing domain code.
- **Universal Quality Gate (00-antigravity-core)**:
  - Run execution audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ast_evaluator.py`
  - Run testing audit: `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/ast_evaluator.py --test`
  - Run OpenAPI generation audit if schemas changed: `uv run python scripts/backend_audit_loop.py backend_v2/models/v2_core.py --openapi`
- **Circuit Breaker Protocol**: If tests fail 3 times iteratively, STOP and ask for human guidance.

---
*Session Handover: To execute this Epic iteratively, start a NEW chat session and run: `/tier2-execute --plan docs/epic/tasks_epic_56/phase4_zero_variance_decoupling.md`*
