# Implementation Plan: Phase 2 - Sequential Worker & Deterministic Lexical Validation (EPIC 56)

## 1. Goal
Refactor the worker logic to be entirely sequential, eliminate all retry loops (Fail-Fast), and implement deterministic 1D index mapping with RapidFuzz.

## 2. Architectural Rules & Invariants
- **Rule 1: No Infinite Retry Loops**: LLM retries must not exceed 2. No `while` retry fuzzing.
- **Rule 2: Fail-Fast**: Let the Pydantic parser fail instantly.
- **Rule 3: Duct Tape Ban**: Do not catch exceptions blindly. Route failures to Dead Letter Queue (DLQ) explicitly.
- **Source**: Epic Phase 2, Phase 4 (Rules 1, 3), Phase 5 (Tests 2, 3).

## 3. Implementation Steps

### Step 1: Remove Retry Loops & Make Sequential
**Target File**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py` (and related workers)
- Remove any existing `while` retry loops for LLM failures.
- Make the Arq worker sequence purely sequential: `await llm_call()` -> `lcs_validate()`.
- Ensure the Arq task is registered with `max_tries=1` to prevent infrastructure-level retry storms.

### Step 2: Deterministic 1D Index Mapping & RapidFuzz
**Target File**: `backend_v2/services/orchestrator/anchor_validation_service.py`
- Replace Cosine Similarity with `fuzz.partial_ratio_alignment` from `rapidfuzz`.
- Implement a 1D Index Mapping:
  - Normalize text (remove whitespace/newlines).
  - Create `index_map[norm_idx] = orig_idx`.
- If `contextual_override` is True, skip lexical validation.
- If `contextual_override` is False, use `fuzz.partial_ratio_alignment`. If score > 85%, use the `index_map` to extract the EXACT original snippet (with original whitespace/newlines) from the raw text and override `exact_quote`.

### Step 3: Graceful DLQ Routing
**Target File**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- Catch `ValidationError` and API errors at the worker level.
- Log the atom as `FAILED/DLQ` in the database with the mathematical reason (e.g., `lcs_score=X, threshold=0.85`).
- **Return silent success** (`return`) so the exception does not bubble up to the Arq engine and trigger a task retry.

### Step 4: TDD Tests
**Target Files**: `tests/unit/services/test_anchor_validation.py`, `tests/integration/test_worker_dlq.py`
- **`test_lcs_normalization_retains_raw_pdf_mapping`** (Unit):
  - Pass chunk: `"Tämä  on\n\t tär\xadkeä \u00ADsopimus."`.
  - Pass extracted `exact_quote`: `"Tämä on tärkeä sopimus."`.
  - Assert RapidFuzz score is 100.0%.
  - Assert the service overrides and returns the original ugly string: `"Tämä  on\n\t tär\xadkeä \u00ADsopimus."`.
- **`test_pydantic_max_length_fail_fast_and_dlq_routing`** (Integration):
  - Mock LLM response with an `exact_quote` of 1501 chars.
  - Assert `.model_validate_json()` raises `ValidationError`.
  - Assert Arq worker catches it, updates state to `FAILED/DLQ`, and does NOT retry (`llm_call` count == 1).

### Step 5: Documentation Update
**Target File**: `docs/architecture/engine/hazards.md`
- Document the 1D mapping strategy and DLQ Arq fallback logic.

## 4. Scoping
**TARGET (Modify)**: `backend_v2/services/orchestrator/anchor_validation_service.py`, `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`, `tests/unit/...`, `tests/integration/...`
**CONTEXT (Read-Only)**: None

## 5. Testing & Quality Gate Plan
- **UNIT TESTS**: Run `test_lcs_normalization_retains_raw_pdf_mapping` and `test_pydantic_max_length_fail_fast_and_dlq_routing`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test`.

---
*Session Handover: To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_56_vaihtoehtob_tracker.md`*
