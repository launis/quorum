# Phase 3: Full-Stack Integration Checkpoint

## Overview
Source: @[c:\src\quorum\docs\epic\EPIC_111_sdui_legacy_eradication_and_ui_refactor.md#L95-L101] Phase 3: Full-Stack Integration Checkpoint
This phase verifies the complete architectural migration by running the `test_sdui_semantic_parity.py` regression suite. All functional code modifications were executed in earlier phases.

## Target
Execute global regression audits for both backend and frontend, particularly focusing on SDUI semantic parity after legacy purges are complete. 

## Expected Target Files
- CONTEXT: `@[c:\src\quorum\backend_v2\tests\integration\test_sdui_semantic_parity.py]`

```xml
<execution_protocol level="2_execute">
  <step id="1" name="RUN SDUI SEMANTIC PARITY TEST">
    <action>Execute `test_sdui_semantic_parity.py` using `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` to ensure 100% semantic parity between Jinja PDFs and Flutter UI.</action>
    <constraint>The test was already updated in Phase 2A to remove `factory_use_construct=True`. If the test fails, debug the failures ensuring strict adherence to the Dumb Painter pattern. The test must pass without any validation bypasses.</constraint>
    <constraint invariant="anti_tdd_trap">If the test fails, fix the underlying logic, but DO NOT revert to legacy hacks.</constraint>
  </step>

  <step id="2" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run the global backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
    <action>Run the cross-domain DTO parity build: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/ --build`</action>
    <constraint>You MUST enforce ALL rule blocks in the `<universal_quality_gate>` section of `00-antigravity-core.md`.</constraint>
  </step>
</execution_protocol>
```
