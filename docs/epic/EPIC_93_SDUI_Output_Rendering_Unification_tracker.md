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
- [ ] `[NOK]` Invoke Tier 1 Planner for remaining phases (Phase 3 & 4)
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
- **Achieved**: Initiated Epic 93 tracking and detailed the first two phases based on the provided epic specifications.
- **Learned**: Workspace has been committed to form a clean baseline. The epic breaks the architecture into a clean BFF mapped SDUI approach via strict DTO projections, dropping legacy HTML/Markdown mixing.
- **Remaining**: Execute Phase 0 (Golden Master Test), Phase 1, and Phase 2.

## Resume Command
To execute this Epic iteratively, start a NEW chat session and run the following command:

`/tier5-resume --workflow=/tier2-execute --target="docs\epic\EPIC_93_SDUI_Output_Rendering_Unification_tracker.md, c:\src\quorum\docs\epic\EPIC_93_SDUI_Output_Rendering_Unification 2.md" --rules="00-antigravity-core.md, 01-python-backend.md"`
