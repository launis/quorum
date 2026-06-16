# Epic SDUI Synthesis - Phase 3: PDF Engine Update
Source: Epic Phase 3

PDF-generaattori ei enää saa luottaa Markdown-filtteriin, vaan sen tulee iteroida uudet `content_blocks`-objektit ja renderöidä natiivia HTML:ää SDUI-sääntöjen mukaisesti.

## Proposed Changes
### PDF Engine Templates
#### [MODIFY] [report_template.jinja2](file:///c:/src/quorum/backend_v2/templates/report_template.jinja2)
- Remove `| md | safe` filter from where synthesis output was previously rendered.
- Write Jinja macros to iterate over `content_blocks` and render native HTML:
  - `paragraph` -> `<p>` with superscript citations `<sup>1</sup>`.
  - `bullet_list` -> `<ul>` and `<li>`.
  - `alert_box` -> `<div class="alert alert-info">`.

#### [MODIFY] [pdf_generator.py](file:///c:/src/quorum/backend_v2/services/pdf_generator.py) (If python data prep is needed)
- Ensure the data structure passed to Jinja maps the new list structure natively without errors.

## Architectural Rules Implemented
- **Hardening Rule 30 (Tripartite Rendering Boundary)**: No markdown parsing in the backend logic, strictly use Jinja for presentation logic.

## Testing & Quality Gate Plan
### Unit/Integration Tests
- Run `uv run python scripts/backend_audit_loop.py backend_v2/templates --test` or specifically generate a test PDF to verify formatting.

## Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_sdui_synthesis_tracker.md`
