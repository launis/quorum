# Phase 4: Soft Delete API & Trace Events

Source: Epic Phase 5.3 and Appendix D.3

## Target Files (Modify)
- `backend_v2/models/state.py`
- `backend_v2/database/repositories/execution.py`
- `backend_v2/services/execution.py`
- `backend_v2/api/v2/execution.py`

## Requirements
1. **Trace Event Model (`state.py`)**: 
   - Ensure `TraceEvent` supports an `"evidence_override"` event type. The content should store: `evq_id`, `user_rejected: bool`, `rejection_reason: str`, `rejected_by`, `rejected_at`.
2. **Repository Layer**:
   - Implement `append_trace_event(execution_id, trace_event)` in `execution.py` repository if it doesn't exist, or ensure we can atomically append to the `execution_trace` array in the database.
3. **Service Layer (`execution.py` service)**:
   - Implement `reject_evidence_quote(execution_id: str, evq_id: str, reason: str, user_uid: str)`.
   - Validation: Verify execution exists and the user has correct privileges (MEMBER for own execution, ADMIN/ROOT for any).
   - Append the `"evidence_override"` TraceEvent to the database via the repository.
4. **API Router (`execution.py` api)**:
   - Implement `PUT /api/v2/execution/executions/{id}/evidence/{evq_id}/reject`.
   - Payload: `{"rejection_reason": "..."}`.
   - Return 200 OK with status.

## Architectural Invariants & Hardening Mandate
- **Rule 32 (anemic_routers)**: Ensure the API router only parses HTTP input and calls `ExecutionService.reject_evidence_quote()`. No RBAC checks in the router!
- **Rule 12 (no_naked_dicts_in_state)**: Ensure the `evidence_override` event uses a strict Pydantic DTO when appended to the trace, not a naked `dict`.
- **Rule 74 (polymorphic_parsing_mandate)**: Repository layer must return `dict[str, Any]` and handle DB specifics.
- **Rule 18 (rfc7807_dual_reporting_strict)**: Raise `AppException(error_code=ErrorCodes.FORBIDDEN...)` if RBAC checks fail.

## Documentation Update
Update `docs/architecture/09_data_persistence.md` regarding the Append-Only approach for `evidence_override` events.

## Testing & Quality Gate Plan
- **Unit Tests**: Test RBAC enforcement in `ExecutionService.reject_evidence_quote()`.
- **Integration Tests**: Test `PUT /api/v2/execution/executions/{id}/evidence/{evq_id}/reject` to ensure the event is successfully appended to the DB.
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/api/v2/execution.py backend_v2/services/execution.py --openapi`

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
