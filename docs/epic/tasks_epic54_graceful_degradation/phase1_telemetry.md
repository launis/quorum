# Phase 1: Telemetry Normalization

## Source
Epic 54: Graceful Degradation & Telemetry Hardening (Vaihe 1)

## Objective
Normalize the logging level in `AnchorValidationService` to prevent Alert Fatigue. Since validation rejections are recoverable via the `LLMTaskExecutor`'s self-healing loop, they must be logged as `WARNING` instead of `ERROR`.

## Architectural Invariants
- **Rule 1: Silent failures (01-python-backend.md)**: We are NOT silencing the exception. `SemanticEvidenceError` must still be raised. We are only changing the telemetry visualization level.
- **Rule 2: Universal Fail-Fast (00-antigravity-core.md)**: The validator still fails fast physically by raising the exception; the change is purely in observability.

## TARGET (Modify)
- `c:\src\quorum\backend_v2\services\orchestrator\anchor_validation_service.py`

## CONTEXT (Read-Only)
- `c:\src\quorum\backend_debug.log` (Reference for log strings)

## Detailed Execution Steps

### 1. Update Log Levels
Modify `AnchorValidationService.validate_extraction()`.
Locate all 4 instances of `logger.error` immediately preceding a `raise SemanticEvidenceError`.
- Trace Contradiction
- Empty Anchor
- Hallucinated Anchor
- Exact Quote not found
Change `logger.error` to `logger.warning` for each instance.

## Testing & Quality Gate Plan
- **UNIT TESTS**: No new unit tests are strictly required for a pure telemetry `WARNING` shift, but run existing unit tests to ensure syntax is valid.
- **INTEGRATION TESTS**: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/orchestrator/anchor_validation_service.py --test` to ensure coverage remains >90% and no syntax is broken.

***
## Session Handover
*Do not execute this file automatically.*
*When the user approves, they will run the Tier 2 execution workflow.*
