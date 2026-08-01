# Phase 2: Blueprint Refactoring (Backend Orchestration)

**Source**: @[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md#L219-L339]

This plan refactors the blueprint generator to emit the new SDUI blocks inline, removes the old layout structures, and updates consumers.

## Target Files
- @[c:\src\quorum\backend_v2\services\blueprint.py]
- @[c:\src\quorum\backend_v2\models\v2_core.py]
- @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py]
- @[c:\src\quorum\backend_v2\services\pdf_generator.py]
- @[c:\src\quorum\backend_v2\services\flattener.py]
- @[c:\src\quorum\backend_v2\worker.py]
- @[c:\src\quorum\backend_v2\services\execution.py]
- Any backend unit test files affected (e.g. `test_blueprint.py`, `test_flattener.py`, etc.)

```xml
<execution_protocol>
    <constraint invariant="the_zero_compromise_pledge">No fallback chains or backwards compatibility.</constraint>
    <constraint invariant="anti_duplication">Explicitly DELETE or OVERWRITE the old version when modifying a file.</constraint>
    <constraint invariant="surgical_precision_edits">Provide the ENTIRE compilable structural block or use precise search-and-replace tools.</constraint>
    <constraint invariant="the_duct_tape_ban">Remove empty catch blocks or catch-alls.</constraint>

    <step id="2.1" name="Refactor _build_layouts() -> _build_visualization_blocks()">
        <action>Rename and refactor `_build_layouts()` in @[c:\src\quorum\backend_v2\services\blueprint.py] to `_build_visualization_blocks()`.</action>
        <action>Return `list[AnySduiBlock]`. Resolve `text_delivery_mode` at build time (emit axes with full detail, only titles, or no axes). Order logic: title -> description -> chart block -> synthesis blocks.</action>
        <action>Migrate standalone variance and authenticity report DTO creations to emit SDUI blocks inline. Replace `__import__()` lazy hack with top-of-file imports. Clean up `try/except Exception` catch-all blocks.</action>
        <demolish>REMOVE: `except Exception: pass` and lazy `__import__` hacks in `blueprint.py`.</demolish>
    </step>
    
    <step id="2.2" name="Update build_report_dto()">
        <action>In `build_report_dto()` within @[c:\src\quorum\backend_v2\services\blueprint.py], call `_build_visualization_blocks()` and `extend()` the results into `inner_sdui_blocks`. Remove `layouts` from the `ReportDataDTO()` instantiation.</action>
    </step>
    
    <step id="2.3" name="Update ReportDataDTO - Remove layouts Field">
        <action>Delete the `layouts` field entirely from `ReportDataDTO` in @[c:\src\quorum\backend_v2\models\v2_core.py].</action>
    </step>
    
    <step id="2.4" name="Delete ReportLayoutDTO Class">
        <action>Remove `ReportLayoutDTO` definition from @[c:\src\quorum\backend_v2\models\v2_core.py]. Remove any imports of it codebase-wide.</action>
    </step>
    
    <step id="2.6" name="Update Downstream Backend Consumers">
        <action>Update @[c:\src\quorum\backend_v2\services\sdui_mapper_service.py] to remove `preset_view` logic.</action>
        <action>Update @[c:\src\quorum\backend_v2\services\pdf_generator.py] to remove `layouts` iteration.</action>
        <action>Update @[c:\src\quorum\backend_v2\services\flattener.py] to extract matrices from `inner_sdui_blocks` using structural pattern matching (`match` case on `AnySduiBlock` chart variants).</action>
        <action>Remove `preset_view` routing logic from @[c:\src\quorum\backend_v2\worker.py] and @[c:\src\quorum\backend_v2\services\execution.py].</action>
    </step>
    
    <step id="2.7" name="Update Backend Tests &amp; Fixtures">
        <action>Update all corresponding test files consuming `ReportLayoutDTO`, `preset_view`, or `layouts`.</action>
        <action>Implement Negative Test Mandates: `test_blueprint.py` MUST verify `ConfigurationError` when custom scale lacks bounds, and unrecognized `text_delivery_mode` fails deterministically.</action>
        <action>CRITICAL: Migrate static JSON mock payloads in `backend_v2/tests/integration/test_data/` by removing `"layouts"` array and merging contents to `"inner_sdui_blocks"` to avoid Pydantic `extra='forbid'` crashes during integration tests.</action>
    </step>

    <step id="2.8" name="Cleanup Title Debt">
        <action>Remove hardcoded generation of `ParagraphBlock` for title/description in `_build_visualization_blocks`.</action>
        <action>Pass `title` and `description` to SduiRadarChartBlock, SduiScatterPlotBlock, SduiMatrixTableBlock, and SduiMetrics1DBlock instead.</action>
    </step>
</execution_protocol>
```
