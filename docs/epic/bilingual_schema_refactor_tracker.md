# Bilingual Schema Refactor Epic Tracker

To execute this Epic iteratively, start a NEW chat session and run the corresponding command for each phase.

The Epic has been structured so that the easier, independent refactorings are executed first. This ensures the codebase remains 100% executable and audit loops can run to completion before tackling the massive "God Commit" schema changes.

- [NOK] `phase1_god_object_refactor.md` - God Object Refactor (Ennakko-Epic A)
- [NOK] `phase2_db_migration_offline.md` - Offline DB ETL Migration Script
- [NOK] `phase3_backend_schema_update.md` - Backend Pydantic Schema & Atomic Commit
- [NOK] `phase4_frontend_schema_ui.md` - Frontend DTO Sync & Admin UI
- [NOK] `phase5_best_of_three_routing.md` - Best-of-3 Routing & Execution (Jälki-Epic C)

## Execution Command
To begin execution, start a new chat session and run:
`/tier5-resume --target docs/epic/bilingual_schema_refactor_tracker.md`
