# Studio Decomposition Epic Tracker

## Goal
Decompose `backend_v2/services/studio.py` into 6 isolated services inside the `backend_v2/services/studio/` domain directory using the Strangler Fig pattern. Update all FastAPI dependency injection boundaries and completely eliminate the original God object.

## Execution Loops
Use the `/tier5-resume` commands at the bottom of each task to navigate through the phases seamlessly. Execute each phase completely before moving to the next.

- [x] `docs\epic\tasks_studio_decomposition\phase1_workflow_step_services.md` - Extract Workflow & Step services.
- [x] `docs\epic\tasks_studio_decomposition\phase2_prompt_profile_services.md` - Extract Prompt Block & Output Profile services.
- [x] `docs\epic\tasks_studio_decomposition\phase3_system_lexicon_services.md` - Extract System Config & Lexicon services.
- [x] `docs\epic\tasks_studio_decomposition\phase4_simulation_and_cleanup.md` - Extract Simulation service, delete God Object.
- [x] Run `/tier2-hardening-backend` on `backend_v2/services/studio/` and `backend_v2/api/routers/studio/` to enforce Phase 9 compliance.

## Instructions for the Execution Agent
1. When executing a sub-plan, you must act as a strict executor. Use the Universal Quality Gate script.
2. DO NOT combine sub-plans.
3. At the end of your execution, update this tracker by changing `[NOK]` to `[x]` for the completed phase.
4. BEFORE handing over the session, you MUST update the `Session Handover` block at the bottom of this tracker file. Ensure the `--done` parameter is a comprehensive, cumulative summary of ALL previously completed phases.

---

### Session Handover
To execute this Epic iteratively, start a NEW chat session and run the following command:

```bash
/tier5-resume --target="docs/epic/studio_decomposition_tracker.md" --achieved="Phases 1-4 Executed. Studio God Object eliminated. Phase 9 Hardening completed for ALL 7 files inside backend_v2/services/studio/ and ALL 8 files inside backend_v2/api/routers/studio/. Epic fully completed." --learned="Applying Phase 9 rules requires strict UserRole enum checks and manual 'strict=False' during db hydration, bypassing Mypy 2.1.0 internal errors by relying on Ruff and Pytest. FastApi router inline models must be extracted to models/dtos/." --remaining="None. Epic Studio Decomposition is complete."
```
