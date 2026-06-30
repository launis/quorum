# Epic 90 Tracker: Prompt Centralization & Hybrid Output Protocol (SDUI)

This epic tracks the implementation of Epic 90, which moves UI directives to OutputProfiles and establishes the Universal Ingress Pipeline with Fast-Track XML Parsing.

## Execution Checklist
- [x] phase1_pydantic_dto.md - Pydantic "Suojamuuri" ja DTO:n rakentaminen
- [x] phase2_database_seed.md - Output Profile -Tietokantamalli ja Seed-migraatio
- [x] phase3_studio_api.md - Studio API & DB Haku
- [x] phase4_llm_dumb_pipe.md - LLM-moottorin purkaminen (The Dumb Pipe)
- [x] phase5_frontend_pdf.md - Frontend & PDF Pariteetti (SDUI Renderöinti)

## Instructions for the Execution Agent
You are working on a continuous execution loop. 
1. Run `/tier2-execute` to process the first `[NOK]` task.
2. After finishing a task, update its status to `[x]` in this tracker.
3. At the end of your execution run, you MUST update the `/tier5-resume` command in the "Session Handover" block below with the cumulative summary of ALL previously completed phases in the `--done` parameter.

---
<!-- Session Handover -->
To execute the next phase or resume execution, start a NEW chat session and run:
`/tier5-resume --target docs/epic/EPIC_90_Output_renewal_tracker.md --done "Epic 90 completed. Phase 1-4: OutputProfile DB Repo and Schema updated, UniversalIngress pipeline implemented with fast-track XML parsing, legacy rules migrated to seed_data.json. Phase 5: Frontend and PDF engines updated to maintain parity, using VisualIntent as SSOT. Both backend and frontend code successfully audited and passing strict tests."`
