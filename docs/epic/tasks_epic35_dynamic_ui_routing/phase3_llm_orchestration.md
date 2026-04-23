# Epic 35 Phase 3: LLM Refactor & Monolith Dismantling

## Context vs Target
*   **TARGET (Modify):** 
    *   `backend_v2/services/orchestrator/strategies/llm.py`
    *   `tests/unit/services/orchestrator/strategies/test_llm.py`
*   **CONTEXT (Read-Only):**
    *   `backend_v2/services/orchestrator/context_router.py`

## Tasks

1.  **[x] Explicit Input Routing (Remove Hardcoded Mappings)**
    *   Remove logic `for ei in context.expected_inputs:` that forcibly pushes files to the AI context.
    *   AI inputs must now solely resolve through `$inputs...` dot-notation using `ContextRouter` (`resolve_dot_notation`).

2.  **[x] Namespace Resolution & Limits (`$steps` Overhaul)**
    *   Remove `if path in ("steps", "$steps"): continue` bypass.
    *   Apply rigorous token checks using `litellm.token_counter()`.
    *   If token max is breached, DO NOT silently truncate. Raise `TokenLimitExceededError` natively.

3.  **[x] Synthesis Validation & Retries**
    *   Integrate `ContextRouter` strictly for generating LLM context `LightweightMatrixOutput.model_dump_json()`. Wrap in `<matrix_data>` XML tags.
    *   Replace freeform `run_chat` reporting logic with `run_structured_task(..., response_model=list[AnySduiBlock], max_retries=3)`.
    *   This forces Socratic Self-Healing if the AI hallucinates SDUI formats.

## Verification & Quality Gate Plan
*   **Unit Tests:** Update `test_llm.py` with mock LLM calls validating that explicit inputs are mapped, unmapped expected_inputs are ignored, and token breaches correctly raise exceptions.
*   **Audit Loop:** `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test`
