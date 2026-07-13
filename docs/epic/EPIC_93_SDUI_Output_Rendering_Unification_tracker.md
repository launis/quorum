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
- [x] Phase 3: Universal Output Adapters & Synthesis Integration
      *Plan: `docs/epic/tasks_EPIC_93_SDUI_Output_Rendering_Unification/phase_3_adapters_and_routers.md`*
- [x] Phase 4: Legacy Pipeline B Sunset (Erase God Code)
      *Plan: `docs/epic/tasks_EPIC_93_SDUI_Output_Rendering_Unification/phase_4_erase_god_code.md`*
- [x] `[NOK]` Invoke Tier 1 Planner for remaining phases (Phase 3 & 4)
- [x] Tier 2 Hardening (run `/tier2-hardening-backend` on new directories)
- [ ] `[NOK]` Proxy Sunset & Consumer Migration
- [ ] `[NOK]` Pre-Delete Audit
- [ ] `[NOK]` Baseline Parity & Zero-Loss Audit
- [ ] `[NOK]` Update architectural documentation and 04_directory_reference.md

## Instructions for the Execution Agent
- Execute the plans one by one using the `/tier2-execute` workflow.
- After completing Phase 2, you MUST stop and invoke `/tier1-planner` to flesh out the placeholders for Phase 3 and Phase 4 before continuing.
- After running the hardening loops, carefully update the session handover context block at the end of this tracker.

# Session Handover Context
- **Achieved**: Completed Tier 1 Planner for Phase 3 and Phase 4. Implementation plans have been generated and saved to the `docs/epic/tasks...` folder. The architecture confirms that Synthesis MUST be executed natively inside Pipeline A (DAG), which requires refactoring MatrixReducer from the end of `dag_executor.py` into the execution stream so the Synthesis PromptBlock can consume it.
- **Learned**: Phase 3 will rely on moving Synthesis into `seed_data.json` and bypassing `hooks/synthesis.py` entirely, leading into the complete deletion of God Code in Phase 4.
- **Remaining**: Execute Phase 3 (`phase_3_adapters_and_routers.md`). Initiate Tier 2 Execution workflow to perform the integration.

## Resume Command
To execute this Epic iteratively, start a NEW chat session and run the following command:

`/tier5-resume --workflow=/tier2-execute --target="docs\epic\EPIC_93_SDUI_Output_Rendering_Unification_tracker.md, docs\epic\tasks_EPIC_93_SDUI_Output_Rendering_Unification\phase_3_adapters_and_routers.md" --rules="00-antigravity-core.md, 01-python-backend.md"`
