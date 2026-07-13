# Epic 93: SDUI Output Rendering Unification Tracker

This tracker orchestrates the execution of Epic 93.

## Tasks
- [x] Phase 0: Coverage Bootstrap Plan (End-to-End Golden Master)
      *Plan: `docs/epic/tasks_EPIC_93_SDUI_Output_Rendering_Unification/phase_0_e2e_golden_master.md`*
- [x] Phase 1: SDUI Mapper Service & Context Injection
      *Plan: `docs/epic/tasks_EPIC_93_SDUI_Output_Rendering_Unification/phase_1_context_injection.md`*
- [x] Phase 2: Matrix Reducer & Pipeline A Integration
      **Goal**: Implement the deterministic `MatrixReducer` to sanitize boolean cards out of the payload, preventing token explosions during Final Synthesis.
      - [x] Implement `backend_v2/services/orchestrator/matrix_reducer.py` with 100% unit test coverage.
      - [x] Natively integrate `MatrixReducer` into `Pipeline A` (`dag_executor.py`).
      - [x] (Token-Compression Cascade) Verify `PASSED` atoms without `extracted_data` are structurally omitted from the `ReportDataDto` payload passed to the Synthesis node.
      - [x] (Knowledge Extraction) Write `ki_matrix_reducer.md` summarizing the payload compression thresholds. Parity & Zero-Loss Audit
- [x] `[NOK]` Invoke Tier 1 Planner for remaining phases (Phase 3 & 4)
- [ ] `[NOK]` Tier 2 Hardening (run `/tier2-hardening-backend` on new directories)
- [ ] `[NOK]` Proxy Sunset & Consumer Migration
- [ ] `[NOK]` Pre-Delete Audit
- [ ] `[NOK]` Baseline Parity & Zero-Loss Audit
- [ ] `[NOK]` Update architectural documentation and 04_directory_reference.md

## Instructions for the Execution Agent
- Execute the plans one by one using the `/tier2-execute` workflow.
- After completing Phase 2, you MUST stop and invoke `/tier1-planner` to flesh out the placeholders for Phase 3 and Phase 4 before continuing.
- After running the hardening loops, carefully update the session handover context block at the end of this tracker.

# Session Handover Context
- **Achieved**: Completed Phase 1 (SDUI Mapper Service) and Phase 2 (Matrix Reducer). DAG Pipeline A is now successfully projecting `ExecutionRecord` to `ReportDataDto` and compressing it via `MatrixReducer`.
- **Learned**: The system relies on strict Pydantic V2 modeling (`ConfigDict(strict=True)`); required `default=[]` explicit overrides in `QuoteEvidenceDTO` to satisfy MyPy and backend audit loops. The git working tree has been cleanly committed.
- **Remaining**: Execute Phase 3 (Synthesis Generation) and Phase 4 (Legacy Proxy Sunset). Currently initiating Tier 1 Planner to generate implementation plans for Phase 3 and 4.

## Resume Command
To execute this Epic iteratively, start a NEW chat session and run the following command:

`/tier5-resume --workflow=/tier1-planner --target="docs\epic\EPIC_93_SDUI_Output_Rendering_Unification_tracker.md, c:\src\quorum\docs\epic\EPIC_93_SDUI_Output_Rendering_Unification 2.md" --rules="00-antigravity-core.md, 01-python-backend.md"`
