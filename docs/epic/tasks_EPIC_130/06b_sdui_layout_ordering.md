# Phase 7B: SDUI Layout Flattening — Block Ordering & PDF/Jinja Parity

**Overview:** Configure the block ordering to match `raportti 2.pdf` exactly. Modify `pdf_generator.py` and Jinja macros to iterate over the flat block array. Verify Flutter rendering parity.

**Source:** @[c:\src\quorum\docs\epic\EPIC_130_blueprint_decomposition.md#L176-L205] Phase 7 (second sub-phase)

**Expected Target Files:**
- @[c:\src\quorum\backend_v2\services\blueprint.py] [MODIFY — block ordering configuration]
- @[c:\src\quorum\backend_v2\services\sdui\adapters\matrix_graphs_adapter.py] [MODIFY — implement Title -> Text -> Graph flattened sequence]
- @[c:\src\quorum\backend_v2\services\pdf_generator.py] [MODIFY — flat layout iteration]
- @[c:\src\quorum\backend_v2\templates\report_template.jinja2] [MODIFY — flat block rendering]

## Execution Steps

1. **Refactor MatrixGraphsAdapter for Flattened Sequence**: Update `MatrixGraphsAdapter.build()` to emit elements in a strict 1-2-3 Dumb Painter sequence using ONLY these exact blocks:
   - Prepend exactly `MarkdownBlock(text=f"### {layout_def.title}")`.
   - Append the LLM Explanation as exactly `ParagraphBlock`.
   - Append the graph as exactly `SduiRadarChartBlock`, `SduiScatterPlotBlock`, or `SduiMetrics1DBlock` with their internal `title` explicitly set to `None`.
   - If `preset_view == "text_only"`, omit the third step entirely.
2. **Flatten PDF Generator**: Modify `pdf_generator.py` and `report_template.jinja2` to sequentially iterate over the flattened `inner_sdui_blocks`, eliminating all legacy matrix nesting logic.
3. **Verify UI/PDF Parity**: Ensure Flutter and PDF rendering match `raportti 2.pdf`.

> [!IMPORTANT]
> The final implementation steps can be fleshed out via `/tier1-planner` if necessary, but the core objective is to execute the above sequence.
