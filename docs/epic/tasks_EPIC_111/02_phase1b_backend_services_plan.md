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
  
  <step id="1" name="REFACTOR EXECUTION.PY EXCEL EXPORT">
    <action>Modify `@[c:\src\quorum\backend_v2\services\execution.py]`. Refactor Excel export summary rows which consume `evaluative_matrices`/`informational_matrices`. They must now extract matrices from `layouts`.</action>
    <action>Purge `.get()` coalescing patterns for `content_blocks`. Rewrite to use explicit `is not None` and dictionary `in` operator checks.</action>
    <demolish>REMOVE: `content_blocks` `.get()` coalescing patterns.</demolish>
  </step>

  <step id="2" name="REFACTOR FLATTENER.PY">
    <action>Modify `@[c:\src\quorum\backend_v2\services\flattener.py]`. Refactor matrix flattening to extract matrices from `layouts` instead of legacy `evaluative_matrices`.</action>
    <demolish>REMOVE: `evaluative_matrices or []` coalescing fallback.</demolish>
  </step>

  <step id="3" name="REFACTOR LINGUISTICS.PY">
    <action>Modify `@[c:\src\quorum\backend_v2\hooks\linguistics.py]`. Refactor linguistic matrix analysis (slop detection) to extract texts from `report_dto.layouts` (`synthesis_blocks` and `axes`).</action>
    <demolish>REMOVE: `evaluative_matrices or []` coalescing fallback.</demolish>
  </step>

  <step id="4" name="REFACTOR SDUI MAPPER SERVICE">
    <action>Modify `@[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]`. Remove direct `content_blocks` mapping, as content is now inherently covered by `layouts` mapping.</action>
  </step>

  <step id="5" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run localized Pytest unit tests for the modified files.</action>
    <action>Ensure negative tests are added to `test_linguistics.py` to handle missing/empty `layouts`.</action>
  </step>
</execution_protocol>
```
