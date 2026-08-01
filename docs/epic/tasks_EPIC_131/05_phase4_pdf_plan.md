<execution_protocol>
## Core Directives
1. **Zero Behavioral Change Mandate**: Enforce structural refactoring ONLY.
2. **Context Amnesia Prevention**: All targets are bounded using `@-references`.

## Implementation Plan

### Step 4.1: Modify Jinja Block Renderer Dispatch & Single Source of Truth
**Target**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- Move all visualization rendering into the `render_sdui_blocks(blocks, level=0, charts=none)` macro.
- Completely delete the secondary legacy layout loop (lines 273+) and the `Yhteenveto / Matrix Summary Table` block at the bottom of the template.
- Concrete rendering strategy per block type inside the macro:
  - `"3d_matrix"` (SduiRadarChartBlock) and `"2d_compare"` (SduiScatterPlotBlock) → If `level == 0` and `charts` is provided, inject the base64 image using `loop.index0` as the key.
  - `"matrix_summary"` (SduiMatrixTableBlock) → Render a full HTML `<table>` using `block.matrix_visible_columns` for headers and `block.axes` for rows. You MUST resolve column headers using specific locale resolution.
  - `"1d_metrics"` (SduiMetrics1DBlock) → Iterate `block.axes`. Render the score label and visual progress bar (`axis.ui_plot_ratio`) FIRST, and then natively call `render_sdui_blocks(axis.inner_sdui_blocks, level=level+1)`.

> [!IMPORTANT]
> **Chart Image Indexing Migration**: By routing all visualizations through `render_sdui_blocks`, `loop.index0` in the macro exactly matches the `idx` in `pdf_generator.py` when `level == 0`. Pass the `charts` dictionary from the global context into the macro.
>
> **1D Metrics Atomic Details**: Phase 2 flattened `evaluated_atoms` into standard SDUI blocks within `axis.inner_sdui_blocks`. Do NOT attempt to loop through `evaluated_atoms` manually. Simply call `render_sdui_blocks(axis.inner_sdui_blocks)` and rely on the UI components.

### Step 4.2: Eradicate Dead Jinja Code
**Target**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- The entire block of legacy layout code at the bottom of the template must be deleted as it relies on `report.layouts` and legacy `preset_view` strings.

### Step 4.3: Strict Exception Handling and Iteration in PDF Generator
**Target**: `@[c:\src\quorum\backend_v2\services\pdf_generator.py]`
- Replace `ReportDataDTO.layouts` iteration with a Python 3.10 `match block:` statement to iterate `report_dto.inner_sdui_blocks`.
- Remove the `except Exception as e:` catch-all block. Instead, explicitly catch `(ValueError, TypeError)` to wrap as `CompliantAppException(status_code=500)`. Do NOT swallow `ConfigurationError`; allow it to bubble up natively.

### Step 4.4: Update pdf_generator.py Rendering Context
**Target**: `@[c:\src\quorum\backend_v2\services\pdf_generator.py]`
- Update Jinja context to pass `report.inner_sdui_blocks` instead of `report.layouts`.

### Step 4.5: Update Phase 4 Tests
**Target**: `@[c:\src\quorum\backend_v2\tests\unit\test_pdf_generator.py]`
- **Negative Test Mandate**: `test_pdf_generator_empty_chart_crashes` - Verify empty bytes from `SduiRadarChartBlock` crashes natively with `ConfigurationError`.
- **Negative Test Mandate**: `test_pdf_generator_unknown_block_type_skipped` - Verify unknown `block_type` gracefully skips during chart generation.
</execution_protocol>
