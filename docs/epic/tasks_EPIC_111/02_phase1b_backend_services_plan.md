# Phase 1b: Backend Services Consumers Refactoring

## Overview
Refactor consumers of the legacy fields (`execution.py`, `flattener.py`, `linguistics.py`, `sdui_mapper_service.py`) to read exclusively from the new `layouts` structure.

## Target Files
- `@[c:\src\quorum\backend_v2\services\execution.py]` (Modify)
- `@[c:\src\quorum\backend_v2\services\flattener.py]` (Modify)
- `@[c:\src\quorum\backend_v2\hooks\linguistics.py]` (Modify)
- `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="the_duct_tape_ban">No empty dicts `{}` on failure, or using `.get("key", default)` to suppress missing data.</constraint>
  
  <step id="1" name="VERIFY REFACTORINGS (ALREADY COMPLETED)">
    <action>Verify that `execution.py`, `flattener.py`, `linguistics.py`, and `sdui_mapper_service.py` no longer use `content_blocks` or `evaluative_matrices` and correctly use `layouts`. (Note: This was completed in a previous phase, so no code changes should be needed here).</action>
  </step>

  <step id="2" name="NEGATIVE TESTING: LINGUISTICS HOOK">
    <action>Modify `@[c:\src\quorum\backend_v2\tests\unit\hooks\test_linguistics.py]`. Add tests for `scan_report_for_slop`.</action>
    <action>Add Negative Test 1: Handle `layouts` being completely empty or missing.</action>
    <action>Add Negative Test 2: Handle `layouts` where `synthesis_blocks` exist but have no `text` fields or are malformed.</action>
    <action>Add Positive Test: Verify it correctly detects performative patterns in `synthesis_blocks` and `axes.row_explanation`.</action>
  </step>

  <step id="3" name="QUALITY GATE PLAN">
    <action>Run localized Pytest for `test_linguistics.py`.</action>
    <action>Run global backend audit: `uv run python scripts/backend_audit_loop.py backend_v2/ --test`</action>
  </step>
</execution_protocol>
```
