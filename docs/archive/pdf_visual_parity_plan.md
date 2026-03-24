# PDF Visual Parity Update (RFC 7807 UI Alignment)

## Goal Description
The user reported that the PDF export of the generated reports does not look identical to the Flutter UI view. According to the "Zero-Math Frontend" parity rule (Section 7.2 of V2 Architecture), the backend's `report_template.jinja2` must render exactly the same logic and components as the `ReportRendererWidget`. The current Python PDF template is missing several UI features introduced recently:
1. It does not format the score utilizing `axis.scale_max` (rendering "Score: 3.0" instead of "3.0 / 5.0").
2. It completely omits the XAI (Explainable AI) citations (Quotes, Framework Source IDs, and Google Web Citations).
3. It lacks the logic to deduplicate identical citations (to prevent flooding the report with the same quote if multiple sub-axes reference the same original text segment).

## User Review Required

> [!IMPORTANT]
> This plan modifies the core HTML-to-PDF `jinja2` template engine to inject the missing citations and deduplicate them logically. Review the planned changes below and respond with **"PROCEED"**.

## Proposed Changes

### Backend PDF Engine

#### [NEW] `backend_v2/utils/static_charts.py`
- Create a new utility utilizing the already installed `matplotlib` library for rendering zero-math Server-Driven charts.
- **`generate_radar_chart(axes: list[ReportAxisDTO]) -> str`**: Renders a Matplotlib polar plot taking 3 to N axes. Normalizes scales and plots a closed polygon. Returns a Base64 encoded PNG string.
- **`generate_scatter_chart(axes: list[ReportAxisDTO]) -> str`**: Renders a Cartesian 2D scatter plot where Data X and Y are plotted. Evaluates `axis.score` logically. Returns a Base64 encoded PNG string.

#### [MODIFY] `backend_v2/services/pdf_generator.py`
- Before templating `report_template.jinja2`, iterate `report_dto.layouts`.
- If a layout's `preset_view` is `radar_3d`, `3d_complex`, `matrix_2d` or `2d_compare`, call `static_charts.py` to generate the Base64 image payload.
- Pass a new `charts` dictionary into the `template.render(...)` context mapping `loop.index0` or stringified layout hashes to the generated PNG string.

#### [MODIFY] `backend_v2/templates/report_template.jinja2`
- **Chart Injection:** Inside `{% for layout in report_data.layouts %}`, verify if `loop.index0` exists in the `charts` dict. If so, render an `<img src="data:image/png;base64,{{ charts[loop.index0] }}" style="max-width: 100%; height: auto;" />` block below the layout title.
- **Scale Maximum Expansion:**
  - Locate the `<div class="value-box">Score: {{ "%.1f"|format(axis.score) }}</div>` block.
  - Upgrade it to use the `scale_max` evaluation securely: `{% if axis.scale_max > axis.scale_min %}{{ "%.1f"|format(axis.score) }} / {{ "%.1f"|format(axis.scale_max) }}{% else %}{{ "%.1f"|format(axis.score) }}{% endif %}`.
- **XAI Citation Parity:**
  - Initialize a `namespace` before the layout loop to track deduplicated quotes: `{% set ns = namespace(seen_quotes=[]) %}`.
  - Inside the `{% if axis.justification and layout.show_text %}` block, inject three new UI boxes explicitly matched to the Finnish translations of `app_fi.arb`:
    1. **Quote Block:** If `axis.cited_text_quote` exists and is not duplicated in `ns.seen_quotes`, render a grey border-left box containing `💬 Ote alkuperäisestä tekstistä:`.
    2. **Framework Reference:** If `axis.cited_source_id` exists, render a blue-grey text line containing `⚖️ Viitekehys: {{ axis.cited_source_id }}`.
    3. **Google Verification:** If `axis.cited_web_citation` exists, render a green rounded box containing `✅ Tarkistettu Googlen lähteistä:`.

## Verification Plan

### Manual Verification
- Generate a PDF from a workflow that inherently contains source text constraints and google citations.
- Compare side-by-side with the Flutter web view to ensure the Quote, Framework, and Google badges appear conditionally correct and identically formatted.
