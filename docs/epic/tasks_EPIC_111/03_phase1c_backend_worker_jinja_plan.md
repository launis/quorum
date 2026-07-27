# Phase 1c: Backend Worker & Jinja Template Migration

## Overview
Refactor `worker.py` slop detection and `hasattr` checks. Migrate `report_template.jinja2` to extract data from `layouts` for PDF generation parity.

## Target Files
- `@[c:\src\quorum\backend_v2\worker.py]` (Modify)
- `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]` (Modify)

```xml
<execution_protocol level="2_execute">
  <constraint invariant="tripartite_rendering_boundary">The Backend passes structured data, Jinja generates static PDFs. UI responsibilities MUST NOT bleed into the backend.</constraint>
  
  <step id="1" name="REFACTOR WORKER.PY SLOP DETECTION">
    <action>Modify `@[c:\src\quorum\backend_v2\worker.py]`. Refactor slop penalty detection safely to read from internal domain/synthesis outputs instead of the deleted `dto.penalties_applied` field.</action>
    <demolish>REMOVE: `penalties_applied or []` coalescing fallback.</demolish>
    <action>Ensure zero usage of `.get()` or `or []` fallbacks.</action>
  </step>

  <step id="2" name="PURGE HASATTR FROM WORKER.PY">
    <action>Modify `@[c:\src\quorum\backend_v2\worker.py]`. Purge all `hasattr()` and naked dictionary checks (isinstance x, dict) to enforce pure Pydantic hydration using `.model_dump()` on `SynthesisOutputDTO`.</action>
    <demolish>REMOVE: `hasattr()` and `isinstance(x, dict)` checks inside `worker.py`.</demolish>
  </step>

  <step id="3" name="MIGRATE JINJA TEMPLATE">
    <action>Modify `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`. Refactor to read matrices from `layouts[*].axes` and penalties from penalty-type layouts.</action>
    <demolish>REMOVE: `evaluative_matrices`, `informational_matrices`, `all_matrices` from legacy fields, and `penalties_applied` loop.</demolish>
    <action>Blindly render `score_display_label` without evaluating `scale_max > scale_min` business logic in the Jinja template.</action>
  </step>

  <step id="4" name="TESTING STRATEGY & QUALITY GATE PLAN">
    <action>Run unit tests for `worker.py`.</action>
    <action>Ensure negative tests are added to `test_worker.py` verifying slop penalty detection safely ignores layouts where `metadata` is `None` or missing `"penalty_type"`.</action>
  </step>
</execution_protocol>
```
