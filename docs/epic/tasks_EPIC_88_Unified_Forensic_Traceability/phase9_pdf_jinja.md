# Phase 9: PDF Rendering & Jinja2 Template Parity

Source: Epic Phase 7.1, 7.2.3, and Appendix F

## Target Files (Modify)
- `backend_v2/templates/report_template.jinja2`

## Requirements
1. **Remove Old Deduplication**:
   - Locate the `ns.seen_quotes` dictionary logic (around line 261).
   - COMPLETELY REMOVE this deduplication logic, as the Python `BlueprintTransformer` now handles deduplication upstream.
2. **Flat UI Evidence Rendering**:
   - Replace the single `cited_text_quote` rendering with nested iteration.
   - `{% for lq in axis.forensics.level_quotes %}`
   - Print `lq.level_name` as a header.
   - `{% for quote in lq.quotes %}`
3. **Icons & Styling**:
   - `{% if quote.user_rejected %}`: Render `<del style="color: #999">{{ quote.text }}</del>`.
   - Else: Render `{{ quote.text }}`.
   - `{% if quote.is_mcp_verified %}`: Render `<span style="color:green">✅ MCP-Varmennettu</span>`. (Remove the old hardcoded `✅ Tarkistettu Googlen lähteistä:`).
4. **Cascading Warning**:
   - `{% if axis.forensics and axis.forensics.all_evidence_rejected %}`: Render `<span style="color: #f57c00">⚠️ Arvosanan perusteet kumottu asiantuntijan toimesta</span>` next to the main grade.
5. **i18n Parity**:
   - Wrap strings like "MCP-Varmennettu" and "Arvosanan perusteet kumottu..." inside Jinja translation tags (e.g. `{{ _("mcp_verified") }}`) to ensure the PDF engine can render them in multiple languages.

## Architectural Invariants & Hardening Mandate
- **Rule 30 (tripartite_rendering_boundary)**: The PDF Jinja2 template is a "dumb" renderer. All complex deduplication and intelligence happens in the Python DTO layer before this point.
- **Rule 40 (no_string_l10n)**: Ensure new display strings are passed through the translation filter.

## Documentation Update
Update `docs/architecture/08_dynamic_rendering_sdui.md` (or `11_empirical_scoring_report.md` if relevant to PDFs) regarding the 100% visual parity between Flutter and the generated PDF report.

## Testing & Quality Gate Plan
- **Verification**: Run `uv run python scripts/backend_audit_loop.py backend_v2/templates/report_template.jinja2 --test`
- **Manual Verification**: Generate a test PDF report using the Python REPL (e.g., via `export_to_pdf.py` or `ReportService`) and verify the tags render correctly.

---
### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md`
