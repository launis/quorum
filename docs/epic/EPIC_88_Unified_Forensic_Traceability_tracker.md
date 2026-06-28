# EPIC 88: Unified Forensic Traceability Tracker

## Master Protocol
This is the execution tracker for Epic 88. 
To process this Epic, execute the tasks below strictly in order. Do not mix Backend and Frontend execution in the same session. Utilize `/tier2-execute` to load a phase plan, implement it, and then run the respective `/tier2-hardening-backend` or `/tier2-hardening-frontend` quality gate before marking the phase as `[OK]`.

## Task List

- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase1_backend_models.md` - Backend DTO Models & CoT
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase2_mcp_aliasing.md` - MCP Aliasing & Unified Source Pipeline
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase3_prompt_escape_hatch.md` - Prompt Escape Hatch & Validation
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase4_soft_delete_api.md` - Soft Delete API & Trace Events
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase5_worker_fuzzy_matching.md` - Async Fuzzy Matching & Worker Pre-Calculation
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase6_blueprint_transformer.md` - Blueprint Transformer & RowForensicsDTO
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase7_flutter_models.md` - Flutter Frontend DTOs
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase8_flutter_ui.md` - Flutter UI & Optimistic Soft Delete
- [NOK] `docs/epic/tasks_EPIC_88_Unified_Forensic_Traceability/phase9_pdf_jinja.md` - PDF Rendering & Jinja2 Template Parity

## Instructions for the Execution Agent
1. Pick the first `[NOK]` task from the list.
2. Read the referenced Markdown file.
3. Call the execution tier slash command for it (e.g. `/tier2-execute docs/epic/tasks_EPIC_88...`).
4. After passing the Hardening Quality Gate, update this tracker file to mark the task as `[OK]`.
5. Handover the session to a fresh context window to process the next task.

---
### Session Handover

Kun aloitat uuden puhdaskontekstisen session (uusi chat-ikkuna) varsinaista koodausta varten, anna tekoälylle seuraava komento. Se lataa tämän trackerin ja kertoo, mitä olemme jo tehneet.

```
/tier5-resume --target="docs/epic/EPIC_88_Unified_Forensic_Traceability_tracker.md" --done="Epic 88 (Unified Forensic Traceability) on pilkottu 9:ään mikro-toteutussuunnitelmaan (phase_1 - phase_9). Tässä suunnittelu-ikkunassa käytiin läpi Epicin vaatimukset (System 2, XAI-jäljitettävyys, Soft Delete, MCP Aliasing, Fuzzy Match Workerissä). Koodausta ei vielä aloitettu." --next="Lataa Tracker ja aloita ensimmäisen [NOK] -vaiheen toteutus /tier2-execute -komennon kautta."
```
