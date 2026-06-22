# EPIC 81 - Phase 1: Diagnostic & Classification

## Source Material Traceability
- **Source**: Epic Phase 1, Step 1 & 2
- **Epic Requirements**: Add `_is_transient_chunk_error()` classifier to `chunk_worker.py`, and add DLQ telemetry to `diff_executions.py` report output.

## Architectural Invariants & Hardening Mandates
- **Invariant (00-antigravity-core.md, Rule 92 - Universal Fail-Fast)**: Do not intercept and silence structural errors. Non-transient exceptions must be explicitly routed to DLQ or crash loudly.
- **Hardening Rule 17 (the_duct_tape_ban)**: "God Blocks" (`except Exception: pass`) are ruthlessly forbidden. Errors must be properly evaluated, and all logging must preserve the full traceback context.
- **Hardening Rule 21 (zero_type_ignore_shortcuts)**: Do not use inline `# type: ignore` directives without explicitly stating the error code and an architectural justification.
- **Hardening Rule 19 (dlq_arq_fallback_routing)**: TaskGroup or ChunkWorker errors must be routed to the Dead Letter Queue by yielding `{"_dlq_status": "FAILED/DLQ"}`.

## TARGET (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- `scratch/diff_executions.py`

## CONTEXT (Read-Only)
- `backend_v2/llm/provider.py` (For comparative transient LLM error checks)

## Sequence Milestones

### Milestone 1: Implement `_is_transient_chunk_error` Classifier
- **Target**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Requirement**: Add a new static helper or module-level function `_is_transient_chunk_error(exc: BaseException) -> bool` inside the file or on `ChunkWorker`.
- **Implementation Spec**:
  ```python
  def _is_transient_chunk_error(exc: BaseException) -> bool:
      """Classify whether a chunk-level error is transient (retryable) or structural (terminal).

      Transient errors include network failures, rate limits, and upstream unavailability.
      Structural errors include Pydantic validation failures, configuration errors, and security violations.
      """
      import litellm

      TRANSIENT_TYPES = (
          asyncio.TimeoutError,
          ConnectionError,
          getattr(litellm, "APIConnectionError", type(None)),
          getattr(litellm, "RateLimitError", type(None)),
          getattr(litellm, "ServiceUnavailableError", type(None)),
          getattr(litellm, "Timeout", type(None)),
      )
      TRANSIENT_KEYWORDS = ("APIConnectionError", "ServiceUnavailable", "Timeout", "Resource exhausted")

      if isinstance(exc, ExceptionGroup):
          return all(_is_transient_chunk_error(inner) for inner in exc.exceptions)

      if isinstance(exc, TRANSIENT_TYPES):
          return True

      error_str = str(exc)
      return any(keyword in error_str for keyword in TRANSIENT_KEYWORDS)
  ```
- **Rule Enforcement**: Ensure we use `isinstance()` for the type checking properly. Do NOT catch `Exception` blindly to ignore errors. Follow `ExceptionGroup` recursive unpacking properly.

### Milestone 2: Enhance diff_executions.py with DLQ Telemetry
- **Target**: `scratch/diff_executions.py`
- **Requirement**: Enhance the reporting output to explicitly count and log atoms dropped to the Dead Letter Queue (DLQ).
- **Implementation Spec**: In `diff_executions.py`, after calculating the "Tekniset virheet (Crash)" line (lines 460-461), add logic to count `"_dlq_status": "FAILED/DLQ"` occurrences in `raw_data` and write it to the report output.
  ```python
  dlq_count = raw_data.count('"_dlq_status": "FAILED/DLQ"')
  f.write(f'  - **DLQ-pudotetut atomit:** `{dlq_count}` kpl\\n')
  ```

### Milestone 3: Update Architecture Documentation
- **Target**: `docs/architecture/execution_orchestration.md` (or equivalent system reliability docs)
- **Requirement**: Document the new transient error classification boundary in the chunk execution phase, explicitly stating what constitutes a transient error vs structural error.

## Testing Strategy & Verification Plan
1. **Unit Tests**:
   - Create unit tests for `_is_transient_chunk_error` ensuring both base Python network errors and mocked `litellm` exceptions (e.g. `APIConnectionError`) correctly return `True`.
   - Ensure `ExceptionGroup` unwrapping evaluates all nested exceptions properly.
   - Run tests using the Universal Quality Gate.
2. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py --test
   ```

---

## Session Handover

<session_handover>
This phase is ready for execution.
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_81_Transient_Error_Resilience_and_DLQ_Classification_tracker.md`
</session_handover>
