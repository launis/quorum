# Phase 4: Formalizing Questionnaire Parsing

## 1. Description and Objective
**Epic 34: Global Hooks Zero-Compromise Hardening.**
The `input_processing.py` hook currently natively guesses if input is a questionnaire bypassing Pydantic with `if isinstance(val, dict) and any(str(k).startswith("q"))`. This is non-deterministic and fragile. We need to implement a strict `GuidedReflectionInputDTO` to handle this deterministically.

## 2. File Scoping
- **TARGET (Modify):** 
  - `backend_v2/hooks/input_processing.py`
  - `backend_v2/models/dtos/inputs.py` (or similar file for `GuidedReflectionInputDTO`)
- **CONTEXT (Read-Only):** 
  - None

## 3. Implementation Steps
1. **Define DTO:** Implement a `GuidedReflectionInputDTO(BaseModel)` with explicit `questions: list[QuestionAnswerPair]` (or equivalent).
2. **Serialization Logic:** Implement `.to_markdown()` inside the model to serialize markdown deterministically (`### Q:` formatting), removing manual string-formats from the hook logic.
3. **Remove Guessing:** Remove the `isinstance(dict) and startswith("q")` markdown hack from `input_processing.py` and rely strictly on model validation.

## 4. Verification & Quality Gate Plan
- **Unit Testing:** Validate `GuidedReflectionInputDTO.to_markdown()` serialization and ensure invalid questionnaire formats raise validation errors instead of silently bypassing.
- **Audit Loop Execution:** `uv run python scripts/backend_audit_loop.py backend_v2/hooks/input_processing.py --test`
