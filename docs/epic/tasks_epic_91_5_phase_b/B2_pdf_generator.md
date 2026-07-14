# Epic 91.5 Phase B2: PDF Generator StrictUndefined Enforcement

## Objective
Enforce `StrictUndefined` compatibility in the PDF Generation pipeline. Ensure the PDF Jinja template correctly consumes the new `v2_core.ReportDataDTO` structure and that no legacy undefined variables crash the PDF generator.

## Context & Architectural Mandates
- **Tripartite Rendering Boundary:** The PDF generation uses Jinja2 with `StrictUndefined`. It must render using strictly available data in `ReportDataDTO`. If data is missing or structurally incompatible, it will intentionally fail (Fail-Fast).
- **Strict Configuration Segregation:** Do not hardcode magic strings inside templates or generator. Use `.arb` L10n keys correctly.

## Target Files (Modify)
- `backend_v2/services/pdf_generator.py`
- `backend_v2/templates/report_template.jinja2`

## Context Files (Read-Only)
- `backend_v2/models/v2_core.py` (Source DTO: `ReportDataDTO`)

## Proposed Changes

### 1. Update `backend_v2/templates/report_template.jinja2`
- Audit `report_template.jinja2` and fix the critical `StrictUndefined` crash vectors caused by the new `MatrixScorecardRowDTO` and `QuoteEvidenceDTO` strict schema definitions.
- **Specific Field Replacements Required:**
  - Replace `axis.justification` with `axis.row_explanation`.
  - Remove or rewrite `axis.forensics.all_evidence_rejected` logic (e.g., check `axis.risk_flag` or `axis.contextual_override` instead, as `forensics` no longer exists).
  - Replace `quote_dto.source_alias` with `quote_dto.verified_source_ids`.
- Verify root-level properties like `scoring_strategy`, `strictness_level`, and `visible_metadata` align with `ReportDataDTO`.

### 2. Audit `backend_v2/services/pdf_generator.py`
- *Note: `generate_execution_html` already loops over `report_dto.layouts` and safely maps `preset_view` to static charts.*
- Perform a read-only verification to ensure `report_dto` passes validation and no exceptions are thrown when `layouts` are empty. Do NOT rewrite the chart generation logic unless a direct bug is found.

## Testing & Quality Gate Plan
- Write or update `backend_v2/tests/unit/services/test_pdf_generator.py` to assert that PDF generation works flawlessly with a mocked `ReportDataDTO`.
- Execute the Universal Quality Gate (`scripts/backend_audit_loop.py backend_v2/services/pdf_generator.py --test`).

---
# Session Handover
To execute this Epic iteratively, start a NEW chat session and run the `/tier5-resume` command found at the bottom of your tracker.
