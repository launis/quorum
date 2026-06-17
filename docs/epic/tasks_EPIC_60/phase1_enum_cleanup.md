# Phase 1: Enum Cleanup and Retry Unification (Epic 60)

Source: Epic 60, ACTION-7

## 1. Goal
Unify the system retry configuration by removing the conflicting `FAIL_FAST_MAX_RETRIES` and strictly using `SystemConcurrency.LLM_MAX_RETRIES` across the codebase, ensuring adherence to the absolute max stringency limit of 2 retries.

## 2. Target Files
- `TARGET (Modify)`: `backend_v2/models/enums.py`
- `TARGET (Modify)`: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- `TARGET (Modify)`: `backend_v2/tests/unit/models/test_system_concurrency_compliance.py`
- `CONTEXT (Read-Only)`: `c:\src\quorum\docs\epic\epic_60_system2_reliability_audit.md`

## 3. Architectural Invariants & Hardening Mandates
- **[05_llm_architecture.md - infinite_retry_loops]**: "Enforce an absolute max stringency using `SystemConcurrency.LLM_MAX_RETRIES` (which MUST be fixed at 2)."
- **[hardening.xml - Rule 4]**: "External data enum conversions MUST be mapped exclusively using `Annotated[CustomEnum, Field(strict=False)]` aliases defined in `enums.py`."
- **[hardening.xml - Rule 84]**: "Pydantic Schema Freeze Mandate: NEVER autonomously tighten or alter the structural types..." (Applies to not changing other enums)

## 4. Implementation Steps

### Step 1: Remove `FAIL_FAST_MAX_RETRIES`
- Open `backend_v2/models/enums.py`.
- Delete the line `FAIL_FAST_MAX_RETRIES = 3` from the `SystemConcurrency` enum.

### Step 2: Update `chunk_worker.py`
- Open `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`.
- Replace instances of `SystemConcurrency.FAIL_FAST_MAX_RETRIES.value` with `SystemConcurrency.LLM_MAX_RETRIES.value`.
- Specific locations: In `max_schema_retries` and `max_logical_retries` arguments around line 471.

### Step 3: Update Unit Tests
- Open `backend_v2/tests/unit/models/test_system_concurrency_compliance.py`.
- Remove or update any assertions that test `FAIL_FAST_MAX_RETRIES`. Ensure the test suite validates `LLM_MAX_RETRIES = 2`.

### Step 4: Documentation Update
- Review `c:\src\quorum\docs\architecture\05_llm_and_hooks.md` and `06_evaluation_and_scoring.md` to ensure they reflect the maximum retry limit of 2, if they mention retry constants.

## 5. Testing & Quality Gate Plan
- **Unit Tests:** Run the modified test `test_system_concurrency_compliance.py`.
- **Universal Quality Gate:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to ensure no `FAIL_FAST_MAX_RETRIES` references remain and the codebase is clean (Ruff, MyPy, Pytest).

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/epic_60_tracker.md`
