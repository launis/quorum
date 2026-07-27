# Phase 2c: Negative Testing & Hardening (Batch 3)

## Overview
Add explicit negative tests verifying that the newly strict `ReportDataDTO` natively rejects legacy fields and ensure slop penalty edge cases are safely handled.

## Target Files
- `@[c:\src\quorum\backend_v2\tests\unit\models\test_v2_core.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\test_worker.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="anti_happy_path_mandate">For every positive test case, you MUST write at least 2 negative test cases covering boundary values or type violations.</constraint>

  <step id="1" name="NEGATIVE TESTING: REPORT DATA DTO">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\models\test_v2_core.py]`. Add explicit negative test cases to prove `ReportDataDTO` throws a `ValidationError` if `evaluative_matrices`, `content_blocks`, or `penalties_applied` are present.</action>
  </step>

  <step id="2" name="NEGATIVE TESTING: WORKER SLOP DETECTION">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\test_worker.py]`. Finish the assertions for the existing `test_generate_pdf_task_slop_penalty_ignores_metadata` test to strictly verify the penalty logic doesn't crash. Then, add a NEW negative test verifying that slop penalty detection safely ignores layouts where `metadata` exists but is missing the `"penalty_type"` key.</action>
  </step>

  <step id="3" name="NEGATIVE TESTING: LINGUISTICS HOOK">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py]`. Since `scan_report_for_slop` already has negative tests, add negative test cases for `detect_performative_patterns`: verify it handles missing `chat_log_user_only` inputs gracefully, and verify it handles a missing/empty Lexicon configuration from the system database.</action>
  </step>

  <step id="4" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run `uv run pytest` specifically on these 3 python test files.</action>
    <action>Run the full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
  </step>
</execution_protocol>
```
