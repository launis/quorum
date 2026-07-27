# Phase 2a: Polyfactory Strictness & Global Test Hardening (Part 1)

## Overview
Enforce `model_construct` bypass removals and purge legacy fields from the first batch of integration and unit tests.

## Target Files
- `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\test_flattener.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_sdui_mapper_service.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="zero_legacy_fallback_hacks">Pydantic models must remain mathematically pure to the V2 spec. Do not bypass `extra='forbid'`.</constraint>

  <step id="1" name="UPDATE REPORT DATA DTO FACTORY (IMPLICIT)">
    <action>Ensure that generating `ReportDataDTO` natively inserts `layouts` data, which should happen automatically if `layouts` schema is strictly defined and test factories rely on standard generation.</action>
  </step>

  <step id="2" name="REMOVE FACTORY BYPASSES (BATCH 1)">
    <action>Modify the target files. Remove `factory_use_construct=True` from Polyfactory fixtures.</action>
    <demolish>REMOVE: `factory_use_construct=True`.</demolish>
  </step>

  <step id="3" name="REMOVE LEGACY MOCK DATA (BATCH 1)">
    <action>Modify the target files. Purge any assignment or referencing of `evaluative_matrices`, `informational_matrices`, `content_blocks`, and `penalties_applied` in the test setup data.</action>
  </step>

  <step id="4" name="UPDATE GOLDEN JSON">
    <action>In `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`, update the Golden JSON generation script (if it exists) to write updated snapshots omitting the legacy fields.</action>
  </step>

  <step id="5" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run `uv run pytest` specifically on these 4 files.</action>
  </step>
</execution_protocol>
```
