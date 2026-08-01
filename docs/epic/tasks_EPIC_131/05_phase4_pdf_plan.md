<execution_protocol>
## Core Directives
1. **Zero Behavioral Change Mandate**: Enforce structural refactoring ONLY.
2. **Context Amnesia Prevention**: All targets are bounded using `@-references`.

## Implementation Plan

### Step 4.1: Modify Jinja Block Renderer Dispatch
**Target**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- Migrate layout loop to iterate `report.inner_sdui_blocks` and dispatch on `block.block_type`.
- For `3d_matrix`, render an HTML table fallback.
- For `2d_compare`, render a 2-column HTML comparison table.
- For `matrix_summary`, render a full HTML `<table>` using `block.visible_columns`.
- For `1d_metrics`, loop through `block.axes`. For each axis, render the score label (`axis.score_display_label`) and the visual progress bar (`axis.ui_plot_ratio`), then render the text via `render_sdui_blocks(axis.inner_sdui_blocks)`.

### Step 4.2: Eradicate Dead Jinja Code
**Target**: `@[c:\src\quorum\backend_v2\templates\report_template.jinja2]`
- Remove dead `'3d_complex'` and `'complex3d'` strings from the `has_graph` set.

### Step 4.3: Remove Legacy layouts Iteration from PDF Generator
**Target**: `@[c:\src\quorum\backend_v2\services\pdf_generator.py]`
- Replace `ReportDataDTO.layouts` iteration with a Python 3.10 `match block:` statement to iterate `report_dto.inner_sdui_blocks`.
- Remove the `except Exception as e:` catch-all block. Catch specifically `(ValueError, TypeError, ConfigurationError)` and re-raise as `CompliantAppException`.

### Step 4.4: Update pdf_generator.py Rendering Context
**Target**: `@[c:\src\quorum\backend_v2\services\pdf_generator.py]`
- Update Jinja context to pass `report.inner_sdui_blocks` instead of `report.layouts`.

### Step 4.5: Update Phase 4 Tests
**Target**: `@[c:\src\quorum\backend_v2\tests\unit\test_pdf_generator.py]`
- **Negative Test Mandate**: `test_pdf_generator_empty_chart_crashes` - Verify empty bytes from `SduiRadarChartBlock` crashes natively with `ConfigurationError`.
- **Negative Test Mandate**: `test_pdf_generator_unknown_block_type_skipped` - Verify unknown `block_type` gracefully skips during chart generation.
</execution_protocol>
