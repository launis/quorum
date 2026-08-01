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
        <action>Modify @[c:\src\quorum\backend_v2\models\view\sdui.py]. Import `MatrixScorecardRowDTO, I18nText` from `backend_v2.models.v2_core` and `LaxXaiExtensionType` from `backend_v2.models.enums`. Create `SduiRadarChartBlock` inheriting from `SduiBlockBase`. Set `model_config = ConfigDict(title="3d_matrix")` and `block_type: Literal["3d_matrix"] = "3d_matrix"`. Specifically and exhaustively add fields: `title: I18nText | None = None`, `description: I18nText | None = None`, `axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)`, `text_delivery_mode: Literal["full", "titles_only", "none"] = "full"`, `synthesis_blocks: list['AnySduiBlock'] | None = None`.</action>
    </step>
    
    <step id="1.2" name="Create SduiScatterPlotBlock">
        <action>Create the `SduiScatterPlotBlock` inheriting from `SduiBlockBase` in @[c:\src\quorum\backend_v2\models\view\sdui.py]. Set `model_config = ConfigDict(title="2d_compare")` and `block_type: Literal["2d_compare"] = "2d_compare"`. Specifically and exhaustively add fields: `title: I18nText | None = None`, `description: I18nText | None = None`, `axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)`, `text_delivery_mode: Literal["full", "titles_only", "none"] = "full"`, `synthesis_blocks: list['AnySduiBlock'] | None = None`.</action>
    </step>
    
    <step id="1.3" name="Create SduiMatrixTableBlock">
        <action>Create the `SduiMatrixTableBlock` inheriting from `SduiBlockBase` in @[c:\src\quorum\backend_v2\models\view\sdui.py]. Set `model_config = ConfigDict(title="matrix_summary")` and `block_type: Literal["matrix_summary"] = "matrix_summary"`. Specifically and exhaustively add fields: `title: I18nText | None = None`, `description: I18nText | None = None`, `axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)`, `text_delivery_mode: Literal["full", "titles_only", "none"] = "full"`, `synthesis_blocks: list['AnySduiBlock'] | None = None`, `matrix_column_labels: dict[str, I18nText] = Field(default_factory=dict)`, `extension_labels: dict[LaxXaiExtensionType, I18nText] = Field(default_factory=dict)`, `matrix_visible_columns: list[str] = Field(default_factory=list)`.</action>
    </step>
    
    <step id="1.4" name="Create SduiMetrics1DBlock">
        <action>Create the `SduiMetrics1DBlock` inheriting from `SduiBlockBase` in @[c:\src\quorum\backend_v2\models\view\sdui.py]. Set `model_config = ConfigDict(title="1d_metrics")` and `block_type: Literal["1d_metrics"] = "1d_metrics"`. Specifically and exhaustively add fields: `title: I18nText | None = None`, `description: I18nText | None = None`, `axes: list[MatrixScorecardRowDTO] = Field(default_factory=list)`, `text_delivery_mode: Literal["full", "titles_only", "none"] = "full"`, `synthesis_blocks: list['AnySduiBlock'] | None = None`.</action>
    </step>
    
    <step id="1.5" name="Update AnySduiBlock Discriminated Union">
        <action>Update the `AnySduiBlock` definition in @[c:\src\quorum\backend_v2\models\view\sdui.py] to include the 4 new blocks.</action>
    </step>
    
    <step id="1.6" name="Satisfy Enum Parity Tests (Cross-Domain Atomicity)">
        <action>Update `SduiBlockType` enum in @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart] to include `matrix3d` (@JsonValue('3d_matrix')), `compare2d` (@JsonValue('2d_compare')), `matrixSummary` (@JsonValue('matrix_summary')), and `metrics1d` (@JsonValue('1d_metrics')).</action>
        <action>Update `render_sdui_blocks` macro in @[c:\src\quorum\backend_v2\templates\report_template.jinja2] with empty placeholder branches. Specifically: `{% elif block.block_type == '3d_matrix' %}`, `{% elif block.block_type == '2d_compare' %}`, `{% elif block.block_type == 'matrix_summary' %}`, and `{% elif block.block_type == '1d_metrics' %}` so the Regex parser detects them.</action>
    </step>
    
    <step id="1.7" name="Unit Tests for New Blocks">
        <action>Create or update @[c:\src\quorum\backend_v2\tests\unit\models\test_sdui_blocks.py] to include positive serialization roundtrip tests for each block.</action>
        <action>Add negative tests for all 4 new blocks. Specifically: `test_sdui_matrix_table_block_missing_axes` (validation error when `axes` are missing), `test_sdui_radar_chart_extra_keys` (validation error on unrecognized keys, enforcing `extra='forbid'`), `test_sdui_scatter_plot_invalid_text_mode` (validation error for invalid `text_delivery_mode`), and `test_sdui_metrics_1d_invalid_type` (validation error if `block_type` is wrong).</action>
    </step>
</execution_protocol>
```
