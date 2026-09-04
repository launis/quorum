# Task Tracking: ExecutionController SSE Stream Error Misclassification Fix

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

Bug Fix Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\1bb3b854-7e4b-48c5-9c98-df23bfb2161b\bug_fix_plan.md]

## Regression Tests Status (Green Phase Confirmed)
- [x] Test 1: `ExecutionController handles SSE update containing error: null without misclassifying as stream error` (PASSED)
- [x] Test 2: `ExecutionController handles failed ExecutionRecord containing domain error without misclassifying as stream error` (PASSED)

## Implementation Tasks
- [x] **Step 1: PRE_IMPLEMENTATION_CLEANUP_AND_FIX_SSE_ERROR_DEFENSE**
  - [x] Cancel existing `_sseSubscription?.cancel()` at the start of `_connectToStream` in `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`.
  - [x] Replace `containsKey('error')` check with explicit discriminators: `hasExplicitErrorCode` (`update['error_code'] != null && update['error_code'].toString().trim().isNotEmpty`) and `isSseErrorPayload` (`update['error'] != null && update['error'].toString().trim().isNotEmpty && !update.containsKey('id')`).
- [x] **Step 2: VERIFY_REGRESSION_TESTS_GREEN**
  - [x] Run `flutter test test/features/execution/controllers/execution_controller_test.dart` and verify all 4 tests pass (0 failures).
- [x] **Step 3: FRONTEND_QUALITY_GATE**
  - [x] Run `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/controllers/execution_controller.dart` (Exit code 0, 0 issues).
  - [x] Run `flutter test test/features/execution/` (All 71 feature tests pass).

# Session Handover Context
- **Achieved**:
  1. Fixed the critical bug in `ExecutionController._connectToStream` (`client_app_v2/lib/features/execution/controllers/execution_controller.dart`) where `update.containsKey('error')` evaluated to `true` for standard `ExecutionRecord` payloads containing `"error": null`.
  2. Implemented strict discriminator logic:
     - `hasExplicitErrorCode`: Checks that `error_code` exists and is non-empty.
     - `isSseErrorPayload`: Checks that `error` exists, is non-empty, AND that `id` is not present (distinguishing transport-level SSE error envelopes from domain-level `ExecutionRecord`s with domain errors).
  3. Added subscription hygiene with `_sseSubscription?.cancel()` at the beginning of `_connectToStream` to prevent stream listener leaks across reconnects.
  4. Both regression tests and the full execution test suite (71 tests) pass 100% green.
  5. Dart formatting and static analysis clean with 0 warnings/errors.
- **Learned**:
  1. In Dart, `Map.containsKey('field')` returns `true` even when `map['field'] == null`. For nullable Pydantic domain models serialized with `None -> null`, key presence checks cause catastrophic misclassification. Discriminators must verify non-null and non-empty values.
  2. Domain models containing `error: str | None` (like `ExecutionRecord`) must be distinguished from transport error envelopes by the presence of primary keys (`id`).
- **Remaining**:
  - Atomic git commit of the verified changes.
