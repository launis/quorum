# Phase 2: Circuit Breaker & Null Object Pattern

## Source
Epic 54: Graceful Degradation & Telemetry Hardening (Vaihe 2 & 3)

## Objective
Implement Graceful Degradation in the `LLMTaskExecutor`. When the AI exhausts its maximum logical retries (`max_logical_retries`), instead of throwing a `WorkflowExecutionError` and crashing the entire pipeline, the executor must intercept the failure and return a Null Object matching the Pydantic schema, allowing the workflow to continue.

## Architectural Invariants
- **Rule 1: The Duct Tape Ban (00-antigravity-core.md)**: We are NOT swallowing the error silently. We log an explicit `WARNING`/`ERROR` stating the AI failed, and we explicitly document the failure in the output schema's `justification` field.
- **Rule 2: Zero-Compromise Math Boundary (01-python-backend.md)**: The fallback payload MUST use `None` (or `null`) for the score, NEVER `0`, to ensure `ScoringHook` legitimately skips the atom without corrupting the mathematical averages.
- **Rule 3: Pydantic Pure Hydration (01-python-backend.md)**: We must dynamically construct the fallback using the `target_schema` passed to the executor.

## TARGET (Modify)
- `c:\src\quorum\backend_v2\services\llm_task_executor.py`

## CONTEXT (Read-Only)
- `c:\src\quorum\backend_v2\hooks\scoring.py` (Validation that `raw_score=None` is skipped)

## Detailed Execution Steps

### 1. Implement Null Object Fallback in Self-Healing Loop
In `backend_v2/services/llm_task_executor.py` within `execute_structured_task()`:
- Locate the exception block catching `SemanticEvidenceError` or `ValidationError`.
- Locate the condition where `current_logical_retries >= max_logical_retries`.
- Currently, it logs an error and raises `WorkflowExecutionError`.
- Modify this block to act as a Circuit Breaker:
  - Log an explicit error: `logger.error(f"Maximum self-healing retries ({max_logical_retries}) exhausted for step {step_id}. Injecting Null Object Fallback.")`
  - Construct a dynamic fallback dict that conforms to the base requirements. Since `target_schema` is usually `Step_XXX_Response` which contains nested blocks (like `_evaluative_matrices`), we need to return an object that won't crash the orchestrator.
  - Wait, the `target_schema` is the entire step response. If the LLM failed to build the entire step, we might need a generic fallback that instantiates `target_schema.model_construct()` with empty/None properties.
  - Or, if it's too complex to dynamically guess nested schemas, we can leverage `model_construct()` and inject a top-level `justification` if available, or rely on `ScoringHook` dropping `None` values.
  - Actually, if we use `target_schema.model_construct()`, it creates a shell object. We should try to populate `extensions={"error": "LLM Validation Failed"}` if possible, or just rely on the empty fields.

### 2. Documentation Update
- Update `c:\src\quorum\docs\architecture\system_architecture_manifesto_2026.md` (or a relevant architectural doc) to formalize the "Graceful Degradation via Null Object Pattern" logic, ensuring future developers don't try to revert to hard crashes for LLM extraction failures.

## Testing & Quality Gate Plan
- **UNIT TESTS**: Create/update a unit test in `tests/unit/services/test_llm_task_executor.py` that mocks the LLM throwing 3 `SemanticEvidenceError`s, and assert that it returns a fallback Pydantic object instead of throwing `WorkflowExecutionError`.
- **INTEGRATION TESTS**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/llm_task_executor.py --test`

***
## Session Handover
*Do not execute this file automatically.*
*When the user approves, they will run the Tier 2 execution workflow.*
