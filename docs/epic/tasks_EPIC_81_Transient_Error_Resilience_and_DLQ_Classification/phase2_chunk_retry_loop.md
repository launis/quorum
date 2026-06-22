# EPIC 81 - Phase 2: Chunk-Level Retry Loop

## Source Material Traceability
- **Source**: Epic Phase 2, Step 1 & 2
- **Epic Requirements**: Wrap the chunk execution in a retry loop (max 2 attempts). Modify the DLQ routing in `chunk_worker.py` to utilize `_is_transient_chunk_error`. Track `_dlq_retry_count` in the resulting payload and log recovery in `llm.py`.

## Architectural Invariants & Hardening Mandates
- **Invariant (01-python-backend.md, Rule 90 - async_io_lock_isolation_mandate)**: Do not lock I/O bound retry loops inappropriately. Retries must backoff via `asyncio.sleep()`.
- **Hardening Rule 19 (dlq_arq_fallback_routing)**: ChunkWorker errors must be routed to DLQ only after transient retries are exhausted.
- **Hardening Rule 17 (the_duct_tape_ban)**: Do not silently retry forever. Ensure explicit limits (max 2 attempts) and exponential backoff are respected.
- **Hardening Rule 24 (python_314_modern_syntax)**: Use modern exception grouping and typing when handling errors during the retry block.

## TARGET (Modify)
- `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- `backend_v2/services/orchestrator/strategies/llm.py`

## CONTEXT (Read-Only)
- `backend_v2/models/enums.py` (Check `SystemConcurrency` bounds if needed)

## Sequence Milestones

### Milestone 1: Implement Chunk-Level Retry Loop in ChunkWorker
- **Target**: `backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py`
- **Requirement**: Wrap the primary chunk execution block inside `process_chunk` (approx lines 382-616) in a retry loop.
- **Implementation Spec**:
  ```python
  MAX_CHUNK_RETRIES = 2
  attempt = 0
  
  while attempt <= MAX_CHUNK_RETRIES:
      try:
          # ... existing chunk processing logic (executor calls, map-merge, pydantic validation)
          # Ensure _dlq_retry_count is injected if attempt > 0 before returning
          if attempt > 0:
              chunk_final["_dlq_retry_count"] = attempt
          return chunk_final, chunk_usage, chunk_traces, prompt_context
          
      except (LLMSchemaValidationError, AppException, ExceptionGroup, Exception) as e:
          if _has_programmatic_errors(e):
              raise e

          if _is_transient_chunk_error(e) and attempt < MAX_CHUNK_RETRIES:
              attempt += 1
              backoff_seconds = min(10 * (2 ** (attempt - 1)), 60)
              logger.warning("[ChunkWorker] Transient error detected. Retrying chunk (attempt %d/%d)...", attempt, MAX_CHUNK_RETRIES)
              await asyncio.sleep(backoff_seconds)
              continue  # retry the chunk
          
          # Only route to DLQ if error is structural OR retries exhausted
          # ... existing DLQ routing logic ...
          chunk_final["_dlq_retry_count"] = attempt
          return chunk_final, None, [], prompt_context
  ```
- **Constraint**: Ensure `_dlq_retry_count` is captured in the response payload.

### Milestone 2: Telemetry in Orchestrator (llm.py)
- **Target**: `backend_v2/services/orchestrator/strategies/llm.py`
- **Requirement**: Track DLQ events and log transient retry recoveries.
- **Implementation Spec**:
  In `LLMNodeStrategy.execute`, when parsing `c_final` from chunks (around line 476 and 507), add:
  ```python
  if c_final.get("_dlq_retry_count", 0) > 0 and c_final.get("_dlq_status") != "FAILED/DLQ":
      logger.info(
          "[Orchestrator] Chunk recovered after %d transient retries.",
          c_final["_dlq_retry_count"],
      )
  ```

### Milestone 3: Update Architecture Documentation
- **Target**: `docs/architecture/workflow_system_design.md` or equivalent
- **Requirement**: Document the Multi-Tier Retry strategy for chunks, emphasizing the 2-attempt Transient Retry fallback before DLQ routing.

## Testing Strategy & Verification Plan
1. **Unit Tests**:
   - Create a test `test_chunk_retry_on_transient_error` that mocks `LLMTaskExecutor.execute_structured_task` to throw an `APIConnectionError` on the first call, and succeed on the second. Assert that `_dlq_retry_count == 1`.
   - Create a test `test_structural_error_routes_to_dlq` verifying that a pure structural error bypasses the retry loop and goes straight to DLQ.
2. **Quality Gate Command**:
   ```bash
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm_execution/chunk_worker.py --test
   uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/strategies/llm.py --test
   ```

---

## Session Handover

<session_handover>
This phase is ready for execution.
To execute this Epic iteratively, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_81_Transient_Error_Resilience_and_DLQ_Classification_tracker.md`
</session_handover>
