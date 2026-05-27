# Epic 60 Master Tracker: Modular Extraction Decoupling

This tracker monitors the phased implementation of Epic 60 to separate the Global Zero-Trust Evidence Extraction Protocol from criteria-specific TDA assertions, update Pydantic and Freezed schemas, and refactor the Admin Studio V2 form widgets.

## Active Sub-plans
- [OK] [phase1_database_refactor.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase1_database_refactor.md) - Extract global guideline boilerplate from TDA assertions and register a modular Global Zero-Trust Evidence Extraction Protocol block in `seed_data.json`.
- [OK] [phase2_backend_models.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase2_backend_models.md) - Update `Step` model in Pydantic to support `role_block_id`, `extraction_protocol_block_id`, and `criteria_block_ids` fields with strict validation.
- [OK] [phase3_prompt_compiler.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase3_prompt_compiler.md) - Modify `PromptFactory` and `LLMNodeStrategy` to resolve, compile, and statically inject decoupled blocks while fencing user payloads in XML to optimize caching.
- [OK] [phase4_frontend_models.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase4_frontend_models.md) - Update Flutter sealed `NodeStrategy` class to support segregated schema properties and regenerate Freezed classes.
- [OK] [phase5_studio_ui.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase5_studio_ui.md) - Build custom selectors in Admin Studio form widgets for decoupled properties and localize all UI labels in `.arb` resource bundles.
- [OK] [phase6_verification.md](file:///c:/src/quorum/docs/epic/tasks_EPIC_60/phase6_verification.md) - Write comprehensive integration tests for prompt compilation and execute quality gate loops on backend and frontend components.


## Universal Hardening Loop Mandate
When all modified files are completed, the user must run:
```powershell
/tier2-hardening-backend
```
and:
```powershell
/tier2-hardening-frontend
```
to audit standards and complete the Quality Gate verification.

---

## Handover Instructions
To start the execution loop:
1. Open a fresh context window.
2. Run command: `/tier5-resume --target docs/epic/EPIC_60_tracker.md`
