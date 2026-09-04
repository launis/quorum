# Task Tracking: SSE Stream Deserialization Failure & Execution Crash Fix

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Bug Fix Plan: @[bug_fix_plan.md]

## Regression Tests Status (Red Phase Confirmed)
- [x] Backend Red Test: `backend_v2/tests/unit/services/test_execution.py::test_stream_status_handles_error_without_yielding_malformed_execution_record` (FAILED with `ValidationError` on malformed dict payload)
- [x] Frontend Red Test: `client_app_v2/test/features/execution/controllers/execution_controller_test.dart` (FAILED with `CheckedFromJsonException` on `id` null cast)

## Implementation Tasks (Quarantine Handover to Tier 2)
- [x] **Phase 1: Backend SSE Resilience & Typed Stream Protocol**
  - [x] Step 1.1: Move `settings = get_settings()` outside the polling loop in `@[backend_v2/services/execution.py]`.
  - [x] Step 1.2: Implement retry tolerance (up to 3 consecutive read attempts with exponential backoff) for transient database lock/read misses in `stream_status`.
  - [x] Step 1.3: If terminal error occurs, emit standards-compliant SSE error event (`event: error\ndata: {"error_code": "SSE_STREAM_INTERRUPTED", "message": "..."}\n\n`) instead of naked dict masquerading as `data: ` ExecutionRecord.

- [x] **Phase 2: Frontend Execution Controller SSE Error Defense**
  - [x] Step 2.1: In `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`, inspect incoming `update` before attempting `ExecutionRecord.fromJson`.
  - [x] Step 2.2: If `update.containsKey('error')` or `update.containsKey('error_code')`, log structured error and set `state = AsyncValue.error(AppException.server(...), stack)` instead of failing inside JSON deserializer.
  - [x] Step 2.3: Wrap `ExecutionRecord.fromJson` with specific error translation to prevent raw `CheckedFromJsonException` from mapping to misleading "Tarkista syöttämäsi tiedot".

- [x] **Phase 3: Verify Regression Tests (Green Phase)**
  - [x] Step 3.1: Run `uv run pytest backend_v2/tests/unit/services/test_execution.py::test_stream_status_handles_error_without_yielding_malformed_execution_record` and verify it passes.
  - [x] Step 3.2: Run `flutter test test/features/execution/controllers/execution_controller_test.dart` in `client_app_v2` and verify it passes.

- [x] **Phase 4: Universal Quality Gates**
  - [x] Step 4.1: Run `uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py`
  - [x] Step 4.2: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/controllers/execution_controller.dart`

# Session Handover Context
- **Achieved**:
  1. Refactored `stream_status` in `backend_v2/services/execution.py` to hoist settings out of the polling loop, add 3-attempt retry tolerance with backoff for transient `ResourceNotFoundError`, and yield RFC-compliant `event: error\ndata: ...` SSE events rather than malformed `data: {"error": ...}` JSON.
  2. Added `AppException.server` helper constructor in `client_app_v2/lib/core/error/app_exception.dart`.
  3. Hardened `ExecutionController._connectToStream` in `client_app_v2/lib/features/execution/controllers/execution_controller.dart` to intercept SSE error payloads before deserialization and wrap deserialization errors into typed `AppException.network` with `SSE_DESERIALIZATION_FAILED` code.
  4. Both backend and frontend regression tests are GREEN and verified.
  5. Universal quality gate loops passed 100% across Ruff, MyPy, Dart Analyzer, and Pytest.
- **Learned**:
  1. Transient file/db locks during background worker completion can cause transient read misses; handling transient misses with retry tolerance in the generator prevents premature stream termination.
  2. On Flutter client, inspecting incoming SSE envelopes before deserializing avoids leaking unhandled `CheckedFromJsonException` into Riverpod state and prevents misleading validation error screens.
- **Remaining**:
  - Perform atomic git commit for the verified fix.
