# Phase 2b: Polyfactory Strictness & Global Test Hardening (Part 2)

## Overview
Purge legacy fields from the second batch of test files, and update test fixtures.

## Target Files
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution_render_bug.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_blueprint.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\integration\test_epic_chain_e2e.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json#L1-L75]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="zero_legacy_fallback_hacks">Pydantic models must remain mathematically pure to the V2 spec. Do not bypass `extra='forbid'`.</constraint>

  <!-- STEP 1 removed: factory_use_construct=True is already purged from the codebase -->

  <step id="2" name="REMOVE LEGACY MOCK DATA (BATCH 2)">
    <action>Modify the target `.py` files. Purge any assignment or referencing of `evaluative_matrices`, `informational_matrices`, `content_blocks`, and `penalties_applied` in the test setup data.</action>
  </step>

  <step id="3" name="UPDATE JSON FIXTURE">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\test_data\report_data_dto_fixture.json#L1-L75]`. Delete the legacy arrays from the JSON mock.</action>
  </step>

  <step id="4" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run the GLOBAL audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` to enforce `fragmented_quality_gates_prevention`.</action>
  </step>
</execution_protocol>
```
