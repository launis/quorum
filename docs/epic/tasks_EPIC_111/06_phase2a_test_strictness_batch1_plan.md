# Phase 2a: Polyfactory Strictness & Global Test Hardening (Part 1)

## Overview
Enforce `model_construct` bypass removals and purge legacy fields from the first batch of integration and unit tests.

## Target Files
- `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]` (Modify)
- `@[c:\src\quorum\backend_v2\tests\unit\services\test_execution.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="zero_legacy_fallback_hacks">Pydantic models must remain mathematically pure to the V2 spec. Do not bypass `extra='forbid'`.</constraint>

  <step id="1" name="UPDATE REPORT DATA DTO FACTORY (IMPLICIT)">
    <action>Ensure that generating `ReportDataDTO` natively inserts `layouts` data, which should happen automatically if `layouts` schema is strictly defined and test factories rely on standard generation.</action>
  </step>

  <step id="2" name="REMOVE FACTORY BYPASSES &amp; LEGACY MOCK DATA">
    <action>In `test_sdui_semantic_parity.py`, completely remove `factory_use_construct=True` from Polyfactory fixtures to restore strict Pydantic V2 instantiation. Additionally, since the factory will now enforce strictness, you MUST remove the dictionary `.model_copy(update={"content_blocks": [], "penalties_applied": []})` from line 55-60, as those fields no longer exist on `ReportDataDTO` and will cause a `ValidationError: extra fields not permitted`.</action>
    <action>In `test_execution.py` (specifically `test_render_execution_json`), remove the explicit assignments `mock_dto.evaluative_matrices = []` and `mock_dto.informational_matrices = []` on the mocked dto around line 422.</action>
    <demolish>REMOVE: `factory_use_construct=True` and legacy field overrides.</demolish>
  </step>

  <step id="3" name="UPDATE GOLDEN JSON &amp; COMPILE">
    <action>In `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`, updating the mock structure will invalidate the Flutter Golden Snapshot. You MUST instruct the user to run `flutter test --update-goldens` inside `client_app_v2/` if the parity test fails due to visual changes in the JSON dump.</action>
  </step>

  <step id="4" name="TESTING STRATEGY &amp; QUALITY GATE PLAN">
    <action>Run the tests: `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py backend_v2/tests/unit/services/test_execution.py`</action>
    <action>If `test_sdui_semantic_parity.py` fails on the Flutter side (Step 3 inside the test), you MUST run `flutter test test/features/execution/sdui_semantic_parity_test.dart --update-goldens` inside `client_app_v2/` to resync the dynamic golden path.</action>
  </step>
</execution_protocol>
```
