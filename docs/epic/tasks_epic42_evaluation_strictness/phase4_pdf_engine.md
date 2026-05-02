# Epic 42: Phase 4 - PDF Engine & Backend DTO Parity

## Goal
Achieve full feature parity between the Flutter UI (Phase 3) and the Backend PDF Engine for the Evaluation Strictness features. This requires exposing `evidence_type` in `MatrixScorecardRowDTO`, mapping it during Blueprint Transformation, and dynamically rendering both the `strictness_level` badge and `EvidenceType` visual indicators in the Jinja2 PDF templates.

## Architectural Laws (Must Follow)
- **Rule 1: No Naked Dicts:** Ensure `evidence_type` is correctly typed as an Optional string or Enum in `MatrixScorecardRowDTO`. Do not pass it loosely.
- **Rule 2: Fallback Prevention:** If the evidence type is missing (legacy execution), gracefully handle it in Jinja2 without throwing a rendering error.
- **Rule 3: PDF / UI Parity:** The PDF must look identical to the UI Execution Report (Epic 42 Phase 3) structurally, avoiding deviations in logic.

## Proposed Changes

### 1. `backend_v2/models/v2_core.py`
**TARGET (Modify)**
- Update `MatrixScorecardRowDTO` to include an optional field `evidence_type: str | None = Field(default=None, description="The EvidenceType extracted from AtomResponse")`.

### 2. `backend_v2/services/blueprint.py`
**TARGET (Modify)**
- In `_build_matrices`, when iterating over atoms and extracting `justification`, `cited_text_quote`, etc., extract the `step_1_evidence_type` from the parsed `TaskResult` (or `AtomResponse` dict depending on how it's stored in `results`) and assign it to `evidence_type` when creating `MatrixScorecardRowDTO`.

### 3. `backend_v2/templates/report_template.jinja2`
**TARGET (Modify)**
- **Header Section:** Where `workflow_name` and `printed_at` are displayed, add a badge/indicator for the Strictness Level (e.g., `<div style="background-color: #eee; border-radius: 4px; padding: 4px 8px; font-size: 10px; display: inline-block;">Strictness Level: {{ report_data.strictness_level }}</div>`).
- **Matrix / Atom Iteration Section:** Inside the loop where `axis.justification` and `axis.cited_text_quote` are rendered, add visual badges based on `axis.evidence_type`. For example:
  - If `EXPLICIT_QUOTE`, show a green checkmark badge "✅ Explicit Quote".
  - If `IMPLIED_INTENT`, show a warning badge "⚠️ Implied Intent".

### 4. Verification & Quality Gate Plan
- Run `uv run python scripts/backend_audit_loop.py backend_v2/models backend_v2/services/blueprint.py --test` to ensure no schema violations occur.
- Generate a PDF locally using `generate_execution_pdf` for a known Epic 42 execution and visually verify that the strictness badge and evidence types render without Jinja2 template errors.
