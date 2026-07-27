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
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\test_worker.py]`. Add negative tests verifying that slop penalty detection safely ignores layouts where `metadata` is `None` or missing `"penalty_type"`.</action>
  </step>

  <step id="3" name="NEGATIVE TESTING: LINGUISTICS HOOK">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py]`. Add negative tests for missing/empty `layouts`.</action>
  </step>

  <step id="4" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run `uv run pytest` specifically on these 3 python test files.</action>
    <action>Run the full backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
  </step>
</execution_protocol>
```
