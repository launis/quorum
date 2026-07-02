# EPIC 93 Phase 4: PDF Parity, Forensics, and Architecture Update

## Source: Epic 93, Sections 3.4 (C & D) and 3.3 (Validation)

### Objective
Wire the final ports to the new `ReportDataDto`: The Jinja2 PDF Generator and the Forensics Flattener. Perform the final 100% parity verification against the existing reference PDF to guarantee compliance with the Phase 0 Prerequisite.

### Target Files (Modify)
- `backend_v2/services/pdf_generator.py`
- `backend_v2/templates/report_template.jinja2`
- `backend_v2/services/flattener.py`
- `docs/architecture/08_dynamic_rendering_sdui.md`

### Context Files (Read-Only)
- `c:\src\quorum\data\files\executions\exe_8a5b9f774b9743a3a6a0a595912e1b94\report.pdf`
- `c:\src\quorum\.agents\rules\01-python-backend.md`

### Architectural Mandates
- **tripartite_rendering_boundary**: Jinja generates static PDFs. UI responsibilities MUST NOT bleed into the backend hooks.
- **Epic Phase 0 Prerequisite**: Visual and semantic output must remain completely unchanged. Parity must be 100%.

### Implementation Details
1.  **PDF Parity & Generation:**
    *   Refactor `pdf_generator.py` to ingest the clean `ReportDataDto` instead of raw markdown states.
    *   Update `report_template.jinja2` to map `QuoteEvidenceDTO` fields accurately to the existing PDF visual layout.
2.  **Forensics & Raakadata:**
    *   Update `flattener.py` to recursively extract raw atoms and validated semantic assertions from the new headless state, enabling CSV/JSON analytical exports.
3.  **Validation Check:**
    *   Run the pipeline against execution `exe_8a5b9f774b9743a3a6a0a595912e1b94`.
    *   Compare the output PDF natively to `report.pdf`. Ensure pixel and semantic parity.
4.  **Architecture Documentation:**
    *   Update `docs/architecture/08_dynamic_rendering_sdui.md` to reflect the new DTO-driven Tripartite boundary, the death of `synthesis.py`, and the SDUI Warning Card mapping logic.

### Destructive Operation Inventory
- None in this phase.

### Bidirectional Integration Check
- **Producer:** `ReportDataDto`.
- **Consumer:** PDF Generator and Flattener parsing the identical object safely.

### Testing & Quality Gate Plan
1.  **Unit Tests:** Test the flattener logic recursively unpacking the new nested structures.
2.  **Integration Tests:** End-to-end template generation tests using mock DTO data to ensure Jinja evaluates safely.
3.  **Verification:** Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/ --test`. Check the PDF.

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run: `/tier5-resume --target docs/epic/epic_93_tracker.md`
