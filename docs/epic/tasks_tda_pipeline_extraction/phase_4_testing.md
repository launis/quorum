# Phase 4: Engine Unit Tests & Post-Extraction Hardening

> **Source**: Epic 104, Phase 4 (Automated Testing) & Post-Extraction Pipeline
> **Domain**: Backend (Python)

## Goal Summary

Create comprehensive `test_tda_engine.py` mocking all 5 sub-services. Verify progress callback routing proportions and exception Anti-Corruption Layer (ACL). Execute the Post-Extraction pipeline, including proxy sunsetting, Tier 2 hardening, and Knowledge Item generation.

## Target Files

- [NEW] `backend_v2/tests/unit/services/orchestrator/engines/test_tda_engine.py`
- [MODIFY] `backend_v2/services/orchestrator/strategies/llm.py` (for proxy sunsetting/cleanup)
- [MODIFY] `.agents/rules/04_directory_reference.md`

## Proposed Changes

### 1. `test_tda_engine.py` (New File)
- **Goal**: Add unit tests for `TDAEngine`.
- **Requirements**:
  - Mock `TwoPassAtomizer`, `SlidingWindowLinker`, `EnrichedDagExecutor`, `ResultProjector`, `LLMTaskExecutor`.
  - Provide a mock `EngineExecutionRequest` containing a mock compiler, bounded client, etc.
  - Test successful execution, asserting `EngineExecutionResult` is correctly populated.
  - Test progress callback firing. The `execute` method has 4 phases of progress: 0-15%, 15-35%, 35-60%, 60-100%. Assert that `progress_callback` is invoked with correct proportional values.
  - Test exception ACL: Raise a standard `Exception("Third-party crash")` from inside a mocked sub-service and ensure it is caught and re-raised as an `AppException` with `error_code="TDA_ENGINE_ERROR"`.
  - Test Exception Bypass: Raise a pre-existing `AppException` from inside a mocked sub-service and ensure it is re-raised exactly as-is without double wrapping.
  - Use `pytest.mark.asyncio`.

### 2. Post-Extraction Pipeline Execution
- **Proxy Sunset**: Search the codebase for inline imports from `llm.py` of the TDA pipeline (e.g. `from backend_v2.services.orchestrator.two_pass_atomizer import ...`). Remove any orphaned dependencies from `llm.py` now that TDA pipeline logic has been shifted to `TDAEngine`.
- **Tier 2 Hardening**: After generating tests, run `/tier2-hardening-backend` targeted at `backend_v2/services/orchestrator/engines/` and `backend_v2/models/dtos/engine.py` to enforce strict Pydantic V2 and Push model architecture.
- **Documentation**: Update `.agents/rules/04_directory_reference.md` to document the `engines/` directory logic.
- **Knowledge Item (KI)**: Create the `ExecutionEngine Protocol` Knowledge Item to document the new decoupled strategy pattern and the `TDAEngine` execution sequence.
- **Semantic Coverage**: Run the `backend_audit_loop.py` and verify >90% coverage for the new files.

## Testing Strategy
- Unit tests will comprehensively cover all logic within `TDAEngine` via `test_tda_engine.py`.
- Run `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to ensure full integration success and verify the passing test count baseline.

## Session Handover

To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
