# Phase 3: Hallucination Shield & Fail-Fast Validation

## Context
**Epic:** `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`

## Architectural Invariants
- **Rule 1:** Strict Pydantic Cross-Field Validation (`01-python-backend.md`).
- **Rule 2:** Model Cascading (`01-python-backend.md`). Use `LLMClient.from_strategy()` and `LLMTaskExecutor.execute_structured_task()`. Direct SDK calls are banned.
- **Rule 3:** The No-Legacy Mandate (`00-antigravity-core.md`). No silent `is_true` overrides.

## Targets (Modify)
- `c:\src\quorum\backend_v2\models\v2_core.py` (or specific dynamic schema DTOs handling responses in PromptCompiler)
- `c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py` (CREATE/MODIFY)
- `c:\src\quorum\backend_v2\services\orchestrator\llm_task_executor.py` 

## Context (Read-Only)
- `c:\src\quorum\docs\epic\epic48_atomization_refactor_plan 2.md`
- `c:\src\quorum\.agents\rules\00-antigravity-core.md`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

## Milestones
### 1. DTO Structure Updates
- [x] Update the execution response evaluation models (e.g. `AtomResponse` or similar dynamically created model).
- [x] Ban `is_true`. Replace with `rule_satisfied: bool` and `evidence_found: bool`.
- [x] Add to result model: `exact_quote: str`, `pre_quote_anchor: str`, `post_quote_anchor: str`, `reasoning_trace: str`.
- [x] Implement Cross-Field Validation via `@model_validator(mode='after')`:
  - [x] If `evidence_found == True`: `exact_quote` MUST NOT be empty.
  - [x] If `evidence_found == False`: `exact_quote` MUST be exactly `""`.

### 2. AnchorValidationService & RapidFuzz
- [x] Create or update `AnchorValidationService` to be a pure TDD-testable service without `@model_validator` side effects.
- [x] **Phase 1 (Normalization):** Regex `[^a-z0-9]`, lowercasing, NFKC-normalization for both PDF source and LLM anchor.
- [x] **Phase 2 (O(1) Anchoring):** Use `RapidFuzz` for finding `exact_quote` or anchors against normalized text. (Performance exception: C/C++ extension is allowed here).

### 3. Semantic Fallback Cascade
- [x] In `llm_task_executor.py` or the validation flow: If deterministic RapidFuzz string search fails, do NOT route directly to DLQ.
- [x] Trigger a fast, cheap LLM call (e.g., GPT-4o-mini NLI prompt "Tarkoittaako väite A samaa kuin lause B tässä PDF-kontekstissa? Y/N").
- [x] MUST use `LLMClient.from_strategy()` and `LLMTaskExecutor.execute_structured_task()` with XML Fencing. No direct SDK calls.
- [x] If AI evaluation also fails, route to DLQ.

### 4. Evidence Cleanup
- [x] Replace `exact_quote` with the database-clipped `pdf_anchor_block` to ensure UI parity and PDF-highlighter compatibility.

## Testing & Quality Gate Plan
- [x] **Unit Tests:** `tests/unit/test_anchor_validation.py` (TDD tested without LLM), testing RapidFuzz and normalization logic.
- [x] **Integration Tests:** Model Cascade fallback using LLM Mocks via `backend_v2/llm/mock.py`.
- [x] **Execution:** Run `uv run python scripts/backend_audit_loop.py backend_v2/[files] --openapi --test`

## Documentation Update
- [x] Document AnchorValidationService in `c:\src\quorum\docs\architecture\06_evaluation_and_scoring.md`.

---
**Session Handover:**
To execute this plan, start a NEW chat session and run: `/tier2-hardening-backend @[c:\src\quorum\docs\epic\tasks_epic48\phase3_validation_cascade.md]`
