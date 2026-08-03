# Phase 6B: Matrix Adapters Extraction (SDUI Graphs and Tables)

**Overview:** Extract the legacy matrix visualization logic from `blueprint.py` into dedicated `MatrixGraphsAdapter` and `MatrixSummaryTableAdapter`. These adapters must strictly read `context.profile.layouts` to determine the discriminator (`preset_view`) and map matrix rows directly to `SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiMetrics1DBlock`, and `SduiMatrixTableBlock` in a flat list.

**Key Epic References:**
- `output_profile_layout_v2.md`: SDUI Flat Polymorphic Pipeline
- `ki_sdui_adapter_pattern.md`: Strict two-section adapter pattern

**Target Files:**
- `c:\src\quorum\backend_v2\services\sdui\adapters\matrix_graphs_adapter.py` [NEW]
- `c:\src\quorum\backend_v2\services\sdui\adapters\matrix_summary_table_adapter.py` [NEW]
- `c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_matrix_graphs_adapter.py` [NEW]
- `c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_matrix_summary_table_adapter.py` [NEW]

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by Phase 6A (specifically `blueprint.py` and `xai_highlights_adapter.py`). Verify it serves the Epic's goal.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
  </step>

  <dod_checklist>
    - [ ] `MatrixGraphsAdapter` implemented and strictly outputs `SduiRadarChartBlock`, `SduiScatterPlotBlock`, or `SduiMetrics1DBlock` based on `profile.layouts`.
    - [ ] `MatrixSummaryTableAdapter` implemented and strictly outputs `SduiMatrixTableBlock`.
    - [ ] Both adapters adhere exactly to the two-section canonical structure (`AESTHETICS_RULES` and `@staticmethod build`).
    - [ ] Negative and boundary tests (ISTQB) implemented for both adapters.
  </dod_checklist>

  <step id="1" name="CREATE MatrixGraphsAdapter">
    <constraint invariant="knowledge_item_preflight">Read KI `sdui_adapter_decomposition` (`ki_sdui_adapter_pattern.md`) before creating adapters.</constraint>
    <action>Create `c:\src\quorum\backend_v2\services\sdui\adapters\matrix_graphs_adapter.py`.</action>
    <action>The `build(context: AdapterContext)` method must iterate over `context.profile.layouts`. For layouts matching `"3d_matrix"`, `"2d_compare"`, or `"1d_metrics"`, it must map the corresponding matrices from `context.execution.results` into the appropriate SDUI blocks.</action>
    <action>Ensure extrema (min/max) are dynamically resolved from the model scales.</action>
    <action>Yield the graph block followed by any AI justification texts (`ParagraphBlock`s) generated for that matrix.</action>
  </step>

  <step id="2" name="CREATE MatrixSummaryTableAdapter">
    <action>Create `c:\src\quorum\backend_v2\services\sdui\adapters\matrix_summary_table_adapter.py`.</action>
    <action>The `build(context: AdapterContext)` method must check `context.profile.layouts` for `"matrix_summary"`. If present, map all evaluator matrices into a single `SduiMatrixTableBlock`.</action>
  </step>

  <step id="3" name="TEST CONTRACT FULFILLMENT">
    <action>Create `c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_matrix_graphs_adapter.py` and `c:\src\quorum\backend_v2\tests\unit\services\sdui\adapters\test_matrix_summary_table_adapter.py`.</action>
    <action>Implement at least two negative test scenarios per adapter (e.g. empty matrices, missing layouts, malformed bounds).</action>
    <action>Use Pytest fixtures and `polyfactory` for deterministic mock data.</action>
  </step>

  <validation_gate>
    <action>Run backend audit loop: `uv run python scripts/backend_audit_loop.py backend_v2 --test`</action>
  </validation_gate>
</execution_protocol>
```
