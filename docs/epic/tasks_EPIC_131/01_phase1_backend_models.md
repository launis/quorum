# Phase 1: New Pydantic SDUI Block Models (Backend Only)

**Source**: @[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md#L111-L217]

This plan implements the Phase 1 goal of creating 4 new polymorphic SDUI block models and registering them in the `AnySduiBlock` union, along with passing cross-domain enum parity tests.

## Target Files
- @[c:\src\quorum\backend_v2\models\view\sdui.py]
- @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart]
- @[c:\src\quorum\backend_v2\templates\report_template.jinja2]
- @[c:\src\quorum\backend_v2\tests\unit\models\test_sdui_blocks.py]

```xml
<execution_protocol>
    <constraint invariant="pydantic_annotated_fields_mandate">Use PEP 593 Annotated syntax</constraint>
    <constraint invariant="universal_fail_fast">Do not swallow exceptions or allow invalid data</constraint>
    <constraint invariant="strict_pydantic_v2_rust">Ensure strict model validation</constraint>
    
    <step id="1.1" name="Create SduiRadarChartBlock">
        <action>Modify @[c:\src\quorum\backend_v2\models\view\sdui.py]. Import `MatrixScorecardRowDTO, I18nText` from `backend_v2.models.v2_core` and `LaxXaiExtensionType` from `backend_v2.models.enums`. Create `SduiRadarChartBlock` inheriting from `V2CoreBase` with `block_type: Literal["3d_matrix"]`.</action>
    </step>
    
    <step id="1.2" name="Create SduiScatterPlotBlock">
        <action>Create the `SduiScatterPlotBlock` inheriting from `V2CoreBase` with `block_type: Literal["2d_compare"]` in @[c:\src\quorum\backend_v2\models\view\sdui.py].</action>
    </step>
    
    <step id="1.3" name="Create SduiMatrixTableBlock">
        <action>Create the `SduiMatrixTableBlock` inheriting from `V2CoreBase` with `block_type: Literal["matrix_summary"]` in @[c:\src\quorum\backend_v2\models\view\sdui.py]. Ensure `extension_labels` uses `LaxXaiExtensionType`.</action>
    </step>
    
    <step id="1.4" name="Create SduiMetrics1DBlock">
        <action>Create the `SduiMetrics1DBlock` inheriting from `V2CoreBase` with `block_type: Literal["1d_metrics"]` in @[c:\src\quorum\backend_v2\models\view\sdui.py].</action>
    </step>
    
    <step id="1.5" name="Update AnySduiBlock Discriminated Union">
        <action>Update the `AnySduiBlock` definition in @[c:\src\quorum\backend_v2\models\view\sdui.py] to include the 4 new blocks.</action>
    </step>
    
    <step id="1.6" name="Satisfy Enum Parity Tests (Cross-Domain Atomicity)">
        <action>Update `SduiBlockType` enum in @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart] to include `matrix3d` (@JsonValue('3d_matrix')), `compare2d`, `matrixSummary`, and `metrics1d`.</action>
        <action>Update `render_sdui_blocks` macro in @[c:\src\quorum\backend_v2\templates\report_template.jinja2] with empty placeholder branches (e.g. `{% elif block.block_type == '3d_matrix' %}`) for the 4 new block types so the Regex parser detects them.</action>
    </step>
    
    <step id="1.7" name="Unit Tests for New Blocks">
        <action>Create or update @[c:\src\quorum\backend_v2\tests\unit\models\test_sdui_blocks.py] to include positive serialization roundtrip tests for each block.</action>
        <action>Add negative tests: `test_sdui_matrix_table_block_missing_axes` (validation error when `axes` are missing) and `test_sdui_radar_chart_extra_keys` (validation error on unrecognized keys, enforcing `extra='forbid'`).</action>
    </step>
</execution_protocol>
```
