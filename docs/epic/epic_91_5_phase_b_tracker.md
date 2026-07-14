# Epic 91.5 Phase B Tracker

- [x] [OK] Execute Plan B1: SDUI Mapper Service
  - Execute `docs/epic/tasks_epic_91_5_phase_b/B1_sdui_mapper.md`
- [x] [OK] Execute Plan B2: PDF Generator StrictUndefined Enforcement
  - Execute `docs/epic/tasks_epic_91_5_phase_b/B2_pdf_generator.md`
- [ ] [NOK] Invoke the Tier 1 Planner again to generate detailed plans for the remaining phases based on the updated codebase state.
- [ ] [NOK] Phase B3: Golden Master E2E Test (uusi, v2_core-pohjainen)
- [ ] [NOK] Phase B4: Excel Export Modernization
- [ ] [NOK] Phase B5: N/A Manual Override API
- [ ] [NOK] Tier 2 Hardening
- [ ] [NOK] Proxy Sunset & Consumer Migration
- [ ] [NOK] Pre-Delete Audit
- [ ] [NOK] Baseline Parity & Zero-Loss Audit

# Instructions for the Execution Agent
You MUST systematically execute the above tasks from top to bottom using the `/tier2-execute` workflow. After completing a task, mark it `[x]` and commit the code using atomic commits. Do not proceed to the next phase without confirming tests pass (Universal Quality Gate). Once B1 and B2 are done, execute the planner again. Update the `/tier5-resume` command below before handing over the session.

# Session Handover Context
**Achieved:**
- Tier 1 Planning completed for Phase B1 and B2.
- Tier 0 Red-Team Analysis and refinement completed for B1 and B2 (Fixed SDUI mapping and Jinja StrictUndefined vectors).

**Learned:**
- `v2_core.ReportDataDTO` is fully established as the SSOT. The SDUI Mapper and PDF Generator must adapt to its nested matrix and layout architecture instead of the deprecated flat list approach from Phase A.
- Jinja template must strictly access `row_explanation` (not `justification`) and `verified_source_ids` (not `source_alias`) to prevent `StrictUndefined` failures.

**Remaining:**
- Execute B1 Plan (SDUI Mapper Service).
- Execute B2 Plan (PDF Generator).
- Re-run Tier 1 Planner for B3, B4, B5.
- Execute remaining phases.

To resume execution in a new context window:
`/tier5-resume --workflow=/tier2-execute --target="docs/epic/epic_91_5_phase_b_tracker.md, docs/epic/tasks_epic_91_5_phase_b/B2_pdf_generator.md" --rules=".agents/rules/00-antigravity-core.md, .agents/rules/01-python-backend.md"`
